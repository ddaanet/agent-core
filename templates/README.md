# agent-core Templates

Templates for new projects using agent-core as a submodule.

## CLAUDE.md Template

**Purpose:** Base CLAUDE.md file for new projects using agent-core fragments.

**Usage:**

1. **Copy template to your project root:**
   ```bash
   cp agent-core/templates/CLAUDE.template.md CLAUDE.md
   ```

2. **Customize project-specific sections:**
   - Search for `<!-- CUSTOMIZE:` comments
   - Add your project's decision documents
   - Add project-specific rules as needed
   - Remove placeholder comments

3. **Verify @file references resolve:**
   - Ensure agent-core submodule is initialized
   - All @file paths should be relative to project root

## What's Included

The template includes @file references to these shared fragments:

**Core workflow and terminology:**
- `workflows-terminology.md` - Workflow selection (general/TDD) and terminology table

**Communication patterns:**
- `communication.md` - Core behavioral rules (stop on unexpected, wait for instruction, etc.)
- `token-economy.md` - Token-efficient communication (file references, avoid numbered lists)
- `error-handling.md` - Error reporting principles
- `bash-strict-mode.md` - Token-efficient bash pattern

**File system rules:**
- `tmp-directory.md` - Project-local tmp/ usage (not system /tmp/)

**Session management:**
- `execute-rule.md` - #execute session continuation

**Orchestration patterns:**
- `delegation.md` - Delegation principle, script-first evaluation, model selection, quiet execution, pre-delegation checkpoint, task agent tool usage
- `tool-batching.md` - Tool batching for efficient parallel/sequential operations

## Customization Areas

**Documentation Structure:**
- Add paths to your project-specific decision documents
- Common: architecture.md, cli.md, testing.md, workflows.md

**Communication Rules:**
- Keep standard rules from fragments
- Add project-specific conventions (commit message format, PR workflow, etc.)

**Project Structure:**
- Document repository layout
- Important paths and conventions
- Build/test commands

**Delegation:**
- Project-specific skill development rules
- Custom orchestration patterns

## Example Projects

See these projects for reference implementations:
- **claudeutils** - Full CLI tool with custom skills
- **pytest-md** - Python library with test integration

## Fragment Updates

When agent-core fragments are updated:
1. Pull latest agent-core: `git submodule update --remote agent-core`
2. Test changes with your project's CLAUDE.md
3. Commit submodule update: `git add agent-core && git commit -m "Update agent-core"`

Your project-specific content remains unchanged - only shared fragments update.
