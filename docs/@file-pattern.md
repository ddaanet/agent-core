# The @file Import Pattern for Modular CLAUDE.md

The `@file` pattern enables CLAUDE.md files to import additional files, allowing you to organize project instructions modularly without copy-pasting content across multiple files.

## Official Syntax

CLAUDE.md files can import additional files using the `@path/to/file` syntax. Imports work inline with regular markdown content:

```markdown
See @README for project overview and @package.json for available npm commands.

# Additional Instructions
- git workflow @docs/git-instructions.md
```

Both relative and absolute paths are supported. This can be mixed with regular markdown and spans multiple files.

## Path Formats Supported

### Relative Paths
- `@docs/git-instructions.md` - Relative to the CLAUDE.md file's directory
- `@../shared-rules.md` - Navigate up the directory tree
- `@./local-config.md` - Explicit current directory reference
- `@../../../agent-core/fragments/workflows.md` - Cross-project relative paths

### Absolute Paths
- `@/Users/david/code/agent-core/fragments/workflows.md` - Full filesystem path
- `/path/to/file.md` - Works in all import contexts

### Home Directory Expansion
- `@~/.claude/my-project-instructions.md` - Tilde expansion for home directory
- `@~/code/shared-config.md` - Convenient for user-level instructions

## Import Location Rules

Imports work in regular markdown content but are **not evaluated** in specific contexts:

### Imports NOT Evaluated
- Inside inline code spans: `` `@anthropic-ai/claude-code` ``
- Inside code blocks (fenced with ``` or ~~~)
- Inside HTML comments

### Imports ARE Evaluated
- In regular paragraph text
- In markdown lists (bullet and numbered)
- In markdown headings
- At the beginning or end of lines
- Mixed with other content on the same line

## Recursion Depth

**Maximum recursion depth: 5 hops**

This means:
- Level 0: Initial CLAUDE.md file
- Level 1: Files imported directly by CLAUDE.md
- Level 2: Files imported by level 1 imports
- Level 3-5: Further nested imports
- Level 6+: **Not imported** (exceeds limit)

To verify import depth, use the `/memory` command during a session to see all loaded memory files.

## Circular Reference Handling

**Circular references are detected and handled gracefully.**

If your imports form a cycle (A → B → C → A), Claude Code:
1. Detects the cycle
2. Skips the duplicate import to prevent infinite recursion
3. Does NOT fail or error
4. Continues loading other imports normally

## When @file References Are Resolved

**Resolution timing: At session startup**

- When you start a Claude Code session, all CLAUDE.md files are discovered and loaded
- All `@file` references are resolved recursively at this time
- The import tree is traversed up to the maximum recursion depth (5 hops)
- Circular references are detected and skipped
- All loaded content is merged and available to Claude in that session

**Important:** Imports are **not re-evaluated during the session**. If you modify imported files while a session is running, Claude won't see the changes until you start a new session or reload context.

## Limitations and Edge Cases

### File Accessibility
- Imported files must be readable by Claude Code
- If a file doesn't exist or can't be read, that import fails silently
- Claude will not alert you to missing imports
- **Workaround:** Use `/memory` command to verify all imports are loaded

### Encoding and Size
- Imported files must be text files (UTF-8 preferred)
- Very large imports (>100KB) are possible but use significant context
- Consider splitting large files into smaller modules

### Path Resolution Order
When importing a relative path:
1. Resolved relative to the CLAUDE.md file's directory
2. If not found, NOT searched in other directories
3. Parent directory traversal (`../`) works as expected

### File Extension
Imports don't require `.md` extension, but it's recommended:
- `@docs/rules` works but may import a directory or ambiguous file
- `@docs/rules.md` is unambiguous and recommended

## Best Practices for Modular Organization

### 1. Fragment Directory Structure
Keep shared fragments in a dedicated directory:

```
agent-core/
├── fragments/
│   ├── workflows-terminology.md
│   ├── communication.md
│   ├── token-economy.md
│   ├── error-handling.md
│   └── bash-strict-mode.md
├── templates/
│   └── CLAUDE.template.md
└── docs/
    └── @file-pattern.md
```

### 2. Naming Conventions
Use descriptive filenames that indicate content:

```markdown
# fragments/ directory
- workflows-terminology.md      # Workflow definitions and terminology
- communication.md              # Communication rules
- token-economy.md              # Token efficiency guidelines
- testing.md                    # Testing conventions
- error-handling.md             # Error handling patterns
```

### 3. Keep Imports at Top or Organized
Place imports in logical groups:

```markdown
# CLAUDE.md

## Core Rules
@agent-core/fragments/communication.md
@agent-core/fragments/token-economy.md

## Workflows
@agent-core/fragments/workflows-terminology.md
@agents/decisions/workflows.md

## Development
@agents/decisions/testing.md
@agents/decisions/cli.md
```

### 4. Mix Imported Content with Project-Specific Content
Don't import everything. Keep project-specific instructions inline:

```markdown
# CLAUDE.md

@agent-core/fragments/communication.md

## This Project Specifics

### Build Commands
- `just build` - Compile TypeScript
- `just test` - Run test suite

### Project Structure
- `/src` - Source code
- `/tests` - Test files
```

### 5. Use Relative Paths for Team Collaboration
Make paths work for all team members:

```markdown
# Good (works for everyone)
@../../agent-core/fragments/workflows.md
@../shared-config.md
@~/.claude/personal-rules.md

# Problematic (hardcoded to one person)
@/Users/alice/code/agent-core/fragments/workflows.md
```

### 6. Verify Imports with /memory
Always check that imports are resolved as expected:

```bash
# In a Claude Code session
/memory
```

This command shows:
- All loaded memory files (including imports)
- The resolution path for each file
- Any import errors or missing files
- Current memory hierarchy

### 7. Avoid Over-Nesting
Keep recursion depth reasonable (aim for 3-4 hops max):

**Good:**
```
CLAUDE.md → rules/testing.md → patterns/test-helpers.md
```

**Less ideal:**
```
CLAUDE.md → rules.md → api/rules.md → api/testing.md → api/testing/edge-cases.md
```

## Real-World Example: Multi-Project Setup

```
my-organization/
├── agent-core/
│   └── fragments/
│       ├── communication.md
│       ├── token-economy.md
│       ├── workflows-terminology.md
│       └── error-handling.md
├── project-a/
│   └── CLAUDE.md
│       ```
│       @../../agent-core/fragments/communication.md
│       @../../agent-core/fragments/workflows-terminology.md
│
│       # Project A Specifics
│       - Tech stack: Node.js + TypeScript
│       - Test runner: Jest
│       ```
└── project-b/
    └── CLAUDE.md
        ```
        @../../agent-core/fragments/communication.md
        @../../agent-core/fragments/error-handling.md

        # Project B Specifics
        - Tech stack: Python + FastAPI
        - Test runner: pytest
        ```
```

All projects share the same foundational rules without duplication, while maintaining project-specific customizations.

## See Also

- [Memory management documentation](https://code.claude.com/docs/en/memory.md)
- [Best practices guide](https://code.claude.com/docs/en/best-practices.md)
- Project-level CLAUDE.md configuration patterns
