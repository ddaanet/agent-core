---
description: Create git commits for completed work with short, dense, structured messages. Use --context flag when you already know what changed from conversation.
allowed-tools: Read, Skill, Bash(git add:*), Bash(git status:*), Bash(git commit:*), Bash(just precommit), Bash(just test), Bash(just lint)
user-invocable: true
---

# Commit Skill

Create a git commit for the current changes using a consistent, high-quality commit message format.

**Note:** This skill does not update session.md. Run `/handoff` separately before committing if session context needs updating.

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

## Flags

**Context mode:**
- `--context` - Skip git discovery (status/diff) when you already know what changed from conversation

**Validation level:**
- (none) - `just precommit` (default, full validation)
- `--test` - `just test` only (TDD cycle commits before lint)
- `--lint` - `just lint` only (post-lint, pre-complexity fixes)

**Gitmoji:**
- `--no-gitmoji` - Skip gitmoji selection

**Usage examples:**
- `/commit` - full discovery + validation + gitmoji
- `/commit --context` - skip discovery, use conversation context
- `/commit --test` - TDD GREEN phase commit (test-only validation)
- `/commit --context --no-gitmoji` - skip discovery and gitmoji

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

### 1. Pre-commit validation + discovery

**Non-context mode** (default):
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

### 1b. Check submodules

If `git status` shows modified submodules (e.g., `M agent-core`):

1. Enter submodule: check `git status` inside it
2. If submodule has uncommitted changes: commit them first with a message generated from the submodule's own diff, following standard commit message style. Do NOT prefix the message with the submodule name — the commit lives inside the submodule repo where it would be redundant
3. Stage the submodule pointer in parent: `git add <submodule-path>`
4. Continue with parent commit

**Scope:** Single-level submodules only. Nested submodules not used in this repo.

**Why:** Submodule pointer updates are invisible unless the submodule is committed first. A parent commit with a dirty submodule creates sync issues.

**Context mode** (`--context` flag):
```bash
# Run validation only (skip discovery)
exec 2>&1
set -xeuo pipefail
just precommit  # or: just test (--test) / just lint (--lint)
```
- Skip `git status -vv` - you already know what changed from conversation
- ERROR if you don't have clear context about what changed
- Use when you just wrote/edited files and know the changes

### 2. Draft commit message

- Based on discovery output (non-context) or conversation context (context mode)
- Follow "short, dense, structured" format
- Ensure title is imperative mood, 50-72 chars
- Add bullet details with quantifiable facts

### 3. Select gitmoji

**Read references/gitmoji-index.txt** (~78 entries, format: `emoji - name - description`).

Analyze commit message semantics (type, scope, impact). Select most specific emoji matching primary intent:
- 🐛 bug - Fix a bug
- ✨ sparkles - Introduce new features
- 📝 memo - Add or update documentation
- ♻️ recycle - Refactor code
- ⚡️ zap - Improve performance
- 🔥 fire - Remove code or files
- 🎨 art - Improve structure / format of the code
- 🤖 robot - Add or update agent skills, instructions, or guidance
- (see full index for all 78 options)

Prefix commit title with selected emoji.

**Skip if `--no-gitmoji` flag provided.**

### 4. Stage, commit, verify

Use heredoc syntax for multiline commit messages:

```bash
# Stage specific files, commit with message, verify result
exec 2>&1
set -xeuo pipefail
git add file1.txt file2.txt
git commit -m "$(cat <<'EOF'
🐛 Fix authentication bug

- Detail 1
- Detail 2
EOF
)"
git status
```

**Guidelines:**
- Intent comment required as first line (before exec)
- Stage specific files only (not `git add -A`)
- Preserve already-staged files
- **Include `agents/session.md`, `plans/` files, and submodule pointer updates if they have uncommitted changes**
- Do NOT commit secrets (.env, credentials.json, etc.)

## Critical Constraints

- **Multi-line commit messages**: Use heredoc syntax with `git commit -m "$(cat <<'EOF' ... EOF)"` for clean formatting
- **No error suppression**: Never use `|| true`, `2>/dev/null`, or ignore exit codes (exception: token-efficient bash pattern - see `/token-efficient-bash` skill)
- **Explicit errors**: If anything fails, report it clearly and stop
- **No secrets**: Do not commit .env, credentials, keys, tokens, etc.
- **Clean tree check**: Must error explicitly if nothing to commit
- **Token-efficient bash**: When running 3+ sequential git commands, use `/token-efficient-bash` skill pattern for 40-60% token savings
- **Context mode requirement**: When using `--context`, error if you don't have clear context about what changed

## Post-Commit: Display Next Task

**This applies to ALL commits**, whether invoked directly or via tail-call from `/handoff --commit`.

After a successful commit, read `agents/session.md` and check for pending tasks (first `- [ ]` item).

**If pending tasks exist** — display the next one:
```
Committed: <commit subject line>

Next: <first pending task description>
```

**If no pending tasks** — tail-call `/next` to find work from broader context (todo.md, etc.).

**Why:** This enables tail-call composition. When `/commit` is tail-called from `/handoff --commit` (which is tail-called from `/plan-tdd` or `/plan-adhoc`), the user sees the next action without manual inspection. For post-planning workflows, this displays "Restart session, switch to haiku model, paste `/orchestrate {name}` from clipboard." When all pending work is done, `/next` finds the next thing.

## Context Gathering (Non-Context Mode)

**Run these commands:**
- `git status` - See what files changed
- `git diff HEAD` - See the actual changes (note: `git diff HEAD` separately - staged/unstaged diffs shown in `git status -vv` output)
- `git branch --show-current` - Current branch name

**Do NOT run:**
- `git log` - Style is hard-coded, log not needed
