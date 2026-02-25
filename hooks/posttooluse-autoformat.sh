#!/usr/bin/env bash
set -euo pipefail

file_path=$(python3 -c 'import sys,json; d=json.load(sys.stdin); print(d.get("tool_input",{}).get("file_path",""))' 2>/dev/null || echo "")

if [[ -z "$file_path" ]]; then
  exit 0
fi

if [[ ! "$file_path" =~ \.py$ ]]; then
  exit 0
fi

ruff format --quiet "$file_path" 2>/dev/null || true

if command -v docformatter >/dev/null 2>&1; then
  docformatter --in-place "$file_path" 2>/dev/null || true
fi

exit 0
