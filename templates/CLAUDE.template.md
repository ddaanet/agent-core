# Agent Instructions

@agents/rules/workflows-terminology.md

---

## Documentation Structure

**Progressive discovery:** Don't preload all documentation. Read specific guides only when needed.

### Core Instructions
- **CLAUDE.md** (this file) - Agent instructions, workflows, communication rules

### Architecture & Design
<!-- CUSTOMIZE: Add paths to your project-specific decision documents -->
<!-- Example:
- **agents/decisions/architecture.md** - Module structure, path handling, data models, code quality
- **agents/decisions/cli.md** - CLI patterns and conventions
- **agents/decisions/testing.md** - Testing conventions and patterns
-->

### Current Work
- @agents/session.md - Current session handoff context (update only on handoff)

---

## Communication Rules

@agents/rules/communication.md

@agents/rules/token-economy.md

@agents/rules/commit-skill-usage.md

@agents/rules/no-estimates.md

<!-- CUSTOMIZE: Add project-specific communication rules if needed -->

@agents/rules/error-handling.md

@agents/rules/bash-strict-mode.md

@agents/rules/tmp-directory.md

## Session Management

@agents/rules/execute-rule.md

<!-- CUSTOMIZE: Add project-specific structure rules if needed -->
<!-- Example:
## Project Structure

### Repository Layout
- `src/` - Source code
- `tests/` - Test files
- `docs/` - Documentation
-->

@agents/rules/execution-routing.md

@agents/rules/delegation.md

<!-- CUSTOMIZE: Add project-specific delegation or routing rules if needed -->
<!-- Example:
### Skill Development

**Rule:** When creating, editing, or discussing skills, start by loading the `plugin-dev:skill-development` skill.

**Why:** The skill-development skill provides:
- Skill structure and frontmatter guidance
- Progressive disclosure patterns
- Triggering condition best practices
- Integration with Claude Code plugin system

**Usage:** Invoke the skill before beginning skill work to load context and patterns.
-->

@agents/rules/tool-batching.md
