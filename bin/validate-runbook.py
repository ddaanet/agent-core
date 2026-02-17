#!/usr/bin/env python3
"""Validate runbook files for structural and semantic correctness."""
import argparse
import importlib.util
import re
import sys
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "prepare_runbook", Path(__file__).parent / "prepare-runbook.py"
)
_mod = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]
parse_frontmatter = _mod.parse_frontmatter
extract_cycles = _mod.extract_cycles
extract_sections = _mod.extract_sections
assemble_phase_files = _mod.assemble_phase_files
extract_file_references = _mod.extract_file_references
extract_step_metadata = _mod.extract_step_metadata

ARTIFACT_PREFIXES = (
    "agent-core/skills/",
    "agent-core/fragments/",
    "agent-core/agents/",
)


def _is_artifact_path(file_path: str) -> bool:
    if any(file_path.startswith(p) for p in ARTIFACT_PREFIXES):
        return True
    return bool(re.match(r"agents/decisions/workflow-[^/]+\.md$", file_path))


def write_report(
    subcommand: str,
    path: str,
    violations: list[str],
    ambiguous: list[str] | None = None,
) -> Path:
    """Write validation report to plans/<job>/reports/validation-<subcommand>.md."""
    p = Path(path)
    job = p.parent.name if p.is_dir() else p.stem
    report_dir = Path("plans") / job / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / f"validation-{subcommand}.md"
    from datetime import datetime, timezone

    passed = not violations
    result = "PASS" if passed else "FAIL"
    date = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [
        f"# Validation Report: {subcommand}\n\n",
        f"**Runbook:** {path}\n\n",
        f"**Date:** {date}\n\n",
        f"**Result:** {result}\n\n",
        "## Summary\n\n",
        f"Failed: {len(violations)}\n\n",
    ]
    if violations:
        lines.append("## Violations\n\n")
        lines.extend(f"- {v}\n" for v in violations)
    if ambiguous:
        lines.append("\n## Ambiguous\n\n")
        lines.extend(f"- {a}\n" for a in ambiguous)
    report_path.write_text("".join(lines))
    return report_path


def check_model_tags(content: str, path: str) -> list[str]:
    """Check that artifact-type file references use opus Execution Model."""
    violations = []
    cycles = extract_cycles(content)
    for cycle in cycles:
        cycle_content = cycle["content"]
        metadata = extract_step_metadata(cycle_content)
        model = metadata.get("model", "haiku")
        file_refs = re.findall(r"- File: `?([^`\n]+)`?", cycle_content)
        for file_path in file_refs:
            file_path = file_path.strip()
            if _is_artifact_path(file_path) and model != "opus":
                violations.append(
                    f"Cycle {cycle['number']}: `{file_path}` — "
                    f"**Expected:** opus, got: {model}"
                )
    return violations


def cmd_model_tags(args: argparse.Namespace) -> None:
    """Check artifact-type files use opus Execution Model."""
    path = args.path
    p = Path(path)
    if p.is_dir():
        content = assemble_phase_files(path)
    else:
        content = p.read_text()
    violations = check_model_tags(content, path)
    write_report("model-tags", path, violations)
    sys.exit(1 if violations else 0)


def check_lifecycle(content: str, path: str) -> list[str]:
    """Check that files are created before being modified."""
    violations = []
    cycles = extract_cycles(content)
    # Map file_path -> (action_type, cycle_number) for first occurrence
    first_seen: dict[str, tuple[str, str]] = {}
    for cycle in cycles:
        cycle_content = cycle["content"]
        cycle_id = cycle["number"]
        # Extract File: / Action: pairs from Changes section
        file_action_pairs = re.findall(
            r"- File: `?([^`\n]+)`?\s*\n\s+Action: ([^\n]+)", cycle_content
        )
        for file_path, action_raw in file_action_pairs:
            file_path = file_path.strip()
            action = action_raw.strip()
            action_lower = action.lower()
            is_create = any(
                action_lower.startswith(kw) for kw in ("create", "write new")
            )
            is_modify = any(
                action_lower.startswith(kw)
                for kw in ("modify", "add", "update", "edit", "extend")
            )
            if file_path not in first_seen:
                first_seen[file_path] = (action, cycle_id)
                if is_modify:
                    violations.append(
                        f"Cycle {cycle_id}: `{file_path}` — no prior creation found"
                    )
            elif is_create:
                orig_action, orig_cycle = first_seen[file_path]
                violations.append(
                    f"Cycle {cycle_id}: `{file_path}` created again "
                    f"(first seen in Cycle {orig_cycle} as '{orig_action}')"
                )
            elif is_modify:
                orig_action, orig_cycle = first_seen[file_path]
                orig_lower = orig_action.lower()
                already_flagged = any(
                    orig_lower.startswith(kw)
                    for kw in ("modify", "add", "update", "edit", "extend")
                )
                if not any(
                    orig_lower.startswith(kw) for kw in ("create", "write new")
                ) and not already_flagged:
                    violations.append(
                        f"Cycle {cycle_id}: `{file_path}` modified before creation "
                        f"(first seen in Cycle {orig_cycle} as '{orig_action}')"
                    )
    return violations


def cmd_lifecycle(args: argparse.Namespace) -> None:
    """Check file lifecycle ordering (create before modify)."""
    path = args.path
    p = Path(path)
    if p.is_dir():
        content = assemble_phase_files(path)
    else:
        content = p.read_text()
    violations = check_lifecycle(content, path)
    write_report("lifecycle", path, violations)
    sys.exit(1 if violations else 0)


def cmd_test_counts(_args: argparse.Namespace) -> None:
    sys.exit(0)


def cmd_red_plausibility(_args: argparse.Namespace) -> None:
    sys.exit(0)


def main() -> None:
    """Entry point for validate-runbook CLI."""
    parser = argparse.ArgumentParser(prog="validate-runbook")
    sub = parser.add_subparsers(dest="subcommand")
    for name, fn in [
        ("model-tags", cmd_model_tags),
        ("lifecycle", cmd_lifecycle),
        ("test-counts", cmd_test_counts),
        ("red-plausibility", cmd_red_plausibility),
    ]:
        p = sub.add_parser(name)
        p.add_argument("path")
        p.set_defaults(func=fn)

    args = parser.parse_args()
    if args.subcommand is None:
        parser.print_usage(sys.stderr)
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
