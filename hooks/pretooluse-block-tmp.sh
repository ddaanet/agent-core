#!/usr/bin/env bash
# PreToolUse hook to block writes to /tmp/
# Enforces project-local tmp/ directory usage per CLAUDE.md File System Rules

set -euo pipefail

# Read JSON input from stdin
input=$(cat)

# Extract tool name and file path
tool_name=$(echo "$input" | jq -r '.tool_name // empty')
file_path=$(echo "$input" | jq -r '.tool_input.file_path // empty')

# Only check Write and Edit tools
if [[ "$tool_name" == "Write" || "$tool_name" == "Edit" ]]; then
  # Check if path starts with /tmp/ or /private/tmp/
  if [[ "$file_path" =~ ^(/tmp/|/private/tmp/) ]]; then
    # Block via permissionDecision:deny
    jq -n '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"Write to /tmp/ blocked — use project-local tmp/ instead","additionalContext":"Do not write to /tmp/. Use project-local tmp/ directory (per CLAUDE.md File System Rules)."},"systemMessage":"🚫 /tmp/ write blocked — use project-local tmp/"}'
    exit 0
  fi
fi

# Allow operation
exit 0
