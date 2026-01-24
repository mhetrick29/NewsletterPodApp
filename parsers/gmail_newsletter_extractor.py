#!/usr/bin/env python3
"""
Gmail Newsletter Extractor
Connects to Gmail via OAuth and extracts all newsletter sources from emails labeled "newsletters"
"""

import os
import json
import pickle
from datetime import datetime
from collections import defaultdict
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
from email.utils import parseaddr
import re

# Gmail API scopes - read-only access
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate_gmail():
    """Authenticate with Gmail API using OAuth 2.0"""
    creds = None
    
    # Token file stores user's access and refresh tokens
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If no valid credentials available, let user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # You need to create credentials.json from Google Cloud Console
            # Instructions: https://developers.google.com/gmail/api/quickstart/python
            if not os.path.exists('credentials.json'):
                print("\nâŒ ERROR: credentials.json not found!")
                print("\nTo create credentials.json:")
                print("1. Go to https://console.cloud.google.com/")
                print("2. Create a new project (or select existing)")
                print("3. Enable Gmail API")
                print("4. Create OAuth 2.0 credentials (Desktop app)")
                print("5. Download the credentials and save as 'credentials.json'")
                print("6. Run this script again")
                return None
            
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save credentials for next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return creds

def get_email_body(payload):
    """Extract text content from email payload"""
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                data = part['body'].get('data', '')
                if data:
                    return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
            elif part['mimeType'] == 'text/html':
                data = part['body'].get('data', '')
                if data:
                    html = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                    # Basic HTML stripping (for preview only)
                    text = re.sub('<[^<]+?>', '', html)
                    return text
    else:
        data = payload['body'].get('data', '')
        if data:
            return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
    return ""

def extract_newsletters(service, max_emails=500, get_samples=True):
    """
    Extract all newsletter sources from Gmail
    
    Args:
        service: Gmail API service object
        max_emails: Maximum number of emails to process
        get_samples: Whether to fetch sample email content
    """
    print("\nðŸ” Searching for newsletters in your Gmail...")
    
    newsletters = defaultdict(lambda: {
        'count': 0,
        'subjects': [],
        'latest_date': None,
        'sender_email': None,
        'sample_content': None
    })
    
    try:
        # Query for all emails with "newsletters" label
        query = 'label:newsletters'
        results = service.users().messages().list(
            userId='me',
            q=query,
            maxResults=max_emails
        ).execute()
        
        messages = results.get('messages', [])
        
        if not messages:
            print("âŒ No emails found with 'newsletters' label")
            print("\nMake sure you have:")
            print("1. Created a label called 'newsletters' in Gmail")
            print("2. Applied this label to your newsletter emails")
            return {}
        
        print(f"ðŸ“§ Found {len(messages)} newsletter emails. Processing...\n")
        
        # Process each message
        for i, message in enumerate(messages):
            try:
                msg = service.users().messages().get(
                    userId='me',
                    id=message['id'],
                    format='full'
                ).execute()
                
                # Extract headers
                headers = {h['name']: h['value'] for h in msg['payload']['headers']}
                
                # Get sender info
                from_header = headers.get('From', '')
                sender_name, sender_email = parseaddr(from_header)
                
                # Use sender name as the key (this is what we'll display)
                if not sender_name:
                    sender_name = sender_email
                
                # Get subject
                subject = headers.get('Subject', 'No Subject')
                
                # Get date
                date_str = headers.get('Date', '')
                
                # Update newsletter info
                newsletters[sender_name]['count'] += 1
                newsletters[sender_name]['sender_email'] = sender_email
                
                # Store up to 3 sample subjects
                if len(newsletters[sender_name]['subjects']) < 3:
                    newsletters[sender_name]['subjects'].append(subject)
                
                # Update latest date
                if date_str:
                    newsletters[sender_name]['latest_date'] = date_str
                
                # Get sample content for first occurrence (if requested)
                if get_samples and newsletters[sender_name]['count'] == 1:
                    content = get_email_body(msg['payload'])
                    # Store first 500 characters as preview
                    newsletters[sender_name]['sample_content'] = content[:500] if content else None
                
                # Progress indicator
                if (i + 1) % 50 == 0:
                    print(f"  Processed {i + 1}/{len(messages)} emails...")
                
            except HttpError as error:
                print(f"  âš ï¸  Error processing message {message['id']}: {error}")
                continue
        
        print(f"\nâœ… Processing complete!")
        return dict(newsletters)
        
    except HttpError as error:
        print(f"âŒ An error occurred: {error}")
        return {}

def save_results(newsletters, filename='newsletter_sources.json'):
    """Save newsletter data to JSON file"""
    output = {
        'extracted_at': datetime.now().isoformat(),
        'total_sources': len(newsletters),
        'newsletters': newsletters
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\nðŸ’¾ Results saved to: {filename}")

def print_summary(newsletters):
    """Print a summary of discovered newsletters"""
    print(f"\n" + "="*80)
    print(f"ðŸ“Š NEWSLETTER SUMMARY")
    print(f"="*80)
    print(f"\nTotal unique newsletters: {len(newsletters)}\n")
    
    # Sort by count (most frequent first)
    sorted_newsletters = sorted(
        newsletters.items(),
        key=lambda x: x[1]['count'],
        reverse=True
    )
    
    for sender_name, data in sorted_newsletters:
        print(f"\nðŸ“¬ {sender_name}")
        print(f"   Email: {data['sender_email']}")
        print(f"   Count: {data['count']} emails")
        print(f"   Latest: {data['latest_date']}")
        print(f"   Sample subjects:")
        for subject in data['subjects'][:3]:
            print(f"      â€¢ {subject}")

def main():
    """Main execution function"""
    print("="*80)
    print("Gmail Newsletter Extractor")
    print("="*80)
    
    # Authenticate
    creds = authenticate_gmail()
    if not creds:
        return
    
    try:
        # Build Gmail service
        service = build('gmail', 'v1', credentials=creds)
        
        print("\nâœ… Successfully authenticated with Gmail!")
        
        # Extract newsletters
        newsletters = extract_newsletters(
            service,
            max_emails=500,  # Adjust if you have more newsletters
            get_samples=True  # Set to False for faster processing
        )
        
        if newsletters:
            # Print summary
            print_summary(newsletters)
            
            # Save to file
            save_results(newsletters)
            
            print("\n" + "="*80)
            print("âœ… EXTRACTION COMPLETE!")
            print("="*80)
            print("\nNext steps:")
            print("1. Review 'newsletter_sources.json' file")
            print("2. Share this file with Claude to populate the PRD")
            print("3. Categorize newsletters (Product/Tech, Health/Fitness, Running, Other)")
            
    except HttpError as error:
        print(f"\nâŒ An error occurred: {error}")

if __name__ == '__main__':
    main()
