#!/bin/sh
set -e

PARSERS_DIR="/app/parsers"
mkdir -p "$PARSERS_DIR"

if [ -n "${PARSERS_CREDENTIALS_JSON_B64:-}" ]; then
  echo "$PARSERS_CREDENTIALS_JSON_B64" | base64 -d > "$PARSERS_DIR/credentials.json"
fi

if [ -n "${PARSERS_TOKEN_PICKLE_B64:-}" ]; then
  echo "$PARSERS_TOKEN_PICKLE_B64" | base64 -d > "$PARSERS_DIR/token.pickle"
fi

exec uvicorn main:app --host 0.0.0.0 --port "${PORT:-8000}"
