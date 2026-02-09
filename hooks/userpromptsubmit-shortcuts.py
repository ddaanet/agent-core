#!/usr/bin/env python3
"""UserPromptSubmit hook: Expand workflow shortcuts.

Tier 1 - Commands (exact match, entire message):
  s, x, xc, r, h, hc, ci, ?

Tier 2 - Directives (colon prefix):
  d:, p:

No match: silent pass-through (exit 0, no output)
"""

import glob
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore

# Tier 1: Command shortcuts (exact match)
COMMANDS = {
    's': (
        '[SHORTCUT: #status] List pending tasks with metadata from session.md. '
        'Display in STATUS format. Wait for instruction.'
    ),
    'x': (
        '[SHORTCUT: #execute] Smart execute: if an in-progress task exists, '
        'resume it. Otherwise start the first pending task from session.md. '
        'Complete the task, then stop. Do NOT commit or handoff.'
    ),
    'xc': (
        '[SHORTCUT: #execute --commit] Execute task to completion, '
        'then handoff → commit → status display.'
    ),
    'r': (
        '[SHORTCUT: #resume] Strict resume: continue in-progress task only. '
        'Error if no in-progress task exists.'
    ),
    'h': '[SHORTCUT: /handoff] Update session.md with current context, '
         'then display status.',
    'hc': '[SHORTCUT: /handoff --commit] Handoff → commit → status display.',
    'ci': '[SHORTCUT: /commit] Commit changes → status display.',
    '?': (
        '[SHORTCUT: #help] List all workflow shortcuts (both tiers), '
        'workflow keywords (y/go/continue), and entry point skills '
        '(/design, /commit, /handoff, /orchestrate, /remember, /shelve, /vet). '
        'Format as a compact reference table.'
    )
}

# Tier 2: Directive shortcuts (colon prefix)
DIRECTIVES = {
    'd': (
        '[DIRECTIVE: DISCUSS] Discussion mode. Analyze and discuss only — '
        'do not execute, implement, or invoke workflow skills. '
        "The user's topic follows in their message."
    ),
    'p': (
        '[DIRECTIVE: PENDING] Record pending task. Append to session.md '
        'Pending Tasks section using metadata format: '
        '`- [ ] **Name** — `command` | model | restart?`. '
        'Infer defaults if not specified. Do NOT execute the task.'
    )
}

# Built-in skills fallback (empty initially — all cooperative skills are project-local or plugin-based)
BUILTIN_SKILLS: Dict[str, Any] = {
    # Add entries here if built-in skills need continuation support
}


