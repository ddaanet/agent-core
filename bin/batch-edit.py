#!/usr/bin/env python3
"""Apply multiple file edits from a marker-based format.

Format:
    path/to/file
    <<<
    old text (can be multi-line)
    >>>
    new text (can be multi-line)
    ===

Each edit block starts with a file path, then old text between <<< and >>>,
then new text between >>> and ===.

Usage:
    batch-edit.py edits.txt
    batch-edit.py < edits.txt
"""

import sys
from pathlib import Path


def parse_edits(content):
    """Parse marker-format edit specifications.

    Yields (filepath, old_text, new_text) tuples.
    """
    lines = content.split('\n')
    i = 0
    n = len(lines)

    while i < n:
        # Skip empty lines
        while i < n and not lines[i].strip():
            i += 1
        if i >= n:
            break

        # File path
        filepath = lines[i].strip()
        i += 1

        # Expect <<<
        while i < n and not lines[i].strip():
            i += 1
        if i >= n or lines[i].strip() != '<<<':
            raise ValueError(f"Expected '<<<' after filepath '{filepath}', got '{lines[i] if i < n else 'EOF'}'")
        i += 1

        # Collect old text until >>>
        old_lines = []
        while i < n and lines[i].strip() != '>>>':
            old_lines.append(lines[i])
            i += 1
        if i >= n:
            raise ValueError(f"Expected '>>>' to end old text for '{filepath}'")
        old_text = '\n'.join(old_lines)
        i += 1

        # Collect new text until ===
        new_lines = []
        while i < n and lines[i].strip() != '===':
            new_lines.append(lines[i])
            i += 1
        if i >= n:
            raise ValueError(f"Expected '===' to end new text for '{filepath}'")
        new_text = '\n'.join(new_lines)
        i += 1

        yield filepath, old_text, new_text


def apply_edit(filepath, old_text, new_text):
    """Apply a single edit. Returns (success, message)."""
    path = Path(filepath)

    if not path.exists():
        return False, f"File not found: {filepath}"

    content = path.read_text()
    count = content.count(old_text)

    if count == 0:
        return False, f"No match found in {filepath}"
    if count > 1:
        return False, f"Multiple matches ({count}) in {filepath}"

    new_content = content.replace(old_text, new_text, 1)
    path.write_text(new_content)
    return True, f"Applied edit to {filepath}"


def main():
    if len(sys.argv) > 1:
        content = Path(sys.argv[1]).read_text()
    else:
        content = sys.stdin.read()

    success_count = 0
    error_count = 0

    for filepath, old_text, new_text in parse_edits(content):
        success, message = apply_edit(filepath, old_text, new_text)
        if success:
            print(f"  {message}")
            success_count += 1
        else:
            print(f"  ERROR: {message}", file=sys.stderr)
            error_count += 1

    print(f"\n{success_count} edits applied, {error_count} errors")
    sys.exit(1 if error_count else 0)


if __name__ == "__main__":
    main()
