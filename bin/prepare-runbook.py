#!/usr/bin/env python3
"""
Prepare execution artifacts from runbook markdown files.

Transforms a runbook markdown file into:
1. Plan-specific agent (.claude/agents/<runbook-name>-task.md)
2. Step/Cycle files (plans/<runbook-name>/steps/)
3. Orchestrator plan (plans/<runbook-name>/orchestrator-plan.md)

Supports:
- General runbooks (## Step N:)
- TDD runbooks (## Cycle X.Y:, requires type: tdd in frontmatter)

Usage:
    prepare-runbook.py <runbook-file.md>

Example (General):
    prepare-runbook.py plans/foo/runbook.md
    # Creates:
    #   .claude/agents/foo-task.md (uses quiet-task.md baseline)
    #   plans/foo/steps/step-*.md
    #   plans/foo/orchestrator-plan.md

Example (TDD):
    prepare-runbook.py plans/tdd-test/runbook.md
    # Creates:
    #   .claude/agents/tdd-test-task.md (uses tdd-task.md baseline)
    #   plans/tdd-test/steps/cycle-*.md
    #   plans/tdd-test/orchestrator-plan.md
"""

import sys
import re
import os
from pathlib import Path


def parse_frontmatter(content):
    """Extract YAML frontmatter from markdown content.

    Returns: (metadata_dict, remaining_content)

    Metadata includes:
    - type: 'tdd' or 'general' (default: 'general')
    - model: execution model (default: 'haiku')
    - name: runbook name
    """
    if not content.startswith('---'):
        return {}, content

    try:
        end_idx = content.index('---', 3)
    except ValueError:
        return {}, content

    meta_str = content[3:end_idx].strip()
    remaining = content[end_idx + 3:].lstrip()

    metadata = {}
    for line in meta_str.split('\n'):
        if ':' in line:
            key, _, value = line.partition(':')
            metadata[key.strip()] = value.strip().strip('"').strip("'")

    # Set default runbook type
    if 'type' not in metadata:
        metadata['type'] = 'general'
    else:
        # Validate type field
        valid_types = ['tdd', 'general']
        if metadata['type'] not in valid_types:
            print(f"WARNING: Unknown runbook type '{metadata['type']}', defaulting to 'general'", file=sys.stderr)
            metadata['type'] = 'general'

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
    cycle_pattern = r'^###? Cycle\s+(\d+)\.(\d+):\s*(.*)'
    lines = content.split('\n')

    cycles = []
    current_cycle = None
    current_content = []

    for i, line in enumerate(lines):
        # Check for cycle header
        match = re.match(cycle_pattern, line)
        if match:
            # Save previous cycle
            if current_cycle is not None:
                current_cycle['content'] = '\n'.join(current_content).strip()
                cycles.append(current_cycle)

            # Start new cycle
            major = int(match.group(1))
            minor = int(match.group(2))
            title = match.group(3).strip()

            current_cycle = {
                'major': major,
                'minor': minor,
                'number': f"{major}.{minor}",
                'title': title
            }
            current_content = [line]

        # Check for next H2/H3 (non-cycle section) - terminates current cycle
        elif (line.startswith('## ') or line.startswith('### ')) and current_cycle is not None:
            # End current cycle - any H2/H3 that's not a cycle terminates the current cycle
            current_cycle['content'] = '\n'.join(current_content).strip()
            cycles.append(current_cycle)
            current_cycle = None
            current_content = []

        # Accumulate content
        elif current_cycle is not None:
            current_content.append(line)

    # Save final cycle
    if current_cycle is not None:
        current_cycle['content'] = '\n'.join(current_content).strip()
        cycles.append(current_cycle)

    return cycles


