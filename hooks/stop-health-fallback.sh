#!/usr/bin/env bash
set -euo pipefail

# Extract session_id from stdin JSON
session_id=$(python3 -c 'import sys,json; d=json.load(sys.stdin); print(d.get("session_id",""))' 2>/dev/null || echo "")

# Check flag file — if SessionStart already fired, skip
if [ -n "$session_id" ] && [ -f "$TMPDIR/health-${session_id}" ]; then
    exit 0  # SessionStart already displayed health
fi

# Flag file absent: new session (#10373 bypass) — run health checks
if [ -n "$session_id" ]; then
    touch "$TMPDIR/health-${session_id}"
fi

# Health check 1 — Dirty tree
dirty=$(git status --porcelain 2>/dev/null)
if [ -n "$dirty" ]; then
    tree_status="⚠️ Dirty tree ($(echo "$dirty" | wc -l | tr -d ' ') files)"
else
    tree_status="✓ Clean tree"
fi

# Health check 2 — Learnings health
learnings_status=$(python3 "$CLAUDE_PROJECT_DIR/agent-core/bin/learning-ages.py" \
  "$CLAUDE_PROJECT_DIR/agents/learnings.md" --summary 2>/dev/null \
  || echo "⚠️ Learnings status unavailable")

# Health check 3 — Stale worktrees
stale_wt=""
while IFS= read -r wt_path; do
    last_ts=$(git -C "$wt_path" log -1 --format="%ct" 2>/dev/null || echo "0")
    now=$(date +%s)
    age_days=$(( (now - last_ts) / 86400 ))
    if [ "$age_days" -gt 7 ]; then
        stale_wt="$stale_wt\n  $(basename "$wt_path") (${age_days}d)"
    fi
done < <(git worktree list --porcelain | grep "^worktree " | awk '{print $2}' | grep -v "^$(git rev-parse --show-toplevel)$" || true)

# Build output message with literal \n (not shell newlines)
message="Session Health:\n${tree_status}\nLearnings: ${learnings_status}"
[ -n "$stale_wt" ] && message="$message\n⚠️ Stale worktrees:$stale_wt"

# Output JSON with systemMessage
printf '{"systemMessage": "%s"}\n' "$(echo "$message" | sed 's/"/\\"/g')"
