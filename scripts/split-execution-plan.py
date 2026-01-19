#!/usr/bin/env python3
"""
Split execution plan into common context and individual step/phase files.

Supports two formats with auto-detection:
- Phase format: "## Phase N:" sections → phase{N}.md, consolidation-context.md
- Step format: "### Step N:" sections → step{N}.md, execution-context.md

Usage: python split-execution-plan.py <plan-file.md> <output-dir>
"""

import re
import sys
from pathlib import Path
from typing import Literal


def detect_format(content: str) -> Literal["phase", "step"]:
    """Auto-detect execution plan format."""
    if re.search(r'^### Step \d+:', content, re.MULTILINE):
        return "step"
    return "phase"


def extract_steps(content: str, format_type: Literal["phase", "step"]) -> dict[int, tuple[int, int]]:
    """Extract step/phase boundaries from content. Returns {num: (start_line, end_line)}."""
    lines = content.split('\n')
    steps = {}
    current_step = None
    start_line = None

    # Define pattern based on format
    if format_type == "phase":
        pattern = r'^## Phase (\d+):'
    else:
        pattern = r'^### Step (\d+):'

    for i, line in enumerate(lines):
        match = re.match(pattern, line)
        if match:
            # Save previous step boundary
            if current_step is not None:
                steps[current_step] = (start_line, i - 1)

            current_step = int(match.group(1))
            start_line = i

    # Save last step
    if current_step is not None:
        # Find end of last step
        end_markers = [
            '## Critical Files',
            '## Open Questions',
            '## Success Criteria',
            '## Execution Notes',
            '## Dependencies for Execution',
            '## Technical Decisions Summary',
            '## Open Questions for Review',
            '## Next Steps'
        ]
        end_line = len(lines) - 1
        for i in range(start_line, len(lines)):
            if any(lines[i].startswith(marker) for marker in end_markers):
                end_line = i - 1
                break
        steps[current_step] = (start_line, end_line)

    return steps


def extract_common_context(content: str, steps: dict[int, tuple[int, int]], format_type: Literal["phase", "step"]) -> str:
    """Extract common context (everything except individual steps/phases)."""
    lines = content.split('\n')

    # Find first step start
    first_step_start = min(start for start, _ in steps.values())

    # Header and overview (before first step)
    header_section = '\n'.join(lines[:first_step_start])

    # Everything after last step
    last_step_end = max(end for _, end in steps.values())
    footer_section = '\n'.join(lines[last_step_end + 1:])

    context = f"""{header_section}

---

## Common Context

This file contains shared context for all execution {"steps" if format_type == "step" else "phases"}.
Each {"step" if format_type == "step" else "phase"} file references this context and should be executed with both files in context.

---

{footer_section}
"""

    return context


def extract_step_content(content: str, step_num: int, start: int, end: int, format_type: Literal["phase", "step"]) -> str:
    """Extract content for a specific step/phase."""
    lines = content.split('\n')
    step_lines = lines[start:end + 1]

    context_file = "execution-context.md" if format_type == "step" else "consolidation-context.md"
    title_prefix = "Step" if format_type == "step" else "Consolidation: Phase"

    step_content = f"""# {title_prefix} {step_num}

**Context**: Read `{context_file}` for full context before executing this {"step" if format_type == "step" else "phase"}.

---

{chr(10).join(step_lines)}

---

**Execution Instructions**:
1. Read {context_file} for prerequisites, critical files, and execution notes
2. Execute this {"step" if format_type == "step" else "phase"} following the actions listed above
3. Perform validation checks as specified
4. Document results in execution report
5. Stop on any unexpected results per communication rules
"""

    return step_content


def main():
    if len(sys.argv) != 3:
        print("Usage: python split-execution-plan.py <plan-file.md> <output-dir>")
        sys.exit(1)

    plan_file = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])

    if not plan_file.exists():
        print(f"Error: {plan_file} does not exist")
        sys.exit(1)

    # Read and detect format
    content = plan_file.read_text()
    format_type = detect_format(content)
    print(f"Detected format: {format_type.upper()}")

    # Extract step boundaries
    steps = extract_steps(content, format_type)
    print(f"Found {len(steps)} {'steps' if format_type == 'step' else 'phases'}")

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Extract and write common context
    context = extract_common_context(content, steps, format_type)
    context_filename = "execution-context.md" if format_type == "step" else "consolidation-context.md"
    context_file = output_dir / context_filename
    context_file.write_text(context)
    print(f"Wrote common context to {context_file}")

    # Extract and write individual steps/phases
    file_prefix = "step" if format_type == "step" else "phase"
    for step_num in sorted(steps.keys()):
        start, end = steps[step_num]
        step_content = extract_step_content(content, step_num, start, end, format_type)
        step_file = output_dir / f"{file_prefix}{step_num}.md"
        step_file.write_text(step_content)
        print(f"Wrote {file_prefix} {step_num} to {step_file}")

    # Create index file
    label = "Steps" if format_type == "step" else "Phases"
    plan_label = "Step" if format_type == "step" else "Phase"

    index_content = f"""# Execution Plan - Split Files

**Generated from**: {plan_file.name}
**{plan_label} count**: {len(steps)}
**Format**: {format_type.upper()}

## Files

- **{context_filename}** - Common context for all {label.lower()} (prerequisites, critical files, execution notes, success criteria)

### {label}
"""

    for step_num in sorted(steps.keys()):
        index_content += f"- **{file_prefix}{step_num}.md** - {plan_label} {step_num} execution instructions\n"

    index_content += f"""
## Usage

For each {plan_label.lower()} execution:
1. Provide both `{context_filename}` and `{file_prefix}{{N}}.md` to the executor
2. Executor reads context first, then executes {plan_label.lower()}
3. Executor writes results to execution report
4. Review before proceeding to next {plan_label.lower()}

## Orchestration Pattern

```
Executor:
  Input: {context_filename} + {file_prefix}{{N}}.md
  Output: Terse return ("done: <summary>" or "blocked: <reason>")
  Reports: Written to execution report file

Review Agent (if needed):
  Input: context + execution report
  Output: Review findings
```
"""

    index_file = output_dir / "README.md"
    index_file.write_text(index_content)
    print(f"Wrote index to {index_file}")

    print(f"\nSuccess! Split {len(steps)} {label.lower()} into {output_dir}")


if __name__ == "__main__":
    main()
