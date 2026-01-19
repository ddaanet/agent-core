---
description: Archive session context to todo list and reset for new work
allowed-tools: Read, Write, Edit, Bash(mkdir:*), Bash(cp:*)
user-invocable: true
---

# Shelve Skill

Archive current session context to todo list and reset context files for new work.

## When to Use

**Use this skill when:**
- Switching to unrelated work within the same project
- Completing a project phase and starting a new one
- Current work needs to be paused and documented for later

**Ask user for approval before running.**

## Decision Criteria

Based on `/Users/david/code/claudeutils/tmp/session-context-scope.md` lines 100-108:

```
Is context.md still accurate?
  YES -> Shelve session.md only
  NO -> Is context.md worth preserving?
    YES -> Shelve both
    NO -> Shelve session.md, reset context.md to template
```

**Always ask user:** "Should I shelve context.md as well, or just session.md?"

## Execution Steps

### 1. Gather Input

Ask user for:
- **Name/topic**: Natural language description (e.g., "unification", "auth-refactor")
- **Shelve context.md?**: Yes/No (use decision criteria above to guide)

### 2. Read Current Files

Read the following files:
- `agents/session.md`
- `agents/context.md` (if shelving both)
- `agents/todo.md` (to prepend to)

### 3. Create Shelf Directory

```bash
mkdir -p agents/shelf
```

### 4. Archive to Shelf

**For session.md (always):**

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

**For context.md (if shelving):**

Archive to `agents/shelf/<name>-context.md` with metadata header:

```markdown
---
archived: YYYY-MM-DD
topic: <name>
reason: <brief description from user input>
---

# Archived Context: <name>

<original context.md content>
```

### 5. Update todo.md

Prepend to `agents/todo.md` after the "## Backlog" header:

**Format (from scope doc lines 111-122):**

```markdown
## Backlog

### YYYY-MM-DD - Session: <name>

<session.md content>

[If context.md was shelved:]

### YYYY-MM-DD - Context: <name>

<context.md content>

---
```

**Important:** Session content comes FIRST (most recent), then context content (if applicable).

### 6. Reset Files

**Reset session.md (always):**

```bash
cp .claude/skills/shelve/templates/session.md agents/session.md
```

**Reset context.md (only if shelved):**

```bash
cp .claude/skills/shelve/templates/context.md agents/context.md
```

### 7. Report Results

Report to user:
- Which files were archived (with paths)
- Where they were archived to (`agents/shelf/`)
- Which files were reset
- Updated `agents/todo.md` with references

## Critical Constraints

- **Read first**: Must read existing files before modifying
- **Use tools**: Read, Write, Edit for file operations (NOT bash cat/echo)
- **Bash only for**: mkdir, cp commands
- **No heredocs**: Sandbox blocks `<<EOF` syntax
- **Metadata**: Always add archive metadata header to shelved files
- **Order in todo.md**: Session first, then context (if both shelved)
- **Date format**: YYYY-MM-DD (e.g., 2026-01-18)
- **Error handling**: Report errors explicitly, do not suppress

## Template Locations

- Session template: `.claude/skills/shelve/templates/session.md`
- Context template: `.claude/skills/shelve/templates/context.md`

Use `cp` command to copy these templates when resetting files.

## Example Interaction

**User:** `/shelve`

**Agent:** "I'll help you shelve the current session context.

First, let me check if context.md is still accurate for future work, or if it should also be shelved.

Looking at context.md, it describes the 'Rules Unification Project' with references to specific plans and architecture.

Questions:
1. What name/topic should I use for this archive? (e.g., 'unification', 'phase1-complete')
2. Should I shelve context.md as well, or just session.md?
   - Shelve both if: You're done with this project phase and the context is no longer relevant
   - Shelve session.md only if: The project context is still accurate, just switching tasks"

**User:** "Use 'unification-phase1' and shelve both"

**Agent:**
*Archives both files with metadata*
*Updates todo.md with references*
*Resets both files to templates*

"Shelving complete:

Archived:
- `agents/shelf/unification-phase1-session.md`
- `agents/shelf/unification-phase1-context.md`

Reset:
- `agents/session.md` (from template)
- `agents/context.md` (from template)

Updated:
- `agents/todo.md` (prepended session and context references)

You can now start fresh with new session and context files."

## Restoration Notes

**To restore from shelf:**

```bash
cp agents/shelf/<name>-session.md agents/session.md
cp agents/shelf/<name>-context.md agents/context.md
```

Then remove the metadata header and "Archived Session/Context" title.
