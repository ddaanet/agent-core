#!/usr/bin/env python3
"""Deliverable inventory: diff merge-base→HEAD, classify files, report counts.

Usage: deliverable-inventory.py [plan-name]

Excludes plan artifacts (plans/, session.md, learnings.md, plan-archive.md, tmp/).
Handles submodule diffs by resolving submodule pointer at merge base.
Outputs markdown table to stdout.
"""

import subprocess
import sys
from pathlib import Path

EXCLUDE = {"agents/session.md", "agents/plan-archive.md", "agents/learnings.md"}
EXCLUDE_PREFIXES = ("plans/", "tmp/")


def run(cmd: str, cwd: str | None = None) -> str:
    r = subprocess.run(
        cmd, check=False, shell=True, capture_output=True, text=True, cwd=cwd
    )
    return r.stdout.strip()


def classify(path: str) -> str:
    name = Path(path).name
    if name.startswith("test_") and name.endswith(".py"):
        return "Test"
    if name.endswith((".py", ".sh")):
        return "Code"
    if name == "SKILL.md":
        return "Agentic prose"
    if name.endswith(".md"):
        parts = path.lower()
        if any(d in parts for d in ("skills/", "agents/", "fragments/")):
            return "Agentic prose"
        return "Human docs"
    if name in ("justfile", "Justfile", "pyproject.toml") or name.endswith(
        (".toml", ".json", ".cfg")
    ):
        return "Configuration"
    return "Configuration"


def numstat(
    base: str, head: str = "HEAD", cwd: str | None = None
) -> list[tuple[int, int, str]]:
    """Parse git diff --numstat into (plus, minus, path) tuples."""
    out = run(f"git diff {base}..{head} --numstat --diff-filter=ACMR", cwd=cwd)
    results = []
    for line in out.splitlines():
        parts = line.split("\t", 2)
        if len(parts) != 3:
            continue
        p, m, f = parts
        results.append((int(p) if p != "-" else 0, int(m) if m != "-" else 0, f))
    return results


def submodule_paths() -> list[str]:
    out = run("git config --file .gitmodules --get-regexp 'submodule\\..*\\.path'")
    return [line.split()[-1] for line in out.splitlines() if line]


def submodule_commit(tree: str, path: str) -> str | None:
    out = run(f"git ls-tree {tree} {path}")
    parts = out.split()
    return parts[2] if len(parts) >= 3 else None


def excluded(path: str) -> bool:
    return path in EXCLUDE or any(path.startswith(p) for p in EXCLUDE_PREFIXES)


def main() -> None:
    merge_base = run("git merge-base HEAD main")
    if not merge_base:
        print("ERROR: Cannot find merge base with main", file=sys.stderr)
        sys.exit(1)

    submods = submodule_paths()

    # Parent repo files
    entries: list[tuple[str, str, int, int]] = []
    for plus, minus, path in numstat(merge_base):
        if path in submods or excluded(path):
            continue
        entries.append((classify(path), path, plus, minus))

    # Submodule files
    for sm in submods:
        base_c = submodule_commit(merge_base, sm)
        head_c = submodule_commit("HEAD", sm)
        if not base_c or not head_c or base_c == head_c:
            continue
        for plus, minus, path in numstat(base_c, head_c, cwd=sm):
            display = f"{sm}/{path}"
            if not excluded(display):
                entries.append((classify(display), display, plus, minus))

    # Print per-file table
    print("## Deliverable Inventory\n")
    print(f"**Merge base:** `{merge_base[:8]}`\n")
    print("| Type | File | + | - |")
    print("|------|------|---|---|")
    for typ, path, plus, minus in entries:
        print(f"| {typ} | {path} | +{plus} | -{minus} |")

    # Summarize by type
    totals: dict[str, list[int]] = {}
    for typ, _, plus, minus in entries:
        t = totals.setdefault(typ, [0, 0, 0])
        t[0] += 1
        t[1] += plus
        t[2] += minus

    print("\n### Summary by Type\n")
    print("| Type | Files | + | - | Net |")
    print("|------|-------|---|---|-----|")
    grand = [0, 0, 0]
    for typ in ("Code", "Test", "Agentic prose", "Human docs", "Configuration"):
        if typ not in totals:
            continue
        fc, p, m = totals[typ]
        print(f"| {typ} | {fc} | +{p} | -{m} | {p - m:+d} |")
        grand[0] += fc
        grand[1] += p
        grand[2] += m
    print(
        f"| **Total** | **{grand[0]}** | **+{grand[1]}** | **-{grand[2]}** | **{grand[1] - grand[2]:+d}** |"
    )


if __name__ == "__main__":
    main()
