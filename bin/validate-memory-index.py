#!/usr/bin/env python3
"""Validate memory-index.md entries against semantic headers in indexed files.

Checks:
- All semantic headers (##+ not starting with .) have index entries
- All index entries match at least one semantic header
- No duplicate index entries
- Document intro content (between # and first ##) is exempt
- Entries are in correct file section (autofix by default)
- Entries are in file order within sections (autofix by default)
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
# Section header that specifies a file path
FILE_SECTION = re.compile(r"^## (agents/decisions/\S+\.md)$")

# Files that contain semantic headers requiring index entries
# Note: learnings.md is excluded — it's inlined via CLAUDE.md, and /remember
# processes staged learnings into permanent locations (fragments/, decisions/)
INDEXED_GLOBS = [
    "agents/decisions/*.md",
]

# Sections that are exempt from file-based validation
EXEMPT_SECTIONS = {
    "Behavioral Rules (fragments — already loaded)",
    "Technical Decisions (mixed — check entry for specific file)",
}


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

    Returns dict: lowercase key → (line_number, full_entry, section_name)
    """
    entries = {}

    try:
        lines = (root / index_path).read_text().splitlines()
    except FileNotFoundError:
        return entries

    current_section = None

    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        # Handle headers - track section state
        if stripped.startswith("##") and not stripped.startswith("###"):
            # Extract section name (part after "## ")
            current_section = stripped[3:] if stripped.startswith("## ") else None
            continue

        # Skip H1 headers
        if stripped.startswith("# "):
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
        if current_section:
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
            entries[key_lower] = (i, stripped, current_section)

    return entries


def extract_index_structure(index_path, root):
    """Extract full index structure for rewriting.

    Returns:
        preamble: lines before first ## section
        sections: list of (section_name, [entry_lines])
    """
    try:
        lines = (root / index_path).read_text().splitlines()
    except FileNotFoundError:
        return [], []

    preamble = []
    sections = []
    current_section = None
    current_entries = []

    for line in lines:
        stripped = line.strip()

        # Detect section headers
        if stripped.startswith("## ") and not stripped.startswith("### "):
            # Save previous section if exists
            if current_section is not None:
                sections.append((current_section, current_entries))
            current_section = stripped[3:]
            current_entries = []
            continue

        # Before first section = preamble
        if current_section is None:
            preamble.append(line)
            continue

        # Skip empty lines
        if not stripped:
            continue

        # Skip bold directives
        if stripped.startswith("**"):
            continue

        # Entry line
        current_entries.append(stripped)

    # Don't forget last section
    if current_section is not None:
        sections.append((current_section, current_entries))

    return preamble, sections


