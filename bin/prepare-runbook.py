#!/usr/bin/env python3
"""Prepare execution artifacts from runbook markdown files.

Transforms a runbook markdown file (or phase-grouped directory) into:
1. Per-phase agents (.claude/agents/crew-<runbook-name>[-p<N>].md)
2. Step/Cycle files (plans/<runbook-name>/steps/)
3. Orchestrator plan (plans/<runbook-name>/orchestrator-plan.md)

Supports:
- General runbooks (## Step N:)
- TDD runbooks (## Cycle X.Y:, requires type: tdd in frontmatter)
- Phase-grouped runbooks (runbook-phase-*.md files in a directory)

Usage:
    prepare-runbook.py <runbook-file.md>
    prepare-runbook.py <directory-with-phase-files>

Example (File):
    prepare-runbook.py plans/foo/runbook.md
    # Creates:
    #   .claude/agents/crew-foo.md (uses artisan.md baseline)
    #   plans/foo/steps/step-*.md
    #   plans/foo/orchestrator-plan.md

Example (Phase Directory):
    prepare-runbook.py plans/foo/
    # Detects runbook-phase-*.md files, assembles them, then creates same artifacts

Example (TDD):
    prepare-runbook.py plans/tdd-test/runbook.md
    # Creates:
    #   .claude/agents/crew-tdd-test.md (uses test-driver.md baseline)
    #   plans/tdd-test/steps/cycle-*.md
    #   plans/tdd-test/orchestrator-plan.md
"""

import re
import subprocess
import sys
from pathlib import Path

# Standard TDD stop/error conditions injected into Common Context
# when phase files don't include them. Satisfies validate_cycle_structure
# which checks for 'stop condition' or 'error condition' in content or common context.
DEFAULT_TDD_COMMON_CONTEXT = """## Common Context

**TDD Protocol:**
Strict RED-GREEN-REFACTOR: 1) RED: Write failing test, 2) Verify RED, 3) GREEN: Minimal implementation, 4) Verify GREEN, 5) Verify Regression, 6) REFACTOR (optional)

**Stop/Error Conditions (all cycles):**
STOP IMMEDIATELY if: RED phase test passes (expected failure) • RED phase failure message doesn't match expected • GREEN phase tests don't pass after implementation • Any existing tests break (regression)

Actions when stopped: 1) Document in reports/cycle-{X}-{Y}-notes.md 2) Test passes unexpectedly → Investigate if feature exists 3) Regression → STOP, report broken tests 4) Scope unclear → STOP, document ambiguity

**Conventions:**
- Use Read/Write/Edit/Grep tools (not Bash for file ops)
- Report errors explicitly (never suppress)
"""


def parse_frontmatter(content):
    """Extract YAML frontmatter from markdown content.

    Returns: (metadata_dict, remaining_content)

    Metadata includes:
    - type: 'tdd' or 'general' (default: 'general')
    - model: execution model (default: 'haiku')
    - name: runbook name
    """
    if not content.startswith("---"):
        return {}, content

    try:
        end_idx = content.index("---", 3)
    except ValueError:
        return {}, content

    meta_str = content[3:end_idx].strip()
    remaining = content[end_idx + 3 :].lstrip()

    metadata = {}
    for line in meta_str.split("\n"):
        if ":" in line:
            key, _, value = line.partition(":")
            metadata[key.strip()] = value.strip().strip('"').strip("'")

    # Set default runbook type
    if "type" not in metadata:
        metadata["type"] = "general"
    else:
        # Validate type field
        valid_types = ["tdd", "general", "mixed", "inline"]
        if metadata["type"] not in valid_types:
            print(
                f"WARNING: Unknown runbook type '{metadata['type']}', defaulting to 'general'",
                file=sys.stderr,
            )
            metadata["type"] = "general"

    return metadata, remaining


def extract_cycles(content):
    """Extract cycles from TDD runbook.

    Returns: List of cycle dictionaries with keys:
        - major: int (major cycle number)
        - minor: int (minor cycle number)
        - number: str (full cycle number "X.Y")
        - title: str (cycle name)
        - content: str (full cycle markdown content)
    """
    cycle_pattern = r"^###? Cycle\s+(\d+)\.(\d+):\s*(.*)"
    lines = content.split("\n")
    tracker = _fence_tracker()

    cycles = []
    current_cycle = None
    current_content = []

    for _i, line in enumerate(lines):
        # Update fence state before processing the line
        in_fence = tracker(line)

        # Check for cycle header (only if not inside a fence)
        match = re.match(cycle_pattern, line) if not in_fence else None
        if match:
            # Save previous cycle
            if current_cycle is not None:
                current_cycle["content"] = "\n".join(current_content).strip()
                cycles.append(current_cycle)

            # Start new cycle
            major = int(match.group(1))
            minor = int(match.group(2))
            title = match.group(3).strip()

            current_cycle = {
                "major": major,
                "minor": minor,
                "number": f"{major}.{minor}",
                "title": title,
            }
            current_content = [line]

        # Check for next H2 (non-cycle section) - terminates current cycle
        # Only H2 headers terminate cycles (H3 like ### RED Phase are cycle content)
        # Skip H2 check if inside a fence (so fenced headers don't terminate cycles)
        elif line.startswith("## ") and current_cycle is not None and not in_fence:
            # End current cycle - H2 header that's not a cycle terminates the current cycle
            current_cycle["content"] = "\n".join(current_content).strip()
            cycles.append(current_cycle)
            current_cycle = None
            current_content = []

        # Accumulate content
        elif current_cycle is not None:
            current_content.append(line)

    # Save final cycle
    if current_cycle is not None:
        current_cycle["content"] = "\n".join(current_content).strip()
        cycles.append(current_cycle)

    return cycles


