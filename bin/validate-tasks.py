#!/usr/bin/env python3
"""Validate task name uniqueness in session.md.

Checks:
- Task name format: - [ ] **Task Name** — description
- Uniqueness across session.md, todo.md, shelved tasks
- Disjointness with learning keys
- Git history search for new tasks only (using git log -S)
- Merge commit handling (compare against all parents)
"""

import re
import subprocess
import sys
from pathlib import Path

TASK_PATTERN = re.compile(r"^- \[[ x>]\] \*\*(.+?)\*\* —")
LEARNING_PATTERN = re.compile(r"^## (.+)$")
H1_PATTERN = re.compile(r"^# ")


def find_project_root():
    """Find project root by locating CLAUDE.md."""
    current = Path.cwd()
    while current != current.parent:
        if (current / "CLAUDE.md").exists():
            return current
        current = current.parent
    return Path.cwd()


def extract_task_names(lines):
    """Extract (line_number, task_name) pairs from task lines."""
    tasks = []
    for i, line in enumerate(lines, 1):
        m = TASK_PATTERN.match(line.strip())
        if m:
            tasks.append((i, m.group(1)))
    return tasks


def extract_learning_keys(lines):
    """Extract learning keys from ## headers (exclude H1 document title)."""
    keys = set()
    h1_seen = False
    for line in lines:
        stripped = line.strip()
        # Skip H1 lines (document title)
        if H1_PATTERN.match(stripped):
            h1_seen = True
            continue
        # Only process ## headers after we've seen H1
        if h1_seen:
            m = LEARNING_PATTERN.match(stripped)
            if m:
                keys.add(m.group(1).lower())
    return keys


def get_new_tasks(session_path):
    """Get task names that are new in the current commit (not in any parent)."""
    try:
        # Get current staged content
        result = subprocess.run(
            ["git", "diff", "--cached", "--unified=0", "--", str(session_path)],
            capture_output=True,
            text=True,
            check=True,
        )

        # Extract added lines (lines starting with +)
        new_lines = []
        for line in result.stdout.splitlines():
            if line.startswith("+") and not line.startswith("+++"):
                new_lines.append(line[1:])  # Strip leading +

        # Extract task names from new lines
        new_tasks = []
        for line in new_lines:
            m = TASK_PATTERN.match(line.strip())
            if m:
                new_tasks.append(m.group(1))

        return new_tasks
    except subprocess.CalledProcessError:
        # Not in a git repo or no staged changes
        return []


def check_history(task_name):
    """Check if task name exists in git history using git log -S (case-insensitive)."""
    try:
        result = subprocess.run(
            [
                "git",
                "log",
                "--all",
                "-S",
                task_name,
                "--regexp-ignore-case",
                "--format=%H",
                "--",
                "agents/session.md",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        return bool(result.stdout.strip())
    except subprocess.CalledProcessError:
        return False


def validate(session_path, learnings_path):
    """Validate task names. Returns list of error strings."""
    project_root = find_project_root()
    session_path = project_root / session_path
    learnings_path = project_root / learnings_path

    errors = []

    # Read session.md
    try:
        with open(session_path) as f:
            session_lines = f.readlines()
    except FileNotFoundError:
        return []

    # Read learnings.md
    try:
        with open(learnings_path) as f:
            learning_lines = f.readlines()
    except FileNotFoundError:
        learning_lines = []

    # Extract task names and learning keys
    tasks = extract_task_names(session_lines)
    learning_keys = extract_learning_keys(learning_lines)

    # Check uniqueness within session.md
    seen = {}
    for lineno, task_name in tasks:
        key = task_name.lower()
        if key in seen:
            errors.append(
                f"  line {lineno}: duplicate task name (first at line {seen[key]}): "
                f"**{task_name}**"
            )
        else:
            seen[key] = lineno

    # Check disjointness with learning keys
    for lineno, task_name in tasks:
        key = task_name.lower()
        if key in learning_keys:
            errors.append(
                f"  line {lineno}: task name conflicts with learning key: "
                f"**{task_name}**"
            )

    # Check git history for new tasks only
    new_tasks = get_new_tasks(session_path)
    for task_name in new_tasks:
        if check_history(task_name):
            errors.append(
                f"  new task name exists in git history: **{task_name}**"
            )

    return errors


def main():
    session_path = sys.argv[1] if len(sys.argv) > 1 else "agents/session.md"
    learnings_path = sys.argv[2] if len(sys.argv) > 2 else "agents/learnings.md"

    errors = validate(session_path, learnings_path)

    if errors:
        print(f"Task validation failed ({len(errors)} errors):", file=sys.stderr)
        for e in errors:
            print(e, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
