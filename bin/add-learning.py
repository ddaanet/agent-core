#!/usr/bin/env python3
"""
Add a learning to the pending learnings staging area.

Usage: python3 add-learning.py "slug" "learning content..."

Creates:
- agents/learnings/{date}-{slug}.md with content
- Appends @agents/learnings/{date}-{slug}.md to pending.md
"""

import sys
import os
from datetime import date
from pathlib import Path


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 add-learning.py <slug> <content>", file=sys.stderr)
        sys.exit(1)

    slug = sys.argv[1]
    content = sys.argv[2]

    # Get project root (2 levels up from bin/)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent

    # Create filename with date
    today = date.today().isoformat()
    filename = f"{today}-{slug}.md"
    learning_path = project_root / "agents" / "learnings" / filename
    pending_path = project_root / "agents" / "learnings" / "pending.md"

    # Ensure learnings directory exists
    learning_path.parent.mkdir(parents=True, exist_ok=True)

    # Write learning file
    learning_path.write_text(content)

    # Append to pending.md
    reference = f"@agents/learnings/{filename}"

    # Read pending.md to check if already exists
    if pending_path.exists():
        pending_content = pending_path.read_text()
        if reference not in pending_content:
            # Append to end
            with open(pending_path, 'a') as f:
                f.write(f"{reference}\n")
    else:
        # Create pending.md with reference
        pending_path.write_text(f"# Pending Learnings\n\n## Learnings\n\n{reference}\n")

    # Return filename for caller
    print(filename)


if __name__ == "__main__":
    main()