def validate_cycle_structure(cycle, common_context=""):
    """Validate that cycle contains mandatory TDD sections.

    Args:
        cycle: Cycle dictionary with 'number', 'content', 'title', 'major' keys
        common_context: Content from Common Context section (for inherited sections)

    Returns: List of error/warning messages (empty if valid)
    """
    content = cycle["content"].lower()
    cycle_num = cycle["number"]
    title = cycle.get("title", "")
    messages = []

    # Detect cycle type from conventions
    is_spike = cycle["major"] == 0
    is_regression = "[regression]" in title.lower()

    # Spike cycles (0.x): no RED/GREEN required
    if is_spike:
        pass  # Skip RED/GREEN validation for exploratory cycles
    # Regression cycles: GREEN only, no RED expected
    elif is_regression:
        if "green" not in content:
            messages.append(
                f"ERROR: Cycle {cycle_num} missing required section: GREEN phase"
            )
    # Standard cycles: both RED and GREEN required
    else:
        if "red" not in content:
            messages.append(
                f"ERROR: Cycle {cycle_num} missing required section: RED phase"
            )
        if "green" not in content:
            messages.append(
                f"ERROR: Cycle {cycle_num} missing required section: GREEN phase"
            )

    # Check for mandatory Stop/Error Conditions (can be in cycle OR Common Context)
    # Accept either "stop condition" or "error condition" as valid
    common_lower = common_context.lower()
    has_conditions = (
        "stop condition" in content
        or "stop condition" in common_lower
        or "error condition" in content
        or "error condition" in common_lower
    )
    if not has_conditions:
        messages.append(
            f"ERROR: Cycle {cycle_num} missing required section: Stop/Error Conditions"
        )

    # Warn if missing dependencies (can be in cycle OR Common Context, non-critical)
    if (
        "dependencies" not in content
        and "dependency" not in content
        and "dependencies" not in common_lower
        and "dependency" not in common_lower
    ):
        messages.append(f"WARNING: Cycle {cycle_num} missing dependencies section")

    return messages


def validate_cycle_numbering(cycles):
    """Validate cycle numbering.

    Errors (fatal): no cycles, duplicates, bad start number.
    Warnings (non-fatal): gaps in numbering (document order
    defines execution sequence, not numbers).

    Returns: (errors, warnings) tuple of string lists.
    """
    if not cycles:
        return (["ERROR: No cycles found in TDD runbook"], [])

    errors = []
    warnings = []

    # Check for duplicates (fatal - ambiguous identity)
    seen = set()
    for cycle in cycles:
        cycle_id = cycle["number"]
        if cycle_id in seen:
            errors.append(f"ERROR: Duplicate cycle number: {cycle_id}")
        seen.add(cycle_id)

    # Check major numbers (info only - mixed runbooks may start cycles at any phase)
    major_nums = sorted({c["major"] for c in cycles})

    # Check major number gaps (warn only - document order is authoritative)
    for i in range(len(major_nums) - 1):
        if major_nums[i + 1] != major_nums[i] + 1:
            warnings.append(
                f"WARNING: Gap in major cycle numbers: {major_nums[i]} -> {major_nums[i + 1]}"
            )

    # Check minor numbers within each major
    by_major = {}
    for cycle in cycles:
        major = cycle["major"]
        if major not in by_major:
            by_major[major] = []
        by_major[major].append(cycle["minor"])

    for major, minors in by_major.items():
        sorted_minors = sorted(minors)
        # Minor must start at 1 (fatal - convention)
        if sorted_minors[0] != 1:
            errors.append(
                f"ERROR: Cycle {major}.x must start at {major}.1, found {major}.{sorted_minors[0]}"
            )

        # Minor gaps (warn only - same rationale as major gaps)
        for i in range(len(sorted_minors) - 1):
            if sorted_minors[i + 1] != sorted_minors[i] + 1:
                warnings.append(
                    f"WARNING: Gap in cycle {major}.x: {major}.{sorted_minors[i]} -> {major}.{sorted_minors[i + 1]}"
                )

    return (errors, warnings)


def validate_phase_numbering(step_phases):
    """Validate phase numbering for general runbooks.

    Errors (fatal): non-monotonic phases (decreasing).
    Warnings (non-fatal): gaps in phase numbers.

    Args:
        step_phases: dict mapping step_num -> phase_number

    Returns: (errors, warnings) tuple of string lists.
    """
    if not step_phases:
        return ([], [])

    errors = []
    warnings = []

    phase_nums = sorted(set(step_phases.values()))

    # Check for gaps (warn only)
    for i in range(len(phase_nums) - 1):
        if phase_nums[i + 1] != phase_nums[i] + 1:
            warnings.append(
                f"WARNING: Gap in phase numbers: {phase_nums[i]} -> {phase_nums[i + 1]}"
            )

    # Check for non-monotonic (error - phases should increase)
    prev_phase = None
    for step_num in sorted(
        step_phases.keys(), key=lambda x: tuple(map(int, x.split(".")))
    ):
        phase = step_phases[step_num]
        if prev_phase is not None and phase < prev_phase:
            errors.append(
                f"ERROR: Phase numbers must not decrease: Step {step_num} has phase {phase} after phase {prev_phase}"
            )
        prev_phase = phase

    return (errors, warnings)


def _fence_tracker():
    """Track fence state line-by-line with CommonMark semantics.

    Supports both backtick and tilde fences:
    - Opening fence requires ≥3 of same character (backtick or tilde)
    - Closing fence requires ≥ opening count of SAME character type
    - No info string allowed on closing fence

    Returns a callable that:
    - Takes a line (str) as argument
    - Returns True if inside a fence after processing this line
    - Uses closure with nonlocal state

    Fence tracking rules:
    - Opening fence: ≥3 backticks OR ≥3 tildes, optional info string
    - Closing fence: ≥ opening count of SAME character, no info string
    - Backtick and tilde fences do NOT cross-close
    """
    in_fence = False
    open_count = 0
    fence_char = None  # Track 'backtick' or 'tilde'

    def tracker(line):
        nonlocal in_fence, open_count, fence_char
        stripped = line.lstrip()

        if in_fence:
            # Check for closing fence: must match the opening fence character
            if fence_char == "backtick" and stripped.startswith("`"):
                # Count backticks at start of line
                backtick_count = 0
                for char in stripped:
                    if char == "`":
                        backtick_count += 1
                    else:
                        break

                # Check if this is a valid closing fence
                # Must have >= opening count and only spaces/tabs after backticks
                remainder = stripped[backtick_count:]
                if backtick_count >= open_count and all(c in " \t" for c in remainder):
                    in_fence = False
                    open_count = 0
                    fence_char = None
            elif fence_char == "tilde" and stripped.startswith("~"):
                # Count tildes at start of line
                tilde_count = 0
                for char in stripped:
                    if char == "~":
                        tilde_count += 1
                    else:
                        break

                # Check if this is a valid closing fence
                # Must have >= opening count and only spaces/tabs after tildes
                remainder = stripped[tilde_count:]
                if tilde_count >= open_count and all(c in " \t" for c in remainder):
                    in_fence = False
                    open_count = 0
                    fence_char = None
        # Check for opening fence: must start with >=3 backticks
        elif stripped.startswith("```"):
            backtick_count = 0
            for char in stripped:
                if char == "`":
                    backtick_count += 1
                else:
                    break

            if backtick_count >= 3:
                in_fence = True
                open_count = backtick_count
                fence_char = "backtick"
        # Check for opening fence: must start with >=3 tildes
        elif stripped.startswith("~~~"):
            tilde_count = 0
            for char in stripped:
                if char == "~":
                    tilde_count += 1
                else:
                    break

            if tilde_count >= 3:
                in_fence = True
                open_count = tilde_count
                fence_char = "tilde"

        return in_fence

    return tracker


