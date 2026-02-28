#!/usr/bin/env python3
"""PreToolUse hook: intercept Bash commands and block via permissionDecision:deny.

All matched commands are blocked with:
- permissionDecisionReason: brief rationale (agent + user)
- additionalContext: extended agent instruction (agent-only)
- systemMessage: user-facing summary (~60 chars)
"""

import json
import re
import sys
from pathlib import Path


def _deny(reason: str, agent_msg: str, user_msg: str) -> dict:
    """Construct permissionDecision:deny JSON output."""
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
            "additionalContext": agent_msg,
        },
        "systemMessage": user_msg,
    }


def main() -> None:
    """Entry point: read hook input, match command, block if matched."""
    hook_input = json.load(sys.stdin)
    command = hook_input.get("tool_input", {}).get("command", "")

    result = _match(command)
    if result is None:
        sys.exit(0)

    print(json.dumps(result))
    sys.exit(0)


def _match_blocks(command: str) -> dict | None:
    """Hard blocks: python -c inline code, rm index.lock."""
    if re.match(r"python3?\s+-c\s", command):
        return _deny(
            "python -c is unreadable — use plans/prototypes/ instead",
            "🚫 python -c is unreadable and untestable. "
            "Write to plans/prototypes/ to identify tooling gaps.",
            "🚫 python -c blocked — use plans/prototypes/",
        )

    if re.search(r"rm\s.*index\.lock", command):
        return _deny(
            "Lock contention from concurrent session. Retry your git command — do not delete lock files.",
            "Lock contention from concurrent session. Retry your git command — do not delete lock files.",
            "🚫 Lock contention — retry git command, do not delete lock",
        )
    return None


def _match_python_uv(command: str) -> dict | None:
    """Blocks for python/python3/uv invocations."""
    # python3 -m <tool>: strip prefix
    m = re.match(r"python3?\s+-m\s+(\S+)(.*)", command)
    if m:
        tool, rest = m.group(1), m.group(2)
        return _deny(
            f"python3 -m prefix unnecessary — use `{tool}` directly",
            f"Use `{tool}{rest}` directly — scripts have shebangs.",
            f"🚫 python3 -m — use `{tool}` directly",
        )

    # python3 <path>: direct script invocation
    m = re.match(r"python3?\s+(?!-)([\w./_-]+\.\w+)(.*)", command)
    if m:
        script, rest = m.group(1), m.group(2)
        error = _validate_script(script)
        if error:
            return _deny(
                error,
                error,
                f"🚫 Script error: {script}",
            )
        return _deny(
            "python3 prefix breaks permissions.allow matching",
            f"Use `{script}{rest}` directly "
            "— python3 prefix breaks permissions.allow matching.",
            f"🚫 Use `{script}` directly (no python3 prefix)",
        )

    # uv run <command>: unnecessary with active .venv
    m = re.match(r"uv\s+run\s+(.*)", command)
    if m:
        rest = m.group(1)
        return _deny(
            f"uv run unnecessary — .venv active, use `{rest}` directly",
            f"Use `{rest}` directly — .venv is already active.",
            f"🚫 uv run — use `{rest}` directly",
        )
    return None


def _match_tool_wrappers(command: str) -> dict | None:
    """Blocks for commands with project wrapper equivalents."""
    if command == "ln" or command.startswith("ln "):
        return _deny(
            "Use just sync-to-parent — recipe encodes correct paths",
            "Use `just sync-to-parent` — recipe encodes correct paths.",
            "🚫 ln blocked — use just sync-to-parent",
        )

    if command.startswith("git worktree "):
        return _deny(
            "Use claudeutils _worktree — wrapper manages session.md",
            "Use `claudeutils _worktree` — wrapper manages session.md.",
            "🚫 git worktree — use claudeutils _worktree",
        )

    if command.startswith("git merge ") or command == "git merge":
        return _deny(
            "Use claudeutils _worktree merge — wrapper manages session.md",
            "Use `claudeutils _worktree merge` — wrapper manages session.md.",
            "🚫 git merge — use claudeutils _worktree merge",
        )
    return None


def _match(command: str) -> dict | None:
    """Match command against routing table."""
    return (
        _match_blocks(command)
        or _match_python_uv(command)
        or _match_tool_wrappers(command)
    )


def _validate_script(path: str) -> str | None:
    """Check if script exists and is executable.

    Return error message or None.
    """
    p = Path(path)
    if not p.is_file():
        return f"Script `{path}` not found on disk. Verify the path."
    if not p.stat().st_mode & 0o111:
        return f"Script `{path}` exists but is not executable. Run `chmod +x {path}`."
    try:
        head = p.read_bytes()[:2]
        if head != b"#!":
            return (
                f"Script `{path}` has no shebang line. "
                "Add `#!/usr/bin/env python3` as first line."
            )
    except OSError:
        pass
    return None


if __name__ == "__main__":
    main()
