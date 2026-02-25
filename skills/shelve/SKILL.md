---
name: shelve
description: Archive session context to todo list and reset for new work
allowed-tools: Read, Write, Edit, Bash(mkdir:*), Bash(cp:*)
user-invocable: true
---

# Archive Session Context

Archive current session context to todo list and reset session file for new work.

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

## Constraints

- Read existing files before modifying (Read, Write, Edit for file ops; Bash only for mkdir, cp)
- Always add archive metadata header to shelved files (date: YYYY-MM-DD)
- Session template: `.claude/skills/shelve/templates/session.md` — use `cp` to reset

## Restoration

```bash
cp agents/shelf/<name>-session.md agents/session.md
```

Remove the metadata header and "Archived Session" title after restoring.