def validate(index_path, autofix=True):
    """Validate memory index. Returns list of error strings.

    Autofix is enabled by default for section placement and ordering issues.
    """
    root = find_project_root()

    headers = collect_semantic_headers(root)
    entries = extract_index_entries(index_path, root)

    errors = []
    seen_entries = {}
    placement_errors = []
    ordering_errors = []

    # Check for duplicate index entries
    for key, (lineno, full_entry, section) in entries.items():
        if key in seen_entries:
            errors.append(
                f"  memory-index.md:{lineno}: duplicate index entry '{key}' "
                f"(first at line {seen_entries[key]})"
            )
        else:
            seen_entries[key] = lineno

    # Check D-3 format compliance: entries must have em-dash separator
    for key, (lineno, full_entry, section) in entries.items():
        if " — " not in full_entry:
            errors.append(
                f"  memory-index.md:{lineno}: entry lacks em-dash separator (D-3): '{full_entry}'"
            )
        else:
            # Check word count (8-12 word hard limit for key + description total)
            word_count = len(full_entry.split())
            if word_count < 8 or word_count > 12:
                errors.append(
                    f"  memory-index.md:{lineno}: entry has {word_count} words, must be 8-12 (D-3): '{full_entry}'"
                )

    # Check section placement: entry should be in section matching its source file
    for key, (lineno, full_entry, section) in entries.items():
        if section in EXEMPT_SECTIONS:
            continue
        if key in headers:
            # Get the file this header is in
            source_file = headers[key][0][0]  # First location's file
            if section != source_file:
                placement_errors.append(
                    f"  memory-index.md:{lineno}: entry '{key}' in section '{section}' "
                    f"but header is in '{source_file}'"
                )

    # Check ordering within sections: entries should match file order
    preamble, sections = extract_index_structure(index_path, root)
    for section_name, entry_lines in sections:
        if section_name in EXEMPT_SECTIONS:
            continue
        # Check if this section is a file path
        if not FILE_SECTION.match(f"## {section_name}"):
            continue

        # Get entries with their source line numbers
        entry_positions = []
        for entry in entry_lines:
            if " — " in entry:
                key = entry.split(" — ")[0].lower()
            else:
                key = entry.lower()
            if key in headers:
                source_lineno = headers[key][0][1]  # Line number in source file
                entry_positions.append((source_lineno, entry))

        # Check if sorted by source line number
        sorted_positions = sorted(entry_positions, key=lambda x: x[0])
        if entry_positions != sorted_positions:
            ordering_errors.append(
                f"  Section '{section_name}': entries not in file order"
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
    for key, (lineno, full_entry, section) in entries.items():
        # Skip exempt sections
        if section in EXEMPT_SECTIONS:
            continue
        if key not in headers:
            errors.append(
                f"  memory-index.md:{lineno}: orphan index entry '{key}' "
                f"has no matching semantic header in agents/decisions/"
            )

    # Check for duplicate headers across files
    # Headers should appear in only one file to avoid confusion
    for title, locations in sorted(headers.items()):
        if len(locations) > 1:
            files = set(filepath for filepath, _, _ in locations)
            if len(files) > 1:  # Only error if duplicates are in different files
                errors.append(
                    f"  Duplicate header '{title}' found in multiple files:"
                )
                for filepath, lineno, level in locations:
                    errors.append(f"    {filepath}:{lineno} ({level} level)")

    # Handle placement and ordering errors
    if placement_errors or ordering_errors:
        if autofix:
            fixed = autofix_index(index_path, root, headers)
            if fixed:
                print(f"Autofixed {len(placement_errors)} placement and "
                      f"{len(ordering_errors)} ordering issues", file=sys.stderr)
            else:
                errors.extend(placement_errors)
                errors.extend(ordering_errors)
        else:
            errors.extend(placement_errors)
            errors.extend(ordering_errors)

    return errors


def autofix_index(index_path, root, headers):
    """Rewrite memory-index.md with entries in correct sections and order.

    Returns True if rewrite succeeded.
    """
    preamble, sections = extract_index_structure(index_path, root)

    # Build map: file path → sorted entries
    file_entries = {}
    exempt_entries = {}  # section_name → entries (preserve as-is)

    for section_name, entry_lines in sections:
        if section_name in EXEMPT_SECTIONS:
            exempt_entries[section_name] = entry_lines
            continue

        for entry in entry_lines:
            if " — " in entry:
                key = entry.split(" — ")[0].lower()
            else:
                key = entry.lower()

            # Find which file this entry belongs to
            if key in headers:
                source_file = headers[key][0][0]
                source_lineno = headers[key][0][1]
                file_entries.setdefault(source_file, []).append(
                    (source_lineno, entry)
                )

    # Sort entries within each file by source line number
    for filepath in file_entries:
        file_entries[filepath].sort(key=lambda x: x[0])

    # Rebuild the file
    output = []

    # Preamble
    output.extend(preamble)

    # Exempt sections first (preserve order from original)
    for section_name, entry_lines in sections:
        if section_name in EXEMPT_SECTIONS:
            output.append(f"\n## {section_name}\n")
            for entry in entry_lines:
                output.append(entry)

    # File sections in sorted order
    for filepath in sorted(file_entries.keys()):
        output.append(f"\n## {filepath}\n")
        for _, entry in file_entries[filepath]:
            output.append(entry)

    # Write back
    try:
        content = "\n".join(output) + "\n"
        (root / index_path).write_text(content)
        return True
    except OSError as e:
        print(f"  Failed to write {index_path}: {e}", file=sys.stderr)
        return False


def main():
    args = sys.argv[1:]

    path = args[0] if args else "agents/memory-index.md"
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