def validate_cycle_structure(cycle, common_context=''):
    """Validate that cycle contains mandatory TDD sections.

    Args:
        cycle: Cycle dictionary with 'number', 'content', 'title', 'major' keys
        common_context: Content from Common Context section (for inherited sections)

    Returns: List of error/warning messages (empty if valid)
    """
    content = cycle['content'].lower()
    cycle_num = cycle['number']
    title = cycle.get('title', '')
    messages = []

    # Detect cycle type from conventions
    is_spike = cycle['major'] == 0
    is_regression = '[regression]' in title.lower()

    # Spike cycles (0.x): no RED/GREEN required
    if is_spike:
        pass  # Skip RED/GREEN validation for exploratory cycles
    # Regression cycles: GREEN only, no RED expected
    elif is_regression:
        if 'green' not in content:
            messages.append(f"ERROR: Cycle {cycle_num} missing required section: GREEN phase")
    # Standard cycles: both RED and GREEN required
    else:
        if 'red' not in content:
            messages.append(f"ERROR: Cycle {cycle_num} missing required section: RED phase")
        if 'green' not in content:
            messages.append(f"ERROR: Cycle {cycle_num} missing required section: GREEN phase")

    # Check for mandatory Stop Conditions (can be in cycle OR Common Context)
    common_lower = common_context.lower()
    if 'stop condition' not in content and 'stop condition' not in common_lower:
        messages.append(f"ERROR: Cycle {cycle_num} missing required section: Stop Conditions")

    # Warn if missing dependencies (can be in cycle OR Common Context, non-critical)
    if 'dependencies' not in content and 'dependency' not in content and 'dependencies' not in common_lower and 'dependency' not in common_lower:
        messages.append(f"WARNING: Cycle {cycle_num} missing dependencies section")

    return messages


def validate_cycle_numbering(cycles):
    """Validate cycle numbering is sequential.

    Returns: List of error messages (empty if valid)
    """
    if not cycles:
        return ["ERROR: No cycles found in TDD runbook"]

    errors = []

    # Check for duplicates
    seen = set()
    for cycle in cycles:
        cycle_id = cycle['number']
        if cycle_id in seen:
            errors.append(f"ERROR: Duplicate cycle number: {cycle_id}")
        seen.add(cycle_id)

    # Check major numbers are sequential
    major_nums = sorted(set(c['major'] for c in cycles))
    if major_nums[0] not in (0, 1):
        errors.append(f"ERROR: First cycle must start at 0.x or 1.x, found {major_nums[0]}.x")

    for i in range(len(major_nums) - 1):
        if major_nums[i+1] != major_nums[i] + 1:
            errors.append(f"ERROR: Gap in major cycle numbers: {major_nums[i]} -> {major_nums[i+1]}")

    # Check minor numbers are sequential within each major
    by_major = {}
    for cycle in cycles:
        major = cycle['major']
        if major not in by_major:
            by_major[major] = []
        by_major[major].append(cycle['minor'])

    for major, minors in by_major.items():
        sorted_minors = sorted(minors)
        if sorted_minors[0] != 1:
            errors.append(f"ERROR: Cycle {major}.x must start at {major}.1, found {major}.{sorted_minors[0]}")

        for i in range(len(sorted_minors) - 1):
            if sorted_minors[i+1] != sorted_minors[i] + 1:
                errors.append(f"ERROR: Gap in cycle {major}.x: {major}.{sorted_minors[i]} -> {major}.{sorted_minors[i+1]}")

    return errors


def extract_sections(content):
    """Extract Common Context, Steps, and Orchestrator sections.

    Returns: {
        'common_context': (section_content or None),
        'steps': {step_num: step_content, ...},
        'orchestrator': section_content or None
    }
    """
    sections = {
        'common_context': None,
        'steps': {},
        'orchestrator': None
    }

    # Split by H2 headings
    h2_pattern = r'^## '
    lines = content.split('\n')

    current_section = None
    current_content = []
    current_step = None
    step_pattern = r'^## Step\s+([\d.]+):\s*(.*)'

    for i, line in enumerate(lines):
        if line.startswith('## '):
            # Save previous section
            if current_section and current_content:
                content_str = '\n'.join(current_content).strip()
                if current_section == 'common_context':
                    sections['common_context'] = content_str
                elif current_section == 'orchestrator':
                    sections['orchestrator'] = content_str
                elif current_section == 'step':
                    sections['steps'][current_step] = content_str

            # Detect new section
            if line == '## Common Context':
                current_section = 'common_context'
                current_content = [line]
            elif line.startswith('## Step '):
                match = re.match(step_pattern, line)
                if match:
                    step_num = match.group(1)
                    if step_num in sections['steps']:
                        print(f"ERROR: Duplicate step number: {step_num}", file=sys.stderr)
                        return None
                    current_section = 'step'
                    current_step = step_num
                    current_content = [line]
                else:
                    current_section = None
                    current_content = []
            elif line == '## Orchestrator Instructions':
                current_section = 'orchestrator'
                current_content = [line]
            else:
                current_section = None
                current_content = []
        else:
            if current_section:
                current_content.append(line)

    # Save final section
    if current_section and current_content:
        content_str = '\n'.join(current_content).strip()
        if current_section == 'common_context':
            sections['common_context'] = content_str
        elif current_section == 'orchestrator':
            sections['orchestrator'] = content_str
        elif current_section == 'step':
            sections['steps'][current_step] = content_str

    return sections


