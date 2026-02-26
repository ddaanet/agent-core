#!/usr/bin/env bash
# PreToolUse hook to block writes to symlinked files from agent-core
# Redirects writes to correct path relative to project root

set -euo pipefail

# Read JSON input from stdin
input=$(cat)

# Extract tool name and file path
tool_name=$(echo "$input" | jq -r '.tool_name // empty')
file_path=$(echo "$input" | jq -r '.tool_input.file_path // empty')

# Only check Write and Edit tools
if [[ "$tool_name" != "Write" && "$tool_name" != "Edit" ]]; then
  exit 0
fi

# Check if file exists and is a symlink
if [[ -L "$file_path" ]]; then
  # Resolve the symlink target
  target=$(readlink "$file_path")

  # Check if it's a symlink to agent-core
  if [[ "$target" == *"agent-core/"* ]]; then
    # Convert relative path to absolute
    if [[ "$target" != /* ]]; then
      dir=$(dirname "$file_path")
      target="$dir/$target"
    fi

    # Normalize the path
    target=$(cd "$(dirname "$target")" && pwd)/$(basename "$target")

    # Block via permissionDecision:deny
    # Extract just the relative path from project root if env var is set
    if [[ -n "${CLAUDE_PROJECT_DIR:-}" ]]; then
      relative_target="${target#$CLAUDE_PROJECT_DIR/}"
    else
      relative_target="$target"
    fi

    jq -n \
      --arg reason "Symlinked to agent-core — edit $relative_target directly" \
      --arg ctx "This file is symlinked to agent-core. Instead, $tool_name file: $relative_target" \
      --arg msg "🚫 Symlink — edit $relative_target" \
      '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":$reason,"additionalContext":$ctx},"systemMessage":$msg}'
    exit 0
  fi
fi

# Allow operation
exit 0
