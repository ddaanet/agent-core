#!/usr/bin/env python3
"""Check that plugin.json version matches pyproject.toml version."""

import json
import sys
from pathlib import Path


def main() -> None:
    repo_root = Path(__file__).parent.parent.parent
    plugin_json_path = repo_root / "agent-core" / ".claude-plugin" / "plugin.json"
    pyproject_path = repo_root / "pyproject.toml"

    # Read plugin.json version
    if not plugin_json_path.exists():
        print(f"Error: {plugin_json_path} not found", file=sys.stderr)
        sys.exit(1)
    with plugin_json_path.open() as f:
        plugin_data = json.load(f)
    plugin_version = plugin_data.get("version")
    if not plugin_version:
        print("Error: 'version' field missing from plugin.json", file=sys.stderr)
        sys.exit(1)

    # Read pyproject.toml version (simple line scan — avoids tomllib version requirements)
    if not pyproject_path.exists():
        print(f"Error: {pyproject_path} not found", file=sys.stderr)
        sys.exit(1)
    pyproject_version = None
    in_project_section = False
    with pyproject_path.open() as f:
        for line in f:
            stripped = line.strip()
            if stripped == "[project]":
                in_project_section = True
                continue
            if in_project_section and stripped.startswith("["):
                in_project_section = False
            if in_project_section and stripped.startswith("version"):
                _, _, raw = stripped.partition("=")
                pyproject_version = raw.strip().strip('"').strip("'")
                break

    if pyproject_version is None:
        print(
            "Error: 'version' field not found in [project] section of pyproject.toml",
            file=sys.stderr,
        )
        sys.exit(1)

    if plugin_version != pyproject_version:
        print(
            f"Version mismatch: plugin.json={plugin_version}, pyproject.toml={pyproject_version}",
            file=sys.stderr,
        )
        print("Run: just release (or manually sync versions)", file=sys.stderr)
        sys.exit(1)

    print(f"Version consistent: {plugin_version}")


if __name__ == "__main__":
    main()
