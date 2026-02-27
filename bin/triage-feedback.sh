#!/usr/bin/env bash

set -uo pipefail

job_dir="${1:-}"
baseline_commit="${2:-}"

if [[ -z "$job_dir" ]] || [[ -z "$baseline_commit" ]]; then
    echo "Usage: triage-feedback.sh <job-dir> <baseline-commit>" >&2
    exit 0
fi

# Count files changed since baseline (exclude summary line)
# The summary line contains "file changed" or "files changed", all other lines are file changes
files_changed=$(git diff --stat "$baseline_commit" | grep -v "file.*changed" | wc -l | tr -d ' ')

# Count report files in plans/$job_dir/reports/
# Exclude pre-execution artifacts: design-review*, outline-review*, recall-*
reports_count=0
reports_dir="plans/$job_dir/reports"
if [[ -d "$reports_dir" ]]; then
    reports_count=$(find "$reports_dir" -maxdepth 1 -type f ! -name "design-review*" ! -name "outline-review*" ! -name "recall-*" | wc -l | tr -d ' ')
fi

# Placeholder output structure
echo "## Evidence"
echo "- Files changed: $files_changed"
echo "- Reports: $reports_count"
echo "- Behavioral code: no"
echo ""
echo "## Verdict"
echo "no-classification"

exit 0
