#!/usr/bin/env bash
# PreToolUse hook to block writes to /tmp/
# Enforces project-local tmp/ directory usage per CLAUDE.md File System Rules

set -euo pipefail

# Read JSON input from stdin
input=$(cat)

# Extract tool name and file path
tool_name=$(echo "$input" | jq -r '.tool_name // empty')
file_path=$(echo "$input" | jq -r '.tool_input.file_path // empty')

# Only check Write tool
if [[ "$tool_name" == "Write" ]]; then
  # Check if path starts with /tmp/ or /private/tmp/
  if [[ "$file_path" =~ ^(/tmp/|/private/tmp/) ]]; then
    # Block the operation - output plain message to stderr and exit 2
    echo "🚫 **BLOCKED: Do not write to /tmp/. Use project-local tmp/ instead.**" >&2
    exit 2
  fi
fi

# Allow operation
exit 0
