#!/usr/bin/env python3
"""
Web search for news about extracted themes.
Uses Claude's web search tool to find recent news related to newsletter themes.
"""

import os
import sys
import json
from anthropic import Anthropic


def search_theme(client, theme):
    """Search web for recent news about a theme"""
    prompt = f"""Search the web for recent news about: {theme['query']}

Focus on: {theme['description']}

Find 2-3 recent news articles or developments from the past week.
Summarize key findings in 2-3 sentences."""

    message = client.messages.create(
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
