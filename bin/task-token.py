#!/usr/bin/env python3
"""Replace #PNDNG placeholders in session.md with unique base62 tokens.

Only replaces on task lines (starting with '- [ ]') to avoid mangling
prose that mentions the placeholder literally.
"""

import random
import re
import string
import sys

CHARSET = string.ascii_letters + string.digits
TOKEN_LEN = 5
PLACEHOLDER = "#PNDNG"


def generate_token():
    return "#" + "".join(random.choices(CHARSET, k=TOKEN_LEN))


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "agents/session.md"

    try:
        with open(path) as f:
            lines = f.readlines()
    except FileNotFoundError:
        return

    count = 0
    for i, line in enumerate(lines):
        if re.match(r"^- \[[ x>]\]", line) and PLACEHOLDER in line:
            lines[i] = line.replace(PLACEHOLDER, generate_token(), 1)
            count += 1

    if count == 0:
        return

    with open(path, "w") as f:
        f.writelines(lines)

    print(f"Replaced {count} placeholder(s)", file=sys.stderr)


if __name__ == "__main__":
    main()
