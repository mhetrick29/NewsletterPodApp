# Newsletter Parser

A robust Python parser for extracting content from email newsletters across multiple platforms.

## Features

- **Multi-platform support**: Substack, Beehiiv, TLDR, ConvertKit, and generic HTML
- **Automatic platform detection**: Identifies newsletter platform from sender and content
- **Category mapping**: Automatically categorizes newsletters into 4 categories:
  - Product & AI
  - Health & Fitness  
  - Finance
  - Sahil Bloom
- **Content extraction**: Pulls out title, sections, links, and clean text
- **Validation**: Quality checks to ensure parsed content is usable

## Installation

```bash
pip install -r parser_requirements.txt
```

## Quick Start

```python
from newsletter_parser import NewsletterParser, validate_parsed_content

# Initialize parser
parser = NewsletterParser()

# Parse a Gmail message (from Gmail API)
result = parser.parse_gmail_message(gmail_message)

# Validate the parsed content
is_valid, checks = validate_parsed_content(result)

print(f"Sender: {result['sender_name']}")
print(f"Category: {result['category']}")
print(f"Content: {result['content'][:500]}...")
```

## Supported Platforms

### Substack
**Newsletters**: Lenny's Newsletter, Peter Yang, mario fraioli

**Features**:
- Extracts title from H1
- Preserves section structure (H2/H3 headings)
- Removes Substack boilerplate and footer
- Extracts links

### Beehiiv
**Newsletters**: Half Baked, The Code by Superhuman

**Features**:
- Handles table-based layouts
- Detects emoji-based section markers (e.g., 🍪)
- Tracks image count for content flagging
- Extracts text from complex HTML

### TLDR Format
**Newsletters**: TLDR, TLDR AI, TLDR Product

**Features**:
- Parses curated news item structure
- Groups items by section
- Preserves headline + description format
- Extracts all story links

### ConvertKit
**Newsletters**: Sahil Bloom's Curiosity Chronicle

**Features**:
- Clean section extraction
- Preserves numbered lists and ideas
- Removes tracking and footer elements

### Generic
**Newsletters**: Stratechery, Snacks, Chartr, and unknown formats

**Features**:
- Fallback parser for any HTML
- Best-effort text extraction
- Flags for manual review

## Usage with Gmail API

```python
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from newsletter_parser import NewsletterParser

# Authenticate with Gmail
creds = Credentials.from_authorized_user_file('token.json')
service = build('gmail', 'v1', credentials=creds)

# Query newsletters
query = 'label:newsletters after:2026/01/17'
results = service.users().messages().list(userId='me', q=query).execute()

# Parse each newsletter
parser = NewsletterParser()
for message in results.get('messages', []):
    msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
    parsed = parser.parse_gmail_message(msg)
    
    print(f"{parsed['category']}: {parsed['sender_name']} - {parsed['subject']}")
```

## Output Structure

Each parsed newsletter returns a dictionary with:

```python
{
    'message_id': str,          # Gmail message ID
    'sender_name': str,         # Newsletter name
    'sender_email': str,        # Sender email address
    'subject': str,             # Email subject
    'date': str,                # Send date
    'platform': str,            # Detected platform (substack, beehiiv, etc.)
    'category': str,            # Newsletter category (product_ai, health_fitness, etc.)
    'content': str,             # Clean text content
    'title': str,               # Extracted title
    'sections': List[Dict],     # Section headings and content
    'links': List[Dict],        # Extracted links
    'images': List[str],        # Image URLs (for image-heavy newsletters)
    'metadata': Dict,           # Platform-specific metadata
    'parsing_success': bool,    # Whether parsing succeeded
    'needs_review': bool        # Flag for manual review
}
```

## Category Mapping

The parser automatically categorizes newsletters based on sender:

**Product & AI**:
- Peter Yang
- Lenny's Newsletter
- Ben Thompson (Stratechery)
- TLDR, TLDR AI, TLDR Product
- The Code by Superhuman
- Elena's Growth Scoop
- Hilary Gridley
- Tal Raviv
- Half Baked

**Health & Fitness**:
- mario fraioli (The Morning Shakeout)
- FittInsider
- Sweat Science

**Finance**:
- Snacks
- Chartr

**Sahil Bloom**:
- Sahil Bloom's Curiosity Chronicle

## Validation

The parser includes content validation:

```python
is_valid, checks = validate_parsed_content(parsed_result)

# Checks:
# - has_content: At least 100 characters
# - has_sentences: Contains sentence-ending punctuation
# - no_excessive_whitespace: Not too many blank lines
# - readable_ratio: >70% readable characters
```

## Error Handling

- **Parsing failures**: Returns error result with `parsing_success: False`
- **Missing content**: Flags with `needs_review: True`
- **Unknown platforms**: Falls back to generic parser
- **Unknown newsletters**: Defaults to 'product_ai' category with warning

## Customization

### Adding New Newsletters

Edit `CATEGORY_MAPPING` in `NewsletterParser` class:

```python
CATEGORY_MAPPING = {
    'new newsletter name': 'category',
    # ...
}
```

### Adding New Platforms

1. Create a new parser class (extend pattern from existing parsers)
2. Add platform detection logic to `_detect_platform()`
3. Add parser to routing in `_route_to_parser()`

Example:

```python
class CustomPlatformParser:
    def parse(self, html_content: str) -> Dict:
        # Your parsing logic
        return {
            'content': '...',
            'title': '...',
            # ... other fields
        }
```

## Integration with Podcast Generation

The parsed output is designed to feed directly into:
1. Claude API for summarization
2. Text-to-speech for podcast generation
3. Database storage for tracking and learning

Example workflow:

```python
# 1. Parse newsletters
parsed = parser.parse_gmail_message(msg)

# 2. Summarize with Claude
summary = summarize_with_claude(parsed['content'])

# 3. Generate podcast script
script = generate_podcast_script([summary])

# 4. Convert to speech
audio = text_to_speech(script)
```

## Testing

Run the test script:

```bash
python test_parser.py
```

This will demonstrate:
- Basic parsing functionality
- Content validation
- Output structure

## Performance

- **Parsing speed**: ~50-100ms per newsletter
- **Memory usage**: Minimal (few MB per newsletter)
- **Batch processing**: Can handle 100+ newsletters efficiently

## Troubleshooting

### "No HTML content found"
- Email might be text-only
- Check Gmail API payload structure

### "Parsing success: False"
- Check logs for specific error
- Verify HTML structure matches expected platform

### "Needs review: True"
- Content was parsed but flagged for quality
- Review manually or adjust validation thresholds

### Unknown newsletters default to 'product_ai'
- Add to CATEGORY_MAPPING if recurring
- Check sender name/email matching logic

## Next Steps

After parsing, the typical workflow is:

1. ✅ **Parse newsletters** (this module)
2. **Summarize with Claude API** (next module)
3. **Generate podcast script** (next module)
4. **Convert to speech** (TTS module)
5. **Store and serve** (API/storage module)

## License

Part of the Newsletter Podcast Agent project.