def extract_frontmatter(skill_path: Path) -> Optional[Dict[str, Any]]:
    """Extract YAML frontmatter from a SKILL.md file.

    Returns:
        Parsed frontmatter dict, or None if no frontmatter or parse error
    """
    if not yaml:
        return None

    try:
        with open(skill_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for YAML frontmatter (--- at start)
        if not content.startswith('---\n'):
            return None

        # Find closing ---
        end_match = re.search(r'\n---\n', content[4:])
        if not end_match:
            return None

        frontmatter_text = content[4:4 + end_match.start()]
        return yaml.safe_load(frontmatter_text)
    except Exception:
        # Skip malformed files
        return None


def get_enabled_plugins() -> List[str]:
    """Get list of enabled plugins from settings.json.

    Returns:
        List of enabled plugin names (empty if no settings or no plugins)
    """
    settings_path = Path.home() / '.claude' / 'settings.json'
    if not settings_path.exists():
        return []

    try:
        with open(settings_path, 'r', encoding='utf-8') as f:
            settings = json.load(f)
        return settings.get('enabledPlugins', [])
    except Exception:
        return []


def get_plugin_install_path(plugin_name: str, project_dir: str) -> Optional[str]:
    """Resolve plugin install path from installed_plugins.json.

    Args:
        plugin_name: Name of the plugin
        project_dir: Current project directory (for scope filtering)

    Returns:
        Install path if plugin is enabled for this project, None otherwise
    """
    installed_path = Path.home() / '.claude' / 'plugins' / 'installed_plugins.json'
    if not installed_path.exists():
        return None

    try:
        with open(installed_path, 'r', encoding='utf-8') as f:
            installed = json.load(f)

        plugin_info = installed.get(plugin_name)
        if not plugin_info:
            return None

        # Check scope filtering
        scope = plugin_info.get('scope', 'user')
        if scope == 'project':
            # Only include if projectPath matches current project
            if plugin_info.get('projectPath') != project_dir:
                return None

        return plugin_info.get('installPath')
    except Exception:
        return None


def scan_skill_files(base_path: Path) -> List[Path]:
    """Scan for SKILL.md files under a base path.

    Args:
        base_path: Directory to scan recursively

    Returns:
        List of SKILL.md file paths
    """
    if not base_path.exists():
        return []

    pattern = str(base_path / '**' / 'SKILL.md')
    return [Path(p) for p in glob.glob(pattern, recursive=True)]


def build_registry() -> Dict[str, Dict[str, Any]]:
    """Build registry of cooperative skills from all sources.

    Returns:
        Dictionary mapping skill names to continuation metadata:
        {
            "design": {
                "cooperative": True,
                "default_exit": ["/handoff --commit", "/commit"]
            },
            ...
        }
    """
    registry: Dict[str, Dict[str, Any]] = {}

    # Get project directory
    project_dir = os.environ.get('CLAUDE_PROJECT_DIR', '')
    if not project_dir:
        return registry

    project_path = Path(project_dir)

    # 1. Scan project-local skills
    project_skills_path = project_path / '.claude' / 'skills'
    for skill_file in scan_skill_files(project_skills_path):
        frontmatter = extract_frontmatter(skill_file)
        if not frontmatter:
            continue

        continuation = frontmatter.get('continuation', {})
        if not continuation.get('cooperative'):
            continue

        # Extract skill name from frontmatter or directory name
        skill_name = frontmatter.get('name')
        if not skill_name:
            # Use parent directory name
            skill_name = skill_file.parent.name

        registry[skill_name] = {
            'cooperative': True,
            'default_exit': continuation.get('default-exit', [])
        }

    # 2. Scan enabled plugin skills
    enabled_plugins = get_enabled_plugins()
    for plugin_name in enabled_plugins:
        install_path = get_plugin_install_path(plugin_name, project_dir)
        if not install_path:
            continue

        plugin_path = Path(install_path)
        skills_path = plugin_path / 'skills'

        for skill_file in scan_skill_files(skills_path):
            frontmatter = extract_frontmatter(skill_file)
            if not frontmatter:
                continue

            continuation = frontmatter.get('continuation', {})
            if not continuation.get('cooperative'):
                continue

            skill_name = frontmatter.get('name')
            if not skill_name:
                skill_name = skill_file.parent.name

            registry[skill_name] = {
                'cooperative': True,
                'default_exit': continuation.get('default-exit', [])
            }

    # 3. Add built-in skills
    registry.update(BUILTIN_SKILLS)

    return registry


def main() -> None:
    """Expand workflow shortcuts in user prompts."""
    # Read hook input
    hook_input = json.load(sys.stdin)
    prompt = hook_input.get('prompt', '').strip()

    # Tier 1: Exact match for commands
    if prompt in COMMANDS:
        expansion = COMMANDS[prompt]
        output = {
            'hookSpecificOutput': {
                'hookEventName': 'UserPromptSubmit',
                'additionalContext': expansion
            },
            'systemMessage': expansion
        }
        print(json.dumps(output))
        return

    # Tier 2: Directive pattern (shortcut: <rest>)
    match = re.match(r'^(\w+):\s+(.+)', prompt)
    if match:
        directive_key = match.group(1)
        if directive_key in DIRECTIVES:
            expansion = DIRECTIVES[directive_key]
            output = {
                'hookSpecificOutput': {
                    'hookEventName': 'UserPromptSubmit',
                    'additionalContext': expansion
                },
                'systemMessage': expansion
            }
            print(json.dumps(output))
            return

    # No match: silent pass-through
    sys.exit(0)


if __name__ == '__main__':
    main()
