#!/usr/bin/env python3
"""UserPromptSubmit hook: Expand workflow shortcuts.

Tier 1 - Commands (exact match, entire message):
  s, x, xc, r, h, hc, ci, ?

Tier 2 - Directives (colon prefix):
  d:, p:

No match: silent pass-through (exit 0, no output)
"""

import glob
import hashlib
import json
import os
import re
import sys
import time
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


def get_cache_path(paths: List[str], project_dir: str) -> Path:
    """Generate cache file path based on hash of skill paths and project dir.

    Args:
        paths: List of skill file paths
        project_dir: Project directory path

    Returns:
        Path to cache file
    """
    # Sort paths for consistent hashing
    sorted_paths = sorted(paths)

    # Concatenate paths + project dir
    hash_input = ''.join(sorted_paths) + project_dir
    hash_digest = hashlib.sha256(hash_input.encode('utf-8')).hexdigest()[:16]

    # Use TMPDIR from environment, fall back to /tmp/claude
    tmp_dir = os.environ.get('TMPDIR', '/tmp/claude')
    cache_dir = Path(tmp_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)

    return cache_dir / f'continuation-registry-{hash_digest}.json'


def get_cached_registry(cache_path: Path) -> Optional[Dict[str, Any]]:
    """Load registry from cache if valid.

    Args:
        cache_path: Path to cache file

    Returns:
        Cached registry dict if valid, None if cache invalid or missing
    """
    if not cache_path.exists():
        return None

    try:
        with open(cache_path, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)

        # Validate cache structure
        if 'paths' not in cache_data or 'registry' not in cache_data or 'timestamp' not in cache_data:
            return None

        cache_timestamp = cache_data['timestamp']

        # Check if any source file modified since cache
        for path_str in cache_data['paths']:
            path = Path(path_str)
            if not path.exists():
                # Source file deleted, invalidate cache
                return None

            if path.stat().st_mtime > cache_timestamp:
                # File modified, invalidate cache
                return None

        return cache_data['registry']
    except Exception:
        # Cache corrupted or unreadable
        return None


def save_registry_cache(registry: Dict[str, Any], paths: List[str], cache_path: Path) -> None:
    """Save registry to cache.

    Args:
        registry: Registry dict to cache
        paths: List of skill file paths
        cache_path: Path to cache file
    """
    try:
        cache_data = {
            'paths': paths,
            'registry': registry,
            'timestamp': time.time()
        }

        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f)
    except Exception:
        # If caching fails, continue in degraded mode
        pass