def strip_fenced_blocks(content):
    """Replace fenced block content with empty lines, preserving line count.

    Args:
        content: String content with potential fenced code blocks

    Returns:
        String with fenced block content replaced by empty lines.
        Fence delimiter lines themselves are preserved.
        Line count is unchanged.

    Rationale: Position-dependent logic elsewhere depends on stable line numbers.
    """
    content.splitlines(keepends=True)
    tracker = _fence_tracker()
    result = []

    for line in content.splitlines():
        in_fence = tracker(line)
        if in_fence and not (
            line.lstrip().startswith("```") or line.lstrip().startswith("~~~")
        ):
            result.append("\n")
        else:
            result.append(line + "\n" if not line.endswith("\n") else line)

    # Remove trailing newline if original didn't have one
    result_str = "".join(result)
    if not content.endswith("\n"):
        result_str = result_str.rstrip("\n")

    return result_str


def extract_sections(content):
    """Extract Common Context, Steps, Inline Phases, and Orchestrator sections.

    Returns: {
        'common_context': (section_content or None),
        'steps': {step_num: step_content, ...},
        'step_phases': {step_num: phase_number, ...},
        'inline_phases': {phase_number: phase_content, ...},
        'orchestrator': section_content or None
    }
    """
    sections = {
        "common_context": None,
        "steps": {},
        "step_phases": {},
        "inline_phases": {},
        "orchestrator": None,
    }

    lines = content.split("\n")

    # First pass: Build a map of line numbers to phases and detect inline phases
    line_to_phase = {}
    current_phase = 1  # Default phase for flat runbooks
    phase_pattern = r"^###? Phase\s+(\d+)"
    inline_phase_pattern = r"^###? Phase\s+(\d+):.*\(type:\s*inline[^)]*\)"
    inline_phase_nums = set()
    tracker = _fence_tracker()

    for i, line in enumerate(lines):
        in_fence = tracker(line)
        phase_match = re.match(phase_pattern, line) if not in_fence else None
        if phase_match:
            current_phase = int(phase_match.group(1))
            if re.match(inline_phase_pattern, line):
                inline_phase_nums.add(current_phase)
        line_to_phase[i] = current_phase

    # Extract inline phase content (text between phase header and next phase/H2)
    if inline_phase_nums:
        in_inline = False
        inline_num = None
        inline_content = []
        tracker = _fence_tracker()
        for i, line in enumerate(lines):
            in_fence = tracker(line)
            phase_match = re.match(phase_pattern, line) if not in_fence else None
            if phase_match:
                # Save previous inline phase
                if in_inline and inline_content:
                    sections["inline_phases"][inline_num] = "\n".join(
                        inline_content
                    ).strip()
                phase_num = int(phase_match.group(1))
                if phase_num in inline_phase_nums:
                    in_inline = True
                    inline_num = phase_num
                    inline_content = [line]
                else:
                    in_inline = False
                    inline_content = []
            elif line.startswith("## ") and in_inline and not in_fence:
                # H2 terminates inline phase collection
                sections["inline_phases"][inline_num] = "\n".join(
                    inline_content
                ).strip()
                in_inline = False
                inline_content = []
            elif in_inline:
                inline_content.append(line)
        # Save final inline phase
        if in_inline and inline_content:
            sections["inline_phases"][inline_num] = "\n".join(inline_content).strip()

    # Second pass: Extract sections with phase information
    current_section = None
    current_content = []
    current_step = None
    current_step_line = None
    step_pattern = r"^## Step\s+([\d.]+):\s*(.*)"
    tracker = _fence_tracker()

    def save_current() -> None:
        if current_section and current_content:
            content_str = "\n".join(current_content).strip()
            if current_section == "common_context":
                sections["common_context"] = content_str
            elif current_section == "orchestrator":
                sections["orchestrator"] = content_str
            elif current_section == "step":
                sections["steps"][current_step] = content_str
                sections["step_phases"][current_step] = line_to_phase[current_step_line]

    for i, line in enumerate(lines):
        in_fence = tracker(line)

        # Phase headers are section boundaries (only when not inside a fence)
        if re.match(phase_pattern, line) and not in_fence:
            save_current()
            current_section = None
            current_content = []
            continue

        if line.startswith("## ") and not in_fence:
            save_current()

            # Detect new section
            if line == "## Common Context":
                current_section = "common_context"
                current_content = [line]
            elif line.startswith("## Step "):
                match = re.match(step_pattern, line)
                if match:
                    step_num = match.group(1)
                    if step_num in sections["steps"]:
                        print(
                            f"ERROR: Duplicate step number: {step_num}", file=sys.stderr
                        )
                        return None
                    current_section = "step"
                    current_step = step_num
                    current_step_line = i
                    current_content = [line]
                else:
                    current_section = None
                    current_content = []
            elif line == "## Orchestrator Instructions":
                current_section = "orchestrator"
                current_content = [line]
            else:
                current_section = None
                current_content = []
        elif current_section:
            current_content.append(line)

    save_current()
    return sections


def extract_phase_models(content):
    """Return {phase_num: model} for phases that have a model: annotation."""
    stripped_content = strip_fenced_blocks(content)
    pattern = re.compile(
        r"^###?\s+Phase\s+(\d+):.*model:\s*(\w+)",
        re.IGNORECASE | re.MULTILINE,
    )
    return {
        int(m.group(1)): m.group(2).lower() for m in pattern.finditer(stripped_content)
    }


def extract_phase_preambles(content):
    """Return {phase_num: preamble_text} for all phases in content.

    Preamble is text between a phase header and the first step/cycle header (or
    next phase header). Phases with no content between header and first
    step/cycle get an empty string.
    """
    phase_header = re.compile(r"^###?\s+Phase\s+(\d+):", re.IGNORECASE | re.MULTILINE)
    step_or_cycle = re.compile(r"^##\s+(Step|Cycle)\s+", re.IGNORECASE | re.MULTILINE)

    preambles = {}
    current_phase = None
    preamble_lines = []
    collecting = False
    tracker = _fence_tracker()

    for line in content.splitlines():
        in_fence = tracker(line)
        ph_match = phase_header.match(line)
        sc_match = step_or_cycle.match(line)

        if ph_match:
            if current_phase is not None and current_phase not in preambles:
                preambles[current_phase] = "\n".join(preamble_lines).strip()
            current_phase = int(ph_match.group(1))
            preamble_lines = []
            collecting = True
        elif sc_match and collecting and not in_fence:
            collecting = False
            preambles[current_phase] = "\n".join(preamble_lines).strip()
            preamble_lines = []
        elif collecting:
            preamble_lines.append(line)

    if current_phase is not None and current_phase not in preambles:
        preambles[current_phase] = "\n".join(preamble_lines).strip()

    return preambles


