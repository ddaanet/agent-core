## Project Tooling Priority

**Rule:** Before executing ad-hoc commands, check if a project recipe already handles the operation.

**Priority order:**
1. **Project recipe** (`just <recipe>`, `make <target>`, project scripts) — always preferred
2. **Ad-hoc command** (`ln`, `mv`, `cp`, etc.) — only when no recipe exists

**Why:** Project recipes encode institutional knowledge — correct paths, ordering, side effects, edge cases. Ad-hoc commands bypass all of this, even when functionally equivalent.

**Check:** Run `just --list` (or equivalent) before writing manual commands for common operations like:
- Symlink management → `just sync-to-parent`
- Code formatting → `just format`
- Linting → `just lint`
- Testing → `just test`
- Pre-commit validation → `just precommit`

**Anti-pattern:** Using `ln -sf` to create symlinks in `.claude/` when `just sync-to-parent` exists.

**Partial failure recovery:** If a recipe fails partway through, fix the obstruction and **retry the recipe** — do not complete remaining steps manually. Recipes are atomic units; manually finishing steps bypasses error handling, ordering, and side effects encoded in the recipe.

**Relationship to Script-First Evaluation:** Script-First Evaluation governs the _delegate vs execute_ decision. This rule governs _how_ to execute: prefer existing project recipes over equivalent ad-hoc commands.
