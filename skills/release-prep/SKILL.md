---
description: Validates git state, runs quality checks, updates documentation, and assesses release readiness before the human executes the release command. Invoked when the user asks to "prepare release", "release prep", "ready to release", "pre-release check", "check release readiness", or mentions releasing a package.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(git:*), Bash(just:*)
user-invocable: true
---

# Prepare for Release

Validate preconditions, update documentation, and produce a readiness assessment. The actual release command is human-executed (protected by `_fail_if_claudecode`).

Documentation updates are batched at the end of the development cycle: hack → hack → hack → **prep** → release. This skill handles the prep stage.

## When to Use

- Before releasing a package to PyPI, npm, crates.io, etc.
- When the user wants to verify the project is ready to release
- After completing a batch of work and before cutting a release

## Execution Steps

### 1. Validate git state

<!-- DESIGN RULE: Every step must open with a tool call (Read/Bash/Glob).
     Prose-only steps get skipped. See: plans/reflect-rca-prose-gates/outline.md
     Comment placement: after heading, before first prose content. -->

Run git checks in parallel:

```bash
# Check git state: branch, tree cleanliness, remote sync, submodules
git branch --show-current
git status --porcelain
git fetch origin --dry-run 2>&1
git log @{u}..HEAD --oneline 2>/dev/null
git submodule status
```

**Check:**
- **On main branch?** Must be on `main` or `master`. Abort if on feature branch.
- **Clean working tree?** No uncommitted changes. Abort if dirty.
- **Synced with remote?** No unpushed commits and not behind remote. Warn if diverged.
- **Submodules clean?** No uncommitted submodule changes. Abort if submodule dirty.

### 2. Check for pending tasks

Read `agents/session.md` and count unchecked pending tasks (`- [ ]`):

```
# Use Grep to find pending task markers
Grep(pattern="^- \\[ \\]", path="agents/session.md", output_mode="count")
```

Warn if pending tasks exist — may indicate incomplete work that should ship first. This is a warning, not a blocker (user may intentionally release before completing all tasks).

### 3. Run quality checks

```bash
# Run full precommit validation suite
just precommit
```

If `just precommit` fails, report the failures and abort. All checks must pass before release.

### 4. Update documentation

Read detailed guidance:

```
# Load documentation update reference
Read("agent-core/skills/release-prep/references/documentation.md")
```

Two audiences:

**Human-facing (README.md):**
- Read style corpus: `tmp/STYLE_CORPUS` if exists, otherwise `references/default-style-corpus.md`
- Audit README against current project state (commits since last release inform what's stale)
- Rewrite stale sections applying style conventions
- Verify all code examples actually work

**Agent-facing:**
- Skill descriptions: verify trigger phrases match actual usage
- CLAUDE.md fragments: verify references point to existing files
- Memory index: verify entries are current

Commit documentation changes before proceeding (release recipe requires clean tree).

### 5. Assess release scope

Show what changed since the last release:

```bash
# Find latest version tag and show commits since then
git tag --sort=-v:refname | head -5
git log $(git describe --tags --abbrev=0 2>/dev/null)..HEAD --oneline
```

If no tags exist, show all commits on current branch.

Summarize: number of commits, key changes (from commit messages).

### 6. Detect version and release infrastructure

**Detect project type** by checking for:
- `pyproject.toml` — Python project
- `package.json` — Node.js project
- `Cargo.toml` — Rust project

**Show current version** from the detected config file.

**Check release recipe:**

```bash
# Look for release recipe
just --list 2>/dev/null | grep -i release
```

If found, that is the release command. If not found, note that no automated release recipe exists.

### 7. Readiness report

Produce a concise readiness report:

```
## Release Readiness

| Check               | Status |
|---------------------|--------|
| Branch              | pass/FAIL |
| Clean tree          | pass/FAIL |
| Remote sync         | pass/warn |
| Quality checks      | pass/FAIL |
| Pending tasks       | pass/warn (N pending) |
| Documentation       | pass/updated (N files) |

**Current version:** X.Y.Z
**Commits since last release:** N
**Key changes:**
- commit summary 1
- commit summary 2

**Release command:**
  `just release`           # patch bump (default)
  `just release minor`     # minor bump
  `just release major`     # major bump
  `just release --dry-run` # verify without publishing
```

If any FAIL: enumerate each failure with specific fix instructions, then STOP. Do not proceed to release command display.

If all pass: confirm ready and show the release command.

## Post-Report Behavior

After displaying the readiness report:
- If any checks FAILED: stop and wait for user to fix issues
- If all checks passed: skill completes — no further action taken
- Do NOT invoke other skills or commands
- User executes release command manually

## Critical Constraints

- **Do NOT run the release command.** It is human-executed only (`_fail_if_claudecode` guard).
- **Abort on FAIL checks.** Branch, clean-tree, and submodule failures are hard blockers. STOP and enumerate fixes needed.
- **Warn on pending tasks.** Inform but do not block — user decides.
- **Tool usage**: Read for files, Bash for git/just commands only. Do NOT use cat, grep, echo for file operations.
- **No version bumping.** This skill assesses readiness; it does not modify version numbers.
- **No error suppression**: Never use `|| true`, `2>/dev/null`, or ignore exit codes (exceptions: token-efficient bash pattern per `/token-efficient-bash` skill; expected no-upstream in `git log @{u}` probe)
- **Token-efficient bash**: When running 3+ sequential git commands, use `/token-efficient-bash` skill pattern for 40-60% token savings
- **Explicit errors**: If anything fails, report it clearly and stop

## Example Interaction

**User:** `/release-prep`

**Agent:**

*Runs git state checks, quality checks, and scope assessment*

```
## Release Readiness

| Check               | Status |
|---------------------|--------|
| Branch (main)       | pass   |
| Clean tree          | pass   |
| Remote sync         | pass   |
| Quality checks      | pass   |
| Pending tasks       | warn (2 pending) |

Current version: 0.0.2
Commits since v0.0.2: 14
Key changes:
- Add statusline CLI with TDD
- Fix authentication flow
- Update memory index infrastructure

Pending tasks (non-blocking):
- Design runbook identifiers
- Implement ambient awareness

Release command:
  just release           # → 0.0.3 (patch)
  just release minor     # → 0.1.0
  just release --dry-run # verify first
```

"Ready to release. 2 pending tasks exist but are independent of this release. Run `just release` (or `just release --dry-run` to verify first)."

## References

- **`references/documentation.md`** — Detailed documentation update guidance (audiences, audit process, staleness patterns)
- **`references/default-style-corpus.md`** — Default README style reference (used when no project-specific `tmp/STYLE_CORPUS` exists)
