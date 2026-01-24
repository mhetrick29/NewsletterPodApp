"""
Test script for newsletter parser
Demonstrates how to use the parser with Gmail API
"""

from newsletter_parser import NewsletterParser, validate_parsed_content
import json


def test_parser_with_gmail():
    """
    Example of how to use the parser with Gmail API
    """
    # Initialize parser
    parser = NewsletterParser()
    
    # Example Gmail message structure (this is what you'd get from Gmail API)
    example_gmail_message = {
        'id': '18abc123def456',
        'payload': {
            'headers': [
                {'name': 'From', 'value': 'Lenny Rachitsky <lenny@substack.com>'},
                {'name': 'Subject', 'value': 'How to build with AI tools'},
                {'name': 'Date', 'value': 'Mon, 14 Jan 2026 10:00:00 +0000'}
            ],
            'mimeType': 'multipart/alternative',
            'parts': [
                {
                    'mimeType': 'text/plain',
                    'body': {'data': 'text content...'}
                },
                {
                    'mimeType': 'text/html',
                    'body': {
                        'data': 'PGh0bWw+PGJvZHk+PGgxPkhvdyB0byBidWlsZCB3aXRoIEFJIHRvb2xzPC9oMT48cD5UaGlzIGlzIGEgdGVzdC4uLjwvcD48L2JvZHk+PC9odG1sPg=='
                        # This is base64 encoded HTML: <html><body><h1>How to build with AI tools</h1><p>This is a test...</p></body></html>
                    }
                }
            ]
        }
    }
    
    # Parse the message
    result = parser.parse_gmail_message(example_gmail_message)
    
    # Validate content
    is_valid, checks = validate_parsed_content(result)
    
    print("="*80)
    print("PARSED NEWSLETTER")
    print("="*80)
    print(f"\nSender: {result['sender_name']}")
    print(f"Email: {result['sender_email']}")
    print(f"Subject: {result['subject']}")
    print(f"Category: {result['category']}")
    print(f"Platform: {result['platform']}")
    print(f"\nTitle: {result['title']}")
    print(f"\nContent Preview:\n{result['content'][:500]}...")
    print(f"\nSections: {len(result['sections'])}")
    print(f"Links: {len(result['links'])}")
    print(f"Images: {len(result['images'])}")
    print(f"\nParsing Success: {result['parsing_success']}")
    print(f"Needs Review: {result['needs_review']}")
    print(f"\nValidation Checks:")
    for check, passed in checks.items():
        status = "✓" if passed else "✗"
        print(f"  {status} {check}")
    print(f"\nOverall Valid: {is_valid}")
    
    return result


def process_newsletters_from_gmail(gmail_service):
    """
    Full workflow example: fetch newsletters from Gmail and parse them
    
    Args:
        gmail_service: Authenticated Gmail API service object
    """
    parser = NewsletterParser()
    
    # Query for newsletters from last 24 hours
    from datetime import datetime, timedelta
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    
    query = f'label:newsletters after:{yesterday.strftime("%Y/%m/%d")} before:{today.strftime("%Y/%m/%d")}'
    
    print(f"Querying Gmail: {query}")
    
    try:
        # Get messages
        results = gmail_service.users().messages().list(
            userId='me',
            q=query,
            maxResults=50
        ).execute()
        
        messages = results.get('messages', [])
        print(f"Found {len(messages)} newsletters")
        
        parsed_newsletters = []
        
        for message in messages:
            # Fetch full message
            msg = gmail_service.users().messages().get(
                userId='me',
                id=message['id'],
                format='full'
            ).execute()
            
            # Parse
            parsed = parser.parse_gmail_message(msg)
            
            # Validate
            is_valid, checks = validate_parsed_content(parsed)
            parsed['is_valid'] = is_valid
            parsed['validation_checks'] = checks
            
            parsed_newsletters.append(parsed)
            
            print(f"  ✓ Parsed: {parsed['sender_name']} - {parsed['subject'][:50]}...")
        
        # Group by category
        by_category = {}
        for newsletter in parsed_newsletters:
            category = newsletter['category']
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(newsletter)
        
        print("\n" + "="*80)
        print("PARSED NEWSLETTERS BY CATEGORY")
        print("="*80)
        
        for category in ['product_ai', 'health_fitness', 'finance', 'sahil_bloom']:
            newsletters = by_category.get(category, [])
            if newsletters:
                print(f"\n{category.upper().replace('_', ' & ')}: {len(newsletters)} newsletters")
                for nl in newsletters:
                    print(f"  • {nl['sender_name']}: {nl['subject'][:60]}...")
        
        return parsed_newsletters
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return []


def save_parsed_newsletters(newsletters, filename='parsed_newsletters.json'):
    """Save parsed newsletters to JSON file"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(newsletters, f, indent=2, ensure_ascii=False)
    print(f"\n✓ Saved {len(newsletters)} parsed newsletters to {filename}")


if __name__ == '__main__':
    # Run basic test
    print("\n" + "="*80)
    print("NEWSLETTER PARSER TEST")
    print("="*80 + "\n")
    
    test_parser_with_gmail()
    
    print("\n\nTo use with real Gmail data:")
    print("1. Authenticate with Gmail API (see gmail_newsletter_extractor.py)")
    print("2. Call: process_newsletters_from_gmail(gmail_service)")
    print("3. Parsed data will be ready for summarization with Claude API")
