#!/usr/bin/env python3
"""Validate decision file structure.

Detects sections with no direct content (only sub-headings).
Such sections must be marked structural with '.' prefix.

Hard error - no autofix. Agent decides:
- Add '.' prefix → organizational grouping
- Add substantive content → knowledge section
"""

import re
import sys
from pathlib import Path

# Minimum substantive lines before first sub-heading to be considered "knowledge"
CONTENT_THRESHOLD = 2

DECISION_GLOBS = [
    "agents/decisions/*.md",
]


def find_project_root():
    """Walk up from script to find project root (has CLAUDE.md)."""
    p = Path(__file__).resolve().parent
    while p != p.parent:
        if (p / "CLAUDE.md").exists():
            return p
        p = p.parent
    return Path.cwd()


def parse_heading(line):
    """Parse a heading line. Returns (level, title, is_structural) or None."""
    match = re.match(r'^(#{2,6}) (.+)$', line.strip())
    if not match:
        return None
    level = len(match.group(1))
    title = match.group(2)
    is_structural = title.startswith('.')
    return level, title, is_structural


def analyze_file(filepath):
    """Analyze a file for organizational sections missing structural marker.

    Returns list of (line_number, heading_title, level) for violations.
    """
    try:
        lines = filepath.read_text().splitlines()
    except (OSError, UnicodeDecodeError):
        return []

    violations = []
    i = 0
    n = len(lines)

    while i < n:
        parsed = parse_heading(lines[i])
        if not parsed:
            i += 1
            continue

        level, title, is_structural = parsed
        heading_line = i + 1  # 1-indexed for error messages
        i += 1

        # Already structural - skip
        if is_structural:
            continue

        # Collect content until next heading at same or higher level
        content_lines = []
        first_subheading_idx = None

        while i < n:
            next_parsed = parse_heading(lines[i])
            if next_parsed:
                next_level = next_parsed[0]
                # Same or higher level = end of this section
                if next_level <= level:
                    break
                # Sub-heading found
                if first_subheading_idx is None:
                    first_subheading_idx = len(content_lines)
            content_lines.append(lines[i])
            i += 1

        # No sub-headings = not organizational (all content is direct)
        if first_subheading_idx is None:
            continue

        # Count substantive lines before first sub-heading
        before_subheading = content_lines[:first_subheading_idx]
        substantive = [
            line for line in before_subheading
            if line.strip() and not line.strip().startswith('<!--')
        ]

        # Organizational if few substantive lines before sub-heading
        if len(substantive) <= CONTENT_THRESHOLD:
            violations.append((heading_line, title, level))

    return violations


def validate():
    """Validate all decision files. Returns list of error strings."""
    root = find_project_root()
    errors = []

    for glob_pattern in DECISION_GLOBS:
        for filepath in sorted(root.glob(glob_pattern)):
            rel = filepath.relative_to(root)
            violations = analyze_file(filepath)

            for lineno, title, level in violations:
                hashes = '#' * level
                errors.append(
                    f"  {rel}:{lineno}: section '{title}' has no direct content\n"
                    f"    Action required:\n"
                    f"    A) Mark structural: '{hashes} .{title}'\n"
                    f"    B) Add substantive content before sub-headings"
                )

    return errors


def main():
    errors = validate()

    if errors:
        print(
            f"Decision file validation failed ({len(errors)} errors):",
            file=sys.stderr,
        )
        for e in errors:
            print(e, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
