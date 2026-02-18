#!/usr/bin/env python3
"""Dual-mode hook: Block commands from wrong cwd.

Blocks PreToolUse commands from wrong cwd, warns PostToolUse after cwd drift.

PreToolUse behavior:
- cwd == project root → allow silently
- cwd != project root AND command starts with `cd <project_root> &&` → allow
- cwd != project root AND command is bare `cd <project_root>` → allow (restore)
- cwd != project root AND any other command → BLOCK (exit 2, stderr)

PostToolUse behavior:
- cwd == project root → silent
- cwd != project root → inject additionalContext warning

Design: Hard boundary to prevent agent confusion. Read-only commands from wrong
cwd actively mislead the agent about context.

Security: `cd <root> && cmd` is equivalent to running cmd from project root.
The && ensures cmd only runs if cd succeeds. Only && is allowed (not ; or ||)
to guarantee the cd-first invariant. Exact path match only — no traversal.
"""

import json
import os
import re
import sys


def main() -> None:
    """Execute hook based on event type."""
    # Read hook input from stdin
    hook_input = json.load(sys.stdin)

    event_name = hook_input.get('hook_event_name', '')
    cwd = hook_input.get('cwd', '')
    project_dir = os.environ.get('CLAUDE_PROJECT_DIR', '')

    # Always allow if at project root
    if cwd == project_dir:
        sys.exit(0)

    # Handle based on event type
    if event_name == 'PreToolUse':
        handle_pretooluse(hook_input, cwd, project_dir)
    elif event_name == 'PostToolUse':
        handle_posttooluse(cwd, project_dir)
    else:
        sys.exit(0)


def _is_cd_to_root(command: str, project_dir: str) -> bool:
    """Check if command starts with cd to project root.

    Matches bare `cd <path>` and `cd <path> && <rest>`.
    Handles unquoted, double-quoted, and single-quoted path variants.
    Rejects `;` and `||` separators — only `&&` preserves the cd-first invariant.
    """
    escaped = re.escape(project_dir)
    # cd <path>, cd "<path>", cd '<path>' — optionally followed by && <rest>
    pattern = rf"""^cd\s+(?:{escaped}|"{escaped}"|'{escaped}')\s*(?:&&\s*.+)?$"""
    return bool(re.match(pattern, command))


def handle_pretooluse(hook_input: dict, cwd: str, project_dir: str) -> None:
    """Block commands from wrong cwd, except restore commands."""
    command = hook_input.get('tool_input', {}).get('command', '').strip()

    if _is_cd_to_root(command, project_dir):
        sys.exit(0)

    # Block all other commands from wrong cwd
    error_msg = (
        f"❌ Bash commands blocked: working directory is not project root.\n"
        f"Current: {cwd}\n"
        f"Run this command to restore: cd {project_dir}"
    )

    # Write to stderr and exit 2 to block
    sys.stderr.write(error_msg + "\n")
    sys.exit(2)


def handle_posttooluse(cwd: str, project_dir: str) -> None:
    """Warn after cwd drift detected."""
    warning = (
        f"⚠️  Working directory changed to: {cwd}\n"
        f"Bash is blocked until cwd is restored.\n"
        f"Run: cd {project_dir}"
    )

    output = {
        'hookSpecificOutput': {
            'hookEventName': 'PostToolUse',
            'additionalContext': warning
        },
        'systemMessage': warning
    }

    print(json.dumps(output))


if __name__ == '__main__':
    main()
