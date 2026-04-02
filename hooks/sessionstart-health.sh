#!/usr/bin/env bash
set -euo pipefail

TMPDIR="${TMPDIR:-/tmp}"

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
    #    Uses .edify-venv (not .venv) to avoid colliding with dev venv in submodule mode
    EDIFY_PKG="edify-cli @ git+https://github.com/ddaanet/edify.git"
    VENV_DIR="$CLAUDE_PLUGIN_ROOT/.edify-venv"
    INSTALL_LOG="$CLAUDE_PLUGIN_ROOT/.edify-install.log"
    if [ -f "$VENV_DIR/bin/edify" ]; then
        : # Already installed
    elif command -v uv > /dev/null 2>&1; then
        if ! uv venv "$VENV_DIR" > "$INSTALL_LOG" 2>&1; then
            setup_warnings="$setup_warnings\n⚠️ CLI venv failed (see .edify-install.log)"
        elif ! uv pip install --python "$VENV_DIR/bin/python" "$EDIFY_PKG" >> "$INSTALL_LOG" 2>&1; then
            setup_warnings="$setup_warnings\n⚠️ CLI install failed (see .edify-install.log)"
        else
            rm -f "$INSTALL_LOG"
        fi
    elif command -v python3 > /dev/null 2>&1; then
        if ! python3 -m venv "$VENV_DIR" > "$INSTALL_LOG" 2>&1; then
            setup_warnings="$setup_warnings\n⚠️ CLI venv failed (see .edify-install.log)"
        elif ! "$VENV_DIR/bin/pip" install "$EDIFY_PKG" >> "$INSTALL_LOG" 2>&1; then
            setup_warnings="$setup_warnings\n⚠️ CLI install failed (see .edify-install.log)"
        else
            rm -f "$INSTALL_LOG"
        fi
    else
        setup_warnings="$setup_warnings\n⚠️ CLI install failed: neither uv nor python3 found"
    fi

    # 3. Add shim dir to PATH so bare `edify` resolves to the plugin venv binary
    #    without exposing the venv's python3/pip (which would shadow system python3)
    if [ -n "${CLAUDE_ENV_FILE:-}" ] && [ -f "$VENV_DIR/bin/edify" ]; then
        SHIM_DIR="$CLAUDE_PLUGIN_ROOT/.bin"
        mkdir -p "$SHIM_DIR"
        ln -sf "$VENV_DIR/bin/edify" "$SHIM_DIR/edify"
        echo "PATH=$SHIM_DIR:\$PATH" >> "$CLAUDE_ENV_FILE"
    fi

    # 4. Staleness check (FR-5)
    # .edify.yaml version is written by /edify:init (creation) and /edify:update (sync).
    # Hook only reads and compares — writing here would defeat the staleness nag.
    PLUGIN_VERSION=""
    PLUGIN_JSON="$CLAUDE_PLUGIN_ROOT/.claude-plugin/plugin.json"
    if [ -f "$PLUGIN_JSON" ]; then
        PLUGIN_VERSION=$(python3 -c "import json; print(json.load(open('$PLUGIN_JSON'))['version'])" 2>/dev/null || echo "")
    fi

    if [ -n "$PLUGIN_VERSION" ] && [ -n "${CLAUDE_PROJECT_DIR:-}" ]; then
        EDIFY_YAML="$CLAUDE_PROJECT_DIR/.edify.yaml"
        if [ -f "$EDIFY_YAML" ]; then
            YAML_VERSION=$(python3 -c "import re; content=open('$EDIFY_YAML').read(); m=re.search(r'^version:\s*[\"\\x27]?([^\"\\x27\\n]+)[\"\\x27]?', content, re.MULTILINE); print(m.group(1).strip()) if m else print('')" 2>/dev/null || echo "")
            if [ -n "$YAML_VERSION" ] && [ "$YAML_VERSION" != "$PLUGIN_VERSION" ]; then
                setup_warnings="$setup_warnings\n⚠️ Fragments may be stale. Run /edify:update"
            fi
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
