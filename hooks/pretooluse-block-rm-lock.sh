#!/usr/bin/env bash
# PreToolUse hook to block removal of .git/index.lock files
# Enforces "when git lock error occurs" decision: never delete lock, retry git command

set -euo pipefail

input=$(cat)
command=$(echo "$input" | jq -r '.tool_input.command // empty')

# Block any rm command targeting an index.lock file
if echo "$command" | grep -qE 'rm[[:space:]].*index\.lock'; then
    echo "🚫 **BLOCKED: Do not remove index.lock files.**" >&2
    echo "The lock indicates a git process was interrupted. Retry the failed git command directly — do not remove the lock." >&2
    exit 2
fi

exit 0
