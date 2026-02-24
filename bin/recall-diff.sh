#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: recall-diff.sh <job-name>" >&2
  exit 1
fi

JOB="$1"
ARTIFACT="plans/${JOB}/recall-artifact.md"

if [[ ! -f "$ARTIFACT" ]]; then
  echo "recall-diff.sh: recall-artifact.md missing for ${JOB}" >&2
  exit 1
fi

if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
  echo "recall-diff.sh: not inside a git repository" >&2
  exit 1
fi

MTIME=$(date -r "$ARTIFACT" "+%Y-%m-%dT%H:%M:%S")

git log --since="${MTIME}" --name-only --pretty=format: -- "plans/${JOB}/" \
  | grep -v '^$' \
  | grep -v "^plans/${JOB}/recall-artifact\.md$" \
  | sort -u \
  || true
