# Agent Instructions

@agent-core/fragments/workflows-terminology.md

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

@agent-core/fragments/communication.md

@agent-core/fragments/token-economy.md

<!-- CUSTOMIZE: Add project-specific communication rules if needed -->
**Additional communication rules:**
- **Use /commit skill** - Always invoke `/commit` skill when committing; it handles multi-line message format correctly. Use `/gitmoji` before `/commit` for emoji-prefixed messages
- **No estimates unless requested** - Do NOT make estimates, predictions, or extrapolations unless explicitly requested by the user. Report measured data only.

@agent-core/fragments/error-handling.md

@agent-core/fragments/bash-strict-mode.md

@agent-core/fragments/tmp-directory.md

## Session Management

@agent-core/fragments/execute-rule.md

<!-- CUSTOMIZE: Add project-specific structure rules if needed -->
<!-- Example:
## Project Structure

### Repository Layout
- `src/` - Source code
- `tests/` - Test files
- `docs/` - Documentation
-->

@agent-core/fragments/delegation.md

<!-- CUSTOMIZE: Add project-specific delegation rules if needed -->
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

@agent-core/fragments/tool-batching.md
