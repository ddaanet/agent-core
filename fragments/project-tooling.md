## Project Tooling Priority

**Rule:** Before executing ad-hoc commands, check if a project recipe already handles the operation.

**Priority order:**
1. **Project recipe** (`just <recipe>`, `make <target>`, project scripts) — always preferred
2. **Ad-hoc command** (`ln`, `mv`, `cp`, etc.) — only when no recipe exists

**Why:** Project recipes encode institutional knowledge — correct paths, ordering, side effects, edge cases. Ad-hoc commands bypass all of this, even when functionally equivalent.

**Check:** Run `just --list` (or equivalent) before writing manual commands for common operations like:
- Symlink management → `just sync-to-parent` (requires `dangerouslyDisableSandbox: true`)
- Code formatting → `just format`
- Linting → `just lint`
- Testing → `just test`
- Pre-commit validation → `just precommit`

**Anti-pattern:** Using `ln -sf` to create symlinks in `.claude/` when `just sync-to-parent` exists.

**Partial failure recovery:** If a recipe fails partway through, fix the obstruction and **retry the recipe** — do not complete remaining steps manually. Recipes are atomic units; manually finishing steps bypasses error handling, ordering, and side effects encoded in the recipe.

**Deny-list as routing signal:** When a CLI command fails and raw commands are denied, the deny list is a routing signal — it means "use the wrapper." After CLI failure, retry with escalated flags (`--force`) before decomposing into raw commands.

**Relationship to Execution Routing:** Execution Routing (`execution-routing.md`) governs the _delegate vs do directly_ decision. This rule governs _how_ to execute: prefer existing project recipes over equivalent ad-hoc commands.

### Check Platform Capabilities Before Building

**Anti-pattern:** Building custom review/workflow infrastructure without checking what the platform already ships.

**Correct pattern:** Inventory platform-provided plugins and features first. Build custom only for gaps. Anthropic ships 28 official plugins including code-review, feature-dev, security-guidance, commit-commands, claude-md-management.

**Rationale:** Custom infrastructure diverges from platform evolution. Official plugins get maintained, updated, and integrated. Reinvention wastes effort and creates maintenance burden.

### Use Full-Featured CLI Invocations

**Anti-pattern:** Using the bare/simple invocation form of a CLI when a richer form exists that automates side effects. Example: `_worktree new <slug>` instead of `_worktree new --task "Task Name"` — then manually editing session.md to compensate.

**Correct pattern:** Before invoking a CLI command, check `--help` or known options. Use the form that includes automation (session.md updates, focused sessions, validation). Manual side effects are worse, error-prone, and miss features.

**Root cause:** Familiarity with the primitive form suppresses discovery of the full-featured form. The simple form's visible output (worktree created) masks the missing side effects.

**Same class as:** Primitive visibility (see execution-routing.md) and ad-hoc Python scripting (write `claudeutils _worktree ls` not `python3 -c "import..."`).

### Rule Suppression by Procedure

**Anti-pattern:** Procedural instructions in fragments suppress cross-cutting operational rules. When a procedure says "call X()" the agent follows it literally, skipping the project-tooling check.

**Correct pattern:** The check-for-existing-tools rule applies even when a procedure names a specific function. Specific instructions must not suppress general operational rules.

**Evidence:** execute-rule.md said "Call `list_plans()`" → agent wrote ad-hoc Python → 3 failed attempts guessing attributes → 6-turn guided diagnostic. CLI existed the whole time (`claudeutils _worktree ls`).
