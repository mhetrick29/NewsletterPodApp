"""
Newsletter Parser Module
Handles parsing of different newsletter formats from Gmail
"""

import base64
import re
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Tuple
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NewsletterParser:
    """Main parser class that routes to platform-specific parsers"""
    
    # Newsletter to category mapping
    CATEGORY_MAPPING = {
        # Product & AI
        'peter yang': 'product_ai',
        'lenny': 'product_ai',
        'lenny\'s newsletter': 'product_ai',
        'ben thompson': 'product_ai',
        'stratechery': 'product_ai',
        'tldr': 'product_ai',
        'tldr ai': 'product_ai',
        'tldr product': 'product_ai',
        'the code': 'product_ai',
        'superhuman': 'product_ai',
        'elena': 'product_ai',
        'elena\'s growth scoop': 'product_ai',
        'hilary gridley': 'product_ai',
        'tal raviv': 'product_ai',
        'half baked': 'product_ai',
        
        # Health & Fitness
        'mario fraioli': 'health_fitness',
        'morning shakeout': 'health_fitness',
        'fittinsider': 'health_fitness',
        'sweat science': 'health_fitness',
        
        # Finance
        'snacks': 'finance',
        'chartr': 'finance',
        
        # Sahil Bloom
        'sahil bloom': 'sahil_bloom',
        'curiosity chronicle': 'sahil_bloom',
    }
    
    def __init__(self):
        self.substack_parser = SubstackParser()
        self.beehiiv_parser = BeehiivParser()
        self.tldr_parser = TLDRParser()
        self.convertkit_parser = ConvertKitParser()
        self.generic_parser = GenericParser()
    
    def parse_gmail_message(self, gmail_message: Dict) -> Dict:
        """
        Parse a Gmail message and extract newsletter content
        
        Args:
            gmail_message: Gmail API message object
            
        Returns:
            Parsed newsletter data
        """
        try:
            # Extract metadata
            headers = {h['name']: h['value'] 
                      for h in gmail_message['payload']['headers']}
            
            from_header = headers.get('From', '')
            sender_name, sender_email = self._parse_sender(from_header)
            subject = headers.get('Subject', 'No Subject')
            date = headers.get('Date', '')
            message_id = gmail_message['id']
            
            # Extract HTML body
            html_body = self._extract_html_body(gmail_message['payload'])
            
            if not html_body:
                logger.warning(f"No HTML body found for message {message_id}")
                return self._create_error_result(
                    message_id, sender_name, sender_email, subject, date,
                    "No HTML content found"
                )
            
            # Detect platform
            platform = self._detect_platform(sender_email, html_body)
            logger.info(f"Detected platform: {platform} for {sender_name}")
            
            # Parse content based on platform
            parsed_content = self._route_to_parser(platform, html_body)
            
            # Determine category
            category = self._determine_category(sender_name, sender_email)
            
            # Build result
            return {
                'message_id': message_id,
                'sender_name': sender_name,
                'sender_email': sender_email,
                'subject': subject,
                'date': date,
                'platform': platform,
                'category': category,
                'content': parsed_content.get('content', ''),
                'title': parsed_content.get('title', subject),
                'sections': parsed_content.get('sections', []),
                'links': parsed_content.get('links', []),
                'images': parsed_content.get('images', []),
                'metadata': parsed_content.get('metadata', {}),
                'parsing_success': True,
                'needs_review': parsed_content.get('needs_review', False)
            }
            
        except Exception as e:
            logger.error(f"Error parsing message: {str(e)}")
            return self._create_error_result(
                gmail_message.get('id', 'unknown'),
                'Unknown', 'unknown', 'Error', '',
                str(e)
            )
    
    def _parse_sender(self, from_header: str) -> Tuple[str, str]:
        """Parse sender name and email from From header"""
        # Format: "Name <email@domain.com>" or just "email@domain.com"
        match = re.match(r'^(.*?)\s*<(.+?)>$', from_header)
        if match:
            name = match.group(1).strip().strip('"')
            email = match.group(2).strip()
            return name, email
        else:
            return from_header.strip(), from_header.strip()
    
    def _extract_html_body(self, payload: Dict) -> Optional[str]:
        """Extract HTML body from Gmail message payload"""
        # Check if payload has body data directly
        if payload.get('mimeType') == 'text/html':
            data = payload.get('body', {}).get('data', '')
            if data:
                return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
        
        # Check parts
        parts = payload.get('parts', [])
        for part in parts:
            if part.get('mimeType') == 'text/html':
                data = part.get('body', {}).get('data', '')
                if data:
                    return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
            
            # Recursive check for nested parts
            if 'parts' in part:
                nested_html = self._extract_html_body(part)
                if nested_html:
                    return nested_html
        
        return None
    
    def _detect_platform(self, sender_email: str, html_content: str) -> str:
        """Detect newsletter platform"""
        email_lower = sender_email.lower()
        html_lower = html_content.lower()
        
        # Substack
        if 'substack.com' in email_lower:
            return 'substack'
        
        # Beehiiv
        if 'beehiiv.com' in email_lower or 'beehiiv' in html_lower:
            return 'beehiiv'
        
        # ConvertKit
        if 'convertkit' in html_lower or 'kit-mail' in email_lower:
            return 'convertkit'
        
        # TLDR
        if 'tldrnewsletter.com' in email_lower or 'tldr' in email_lower:
            return 'tldr'
        
        # Stratechery
        if 'stratechery.com' in email_lower:
            return 'stratechery'
        
        return 'generic'
    
    def _route_to_parser(self, platform: str, html_content: str) -> Dict:
        """Route to appropriate parser based on platform"""
        parsers = {
            'substack': self.substack_parser,
            'beehiiv': self.beehiiv_parser,
            'tldr': self.tldr_parser,
            'convertkit': self.convertkit_parser,
            'stratechery': self.generic_parser,  # Stratechery is clean HTML
            'generic': self.generic_parser
        }
        
        parser = parsers.get(platform, self.generic_parser)
        return parser.parse(html_content)
    
    def _determine_category(self, sender_name: str, sender_email: str) -> str:
        """Determine newsletter category based on sender"""
        name_lower = sender_name.lower()
        email_lower = sender_email.lower()
        
        # Check against mapping
        for key, category in self.CATEGORY_MAPPING.items():
            if key in name_lower or key in email_lower:
                return category
        
        # Default to product_ai if unknown
        logger.warning(f"Unknown newsletter: {sender_name}, defaulting to product_ai")
        return 'product_ai'
    
    def _create_error_result(self, message_id: str, sender_name: str, 
                            sender_email: str, subject: str, date: str,
                            error_msg: str) -> Dict:
        """Create error result structure"""
        return {
            'message_id': message_id,
            'sender_name': sender_name,
            'sender_email': sender_email,
            'subject': subject,
            'date': date,
            'platform': 'unknown',
            'category': 'product_ai',
            'content': '',
            'title': subject,
            'sections': [],
            'links': [],
            'images': [],
            'metadata': {'error': error_msg},
            'parsing_success': False,
            'needs_review': True
        }


