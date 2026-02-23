"""
Newsletter service - handles Gmail extraction and parsing
Integrates with existing gmail_newsletter_extractor.py and newsletter_parser.py
"""
import os
import sys
import json
import pickle
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

# Add parsers directory to path (supports both repo-root and backend-local layouts)
DEFAULT_PARSERS_DIRS = [
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'parsers')),
    os.path.abspath(os.path.join(os.path.dirname(__file__), 'parsers')),
]
PARSERS_DIR = next((path for path in DEFAULT_PARSERS_DIRS if os.path.isdir(path)), DEFAULT_PARSERS_DIRS[0])
sys.path.insert(0, PARSERS_DIR)

from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from newsletter_parser import NewsletterParser, validate_parsed_content
from sqlalchemy.orm import Session
from database import Newsletter, DEFAULT_OWNER_EMAIL

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def normalize_owner_email(owner_email: Optional[str]) -> str:
    """Normalize missing/empty owner identities to a stable default."""
    candidate = (owner_email or "").strip().lower()
    return candidate or DEFAULT_OWNER_EMAIL


class NewsletterService:
    """Service for extracting and parsing newsletters from Gmail"""
    
    def __init__(self):
        self.parser = NewsletterParser()
        self.gmail_service = None
        
    def authenticate_gmail(self) -> bool:
        """Authenticate with Gmail API"""
        creds = None
        token_path = os.path.join(PARSERS_DIR, 'token.pickle')
        credentials_path = os.path.join(PARSERS_DIR, 'credentials.json')
        
        # Load existing token
        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # Refresh or create new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except RefreshError:
                    logger.warning("Token refresh failed, re-authenticating via browser...")
                    os.remove(token_path)
                    creds = None

            if not creds or not creds.valid:
                if not os.path.exists(credentials_path):
                    raise FileNotFoundError(
                        f"credentials.json not found at {credentials_path}. "
                        "Please add your Google OAuth credentials."
                    )
                if os.getenv("DISABLE_INTERACTIVE_AUTH", "false").lower() in {"1", "true", "yes"}:
                    raise RuntimeError(
                        "Gmail token is missing/invalid and interactive auth is disabled. "
                        "Generate token.pickle locally, then deploy it with credentials.json."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)

            # Save credentials
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)
        
        # Build Gmail service
        self.gmail_service = build('gmail', 'v1', credentials=creds)
        return True
    
    def extract_newsletters(
        self,
        db: Session,
        days_back: int = 1,
        max_results: int = 100,
        target_date: Optional[str] = None,
        owner_email: Optional[str] = None,
    ) -> Dict:
        """
        Extract newsletters from Gmail and parse them

        Args:
            db: Database session
            days_back: How many days back to search (ignored if target_date set)
            max_results: Maximum number of emails to retrieve
            target_date: Specific date to fetch (YYYY-MM-DD). Overrides days_back.
            owner_email: Identity used to partition newsletter data per user.

        Returns:
            Dict with statistics about the extraction
        """
        owner_email = normalize_owner_email(owner_email)

        if not self.gmail_service:
            self.authenticate_gmail()

        # Build query for newsletters
        if target_date:
            from datetime import date as date_type
            td = datetime.fromisoformat(target_date).date()
            next_day = td + timedelta(days=1)
            query = f'label:newsletters after:{td.strftime("%Y/%m/%d")} before:{next_day.strftime("%Y/%m/%d")}'
        else:
            date_filter = (datetime.now() - timedelta(days=days_back)).strftime('%Y/%m/%d')
            query = f'label:newsletters after:{date_filter}'
        
        stats = {
            'total_fetched': 0,
            'already_exists': 0,
            'newly_parsed': 0,
            'parse_errors': 0,
            'by_category': {}
        }
        
        try:
            # Query Gmail
            results = self.gmail_service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            stats['total_fetched'] = len(messages)
            
            for message in messages:
                try:
                    scoped_message_id = f"{owner_email}::{message['id']}"

                    # Check if already in database
                    existing = db.query(Newsletter).filter(
                        Newsletter.message_id == scoped_message_id
                    ).first()
                    
                    if existing:
                        stats['already_exists'] += 1
                        continue
                    
                    # Fetch full message
                    msg = self.gmail_service.users().messages().get(
                        userId='me',
                        id=message['id'],
                        format='full'
                    ).execute()
                    
                    # Parse newsletter
                    parsed = self.parser.parse_gmail_message(msg)
                    
                    # Validate
                    is_valid, checks = validate_parsed_content(parsed)
                    
                    # Parse the email date to a proper datetime
                    received_datetime = None
                    if parsed['date']:
                        try:
                            from email.utils import parsedate_to_datetime
                            from datetime import timezone
                            received_datetime = parsedate_to_datetime(parsed['date'])
                            # Convert to UTC and remove timezone info for SQLite
                            received_datetime = received_datetime.astimezone(timezone.utc).replace(tzinfo=None)
                        except Exception as e:
                            logger.warning(f"Could not parse date '{parsed['date']}': {e}")
                            received_datetime = datetime.utcnow()
                    else:
                        received_datetime = datetime.utcnow()
                    
                    # Save to database
                    newsletter = Newsletter(
                        message_id=scoped_message_id,
                        owner_email=owner_email,
                        sender_name=parsed['sender_name'],
                        sender_email=parsed['sender_email'],
                        subject=parsed['subject'],
                        date=parsed['date'],
                        received_at=received_datetime,  # Use parsed email date
                        platform=parsed['platform'],
                        category=parsed['category'],
                        raw_html=parsed['raw_html'],  # Store HTML for AI summarization
                        parsed_content=parsed['content'],
                        title=parsed['title'],
                        sections=json.dumps(parsed['sections']),
                        links=json.dumps(parsed['links']),
                        images=json.dumps(parsed['images']),
                        extra_metadata=json.dumps(parsed['metadata']),
                        parsing_success=parsed['parsing_success'],
                        needs_review=parsed['needs_review']
                    )
                    
                    db.add(newsletter)
                    db.commit()
                    
                    stats['newly_parsed'] += 1
                    
                    # Update category stats
                    category = parsed['category']
                    if category not in stats['by_category']:
                        stats['by_category'][category] = 0
                    stats['by_category'][category] += 1
                    
                except Exception as e:
                    print(f"Error parsing message {message['id']}: {str(e)}")
                    stats['parse_errors'] += 1
                    continue
            
            return stats
            
        except HttpError as error:
            raise Exception(f"Gmail API error: {str(error)}")
    
    def get_newsletters(
        self,
        db: Session,
        category: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Newsletter]:
        """
        Get newsletters from database with optional filtering
        
        Args:
            db: Database session
            category: Filter by category (product_ai, health_fitness, etc.)
            start_date: Filter newsletters received after this date
            end_date: Filter newsletters received before this date
            limit: Maximum number of results
            offset: Pagination offset
            
        Returns:
            List of Newsletter objects
        """
        query = db.query(Newsletter)
        
        # Apply filters
        if category:
            query = query.filter(Newsletter.category == category)
        if start_date:
            query = query.filter(Newsletter.received_at >= start_date)
        if end_date:
            query = query.filter(Newsletter.received_at <= end_date)
        
        # Order by received date (newest first)
        query = query.order_by(Newsletter.received_at.desc())
        
        # Apply pagination
        query = query.limit(limit).offset(offset)
        
        return query.all()
    
    def get_newsletter_by_id(self, db: Session, newsletter_id: int) -> Optional[Newsletter]:
        """Get a single newsletter by ID"""
        return db.query(Newsletter).filter(Newsletter.id == newsletter_id).first()
    
    def get_categories(self, db: Session) -> List[Dict]:
        """Get all categories with counts"""
        from sqlalchemy import func

        results = db.query(
            Newsletter.category,
            func.count(Newsletter.id).label('count')
        ).group_by(Newsletter.category).all()

        return [{'category': r.category, 'count': r.count} for r in results]

    @staticmethod
    def cleanup_old_newsletters(db: Session, retention_days: int = 10) -> int:
        """
        Delete newsletters older than retention_days.

        Returns:
            Number of deleted rows
        """
        cutoff = datetime.utcnow() - timedelta(days=retention_days)
        count = db.query(Newsletter).filter(Newsletter.received_at < cutoff).delete()
        db.commit()
        logger.info(f"Cleaned up {count} newsletters older than {retention_days} days")
        return count
