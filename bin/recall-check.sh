#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: recall-check.sh <job-name>" >&2
  exit 1
fi

JOB="$1"
ARTIFACT="plans/${JOB}/recall-artifact.md"

if [[ ! -f "$ARTIFACT" ]]; then
  echo "recall-artifact.md missing for ${JOB}" >&2
  exit 1
fi

if [[ ! -s "$ARTIFACT" ]]; then
  echo "recall-artifact.md empty for ${JOB}" >&2
  exit 1
fi