class SubstackParser:
    """Parser for Substack newsletters"""
    
    def parse(self, html_content: str) -> Dict:
        """Parse Substack newsletter HTML"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove unwanted elements
        for element in soup.find_all(['script', 'style']):
            element.decompose()
        
        # Remove Substack footer/boilerplate
        for element in soup.find_all(string=re.compile('View this post on the web|Unsubscribe|Share')):
            if element.parent:
                element.parent.decompose()
        
        # Extract title
        title = ''
        h1 = soup.find('h1')
        if h1:
            title = h1.get_text(strip=True)
            h1.decompose()  # Remove after extracting
        
        # Extract sections
        sections = []
        for heading in soup.find_all(['h2', 'h3']):
            section_title = heading.get_text(strip=True)
            
            # Get content until next heading
            section_content = []
            for sibling in heading.find_next_siblings():
                if sibling.name in ['h2', 'h3']:
                    break
                if sibling.name == 'p':
                    text = sibling.get_text(strip=True)
                    if text:
                        section_content.append(text)
            
            if section_content:
                sections.append({
                    'heading': section_title,
                    'content': '\n'.join(section_content)
                })
        
        # Extract all text content
        content_text = soup.get_text(separator='\n\n', strip=True)
        
        # Clean up excessive whitespace
        content_text = re.sub(r'\n{3,}', '\n\n', content_text)
        
        # Extract links
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if href and not href.startswith(('mailto:', '#', 'javascript:')):
                links.append({
                    'url': href,
                    'text': a.get_text(strip=True)
                })
        
        return {
            'content': content_text,
            'title': title,
            'sections': sections,
            'links': links,
            'images': [],
            'metadata': {'platform': 'substack'},
            'needs_review': False
        }


class BeehiivParser:
    """Parser for Beehiiv newsletters"""
    
    def parse(self, html_content: str) -> Dict:
        """Parse Beehiiv newsletter HTML"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Beehiiv uses table-based layouts
        # Remove scripts and styles
        for element in soup.find_all(['script', 'style']):
            element.decompose()
        
        # Extract text from all meaningful elements
        text_elements = []
        for element in soup.find_all(['h1', 'h2', 'h3', 'p', 'li']):
            text = element.get_text(strip=True)
            if text and len(text) > 10:  # Filter out noise
                text_elements.append(text)
        
        content_text = '\n\n'.join(text_elements)
        
        # Extract title (usually first h1)
        title = ''
        h1 = soup.find('h1')
        if h1:
            title = h1.get_text(strip=True)
        
        # Extract sections (look for emoji markers like ðŸª)
        sections = []
        for element in text_elements:
            # Check if this looks like a section header (emoji + text)
            if re.match(r'^[^\w\s]{1,3}\s+.+', element):
                sections.append({
                    'heading': element,
                    'content': ''
                })
        
        # Note images
        images = []
        for img in soup.find_all('img'):
            src = img.get('src')
            if src:
                images.append(src)
        
        # Extract links
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if href and not href.startswith(('mailto:', '#')):
                links.append({
                    'url': href,
                    'text': a.get_text(strip=True)
                })
        
        return {
            'content': content_text,
            'title': title,
            'sections': sections,
            'links': links,
            'images': images,
            'metadata': {
                'platform': 'beehiiv',
                'image_count': len(images)
            },
            'needs_review': len(images) > 5  # Flag if very image-heavy
        }