def derive_paths(runbook_path):
    """Derive output paths from runbook location and name.

    Input: plans/foo/runbook.md
    Returns:
        runbook_name: 'foo' (parent directory)
        agent_path: .claude/agents/foo-task.md
        steps_dir: plans/foo/steps/
        orchestrator_path: plans/foo/orchestrator-plan.md
    """
    path = Path(runbook_path)
    runbook_name = path.parent.name

    agent_path = Path('.claude/agents') / f'{runbook_name}-task.md'
    steps_dir = path.parent / 'steps'
    orchestrator_path = path.parent / 'orchestrator-plan.md'

    return runbook_name, agent_path, steps_dir, orchestrator_path


def read_baseline_agent(runbook_type='general'):
    """Read baseline agent template based on runbook type.

    Args:
        runbook_type: 'tdd' or 'general'

    Returns:
        Baseline agent body (without frontmatter)
    """
    if runbook_type == 'tdd':
        baseline_path = Path('agent-core/agents/tdd-task.md')
    else:
        baseline_path = Path('agent-core/agents/quiet-task.md')

    if not baseline_path.exists():
        print(f"ERROR: Baseline agent not found: {baseline_path}", file=sys.stderr)
        sys.exit(1)

    content = baseline_path.read_text()
    _, body = parse_frontmatter(content)
    return body


def generate_agent_frontmatter(runbook_name, model='haiku'):
    """Generate frontmatter for plan-specific agent."""
    return f"""---
name: {runbook_name}-task
description: Execute {runbook_name} steps from the plan with plan-specific context.
model: {model}
color: cyan
tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob"]
---
"""


def generate_step_file(step_num, step_content, runbook_path):
    """Generate step file with references."""
    return f"""# Step {step_num}

**Plan**: `{runbook_path}`
**Common Context**: See plan file for context

---

{step_content}
"""


def generate_cycle_file(cycle, runbook_path):
    """Generate cycle file with references.

    Args:
        cycle: Dictionary with keys: major, minor, number, title, content
        runbook_path: Path to runbook file

    Returns:
        Formatted cycle file content
    """
    return f"""# Cycle {cycle['number']}

**Plan**: `{runbook_path}`
**Common Context**: See plan file for context

---

{cycle['content']}
"""


def generate_default_orchestrator(runbook_name):
    """Generate default orchestrator instructions."""
    return f"""# Orchestrator Plan: {runbook_name}

Execute steps sequentially using {runbook_name}-task agent.

Stop on error and escalate to sonnet for diagnostic/fix.
"""


def validate_and_create(runbook_path, sections, runbook_name, agent_path, steps_dir, orchestrator_path, metadata, cycles=None):
    """Validate and create all output files."""
    runbook_type = metadata.get('type', 'general')

    # Validation
    if runbook_type == 'tdd':
        if not cycles:
            print("ERROR: No cycles found in TDD runbook", file=sys.stderr)
            return False
    else:
        if not sections['steps']:
            print("ERROR: No steps found in general runbook", file=sys.stderr)
            return False

    # Create directories
    agent_path.parent.mkdir(parents=True, exist_ok=True)
    steps_dir.mkdir(parents=True, exist_ok=True)

    # Verify writable
    try:
        agent_path.parent.touch(exist_ok=True)
        steps_dir.touch(exist_ok=True)
    except (OSError, IsADirectoryError):
        pass

    # Generate plan-specific agent
    baseline_body = read_baseline_agent(runbook_type)
    model = metadata.get('model', 'haiku')
    frontmatter = generate_agent_frontmatter(runbook_name, model)

    agent_content = frontmatter + baseline_body
    if sections['common_context']:
        agent_content += "\n---\n# Runbook-Specific Context\n\n" + sections['common_context']

    agent_path.write_text(agent_content)
    print(f"✓ Created agent: {agent_path}")

    # Generate step files (uniform naming for all runbook types)
    if runbook_type == 'tdd':
        # Generate step files for TDD cycles
        for cycle in sorted(cycles, key=lambda c: (c['major'], c['minor'])):
            step_file_name = f"step-{cycle['major']}-{cycle['minor']}.md"
            step_path = steps_dir / step_file_name

            step_file_content = generate_cycle_file(cycle, str(runbook_path))
            step_path.write_text(step_file_content)
            print(f"✓ Created step: {step_path}")
    else:
        # Generate step files
        for step_num in sorted(sections['steps'].keys(), key=lambda x: tuple(map(int, x.split('.')))):
            step_content = sections['steps'][step_num]
            step_file_name = f"step-{step_num.replace('.', '-')}.md"
            step_path = steps_dir / step_file_name

            step_file_content = generate_step_file(step_num, step_content, str(runbook_path))
            step_path.write_text(step_file_content)
            print(f"✓ Created step: {step_path}")

    # Generate orchestrator plan
    if sections['orchestrator']:
        orchestrator_content = sections['orchestrator']
    else:
        orchestrator_content = generate_default_orchestrator(runbook_name)

    orchestrator_path.write_text(orchestrator_content)
    print(f"✓ Created orchestrator: {orchestrator_path}")

    # Summary
    print(f"\nSummary:")
    print(f"  Runbook: {runbook_name}")
    print(f"  Type: {runbook_type}")
    if runbook_type == 'tdd':
        print(f"  Steps: {len(cycles)}")
    else:
        print(f"  Steps: {len(sections['steps'])}")
    print(f"  Model: {model}")

    return True


