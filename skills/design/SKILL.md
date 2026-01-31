---
description: Entry point for implementation tasks. Triages complexity (simple/moderate/complex), then produces design documents for complex jobs or routes to planning for moderate ones.
allowed-tools: Task, Read, Write, Bash, Grep, Glob, WebSearch, WebFetch
user-invocable: true
---

# Design Skill

Produce dense design documents that guide implementation by downstream agents (Sonnet/Haiku).

## Mode Detection

**TDD Mode:** Test-first culture, user mentions TDD/tests, behavioral verification needed.
**General Mode:** Infrastructure, refactoring, migrations, prototypes. Default.

Mode determines downstream consumer: TDD → `/plan-tdd`, General → `/plan-adhoc`.

## Process

### 0. Complexity Triage

Before doing design work, assess whether design is actually needed:

**Simple (no design needed):**
- Single file, obvious implementation, no architectural decisions
- → Execute directly. Update session.md with what was done.

**Moderate (planning needed, not design):**
- Clear requirements, no architectural uncertainty, well-defined scope
- → Skip design. Route to `/plan-adhoc` (or `/plan-tdd` in TDD mode), which has its own tier assessment.

**Complex (design needed):**
- Architectural decisions, multiple valid approaches, uncertain requirements, significant codebase impact
- → Proceed with steps 1-6 below.

**Session state check:** If session has significant pending work (>5 tasks), suggest `/shelve` before proceeding.

---

### 1. Understand Request

Read `agents/design-decisions.md` for existing patterns. Clarify ambiguous requirements with user.

**Design decision escalation:** When facing architectural choices between approaches (e.g., "approach A vs B"), use `/opus-design-question` to consult an Opus subagent instead of asking the user. Only ask the user for subjective preferences, business logic, or scope changes.

### 2. Explore Codebase

**CRITICAL: Delegate exploration. Opus must not grep/glob/browse directly.**

Use Task tool with `subagent_type="Explore"` (or `"quiet-explore"`). Only use Read for specific files AFTER exploration identifies them.

### 3. Research (if needed)

WebSearch/WebFetch for external patterns, prior art, or specifications.

### 4. Create Design Document

**Output:** `plans/<job-name>/design.md`

**Content principles:**
- Dense, not verbose - downstream agents are intelligent
- Decisions with rationale, not just conclusions
- Concrete file paths and integration points
- Explicit scope boundaries (in/out)

**Structure guidance (adapt as needed):**
- Problem statement
- Requirements (functional, non-functional, out of scope)
- Architecture/approach
- Key design decisions with rationale
- Implementation notes (affected files, testing strategy)
- Next steps

**TDD mode additions:** Spike test strategy, confirmation markers for uncertain decisions, "what might already work" analysis.

### 5. Vet Design

**CRITICAL: Delegate to opus subagent for review.**

Use Task tool with `subagent_type="general-purpose"`, `model="opus"`:

```
Review plans/<job-name>/design.md for:
1. Completeness - Missing requirements or edge cases?
2. Clarity - Ambiguous decisions or insufficient rationale?
3. Feasibility - Implementation complexity realistic?
4. Consistency - Conflicts with existing patterns?

Return concise feedback with actionable fixes.
```

### 6. Apply Fixes

**Address all high and medium priority feedback from vet review.**

Update design.md with corrections. Low priority items can be deferred or documented as known limitations.

## Output Expectations

Design documents are consumed by planning agents (`/plan-tdd` or `/plan-adhoc`).

**Minimize designer output tokens** by relying on planner inference:
- Omit obvious details planners can infer
- Focus on non-obvious decisions and constraints
- Provide enough context for autonomous planning
- Flag areas requiring user confirmation

Large tasks require planning anyway - dense design output naturally aligns with planning needs.

## Constraints

- High-capability model only (deep reasoning required)
- Delegate exploration (cost/context management)
- Dense output (minimize designer output tokens)
