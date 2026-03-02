#!/usr/bin/env bash
exec 2>&1
set -xeuo pipefail

# Check git status
status=$(git status --porcelain)
if [[ -n "$status" ]]; then
    echo "DIRTY: uncommitted changes"
    echo "$status"
    exit 1
fi

# Check submodule pointer consistency
sub_status=$(git submodule status || true)
if [[ -n "$sub_status" ]] && echo "$sub_status" | grep -q '^+'; then
    echo "SUBMODULE: pointer out of sync"
    echo "$sub_status"
    exit 1
fi

# Check precommit
just precommit || {
    echo "PRECOMMIT: validation failed"
    exit 1
}

echo "CLEAN"
exit 0
