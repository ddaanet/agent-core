#\!/usr/bin/env python3
"""
UserPromptSubmit hook: Expand workflow shortcuts.

Tier 1 - Commands (exact match, entire message):
  s, x, xc, r, h, hc, ci

Tier 2 - Directives (colon prefix):
  d:, p:

No match: silent pass-through (exit 0, no output)
"""

import json
import re
import sys

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
    'ci': '[SHORTCUT: /commit] Commit changes → status display.'
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
