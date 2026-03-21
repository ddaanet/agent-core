#!/usr/bin/env python3
"""Bump plugin.json version to match the given version string."""

import json
import sys
from pathlib import Path


def main() -> None:
    if len(sys.argv) != 2:  # noqa: PLR2004
        print("Usage: bump-plugin-version.py <version>", file=sys.stderr)
        sys.exit(1)

    version = sys.argv[1]
    plugin_json_path = Path(__file__).parent.parent / ".claude-plugin" / "plugin.json"

    if not plugin_json_path.exists():
        print(f"Error: {plugin_json_path} not found", file=sys.stderr)
        sys.exit(1)

    with plugin_json_path.open() as f:
        data = json.load(f)

    data["version"] = version

    with plugin_json_path.open("w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")

    print(f"Bumped plugin.json version to {version}")


if __name__ == "__main__":
    main()
