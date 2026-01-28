"""
AI Summarization Service using Claude API
Phase 2: Intelligent newsletter summarization
"""
import os
import json
import logging
from typing import Dict, List, Optional
from anthropic import Anthropic
from datetime import datetime

logger = logging.getLogger(__name__)

# Cost per 1M tokens (as of Jan 2025)
# Update these if pricing changes
PRICING = {
    "claude-sonnet-4-20250514": {"input": 3.00, "output": 15.00},
    "claude-3-5-sonnet-20241022": {"input": 3.00, "output": 15.00},
    "claude-3-haiku-20240307": {"input": 0.25, "output": 1.25},
}


class SummarizationService:
    """Service for AI-powered newsletter summarization using Claude"""

    def __init__(self):
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY environment variable not set. "
                "Get your API key at https://console.anthropic.com/"
            )
        self.client = Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-20250514"
        self.session_stats = {
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "total_cost": 0.0,
            "api_calls": 0,
            "started_at": datetime.now().isoformat()
        }

    def _log_usage(self, response, context: str = ""):
        """Log token usage and cost for an API call"""
        usage = response.usage
        input_tokens = usage.input_tokens
        output_tokens = usage.output_tokens

        # Calculate cost
        pricing = PRICING.get(self.model, PRICING["claude-sonnet-4-20250514"])
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        total_cost = input_cost + output_cost

        # Update session stats
        self.session_stats["total_input_tokens"] += input_tokens
        self.session_stats["total_output_tokens"] += output_tokens
        self.session_stats["total_cost"] += total_cost
        self.session_stats["api_calls"] += 1

        # Log the usage
        logger.info(
            f"[AI USAGE] {context} | "
            f"Input: {input_tokens:,} tokens (${input_cost:.4f}) | "
            f"Output: {output_tokens:,} tokens (${output_cost:.4f}) | "
            f"Total: ${total_cost:.4f}"
        )
        logger.info(
            f"[SESSION TOTAL] "
            f"Calls: {self.session_stats['api_calls']} | "
            f"Tokens: {self.session_stats['total_input_tokens']:,} in / "
            f"{self.session_stats['total_output_tokens']:,} out | "
            f"Cost: ${self.session_stats['total_cost']:.4f}"
        )

    def summarize_newsletter(self, html_content: str, sender_name: str, subject: str) -> Dict:
        """
        Use Claude to read and summarize a newsletter like a human would.

        Args:
            html_content: Raw HTML of the newsletter
            sender_name: Name of the newsletter sender
            subject: Email subject line

        Returns:
            Dict with title, summary, key_points, and sections
        """
        prompt = f"""You are reading a newsletter email. Read it like a human would and extract the key information.

Newsletter from: {sender_name}
Subject: {subject}

Here is the newsletter HTML content:

<newsletter>
{html_content[:50000]}
</newsletter>

Please analyze this newsletter and provide:

1. **Title**: The main title or headline of this newsletter issue
2. **Summary**: A 2-3 sentence summary of what this newsletter covers
3. **Key Points**: 3-5 bullet points of the most important takeaways
4. **Sections**: Break down the newsletter into its main sections, each with:
   - A heading
   - A brief summary of that section (1-2 sentences)
   - Any notable links or resources mentioned

Respond in JSON format:
{{
    "title": "...",
    "summary": "...",
    "key_points": ["...", "...", "..."],
    "sections": [
        {{
            "heading": "...",
            "summary": "...",
            "links": [{{"text": "...", "context": "..."}}]
        }}
    ]
}}

Focus on the actual content - ignore navigation, footers, unsubscribe links, and other boilerplate.
If there are images or charts referenced, describe what they likely show based on context."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # Log usage and cost
            self._log_usage(response, f"Newsletter: {sender_name}")

            # Parse the JSON response
            response_text = response.content[0].text

            # Try to extract JSON from the response
            # Sometimes Claude wraps it in markdown code blocks
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]

            result = json.loads(response_text.strip())
            result['ai_generated'] = True
            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Claude response as JSON: {e}")
            # Return a basic structure with the raw response
            return {
                "title": subject,
                "summary": response.content[0].text[:500] if response else "Failed to generate summary",
                "key_points": [],
                "sections": [],
                "ai_generated": True,
                "parse_error": True
            }
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            raise

    def summarize_category(self, newsletters: List[Dict], category_name: str) -> Dict:
        """
        Create a single combined summary for all newsletters in a category.

        Args:
            newsletters: List of newsletter dicts with html_content, sender_name, subject
            category_name: Display name of the category

        Returns:
            Dict with combined summary, key_points, and per-newsletter highlights
        """
        if not newsletters:
            return {
                "summary": "No newsletters in this category.",
                "key_points": [],
                "newsletters": [],
                "ai_generated": True
            }

        # Build context from all newsletters
        newsletter_context = []
        for i, nl in enumerate(newsletters, 1):
            # Truncate HTML to avoid token limits
            html = nl.get('html_content', '')[:30000] if nl.get('html_content') else ''
            newsletter_context.append(f"""
