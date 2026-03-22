#!/usr/bin/env python3
"""Bump plugin.json and sessionstart-health.sh versions to match the given
version string."""

import json
import re
import sys
from pathlib import Path


def main() -> None:
    if len(sys.argv) != 2:  # noqa: PLR2004
        print("Usage: bump-plugin-version.py <version>", file=sys.stderr)
        sys.exit(1)

    version = sys.argv[1]
    agent_core = Path(__file__).parent.parent

    # Bump plugin.json
    plugin_json_path = agent_core / ".claude-plugin" / "plugin.json"
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

    # Bump EDIFY_VERSION in sessionstart-health.sh
    health_sh = agent_core / "hooks" / "sessionstart-health.sh"
    if health_sh.exists():
        content = health_sh.read_text()
        updated = re.sub(
            r'^(\s*EDIFY_VERSION=)"[^"]*"',
            rf'\1"{version}"',
            content,
            count=1,
            flags=re.MULTILINE,
        )
        if updated != content:
            health_sh.write_text(updated)
            print(f"Bumped EDIFY_VERSION in sessionstart-health.sh to {version}")
        else:
            print(
                "Warning: EDIFY_VERSION pattern not found in sessionstart-health.sh",
                file=sys.stderr,
            )
            sys.exit(1)


if __name__ == "__main__":
    main()
