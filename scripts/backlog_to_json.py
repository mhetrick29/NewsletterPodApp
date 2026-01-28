#!/usr/bin/env python3
"""
Backlog Export Script
Converts BACKLOG.md to JSON and generates import files for Trello/Notion.

Usage:
    python scripts/backlog_to_json.py                    # Export all formats
    python scripts/backlog_to_json.py --format json      # JSON only
    python scripts/backlog_to_json.py --format trello    # Trello CSV
    python scripts/backlog_to_json.py --format notion    # Notion CSV
"""

import re
import json
import csv
import argparse
from pathlib import Path
from datetime import datetime


def parse_backlog_md(filepath: str) -> dict:
    """Parse BACKLOG.md and extract all tasks."""
    with open(filepath, 'r') as f:
        content = f.read()

    phases = []
    current_phase = None

    # Split by phase headers
    lines = content.split('\n')
    i = 0

    while i < len(lines):
        line = lines[i]

        # Detect phase header (# Phase X: or # Future Ideas)
        if line.startswith('# Phase') or line.startswith('# Future'):
            if current_phase:
                phases.append(current_phase)

            phase_match = re.match(r'# (Phase \d+|Future Ideas).*', line)
            if phase_match:
                current_phase = {
                    'name': phase_match.group(1),
                    'full_name': line.replace('# ', ''),
                    'tasks': []
                }
            i += 1
            continue

        # Detect table rows (tasks)
        if line.startswith('|') and current_phase and '---' not in line:
            # Skip header row
            if 'ID' in line and 'Task' in line:
                i += 1
                continue

            # Parse task row
            cells = [c.strip() for c in line.split('|')[1:-1]]
            if len(cells) >= 5:
                task_id = cells[0].strip()
                task_name = cells[1].strip().replace('**', '')  # Remove bold
                status = cells[2].strip().replace('`', '')  # Remove backticks
                priority = cells[3].strip()
                labels = [l.strip() for l in cells[4].split(',')]

                if task_id and task_id not in ['ID', '----']:
                    current_phase['tasks'].append({
                        'id': task_id,
                        'name': task_name,
                        'status': status,
                        'priority': priority,
                        'labels': labels,
                        'phase': current_phase['name']
                    })

        i += 1

    # Don't forget last phase
    if current_phase:
        phases.append(current_phase)

    return {
        'exported_at': datetime.now().isoformat(),
        'phases': phases,
        'stats': calculate_stats(phases)
    }


def calculate_stats(phases: list) -> dict:
    """Calculate completion statistics."""
    stats = {
        'total_tasks': 0,
        'by_status': {},
        'by_priority': {},
        'by_phase': {}
    }

    for phase in phases:
        phase_total = len(phase['tasks'])
        phase_done = sum(1 for t in phase['tasks'] if t['status'] == 'done')

        stats['by_phase'][phase['name']] = {
            'total': phase_total,
            'done': phase_done,
            'percent': round(phase_done / phase_total * 100) if phase_total > 0 else 0
        }

        for task in phase['tasks']:
            stats['total_tasks'] += 1

            status = task['status']
            stats['by_status'][status] = stats['by_status'].get(status, 0) + 1

            priority = task['priority']
            stats['by_priority'][priority] = stats['by_priority'].get(priority, 0) + 1

    return stats


def export_json(data: dict, output_path: str):
    """Export to JSON format."""
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Exported JSON to {output_path}")


def export_trello_csv(data: dict, output_path: str):
    """
    Export to Trello-compatible CSV.
    Trello CSV format: Card Name, Card Description, Labels, List Name
    """
    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Card Name', 'Card Description', 'Labels', 'List Name'])

        for phase in data['phases']:
            list_name = phase['full_name']

            for task in phase['tasks']:
                card_name = f"[{task['id']}] {task['name']}"
                description = f"Priority: {task['priority']}\nStatus: {task['status']}"
                labels = ','.join(task['labels'])

                # Map status to Trello list
                if task['status'] == 'done':
                    list_name = 'Done'
                elif task['status'] == 'in-progress':
                    list_name = 'In Progress'
                elif task['status'] == 'ready':
                    list_name = 'Ready'
                else:
                    list_name = phase['full_name']

                writer.writerow([card_name, description, labels, list_name])

    print(f"Exported Trello CSV to {output_path}")


def export_notion_csv(data: dict, output_path: str):
    """
    Export to Notion-compatible CSV.
    Can be imported as a database with properties.
    """
    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['ID', 'Name', 'Status', 'Priority', 'Phase', 'Labels'])

        for phase in data['phases']:
            for task in phase['tasks']:
                writer.writerow([
                    task['id'],
                    task['name'],
                    task['status'].title(),
                    task['priority'],
                    phase['name'],
                    ', '.join(task['labels'])
                ])

    print(f"Exported Notion CSV to {output_path}")


def export_github_issues_json(data: dict, output_path: str):
    """
    Export to GitHub Issues format (for gh CLI bulk import).
    """
    issues = []

    for phase in data['phases']:
        for task in phase['tasks']:
            if task['status'] not in ['done']:  # Only export incomplete tasks
                issue = {
                    'title': f"[{task['id']}] {task['name']}",
                    'body': f"**Phase:** {phase['name']}\n**Priority:** {task['priority']}\n**Status:** {task['status']}",
                    'labels': task['labels'] + [task['priority'], phase['name'].lower().replace(' ', '-')]
                }
                issues.append(issue)

    with open(output_path, 'w') as f:
        json.dump(issues, f, indent=2)

    print(f"Exported GitHub Issues JSON to {output_path}")
    print(f"  To create issues: gh issue create --title \"...\" --body \"...\" --label \"...\"")


def main():
    parser = argparse.ArgumentParser(description='Export BACKLOG.md to various formats')
    parser.add_argument('--format', choices=['all', 'json', 'trello', 'notion', 'github'],
                        default='all', help='Export format')
    parser.add_argument('--input', default='docs/BACKLOG.md', help='Input markdown file')
    parser.add_argument('--output-dir', default='docs/exports', help='Output directory')
    args = parser.parse_args()

    # Find project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    input_path = project_root / args.input
    output_dir = project_root / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    # Parse backlog
    print(f"Parsing {input_path}...")
    data = parse_backlog_md(str(input_path))

    print(f"\nFound {data['stats']['total_tasks']} tasks across {len(data['phases'])} phases")
    print(f"Status breakdown: {data['stats']['by_status']}")

    # Export based on format
    if args.format in ['all', 'json']:
        export_json(data, str(output_dir / 'backlog.json'))

    if args.format in ['all', 'trello']:
        export_trello_csv(data, str(output_dir / 'backlog_trello.csv'))

    if args.format in ['all', 'notion']:
        export_notion_csv(data, str(output_dir / 'backlog_notion.csv'))

    if args.format in ['all', 'github']:
        export_github_issues_json(data, str(output_dir / 'backlog_github_issues.json'))

    print(f"\nExports saved to {output_dir}/")


if __name__ == '__main__':
    main()
