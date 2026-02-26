#!/usr/bin/env python3
"""PreToolUse hook: gate Task dispatch for execution agents without recall artifacts.

Fires on Task tool. Blocks execution agents (artisan, corrector, etc.) that dispatch
to a plans/ directory without a recall-artifact.md present.

Gating by subagent_type is more precise than prompt-path scanning:
- Targets execution agents only (not scouts, researchers, design agents)
- Blocks before dispatch (permissionDecision:deny on exit 0)
- No re-run between PreToolUse and tool execution — must block, not advise
"""

import json
import os
import re
import sys

EXECUTION_AGENTS = {
    "artisan",
    "test-driver",
    "corrector",
    "runbook-corrector",
    "design-corrector",
    "outline-corrector",
    "runbook-outline-corrector",
    "tdd-auditor",
    "refactor",
}


def main() -> None:
    try:
        hook_input = json.load(sys.stdin)
        tool_input = hook_input.get("tool_input", {})
    except Exception:
        sys.exit(0)

    # Gate only execution agents
    subagent_type = tool_input.get("subagent_type", "")
    if subagent_type not in EXECUTION_AGENTS:
        sys.exit(0)

    # Check for recall artifact in referenced plan directory
    prompt = tool_input.get("prompt", "")
    message = _check_recall(prompt)
    if message is None:
        sys.exit(0)

    # Block: execution agent dispatching without recall artifact
    output = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": message,
            "additionalContext": (
                f"{message}\n\n"
                f"Run /recall or generate recall-artifact.md before delegating "
                f"to {subagent_type}."
            ),
        },
        "systemMessage": "🚫 No recall-artifact — run /recall first",
    }
    print(json.dumps(output))
    sys.exit(0)


def _check_recall(prompt: str) -> str | None:
    """Return block message if plan directory lacks recall-artifact.md, else
    None."""
    match = re.search(r"plans/([^/]+)/", prompt)
    if match is None:
        return None

    job = match.group(1)
    artifact_path = os.path.join("plans", job, "recall-artifact.md")
    if os.path.exists(artifact_path):
        return None

    return f"No recall-artifact.md for plans/{job}/."


if __name__ == "__main__":
    main()
