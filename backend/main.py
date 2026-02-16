"""
FastAPI application for Newsletter Podcast Agent
Phase 1: Core backend with newsletter extraction and viewing
Phase 2: AI-powered summarization
"""
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from database import get_db, init_db, Newsletter
from newsletter_service import NewsletterService

# Initialize FastAPI app
app = FastAPI(
    title="Newsletter Podcast Agent API",
    description="Backend API for newsletter extraction, parsing, and podcast generation",
    version="1.0.0"
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    init_db()
    print("✅ Database initialized")


# Pydantic models for request/response
class ExtractionRequest(BaseModel):
    days_back: int = 1
    max_results: int = 100


class NewsletterListResponse(BaseModel):
    id: int
    sender_name: str
    subject: str
    category: str
    date: str
    platform: str
    needs_review: bool
    
    class Config:
        from_attributes = True


# API Endpoints

@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "message": "Newsletter Podcast Agent API",
        "version": "1.0.0"
    }


@app.get("/api/newsletters", response_model=List[dict])
def list_newsletters(
    category: Optional[str] = Query(None, description="Filter by category"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Get list of newsletters with optional filtering
    
    Query Parameters:
    - category: Filter by category (product_ai, health_fitness, finance, sahil_bloom)
    - start_date: Filter newsletters received after this date
    - end_date: Filter newsletters received before this date
    - limit: Maximum number of results (default: 100, max: 500)
    - offset: Pagination offset (default: 0)
    """
    service = NewsletterService()
    
    # Parse dates
    start_dt = datetime.fromisoformat(start_date) if start_date else None
    end_dt = datetime.fromisoformat(end_date) if end_date else None
    
    newsletters = service.get_newsletters(
        db=db,
        category=category,
        start_date=start_dt,
        end_date=end_dt,
        limit=limit,
        offset=offset
    )
    
    return [nl.to_dict() for nl in newsletters]


@app.get("/api/newsletters/{newsletter_id}")
def get_newsletter(newsletter_id: int, db: Session = Depends(get_db)):
    """
    Get detailed information for a specific newsletter
    
    Path Parameters:
    - newsletter_id: Database ID of the newsletter
    """
    service = NewsletterService()
    newsletter = service.get_newsletter_by_id(db, newsletter_id)
    
    if not newsletter:
        raise HTTPException(status_code=404, detail="Newsletter not found")
    
    return newsletter.to_dict()


@app.get("/api/categories")
def get_categories(db: Session = Depends(get_db)):
    """
    Get all newsletter categories with counts
    
    Returns list of categories and how many newsletters are in each
    """
    service = NewsletterService()
    return service.get_categories(db)


@app.post("/api/extract")
def extract_newsletters(
    request: ExtractionRequest,
    db: Session = Depends(get_db)
):
    """
    Manually trigger newsletter extraction from Gmail
    
    Request Body:
    - days_back: How many days back to search (default: 1)
    - max_results: Maximum number of emails to retrieve (default: 100)
    
    Returns statistics about the extraction
    """
    service = NewsletterService()
    
    try:
        # Authenticate with Gmail
        service.authenticate_gmail()
        
        # Extract and parse newsletters
        stats = service.extract_newsletters(
            db=db,
            days_back=request.days_back,
            max_results=request.max_results
        )
        
        return {
            "success": True,
            "message": f"Extracted {stats['newly_parsed']} new newsletters",
            "stats": stats
        }
        
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Extraction failed: {str(e)}"
        )


@app.get("/api/stats")
def get_stats(db: Session = Depends(get_db)):
    """
    Get overall statistics about the newsletter database
    
    Returns:
    - Total number of newsletters
    - Breakdown by category
    - Breakdown by platform
    - Recent activity
    """
    from sqlalchemy import func
    
    # Total count
    total = db.query(func.count(Newsletter.id)).scalar()
    
    # By category
    by_category = db.query(
        Newsletter.category,
        func.count(Newsletter.id).label('count')
    ).group_by(Newsletter.category).all()
    
    # By platform
    by_platform = db.query(
        Newsletter.platform,
        func.count(Newsletter.id).label('count')
    ).group_by(Newsletter.platform).all()
    
    # Needs review count
    needs_review = db.query(func.count(Newsletter.id)).filter(
        Newsletter.needs_review == True
    ).scalar()
    
    # Recent newsletters (last 7 days)
    seven_days_ago = datetime.now() - timedelta(days=7)
    recent = db.query(func.count(Newsletter.id)).filter(
        Newsletter.received_at >= seven_days_ago
    ).scalar()
    
    return {
        "total_newsletters": total,
        "needs_review": needs_review,
        "recent_7_days": recent,
        "by_category": [{"category": r.category, "count": r.count} for r in by_category],
        "by_platform": [{"platform": r.platform, "count": r.count} for r in by_platform]
    }


from datetime import timedelta


@app.get("/api/summary")
def get_daily_summary(
    date: Optional[str] = Query(None, description="Date to summarize (YYYY-MM-DD), defaults to today"),
    db: Session = Depends(get_db)
):
    """
    Get a summary of newsletters grouped by category for a specific date.

    Query Parameters:
    - date: The date to summarize (defaults to today in local time)

    Returns:
    - Newsletters grouped by category with key information
    """
    from sqlalchemy import func
    from zoneinfo import ZoneInfo
    import time

    # Get local timezone - default to America/Los_Angeles (PST/PDT)
    local_tz = ZoneInfo('America/Los_Angeles')
    try:
        # Try to get proper timezone from system
        import subprocess
        tz_result = subprocess.run(['readlink', '/etc/localtime'], capture_output=True, text=True, timeout=1)
        if tz_result.returncode == 0:
            # Extract timezone from path
            tz_path = tz_result.stdout.strip()
            if 'zoneinfo' in tz_path:
                tz_name = tz_path.split('zoneinfo/')[-1]
                local_tz = ZoneInfo(tz_name)
    except Exception as e:
        logger.warning(f"Could not detect timezone, using America/Los_Angeles: {e}")

    # Parse date or use today (in local time)
    if date:
        target_date = datetime.fromisoformat(date).date()
    else:
        target_date = datetime.now(local_tz).date()

    # Get start and end of the target date in local time, then convert to UTC
    local_start = datetime.combine(target_date, datetime.min.time()).replace(tzinfo=local_tz)
    local_end = datetime.combine(target_date, datetime.max.time()).replace(tzinfo=local_tz)

    # Convert to UTC for database query (database stores UTC)
    start_dt = local_start.astimezone(ZoneInfo('UTC')).replace(tzinfo=None)
    end_dt = local_end.astimezone(ZoneInfo('UTC')).replace(tzinfo=None)
    
    logger.info(f"Querying newsletters from {start_dt} to {end_dt} UTC (local date: {target_date})")

    # Query newsletters for this date
    newsletters = db.query(Newsletter).filter(
        Newsletter.received_at >= start_dt,
        Newsletter.received_at <= end_dt
    ).order_by(Newsletter.category, Newsletter.received_at.desc()).all()

    # Group by category
    categories = {}
    category_display_names = {
        'product_ai': 'Product & AI',
        'health_fitness': 'Health & Fitness',
        'finance': 'Finance',
        'sahil_bloom': 'Sahil Bloom'
    }

    for nl in newsletters:
        cat = nl.category or 'uncategorized'
        if cat not in categories:
            categories[cat] = {
                'display_name': category_display_names.get(cat, cat.replace('_', ' ').title()),
                'newsletters': []
            }

        categories[cat]['newsletters'].append({
            'id': nl.id,
            'sender_name': nl.sender_name,
            'subject': nl.subject,
            'title': nl.title,
            'date': nl.date,
            'platform': nl.platform,
            'parsed_content': nl.parsed_content[:500] + '...' if nl.parsed_content and len(nl.parsed_content) > 500 else nl.parsed_content,
            'sections': nl.sections
        })

    return {
        'date': target_date.isoformat(),
        'total_newsletters': len(newsletters),
        'categories': categories
    }


# ============================================
# Phase 2: AI Summarization Endpoints
# ============================================

def get_summarization_service():
    """Get the AI summarization service (lazy initialization)"""
    from summarization_service import SummarizationService
    try:
        return SummarizationService()
    except ValueError as e:
        raise HTTPException(
            status_code=503,
            detail=str(e)
        )


@app.get("/api/newsletters/{newsletter_id}/ai-summary")
def get_ai_summary(newsletter_id: int, db: Session = Depends(get_db)):
    """
    Get an AI-generated summary for a specific newsletter.
    Uses Claude to read and understand the newsletter like a human would.
    """
    newsletter = db.query(Newsletter).filter(Newsletter.id == newsletter_id).first()
    if not newsletter:
        raise HTTPException(status_code=404, detail="Newsletter not found")

    if not newsletter.raw_html:
        raise HTTPException(
            status_code=400,
            detail="Newsletter has no HTML content to summarize"
        )

    try:
        service = get_summarization_service()
        summary = service.summarize_newsletter(
            newsletter.raw_html,
            newsletter.sender_name,
            newsletter.subject
        )
        summary['newsletter_id'] = newsletter_id
        summary['sender_name'] = newsletter.sender_name
        summary['category'] = newsletter.category
        return summary
    except Exception as e:
        logger.error(f"AI summary failed for newsletter {newsletter_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate AI summary: {str(e)}"
        )


@app.get("/api/ai-summary")
def get_daily_ai_summary(
    date: Optional[str] = Query(None, description="Date to summarize (YYYY-MM-DD), defaults to today"),
    db: Session = Depends(get_db)
):
    """
    Get AI-generated summaries for all newsletters on a specific date.
    Groups newsletters by category with intelligent summaries.
    """
    from zoneinfo import ZoneInfo
    import time

    # Get local timezone - default to America/Los_Angeles (PST/PDT)
    local_tz = ZoneInfo('America/Los_Angeles')
    try:
        import subprocess
        tz_result = subprocess.run(['readlink', '/etc/localtime'], capture_output=True, text=True, timeout=1)
        if tz_result.returncode == 0:
            tz_path = tz_result.stdout.strip()
            if 'zoneinfo' in tz_path:
                tz_name = tz_path.split('zoneinfo/')[-1]
                local_tz = ZoneInfo(tz_name)
    except Exception as e:
        logger.warning(f"Could not detect timezone, using America/Los_Angeles: {e}")

    # Parse date or use today
    if date:
        target_date = datetime.fromisoformat(date).date()
    else:
        target_date = datetime.now(local_tz).date()

    # Get date boundaries in UTC
    local_start = datetime.combine(target_date, datetime.min.time()).replace(tzinfo=local_tz)
    local_end = datetime.combine(target_date, datetime.max.time()).replace(tzinfo=local_tz)
    start_dt = local_start.astimezone(ZoneInfo('UTC')).replace(tzinfo=None)
    end_dt = local_end.astimezone(ZoneInfo('UTC')).replace(tzinfo=None)
    
    logger.info(f"Querying newsletters from {start_dt} to {end_dt} UTC (local date: {target_date})")

    # Query newsletters
    newsletters = db.query(Newsletter).filter(
        Newsletter.received_at >= start_dt,
        Newsletter.received_at <= end_dt
    ).order_by(Newsletter.category, Newsletter.received_at.desc()).all()

    if not newsletters:
        return {
            'date': target_date.isoformat(),
            'total_newsletters': 0,
            'categories': {},
            'message': 'No newsletters found for this date'
        }

    # Generate AI summaries
    try:
        service = get_summarization_service()
    except HTTPException:
        raise

    category_display_names = {
        'product_ai': 'Product & AI',
        'health_fitness': 'Health & Fitness',
        'finance': 'Finance',
        'sahil_bloom': 'Sahil Bloom'
    }

    # Group newsletters by category first
    newsletters_by_category = {}
    for nl in newsletters:
        cat = nl.category or 'uncategorized'
        if cat not in newsletters_by_category:
            newsletters_by_category[cat] = []
        newsletters_by_category[cat].append(nl)

    # Generate AI summaries: Step 1 - Individual newsletters, Step 2 - Category rollup
    categories = {}
    for idx, (cat, cat_newsletters) in enumerate(newsletters_by_category.items()):
        display_name = category_display_names.get(cat, cat.replace('_', ' ').title())

        # Add delay between categories to respect rate limits (except for first category)
        if idx > 0:
            logger.info(f"Waiting 60 seconds before processing next category to respect rate limits...")
            time.sleep(60)

        try:
            logger.info(f"Processing category {display_name} ({len(cat_newsletters)} newsletters)")
            
            # Step 1: Summarize each newsletter individually
            individual_summaries = []
            for nl in cat_newsletters:
                if not nl.raw_html:
                    logger.warning(f"Newsletter {nl.id} has no HTML content, skipping")
                    continue
                
                try:
                    logger.info(f"Summarizing newsletter: {nl.sender_name} - {nl.subject}")
                    nl_summary = service.summarize_newsletter(
                        nl.raw_html,
                        nl.sender_name,
                        nl.subject
                    )
                    nl_summary['id'] = nl.id
                    nl_summary['sender_name'] = nl.sender_name
                    individual_summaries.append(nl_summary)
                    
                    # Small delay between individual newsletters (5 seconds)
                    if len(individual_summaries) < len(cat_newsletters):
                        time.sleep(5)
                        
                except Exception as e:
                    logger.error(f"Failed to summarize newsletter {nl.id}: {e}")
                    individual_summaries.append({
                        'id': nl.id,
                        'sender_name': nl.sender_name,
                        'title': nl.subject,
                        'summary': 'Failed to generate summary',
                        'error': str(e)
                    })
            
            # Step 2: Create category-level summary from individual summaries
            if individual_summaries:
                logger.info(f"Creating category rollup for {display_name}")
                category_summary = service.create_category_rollup(individual_summaries, display_name)
            else:
                category_summary = {
                    'summary': 'No content available for summarization.',
                    'key_points': [],
                    'ai_generated': False
                }
                
        except Exception as e:
            logger.error(f"Failed to process category {cat}: {e}")
            category_summary = {
                'summary': f'Failed to generate AI summary: {str(e)}',
                'key_points': [],
                'error': True
            }
            individual_summaries = []

        categories[cat] = {
            'display_name': display_name,
            'newsletter_count': len(cat_newsletters),
            'summary': category_summary.get('summary', ''),
            'key_points': category_summary.get('key_points', []),
            'newsletters': individual_summaries,
            'ai_generated': category_summary.get('ai_generated', True)
        }

    return {
        'date': target_date.isoformat(),
        'total_newsletters': len(newsletters),
        'categories': categories,
        'ai_generated': True
    }


@app.get("/api/daily-briefing")
def get_daily_briefing(
    date: Optional[str] = Query(None, description="Date for briefing (YYYY-MM-DD), defaults to today"),
    db: Session = Depends(get_db)
):
    """
    Generate a podcast-style daily briefing from all newsletters.
    Returns natural language text suitable for reading aloud or text-to-speech.
    """
    from zoneinfo import ZoneInfo

    # Get local timezone
    local_tz = ZoneInfo('UTC')
    try:
        import subprocess
        tz_result = subprocess.run(['readlink', '/etc/localtime'], capture_output=True, text=True)
        if tz_result.returncode == 0:
            tz_path = tz_result.stdout.strip()
            tz_name = '/'.join(tz_path.split('/')[-2:])
            local_tz = ZoneInfo(tz_name)
    except Exception:
        pass

    # Parse date
    if date:
        target_date = datetime.fromisoformat(date).date()
    else:
        target_date = datetime.now(local_tz).date()

    # Get date boundaries
    local_start = datetime.combine(target_date, datetime.min.time()).replace(tzinfo=local_tz)
    local_end = datetime.combine(target_date, datetime.max.time()).replace(tzinfo=local_tz)
    start_dt = local_start.astimezone(ZoneInfo('UTC')).replace(tzinfo=None)
    end_dt = local_end.astimezone(ZoneInfo('UTC')).replace(tzinfo=None)

    # Query newsletters
    newsletters = db.query(Newsletter).filter(
        Newsletter.received_at >= start_dt,
        Newsletter.received_at <= end_dt,
        Newsletter.raw_html.isnot(None)
    ).all()

    if not newsletters:
        return {
            'date': target_date.isoformat(),
            'briefing': f"No newsletters found for {target_date.isoformat()}.",
            'newsletter_count': 0
        }

    # Generate briefing
    try:
        service = get_summarization_service()
        newsletter_data = [
            {
                'id': nl.id,
                'html_content': nl.raw_html,
                'sender_name': nl.sender_name,
                'subject': nl.subject,
                'category': nl.category
            }
            for nl in newsletters
        ]
        briefing = service.generate_daily_briefing(newsletter_data)
        return {
            'date': target_date.isoformat(),
            'briefing': briefing,
            'newsletter_count': len(newsletters)
        }
    except Exception as e:
        logger.error(f"Failed to generate daily briefing: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate briefing: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
