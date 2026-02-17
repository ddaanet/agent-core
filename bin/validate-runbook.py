#!/usr/bin/env python3
"""Validate runbook files for structural and semantic correctness."""
import argparse
import importlib.util
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
    lines = [f"# Validation: {subcommand}\n\n"]
    if violations:
        lines.append("## Violations\n\n")
        lines.extend(f"- {v}\n" for v in violations)
    else:
        lines.append("All checks passed.\n")
    if ambiguous:
        lines.append("\n## Ambiguous\n\n")
        lines.extend(f"- {a}\n" for a in ambiguous)
    report_path.write_text("".join(lines))
    return report_path


def cmd_model_tags(_args: argparse.Namespace) -> None:
    """Stub: check artifact-type files use opus Execution Model."""
    sys.exit(0)


def cmd_lifecycle(_args: argparse.Namespace) -> None:
    """Stub: check create→modify file dependency ordering."""
    sys.exit(0)


def cmd_test_counts(_args: argparse.Namespace) -> None:
    """Stub: check checkpoint claims vs actual test function count."""
    sys.exit(0)


def cmd_red_plausibility(_args: argparse.Namespace) -> None:
    """Stub: check RED expectations vs prior GREEN state."""
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