def build_registry() -> Dict[str, Dict[str, Any]]:
    """Build registry of cooperative skills from all sources.

    Uses caching for performance. Cache is invalidated when skill files are modified.

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
    # Get project directory
    project_dir = os.environ.get('CLAUDE_PROJECT_DIR', '')
    if not project_dir:
        return {}

    project_path = Path(project_dir)

    # Collect all skill file paths for cache key generation
    all_paths: List[str] = []
    registry: Dict[str, Dict[str, Any]] = {}

    # 1. Scan project-local skills
    project_skills_path = project_path / '.claude' / 'skills'
    project_skill_files = scan_skill_files(project_skills_path)
    all_paths.extend([str(p) for p in project_skill_files])

    # 2. Scan enabled plugin skills
    plugin_skill_files: List[Path] = []
    enabled_plugins = get_enabled_plugins()
    for plugin_name in enabled_plugins:
        install_path = get_plugin_install_path(plugin_name, project_dir)
        if not install_path:
            continue

        plugin_path = Path(install_path)
        skills_path = plugin_path / 'skills'
        plugin_files = scan_skill_files(skills_path)
        plugin_skill_files.extend(plugin_files)
        all_paths.extend([str(p) for p in plugin_files])

    # Generate cache path and check cache
    cache_path = get_cache_path(all_paths, project_dir)
    cached_registry = get_cached_registry(cache_path)

    if cached_registry is not None:
        # Cache hit - return cached registry
        return cached_registry

    # Cache miss - build registry from scratch
    # Process project-local skills
    for skill_file in project_skill_files:
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

    # Process plugin skills
    for skill_file in plugin_skill_files:
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

    # Save to cache
    save_registry_cache(registry, all_paths, cache_path)

    return registry


def find_skill_references(prompt: str, registry: Dict[str, Dict[str, Any]]) -> List[tuple]:
    """Find all skill references in the prompt.

    Args:
        prompt: User input
        registry: Skill registry mapping names to metadata

    Returns:
        List of (position, skill_name, args_start) tuples for found skills
    """
    references = []

    # Find all /word patterns
    for match in re.finditer(r'/(\w+)', prompt):
        skill_name = match.group(1)
        if skill_name in registry:
            references.append((match.start(), skill_name, match.end()))

    return references


def parse_continuation(prompt: str, registry: Dict[str, Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Parse prompt for continuation.

    Returns:
        None if no skill detected (pass-through)
        {
            "current": {"skill": str, "args": str},
            "continuation": [{"skill": str, "args": str}, ...]
        }
    """
    # Find all skill references
    references = find_skill_references(prompt, registry)

    if not references:
        # No skills found - pass through
        return None

    if len(references) == 1:
        # Mode 1: Single skill
        pos, skill_name, args_start = references[0]
        args = prompt[args_start:].strip()

        # Get default exit for this skill
        default_exit = registry[skill_name].get('default_exit', [])

        # Special case: /handoff without --commit flag is terminal
        if skill_name == 'handoff' and '--commit' not in args:
            default_exit = []

        # Build continuation entries from default exit
        continuation = []
        for exit_entry in default_exit:
            # Parse each default exit entry
            exit_match = re.match(r'/(\w+)(?:\s+(.*))?', exit_entry.strip())
            if exit_match:
                exit_skill = exit_match.group(1)
                exit_args = exit_match.group(2) or ''
                continuation.append({'skill': exit_skill, 'args': exit_args.strip()})

        return {
            'current': {'skill': skill_name, 'args': args},
            'continuation': continuation
        }

    # Multiple skills detected - check Mode 3 first (more specific)
    # Mode 3: Multi-line list pattern: "and\n- /skill"
    mode3_pattern = r'and\s*\n\s*-\s+/'
    if re.search(mode3_pattern, prompt):
        # Extract current skill (first reference)
        first_pos, first_skill, first_args_start = references[0]

        # Find where the "and" appears
        and_match = re.search(r'\s+and\s*\n', prompt[first_args_start:])
        if and_match:
            # Args for first skill are everything before "and"
            current_args = prompt[first_args_start:first_args_start + and_match.start()].strip()

            # Parse list items
            list_section = prompt[first_args_start + and_match.end():]
            continuation_entries = []

            for line in list_section.split('\n'):
                line = line.strip()
                if line.startswith('- /'):
                    # Parse skill and args from this line
                    skill_match = re.match(r'-\s+/(\w+)(?:\s+(.*))?', line)
                    if skill_match:
                        list_skill = skill_match.group(1)
                        list_args = skill_match.group(2) or ''
                        if list_skill in registry:
                            continuation_entries.append({
                                'skill': list_skill,
                                'args': list_args.strip()
                            })

            # Append default exit of last skill
            if continuation_entries:
                last_skill_name = continuation_entries[-1]['skill']
            else:
                last_skill_name = first_skill

            default_exit = registry[last_skill_name].get('default_exit', [])

            # Special case: /handoff without --commit in mid-chain
            if continuation_entries and last_skill_name == 'handoff':
                last_args = continuation_entries[-1]['args']
                if '--commit' not in last_args:
                    # Check if there are more entries after handoff in user's chain
                    # If yes, preserve them; if no, use empty default
                    # This is terminal only for solo /handoff, not mid-chain
                    pass  # User-specified continuation preserved
                else:
                    # Append commit for --commit flag
                    for exit_entry in default_exit:
                        exit_match = re.match(r'/(\w+)(?:\s+(.*))?', exit_entry.strip())
                        if exit_match:
                            continuation_entries.append({
                                'skill': exit_match.group(1),
                                'args': exit_match.group(2) or ''
                            })
            else:
                # Regular default exit appending
                for exit_entry in default_exit:
                    exit_match = re.match(r'/(\w+)(?:\s+(.*))?', exit_entry.strip())
                    if exit_match:
                        continuation_entries.append({
                            'skill': exit_match.group(1),
                            'args': exit_match.group(2) or ''
                        })

            return {
                'current': {'skill': first_skill, 'args': current_args},
                'continuation': continuation_entries
            }

    # Mode 2: Inline prose - delimiters: ", /" or connecting words before /
    continuation_entries = []
    current_skill = None
    current_args = None

    # Sort references by position
    sorted_refs = sorted(references, key=lambda x: x[0])

    for i, (pos, skill_name, args_start) in enumerate(sorted_refs):
        if i == 0:
            # First skill is the current one
            current_skill = skill_name

            # Find args for first skill - everything until next delimiter
            if i + 1 < len(sorted_refs):
                next_pos = sorted_refs[i + 1][0]
                # Find delimiter before next skill
                segment = prompt[args_start:next_pos]

                # Look for ", /" or connecting word pattern
                delimiter_match = re.search(r'(,\s*/|(?:\s+(?:and|then|finally)\s+/))', segment)
                if delimiter_match:
                    current_args = segment[:delimiter_match.start()].strip()
                else:
                    current_args = segment.strip()
            else:
                current_args = prompt[args_start:].strip()
        else:
            # Subsequent skills go into continuation
            if i + 1 < len(sorted_refs):
                next_pos = sorted_refs[i + 1][0]
                segment = prompt[args_start:next_pos]
                delimiter_match = re.search(r'(,\s*/|(?:\s+(?:and|then|finally)\s+/))', segment)
                if delimiter_match:
                    skill_args = segment[:delimiter_match.start()].strip()
                else:
                    skill_args = segment.strip()
            else:
                skill_args = prompt[args_start:].strip()

            continuation_entries.append({'skill': skill_name, 'args': skill_args})

    # Append default exit of last skill
    if continuation_entries:
        last_skill_name = continuation_entries[-1]['skill']
    else:
        last_skill_name = current_skill

    default_exit = registry.get(last_skill_name, {}).get('default_exit', [])

    # Special case: /handoff without --commit
    if last_skill_name == 'handoff':
        if continuation_entries:
            last_args = continuation_entries[-1]['args']
        else:
            last_args = current_args or ''

        if '--commit' not in last_args:
            # Mid-chain handoff: check if user specified more skills after
            # If this is the last skill in user's chain, it's terminal
            if not continuation_entries or continuation_entries[-1]['skill'] == 'handoff':
                default_exit = []

    # Append default exit
    for exit_entry in default_exit:
        exit_match = re.match(r'/(\w+)(?:\s+(.*))?', exit_entry.strip())
        if exit_match:
            continuation_entries.append({
                'skill': exit_match.group(1),
                'args': exit_match.group(2) or ''
            })

    return {
        'current': {'skill': current_skill, 'args': current_args},
        'continuation': continuation_entries
    }


