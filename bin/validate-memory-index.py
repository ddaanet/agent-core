#!/usr/bin/env python3
"""Validate memory-index.md entries against titles in indexed files.

Checks:
- Each index entry matches a **Title:** in at least one indexed file
- Each index entry resolves unambiguously (not in multiple files)
- No duplicate index entries
"""

import re
import sys
from pathlib import Path

# Standalone bold title: **Title here:** (nothing after closing **)
TITLE_PATTERN = re.compile(r"^\*\*(.+?):\*\*\s*$")
INDEX_ENTRY_PATTERN = re.compile(r"^- (.+)$")

# Files that contain identifier titles
INDEXED_GLOBS = [
    "agents/learnings.md",
    "agents/decisions/*.md",
    "agent-core/skills/*/SKILL.md",
]


def find_project_root():
    """Walk up from script to find project root (has CLAUDE.md)."""
    p = Path(__file__).resolve().parent
    while p != p.parent:
        if (p / "CLAUDE.md").exists():
            return p
        p = p.parent
    return Path.cwd()


def collect_titles(root):
    """Scan indexed files for all standalone **Title:** patterns.

    Returns dict: lowercase title → list of (file_path, line_number).
    """
    titles = {}

    for glob_pattern in INDEXED_GLOBS:
        for filepath in sorted(root.glob(glob_pattern)):
            rel = str(filepath.relative_to(root))
            try:
                lines = filepath.read_text().splitlines()
            except (OSError, UnicodeDecodeError):
                continue

            for i, line in enumerate(lines, 1):
                m = TITLE_PATTERN.match(line.strip())
                if m:
                    key = m.group(1).lower()
                    titles.setdefault(key, []).append((rel, i))

    return titles


def validate(index_path):
    """Validate memory index. Returns list of error strings."""
    root = find_project_root()

    try:
        lines = (root / index_path).read_text().splitlines()
    except FileNotFoundError:
        return []

    titles = collect_titles(root)
    errors = []
    seen_entries = {}

    for lineno, line in enumerate(lines, 1):
        m = INDEX_ENTRY_PATTERN.match(line.strip())
        if not m:
            continue

        entry = m.group(1).strip()
        key = entry.lower()

        # Duplicate index entry check
        if key in seen_entries:
            errors.append(
                f"  line {lineno}: duplicate index entry '{entry}' "
                f"(first at line {seen_entries[key]})"
            )
        else:
            seen_entries[key] = lineno

        # Title existence check
        locations = titles.get(key, [])
        if not locations:
            errors.append(
                f"  line {lineno}: no matching **{entry}:** in indexed files"
            )
        elif len(locations) > 1:
            locs = ", ".join(f"{f}:{ln}" for f, ln in locations)
            errors.append(
                f"  line {lineno}: ambiguous '{entry}' found in multiple files: {locs}"
            )

    return errors


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "agents/memory-index.md"
    errors = validate(path)

    if errors:
        print(
            f"Memory index validation failed ({len(errors)} errors):", file=sys.stderr
        )
        for e in errors:
            print(e, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
