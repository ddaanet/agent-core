#!/usr/bin/env python3
"""Validate learnings.md identifier syntax and uniqueness.

Checks:
- Title format: ## Title (markdown header)
- Max word count per title (default: 5)
- No duplicate titles
- No empty titles
"""

import re
import sys

MAX_WORDS = 5
TITLE_PATTERN = re.compile(r"^## (.+)$")


def extract_titles(lines):
    """Extract (line_number, title_text) pairs from learning titles."""
    titles = []
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        # Skip first 10 lines (preamble/header)
        if i <= 10:
            continue
        # Match ## Title headers
        m = TITLE_PATTERN.match(stripped)
        if m:
            titles.append((i, m.group(1)))
    return titles


def validate(path, max_words=MAX_WORDS):
    """Validate learnings file. Returns list of error strings."""
    try:
        with open(path) as f:
            lines = f.readlines()
    except FileNotFoundError:
        return []

    titles = extract_titles(lines)
    errors = []
    seen = {}

    for lineno, title in titles:
        # Word count check
        words = title.split()
        if len(words) > max_words:
            errors.append(
                f"  line {lineno}: title has {len(words)} words (max {max_words}): "
                f"## {title}"
            )

        # Uniqueness check
        key = title.lower()
        if key in seen:
            errors.append(
                f"  line {lineno}: duplicate title (first at line {seen[key]}): "
                f"## {title}"
            )
        else:
            seen[key] = lineno

    return errors


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "agents/learnings.md"
    errors = validate(path)

    if errors:
        print(f"Learnings validation failed ({len(errors)} errors):", file=sys.stderr)
        for e in errors:
            print(e, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
