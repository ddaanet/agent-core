#!/usr/bin/env python3
"""CLI wrapper for compress_key functionality."""

import sys
from pathlib import Path

from claudeutils.when.compress import compress_key, load_heading_corpus


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: compress-key.py <heading> [decisions-dir]", file=sys.stderr)
        sys.exit(1)

    heading = sys.argv[1]
    decisions_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path.cwd() / "agents" / "decisions"

    corpus = load_heading_corpus(decisions_dir)
    result = compress_key(heading, corpus)
    print(result)


if __name__ == "__main__":
    main()