def get_phase_baseline_type(phase_content) -> str:
    """Determine baseline type for a phase by inspecting its content structure.

    Returns "tdd" if the content contains Cycle headers (indicating TDD
    workflow), "general" otherwise.
    """
    stripped = strip_fenced_blocks(phase_content)
    if re.search(r"^##\s+Cycle\s+\d+\.\d+:", stripped, re.MULTILINE):
        return "tdd"
    return "general"


def detect_phase_types(content) -> dict:
    """Return {phase_num: type_str} for all phases in content.

    Classifies each phase as "tdd", "general", or "inline":
    - "inline" if the phase header contains `(type: inline)`
    - Otherwise delegates to get_phase_baseline_type() on the phase's content
    """
    stripped = strip_fenced_blocks(content)
    phase_header_re = re.compile(r"^###?\s+Phase\s+(\d+):", re.MULTILINE)
    inline_re = re.compile(r"\(type:\s*inline[^)]*\)", re.IGNORECASE)

    # Find all phase header positions and numbers
    matches = list(phase_header_re.finditer(stripped))
    if not matches:
        return {}

    result = {}
    for i, m in enumerate(matches):
        phase_num = int(m.group(1))
        header_line = (
            stripped[m.start() : stripped.index("\n", m.start())]
            if "\n" in stripped[m.start() :]
            else stripped[m.start() :]
        )
        if inline_re.search(header_line):
            result[phase_num] = "inline"
        else:
            # Extract content from after the header to the next phase header (or end)
            content_start = m.end()
            content_end = (
                matches[i + 1].start() if i + 1 < len(matches) else len(stripped)
            )
            phase_content = stripped[content_start:content_end]
            result[phase_num] = get_phase_baseline_type(phase_content)

    return result


def assemble_phase_files(directory):
    """Assemble runbook from phase files in a directory.

    Detects runbook-phase-*.md files, sorts by phase number,
    and concatenates into assembled content. Prepends TDD frontmatter
    since phase files contain only content.

    Args:
        directory: Path to directory containing runbook-phase-*.md files

    Returns:
        (assembled_content_with_frontmatter, phase_dir) or (None, None) if no phase files found
    """
    dir_path = Path(directory)
    if not dir_path.is_dir():
        return None, None

    # Find all phase files: runbook-phase-*.md
    phase_files = sorted(dir_path.glob("runbook-phase-*.md"))
    if not phase_files:
        return None, None

    # Extract phase numbers for sorting
    def get_phase_num(path):
        match = re.search(r"runbook-phase-(\d+)\.md", path.name)
        return int(match.group(1)) if match else float("inf")

    phase_files = sorted(phase_files, key=get_phase_num)

    # Validate sequential phase numbering (accept 0-based or 1-based)
    phase_nums = [get_phase_num(f) for f in phase_files]
    start_num = phase_nums[0] if phase_nums else 0
    expected_nums = list(range(start_num, start_num + len(phase_nums)))
    if phase_nums != expected_nums:
        missing = set(expected_nums) - set(phase_nums)
        print(
            f"ERROR: Phase numbering gaps detected. Expected {expected_nums}, got {phase_nums}. Missing: {sorted(missing)}",
            file=sys.stderr,
        )
        return None, None

    # Read and validate each phase file
    # Detect runbook type from first phase file (Step = general, Cycle = TDD)
    assembled_parts = []
    is_tdd = False

    for i, phase_file in enumerate(phase_files):
        content = phase_file.read_text()
        if not content.strip():
            print(f"ERROR: Empty phase file: {phase_file}", file=sys.stderr)
            return None, None

        # Detect runbook type from first file
        if i == 0:
            stripped_content = strip_fenced_blocks(content)
            has_cycles = bool(
                re.search(r"^##+ Cycle\s+\d+\.\d+:", stripped_content, re.MULTILINE)
            )
            has_steps = bool(
                re.search(r"^##+ Step\s+\d+\.\d+:", stripped_content, re.MULTILINE)
            )
            if has_cycles:
                is_tdd = True
            elif not has_steps:
                print(
                    f"ERROR: Phase file missing Step or Cycle headers: {phase_file}",
                    file=sys.stderr,
                )
                return None, None

        phase_num = phase_nums[i]
        if re.search(rf"^###? Phase\s+{phase_num}:", content, re.MULTILINE):
            assembled_parts.append(f"\n{content}")
        else:
            assembled_parts.append(f"\n### Phase {phase_num}:\n\n{content}")

    # Derive runbook name from directory (plans/foo -> foo)
    runbook_name = dir_path.name

    assembled_body = "\n".join(assembled_parts)

    # Prepend appropriate frontmatter (phase files have no frontmatter)
    if is_tdd:
        phase_models = extract_phase_models(assembled_body)
        detected_model = phase_models[min(phase_models)] if phase_models else None
        model_line = f"model: {detected_model}\n" if detected_model else ""
        frontmatter = f"---\ntype: tdd\n{model_line}name: {runbook_name}\n---\n"
    else:
        frontmatter = ""  # General runbooks derive frontmatter from assembled content

    # Inject default Common Context for TDD runbooks assembled from phase files
    # when phases don't include one. Provides standard stop/error conditions
    # that validate_cycle_structure requires.
    if is_tdd and "## Common Context" not in assembled_body:
        assembled_body = DEFAULT_TDD_COMMON_CONTEXT + "\n" + assembled_body

    assembled_content = frontmatter + assembled_body

    return assembled_content, str(dir_path)


def derive_paths(runbook_path):
    """Derive output paths from runbook location and name.

    Input: plans/foo/runbook.md
    Returns:
        runbook_name: 'foo' (parent directory)
        agents_dir: .claude/agents/ (directory for per-phase agent files)
        steps_dir: plans/foo/steps/
        orchestrator_path: plans/foo/orchestrator-plan.md
    """
    path = Path(runbook_path)
    runbook_name = path.parent.name

    agents_dir = Path(".claude/agents")
    steps_dir = path.parent / "steps"
    orchestrator_path = path.parent / "orchestrator-plan.md"

    return runbook_name, agents_dir, steps_dir, orchestrator_path


