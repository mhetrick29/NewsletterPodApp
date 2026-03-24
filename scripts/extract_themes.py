#!/usr/bin/env python3
"""
Extract key themes from parsed newsletters.
Uses Claude to identify 3-5 cross-cutting themes for web search enrichment.
"""

import os
import sys
import json
import time
from anthropic import Anthropic, RateLimitError

MAX_RETRIES = 5
BASE_RETRY_DELAY = 60


def call_with_retry(client, **kwargs):
    """Call Claude API with exponential backoff on rate limit errors."""
    for attempt in range(MAX_RETRIES):
        try:
            return client.messages.create(**kwargs)
        except RateLimitError as e:
            if attempt == MAX_RETRIES - 1:
                raise
            retry_after = getattr(e, 'response', None)
            wait = BASE_RETRY_DELAY * (2 ** attempt)
            if retry_after and hasattr(retry_after, 'headers'):
                wait = int(retry_after.headers.get('retry-after', wait))
            print(f"  Rate limited, waiting {wait}s (attempt {attempt + 1}/{MAX_RETRIES})...")
            time.sleep(wait)


def extract_themes(newsletters):
    """Extract 3-5 key themes using Claude"""
    client = Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))

    # Build context from headlines and content previews
    context_parts = []
    for nl in newsletters[:15]:
        sender = nl.get('sender_name', 'Unknown')
        subject = nl.get('subject', 'No Subject')
        context_parts.append(f"{sender}: {subject}")
        content_preview = (nl.get('content') or '')[:200]
        if content_preview:
            context_parts.append(f"  > {content_preview}...")

    context = "\n".join(context_parts)

    prompt = f"""You are analyzing newsletter headlines to identify key themes.

Here are today's newsletter subjects and previews:

{context}

Identify 3-5 key themes that appear across multiple newsletters.

For each theme, provide:
1. A 2-4 word search query (optimized for web search)
2. A one-sentence description

Output as JSON:
[
  {{"query": "anthropic enterprise growth", "description": "Anthropic's dominance in enterprise AI spending"}},
  {{"query": "chinese AI models", "description": "Chinese labs releasing frontier-competitive models"}}
]

Only output the JSON array, nothing else."""

    message = call_with_retry(
        client,
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )

    response_text = message.content[0].text.strip()
    # Handle possible markdown code blocks
    if "```json" in response_text:
        response_text = response_text.split("```json")[1].split("```")[0]
    elif "```" in response_text:
        response_text = response_text.split("```")[1].split("```")[0]

    return json.loads(response_text.strip())


def main():
    if len(sys.argv) < 3:
        print("Usage: python extract_themes.py <parsed.json> <themes.json>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    if not os.environ.get('ANTHROPIC_API_KEY'):
        print("Error: ANTHROPIC_API_KEY not set")
        sys.exit(1)

    print(f"Loading newsletters from {input_file}...")
    with open(input_file, 'r') as f:
        data = json.load(f)

    newsletters = data.get('newsletters', [])
    print(f"  Found {len(newsletters)} newsletters")

    print("Extracting themes with Claude...")
    themes = extract_themes(newsletters)
    print(f"  Identified {len(themes)} themes:")
    for theme in themes:
        print(f"    - {theme['query']}: {theme['description']}")

    with open(output_file, 'w') as f:
        json.dump(themes, f, indent=2)

    print(f"\nThemes saved to {output_file}")


if __name__ == "__main__":
    main()
