#!/bin/bash
# Daily Newsletter Briefing Pipeline
# Extracts newsletters -> parses -> enriches with web context -> generates summary

set -e  # Exit on any error

# ============================================
# CONFIGURATION
# ============================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
BRIEFINGS_DIR="${BRIEFINGS_DIR:-$HOME/Briefings}"
VENV_PATH="$PROJECT_DIR/backend/venv"

# ============================================
# SETUP
# ============================================
DATE=$(date +%Y-%m-%d)
DAYS_BACK="${PIPELINE_DAYS_BACK:-1}"
OUTPUT_DIR="$BRIEFINGS_DIR/$DATE"
TEMP_DIR="/tmp/newsletters-$DATE"

# Load environment variables
if [ -f "$PROJECT_DIR/.env" ]; then
    export $(cat "$PROJECT_DIR/.env" | grep -v '^#' | grep -v '^$' | xargs)
fi

# Create directories
mkdir -p "$OUTPUT_DIR/sources"
mkdir -p "$TEMP_DIR/raw"

cd "$PROJECT_DIR"

# Activate virtual environment if it exists
if [ -f "$VENV_PATH/bin/activate" ]; then
    source "$VENV_PATH/bin/activate"
elif [ -f "$VENV_PATH/Scripts/activate" ]; then
    source "$VENV_PATH/Scripts/activate"
fi

# Verify ANTHROPIC_API_KEY is set
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "Error: ANTHROPIC_API_KEY not set"
    echo "Set it in $PROJECT_DIR/.env or export it"
    exit 1
fi

# ============================================
# PIPELINE
# ============================================
echo "============================================"
echo "Daily Newsletter Briefing"
echo "  $(date '+%A, %B %d, %Y at %I:%M %p')"
echo "============================================"
echo

# Step 1: Extract newsletters from Gmail
echo "Step 1: Extracting newsletters from Gmail..."
python parsers/gmail_newsletter_extractor.py \
    --output-html "$TEMP_DIR/raw" \
    --days "$DAYS_BACK" \
    --max-results 100

if [ $? -ne 0 ]; then
    echo "Extraction failed"
    exit 1
fi
echo

# Step 2: Parse HTML to clean JSON
echo "Step 2: Parsing newsletter content..."
python parsers/newsletter_parser.py \
    "$TEMP_DIR/raw"/*.html \
    --output "$TEMP_DIR/parsed.json"

if [ $? -ne 0 ]; then
    echo "Parsing failed"
    exit 1
fi
echo

# Step 3: Extract key themes
echo "Step 3: Extracting key themes..."
SKIP_SEARCH=false
python scripts/extract_themes.py \
    "$TEMP_DIR/parsed.json" \
    "$TEMP_DIR/themes.json" || {
    echo "Theme extraction failed, continuing without web search..."
    SKIP_SEARCH=true
}
echo

# Step 4a: Web search for news about themes
SEARCH_RESULTS=""
if [ "$SKIP_SEARCH" = false ]; then
    echo "Step 4a: Searching web for related news..."
    python scripts/search_themes.py \
        "$TEMP_DIR/themes.json" \
        "$TEMP_DIR/search_results.json" && {
        SEARCH_RESULTS="$TEMP_DIR/search_results.json"
    } || {
        echo "Theme search failed, continuing without those results..."
    }
else
    echo "Step 4a: Skipping theme search (no themes extracted)"
fi
echo

# Step 4b: Search major AI companies for updates
echo "Step 4b: Searching for AI company updates..."
COMPANY_UPDATES=""
python scripts/search_companies.py \
    "$TEMP_DIR/company_updates.json" && {
    COMPANY_UPDATES="$TEMP_DIR/company_updates.json"
} || {
    echo "Company search failed, continuing without those results..."
}
echo

# Step 5: Generate enriched summary
echo "Step 5: Generating summary with Claude API..."
SUMMARY_ARGS="$TEMP_DIR/parsed.json $OUTPUT_DIR/summary.md"
[ -n "$SEARCH_RESULTS" ] && [ -f "$SEARCH_RESULTS" ] && SUMMARY_ARGS="$SUMMARY_ARGS $SEARCH_RESULTS"
[ -n "$COMPANY_UPDATES" ] && [ -f "$COMPANY_UPDATES" ] && SUMMARY_ARGS="$SUMMARY_ARGS $COMPANY_UPDATES"

python scripts/generate_summary.py $SUMMARY_ARGS

if [ $? -ne 0 ]; then
    echo "Summary generation failed"
    exit 1
fi
echo

# Step 6: Package everything for Q&A
echo "Step 6: Packaging for Q&A..."
cp -r "$TEMP_DIR/raw"/* "$OUTPUT_DIR/sources/" 2>/dev/null || true
cp "$TEMP_DIR/parsed.json" "$OUTPUT_DIR/parsed.json"

# Copy optional files if they exist
[ -f "$TEMP_DIR/themes.json" ] && cp "$TEMP_DIR/themes.json" "$OUTPUT_DIR/"
[ -f "$TEMP_DIR/search_results.json" ] && cp "$TEMP_DIR/search_results.json" "$OUTPUT_DIR/"
[ -f "$TEMP_DIR/company_updates.json" ] && cp "$TEMP_DIR/company_updates.json" "$OUTPUT_DIR/"

# Create README in the output folder
cat > "$OUTPUT_DIR/README.txt" << EOF
Newsletter Briefing - $DATE
Generated: $(date)

Files in this folder:
- summary.md            : Daily briefing (enriched with web context + company news)
- parsed.json           : Structured newsletter data
- themes.json           : Key themes extracted from newsletters
- search_results.json   : Web search results about the themes
- company_updates.json  : Latest updates from major AI companies
- sources/              : Raw newsletter HTML files

How to use for Q&A:
1. Read summary.md for the overview
2. Drag this entire folder into Claude chat
3. Ask follow-up questions about the content
EOF

# Cleanup temp files
rm -rf "$TEMP_DIR"

echo "============================================"
echo "Briefing Complete!"
echo "============================================"
echo
echo "Output location: $OUTPUT_DIR"
echo
echo "Next steps:"
echo "  1. Read: $OUTPUT_DIR/summary.md"
echo "  2. For Q&A: drag $OUTPUT_DIR folder into Claude"
echo

# macOS notification (silent fail if not on macOS)
osascript -e 'display notification "Your daily briefing is ready" with title "Newsletter Agent"' 2>/dev/null || true

exit 0