def read_baseline_agent(runbook_type="general"):
    """Read baseline agent template based on runbook type.

    Args:
        runbook_type: 'tdd' or 'general' (caller maps 'mixed' to 'general')

    Returns:
        Baseline agent body (without frontmatter)
    """
    if runbook_type == "tdd":
        baseline_path = Path("agent-core/agents/test-driver.md")
    else:
        baseline_path = Path("agent-core/agents/artisan.md")

    if not baseline_path.exists():
        print(f"ERROR: Baseline agent not found: {baseline_path}", file=sys.stderr)
        sys.exit(1)

    content = baseline_path.read_text()
    _, body = parse_frontmatter(content)
    return body


def generate_agent_frontmatter(
    runbook_name, model=None, phase_num=1, total_phases=1
) -> str:
    """Generate frontmatter for plan-specific agent."""
    model_line = f"model: {model}\n" if model is not None else ""
    if total_phases > 1:
        name = f"crew-{runbook_name}-p{phase_num}"
        description = f"Execute phase {phase_num} of {runbook_name}"
    else:
        name = f"crew-{runbook_name}"
        description = f"Execute {runbook_name}"
    return f'---\nname: {name}\ndescription: {description}\n{model_line}color: cyan\ntools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob"]\n---\n'


def generate_phase_agent(
    runbook_name,
    phase_num,
    phase_type,
    plan_context="",
    phase_context="",
    model=None,
    total_phases=1,
) -> str:
    """Compose a phase-scoped agent from 5 ordered layers."""
    result = generate_agent_frontmatter(runbook_name, model, phase_num, total_phases)
    result += read_baseline_agent(phase_type)
    if plan_context:
        result += "\n---\n# Runbook-Specific Context\n\n" + plan_context
    if phase_context:
        result += "\n---\n# Phase Context\n\n" + phase_context
    result += "\n\n---\n\n**Clean tree requirement:** Commit all changes before reporting success. The orchestrator will reject dirty trees — there are no exceptions.\n"
    return result


def extract_step_metadata(content, default_model=None):
    """Extract execution metadata from step/cycle content.

    Looks for bold-label fields like **Execution Model**: Sonnet
    in the step body content. Extracted model is normalized to
    lowercase and validated against known models.

    Returns: dict with extracted metadata (model, report_path)
    """
    valid_models = {"haiku", "sonnet", "opus"}
    metadata = {}

    # Extract Execution Model (case-insensitive)
    model_match = re.search(r"\*\*Execution Model\*\*:\s*(\w+)", content, re.IGNORECASE)
    if model_match:
        model_val = model_match.group(1).strip().lower()
        if model_val in valid_models:
            metadata["model"] = model_val
        else:
            print(
                f"WARNING: Invalid execution model '{model_val}', using default '{default_model}'",
                file=sys.stderr,
            )
            metadata["model"] = default_model
    else:
        metadata["model"] = default_model

    # Extract Report Path (may have backtick wrapping)
    report_match = re.search(r"\*\*Report Path\*\*:\s*`?([^`\n]+)`?", content)
    if report_match:
        metadata["report_path"] = report_match.group(1).strip()

    return metadata


def extract_file_references(content):
    """Extract file path references from step/cycle content.

    Finds backtick-wrapped paths that look like project files.
    Excludes paths inside fenced code blocks (``` ... ```).

    Returns: set of file path strings
    """
    # Strip fenced code blocks to avoid matching paths inside them
    stripped = strip_fenced_blocks(content)

    # Match backtick-wrapped paths containing at least one / (directory separator)
    # and ending with a known file extension. Requires / to avoid matching
    # method names like `utils.json` or `config.py`.
    file_exts = r"\.(?:py|md|json|sh|txt|toml|yml|yaml|cfg|ini|js|ts|tsx)"
    matches = re.findall(
        rf"`([a-zA-Z][a-zA-Z0-9_.\-]*/[a-zA-Z0-9_/.\-]*{file_exts})`", stripped
    )
    return set(matches)


def validate_file_references(sections, cycles=None, runbook_path=""):
    """Validate that file references in steps point to existing files.

    Extracts backtick-wrapped file paths from step content and checks
    existence. Skips paths that are expected to be created during
    execution (report paths, paths under plans/*/reports/).

    Returns: list of warning strings (empty if all valid)
    """
    warnings = []

    # Collect all step contents with identifiers
    step_items = []
    if cycles:
        for cycle in cycles:
            step_items.append((f"Cycle {cycle['number']}", cycle["content"]))
    if sections.get("steps"):
        for step_num, content in sections["steps"].items():
            step_items.append((f"Step {step_num}", content))

    # Also check common context
    if sections.get("common_context"):
        step_items.append(("Common Context", sections["common_context"]))

    # Paths to exclude from validation
    runbook_str = str(runbook_path)

    for step_id, content in step_items:
        refs = extract_file_references(content)
        meta = extract_step_metadata(content)
        report_path = meta.get("report_path", "")

        for ref in sorted(refs):
            # Skip the runbook itself (Plan reference)
            if ref == runbook_str:
                continue

            # Skip report paths (created during execution)
            if ref == report_path:
                continue

            # Skip paths under plans/*/reports/ (always created)
            if re.match(r"plans/[^/]+/reports/", ref):
                continue

            # Skip paths preceded by creation-verb context
            create_pattern = r"(?:Create|Write|mkdir)[^`]*`" + re.escape(ref) + r"`"
            if re.search(create_pattern, content, re.IGNORECASE):
                continue

            # Check existence
            if not Path(ref).exists():
                warnings.append(
                    f"WARNING: {step_id} references non-existent file: {ref}"
                )

    return warnings


def generate_step_file(
    step_num, step_content, runbook_path, default_model=None, phase=1, phase_context=""
):
    """Generate step file with references and execution metadata header.

    Args:
        step_num: Step number (e.g., "1.1")
        step_content: Step body content
        runbook_path: Path to runbook file
        default_model: Default model if not specified in content
        phase: Phase number for this step
        phase_context: Optional preamble text for the phase (injected as ## Phase Context)

    Returns:
        Formatted step file content with phase in frontmatter
    """
    meta = extract_step_metadata(step_content, default_model)

    header_lines = [
        f"# Step {step_num}",
        "",
        f"**Plan**: `{runbook_path}`",
        f"**Execution Model**: {meta['model']}",
        f"**Phase**: {phase}",
    ]
    if "report_path" in meta:
        header_lines.append(f"**Report Path**: `{meta['report_path']}`")

    header_lines.append("")
    header_lines.append("---")
    if phase_context and phase_context.strip():
        header_lines.extend(
            ["", "## Phase Context", "", phase_context.strip(), "", "---"]
        )
    header_lines.extend(["", step_content, ""])
    return "\n".join(header_lines)


