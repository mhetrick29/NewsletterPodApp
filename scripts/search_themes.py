#!/usr/bin/env python3
"""
Web search for news about extracted themes.
Uses Claude's web search tool to find recent news related to newsletter themes.
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


def search_theme(client, theme):
    """Search web for recent news about a theme"""
    prompt = f"""Search the web for recent news about: {theme['query']}

Focus on: {theme['description']}

Find 2-3 recent news articles or developments from the past week.
Summarize key findings in 2-3 sentences."""

    message = call_with_retry(
        client,
        model="claude-sonnet-4-20250514",
        max_tokens=500,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": prompt}]
    )

    results = []
    for block in message.content:
        if hasattr(block, 'text') and block.text:
            results.append(block.text)

    return ' '.join(results)


def main():
    if len(sys.argv) < 3:
        print("Usage: python search_themes.py <themes.json> <search_results.json>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    if not os.environ.get('ANTHROPIC_API_KEY'):
        print("Error: ANTHROPIC_API_KEY not set")
        sys.exit(1)

    print(f"Loading themes from {input_file}...")
    with open(input_file, 'r') as f:
        themes = json.load(f)

    print(f"  Found {len(themes)} themes to search")

    client = Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))

    search_results = []
    for i, theme in enumerate(themes, 1):
        print(f"\nSearching {i}/{len(themes)}: {theme['query']}")

        try:
            result = search_theme(client, theme)
            search_results.append({
                'theme': theme,
                'search_result': result
            })
            print(f"  Found relevant news")
            if i < len(themes):
                time.sleep(15)  # Rate limiting between searches
        except Exception as e:
            print(f"  Search failed: {e}")
            search_results.append({
                'theme': theme,
                'search_result': None,
                'error': str(e)
            })

    with open(output_file, 'w') as f:
        json.dump(search_results, f, indent=2)

    print(f"\nSearch results saved to {output_file}")


if __name__ == "__main__":
    main()