class TLDRParser:
    """Parser for TLDR newsletters (TLDR, TLDR AI, TLDR Product)"""
    
    def parse(self, html_content: str) -> Dict:
        """Parse TLDR newsletter HTML"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove scripts and styles
        for element in soup.find_all(['script', 'style']):
            element.decompose()
        
        # TLDR has a specific structure with news items
        # Each item typically has: headline + brief description + link
        
        sections = []
        current_section = None
        
        # Look for section headers and items
        for element in soup.find_all(['h2', 'h3', 'p', 'a']):
            text = element.get_text(strip=True)
            
            # Section headers are usually all caps or have special formatting
            if element.name in ['h2', 'h3'] and text:
                current_section = {
                    'heading': text,
                    'items': []
                }
                sections.append(current_section)
            
            # Items are paragraphs or links
            elif current_section and text and len(text) > 20:
                current_section['items'].append(text)
        
        # Build content text
        content_parts = []
        for section in sections:
            content_parts.append(f"{section['heading']}\n")
            content_parts.extend(section['items'])
            content_parts.append('')  # Blank line between sections
        
        content_text = '\n'.join(content_parts)
        
        # Extract all links
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if href and not href.startswith(('mailto:', '#')):
                links.append({
                    'url': href,
                    'text': a.get_text(strip=True)
                })
        
        return {
            'content': content_text,
            'title': 'TLDR Newsletter',
            'sections': sections,
            'links': links,
            'images': [],
            'metadata': {'platform': 'tldr'},
            'needs_review': False
        }


class ConvertKitParser:
    """Parser for ConvertKit newsletters (Sahil Bloom)"""
    
    def parse(self, html_content: str) -> Dict:
        """Parse ConvertKit newsletter HTML"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove scripts and styles
        for element in soup.find_all(['script', 'style']):
            element.decompose()
        
        # Extract title
        title = ''
        h1 = soup.find('h1')
        if h1:
            title = h1.get_text(strip=True)
        
        # ConvertKit often has clear section structure
        sections = []
        for heading in soup.find_all(['h2', 'h3']):
            section_title = heading.get_text(strip=True)
            
            # Get paragraphs after heading
            section_content = []
            for sibling in heading.find_next_siblings():
                if sibling.name in ['h2', 'h3']:
                    break
                if sibling.name == 'p':
                    text = sibling.get_text(strip=True)
                    if text:
                        section_content.append(text)
            
            if section_content:
                sections.append({
                    'heading': section_title,
                    'content': '\n'.join(section_content)
                })
        
        # Get all content
        content_text = soup.get_text(separator='\n\n', strip=True)
        content_text = re.sub(r'\n{3,}', '\n\n', content_text)
        
        # Extract links
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if href and not href.startswith(('mailto:', '#')):
                links.append({
                    'url': href,
                    'text': a.get_text(strip=True)
                })
        
        return {
            'content': content_text,
            'title': title,
            'sections': sections,
            'links': links,
            'images': [],
            'metadata': {'platform': 'convertkit'},
            'needs_review': False
        }


class GenericParser:
    """Fallback parser for unknown formats"""
    
    def parse(self, html_content: str) -> Dict:
        """Parse generic newsletter HTML"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove unwanted elements
        for element in soup.find_all(['script', 'style', 'footer', 'header']):
            element.decompose()
        
        # Extract all meaningful text
        text = soup.get_text(separator='\n\n', strip=True)
        
        # Clean up whitespace
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        content_text = '\n\n'.join(lines)
        
        # Try to find title
        title = ''
        h1 = soup.find('h1')
        if h1:
            title = h1.get_text(strip=True)
        
        # Extract links
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if href and not href.startswith(('mailto:', '#', 'javascript:')):
                links.append({
                    'url': href,
                    'text': a.get_text(strip=True)
                })
        
        return {
            'content': content_text,
            'title': title,
            'sections': [],
            'links': links,
            'images': [],
            'metadata': {'platform': 'generic'},
            'needs_review': True  # Flag for manual review
        }


def validate_parsed_content(parsed_data: Dict) -> Tuple[bool, Dict]:
    """
    Validate parsed content meets minimum quality standards
    
    Returns:
        (is_valid, validation_checks)
    """
    content = parsed_data.get('content', '')
    
    checks = {
        'has_content': len(content) > 100,
        'has_sentences': '.' in content or '!' in content or '?' in content,
        'no_excessive_whitespace': content.count('\n\n\n') < 5,
        'readable_ratio': True  # Default to true
    }
    
    # Check readable character ratio
    if content:
        readable_chars = sum(c.isalnum() or c.isspace() for c in content)
        checks['readable_ratio'] = (readable_chars / len(content)) > 0.7
    
    is_valid = all(checks.values())
    
    return is_valid, checks