def generate_cycle_file(cycle, runbook_path, default_model=None, phase_context=""):
    """Generate cycle file with references and execution metadata header.

    Args:
        cycle: Dictionary with keys: major, minor, number, title, content
        runbook_path: Path to runbook file
        default_model: Default model if not specified in cycle content
        phase_context: Optional preamble text for the phase (injected as ## Phase Context)

    Returns:
        Formatted cycle file content with phase (major cycle number)
    """
    meta = extract_step_metadata(cycle["content"], default_model)

    header_lines = [
        f"# Cycle {cycle['number']}",
        "",
        f"**Plan**: `{runbook_path}`",
        f"**Execution Model**: {meta['model']}",
        f"**Phase**: {cycle['major']}",
    ]
    if "report_path" in meta:
        header_lines.append(f"**Report Path**: `{meta['report_path']}`")

    header_lines.append("")
    header_lines.append("---")
    if phase_context and phase_context.strip():
        header_lines.extend(
            ["", "## Phase Context", "", phase_context.strip(), "", "---"]
        )
    header_lines.extend(["", cycle["content"], ""])
    return "\n".join(header_lines)


def generate_default_orchestrator(
    runbook_name,
    cycles=None,
    steps=None,
    step_phases=None,
    inline_phases=None,
    phase_dir=None,
    phase_models=None,
    default_model=None,
    phase_agents=None,
    phase_types=None,
):
    """Generate default orchestrator instructions.

    Args:
        runbook_name: Name of the runbook
        cycles: Optional list of cycles (TDD items)
        steps: Optional dict of step_num -> content (general items)
        step_phases: Optional dict of step_num -> phase_number
        inline_phases: Optional dict of phase_number -> phase_content
        phase_dir: Optional path to directory containing source phase files
        phase_models: Optional dict of phase_num -> model (phase-level overrides)
        default_model: Optional fallback model from frontmatter
        phase_agents: Optional dict of phase_num -> agent_name
        phase_types: Optional dict of phase_num -> type_str

    Returns:
        Orchestrator plan content with phase boundary markers
    """
    if phase_agents:
        header_text = "Execute steps using per-phase agents."
    else:
        header_text = f"Execute steps sequentially using crew-{runbook_name} agent."

    content = f"""# Orchestrator Plan: {runbook_name}

{header_text}

Stop on error and escalate to sonnet for diagnostic/fix.
"""

    # Build unified item list: (phase, minor, file_stem, display, execution_mode)
    # execution_mode: 'steps' for agent-delegated, 'inline' for orchestrator-direct
    items = []
    if cycles:
        for cycle in cycles:
            file_stem = f"step-{cycle['major']}-{cycle['minor']}"
            items.append(
                (
                    cycle["major"],
                    cycle["minor"],
                    file_stem,
                    f"Cycle {cycle['number']}",
                    "steps",
                )
            )
    if steps:
        step_phases = step_phases or {}
        for step_num in steps:
            parts = step_num.split(".")
            phase = step_phases.get(step_num, int(parts[0]) if parts else 1)
            minor = int(parts[1]) if len(parts) > 1 else 0
            file_stem = f"step-{step_num.replace('.', '-')}"
            items.append((phase, minor, file_stem, f"Step {step_num}", "steps"))
    if inline_phases:
        for phase_num in sorted(inline_phases):
            items.append(
                (
                    phase_num,
                    0,
                    f"phase-{phase_num}",
                    f"Phase {phase_num} (inline)",
                    "inline",
                )
            )

    if not items:
        return content

    items.sort(key=lambda x: (x[0], x[1]))

    if phase_agents is not None:
        all_phases = sorted({item[0] for item in items})
        content += "\n## Phase-Agent Mapping\n\n"
        content += "| Phase | Agent | Type |\n"
        content += "| --- | --- | --- |\n"
        for p in all_phases:
            agent = (phase_agents or {}).get(p, f"crew-{runbook_name}-p{p}")
            ptype = (phase_types or {}).get(p, "")
            content += f"| {p} | {agent} | {ptype} |\n"
        content += "\n"

    content += "\n## Step Execution Order\n\n"

    for i, (phase, minor, file_stem, display, exec_mode) in enumerate(items):
        is_phase_boundary = (i + 1 == len(items)) or (items[i + 1][0] != phase)
        agent_line = ""
        if phase_agents is not None:
            agent_name = phase_agents.get(phase, f"crew-{runbook_name}-p{phase}")
            agent_line = f"Agent: {agent_name}\n"
        if exec_mode == "inline":
            content += f"## {file_stem} ({display})\n"
            if agent_line:
                content += agent_line
            content += "Execution: inline\n"
            if is_phase_boundary:
                content += f"[Last item of phase {phase}. Insert functional review checkpoint before Phase {phase + 1}.]\n\n"
            else:
                content += "\n"
        elif is_phase_boundary:
            content += f"## {file_stem} ({display}) — PHASE_BOUNDARY\n"
            if agent_line:
                content += agent_line
            content += f"Execution: steps/{file_stem}.md\n"
            if phase_dir is not None:
                content += f"Phase file: {phase_dir}/runbook-phase-{phase}.md\n"
            content += f"[Last item of phase {phase}. Insert functional review checkpoint before Phase {phase + 1}.]\n\n"
        else:
            content += f"## {file_stem} ({display})\n"
            if agent_line:
                content += agent_line
            content += f"Execution: steps/{file_stem}.md\n\n"

    if phase_models is not None or default_model is not None:
        all_phases = sorted({phase for phase, _, _, _, _ in items})
        resolved = phase_models or {}
        content += "\n## Phase Models\n\n"
        for p in all_phases:
            model = resolved.get(p, default_model)
            content += f"- Phase {p}: {model}\n"

    return content


