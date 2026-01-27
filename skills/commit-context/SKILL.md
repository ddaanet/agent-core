---
description: This skill should be used when committing changes where the agent already has context from the conversation (just wrote/edited files, knows what changed). Skips git discovery (status/diff) for efficiency. Use when you know what files changed and why from conversation context.
allowed-tools: Bash(git add:*), Bash(git commit:*), Bash(git status:*), Bash(just precommit), Bash(just test), Bash(just lint)
user-invocable: true
---

# Commit Context Skill

Create a git commit using conversation context, skipping git discovery steps. Use when the agent already knows what changed from the conversation (e.g., just finished writing or editing files).

## When to Use

Use this skill instead of `/commit` when:
- Just wrote or edited files in the conversation
- Already analyzed what changed and why
- Want to skip redundant git status/diff discovery
- Have conversation context about the changes

**Do NOT use when:**
- Uncertain what files changed
- Need to review changes before committing
- Starting fresh with unknown state
- User explicitly requested review of changes

## Key Differences from /commit

**Skips:**
- `git status` for discovery (caller knows changes)
- `git diff HEAD` for analysis (caller analyzed already)

**Keeps:**
- Pre-commit validation (test/lint/precommit)
- Commit message format requirements
- Stage specific files (based on context)
- Post-commit verification

## Validation Flags

Control pre-commit validation level with optional flags:

| Flag | Validation | Use Case |
|------|------------|----------|
| (none) | `just precommit` | Default - full validation |
| `--test` | `just test` | TDD cycle commits before lint |
| `--lint` | `just lint` | Post-lint, pre-complexity fixes |

**Usage:**
- `/commit-context` - full validation (default)
- `/commit-context --test` - test only
- `/commit-context --lint` - lint only

**TDD workflow pattern:**
- After GREEN phase: `/commit-context --test` for WIP commit
- After REFACTOR complete: `/commit-context` for final amend

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
Add commit-context skill for efficient commits with conversation context

- Skip git discovery when agent knows what changed
- Keep pre-commit validation and message format
- Stage specific files based on context
```

```
Fix authentication bug in login flow

- Prevent session token expiration on page refresh
- Add token refresh logic to AuthProvider
- Update tests for new refresh behavior
```

## Execution Steps

1. **Use conversation context**
   - Agent already knows what files changed from conversation
   - Agent already analyzed changes
   - NO `git status` or `git diff` needed

2. **Update session.md if tasks completed**
   - Only if `agents/session.md` exists AND tasks were completed since last commit
   - Update handoff context to reflect current state (mark completed tasks, update blockers/notes)
   - Skip if no session.md or no relevant task progress since last commit

3. **Draft commit message**
   - Follow "short, dense, structured" format
   - Ensure title is imperative mood, 50-72 chars
   - Add bullet details with quantifiable facts
   - Use conversation context to inform message

4. **Run pre-commit checks**
   - If `--test` flag: Run `just test` only
   - If `--lint` flag: Run `just lint` only
   - Otherwise: Run `just precommit` (full validation)
   - If checks fail, STOP and report the error (do not proceed with commit)

5. **Stage specific files**
   - Run `git add <file1> <file2> ...` for specific files from context
   - Do NOT use `git add -A` (be explicit based on context)
   - Do NOT commit files with secrets (.env, credentials.json, etc.)
   - If secrets detected, ERROR and abort

6. **Create commit**
   - Use multi-line quoted string format (NOT heredocs - sandbox blocks them):
   ```bash
   git commit -m "Title line here

   - Detail 1
   - Detail 2
   - Detail 3"
   ```
   - The entire message should be in a single quoted string with actual newlines

7. **Verify success**
   - Run `git status` after commit
   - Confirm working tree is clean or show remaining unstaged files

## Critical Constraints

- **Require context**: Error if agent doesn't have clear context about what changed
- **Multi-line quoted strings**: Use `git commit -m "multi\nline"` format, NOT heredocs
- **No error suppression**: Never use `|| true`, `2>/dev/null`, or ignore exit codes (exception: token-efficient bash pattern - see `/token-efficient-bash` skill)
- **Explicit errors**: If anything fails, report it clearly and stop
- **No secrets**: Do not commit .env, credentials, keys, tokens, etc.
- **Specific staging**: Stage specific files from context, not `git add -A`
- **Token-efficient bash**: When running 3+ sequential git commands, use `/token-efficient-bash` skill pattern for 40-60% token savings

## When to Use /commit Instead

Use the standard `/commit` skill when:
- Need to discover what changed (git status/diff)
- Want to review changes before committing
- Uncertain about current state
- User explicitly wants to see changes
- Starting a new conversation without context
