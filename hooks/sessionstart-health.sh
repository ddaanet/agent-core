#!/usr/bin/env bash
set -euo pipefail

# Extract session_id from stdin JSON
session_id=$(python3 -c 'import sys,json; d=json.load(sys.stdin); print(d.get("session_id",""))' 2>/dev/null || echo "")

# Write flag file (mark that SessionStart fired for this session)
if [ -n "$session_id" ]; then
    touch "$TMPDIR/health-${session_id}"
fi

# Setup section — only runs when loaded as a plugin (CLAUDE_PLUGIN_ROOT is set)
setup_warnings=""
if [ -n "${CLAUDE_PLUGIN_ROOT:-}" ]; then

    # 1. Export EDIFY_PLUGIN_ROOT via $CLAUDE_ENV_FILE for use in subsequent Bash commands
    if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
        echo "EDIFY_PLUGIN_ROOT=$CLAUDE_PLUGIN_ROOT" >> "$CLAUDE_ENV_FILE"
    fi

    # 2. Install edify CLI into plugin-local venv
    EDIFY_VERSION="0.0.2"  # Updated with each plugin release
    VENV_DIR="$CLAUDE_PLUGIN_ROOT/.venv"
    if command -v uv > /dev/null 2>&1; then
        if [ ! -d "$VENV_DIR" ]; then
            uv venv "$VENV_DIR" > /dev/null 2>&1 \
                || setup_warnings="$setup_warnings\n⚠️ CLI install failed: could not create venv"
        fi
        if [ -d "$VENV_DIR" ]; then
            uv pip install --quiet --python "$VENV_DIR/bin/python" "claudeutils==$EDIFY_VERSION" > /dev/null 2>&1 \
                || setup_warnings="$setup_warnings\n⚠️ CLI install failed: uv pip install error"
        fi
    elif command -v pip > /dev/null 2>&1; then
        mkdir -p "$VENV_DIR/lib"
        pip install --quiet --target "$VENV_DIR/lib" "claudeutils==$EDIFY_VERSION" > /dev/null 2>&1 \
            || setup_warnings="$setup_warnings\n⚠️ CLI install failed: pip install error"
    else
        setup_warnings="$setup_warnings\n⚠️ CLI install failed: uv not found"
    fi

    # 3. Write version provenance to .edify.yaml (FR-10)
    PLUGIN_VERSION=""
    PLUGIN_JSON="$CLAUDE_PLUGIN_ROOT/.claude-plugin/plugin.json"
    if [ -f "$PLUGIN_JSON" ]; then
        PLUGIN_VERSION=$(python3 -c "import json; print(json.load(open('$PLUGIN_JSON'))['version'])" 2>/dev/null || echo "")
    fi

    if [ -n "$PLUGIN_VERSION" ] && [ -n "${CLAUDE_PROJECT_DIR:-}" ]; then
        EDIFY_YAML="$CLAUDE_PROJECT_DIR/.edify.yaml"
        if [ -f "$EDIFY_YAML" ]; then
            # Update existing .edify.yaml version field
            python3 - "$EDIFY_YAML" "$PLUGIN_VERSION" 2>/dev/null <<'PYEOF' \
                || setup_warnings="$setup_warnings\n⚠️ Version write failed"
import sys
import re

yaml_file = sys.argv[1]
new_version = sys.argv[2]

with open(yaml_file, 'r') as f:
    content = f.read()

# Replace version line
updated = re.sub(r'^version:.*$', f'version: "{new_version}"', content, flags=re.MULTILINE)

with open(yaml_file, 'w') as f:
    f.write(updated)
PYEOF
        else
            # Create .edify.yaml (first run scenario)
            cat > "$EDIFY_YAML" <<YAMLEOF || setup_warnings="$setup_warnings\n⚠️ Version write failed"
# Edify plugin version marker
# Written by sessionstart-health.sh on session start, updated by /edify:update
version: "$PLUGIN_VERSION"
sync_policy: nag  # nag | auto-with-report (future)
YAMLEOF
        fi

        # 4. Compare versions and nag if stale (FR-5)
        YAML_VERSION=$(python3 -c "import re; content=open('$EDIFY_YAML').read(); m=re.search(r'^version:\s*[\"\\x27]?([^\"\\x27\\n]+)[\"\\x27]?', content, re.MULTILINE); print(m.group(1).strip()) if m else print('')" 2>/dev/null || echo "")
        if [ -n "$YAML_VERSION" ] && [ "$YAML_VERSION" != "$PLUGIN_VERSION" ]; then
            setup_warnings="$setup_warnings\n⚠️ Fragments may be stale. Run /edify:update"
        fi
    fi

fi

# Health check 1 — Dirty tree
dirty=$(git status --porcelain 2>/dev/null)
if [ -n "$dirty" ]; then
    tree_status="⚠️ Dirty tree ($(echo "$dirty" | wc -l | tr -d ' ') files)"
else
    tree_status="✓ Clean tree"
fi

# Health check 2 — Learnings health
learnings_status=$(python3 "${CLAUDE_PLUGIN_ROOT:-}/bin/learning-ages.py" \
  "${CLAUDE_PROJECT_DIR:-$PWD}/agents/learnings.md" --summary 2>/dev/null \
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
[ -n "$setup_warnings" ] && message="$message$setup_warnings"

# Output JSON with systemMessage
printf '{"systemMessage": "%s"}\n' "$(echo "$message" | sed 's/"/\\"/g')"
