#!/usr/bin/env python3
"""
Prepare execution artifacts from runbook markdown files.

Transforms a runbook markdown file into:
1. Plan-specific agent (.claude/agents/<runbook-name>-task.md)
2. Step files (plans/<runbook-name>/steps/step-*.md)
3. Orchestrator plan (plans/<runbook-name>/orchestrator-plan.md)

Usage:
    prepare-runbook.py <runbook-file.md>

Example:
    prepare-runbook.py plans/foo/phase2-execution-plan.md
    # Creates:
    #   .claude/agents/foo-task.md
    #   plans/foo/steps/step-*.md
    #   plans/foo/orchestrator-plan.md
"""

import sys
import re
import os
from pathlib import Path


def parse_frontmatter(content):
    """Extract YAML frontmatter from markdown content.

    Returns: (metadata_dict, remaining_content)
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

    return metadata, remaining


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


def read_baseline_agent():
    """Read baseline quiet-task agent, skip frontmatter."""
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


def generate_default_orchestrator(runbook_name):
    """Generate default orchestrator instructions."""
    return f"""# Orchestrator Plan: {runbook_name}

Execute steps sequentially using {runbook_name}-task agent.

Stop on error and escalate to sonnet for diagnostic/fix.
"""


def validate_and_create(runbook_path, sections, runbook_name, agent_path, steps_dir, orchestrator_path, metadata):
    """Validate and create all output files."""
    # Validation
    if not sections['steps']:
        print("ERROR: No step sections found in runbook", file=sys.stderr)
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
    baseline_body = read_baseline_agent()
    model = metadata.get('model', 'haiku')
    frontmatter = generate_agent_frontmatter(runbook_name, model)

    agent_content = frontmatter + baseline_body
    if sections['common_context']:
        agent_content += "\n---\n# Runbook-Specific Context\n\n" + sections['common_context']

    agent_path.write_text(agent_content)
    print(f"✓ Created agent: {agent_path}")

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
    print(f"  Steps: {len(sections['steps'])}")
    print(f"  Model: {model}")

    return True


def main():
    if len(sys.argv) < 2:
        print("Usage: prepare-runbook.py <runbook-file.md>", file=sys.stderr)
        print("", file=sys.stderr)
        print("Transforms runbook markdown into execution artifacts:", file=sys.stderr)
        print("  - Plan-specific agent (.claude/agents/<runbook-name>-task.md)", file=sys.stderr)
        print("  - Step files (plans/<runbook-name>/steps/step-*.md)", file=sys.stderr)
        print("  - Orchestrator plan (plans/<runbook-name>/orchestrator-plan.md)", file=sys.stderr)
        sys.exit(1)

    runbook_path = Path(sys.argv[1])

    # Validate runbook exists
    if not runbook_path.exists():
        print(f"ERROR: Runbook not found: {runbook_path}", file=sys.stderr)
        sys.exit(1)

    # Read and parse runbook
    content = runbook_path.read_text()
    metadata, body = parse_frontmatter(content)

    # Extract sections
    sections = extract_sections(body)
    if sections is None:
        sys.exit(1)

    # Derive paths
    runbook_name, agent_path, steps_dir, orchestrator_path = derive_paths(runbook_path)

    # Validate and create
    if not validate_and_create(runbook_path, sections, runbook_name, agent_path, steps_dir, orchestrator_path, metadata):
        sys.exit(1)


if __name__ == '__main__':
    main()
