#!/usr/bin/env python3
"""
Search for recent updates from major AI companies.
Catches breaking news that newsletters haven't covered yet.
"""

import os
import sys
import json
import time
from datetime import datetime
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

# Major AI companies to monitor
COMPANIES = [
    {"name": "OpenAI", "query": "OpenAI news updates announcements"},
    {"name": "Anthropic", "query": "Anthropic Claude news updates"},
    {"name": "Google AI", "query": "Google Gemini DeepMind AI news"},
    {"name": "Microsoft AI", "query": "Microsoft Copilot AI news"},
    {"name": "Mistral", "query": "Mistral AI news updates"},
    {"name": "xAI", "query": "xAI Grok Elon Musk news"},
    {"name": "Perplexity", "query": "Perplexity AI news updates"},
    {"name": "Cursor", "query": "Cursor AI IDE news updates"},
    {"name": "Meta AI", "query": "Meta Llama AI news"},
    {"name": "Cohere", "query": "Cohere AI enterprise news"},
]


def search_company(client, company):
    """Search for recent news about a specific company"""
    prompt = f"""Search the web for news about {company['name']} from the past 24 hours.

Focus on: product launches, model releases, partnerships, funding, leadership changes, major announcements.

If you find relevant news, summarize the key updates in 2-3 sentences.
If there's nothing significant in the past 24 hours, return "No major updates."
"""

    try:
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
    except Exception as e:
        return f"Search failed: {str(e)}"


def main():
    if len(sys.argv) < 2:
        print("Usage: python search_companies.py <output.json>")
        sys.exit(1)

    output_file = sys.argv[1]

    if not os.environ.get('ANTHROPIC_API_KEY'):
        print("Error: ANTHROPIC_API_KEY not set")
        sys.exit(1)

    client = Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))

    print(f"Searching for updates from {len(COMPANIES)} major AI companies...")

    company_updates = []
    significant_updates = 0

    for i, company in enumerate(COMPANIES, 1):
        print(f"\n[{i}/{len(COMPANIES)}] {company['name']}...")

        result = search_company(client, company)

        has_updates = 'no major updates' not in result.lower()
        company_updates.append({
            'company': company['name'],
            'search_query': company['query'],
            'result': result,
            'has_updates': has_updates
        })

        if has_updates:
            print(f"  Found updates")
            significant_updates += 1
        else:
            print(f"  No major updates")

        if i < len(COMPANIES):
            time.sleep(15)  # Rate limiting between searches

    output = {
        'searched_at': datetime.now().isoformat(),
        'companies_searched': len(COMPANIES),
        'significant_updates': significant_updates,
        'updates': company_updates
    }

    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nCompany search complete: {significant_updates}/{len(COMPANIES)} had updates")
    print(f"  Saved to {output_file}")


if __name__ == "__main__":
    main()
