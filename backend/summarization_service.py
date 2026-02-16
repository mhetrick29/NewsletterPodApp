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
        self.client = Anthropic(api_key=api_key, timeout=300.0)  # 5 minute timeout
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

    def synthesize_themes(self, individual_summaries: List[Dict]) -> Dict:
        """
        Identify overlapping themes across all newsletters for a given day.

        Args:
            individual_summaries: List of already-generated newsletter summaries

        Returns:
            Dict with themes list and synthesis paragraph
        """
        if not individual_summaries:
            return {
                "themes": [],
                "synthesis": "No newsletters to synthesize.",
                "ai_generated": True
            }

        summaries_text = []
        for i, summary in enumerate(individual_summaries, 1):
            summaries_text.append(
                f"Newsletter {i}: {summary.get('sender_name', 'Unknown')}\n"
                f"Title: {summary.get('title', 'No title')}\n"
                f"Summary: {summary.get('summary', 'No summary')}\n"
                f"Key Points: {', '.join(summary.get('key_points', []))}"
            )

        combined = "\n\n".join(summaries_text)

        prompt = f"""You have summaries from {len(individual_summaries)} newsletters received today. Identify the overlapping themes and connections across them.

{combined}

Respond in JSON format:
{{
    "themes": [
        {{
            "title": "Short theme title",
            "description": "1-2 sentence description of this theme and why it matters",
            "sources": ["Newsletter sender names that touch on this theme"]
        }}
    ],
    "synthesis": "A 2-3 sentence overview paragraph connecting the major themes of the day"
}}

Identify 3-5 themes. Focus on genuine overlaps and connections, not forced similarities."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            self._log_usage(response, f"Theme Synthesis ({len(individual_summaries)} newsletters)")

            response_text = response.content[0].text
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]

            result = json.loads(response_text.strip())
            result['ai_generated'] = True
            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse theme synthesis JSON: {e}")
            return {
                "themes": [],
                "synthesis": response.content[0].text[:500] if response else "Failed to synthesize themes",
                "ai_generated": True,
                "parse_error": True
            }
        except Exception as e:
            logger.error(f"Theme synthesis failed: {e}")
            raise