def format_continuation_context(parsed: Dict[str, Any]) -> str:
    """Format parsed continuation as additionalContext string.

    Args:
        parsed: Parsed continuation dict with current and continuation

    Returns:
        Formatted prose instruction for Claude
    """
    current = parsed['current']
    continuation = parsed['continuation']

    # Format continuation list as comma-separated skill references
    cont_list = []
    for entry in continuation:
        if entry['args']:
            cont_list.append(f"/{entry['skill']} {entry['args']}")
        else:
            cont_list.append(f"/{entry['skill']}")

    cont_str = ', '.join(cont_list) if cont_list else '(empty - terminal)'

    # Build the instruction
    lines = [
        '[CONTINUATION-PASSING]',
        f"Current: /{current['skill']} {current['args']}".strip(),
        f"Continuation: {cont_str}",
        ''
    ]

    if continuation:
        # Provide next tail-call instruction
        next_entry = continuation[0]
        remainder = continuation[1:]

        remainder_str = ', '.join([
            f"/{e['skill']} {e['args']}".strip() if e['args'] else f"/{e['skill']}"
            for e in remainder
        ]) if remainder else ''

        if remainder_str:
            args_with_cont = f"{next_entry['args']} [CONTINUATION: {remainder_str}]".strip()
        else:
            args_with_cont = next_entry['args']

        lines.extend([
            'After completing the current skill, invoke the NEXT continuation entry via Skill tool:',
            f"  Skill(skill: \"{next_entry['skill']}\", args: \"{args_with_cont}\")",
            '',
            'Do NOT include continuation metadata in Task tool prompts.'
        ])
    else:
        # Terminal
        lines.extend([
            'Continuation is empty - this is a terminal skill.',
            'After completing the current skill, do NOT tail-call any other skill.'
        ])

    return '\n'.join(lines)


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

    # Tier 3: Continuation parsing
    try:
        registry = build_registry()
        parsed = parse_continuation(prompt, registry)

        if parsed:
            # Format and inject continuation
            context = format_continuation_context(parsed)
            output = {
                'hookSpecificOutput': {
                    'hookEventName': 'UserPromptSubmit',
                    'additionalContext': context
                }
            }
            print(json.dumps(output))
            return
    except Exception:
        # If continuation parsing fails, pass through silently
        pass

    # No match: silent pass-through
    sys.exit(0)


if __name__ == '__main__':
    main()
