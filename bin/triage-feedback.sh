#!/usr/bin/env bash

set -euo pipefail

job_dir="${1:-}"
baseline_commit="${2:-}"

if [[ -z "$job_dir" ]] || [[ -z "$baseline_commit" ]]; then
    echo "Usage: triage-feedback.sh <job-dir> <baseline-commit>" >&2
    exit 1
fi

# Count files changed since baseline
files_changed=$(git diff --name-only "$baseline_commit" | wc -l | tr -d ' ')

# Count report files in plans/$job_dir/reports/
# Exclude pre-execution artifacts: design-review*, outline-review*, recall-*
reports_count=0
reports_dir="plans/$job_dir/reports"
if [[ -d "$reports_dir" ]]; then
    reports_count=$(find "$reports_dir" -maxdepth 1 -type f ! -name "design-review*" ! -name "outline-review*" ! -name "recall-*" | wc -l | tr -d ' ')
fi

# Detect behavioral code: check for new function/class definitions in git diff
behavioral_code="no"
if git diff "$baseline_commit" | grep -E "^\+[^#]*(def |class |function )" > /dev/null; then
    behavioral_code="yes"
fi

# Compare against classification if present
verdict="no-classification"
classification_file="plans/$job_dir/classification.md"
if [[ -f "$classification_file" ]]; then
    classification=$(grep -E "(^-?\s*\*\*Classification:\*\*|^-?\s*Classification:)" "$classification_file" | head -1 | sed -E 's/.*:\s*//;s/\*//g' | xargs || true)

    if [[ -z "$classification" ]]; then
        verdict="no-classification"
    elif [[ "$classification" == "Simple" ]]; then
        if [[ "$behavioral_code" == "yes" ]] || [[ "$reports_count" -gt 0 ]]; then
            verdict="underclassified"
        else
            verdict="match"
        fi
    elif [[ "$classification" == "Complex" ]]; then
        if [[ "$files_changed" -le 2 ]] && [[ "$reports_count" -eq 0 ]] && [[ "$behavioral_code" == "no" ]]; then
            verdict="overclassified"
        else
            verdict="match"
        fi
    else
        verdict="match"
    fi
fi

# Output structure
echo "## Evidence"
echo "- Files changed: $files_changed"
echo "- Reports: $reports_count"
echo "- Behavioral code: $behavioral_code"
echo ""
echo "## Verdict"
echo "$verdict"

if [[ "$verdict" == "underclassified" ]] || [[ "$verdict" == "overclassified" ]]; then
    echo ""
    echo "Triage: predicted $classification, evidence suggests $verdict (files=$files_changed, reports=$reports_count, code=$behavioral_code)"
fi

# Append to triage-feedback-log.md (only if verdict is not no-classification)
if [[ "$verdict" != "no-classification" ]]; then
    log_dir="plans/reports"
    mkdir -p "$log_dir"
    log_file="$log_dir/triage-feedback-log.md"

    if [[ ! -f "$log_file" ]]; then
        echo "| Date | Job | Predicted | Files Changed | Reports | Behavioral Code | Verdict |" > "$log_file"
        echo "|---|---|---|---|---|---|---|" >> "$log_file"
    fi

    log_date=$(date -u +%Y-%m-%d)
    echo "| $log_date | $job_dir | $classification | $files_changed | $reports_count | $behavioral_code | $verdict |" >> "$log_file"
fi

exit 0
