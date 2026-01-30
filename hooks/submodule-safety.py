#!/usr/bin/env python3
"""
PreToolUse hook: Warn when git operations risk submodule cwd confusion.

Detects:
1. Git operations in project root that reference submodule paths
2. Git operations while inside a submodule

Provides non-blocking warnings to prevent common mistakes:
- Forgetting to cd into submodule before git add/commit
- Forgetting to cd back to project root after submodule operations
"""

import json
import os
import re
import sys
from pathlib import Path


def detect_git_operation(command: str) -> bool:
    """Check if command is a git operation."""
    git_ops = ['git add', 'git commit', 'git push', 'git status', 'git diff', 'git log']
    return any(op in command for op in git_ops)


def detect_submodule_reference(command: str) -> list[str]:
    """Detect if command references submodule paths."""
    # Common submodule patterns in this project
    submodule_patterns = [
        r'\bagent-core\b',
        r'\bpytest-md\b',
        r'\btuick\b',
    ]

    referenced = []
    for pattern in submodule_patterns:
        if re.search(pattern, command):
            # Extract the submodule name
            match = re.search(pattern, command)
            if match:
                referenced.append(match.group(0))

    return list(set(referenced))  # Deduplicate


def is_inside_submodule(cwd: str) -> str | None:
    """Check if cwd is inside a submodule. Returns submodule name or None."""
    cwd_path = Path(cwd)

    # Common submodules in this project
    submodules = ['agent-core', 'pytest-md', 'tuick']

    for submodule in submodules:
        # Check if cwd contains the submodule name as a path component
        if submodule in cwd_path.parts:
            return submodule

    return None


def main():
    # Read hook input from stdin
    hook_input = json.load(sys.stdin)

    command = hook_input.get('tool_input', {}).get('command', '')
    cwd = hook_input.get('cwd', '')

    # Skip if not a git operation
    if not detect_git_operation(command):
        print(json.dumps({
            "continue": True,
            "suppressOutput": True
        }))
        return

    # Check for submodule cwd issues
    current_submodule = is_inside_submodule(cwd)
    referenced_submodules = detect_submodule_reference(command)

    warnings = []

    # Case 1: In project root, referencing submodule paths
    if not current_submodule and referenced_submodules:
        for submodule in referenced_submodules:
            warnings.append(
                f"⚠️  Git operation references '{submodule}/' from project root.\n"
                f"   Consider: (cd {submodule} && git ...) to avoid path confusion.\n"
                f"   Subshell preserves parent cwd automatically."
            )

    # Case 2: Inside a submodule
    if current_submodule:
        warnings.append(
            f"⚠️  You are in submodule '{current_submodule}'.\n"
            f"   After this git operation, remember to cd back to project root.\n"
            f"   OR use subshell: (cd {current_submodule} && git ...) to preserve cwd."
        )

    # Output warnings if any
    if warnings:
        output = {
            "continue": True,
            "systemMessage": "\n\n".join(warnings)
        }
    else:
        output = {
            "continue": True,
            "suppressOutput": True
        }

    print(json.dumps(output))


if __name__ == '__main__':
    main()
