---
name: opus-design-question
description: >
  REQUIRED instead of AskUserQuestion for design/architectural decisions.
  When you face a choice between approaches (A vs B), trade-off analysis,
  pattern selection, or structural decisions — use this skill to consult
  Opus instead of asking the user. Only ask the user for subjective
  preferences, business logic, scope changes, or unclear requirements.
user-invocable: false
---

# Consult Opus for Design Decisions

Delegate design decisions to an Opus subagent. Routing criteria (when to use this vs AskUserQuestion) are in the always-loaded `design-decisions.md` fragment.

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

