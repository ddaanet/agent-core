#!/usr/bin/env python3
"""PreToolUse hook: intercept Bash commands and redirect or block.

Routing table with two action types:
- Soft redirect: additionalContext suggestion (exit 0, agent sees message)
- Hard block: stderr message + exit 2 (tool call prevented)
"""

import json
import re
import sys
from pathlib import Path
from typing import NamedTuple


class _Redirect(NamedTuple):
    """Soft redirect — inject additionalContext, allow tool call."""

    message: str


class _Block(NamedTuple):
    """Hard block — stderr message, exit 2, prevent tool call."""

    message: str


_Action = _Redirect | _Block


def main() -> None:
    """Entry point: read hook input, match command, act."""
    hook_input = json.load(sys.stdin)
    command = hook_input.get("tool_input", {}).get("command", "")

    action = _match(command)
    if action is None:
        sys.exit(0)

    if isinstance(action, _Block):
        sys.stderr.write(action.message + "\n")
        sys.exit(2)

    # Redirect — inject additionalContext
    output = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": action.message,
        }
    }
    print(json.dumps(output))
    sys.exit(0)


def _match_blocks(command: str) -> _Action | None:
    """Hard blocks — exit 2, tool call prevented."""
    # python3 -c / python -c: block inline code execution
    if re.match(r"python3?\s+-c\s", command):
        return _Block(
            "🚫 python -c is unreadable and untestable. "
            "Write to plans/prototypes/ to identify tooling gaps."
        )

    # rm index.lock: never delete git lock files
    if re.search(r"rm\s.*index\.lock", command):
        return _Block(
            "🚫 index.lock indicates concurrent git access. Retry the git command."
        )
    return None


def _match_python_uv(command: str) -> _Action | None:
    """Redirects for python/python3/uv invocations."""
    # python3 -m <tool> / python -m <tool>: strip prefix
    m = re.match(r"python3?\s+-m\s+(\S+)(.*)", command)
    if m:
        tool, rest = m.group(1), m.group(2)
        return _Redirect(f"Use `{tool}{rest}` directly — scripts have shebangs.")

    # python3 <path> / python <path>: direct script invocation
    m = re.match(r"python3?\s+(?!-)([\w./_-]+\.\w+)(.*)", command)
    if m:
        script, rest = m.group(1), m.group(2)
        msg = _validate_script(script)
        if msg:
            return _Redirect(msg)
        return _Redirect(
            f"Use `{script}{rest}` directly "
            "— python3 prefix breaks permissions.allow matching."
        )

    # uv run <command>: unnecessary in sandbox with .venv active
    m = re.match(r"uv\s+run\s+(.*)", command)
    if m:
        rest = m.group(1)
        return _Redirect(f"Use `{rest}` directly — .venv is already active.")
    return None


def _match_tool_wrappers(command: str) -> _Action | None:
    """Redirects for commands with project wrappers."""
    # ln: use just sync-to-parent
    if command == "ln" or command.startswith("ln "):
        return _Redirect("Use `just sync-to-parent` — recipe encodes correct paths.")

    # git worktree: use claudeutils wrapper
    if command.startswith("git worktree "):
        return _Redirect("Use `claudeutils _worktree` — wrapper manages session.md.")

    # git merge: use claudeutils wrapper
    if command.startswith("git merge ") or command == "git merge":
        return _Redirect(
            "Use `claudeutils _worktree merge` — wrapper manages session.md."
        )
    return None


def _match(command: str) -> _Action | None:
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
