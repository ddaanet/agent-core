#!/usr/bin/env python3
"""
PreToolUse hook: Warn when working directory is not project root.

Detects:
1. ANY Bash command executed when cwd != project root
2. Git operations in project root that reference submodule paths

Provides non-blocking warnings to prevent common mistakes:
- Forgetting to return to project root after operations in subdirectories
- Forgetting to use subshell pattern to preserve cwd
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


def main() -> None:
    """Execute hook to warn about non-project-root working directory."""
    # Read hook input from stdin
    hook_input = json.load(sys.stdin)

    command = hook_input.get('tool_input', {}).get('command', '')
    cwd = hook_input.get('cwd', '')
    project_dir = os.environ.get('CLAUDE_PROJECT_DIR', '')

    warnings = []

    # Case 1: Not at project root (for ANY Bash command)
    if cwd != project_dir:
        cwd_path = Path(cwd)
        project_path = Path(project_dir)
        relative_cwd = (
            cwd_path.relative_to(project_path)
            if project_dir and cwd.startswith(project_dir)
            else cwd_path
        )

        msg = (
            f"⚠️  Working directory is not project root: {relative_cwd}\n"
            f"   After this command, consider returning to project root.\n"
            f"   OR use subshell: (cd {relative_cwd} && ...) to preserve cwd."
        )
        warnings.append(msg)

    # Case 2: Git operation from project root referencing submodule paths
    if detect_git_operation(command) and cwd == project_dir:
        referenced_submodules = detect_submodule_reference(command)
        warnings.extend(
            f"⚠️  Git operation references '{submodule}/' from project root.\n"
            f"   Consider: (cd {submodule} && git ...) to avoid path confusion.\n"
            f"   Subshell preserves parent cwd automatically."
            for submodule in referenced_submodules
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
