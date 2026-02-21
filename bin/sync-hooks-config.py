#!/usr/bin/env python3
"""Merge agent-core/hooks/hooks.json into .claude/settings.json.

Idempotent: deduplicates by command string. Preserves existing hooks.
"""

import json
import os
import sys
from pathlib import Path


def find_settings_path():
    """Find .claude/settings.json — use CLAUDE_PROJECT_DIR or parent of agent-
    core."""
    env_dir = os.environ.get("CLAUDE_PROJECT_DIR")
    if env_dir:
        return Path(env_dir) / ".claude" / "settings.json"
    script_dir = Path(__file__).parent
    return script_dir.parent.parent / ".claude" / "settings.json"


def find_hooks_path():
    """Find agent-core/hooks/hooks.json."""
    script_dir = Path(__file__).parent
    return script_dir.parent / "hooks" / "hooks.json"


def load_json(path):
    """Load JSON file, exit 1 on error."""
    if not path.exists():
        print(f"Error: {path.name} not found at {path}", file=sys.stderr)
        sys.exit(1)
    try:
        with open(path) as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error parsing {path}: {e}", file=sys.stderr)
        sys.exit(1)


def get_command_string(hook_entry):
    """Extract command string from hook entry for dedup comparison."""
    if isinstance(hook_entry, dict) and hook_entry.get("type") == "command":
        return hook_entry.get("command")
    return None


def merge_hooks(settings, hooks_config):
    """Merge hooks.json into settings.json, deduplicating by command string.

    Args:
        settings: Current settings.json content
        hooks_config: hooks.json content

    Returns:
        Updated settings dict
    """
    if "hooks" not in settings:
        settings["hooks"] = {}

    for event_key, hooks_list in hooks_config.items():
        if event_key not in settings["hooks"]:
            settings["hooks"][event_key] = []

        existing_hooks = settings["hooks"][event_key]

        for new_entry in hooks_list:
            matcher = new_entry.get("matcher")

            if matcher is None:
                matching_entry_idx = None
                for i, entry in enumerate(existing_hooks):
                    if entry.get("matcher") is None:
                        matching_entry_idx = i
                        break

                if matching_entry_idx is None:
                    existing_hooks.append(new_entry)
                else:
                    existing_entry = existing_hooks[matching_entry_idx]
                    existing_commands = {
                        get_command_string(h) for h in existing_entry.get("hooks", [])
                    }

                    for new_hook in new_entry.get("hooks", []):
                        cmd = get_command_string(new_hook)
                        if cmd not in existing_commands:
                            existing_entry["hooks"].append(new_hook)

            else:
                matching_entry_idx = None
                for i, entry in enumerate(existing_hooks):
                    if entry.get("matcher") == matcher:
                        matching_entry_idx = i
                        break

                if matching_entry_idx is None:
                    existing_hooks.append(new_entry)
                else:
                    existing_entry = existing_hooks[matching_entry_idx]
                    existing_commands = {
                        get_command_string(h) for h in existing_entry.get("hooks", [])
                    }

                    for new_hook in new_entry.get("hooks", []):
                        cmd = get_command_string(new_hook)
                        if cmd not in existing_commands:
                            existing_entry["hooks"].append(new_hook)

    return settings


def write_json(path, data) -> None:
    """Write JSON file with indent=2, exit 1 on error."""
    try:
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
            f.write("\n")
    except Exception as e:
        print(f"Error writing {path}: {e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    settings_path = find_settings_path()
    hooks_path = find_hooks_path()

    settings = load_json(settings_path)
    hooks_config = load_json(hooks_path)

    merged = merge_hooks(settings, hooks_config)
    write_json(settings_path, merged)


if __name__ == "__main__":
    main()
