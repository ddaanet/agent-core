#!/usr/bin/env python3
"""
Assemble runbook from phase files.

Reads runbook-outline.md for metadata and all runbook-phase-N.md files,
then assembles them into a complete runbook.md with orchestrator metadata.
"""

import sys
import re
from pathlib import Path
import yaml


def extract_yaml_frontmatter(content: str) -> tuple[dict, str]:
    """Extract YAML frontmatter and return (dict, remaining_content)."""
    if not content.startswith("---"):
        return {}, content

    lines = content.split("\n")
    if len(lines) < 2:
        return {}, content

    try:
        end_idx = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        return {}, content

    yaml_content = "\n".join(lines[1:end_idx])
    remaining = "\n".join(lines[end_idx + 1:])

    try:
        data = yaml.safe_load(yaml_content) or {}
    except yaml.YAMLError:
        return {}, content

    return data, remaining


def extract_metadata_from_outline(outline_content: str) -> dict:
    """Extract design ref, type, requirements mapping, and key decisions from outline."""
    metadata = {}

    # Extract design reference
    match = re.search(r"\*\*Design:\*\*\s+(.+?)(?:\n|$)", outline_content)
    if match:
        metadata["design"] = match.group(1).strip()

    # Extract type
    match = re.search(r"\*\*Type:\*\*\s+(.+?)(?:\n|$)", outline_content)
    if match:
        metadata["type"] = match.group(1).strip()

    return metadata


def count_steps(content: str) -> int:
    """Count total steps in phase content."""
    return len(re.findall(r"^###\s+Step\s+\d+\.\d+:", content, re.MULTILINE))


def assemble_runbook(runbook_dir: str) -> str:
    """
    Assemble runbook from phase files.

    Args:
        runbook_dir: Path to runbook directory (e.g., plans/workflow-feedback-loops)

    Returns:
        Path to created runbook.md
    """
    runbook_path = Path(runbook_dir)
    if not runbook_path.is_dir():
        print(f"Error: {runbook_dir} is not a directory", file=sys.stderr)
        sys.exit(1)

    # Read outline
    outline_file = runbook_path / "runbook-outline.md"
    if not outline_file.exists():
        print(f"Error: {outline_file} not found", file=sys.stderr)
        sys.exit(1)

    outline_content = outline_file.read_text()

    # Extract metadata from outline
    metadata = extract_metadata_from_outline(outline_content)

    # Extract requirements mapping and key decisions sections
    requirements_section = ""
    key_decisions_section = ""

    # Find Requirements Mapping section
    req_match = re.search(
        r"(## Requirements Mapping\n\n.*?)(?:\n## |\Z)",
        outline_content,
        re.DOTALL
    )
    if req_match:
        requirements_section = req_match.group(1).rstrip()

    # Find Key Decisions Reference section
    decisions_match = re.search(
        r"(## Key Decisions Reference\n\n.*?)(?:\n## |\Z)",
        outline_content,
        re.DOTALL
    )
    if decisions_match:
        key_decisions_section = decisions_match.group(1).rstrip()

    # Collect all phase files
    phase_files = sorted(
        runbook_path.glob("runbook-phase-*.md"),
        key=lambda p: int(p.stem.split("-")[-1])
    )

    if not phase_files:
        print(f"Error: No runbook-phase-*.md files found in {runbook_dir}", file=sys.stderr)
        sys.exit(1)

    # Read all phase content
    phases_content = []
    total_steps = 0

    for phase_file in phase_files:
        content = phase_file.read_text()
        phases_content.append(content)
        total_steps += count_steps(content)

    # Get directory name as runbook name
    runbook_name = runbook_path.name

    # Build YAML frontmatter
    frontmatter = {
        "name": runbook_name,
        "model": "sonnet",
    }

    # Build runbook content
    runbook_lines = []
    runbook_lines.append("---")
    runbook_lines.append(yaml.dump(frontmatter, default_flow_style=False, sort_keys=False).rstrip())
    runbook_lines.append("---")
    runbook_lines.append("")

    # Add Common Context section
    runbook_lines.append("## Common Context")
    runbook_lines.append("")

    if metadata.get("design"):
        runbook_lines.append(f"**Design Reference:** {metadata['design']}")
        runbook_lines.append("")

    if requirements_section:
        runbook_lines.append(requirements_section)
        runbook_lines.append("")

    if key_decisions_section:
        runbook_lines.append(key_decisions_section)
        runbook_lines.append("")

    # Add Weak Orchestrator Metadata section
    runbook_lines.append("## Weak Orchestrator Metadata")
    runbook_lines.append("")
    runbook_lines.append("| Attribute | Value |")
    runbook_lines.append("|-----------|-------|")
    runbook_lines.append(f"| Total Steps | {total_steps} |")
    runbook_lines.append("| Execution Model | Sequential |")
    runbook_lines.append("| Dependencies | See design for cross-plan dependencies |")
    runbook_lines.append("| Error Escalation | Any phase failure → stop and report |")
    runbook_lines.append("")

    # Add all phase content
    for content in phases_content:
        runbook_lines.append(content)
        runbook_lines.append("")

    # Add Orchestrator Instructions section
    runbook_lines.append("## Orchestrator Instructions")
    runbook_lines.append("")
    runbook_lines.append("Execute all phases sequentially:")
    runbook_lines.append("")
    runbook_lines.append("1. Read each phase header to understand objective and complexity")
    runbook_lines.append("2. Execute all steps in phase order")
    runbook_lines.append("3. After each phase: check reports directory for review results")
    runbook_lines.append("4. If review identifies blockers: fix and re-run phase")
    runbook_lines.append("5. Continue to next phase")
    runbook_lines.append("")
    runbook_lines.append("**Stop on:** Any failure in step execution, blocker in review, or missing artifact.")
    runbook_lines.append("")

    # Write runbook
    output_file = runbook_path / "runbook.md"
    output_file.write_text("\n".join(runbook_lines))

    # Return absolute path
    return str(output_file.resolve())


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: assemble-runbook.py <runbook-directory>", file=sys.stderr)
        print("Example: assemble-runbook.py plans/workflow-feedback-loops", file=sys.stderr)
        sys.exit(1)

    result = assemble_runbook(sys.argv[1])
    print(result)