def main():
    if len(sys.argv) < 2:
        print("Usage: prepare-runbook.py <runbook-file.md>", file=sys.stderr)
        print("", file=sys.stderr)
        print("Transforms runbook markdown into execution artifacts:", file=sys.stderr)
        print("  - Plan-specific agent (.claude/agents/<runbook-name>-task.md)", file=sys.stderr)
        print("  - Step/Cycle files (plans/<runbook-name>/steps/)", file=sys.stderr)
        print("  - Orchestrator plan (plans/<runbook-name>/orchestrator-plan.md)", file=sys.stderr)
        print("", file=sys.stderr)
        print("Supports:", file=sys.stderr)
        print("  - General runbooks (## Step N:)", file=sys.stderr)
        print("  - TDD runbooks (## Cycle X.Y:, requires type: tdd in frontmatter)", file=sys.stderr)
        sys.exit(1)

    runbook_path = Path(sys.argv[1])

    # Validate runbook exists
    if not runbook_path.exists():
        print(f"ERROR: Runbook not found: {runbook_path}", file=sys.stderr)
        sys.exit(1)

    # Read and parse runbook
    content = runbook_path.read_text()
    metadata, body = parse_frontmatter(content)

    runbook_type = metadata.get('type', 'general')

    # Extract sections based on runbook type
    if runbook_type == 'tdd':
        # Extract cycles and validate numbering
        cycles = extract_cycles(body)
        errors = validate_cycle_numbering(cycles)
        if errors:
            for error in errors:
                print(error, file=sys.stderr)
            sys.exit(1)

        # Extract Common Context for inherited section validation
        common_context = ''
        common_match = re.search(r'## Common Context\s*\n(.*?)(?=\n## |\Z)', body, re.DOTALL)
        if common_match:
            common_context = common_match.group(1)

        # Validate cycle structure (mandatory sections)
        all_messages = []
        critical_errors = []
        for cycle in cycles:
            messages = validate_cycle_structure(cycle, common_context)
            all_messages.extend(messages)
            critical_errors.extend([m for m in messages if m.startswith('ERROR:')])

        # Print all validation messages
        for msg in all_messages:
            if msg.startswith('ERROR:'):
                print(msg, file=sys.stderr)
            else:
                print(msg, file=sys.stderr)  # Warnings also to stderr

        # Stop if critical errors found
        if critical_errors:
            print(f"\nERROR: Found {len(critical_errors)} critical validation error(s)", file=sys.stderr)
            sys.exit(1)

        # Extract common context and orchestrator (reuse extract_sections for these)
        sections = extract_sections(body)
        if sections is None:
            sys.exit(1)
    else:
        # Extract steps (general runbook)
        sections = extract_sections(body)
        if sections is None:
            sys.exit(1)
        cycles = None

    # Derive paths
    runbook_name, agent_path, steps_dir, orchestrator_path = derive_paths(runbook_path)

    # Validate and create
    if not validate_and_create(runbook_path, sections, runbook_name, agent_path, steps_dir, orchestrator_path, metadata, cycles):
        sys.exit(1)


if __name__ == '__main__':
    main()
