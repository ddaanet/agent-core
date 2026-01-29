---
description: Create git commits for completed work with short, dense, structured messages
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git commit:*), Bash(just precommit), Bash(just test), Bash(just lint)
user-invocable: true
---

# Commit Skill

Create a git commit for the current changes using a consistent, high-quality commit message format.

## When to Use

**Interactive sessions (user present):**
- **Only commit when:**
  - User explicitly requests (`/commit`)
  - At natural breakpoints: end of multi-step task, before switching major context
  - After completing a cohesive set of related changes
- **Batch related changes** - don't commit after each individual file edit or small fix
- **Wait for user direction** - when in doubt, wait for explicit commit request

**Automated workflows (runbook execution, /orchestrate):**
- Auto-commit after completing each logical unit of work defined in the plan
- Checkpoint commits at specified intervals in the runbook
- Each step completion typically warrants a commit

**Examples of logical units:**
- Implementing a complete feature (not each file in the feature)
- Fixing a bug (all related changes together)
- Completing a refactoring pass (not mid-refactor)
- Updating documentation (related doc changes together)

## Validation Flags

Control pre-commit validation level with optional flags:

| Flag | Validation | Use Case |
|------|------------|----------|
| (none) | `just precommit` | Default - full validation |
| `--test` | `just test` | TDD cycle commits before lint |
| `--lint` | `just lint` | Post-lint, pre-complexity fixes |

**Usage:**
- `/commit` - full validation (default)
- `/commit --test` - test only
- `/commit --lint` - lint only

**TDD workflow pattern:**
- After GREEN phase: `/commit --test` for WIP commit
- After REFACTOR complete: `/commit` for final amend

## Commit Message Style

**Format: "Short, dense, structured"**

```
<Imperative verb> <what changed>

- <detail 1>
- <detail 2>
- <detail 3>
```

**Rules:**
- **Title line**: 50-72 characters, imperative mood (Add, Fix, Update, Refactor), no period
- **Blank line** before details
- **Details**: Bullet points with dense facts
  - Focus on WHAT changed and WHY
  - Include quantifiable information (file counts, line counts)
  - Mention exclusions or constraints if relevant
  - NOT implementation details (that's in the diff)
- **User-facing perspective**: What does this commit accomplish?

**Examples:**

```
Add #load rule and replace AGENTS.md references with CLAUDE.md

- Add Session Management section with exact file paths
- Replace AGENTS.md with CLAUDE.md across 50 files (319 replacements)
- Exclude scratch/ directory with nested git repos
```

```
Fix authentication bug in login flow

- Prevent session token expiration on page refresh
- Add token refresh logic to AuthProvider
- Update tests for new refresh behavior
```

## Execution Steps

1. **Pre-commit + discovery** (single bash block, fail fast)
   ```bash
   # Run validation and discover staged/unstaged changes
   exec 2>&1
   set -xeuo pipefail
   just precommit  # or: just test (--test) / just lint (--lint)
   git status -vv
   ```
   - Intent comment required as first line (before exec)
   - Precommit first: if it fails, no verbose output bloat
   - Shows: file status + staged diffs + unstaged diffs
   - Note what's already staged vs unstaged (preserve staging state)
   - ERROR if working tree is clean

2. **Perform handoff**
   - Run `/handoff` skill to update session.md

3. **Draft commit message**
   - Based on discovery output, follow "short, dense, structured" format

4. **Select gitmoji**
   - Invoke `/gitmoji` skill to select appropriate emoji
   - Prefix commit message title with selected gitmoji
   - Skip if `--no-gitmoji` flag provided

5. **Stage, commit, verify** (single bash block)
   ```bash
   # Stage specific files, commit with message, verify result
   exec 2>&1
   set -xeuo pipefail
   git add file1.txt file2.txt
   git commit -m "🐛 Fix authentication bug

   - Detail 1
   - Detail 2"
   git status
   ```
   - Intent comment required as first line (before exec)
   - Stage specific files only (not `git add -A`)
   - Preserve already-staged files
   - Do NOT commit secrets (.env, credentials.json, etc.)

## Critical Constraints

- **Multi-line quoted strings**: Use `git commit -m "multi\nline"` format, NOT heredocs
- **No error suppression**: Never use `|| true`, `2>/dev/null`, or ignore exit codes (exception: token-efficient bash pattern - see `/token-efficient-bash` skill)
- **Explicit errors**: If anything fails, report it clearly and stop
- **No secrets**: Do not commit .env, credentials, keys, tokens, etc.
- **Clean tree check**: Must error explicitly if nothing to commit
- **Token-efficient bash**: When running 3+ sequential git commands, use `/token-efficient-bash` skill pattern for 40-60% token savings

## Context Gathering

**Run these commands:**
- `git status` - See what files changed
- `git diff HEAD` - See the actual changes
- `git branch --show-current` - Current branch name

**Do NOT run:**
- `git log` - Style is hard-coded, log not needed
