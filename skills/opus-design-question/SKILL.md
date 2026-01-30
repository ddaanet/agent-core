---
name: opus-design-question
description: This skill should be used when facing a design decision or architectural choice that would normally require user input, but where an Opus subagent consultation would provide expert guidance without blocking the user. Use when questions like "Should I use approach A or B?", "How should I structure this?", "What's the best way to handle X?" arise during implementation.
user-invocable: false
---

# Opus Design Question Skill

Consult an Opus subagent for design decisions and architectural guidance instead of blocking the user with questions.

## Purpose

During implementation, agents often encounter design questions that would traditionally require user input via AskUserQuestion. This skill provides an alternative: delegate the decision to an Opus subagent that can provide expert architectural guidance based on the codebase context and design principles.

**When to use this instead of AskUserQuestion:**
- Design decisions with clear architectural principles to apply
- Trade-off analysis between implementation approaches
- Pattern selection from established options
- Structural decisions within an already-defined scope

**When to still use AskUserQuestion:**
- User preference matters (subjective choices)
- Business logic or domain-specific decisions
- Unclear requirements needing clarification
- Scope changes or new features beyond current design

## Usage Pattern

### Step 1: Identify the Decision

Recognize when you're about to use AskUserQuestion for a design/architectural choice:

**Examples:**
- "Should I structure this as a class or functions?"
- "Which error handling pattern fits better here?"
- "How should I organize these modules?"
- "What's the right abstraction level for this component?"

### Step 2: Formulate Context for Opus

Prepare the decision context:
1. **Current situation**: What are you implementing?
2. **The decision**: What specific choice needs to be made?
3. **Options**: What are the 2-4 approaches you're considering?
4. **Constraints**: What design principles or requirements apply?
5. **Codebase context**: What existing patterns or files are relevant?

### Step 3: Invoke Opus Subagent

Use Task tool to launch an Opus agent with the design question:

```
Task(
  subagent_type="general-purpose",
  model="opus",
  description="Design decision for [brief description]",
  prompt="You are providing architectural guidance for a design decision.

## Context
[Describe the implementation context]

## Decision Needed
[State the specific question]

## Options Considered
1. [Option A with trade-offs]
2. [Option B with trade-offs]
3. [Option C if applicable]

## Constraints
- [Design principle 1]
- [Design principle 2]
- [Existing pattern: reference to code/docs]

## Your Task
Recommend the best approach and explain your reasoning:
1. Which option best fits the constraints?
2. Why is it superior to the alternatives?
3. Are there any important caveats or implementation notes?

Return a concise recommendation (1-2 paragraphs) that I can immediately act on."
)
```

### Step 4: Execute Recommendation

When Opus returns:
- Read the recommendation
- Apply the guidance immediately
- No need to confirm with user (Opus made the call)
- Document the decision if significant (in code comments or design docs)

## Example Workflow

**Scenario:** Implementing a new CLI command and unsure whether to use Click or argparse.

**Traditional approach (blocks user):**
```python
AskUserQuestion: "Which CLI framework should I use? Click or argparse?"
```

**Opus-design-question approach (non-blocking):**
```python
Task(
  subagent_type="general-purpose",
  model="opus",
  prompt="I'm implementing a new CLI command for the project.

Decision: Should I use Click or argparse?

Options:
1. Click - More concise, decorator-based, but adds dependency
2. argparse - Stdlib, no dependencies, more verbose

Constraints:
- Project uses Click for existing commands (see src/claudeutils/cli.py)
- Consistency with existing tooling is valued
- Minimal dependencies preferred but not required

Recommend which to use and why, considering project patterns."
)
```

**Opus returns:**
> "Use Click. The project already depends on Click (evident from src/claudeutils/cli.py) and has established patterns for Click-based commands. Consistency with existing commands is more valuable than the marginal benefit of avoiding the dependency, which you already have. New commands should follow the decorator-based pattern in cli.py for maintainability."

