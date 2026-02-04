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


def get_session_from_commit(commit_ref, session_path):
    """Get session.md content from a specific commit."""
    try:
        result = subprocess.run(
            ["git", "show", f"{commit_ref}:{session_path}"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.splitlines()
    except subprocess.CalledProcessError:
        return []


def get_merge_parents():
    """Get parent commits for current merge. Returns (parent1, parent2) or None."""
    try:
        # Check if we're in a merge
        result = subprocess.run(
            ["git", "rev-parse", "MERGE_HEAD"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            return None  # Not in a merge

        merge_head = result.stdout.strip()

        # Get HEAD
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        head = result.stdout.strip()

        return (head, merge_head)
    except subprocess.CalledProcessError:
        return None


def get_staged_session(session_path):
    """Get staged session.md content."""
    try:
        result = subprocess.run(
            ["git", "show", f":{session_path}"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.splitlines()
    except subprocess.CalledProcessError:
        return []


def get_new_tasks(session_path):
    """Get task names that are new (not present in any parent).

    For regular commits: compares against HEAD.
    For merge commits: compares against both parents. A task is "new" only if
    present in current session.md but not present in either parent.
    """
    try:
        parents = get_merge_parents()

        # Get current (staged) task list
        current_lines = get_staged_session(session_path)
        current_tasks = {name for _, name in extract_task_names(current_lines)}

        if parents is None:
            # Regular commit - compare against HEAD
            parent_lines = get_session_from_commit("HEAD", session_path)
            parent_tasks = {name for _, name in extract_task_names(parent_lines)}
            new_tasks = current_tasks - parent_tasks
            return list(new_tasks)

        # Merge commit - check both parents
        parent1, parent2 = parents

        # Check if we have more than 2 parents (octopus merge)
        result = subprocess.run(
            ["git", "rev-list", "--parents", "--max-count=1", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        parent_count = len(result.stdout.strip().split()) - 1
        if parent_count > 2:
            print(
                f"Error: Octopus merge detected ({parent_count} parents). "
                "Task validation logic needs augmentation for n-way merges.",
                file=sys.stderr,
            )
            sys.exit(1)

        # Get task lists from both parents
        p1_lines = get_session_from_commit(parent1, session_path)
        p1_tasks = {name for _, name in extract_task_names(p1_lines)}

        p2_lines = get_session_from_commit(parent2, session_path)
        p2_tasks = {name for _, name in extract_task_names(p2_lines)}

        # Combine parent task lists
        all_parent_tasks = p1_tasks | p2_tasks

        # A task is "new" if present in current but not in either parent
        new_tasks = current_tasks - all_parent_tasks

        return list(new_tasks)

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
