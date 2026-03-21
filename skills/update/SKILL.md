---
name: update
description: Sync edify fragments and portable justfile to match the current plugin version. Detects user-edited files and warns instead of overwriting. Use --force to overwrite conflicts.
allowed-tools: Read, Write, Edit, Bash(ls:*), Bash(mkdir:*), Bash(cp:*), Bash(find:*), Bash(python3:*), Bash(sha256sum:*), Glob, Grep
user-invocable: true
---

# Update Edify Fragments

Sync instruction fragments and `portable.just` from the edify plugin to the consumer project. Updates `.edify.yaml` version and content hashes.

**This skill is for consumer projects only.** In dev mode (submodule), fragments are read directly via `@agent-core/fragments/` references -- update is a no-op.

## Flags

- `--force` -- Overwrite conflicting files (user-edited) with the plugin version. Review the conflict list from a normal run first, then re-run with `--force` to accept plugin versions.

## Prerequisite Check

Before proceeding, verify `agents/rules/` exists in the project root. If it does not exist, stop and report:

```
agents/rules/ not found. Run /edify:init first to set up the project structure.
```

## Execution Steps

### 1. Read plugin version

Read `$CLAUDE_PLUGIN_ROOT/.claude-plugin/plugin.json` and extract the `version` field.

### 2. Read .edify.yaml

Read `.edify.yaml` from the project root. Extract:
- `version` -- the last-synced plugin version
- `synced_hashes` -- map of relative file paths to SHA-256 content hashes at last sync

If `.edify.yaml` does not exist, stop and report:

```
.edify.yaml not found. Run /edify:init first to set up version tracking.
```

### 3. Inventory sync targets

Two categories of sync targets:

**Fragments:**
- Source: all `.md` files in `$CLAUDE_PLUGIN_ROOT/fragments/`
- Destination: `agents/rules/<filename>`

**Portable justfile:**
- Source: `$CLAUDE_PLUGIN_ROOT/just/portable.just`
- Destination: `portable.just` in project root
- **Guard:** If source does not exist (plugin version predates justfile modularization), skip this sync target and note it in the summary as "portable.just: not yet available in this plugin version".

### 4. Per-file sync with conflict detection

For each sync target, compute the SHA-256 hash of the **source** file (plugin version) and the **destination** file (consumer version, if it exists).

Classify each file into one of four categories:

**New** -- destination file does not exist in consumer project:
- Copy from plugin source to destination
- Record SHA-256 of the copied content in `synced_hashes`

**Safe to update** -- destination file exists AND its SHA-256 matches the `synced_hashes` entry (user has not edited it since last sync):
- Compare source hash to destination hash
- If they differ: overwrite destination with plugin source, update `synced_hashes` with new hash
- If they are identical: file is current, no action needed (categorize as **Current**)

**Conflict** -- destination file exists AND its SHA-256 does NOT match the `synced_hashes` entry (user has local edits):
- Without `--force`: warn and skip. Report the file path. Do NOT overwrite.
- With `--force`: overwrite destination with plugin source, update `synced_hashes` with new hash. Categorize as **Overwritten**.

**No hash entry** -- destination file exists but has no entry in `synced_hashes` (legacy or first run after manual setup):
- Treat as conflict (safe default). Same behavior as Conflict above.

### 5. Update .edify.yaml

After all files are processed:

1. Update the `version` field to match the current plugin version from Step 1
2. Write the updated `synced_hashes` map with all current hash values
3. Preserve any other fields in `.edify.yaml` (e.g., `sync_policy`)

Write the updated `.edify.yaml` back to the project root.

### 6. Summary

Report what was done:

```
/edify:update complete (vX.Y.Z)

New:       N files copied
  - agents/rules/new-fragment.md
Updated:   N files synced
  - agents/rules/changed-fragment.md
Current:   N files (no changes)
Conflicts: N files skipped (user-edited)
  - agents/rules/edited-fragment.md
```

With `--force`, replace the Conflicts line:

```
Overwritten: N files (user edits replaced)
  - agents/rules/edited-fragment.md
```

If all files are current and version matches:

```
/edify:update: already up-to-date (vX.Y.Z)
```

## Conflict Resolution Guidance

When conflicts are reported, the user has three options:

1. **Accept plugin version:** Re-run `/edify:update --force` to overwrite all conflicting files
2. **Keep local edits:** No action needed -- conflicting files are preserved as-is
3. **Manual merge:** Compare the conflicting file against the plugin source at `$CLAUDE_PLUGIN_ROOT/fragments/<filename>` and merge changes manually. After merging, the next `/edify:update` run will detect the merged file as a conflict again (hash differs from synced version). Use `--force` after manual merge to update the hash baseline

## Separation from /edify:init

This skill handles **sync only**:
- Fragment and justfile content updates
- Version tracking updates
- Conflict detection and resolution

It does NOT handle scaffolding (that is `/edify:init`):
- No `agents/` directory creation
- No `session.md`, `learnings.md`, `jobs.md` scaffolding
- No CLAUDE.md creation or reference rewriting