**Agent proceeds:** Implements using Click, following existing patterns.

## Integration with Workflows

**In TDD cycles:**
- When GREEN phase has multiple implementation approaches, consult Opus before coding
- Document Opus's recommendation in cycle notes if significant

**In runbook execution:**
- If a step has ambiguous implementation details, pause and consult Opus
- Include Opus's guidance in the execution report

**In direct implementation:**
- When you'd normally stop to ask user a design question, try Opus first
- Only escalate to user if Opus can't decide (genuinely needs user preference)

## When NOT to Use This Skill

**Don't use Opus subagent for:**
1. **User preferences**: "What should I name this variable?" → User might care
2. **Business logic**: "How should the discount be calculated?" → Domain-specific knowledge
3. **Scope decisions**: "Should I also add feature X?" → Changes requirements
4. **Ambiguous requirements**: "What should this function do?" → Need user clarification
5. **Trivial decisions**: "Should I use a dict or a class?" → Just pick based on context

**Use AskUserQuestion for those instead.**

## Best Practices

**Provide sufficient context to Opus:**
- Reference specific files/patterns in the codebase
- Include design principles from CLAUDE.md or design docs
- Mention constraints (performance, dependencies, etc.)
- Give 2-4 concrete options to evaluate

**Don't over-rely on Opus:**
- For straightforward decisions matching obvious patterns, just implement
- For truly subjective choices, ask user
- Opus is for architectural guidance, not micro-decisions

**Document significant decisions:**
- If Opus made a non-obvious architectural choice, note it in code comments
- Reference Opus's reasoning in commit messages if relevant
- Update design docs if the decision affects future work

## Benefits

**Unblocks implementation:**
- No waiting for user to answer design questions
- Maintains flow during execution
- User sees completed work instead of being interrupted mid-task

**Leverages Opus's strengths:**
- Architectural reasoning
- Trade-off analysis
- Pattern recognition from codebase
- Design principle application

**Reduces context switching:**
- User focused on high-level work
- Agent handles implementation details with expert consultation
- Only escalate truly user-dependent decisions

## Example Prompts for Opus

### Module Structure Decision
```
Context: Implementing new authentication system
Decision: Should auth logic live in single module or split by concern?
Options:
1. auth.py (single file, ~300 lines)
2. auth/ directory with login.py, session.py, validation.py
3. auth/ with models.py and handlers.py
Constraints:
- Project follows one-file-per-concern pattern (see src/utils/)
- Auth system has 3 distinct concerns: validation, session, credentials
Recommend structure.
```

### Error Handling Pattern
```
Context: Implementing file operations that can fail
Decision: Error handling strategy?
Options:
1. Raise exceptions, let caller handle
2. Return Result[T, Error] type
3. Return None on error, log internally
Constraints:
- Existing code raises exceptions (see src/file_ops.py)
- User facing errors should be clean
Recommend approach and explain trade-offs.
```

### Abstraction Level
```
Context: Refactoring duplicated code across 3 functions
Decision: What level of abstraction?
Options:
1. Extract helper function (simple, single-use)
2. Create reusable utility class (general-purpose)
3. Leave as-is with comments (YAGNI principle)
Constraints:
- Duplication is only across these 3 functions
- No anticipated future use cases
- Project prefers simple over clever
Recommend approach.
```

## Success Criteria

You've successfully used this skill when:
- ✓ Implementation continues without user interruption
- ✓ Design decision was made based on sound architectural reasoning
- ✓ Opus's recommendation aligns with project patterns and constraints
- ✓ You can explain the decision if user asks later

## Notes

This skill is about **maintaining forward momentum** during implementation while still getting expert design guidance. It's not about avoiding user input entirely - it's about recognizing which decisions need user involvement (preferences, requirements) vs. which can be delegated to architectural expertise (patterns, trade-offs, structure).

**Remember:** When in doubt, err on the side of asking the user. This skill is for clear architectural decisions within well-defined scope.
