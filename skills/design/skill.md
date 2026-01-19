---
description: Opus design session for complex jobs with uncertain requirements
allowed-tools: Task, Read, Write, Bash, Grep, Glob, WebSearch, WebFetch
user-invocable: true
---

# Design Skill

Create comprehensive design documents for complex tasks through thorough exploration and analysis. This skill uses Opus-level reasoning to examine the problem space, explore existing code, and produce dense design documents that guide implementation.

## When to Use

**Use this skill when:**
- Requirements are unclear or ambiguous
- Task involves multiple components or systems
- Architectural decisions need to be made
- Complex job requires upfront design thinking
- Trade-offs need to be evaluated

**Do NOT use when:**
- Task is well-defined and straightforward
- Implementation approach is obvious
- Simple bug fix or minor change
- Plan already exists

## Design Process

### 1. Understand the Request

**Read context:**
- Review `agents/context.md` for current project state
- Check `agents/design-decisions.md` for existing architectural patterns
- Identify any related work or constraints

**Clarify scope:**
- Ask questions if requirements are ambiguous
- Identify what's in scope and what's explicitly out of scope
- Determine success criteria

### 2. Explore the Codebase

**CRITICAL: Delegate all exploration - Opus must not explore directly.**

**Exploration delegation:**
1. Try Task tool with subagent_type="quiet-explore"
2. If that fails: fallback to subagent_type="Explore"

**Never use directly during exploration:**
- ❌ Grep for searching
- ❌ Glob for finding files
- ❌ Read for browsing code
- ✅ Only use Read for specific files AFTER exploration identifies them

**Exploration prompt template:**

```
Explore the codebase to understand: [specific exploration goal]

Focus areas:
- Existing implementations of similar features
- Related components that will be affected
- Patterns and conventions to follow
- Potential integration points

Provide:
- File locations and their purposes
- Key patterns or conventions identified
- Integration points and dependencies
- Relevant code snippets with file paths

Thoroughness: [quick / medium / very thorough]
```

**After exploration:**
- Use Read to examine specific files identified by exploration
- Extract concrete details for design decisions

### 3. Research (if needed)

**External research:**
- WebSearch for best practices and patterns
- WebFetch for documentation or specifications
- Look for similar implementations or approaches

**Document findings:**
- Summarize relevant information
- Note applicable patterns or constraints
- Identify trade-offs

### 4. Create Design Document

**Document structure:**

```markdown
# Design: <Task Name>

## Problem Statement

[2-3 sentences describing what needs to be built and why]

## Requirements

### Functional
- [Clear, testable requirement]
- [Another requirement]

### Non-Functional
- [Performance, security, maintainability requirements]

### Out of Scope
- [Explicitly state what's NOT being built]

## Design

### Approach

[High-level description of the solution approach]

### Architecture

[Component diagram, file structure, or system layout]

### Key Design Decisions

**Decision 1: [Title]**
- **Problem:** [What decision needs to be made]
- **Options:** [2-3 options considered]
- **Choice:** [Selected option]
- **Rationale:** [Why this option was chosen]

[Repeat for other key decisions]

### Integration Points

[How this integrates with existing systems]

### Edge Cases

[Important edge cases to handle]

## Implementation Notes

### File Changes

- `path/to/file.ext` - [Brief description of changes]
- `path/to/new/file.ext` - [New file, what it does]

### Testing Strategy

[How to verify the implementation works]

### Risks and Mitigations

**Risk:** [Potential problem]
**Mitigation:** [How to address it]

## Next Steps

1. [Immediate next action]
2. [Following action]
3. [Final action]
```

**Design principles:**
- **Dense:** Pack information efficiently, avoid fluff
- **Specific:** Use concrete examples, not abstractions
- **Complete:** Address all requirements and edge cases
- **Actionable:** Implementation should be straightforward from this document

### 5. Validate Design

**Review checklist:**
- All requirements addressed?
- Design decisions documented with rationale?
- Integration points identified?
- Edge cases considered?
- Next steps clear?

**Output location:**
- Save to `plans/<job-name>/design.md`
- Create directory if needed

## Critical Constraints

- **Model:** This skill must use Opus for deep reasoning
- **Thoroughness:** Don't skip exploration or research phases
- **Density:** Design docs should be information-dense, not verbose
- **Specificity:** Use concrete examples and file paths
- **Completeness:** All design decisions must have documented rationale

## Output

**Primary artifact:** `plans/<job-name>/design.md`

**Handoff:** Design document serves as input to `/plan-adhoc` for creating execution runbook
