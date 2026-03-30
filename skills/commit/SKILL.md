---
name: commit
description: Create git commits for completed work with short, dense, structured messages. Use --context flag when you already know what changed from conversation.
allowed-tools: Read, Edit, Skill, Bash(git add:*), Bash(git diff:*), Bash(git status:*), Bash(claudeutils _commit*), Bash(just precommit), Bash(just test), Bash(just lint)
user-invocable: true
continuation:
  cooperative: true
  default-exit: []
---

# Create Git Commits

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

**Allowlist constraint:** Run each git/just command as a separate Bash call. Do NOT chain commands (`git add && git diff`) or wrap in `exec 2>&1` — these fail allowlist matching.

### 1. Pre-commit validation + discovery

**Gate — Vet checkpoint:**

Run as separate Bash calls:
```bash
git diff --name-only $(git merge-base HEAD @{u} 2>/dev/null || echo HEAD~5)
```
```bash
git status --porcelain
```
```bash
# Grep changed file paths for production artifact prefixes
git diff --name-only $(git merge-base HEAD @{u} 2>/dev/null || echo HEAD~5) | grep -E '^(agent-core/|plans/|src/|agents/|\.claude/)' || true
```

Classify using Grep output — production artifacts are files matching the artifact prefixes above.

- **No artifact-prefix matches?** Proceed to validation.
- **Trivial?** (≤5 net lines, ≤2 files, additive, no behavioral change) Self-review via `git diff HEAD`.
- **Non-trivial?** Check for review report in `plans/*/reports/` or `tmp/`. No report → STOP, delegate review first. UNFIXABLE → escalate. No alignment criteria → escalate.

Reports are exempt — they ARE the verification artifacts.

**Validation + discovery (separate Bash calls):**

Non-context mode:
1. `just precommit` (or per flag)
2. `git status -vv`

Context mode:
1. `just precommit` (or per flag) only

**Gate: precommit fails → STOP.** Fix before committing. Do not rationalize failures.

ERROR if nothing to commit (no staged or unstaged changes). Note what's already staged vs unstaged.

### 1b. Submodule info gathering

If `git status` shows modified submodules (e.g., `M agent-core`), gather info for CLI input:

```bash
git -C agent-core diff --name-only HEAD
```

Note changed files and draft a submodule commit message. The CLI handles staging, committing, and pointer update via the `## Submodule` input section.

### 1c. Settings triage

**D+B anchor:**

```
Read(.claude/settings.local.json)
```

- **File absent** (Read returns error) → skip to step 2
- **Content is `{}`** → skip to step 2
- **Non-empty** → triage each permission entry below

| Classification | Action | Examples |
|---------------|--------|----------|
| **Permanent** — recurring workflow feature | Edit `.claude/settings.json` to add entry, Edit `.claude/settings.local.json` to remove it | `pbcopy`, `open`, `osascript`, frequently-used WebFetch domains (`docs.claude.com`, `github.com`) |
| **Session** — one-time grant, exploratory | Edit `.claude/settings.local.json` to remove it | One-off WebFetch domains, temporary Bash patterns used during investigation |
| **Job-specific** — needed by active worktree or in-progress task | Keep in `.claude/settings.local.json` only if handoff context justifies retention | Worktree sandbox paths (managed by `_worktree` CLI) |

After triage, `.claude/settings.local.json` should be empty `{}` or contain only job-justified entries. Stage modified settings files:
```bash
git add .claude/settings.local.json .claude/settings.json
```

**Classification signal:** If the entry already exists in `settings.json`, it was granted redundantly — remove from local, no promotion needed.

### 2. Draft commit message

Based on discovery output or conversation context. Follow format above. Do NOT run `git log` — style is defined in this skill.

### 3. Select gitmoji

Read `references/gitmoji-index.txt` (~78 entries). Analyze commit semantics, select most specific match. Prefix title with emoji. Skip if `--no-gitmoji`.

### 4. Compose and commit via CLI

Build structured markdown input and pipe to CLI:

```bash
claudeutils _commit <<'EOF'
## Files
- path/to/file1.py
- path/to/file2.md

## Options
- no-vet

## Submodule agent-core
> Submodule commit message

## Message
🔧 Parent commit message
EOF
```

**Sections:**
- `## Files` — specific files from git status (not `git add -A`). Include session.md, plans/, submodule pointers if changed.
- `## Options` — from flags: `--test` or `--lint` → `just-lint`, `--no-vet` or trivial classification → `no-vet`. Omit section if no options.
- `## Submodule <path>` — if submodule changes detected (Step 1b), include submodule commit message as blockquote. Omit if no submodule changes.
- `## Message` — drafted message with gitmoji prefix from Steps 2-3.

**Exit codes:** 0 = success. 1 = validation failure (surface CLI output). 2 = parse error (fix input).

## Post-Commit

After successful commit, output:

```
Committed: <commit subject line>

Status.
```

Stop hook renders via `_status` CLI.

## Continuation

Read continuation from `additionalContext` or `[CONTINUATION: ...]` suffix. If continuation present: peel first entry, tail-call with remainder. If empty: stop (terminal skill — default-exit is `[]`).

Do NOT include continuation metadata in Task tool prompts.
