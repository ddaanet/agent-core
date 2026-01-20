---
description: Create git commits for completed work with short, dense, structured messages
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git commit:*), Bash(just precommit), Bash(just test), Bash(just lint)
user-invocable: true
---

# Commit Skill

Create a git commit for the current changes using a consistent, high-quality commit message format.

## When to Use

**Auto-commit** after completing a logical unit of work:
- Implementing a feature
- Fixing a bug
- Refactoring code
- Updating documentation
- Any other discrete, complete change

**Manual invocation** when user requests a commit.

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

1. **Check for changes**
   - Run `git status`
   - ERROR if working tree is clean (errors should never pass silently)
   - Identify staged and unstaged changes

2. **Review changes**
   - Run `git diff HEAD` to see all changes (staged and unstaged)
   - Analyze what changed and why

3. **Update session.md if tasks completed**
   - Only if `agents/session.md` exists AND tasks were completed since last commit
   - Update handoff context to reflect current state (mark completed tasks, update blockers/notes)
   - Skip if no session.md or no relevant task progress since last commit

4. **Draft commit message**
   - Follow "short, dense, structured" format
   - Ensure title is imperative mood, 50-72 chars
   - Add bullet details with quantifiable facts

5. **Run pre-commit checks**
   - If `--test` flag: Run `just test` only
   - If `--lint` flag: Run `just lint` only
   - Otherwise: Run `just precommit` (full validation)
   - If checks fail, STOP and report the error (do not proceed with commit)

6. **Stage changes**
   - Run `git add -A` to stage all changes
   - Do NOT commit files with secrets (.env, credentials.json, etc.)
   - If secrets detected, ERROR and abort

7. **Create commit**
   - Use multi-line quoted string format (NOT heredocs - sandbox blocks them):
   ```bash
   git commit -m "Title line here

   - Detail 1
   - Detail 2
   - Detail 3"
   ```
   - The entire message should be in a single quoted string with actual newlines

8. **Verify success**
   - Run `git status` after commit
   - Confirm working tree is clean

## Critical Constraints

- **Multi-line quoted strings**: Use `git commit -m "multi\nline"` format, NOT heredocs
- **No error suppression**: Never use `|| true`, `2>/dev/null`, or ignore exit codes
- **Explicit errors**: If anything fails, report it clearly and stop
- **No secrets**: Do not commit .env, credentials, keys, tokens, etc.
- **Clean tree check**: Must error explicitly if nothing to commit

## Context Gathering

**Run these commands:**
- `git status` - See what files changed
- `git diff HEAD` - See the actual changes
- `git branch --show-current` - Current branch name

**Do NOT run:**
- `git log` - Style is hard-coded, log not needed
