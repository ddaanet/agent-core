#!/usr/bin/env python3
import json
import os
import re
import sys


def main() -> None:
    try:
        hook_input = json.load(sys.stdin)
        prompt = hook_input.get("tool_input", {}).get("prompt", "")
    except Exception:
        sys.exit(0)

    message = _check_recall(prompt)
    if message is None:
        sys.exit(0)

    output = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": message,
        }
    }
    print(json.dumps(output))
    sys.exit(0)


def _check_recall(prompt: str) -> str | None:
    match = re.search(r"plans/([^/]+)/", prompt)
    if match is None:
        return None

    job = match.group(1)
    artifact_path = os.path.join("plans", job, "recall-artifact.md")
    if os.path.exists(artifact_path):
        return None

    return f"⚠️ No recall-artifact.md for plans/{job}/. Consider /recall or generating artifact before delegation."


if __name__ == "__main__":
    main()
