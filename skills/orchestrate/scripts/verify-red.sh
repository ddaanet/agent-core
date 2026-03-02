#!/usr/bin/env bash
exec 2>&1
set -xeuo pipefail

if [[ $# -ne 1 ]]; then
    echo "ERROR: exactly one argument required: <test_file>"
    exit 1
fi

test_file="$1"

if [[ ! -f "$test_file" ]]; then
    echo "ERROR: test file not found: $test_file"
    exit 1
fi

# Run pytest — non-zero exit means test failed (RED state)
if pytest "$test_file" --no-header -q; then
    echo "RED REJECTED: test passed unexpectedly"
    exit 1
else
    echo "RED CONFIRMED"
    exit 0
fi