def validate_and_create(
    runbook_path,
    sections,
    runbook_name,
    agents_dir,
    steps_dir,
    orchestrator_path,
    metadata,
    cycles=None,
    phase_models=None,
    phase_preambles=None,
    phase_dir=None,
) -> bool:
    """Validate and create all output files."""
    runbook_type = metadata.get("type", "general")
    has_inline = bool(sections.get("inline_phases"))

    # Validation
    if runbook_type == "tdd":
        if not cycles:
            print("ERROR: No cycles found in TDD runbook", file=sys.stderr)
            return False
    elif runbook_type == "mixed":
        if not cycles:
            print("ERROR: No cycles found in mixed runbook", file=sys.stderr)
            return False
        if not sections["steps"] and not has_inline:
            print(
                "ERROR: No steps or inline phases found in mixed runbook",
                file=sys.stderr,
            )
            return False
    elif runbook_type == "inline":
        if not has_inline:
            print("ERROR: No inline phases found in inline runbook", file=sys.stderr)
            return False
    elif not sections["steps"] and not has_inline:
        print(
            "ERROR: No steps or inline phases found in general runbook", file=sys.stderr
        )
        return False

    # Validate phase numbering (include cycle phases for mixed runbooks)
    if sections["steps"] or cycles:
        all_phases = dict(sections.get("step_phases", {}))
        if cycles:
            for cycle in cycles:
                all_phases[cycle["number"]] = cycle["major"]
        phase_errors, phase_warnings = validate_phase_numbering(all_phases)
        for warning in phase_warnings:
            print(warning, file=sys.stderr)
        if phase_errors:
            for error in phase_errors:
                print(error, file=sys.stderr)
            return False

    # Validate every step/cycle resolves to a model
    frontmatter_model = metadata.get("model")
    phase_models = phase_models or {}
    unresolved = []
    if cycles:
        for cycle in cycles:
            step_model = extract_step_metadata(cycle["content"]).get("model")
            resolved = (
                step_model or phase_models.get(cycle["major"]) or frontmatter_model
            )
            if not resolved:
                unresolved.append(f"cycle {cycle['number']}")
    if sections.get("steps"):
        step_phases_map = sections.get("step_phases", {})
        for step_num in sections["steps"]:
            step_model = extract_step_metadata(sections["steps"][step_num]).get("model")
            phase = step_phases_map.get(step_num, 1)
            resolved = step_model or phase_models.get(phase) or frontmatter_model
            if not resolved:
                unresolved.append(f"step {step_num}")
    if unresolved:
        for item in unresolved:
            print(f"ERROR: No model specified for {item}", file=sys.stderr)
        return False

    # Create directories
    agents_dir.mkdir(parents=True, exist_ok=True)
    steps_dir.mkdir(parents=True, exist_ok=True)

    # Clean steps directory to prevent orphaned files from previous runs
    if steps_dir.exists():
        for step_file in steps_dir.glob("*.md"):
            step_file.unlink()

    # Verify writable
    try:
        agents_dir.touch(exist_ok=True)
        steps_dir.touch(exist_ok=True)
    except (OSError, IsADirectoryError):
        pass

    model = metadata.get("model")

    # Detect phase types from assembled content
    assembled_content = ""
    if cycles:
        for cycle in cycles:
            assembled_content += cycle.get("content", "")
    if sections.get("steps"):
        for step_content in sections["steps"].values():
            assembled_content += step_content

    # Build full content with phase headers for detect_phase_types
    full_content_parts = []
    if cycles:
        # Reconstruct phase headers from cycle major numbers
        seen_phases: set = set()
        for cycle in sorted(cycles, key=lambda c: (c["major"], c["minor"])):
            if cycle["major"] not in seen_phases:
                full_content_parts.append(f"### Phase {cycle['major']}:\n")
                seen_phases.add(cycle["major"])
            full_content_parts.append(cycle.get("content", "") + "\n")
    if sections.get("steps"):
        step_phases_map = sections.get("step_phases", {})
        seen_phases = set()
        for step_num in sorted(
            sections["steps"].keys(), key=lambda x: tuple(map(int, x.split(".")))
        ):
            phase = step_phases_map.get(step_num, 1)
            if phase not in seen_phases:
                full_content_parts.append(f"### Phase {phase}:\n")
                seen_phases.add(phase)
            full_content_parts.append(sections["steps"][step_num] + "\n")
    if sections.get("inline_phases"):
        for phase_num, phase_content in sorted(sections["inline_phases"].items()):
            full_content_parts.append(
                f"### Phase {phase_num}: (type: inline)\n{phase_content}\n"
            )

    full_content = "".join(full_content_parts)
    phase_types = detect_phase_types(full_content)

    # Determine total non-inline phases for naming
    non_inline_phases = sorted(p for p, t in phase_types.items() if t != "inline")
    total_non_inline = len(non_inline_phases)

    # Generate per-phase agent files
    plan_context = sections["common_context"] or ""
    preambles = phase_preambles or {}
    phase_agents: dict = {}
    created_agents = []

    for phase_num, ptype in sorted(phase_types.items()):
        if ptype == "inline":
            phase_agents[phase_num] = "(orchestrator-direct)"
            continue

        # Resolve model for this phase
        phase_model = phase_models.get(phase_num) or model

        # For single non-inline phase, use no -pN suffix
        if total_non_inline == 1:
            agent_name = f"crew-{runbook_name}"
        else:
            agent_name = f"crew-{runbook_name}-p{phase_num}"

        phase_agents[phase_num] = agent_name

        agent_content = generate_phase_agent(
            runbook_name,
            phase_num=phase_num,
            phase_type=ptype,
            plan_context=plan_context,
            phase_context=preambles.get(phase_num, ""),
            model=phase_model,
            total_phases=total_non_inline,
        )
        agent_file = agents_dir / f"{agent_name}.md"
        agent_file.write_text(agent_content)
        print(f"✓ Created agent: {agent_file}")
        created_agents.append(str(agent_file))

    # Generate step files for TDD cycles
    if cycles:
        for cycle in sorted(cycles, key=lambda c: (c["major"], c["minor"])):
            step_file_name = f"step-{cycle['major']}-{cycle['minor']}.md"
            step_path = steps_dir / step_file_name
            cycle_model = phase_models.get(cycle["major"], model)
            step_file_content = generate_cycle_file(
                cycle,
                str(runbook_path),
                cycle_model,
                phase_context=preambles.get(cycle["major"], ""),
            )
            step_path.write_text(step_file_content)
            print(f"✓ Created step: {step_path}")

    # Generate step files for general steps
    if sections["steps"]:
        step_phases = sections.get("step_phases", {})
        for step_num in sorted(
            sections["steps"].keys(), key=lambda x: tuple(map(int, x.split(".")))
        ):
            step_content = sections["steps"][step_num]
            step_file_name = f"step-{step_num.replace('.', '-')}.md"
            step_path = steps_dir / step_file_name
            phase = step_phases.get(step_num, 1)
            step_model = phase_models.get(phase, model)
            step_file_content = generate_step_file(
                step_num,
                step_content,
                str(runbook_path),
                step_model,
                phase,
                phase_context=preambles.get(phase, ""),
            )
            step_path.write_text(step_file_content)
            print(f"✓ Created step: {step_path}")

    # Generate orchestrator plan
    if sections["orchestrator"]:
        orchestrator_content = sections["orchestrator"]
    else:
        orchestrator_content = generate_default_orchestrator(
            runbook_name,
            cycles,
            sections["steps"] if sections else None,
            sections.get("step_phases") if sections else None,
            sections.get("inline_phases") if sections else None,
            phase_dir=phase_dir,
            phase_models=phase_models or {},
            default_model=frontmatter_model,
            phase_agents=phase_agents if phase_agents else None,
            phase_types=phase_types if phase_types else None,
        )

    orchestrator_path.write_text(orchestrator_content)
    print(f"✓ Created orchestrator: {orchestrator_path}")

    # Summary
    print("\nSummary:")
    print(f"  Runbook: {runbook_name}")
    print(f"  Type: {runbook_type}")
    total_steps = len(cycles or []) + len(sections["steps"])
    print(f"  Steps: {total_steps}")
    print(f"  Model: {model}")

    # Stage all generated artifacts
    paths_to_stage = [*created_agents, str(steps_dir), str(orchestrator_path)]
    result = subprocess.run(
        ["git", "add", *paths_to_stage], check=False, capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"⚠ git add failed: {result.stderr.strip()}")
        return False
    print("✓ Staged artifacts for commit")

    return True


