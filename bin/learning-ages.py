#!/usr/bin/env python3
"""Calculate git-active-day age per learning entry.

Usage:
    learning-ages.py [learnings-file]

Default: agents/learnings.md

Output: Markdown report to stdout
Exit: 0 on success, 1 on error (stderr)
"""

import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path


TITLE_PATTERN = re.compile(r"^## (.+)$")
REMOVED_HEADER_PATTERN = re.compile(r"^-## ")


def extract_titles(lines):
    """Extract (line_number, title_text) pairs from learning titles.

    Skips first 10 lines (preamble) matching validate-learnings.py pattern.
    """
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


def get_commit_date_for_line(filepath, line_number):
    """Get commit date for specific line using git blame.

    Args:
        filepath: Path to file
        line_number: Line number to blame (1-indexed)

    Returns:
        Date string (YYYY-MM-DD) or None on error
    """
    try:
        # git blame -C -C --first-parent -- <file>
        # -C -C: detect renames and copies across files
        # --first-parent: handle merge commits via first-parent chain
        result = subprocess.run(
            ["git", "blame", "-C", "-C", "--first-parent",
             "--line-porcelain", f"-L{line_number},{line_number}", "--", filepath],
            capture_output=True,
            text=True,
            check=True
        )

        # Parse porcelain output for commit date
        # Format: "committer-time <unix-timestamp>"
        for line in result.stdout.splitlines():
            if line.startswith("committer-time "):
                timestamp = int(line.split()[1])
                date = datetime.fromtimestamp(timestamp)
                return date.strftime("%Y-%m-%d")

        return None
    except subprocess.CalledProcessError as e:
        print(f"Error running git blame for line {line_number}: {e}", file=sys.stderr)
        return None


def get_active_days_since(start_date):
    """Calculate active days (unique commit dates) since start_date.

    Args:
        start_date: ISO date string (YYYY-MM-DD)

    Returns:
        Number of unique commit dates from start_date to today
    """
    try:
        # Get all commit dates since start_date
        result = subprocess.run(
            ["git", "log", "--format=%ad", "--date=short",
             f"--since={start_date}"],
            capture_output=True,
            text=True,
            check=True
        )

        # Build set of unique dates
        commit_dates = set()
        for line in result.stdout.splitlines():
            if line.strip():
                commit_dates.add(line.strip())

        # Edge case: entry added today → 0 active days
        # (git log --since=<today> includes commits from today)
        return len(commit_dates)
    except subprocess.CalledProcessError as e:
        print(f"Error calculating active days: {e}", file=sys.stderr)
        return 0


def get_last_consolidation_date(filepath):
    """Find last consolidation by detecting removed H2 headers in git log.

    Args:
        filepath: Path to learnings file

    Returns:
        Tuple of (date_string, active_days) or (None, None) if not found
    """
    try:
        # Walk git log -p looking for removed H2 headers
        result = subprocess.run(
            ["git", "log", "-p", "--first-parent", "--", filepath],
            capture_output=True,
            text=True,
            check=True
        )

        current_commit_date = None
        for line in result.stdout.splitlines():
            # Track commit dates
            if line.startswith("Date:"):
                # Parse date from git log output
                # Format: "Date:   Wed Jan 29 12:34:56 2025 -0800"
                date_str = " ".join(line.split()[1:])
                try:
                    date_obj = datetime.strptime(date_str, "%a %b %d %H:%M:%S %Y %z")
                    current_commit_date = date_obj.strftime("%Y-%m-%d")
                except ValueError:
                    continue

            # Look for removed H2 headers (lines starting with "-## ")
            if REMOVED_HEADER_PATTERN.match(line):
                if current_commit_date:
                    # Found most recent consolidation
                    active_days = get_active_days_since(current_commit_date)
                    return (current_commit_date, active_days)

        # No removed headers found
        return (None, None)
    except subprocess.CalledProcessError as e:
        print(f"Error searching for consolidation: {e}", file=sys.stderr)
        return (None, None)


def main():
    # Parse arguments
    filepath = sys.argv[1] if len(sys.argv) > 1 else "agents/learnings.md"

    # Check file exists
    if not Path(filepath).exists():
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)

    # Read file
    try:
        with open(filepath) as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)

    # Extract learning entries
    titles = extract_titles(lines)

    if not titles:
        print(f"Error: No learning entries found in {filepath}", file=sys.stderr)
        sys.exit(1)

    # Calculate ages for each entry
    entries_with_ages = []
    for line_num, title in titles:
        commit_date = get_commit_date_for_line(filepath, line_num)
        if commit_date:
            active_days = get_active_days_since(commit_date)
            entries_with_ages.append((title, active_days, commit_date))

    # Get staleness info
    last_consolidation_date, staleness_days = get_last_consolidation_date(filepath)

    # Calculate summary statistics
    total_entries = len(entries_with_ages)
    entries_7plus = len([e for e in entries_with_ages if e[1] >= 7])
    total_lines = len(lines)

    # Generate markdown report
    print("# Learning Ages Report")
    print()
    print(f"**File lines:** {total_lines}")

    if last_consolidation_date:
        print(f"**Last consolidation:** {staleness_days} active days ago")
    else:
        print("**Last consolidation:** N/A (no prior consolidation detected)")

    print(f"**Total entries:** {total_entries}")
    print(f"**Entries ≥7 active days:** {entries_7plus}")
    print()
    print("## Entries by Age")
    print()

    # Sort by active days descending
    entries_with_ages.sort(key=lambda x: x[1], reverse=True)

    for title, active_days, commit_date in entries_with_ages:
        print(f"- **{active_days} days**: {title} (added {commit_date})")


if __name__ == "__main__":
    main()
