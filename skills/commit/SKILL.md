---
description: Create git commits for completed work with short, dense, structured messages
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git commit:*), Bash(just precommit)
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

3. **Draft commit message**
   - Follow "short, dense, structured" format
   - Ensure title is imperative mood, 50-72 chars
   - Add bullet details with quantifiable facts

4. **Run pre-commit checks**
   - Run `just precommit` to verify code quality
   - If it fails, STOP and report the error (do not proceed with commit)

5. **Stage changes**
   - Run `git add -A` to stage all changes
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
