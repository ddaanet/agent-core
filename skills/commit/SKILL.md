---
description: Create git commits for completed work with short, dense, structured messages. Use --context flag when you already know what changed from conversation.
allowed-tools: Read, Skill, Bash(git add:*), Bash(git diff:*), Bash(git status:*), Bash(git commit:*), Bash(just precommit), Bash(just test), Bash(just lint)
user-invocable: true
continuation:
  cooperative: true
  default-exit: []
---

# Commit Skill

Create a git commit with consistent, high-quality messages.

**Note:** This skill does not update session.md. Run `/handoff` separately before committing if session context needs updating.

**Only commit when explicitly requested.** `/commit`, `ci`, `xc`, `hc`. Never auto-commit — completing a task is NOT a commit trigger.

## Flags

**Context mode:**
- `--context` - Skip git discovery when you already know what changed

**Validation level** (WIP commits only — feature/fix commits require full `just precommit`):
- (none) - `just precommit` (default)
- `--test` - `just test` only (TDD GREEN WIP)
- `--lint` - `just lint` only (post-lint WIP)

**Gitmoji:**
- `--no-gitmoji` - Skip gitmoji selection

**TDD workflow pattern:**
- GREEN phase: `/commit --test` (WIP, test-only validation)
- After REFACTOR: `/commit` (full precommit, final commit)

## Commit Message Style

**Format: "Short, dense, structured"**

```
<Imperative verb> <what changed>

- <detail 1>
- <detail 2>
- <detail 3>
```

Title: 50-72 chars, imperative mood, no period. Details: quantifiable facts, WHAT+WHY, exclusions/constraints. User-facing perspective — not implementation details.

**Example:**

```
Add #load rule and replace AGENTS.md references with CLAUDE.md

- Add Session Management section with exact file paths
- Replace AGENTS.md with CLAUDE.md across 50 files (319 replacements)
- Exclude scratch/ directory with nested git repos
```

## Execution Steps

**Allowlist constraint:** Run each git/just command as a separate Bash call. Do NOT chain commands (`git add && git commit`) or wrap in `exec 2>&1` — these fail allowlist matching.

### 1. Pre-commit validation + discovery

**Gate — Vet checkpoint:**

Run as separate Bash calls:
```bash
git diff --name-only $(git merge-base HEAD @{u} 2>/dev/null || echo HEAD~5)
```
```bash
git status --porcelain
```

Classify changed files — production artifacts (code, scripts, plans, skills, agents)?

- **No production artifacts?** Proceed to validation.
- **Trivial?** (≤5 net lines, ≤2 files, additive, no behavioral change) Self-review via `git diff HEAD`.
- **Non-trivial?** Check for vet report in `plans/*/reports/` or `tmp/`. No report → STOP, delegate vet first. UNFIXABLE → escalate. No alignment criteria → escalate.

Reports are exempt — they ARE the verification artifacts.

**Validation + discovery (separate Bash calls):**

Non-context mode:
1. `just precommit` (or per flag)
2. `git status -vv`

Context mode:
1. `just precommit` (or per flag) only

**Gate: precommit fails → STOP.** Fix before committing. Do not rationalize failures.

ERROR if nothing to commit (no staged or unstaged changes). Note what's already staged vs unstaged.

### 1b. Submodule handling

If `git status` shows modified submodules (e.g., `M agent-core`), commit submodule first:

1. `(cd agent-core && git status)`
2. `(cd agent-core && git add <files>)`
3. `(cd agent-core && git commit -m "$(cat <<'EOF'` ... `EOF` `)")`
4. `git add agent-core` — stage pointer in parent
5. Continue with parent commit

Use `(cd submodule && ...)` subshell to preserve working directory. One command per Bash call.

### 2. Draft commit message

Based on discovery output or conversation context. Follow format above. Do NOT run `git log` — style is defined in this skill.

### 3. Select gitmoji

Read `references/gitmoji-index.txt` (~78 entries). Analyze commit semantics, select most specific match. Prefix title with emoji. Skip if `--no-gitmoji`.

### 4. Stage, commit, verify

Separate Bash calls:
1. `git add <specific files>` — not `git add -A`. Include session.md, plans/, submodule pointers if changed. Preserve already-staged files.
2. `git commit -m "$(cat <<'EOF'` ... `EOF` `)"` — heredoc for multiline
3. `git status` — verify clean

Do NOT commit secrets (.env, credentials, keys).

## Post-Commit: Display STATUS

After successful commit:

```
Committed: <commit subject line>
```

Then display STATUS per execute-rule.md MODE 1. Copy first pending task command to clipboard (`dangerouslyDisableSandbox: true`). No pending tasks → "No pending tasks." and suggest `/next`.
