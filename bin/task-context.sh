#!/usr/bin/env bash
set -euo pipefail

if [[ $# -eq 0 ]]; then
    echo "Usage: task-context.sh '<task-name>'" >&2
    echo "Example: task-context.sh 'Task prose keys'" >&2
    exit 1
fi
task_name="$1"

# Find the oldest commit where this task name's count changed (= introduction)
commit=$(git log --all -S "$task_name" --format=%H -- agents/session.md | tail -1)

if [[ -z "$commit" ]]; then
    echo "Error: task name '$task_name' not found in git history" >&2
    exit 1
fi

echo "# Context from $(git log -1 --format='%h %s' "$commit")" >&2
git show "$commit:agents/session.md"
