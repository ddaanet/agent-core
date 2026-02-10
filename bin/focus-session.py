#!/usr/bin/env python3
"""
Focus session.md on a specific task for worktree isolation.

Extracts a single task from session.md and creates minimal context
suitable for focused work in a git worktree.

Usage:
    focus-session.py '<task-name>' > tmp/focused-session.md
    just wt-new mywork session=tmp/focused-session.md
"""
import re
import sys
from pathlib import Path


def extract_task(session_content: str, task_name: str) -> tuple[str, list[str]]:
    """Extract task and its related context from session.md.

    Returns:
        (task_markdown, related_plan_refs)
    """
    lines = session_content.split('\n')

    # Find the task line
    task_pattern = re.compile(rf'- \[.\] \*\*{re.escape(task_name)}\*\*')
    task_line_idx = None

    for i, line in enumerate(lines):
        if task_pattern.search(line):
            task_line_idx = i
            break

    if task_line_idx is None:
        print(f"Error: Task '{task_name}' not found in session.md", file=sys.stderr)
        sys.exit(1)

    # Extract task and any indented continuation lines
    task_lines = [lines[task_line_idx]]
    i = task_line_idx + 1
    while i < len(lines) and (lines[i].startswith('  ') or lines[i].strip() == ''):
        task_lines.append(lines[i])
        i += 1

    task_text = '\n'.join(task_lines)

    # Extract plan references from task (both formats)
    plan_refs = []
    # Format 1: plans/plan-name/
    plan_refs.extend(re.findall(r'plans/([^/\s]+)', task_text))
    # Format 2: Plan: plan-name
    plan_refs.extend(re.findall(r'Plan:\s+([^\s|]+)', task_text))

    # Remove duplicates while preserving order
    seen = set()
    plan_refs = [p for p in plan_refs if not (p in seen or seen.add(p))]

    return task_text, plan_refs


def extract_section(content: str, section_header: str, max_lines: int = 20) -> list[str]:
    """Extract content from a markdown section until next ## header.

    Includes ### subsections within the ## section.
    """
    lines = content.split('\n')
    extracted = []
    in_section = False
    line_count = 0

    for line in lines:
        if line.strip() == f"## {section_header}":
            in_section = True
            continue
        elif line.startswith("##") and not line.startswith("###") and in_section:
            # Next ## section, stop
            break
        elif in_section:
            if line.strip():  # Non-empty line
                extracted.append(line)
                line_count += 1
                if line_count >= max_lines:
                    break
            elif extracted and not line.strip():  # Preserve blank lines within section
                extracted.append(line)

    return extracted


def extract_doc_summary(doc_path: Path) -> str:
    """Extract relevant summary from different document types."""
    if not doc_path.exists():
        return ""

    content = doc_path.read_text()
    doc_type = doc_path.stem
    result = ""

    if doc_type == "rca":
        # Extract executive summary and fix tasks
        summary = extract_section(content, "Executive Summary", max_lines=10)
        fixes = extract_section(content, "Fix Tasks", max_lines=15)

        if summary:
            result += "\n**RCA Summary:**\n" + '\n'.join(summary) + "\n"
        if fixes:
            # Filter to just the numbered/bulleted items
            fix_items = [l for l in fixes if l.strip() and (l.strip()[0].isdigit() or l.strip().startswith('-'))]
            if fix_items:
                result += "\n**Required Fixes:**\n" + '\n'.join(fix_items[:10]) + "\n"

    elif doc_type == "requirements":
        # Extract Requirements or Functional Requirements section
        reqs = extract_section(content, "Requirements", max_lines=15)
        if not reqs:
            reqs = extract_section(content, "Functional Requirements", max_lines=15)
        if reqs:
            result += "\n**Requirements:**\n" + '\n'.join(reqs) + "\n"

    elif doc_type == "design":
        # Extract Problem and Requirements sections
        problem = extract_section(content, "Problem", max_lines=8)
        reqs = extract_section(content, "Requirements", max_lines=12)

        if problem:
            result += "\n**Problem:**\n" + '\n'.join(problem) + "\n"
        if reqs:
            result += "\n**Requirements:**\n" + '\n'.join(reqs) + "\n"

    elif doc_type == "problem":
        # Extract first 15 lines after title
        lines = content.split('\n')
        problem_lines = []
        skip_title = True
        for line in lines:
            if skip_title and line.startswith('#'):
                skip_title = False
                continue
            if not skip_title and line.strip():
                problem_lines.append(line)
                if len(problem_lines) >= 15:
                    break
        if problem_lines:
            result += "\n**Problem Statement:**\n" + '\n'.join(problem_lines) + "\n"

    elif doc_type in ("runbook", "runbook-outline", "outline"):
        # Extract overview or summary
        overview = extract_section(content, "Overview", max_lines=10)
        if not overview:
            overview = extract_section(content, "Summary", max_lines=10)
        if overview:
            result += "\n**Overview:**\n" + '\n'.join(overview) + "\n"

    return result


def create_focused_session(task_markdown: str, plan_refs: list[str]) -> str:
    """Create minimal session.md focused on one task."""
    from datetime import date

    # Build reference section with document excerpts if available
    ref_section = ""
    if plan_refs:
        ref_section = "\n## Context\n"
        for plan in plan_refs:
            ref_section += f"\n### Plan: {plan}\n"

            plan_dir = Path(f'plans/{plan}')
            if not plan_dir.exists():
                continue

            # Check for primary document types in priority order
            doc_types = ['rca.md', 'requirements.md', 'design.md', 'problem.md',
                        'runbook-outline.md', 'runbook.md', 'outline.md']

            found_docs = []
            for doc_type in doc_types:
                doc_path = plan_dir / doc_type
                if doc_path.exists():
                    excerpt = extract_doc_summary(doc_path)
                    if excerpt:
                        ref_section += excerpt
                    found_docs.append(doc_type)

            # List all available documents
            all_docs = sorted([d.name for d in plan_dir.glob('*.md')])
            if all_docs:
                ref_section += f"\n**Available docs:** {', '.join(f'`{d}`' for d in all_docs[:8])}\n"

    return f"""# Session Handoff: {date.today().isoformat()}

**Status:** Focused worktree session

## Pending Tasks

{task_markdown}
{ref_section}
---
*Focused session for worktree isolation*
"""


def main():
    if len(sys.argv) != 2:
        print("Usage: focus-session.py '<task-name>'", file=sys.stderr)
        print("Example: focus-session.py 'Strengthen vet-fix-agent delegation pattern'", file=sys.stderr)
        sys.exit(1)

    task_name = sys.argv[1]

    # Read current session.md
    session_path = Path('agents/session.md')
    if not session_path.exists():
        print("Error: agents/session.md not found", file=sys.stderr)
        sys.exit(1)

    session_content = session_path.read_text()

    # Extract and focus
    task_markdown, plan_refs = extract_task(session_content, task_name)
    focused = create_focused_session(task_markdown, plan_refs)

    print(focused)


if __name__ == '__main__':
    main()
