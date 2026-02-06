#!/usr/bin/env python3
"""Validate jobs.md matches plans/ directory contents."""

import re
import sys
from pathlib import Path


def parse_jobs_md(jobs_path: Path) -> dict[str, str]:
    """Extract plan names and statuses from jobs.md Plans table."""
    content = jobs_path.read_text()
    plans: dict[str, str] = {}

    # Find the Plans table section
    in_table = False
    for line in content.splitlines():
        if line.startswith("## Plans"):
            in_table = True
            continue
        if in_table and line.startswith("## "):
            break
        if in_table and line.startswith("|") and not line.startswith("| Plan"):
            # Skip header separator
            if line.startswith("|---"):
                continue
            # Parse table row: | plan-name | status | notes |
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 3:
                plan_name = parts[1]
                status = parts[2]
                if plan_name and status:
                    plans[plan_name] = status

    return plans


def get_plans_directories(plans_dir: Path) -> set[str]:
    """Get all plan directories and files from plans/."""
    plans: set[str] = set()

    if not plans_dir.exists():
        return plans

    for item in plans_dir.iterdir():
        if item.name.startswith("."):
            continue

        # Skip plans/claude/ (gitignored, ephemeral plan-mode files)
        if item.name == "claude" and item.is_dir():
            continue

        # Regular .md files (one-off documents)
        if item.is_file() and item.suffix == ".md":
            if item.name != "README.md":
                plans.add(item.stem)
            continue

        # Plan directories
        if item.is_dir():
            plans.add(item.name)

    return plans


def main() -> int:
    """Validate jobs.md against plans/ directory."""
    # Find project root (where CLAUDE.md lives)
    cwd = Path.cwd()
    while cwd != cwd.parent:
        if (cwd / "CLAUDE.md").exists():
            break
        cwd = cwd.parent
    else:
        print("Error: Could not find project root (no CLAUDE.md)", file=sys.stderr)
        return 1

    jobs_path = cwd / "agents" / "jobs.md"
    plans_dir = cwd / "plans"

    if not jobs_path.exists():
        print(f"Error: {jobs_path} not found", file=sys.stderr)
        return 1

    jobs_plans = parse_jobs_md(jobs_path)
    dir_plans = get_plans_directories(plans_dir)

    errors: list[str] = []

    # Check for plans in directory but not in jobs.md
    missing_from_jobs = dir_plans - set(jobs_plans.keys())
    for plan in sorted(missing_from_jobs):
        errors.append(f"Plan '{plan}' exists in plans/ but not in jobs.md")

    # Check for plans in jobs.md but not in directory (excluding complete plans)
    for plan, status in jobs_plans.items():
        if status != "complete" and plan not in dir_plans:
            errors.append(
                f"Plan '{plan}' in jobs.md (status: {status}) "
                f"but not found in plans/"
            )

    if errors:
        print("jobs.md validation errors:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
