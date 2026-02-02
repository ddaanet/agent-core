#!/usr/bin/env bash
set -euo pipefail

if [[ $# -eq 0 ]]; then
    echo "Usage: task-context.sh <token>" >&2
    exit 1
fi
token="$1"

# Find the oldest commit where this token's count changed (= introduction)
commit=$(git log --all -S "$token" --format=%H -- agents/session.md | tail -1)

if [[ -z "$commit" ]]; then
    echo "Error: token $token not found in git history" >&2
    exit 1
fi

echo "# Context from $(git log -1 --format='%h %s' "$commit")" >&2
git show "$commit:agents/session.md"
