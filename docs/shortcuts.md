# Workflow Shortcuts

Quick reference for all shortcuts, keywords, and entry points.

## Command Shortcuts

Type alone as entire message. Expanded by UserPromptSubmit hook.

| Input | Action |
|-------|--------|
| `s` | Show pending tasks (STATUS), wait |
| `x` | Smart execute: resume in-progress or start first pending |
| `xc` | Execute → handoff → commit → status |
| `r` | Strict resume (error if nothing in-progress) |
| `h` | Handoff (update session.md) → status |
| `hc` | Handoff → commit → status |
| `ci` | Commit → status |
| `?` | List shortcuts, keywords, and entry skills |

## Directive Shortcuts

Colon prefix with argument. `shortcut: text`

| Input | Action |
|-------|--------|
| `d: <text>` | Discussion mode — analyze only, don't execute |
| `p: <text>` | Record pending task in session.md, don't execute |

## Workflow Keywords

Natural language — no hook expansion needed, Claude understands directly.

| Input | Meaning |
|-------|---------|
| `y`, `yes`, `go`, `g` | Confirm / proceed |
| `continue`, `c` | Continue current work |
| `n`, `no` | Decline / stop |

## Entry Point Skills

| Skill | Purpose |
|-------|---------|
| `/design` | Entry point for implementation tasks (triages complexity) |
| `/commit` | Commit with gitmoji, structured message |
| `/handoff` | Update session.md for agent continuation |
| `/orchestrate` | Execute prepared runbooks |
| `/runbook` | Create execution runbook (unified — TDD + general phases) |
| `/remember` | Consolidate learnings into permanent docs |
| `/shelve` | Archive session context, reset for new work |
| `/vet` | Review artifacts for quality |

## How It Works

**Two layers:**
- **Hook** (`userpromptsubmit-shortcuts.py`): Mechanical expansion for standalone shortcuts. Exact match for commands, regex for directives.
- **Fragment** (`execute-rule.md`): Vocabulary table loaded via CLAUDE.md. Agent understands shortcuts inline in natural language ("design this then hc").

Hook handles bare shortcuts reliably. Fragment handles inline comprehension.
