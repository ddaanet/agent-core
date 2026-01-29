---
description: Opus design session for complex jobs with uncertain requirements
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

### 1. Understand Request

Read `agents/design-decisions.md` for existing patterns. Clarify ambiguous requirements with user.

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
