---
name: init
description: Set up the edify agent framework in a new project. Scaffolds CLAUDE.md, copies instruction fragments, creates agents/ directory structure, and writes version marker. Idempotent — safe to re-run.
allowed-tools: Read, Write, Edit, Bash(ls:*), Bash(mkdir:*), Bash(cp:*), Bash(find:*), Bash(python3:*), Bash(sha256sum:*), Glob, Grep
user-invocable: true
---

# Initialize Edify Framework

Set up the edify agent framework in a consumer project (marketplace install). Copies instruction fragments, scaffolds project structure, and writes version tracking.

**This skill is for consumer projects only.** The edify-plugin repository itself does not run `/edify:init` — it IS the plugin.

## Execution Steps

### 1. Read plugin version

Read `$CLAUDE_PLUGIN_ROOT/.claude-plugin/plugin.json` and extract the `version` field. This is the authoritative version for `.edify.yaml`.

### 2. Inventory fragments

List all `.md` files in `$CLAUDE_PLUGIN_ROOT/fragments/`. These are the instruction fragments to copy.

### 3. Create agents directory structure

Check and create each of the following if it does not already exist. Never overwrite existing files.

- `agents/` directory
- `agents/rules/` directory (fragment destination)
- `agents/session.md` — create with this content:

```markdown
# Session Handoff

**Status:** New project — no prior sessions.

## In-tree Tasks

(none)

## Next Steps

Begin work.
```

- `agents/learnings.md` — create with this content:

```markdown
# Learnings

Institutional knowledge accumulated across sessions. Append new learnings at the bottom.
```

- `agents/jobs.md` — create with this content:

```markdown
# Jobs

Track job-level context here.
```

### 4. Copy fragments

Copy every `.md` file from `$CLAUDE_PLUGIN_ROOT/fragments/` to `agents/rules/`.

For each fragment:
- If the file already exists in `agents/rules/` — **skip it** (do not overwrite user content)
- If the file does not exist — copy it

Record the list of copied files and skipped files for the summary.

### 5. Handle CLAUDE.md

**Two cases:**

**Case A — CLAUDE.md exists in project root:**
- Read the existing CLAUDE.md
- Find all `@agent-core/fragments/` references and rewrite them to `@agents/rules/` (the local copies created in Step 4)
- Find all `@edify-plugin/fragments/` references and rewrite them to `@agents/rules/`
- Do NOT modify any other content — preserve everything the user has written
- Report which references were rewritten

**Case B — No CLAUDE.md in project root:**
- Read the template at `$CLAUDE_PLUGIN_ROOT/templates/CLAUDE.template.md`
- Write it to `CLAUDE.md` in the project root
- The template already uses `@agents/rules/` references — no rewriting needed
- Report that CLAUDE.md was created from template

### 6. Write .edify.yaml

If `.edify.yaml` already exists, do NOT overwrite it. Report that it was skipped.

If `.edify.yaml` does not exist, create it in a single write:

1. Compute SHA-256 hashes for each fragment file that was **copied** in Step 4 (not skipped — skipped files are treated as potential user edits)
2. Write `.edify.yaml` with the version, policy, and computed hashes in one operation:

```yaml
# Edify plugin version tracking
# Run /edify:update when plugin updates to sync fragments
version: "<plugin version from Step 1>"
sync_policy: nag
synced_hashes:
  agents/rules/communication.md: "<sha256>"
  agents/rules/execute-rule.md: "<sha256>"
  # ... one entry per copied fragment
```

Fragments that were skipped (already existed) do NOT get hash entries.

### 7. Summary

Report what was done:

```
/edify:init complete

Fragments: N copied, M skipped (already existed)
Structure: agents/session.md, agents/learnings.md, agents/jobs.md [created/existed]
CLAUDE.md: [created from template / N references rewritten / already existed, no refs found]
Version: .edify.yaml [created at vX.Y.Z / already existed]
```

## Idempotency

Every operation checks before acting:
- Directories: create only if missing
- Files: write only if missing
- CLAUDE.md refs: rewrite only if `@agent-core/fragments/` or `@edify-plugin/fragments/` patterns found
- `.edify.yaml`: write only if missing

Re-running `/edify:init` applies only missing pieces. It never destroys existing content.