--- Newsletter {i}: {nl['sender_name']} ---
Subject: {nl['subject']}
Content:
{html}
""")

        combined_content = "\n".join(newsletter_context)

        prompt = f"""You are reading {len(newsletters)} newsletters from the "{category_name}" category. Read them all and create a unified summary.

{combined_content}

Create a combined summary that:
1. Synthesizes the key themes and stories across all newsletters
2. Highlights the most important news/insights
3. Notes any overlapping coverage or different perspectives on the same topic
4. Calls out the source newsletter for key points

Respond in JSON format:
{{
    "summary": "2-3 paragraph summary of the category's key content",
    "key_points": [
        "Key point 1 (Source: Newsletter Name)",
        "Key point 2 (Source: Newsletter Name)",
        ...
    ],
    "newsletters": [
        {{
            "sender_name": "...",
            "one_liner": "One sentence summary of this newsletter's unique contribution"
        }}
    ]
}}

Focus on substance - ignore ads, promotions, and boilerplate."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # Log usage
            self._log_usage(response, f"Category: {category_name} ({len(newsletters)} newsletters)")

            # Parse response
            response_text = response.content[0].text
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]

            result = json.loads(response_text.strip())
            result['ai_generated'] = True
            result['newsletter_count'] = len(newsletters)
            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse category summary JSON: {e}")
            return {
                "summary": response.content[0].text[:1000] if response else "Failed to generate summary",
                "key_points": [],
                "newsletters": [],
                "ai_generated": True,
                "parse_error": True
            }
        except Exception as e:
            logger.error(f"Category summary failed: {e}")
            raise

    def summarize_multiple(self, newsletters: List[Dict]) -> Dict:
        """
        Create a combined summary of multiple newsletters, grouped by category.

        Args:
            newsletters: List of newsletter dicts with html_content, sender_name, subject, category

        Returns:
            Dict with category-grouped summaries
        """
        # Group by category
        by_category = {}
        for nl in newsletters:
            cat = nl.get('category', 'uncategorized')
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(nl)

        # Summarize each newsletter
        results = {}
        for category, nls in by_category.items():
            results[category] = {
                'newsletters': []
            }
            for nl in nls:
                try:
                    summary = self.summarize_newsletter(
                        nl['html_content'],
                        nl['sender_name'],
                        nl['subject']
                    )
                    summary['id'] = nl.get('id')
                    summary['sender_name'] = nl['sender_name']
                    results[category]['newsletters'].append(summary)
                except Exception as e:
                    logger.error(f"Failed to summarize newsletter {nl.get('id')}: {e}")
                    results[category]['newsletters'].append({
                        'id': nl.get('id'),
                        'sender_name': nl['sender_name'],
                        'title': nl['subject'],
                        'summary': 'Failed to generate AI summary',
                        'error': str(e)
                    })

        return results

    def generate_daily_briefing(self, newsletters: List[Dict]) -> str:
        """
        Generate a cohesive daily briefing from multiple newsletters.
        This could be used as a podcast script.

        Args:
            newsletters: List of newsletter dicts

        Returns:
            A natural language briefing suitable for reading aloud
        """
        # First summarize each newsletter
        summaries = []
        for nl in newsletters:
            try:
                summary = self.summarize_newsletter(
                    nl['html_content'],
                    nl['sender_name'],
                    nl['subject']
                )
                summary['sender_name'] = nl['sender_name']
                summary['category'] = nl.get('category', 'general')
                summaries.append(summary)
            except Exception as e:
                logger.error(f"Failed to summarize: {e}")
                continue

        if not summaries:
            return "No newsletters to summarize today."

        # Now create a cohesive briefing
        briefing_prompt = f"""You are creating a daily newsletter briefing that will be read aloud as a podcast.

Here are today's newsletter summaries:

{json.dumps(summaries, indent=2)}

Create a natural, conversational briefing that:
1. Opens with a brief greeting and overview of what's covered
2. Groups related topics together logically
3. Highlights the most important stories first
4. Uses natural transitions between topics
5. Ends with a brief wrap-up

The tone should be informative but conversational, like a morning news podcast.
Aim for about 3-5 minutes of speaking time (roughly 500-750 words).

Do not use any special formatting - just plain text that reads naturally aloud."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                messages=[
                    {"role": "user", "content": briefing_prompt}
                ]
            )

            # Log usage and cost
            self._log_usage(response, "Daily Briefing")

            return response.content[0].text
        except Exception as e:
            logger.error(f"Failed to generate briefing: {e}")
            raise
