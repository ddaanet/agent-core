#!/usr/bin/env python3
import json
import sys


def main() -> None:
    hook_input = json.load(sys.stdin)
    command = hook_input.get("tool_input", {}).get("command", "")

    redirect = _find_redirect(command)
    if redirect is None:
        sys.exit(0)

    output = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": redirect,
        }
    }
    print(json.dumps(output))
    sys.exit(0)


def _find_redirect(command: str) -> str | None:
    if command.startswith("ln "):
        return "Use `just sync-to-parent` instead of `ln` for managing symlinks in .claude/."
    if command.startswith("git worktree "):
        return "Use `claudeutils _worktree` instead of `git worktree` directly."
    if command.startswith("git merge ") or command == "git merge":
        return "Use `claudeutils _worktree merge` instead of `git merge` directly."
    return None


if __name__ == "__main__":
    main()
