#!/usr/bin/env python3
"""UserPromptSubmit hook: Expand workflow shortcuts.

Tier 1 - Commands (exact match on own line):
  s, x, xc, r, h, hc, ci, ?

Tier 2 - Directives (colon prefix, additive):
  d:, p:, b:, q:, learn: (and long-form aliases)

Tier 2.5 - Pattern guards (additive):
  skill-editing, CCG platform keywords

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
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore

# Tier 1: Command shortcuts (exact match)
COMMANDS = {
    "s": (
        "[#status] List pending tasks with metadata from session.md. "
        "Display in STATUS format. Wait for instruction."
    ),
    "x": (
        "[#execute] If in-progress task exists, resume it. "
        "Otherwise start first pending task from session.md. "
        "Complete the task, then stop. Do NOT commit or handoff."
    ),
    "xc": (
        "[execute, commit] Shorthand for execute then /handoff and /commit continuation chain. "
        "Complete task, then chain: handoff → commit → status display."
    ),
    "r": (
        "[#resume] Resume in-progress task using graduated lookup:\n"
        "1. Check conversation context — if in-progress task visible, resume directly.\n"
        "2. Read session.md — look for [>] or in-progress task.\n"
        "3. Check git status/diff — look for uncommitted work indicating active task.\n"
        "Report only if genuinely nothing to resume."
    ),
    "h": "[/handoff] Update session.md with current context, then display status.",
    "hc": (
        "[handoff, commit] Shorthand for /handoff then /commit continuation chain. "
        "Update session.md, then commit → status display."
    ),
    "ci": "[/commit] Commit changes → status display.",
    "?": (
        "[#help] List shortcuts (both tiers), "
        "keywords (y/go/continue), and entry skills "
        "(/design, /commit, /handoff, /orchestrate, /codify, /shelve, /review). "
        "Format as compact reference table."
    ),
}

# Tier 2: Directive shortcuts (colon prefix)
_DISCUSS_EXPANSION = (
    "[DISCUSS] Evaluate critically, do not execute.\n"
    "\n"
    "Form your assessment first, then stress-test it.\n"
    "Argue against your OWN position, not the proposal.\n"
    "\n"
    "State verdict explicitly: agree or disagree with reasons.\n"
    "Agreement with specific reasons is substantive. "
    "Reflexive disagreement is as harmful as reflexive agreement.\n"
    "\n"
    "The user's topic follows in their message."
)

_PENDING_EXPANSION = (
    "[PENDING] Do NOT execute. Do NOT write to session.md now.\n"
    "\n"
    "Assess model tier: "
    "opus (design/architecture/synthesis), "
    "sonnet (implementation/planning), "
    "haiku (mechanical/repetitive).\n"
    "\n"
    "Respond: task name, model tier with reasoning, "
    "restart flag if needed. "
    "Task written to session.md during next handoff."
)

_BRAINSTORM_EXPANSION = (
    "[BRAINSTORM] Generate options, do not narrow down.\n"
    "\n"
    "diverge: produce multiple alternatives, ideas, or approaches.\n"
    "Do not evaluate, rank, or eliminate options (no ranking, no selection).\n"
    "Defer judgment — the user will evaluate separately."
)

_QUICK_EXPANSION = (
    "[QUICK] Terse response, no ceremony.\n"
    "\n"
    "Answer directly — no preamble, no framing, no hedging.\n"
    "No follow-up suggestions.\n"
    "Stop when the answer is complete."
)

_LEARN_EXPANSION = (
    "[LEARN] Append to agents/learnings.md.\n"
    "\n"
    "Format: H2 heading (When <situation>), then:\n"
    "- Anti-pattern: what was done wrong\n"
    "- Correct pattern: what to do instead\n"
    "- Rationale or evidence\n"
    "\n"
    "Check line count after appending (soft limit: 80 lines)."
)

DIRECTIVES = {
    "d": _DISCUSS_EXPANSION,
    "discuss": _DISCUSS_EXPANSION,
    "p": _PENDING_EXPANSION,
    "pending": _PENDING_EXPANSION,
    "b": _BRAINSTORM_EXPANSION,
    "brainstorm": _BRAINSTORM_EXPANSION,
    "q": _QUICK_EXPANSION,
    "question": _QUICK_EXPANSION,
    "learn": _LEARN_EXPANSION,
}

# Built-in skills fallback (empty initially — all cooperative skills are project-local or plugin-based)
BUILTIN_SKILLS: dict[str, Any] = {}

# Tier 2.5: Pattern guard regex constants
_EDIT_VERBS = r"(?:fix|edit|update|improve|change|modify|rewrite|refactor)"
_SKILL_NOUNS = r"(?:skill|agent|plugin|hook)"
EDIT_SKILL_PATTERN = re.compile(
    rf"(?:{_EDIT_VERBS}\b.*\b{_SKILL_NOUNS}|\b{_SKILL_NOUNS}\b.*\b{_EDIT_VERBS})",
    re.IGNORECASE,
)
EDIT_SLASH_PATTERN = re.compile(
    rf"\b{_EDIT_VERBS}\b.*\s/\w+",
    re.IGNORECASE,
)
CCG_PATTERN = re.compile(
    r"\b(?:hooks?|PreToolUse|PostToolUse|SessionStart|UserPromptSubmit"
    r"|mcp\s+server|slash\s+command|settings\.json|\.claude/|plugin\.json"
    r"|keybinding|IDE\s+integration|agent\s+sdk)\b",
    re.IGNORECASE,
)


def is_line_in_fence(lines: list[str], line_idx: int) -> bool:
    """Check if a line is inside a fenced code block.

    Tracks fence depth while scanning from start to line_idx.
    Opening fence: 3+ consecutive backticks or tildes at line start.
    Closing fence: same character, same or greater count.

    Args:
        lines: List of text lines
        line_idx: Index of line to check

    Returns:
        True if line is inside or part of a fence, False otherwise
    """
    if line_idx >= len(lines):
        return False

    fence_char = None  # Current fence character (` or ~)
    fence_count = 0  # Minimum count for closing fence
    in_fence = False

    for i in range(line_idx + 1):
        line = lines[i]
        stripped = line.strip()

        # Check for fence markers (3+ backticks or tildes at start)
        if stripped.startswith(("```", "~~~")):
            # Determine fence character
            char = stripped[0]

            # Count consecutive fence characters
            count = 0
            for c in stripped:
                if c == char:
                    count += 1
                else:
                    break

            if count >= 3:
                if not in_fence:
                    # Opening fence
                    fence_char = char
                    fence_count = count
                    in_fence = True
                    # If this is the line we're checking, it's part of the fence
                    if i == line_idx:
                        return True
                elif char == fence_char and count >= fence_count:
                    # Closing fence (same char, same or greater count)
                    # If this is the line we're checking, it's part of the fence
                    if i == line_idx:
                        return True
                    fence_char = None
                    fence_count = 0
                    in_fence = False

    return in_fence


def scan_for_directives(prompt: str) -> list[tuple[str, str]]:
    """Scan prompt for all directive matches, returning each with its section
    content.

    Section content spans from the directive line to the next directive line
    (exclusive) or end of prompt. Directive lines inside fenced blocks are
    skipped.

    Returns list of (directive_key, section_content) tuples in order of
    appearance.
    """
    lines = prompt.split("\n")
    fence_char = None
    fence_count = 0
    in_fence = False

    # First pass: find all non-fenced directive line indices and their keys
    directive_lines: list[tuple[int, str, str]] = []  # (line_idx, key, first_value)
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith(("```", "~~~")):
            char = stripped[0]
            count = 0
            for c in stripped:
                if c == char:
                    count += 1
                else:
                    break
            if count >= 3:
                if not in_fence:
                    fence_char = char
                    fence_count = count
                    in_fence = True
                    continue
                if char == fence_char and count >= fence_count:
                    fence_char = None
                    fence_count = 0
                    in_fence = False
                    continue
        if in_fence:
            continue
        match = re.match(r"^(\w+):\s+(.+)", line)
        if match:
            key = match.group(1)
            if key in DIRECTIVES:
                directive_lines.append((i, key, match.group(2)))

    if not directive_lines:
        return []

    # Second pass: build section content for each directive
    # Section spans from directive line through lines before next directive (or end)
    results: list[tuple[str, str]] = []
    for idx, (line_i, key, first_value) in enumerate(directive_lines):
        next_directive_line = (
            directive_lines[idx + 1][0]
            if idx + 1 < len(directive_lines)
            else len(lines)
        )
        section_lines = [first_value, *lines[line_i + 1 : next_directive_line]]
        section_content = "\n".join(section_lines).strip()
        results.append((key, section_content))

    return results


def extract_frontmatter(skill_path: Path) -> dict[str, Any] | None:
    """Extract YAML frontmatter from a SKILL.md file.

    Returns:
        Parsed frontmatter dict, or None if no frontmatter or parse error
    """
    if not yaml:
        return None

    try:
        with open(skill_path, encoding="utf-8") as f:
            content = f.read()

        # Check for YAML frontmatter (--- at start)
        if not content.startswith("---\n"):
            return None

        # Find closing ---
        end_match = re.search(r"\n---\n", content[4:])
        if not end_match:
            return None

        frontmatter_text = content[4 : 4 + end_match.start()]
        return yaml.safe_load(frontmatter_text)
    except Exception:
        # Skip malformed files
        return None


def get_enabled_plugins() -> list[str]:
    """Get list of enabled plugins from settings.json.

    Returns:
        List of enabled plugin names (empty if no settings or no plugins)
    """
    settings_path = Path.home() / ".claude" / "settings.json"
    if not settings_path.exists():
        return []

    try:
        with open(settings_path, encoding="utf-8") as f:
            settings = json.load(f)
        return settings.get("enabledPlugins", [])
    except Exception:
        return []


def get_plugin_install_path(plugin_name: str, project_dir: str) -> str | None:
    """Resolve plugin install path from installed_plugins.json.

    Args:
        plugin_name: Name of the plugin
        project_dir: Current project directory (for scope filtering)

    Returns:
        Install path if plugin is enabled for this project, None otherwise
    """
    installed_path = Path.home() / ".claude" / "plugins" / "installed_plugins.json"
    if not installed_path.exists():
        return None

    try:
        with open(installed_path, encoding="utf-8") as f:
            installed = json.load(f)

        plugin_info = installed.get(plugin_name)
        if not plugin_info:
            return None

        # Check scope filtering
        scope = plugin_info.get("scope", "user")
        if scope == "project":
            # Only include if projectPath matches current project
            if plugin_info.get("projectPath") != project_dir:
                return None

        return plugin_info.get("installPath")
    except Exception:
        return None


def scan_skill_files(base_path: Path) -> list[Path]:
    """Scan for SKILL.md files under a base path.

    Args:
        base_path: Directory to scan recursively

    Returns:
        List of SKILL.md file paths
    """
    if not base_path.exists():
        return []

    pattern = str(base_path / "**" / "SKILL.md")
    return [Path(p) for p in glob.glob(pattern, recursive=True)]


def get_cache_path(paths: list[str], project_dir: str) -> Path:
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
    hash_input = "".join(sorted_paths) + project_dir
    hash_digest = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()[:16]

    # Use TMPDIR from environment, fall back to /tmp/claude
    tmp_dir = os.environ.get("TMPDIR", "/tmp/claude")
    cache_dir = Path(tmp_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)

    return cache_dir / f"continuation-registry-{hash_digest}.json"


def get_cached_registry(cache_path: Path) -> dict[str, Any] | None:
    """Load registry from cache if valid.

    Args:
        cache_path: Path to cache file

    Returns:
        Cached registry dict if valid, None if cache invalid or missing
    """
    if not cache_path.exists():
        return None

    try:
        with open(cache_path, encoding="utf-8") as f:
            cache_data = json.load(f)

        # Validate cache structure
        if (
            "paths" not in cache_data
            or "registry" not in cache_data
            or "timestamp" not in cache_data
        ):
            return None

        cache_timestamp = cache_data["timestamp"]

        # Check if any source file modified since cache
        for path_str in cache_data["paths"]:
            path = Path(path_str)
            if not path.exists():
                # Source file deleted, invalidate cache
                return None

            if path.stat().st_mtime > cache_timestamp:
                # File modified, invalidate cache
                return None

        return cache_data["registry"]
    except Exception:
        # Cache corrupted or unreadable
        return None


def save_registry_cache(
    registry: dict[str, Any], paths: list[str], cache_path: Path
) -> None:
    """Save registry to cache.

    Args:
        registry: Registry dict to cache
        paths: List of skill file paths
        cache_path: Path to cache file
    """
    try:
        cache_data = {"paths": paths, "registry": registry, "timestamp": time.time()}

        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(cache_data, f)
    except Exception:
        # If caching fails, continue in degraded mode
        pass


def build_registry() -> dict[str, dict[str, Any]]:
    """Build registry of cooperative skills from all sources.

    Uses caching for performance. Cache is invalidated when skill files are modified.

    Returns:
        Dictionary mapping skill names to continuation metadata:
        {
            "design": {
                "cooperative": True,
                "default-exit": ["/handoff --commit", "/commit"]
            },
            ...
        }
    """
    # Get project directory
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", "")
    if not project_dir:
        return {}

    project_path = Path(project_dir)

    # Collect all skill file paths for cache key generation
    all_paths: list[str] = []
    registry: dict[str, dict[str, Any]] = {}

    # 1. Scan project-local skills
    project_skills_path = project_path / ".claude" / "skills"
    project_skill_files = scan_skill_files(project_skills_path)
    all_paths.extend([str(p) for p in project_skill_files])

    # 2. Scan enabled plugin skills
    plugin_skill_files: list[Path] = []
    enabled_plugins = get_enabled_plugins()
    for plugin_name in enabled_plugins:
        install_path = get_plugin_install_path(plugin_name, project_dir)
        if not install_path:
            continue

        plugin_path = Path(install_path)
        skills_path = plugin_path / "skills"
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

        continuation = frontmatter.get("continuation", {})
        if not continuation.get("cooperative"):
            continue

        # Extract skill name from frontmatter or directory name
        skill_name = frontmatter.get("name")
        if not skill_name:
            # Use parent directory name
            skill_name = skill_file.parent.name

        registry[skill_name] = {
            "cooperative": True,
            "default-exit": continuation.get("default-exit", []),
        }

    # Process plugin skills
    for skill_file in plugin_skill_files:
        frontmatter = extract_frontmatter(skill_file)
        if not frontmatter:
            continue

        continuation = frontmatter.get("continuation", {})
        if not continuation.get("cooperative"):
            continue

        skill_name = frontmatter.get("name")
        if not skill_name:
            skill_name = skill_file.parent.name

        registry[skill_name] = {
            "cooperative": True,
            "default-exit": continuation.get("default-exit", []),
        }

    # 3. Add built-in skills
    registry.update(BUILTIN_SKILLS)

    # Save to cache
    save_registry_cache(registry, all_paths, cache_path)

    return registry


def _is_line_prefixed_note(prompt: str, pos: int) -> bool:
    """Check if skill reference is on a line starting with 'note:'.

    Args:
        prompt: User input
        pos: Position of skill reference

    Returns:
        True if line starts with 'note:' (case-insensitive)
    """
    # Find start of current line
    line_start = prompt.rfind("\n", 0, pos)
    if line_start == -1:
        line_start = 0
    else:
        line_start += 1  # Move past the newline

    # Get line content up to position
    line_prefix = prompt[line_start:pos].strip().lower()

    # Check if line starts with "note:"
    return line_prefix.startswith("note:")


def _should_exclude_reference(prompt: str, pos: int, skill_name: str) -> bool:
    """Determine if skill reference should be excluded from parsing.

    Simplified approach matching Claude CLI behavior:
    - Only match /skill when preceded by whitespace or at line start
    - Exclude file path patterns (/word-word/, /word/)
    - Exclude lines prefixed with "note:"

    Args:
        prompt: User input
        pos: Position of skill reference
        skill_name: Detected skill name

    Returns:
        True if reference should be EXCLUDED (false positive context).
        False if reference is a valid invocation (should be parsed).
    """
    # 1. Primary filter: Only match when preceded by whitespace or at line start
    # This aligns with Claude CLI behavior and handles most false positives:
    # - Quoted references: "/skill" (preceded by quote, not whitespace)
    # - File paths: plans/skill/ (preceded by letter, not whitespace)
    # - Mid-word: foo/bar (preceded by letter, not whitespace)
    if pos > 0 and not prompt[pos - 1].isspace():
        return True  # Not preceded by whitespace - exclude

    # 2. File path check: Exclude /skill-word/ or /skill/ patterns
    # These indicate directory paths, not skill invocations
    skill_end = pos + len(skill_name) + 1  # +1 for the '/'
    if skill_end < len(prompt):
        next_char = prompt[skill_end]
        # Check if followed by '-' or '/' (path continuation)
        if next_char in ("-", "/"):
            return True

    # 3. Exclude lines prefixed with "note:" (meta-discussion marker)
    if _is_line_prefixed_note(prompt, pos):
        return True

    # If we reach here, this is a valid invocation
    return False


def find_skill_references(
    prompt: str, registry: dict[str, dict[str, Any]]
) -> list[tuple]:
    """Find all skill references in the prompt with context-aware filtering.

    Filters out false positives:
    - XML/structured output contexts
    - Meta-discussion (prose mentions of skills)
    - File paths

    Args:
        prompt: User input
        registry: Skill registry mapping names to metadata

    Returns:
        List of (position, skill_name, args_start) tuples for valid invocations
    """
    references = []

    for match in re.finditer(r"/(\w+)", prompt):
        skill_name = match.group(1)
        if skill_name not in registry:
            continue

        pos = match.start()

        # Context filtering
        if _should_exclude_reference(prompt, pos, skill_name):
            continue

        references.append((pos, skill_name, match.end()))

    return references


def parse_continuation(
    prompt: str, registry: dict[str, dict[str, Any]]
) -> dict[str, Any] | None:
    """Parse prompt for multi-skill continuation chains.

    Only activates when multiple skills are present (continuation patterns).
    Single skill invocations pass through — Claude's skill system handles them,
    and skills manage their own default-exit logic.

    Returns:
        None if no continuation detected (pass-through)
        {
            "current": {"skill": str, "args": str},
            "continuation": [{"skill": str, "args": str}, ...]
        }
    """
    # Find all skill references
    references = find_skill_references(prompt, registry)

    if len(references) <= 1:
        # No skills or single skill — pass through
        # Single skills are handled by Claude's built-in skill system.
        # Skills manage their own default-exit (standalone or last-in-chain).
        return None

    # Multiple skills detected - check Mode 3 first (more specific)
    # Mode 3: Multi-line list pattern: "and\n- /skill"
    mode3_pattern = r"and\s*\n\s*-\s+/"
    if re.search(mode3_pattern, prompt):
        # Extract current skill (first reference)
        _first_pos, first_skill, first_args_start = references[0]

        # Find where the "and" appears
        and_match = re.search(r"\s+and\s*\n", prompt[first_args_start:])
        if and_match:
            # Args for first skill are everything before "and"
            current_args = prompt[
                first_args_start : first_args_start + and_match.start()
            ].strip()

            # Parse list items
            list_section = prompt[first_args_start + and_match.end() :]
            continuation_entries = []

            for line in list_section.split("\n"):
                line = line.strip()
                if line.startswith("- /"):
                    # Parse skill and args from this line
                    skill_match = re.match(r"-\s+/(\w+)(?:\s+(.*))?", line)
                    if skill_match:
                        list_skill = skill_match.group(1)
                        list_args = skill_match.group(2) or ""
                        if list_skill in registry:
                            continuation_entries.append(
                                {"skill": list_skill, "args": list_args.strip()}
                            )

            return {
                "current": {"skill": first_skill, "args": current_args},
                "continuation": continuation_entries,
            }

    # Mode 2: Inline prose - delimiters: ", /" or connecting words before /
    continuation_entries = []
    current_skill = None
    current_args = None

    # Sort references by position
    sorted_refs = sorted(references, key=lambda x: x[0])

    for i, (_pos, skill_name, args_start) in enumerate(sorted_refs):
        if i == 0:
            # First skill is the current one
            current_skill = skill_name

            # Find args for first skill - everything until next delimiter
            if i + 1 < len(sorted_refs):
                next_pos = sorted_refs[i + 1][0]
                # Find delimiter before next skill
                segment = prompt[args_start:next_pos]

                # Look for ", /" or connecting word pattern
                delimiter_match = re.search(
                    r"(,\s*/|(?:\s+(?:and|then|finally)\s+/))", segment
                )
                if delimiter_match:
                    current_args = segment[: delimiter_match.start()].strip()
                else:
                    current_args = segment.strip()
            else:
                current_args = prompt[args_start:].strip()
        else:
            # Subsequent skills go into continuation
            if i + 1 < len(sorted_refs):
                next_pos = sorted_refs[i + 1][0]
                segment = prompt[args_start:next_pos]
                delimiter_match = re.search(
                    r"(,\s*/|(?:\s+(?:and|then|finally)\s+/))", segment
                )
                if delimiter_match:
                    skill_args = segment[: delimiter_match.start()].strip()
                else:
                    skill_args = segment.strip()
            else:
                skill_args = prompt[args_start:].strip()

            continuation_entries.append({"skill": skill_name, "args": skill_args})

    return {
        "current": {"skill": current_skill, "args": current_args},
        "continuation": continuation_entries,
    }


def format_continuation_context(parsed: dict[str, Any]) -> str:
    """Format parsed continuation as additionalContext string.

    Args:
        parsed: Parsed continuation dict with current and continuation

    Returns:
        Formatted prose instruction for Claude
    """
    current = parsed["current"]
    continuation = parsed["continuation"]

    # Format continuation list as comma-separated skill references
    cont_list = []
    for entry in continuation:
        if entry["args"]:
            cont_list.append(f"/{entry['skill']} {entry['args']}".strip())
        else:
            cont_list.append(f"/{entry['skill']}")

    cont_str = ", ".join(cont_list) if cont_list else "(empty - terminal)"

    # Build the instruction
    lines = [
        "[CONTINUATION-PASSING]",
        f"Current: /{current['skill']} {current['args']}".strip(),
        f"Continuation: {cont_str}",
        "",
    ]

    if continuation:
        # Provide next tail-call instruction
        next_entry = continuation[0]
        remainder = continuation[1:]

        remainder_str = (
            ", ".join(
                [
                    f"/{e['skill']} {e['args']}".strip()
                    if e["args"]
                    else f"/{e['skill']}"
                    for e in remainder
                ]
            )
            if remainder
            else ""
        )

        if remainder_str:
            args_with_cont = (
                f"{next_entry['args']} [CONTINUATION: {remainder_str}]".strip()
            )
        else:
            args_with_cont = next_entry["args"]

        lines.extend(
            [
                "After completing the current skill, invoke the NEXT continuation entry via Skill tool:",
                f'  Skill(skill: "{next_entry["skill"]}", args: "{args_with_cont}")',
                "",
                "Do NOT include continuation metadata in Task tool prompts.",
            ]
        )
    else:
        # Terminal
        lines.extend(
            [
                "Continuation is empty - this is a terminal skill.",
                "After completing the current skill, do NOT tail-call any other skill.",
            ]
        )

    return "\n".join(lines)


def main() -> None:
    """Expand workflow shortcuts in user prompts."""
    # Read hook input
    hook_input = json.load(sys.stdin)
    prompt = hook_input.get("prompt", "").strip()

    # Tier 1: Command on its own line (first matching line wins)
    lines = prompt.split("\n")
    is_single_line = len(lines) == 1
    for line in lines:
        stripped = line.strip()
        if stripped in COMMANDS:
            expansion = COMMANDS[stripped]
            output: dict[str, Any] = {
                "hookSpecificOutput": {
                    "hookEventName": "UserPromptSubmit",
                    "additionalContext": expansion,
                }
            }
            # Single-line exact match gets systemMessage; multi-line avoids noisy status bar
            if is_single_line:
                output["systemMessage"] = expansion
            print(json.dumps(output))
            return

    # Tier 2: Directive pattern — additive, all matching directives fire (D-7)
    directive_matches = scan_for_directives(prompt)
    context_parts: list[str] = []
    system_parts: list[str] = []
    if directive_matches:
        for directive_key, _section in directive_matches:
            expansion = DIRECTIVES[directive_key]
            context_parts.append(expansion)
            if directive_key in ("d", "discuss"):
                system_parts.append("[DISCUSS] Evaluate critically, do not execute.")
            elif directive_key in ("p", "pending"):
                system_parts.append("[PENDING] Capture task, do not execute.")
            elif directive_key in ("b", "brainstorm"):
                system_parts.append("[BRAINSTORM] Generate options, do not converge.")
            elif directive_key in ("q", "question"):
                system_parts.append("[QUICK] Terse response, no ceremony.")
            elif directive_key == "learn":
                system_parts.append("[LEARN] Append to learnings.")
            else:
                system_parts.append(expansion)

    # Tier 2.5: Pattern guards — additionalContext only, additive with Tier 2
    if EDIT_SKILL_PATTERN.search(prompt) or EDIT_SLASH_PATTERN.search(prompt):
        context_parts.append(
            "Load /plugin-dev:skill-development before editing skill files. "
            "Load /plugin-dev:agent-development before editing agent files. "
            "Skill descriptions require 'This skill should be used when...' format."
        )
    if CCG_PATTERN.search(prompt):
        context_parts.append(
            "Platform question detected. Use claude-code-guide agent "
            "(subagent_type='claude-code-guide') for authoritative Claude Code documentation."
        )

    # Directives change interaction mode — output Tier 2 + 2.5, skip Tier 3
    if directive_matches and context_parts:
        combined_context = "\n\n".join(context_parts)
        output: dict[str, Any] = {
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": combined_context,
            }
        }
        if system_parts:
            output["systemMessage"] = " | ".join(system_parts)
        print(json.dumps(output))
        return

    # Tier 3: Continuation parsing — combines with Tier 2.5 guards
    try:
        registry = build_registry()
        parsed = parse_continuation(prompt, registry)
        if parsed:
            context_parts.append(format_continuation_context(parsed))
    except Exception:
        pass

    if context_parts:
        combined_context = "\n\n".join(context_parts)
        output: dict[str, Any] = {
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": combined_context,
            }
        }
        print(json.dumps(output))
        return

    # No match: silent pass-through
    sys.exit(0)


if __name__ == "__main__":
    main()
