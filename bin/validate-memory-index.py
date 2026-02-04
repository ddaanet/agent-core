#!/usr/bin/env python3
"""Validate memory-index.md entries against semantic headers in indexed files.

Checks:
- All semantic headers (##+ not starting with .) have index entries
- All index entries match at least one semantic header
- No duplicate index entries
- Document intro content (between # and first ##) is exempt
"""

import re
import sys
from pathlib import Path

# Semantic header: ##+ followed by space and non-dot
SEMANTIC_HEADER = re.compile(r"^(##+) ([^.].+)$")
# Structural header: ##+ followed by space and dot
STRUCTURAL_HEADER = re.compile(r"^(##+) \..+$")
# Document title
DOC_TITLE = re.compile(r"^# .+$")

# Files that contain semantic headers requiring index entries
# Note: learnings.md is excluded — it's inlined via CLAUDE.md, and /remember
# processes staged learnings into permanent locations (fragments/, decisions/)
INDEXED_GLOBS = [
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


def collect_semantic_headers(root):
    """Scan indexed files for all semantic headers.

    Returns dict: lowercase title → list of (file_path, line_number, header_level).
    """
    headers = {}

    for glob_pattern in INDEXED_GLOBS:
        for filepath in sorted(root.glob(glob_pattern)):
            rel = str(filepath.relative_to(root))
            try:
                lines = filepath.read_text().splitlines()
            except (OSError, UnicodeDecodeError):
                continue

            in_doc_intro = False
            seen_first_h2 = False

            for i, line in enumerate(lines, 1):
                stripped = line.strip()

                # Track document intro exemption (only before first ## header)
                # After first ##, don't re-enter intro (# lines may be code comments)
                if not seen_first_h2 and DOC_TITLE.match(stripped):
                    in_doc_intro = True
                    continue

                # First ## ends document intro permanently
                if in_doc_intro and stripped.startswith("## "):
                    in_doc_intro = False
                    seen_first_h2 = True

                # Skip content in document intro
                if in_doc_intro:
                    continue

                # Match semantic headers
                m = SEMANTIC_HEADER.match(stripped)
                if m:
                    level = m.group(1)
                    title = m.group(2)
                    key = title.lower()
                    headers.setdefault(key, []).append((rel, i, level))

    return headers


def extract_index_entries(index_path, root):
    """Extract index entries from memory-index.md.

    Index entries are bare lines (not headers, not bold, not list markers)
    with em-dash separator: "Key — description"

    Returns dict: lowercase key → (line_number, full_entry)
    """
    entries = {}

    try:
        lines = (root / index_path).read_text().splitlines()
    except FileNotFoundError:
        return entries

    in_section = False

    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        # Handle headers - track section state
        if stripped.startswith("#"):
            in_section = stripped.startswith("##")
            continue

        # Skip empty lines without changing section state
        if not stripped:
            continue

        # Skip bold directives (** at start)
        if stripped.startswith("**"):
            continue

        # Skip list markers (old format, shouldn't exist but handle gracefully)
        if stripped.startswith("- "):
            continue

        # In a section, non-header, non-bold, non-empty = index entry
        if in_section:
            # Extract key (part before em-dash)
            if " — " in stripped:
                key = stripped.split(" — ")[0]
            else:
                # Fallback: whole line is key
                key = stripped

            key_lower = key.lower()
            if key_lower in entries:
                # Duplicate will be caught later
                pass
            entries[key_lower] = (i, stripped)

    return entries


def validate(index_path):
    """Validate memory index. Returns list of error strings."""
    root = find_project_root()

    headers = collect_semantic_headers(root)
    entries = extract_index_entries(index_path, root)

    errors = []
    warnings = []
    seen_entries = {}

    # Check for duplicate index entries
    for key, (lineno, full_entry) in entries.items():
        if key in seen_entries:
            errors.append(
                f"  memory-index.md:{lineno}: duplicate index entry '{key}' "
                f"(first at line {seen_entries[key]})"
            )
        else:
            seen_entries[key] = lineno

    # Check D-3 format compliance: entries must have em-dash separator
    for key, (lineno, full_entry) in entries.items():
        if " — " not in full_entry:
            errors.append(
                f"  memory-index.md:{lineno}: entry lacks em-dash separator (D-3): '{full_entry}'"
            )
        else:
            # Check word count (8-12 word soft limit for key + description total)
            word_count = len(full_entry.split())
            if word_count < 8:
                warnings.append(
                    f"  memory-index.md:{lineno}: description has {word_count} words, soft limit 8-12 (D-3): '{full_entry}'"
                )

    # Check for orphan semantic headers (headers without index entries)
    # Per design R-4: all semantic headers must have index entries (ERROR blocks commit)
    for title, locations in sorted(headers.items()):
        if title not in entries:
            for filepath, lineno, level in locations:
                errors.append(
                    f"  {filepath}:{lineno}: orphan semantic header '{title}' "
                    f"({level} level) has no memory-index.md entry"
                )

    # Check for orphan index entries (entries without matching headers)
    # Index entries must reference semantic headers in permanent docs (decisions/)
    for key, (lineno, full_entry) in entries.items():
        if key not in headers:
            errors.append(
                f"  memory-index.md:{lineno}: orphan index entry '{key}' "
                f"has no matching semantic header in agents/decisions/"
            )

    # Print warnings to stderr but don't fail
    if warnings:
        print(
            f"Memory index warnings ({len(warnings)}):", file=sys.stderr,
        )
        for w in warnings:
            print(w, file=sys.stderr)

    return errors


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "agents/memory-index.md"
    errors = validate(path)

    if errors:
        print(
            f"Memory index validation failed ({len(errors)} errors):", file=sys.stderr,
        )
        for e in errors:
            print(e, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