def main() -> None:
    if len(sys.argv) < 2:
        print(
            "Usage: prepare-runbook.py <runbook-file.md> OR <directory-with-phase-files>",
            file=sys.stderr,
        )
        print(file=sys.stderr)
        print("Transforms runbook markdown into execution artifacts:", file=sys.stderr)
        print(
            "  - Per-phase agents (.claude/agents/crew-<runbook-name>[-p<N>].md)",
            file=sys.stderr,
        )
        print("  - Step/Cycle files (plans/<runbook-name>/steps/)", file=sys.stderr)
        print(
            "  - Orchestrator plan (plans/<runbook-name>/orchestrator-plan.md)",
            file=sys.stderr,
        )
        print(file=sys.stderr)
        print("Supports:", file=sys.stderr)
        print("  - General runbooks (## Step N:)", file=sys.stderr)
        print(
            "  - TDD runbooks (## Cycle X.Y:, requires type: tdd in frontmatter)",
            file=sys.stderr,
        )
        print(
            "  - Phase-grouped runbooks (runbook-phase-*.md files in directory)",
            file=sys.stderr,
        )
        sys.exit(1)

    input_path = Path(sys.argv[1])

    # Validate input exists
    if not input_path.exists():
        print(f"ERROR: Path not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    # Handle directory vs file input
    if input_path.is_dir():
        # Try to assemble from phase files
        assembled_content, _phase_file = assemble_phase_files(input_path)
        if assembled_content is None:
            # Error already printed by assemble_phase_files if validation failed
            # Only print "not found" message if no phase files exist
            if not list(input_path.glob("runbook-phase-*.md")):
                print(
                    f"ERROR: No runbook-phase-*.md files found in directory: {input_path}",
                    file=sys.stderr,
                )
            sys.exit(1)
        content = assembled_content
        # Use parent directory for naming (plans/foo/ -> foo)
        runbook_path = input_path / "runbook.md"
        print(f"✓ Assembled from phase files in {input_path}", file=sys.stderr)
    else:
        # Single file input
        runbook_path = input_path
        content = runbook_path.read_text()

    # Parse runbook
    metadata, body = parse_frontmatter(content)

    # Always extract both general sections and TDD cycles
    sections = extract_sections(body)
    if sections is None:
        sys.exit(1)
    cycles = extract_cycles(body)

    # Auto-detect effective type from content
    has_cycles = bool(cycles)
    has_steps = bool(sections["steps"])
    has_inline = bool(sections.get("inline_phases"))
    if has_cycles and (has_steps or has_inline):
        metadata["type"] = "mixed"
    elif has_cycles:
        metadata["type"] = "tdd"
    elif has_inline and not has_steps:
        metadata["type"] = "inline"
    elif not has_steps and not has_inline:
        metadata["type"] = metadata.get("type", "general")

    # Validate cycles if present
    if has_cycles:
        errors, warnings = validate_cycle_numbering(cycles)
        for warning in warnings:
            print(warning, file=sys.stderr)
        if errors:
            for error in errors:
                print(error, file=sys.stderr)
            sys.exit(1)

        # Build validation context from Common Context + phase preambles
        common_parts = []
        common_match = re.search(
            r"## Common Context\s*\n(.*?)(?=\n## |\Z)", body, re.DOTALL
        )
        if common_match:
            common_parts.append(common_match.group(1))
        # Phase preambles (text between ### Phase N: and first ## child)
        for m in re.finditer(r"### Phase\s+\d+:.*?\n(.*?)(?=\n## )", body, re.DOTALL):
            common_parts.append(m.group(1))
        common_context = "\n".join(common_parts)

        all_messages = []
        critical_errors = []
        for cycle in cycles:
            messages = validate_cycle_structure(cycle, common_context)
            all_messages.extend(messages)
            critical_errors.extend([m for m in messages if m.startswith("ERROR:")])

        for msg in all_messages:
            print(msg, file=sys.stderr)

        if critical_errors:
            print(
                f"\nERROR: Found {len(critical_errors)} critical validation error(s)",
                file=sys.stderr,
            )
            sys.exit(1)

    # Validate file references in steps
    ref_warnings = validate_file_references(sections, cycles, runbook_path)
    for warning in ref_warnings:
        print(warning, file=sys.stderr)

    # Derive paths
    runbook_name, agents_dir, steps_dir, orchestrator_path = derive_paths(runbook_path)

    # Extract per-phase model overrides and phase preambles
    phase_models = extract_phase_models(body)
    phase_preambles = extract_phase_preambles(body)

    # Validate and create
    phase_dir = str(input_path) if input_path.is_dir() else None
    if not validate_and_create(
        runbook_path,
        sections,
        runbook_name,
        agents_dir,
        steps_dir,
        orchestrator_path,
        metadata,
        cycles,
        phase_models,
        phase_preambles,
        phase_dir=phase_dir,
    ):
        sys.exit(1)


if __name__ == "__main__":
    main()
