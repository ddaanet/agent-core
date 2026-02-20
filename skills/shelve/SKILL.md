---
name: shelve
description: Archive session context to todo list and reset for new work
allowed-tools: Read, Write, Edit, Bash(mkdir:*), Bash(cp:*)
user-invocable: true
---

# Archive Session Context

Archive current session context to todo list and reset session file for new work.

## When to Use

**Use this skill when:**
- Switching to unrelated work within the same project
- Completing a project phase and starting a new one
- Current work needs to be paused and documented for later

**Ask user for approval before running.**

## Execution Steps

### 1. Gather Input

Ask user for:
- **Name/topic**: Natural language description (e.g., "unification", "auth-refactor")

### 2. Read Current Files

Read the following files:
- `agents/session.md`
- `agents/todo.md` (to prepend to)

### 3. Create Shelf Directory

```bash
mkdir -p agents/shelf
```

### 4. Archive to Shelf

Archive to `agents/shelf/<name>-session.md` with metadata header:

```markdown
---
archived: YYYY-MM-DD
topic: <name>
reason: <brief description from user input>
---

# Archived Session: <name>

<original session.md content>
```

### 5. Update todo.md

Prepend to `agents/todo.md` after the "## Backlog" header:

```markdown
## Backlog

### YYYY-MM-DD - Session: <name>

<session.md content>

---
```

### 6. Reset Files

**Reset session.md:**

```bash
cp .claude/skills/shelve/templates/session.md agents/session.md
```

### 7. Report Results

Report to user:
- Where session was archived to (`agents/shelf/<name>-session.md`)
- Session file reset to template
- Updated `agents/todo.md` with reference

## Critical Constraints

- **Read first**: Must read existing files before modifying
- **Use tools**: Read, Write, Edit for file operations (NOT bash cat/echo)
- **Bash only for**: mkdir, cp commands
- **Metadata**: Always add archive metadata header to shelved files
- **Date format**: YYYY-MM-DD (e.g., 2026-01-18)
- **Error handling**: Report errors explicitly, do not suppress

## Template Location

- Session template: `.claude/skills/shelve/templates/session.md`

Use `cp` command to copy this template when resetting session.md.

## Example Interaction

**User:** `/shelve`

**Agent:** "I'll help you shelve the current session context.

What name/topic should I use for this archive? (e.g., 'unification-phase1', 'auth-refactor')"

**User:** "Use 'unification-phase1'"

**Agent:**
*Archives session file with metadata*
*Updates todo.md with reference*
*Resets session file to template*

"Shelving complete:

Archived:
- `agents/shelf/unification-phase1-session.md`

Reset:
- `agents/session.md` (from template)

Updated:
- `agents/todo.md` (prepended session reference)

You can now start fresh with a new session file."

## Restoration Notes

**To restore from shelf:**

```bash
cp agents/shelf/<name>-session.md agents/session.md
```

Then remove the metadata header and "Archived Session" title.
