#!/usr/bin/env python3
"""
Generate daily newsletter summary using Claude API.
Enriched with web search results about themes and major company updates.
"""

import os
import sys
import json
from datetime import datetime

# Add backend to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from summarization_service import SummarizationService


def main():
    if len(sys.argv) < 3:
        print("Usage: python generate_summary.py <parsed.json> <output.md> [search_results.json] [company_updates.json]")
        print()
        print("Arguments:")
        print("  parsed.json          - JSON file with parsed newsletters")
        print("  output.md            - Output markdown file for summary")
        print("  search_results.json  - (Optional) Web search results about themes")
        print("  company_updates.json - (Optional) Updates from major AI companies")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    search_file = sys.argv[3] if len(sys.argv) > 3 else None
    company_file = sys.argv[4] if len(sys.argv) > 4 else None

    if not os.environ.get('ANTHROPIC_API_KEY'):
        print("Error: ANTHROPIC_API_KEY environment variable not set")
        sys.exit(1)

    # Load parsed newsletters
    print(f"Loading newsletters from {input_file}...")
    try:
        with open(input_file, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {input_file}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {input_file}")
        sys.exit(1)

    newsletters = data.get('newsletters', [])
    print(f"  Found {len(newsletters)} newsletters")

    if not newsletters:
        print("Error: No newsletters found in input file")
        sys.exit(1)

    # Build additional context from search results and company updates
    context_parts = []

    if search_file and os.path.exists(search_file):
        print(f"Loading theme search results from {search_file}...")
        with open(search_file, 'r') as f:
            search_results = json.load(f)

        if search_results:
            context_parts.append("\n### Web News About Newsletter Themes:\n")
            for result in search_results:
                if result.get('search_result'):
                    theme = result['theme']
                    context_parts.append(f"\n**{theme['query']}**: {result['search_result']}")
            print(f"  Found search results for {len(search_results)} themes")

    if company_file and os.path.exists(company_file):
        print(f"Loading company updates from {company_file}...")
        with open(company_file, 'r') as f:
            company_data = json.load(f)

        updates_with_news = [u for u in company_data.get('updates', []) if u.get('has_updates')]

        if updates_with_news:
            context_parts.append("\n### Recent Updates from Major AI Companies:\n")
            for update in updates_with_news:
                context_parts.append(f"\n**{update['company']}**: {update['result']}")
            print(f"  Found updates from {len(updates_with_news)} companies")

    search_context = ''.join(context_parts) if context_parts else None

    # Generate summary
    print("Generating summary with Claude API...")
    try:
        service = SummarizationService()
        summary = service.generate_daily_summary(newsletters, additional_context=search_context)
    except Exception as e:
        print(f"Error generating summary: {e}")
        sys.exit(1)

    # Add header with metadata
    date_str = datetime.now().strftime("%A, %B %d, %Y")
    sources = ' | '.join([n.get('sender_name', 'Unknown') for n in newsletters[:8]])
    if len(newsletters) > 8:
        sources += f" | +{len(newsletters) - 8} more"

    header = f"""# Newsletter Summary - {date_str}

**Sources:** {sources}
**Newsletters analyzed:** {len(newsletters)}

---

"""

    full_summary = header + summary

    # Save summary
    print(f"Saving summary to {output_file}...")
    os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(full_summary)

    print()
    print("Summary generated successfully!")
    print(f"  View at: {output_file}")


if __name__ == "__main__":
    main()
