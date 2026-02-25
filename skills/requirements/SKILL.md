---
name: requirements
description: Capture requirements from conversation or guide structured elicitation. Produces requirements.md artifact for design/planning phases. Use when the user asks to "capture requirements", "document requirements", "what do I want to build", or starts discussing a feature without clear documentation.
allowed-tools: Read, Write, Glob, Grep, AskUserQuestion
user-invocable: true
---

# Capture Requirements

Dual-mode requirements capture: extract from conversation or elicit through semi-structured questions. Produces `plans/<job>/requirements.md` artifact consumed by `/design` and `/runbook`.

## Target Model

**Opus required.** Extract mode requires synthesizing nuanced conversation context; sonnet misses implicit requirements.

## Usage

```
/requirements <job-name>
```

Skill automatically detects appropriate mode based on conversation history.

## Mode Detection

**Primary signal:** `Glob: plans/<job>/requirements.md` — if file exists, Read it and use as base for update/refinement (extract mode with existing artifact). If absent, fall through to conversation heuristic.

**Conversation heuristic (fallback):**
- **Extract mode** — conversation contains substantive discussion (feature descriptions, constraints, scope)
- **Elicit mode** — fresh conversation or minimal context (no prior feature discussion, cold-start)

## Extract Mode Procedure

When conversation contains requirements signals:

### 1. Scan Conversation

Extract from conversation history:
- **Functional requirements:** What should the system do?
- **Non-functional requirements:** Performance, usability, constraints
- **Explicit constraints:** Technology, compatibility, architecture
- **Scope boundaries:** What's in vs out of scope
- **Dependencies:** Blocking work, prerequisites
- **Open questions:** Unresolved items mentioned

**Critical rule:** Extract from what was said, do NOT infer unstated requirements. Hallucination risk — if not discussed, flag as Open Question rather than inventing.

### 2. Lightweight Codebase Discovery

Quick scan to ground requirements (runs after extraction, so scan is targeted):

**Discovery actions** (guideline: ~5 tool calls, flexible based on complexity):
1. `Glob` for `plans/*/requirements.md` and `plans/*/design.md` — find related work
2. `Grep` for key terms from extracted requirements — check what exists
3. `Read` existing patterns in relevant area — inform constraints

**Boundaries:**
- Direct tool use only (Glob, Grep, Read)
- No agent delegation
- No Context7, no web research, no scout
- Purpose: prevent naive requirements (e.g., "add X" when X exists)
- Tool count is a guideline, not a hard limit — use judgment for complex domains

### 3. Structure Requirements

Format into standard artifact (see Standard Format section below):
- Number items sequentially within each section (FR-1, FR-2, ...)
- Include acceptance criteria for functional requirements
- Capture rationale for constraints
- Omit empty sections entirely

### 4. Gap Detection

Check for empty critical sections:

**Critical sections** (ask if empty):
- Functional Requirements — "What should the system do?"
- Out of Scope — "What should it NOT do?"

**Non-critical sections** (note absence, don't ask):
- NFRs, Constraints, Dependencies — many tasks genuinely have none

**Question budget (applies to both Extract and Elicit modes):**
- Extract mode: Maximum 3 gap-fill questions for empty critical sections
- Elicit mode: 4-6 total questions (section questions + adaptive follow-ups)

Use `AskUserQuestion` tool for gap-fill:
```
questions: [
  {
    question: "What should the system do? (Functional requirements)",
    header: "Functional",
    options: [
      // Generate context-relevant options from job name and conversation
      // Example for job "git-hook-validator":
      {label: "Validate hook scripts before commit", description: "Parse and check hooks for common errors"},
      {label: "Block commits with invalid hooks", description: "Fail commit if hooks malformed"},
      {label: "Report hook validation errors", description: "Show clear error messages for failures"},
      ...
    ],
    multiSelect: true
  }
]
```

### 5. Present Draft

Show user the structured requirements:
- Display artifact path
- Summarize sections populated
- Note Open Questions if any
- Ask: "Does this capture your requirements accurately?"

### 6. Write Artifact

After user validation:
- Write to `plans/<job>/requirements.md` (create directory if needed)
- Scan for skill dependencies (see Skill Dependency Scanning section)
- Suggest next step (see Default Exit section)

## Elicit Mode Procedure

When conversation lacks requirements context:

### 1. Semi-Structured Elicitation

Use `AskUserQuestion` for each critical section (Functional Requirements, Scope Boundaries) with domain-relevant options. Add optional Constraints/Dependencies questions if job suggests them. Adaptive follow-ups: 1-2 clarifying questions based on responses. Total budget: 4-6 questions.

### 2-6. Shared Steps

After elicitation, follow Extract mode steps 2-6 (Codebase Discovery, Structure, Gap Detection, Present Draft, Write Artifact).

## Standard Format

```markdown
# <Job Name>

## Requirements

### Functional Requirements
**FR-1: <requirement title>**
<description, acceptance criteria>

**FR-2: <requirement title>**
<description, acceptance criteria>

### Non-Functional Requirements
**NFR-1: <requirement title>**
<description>

### Constraints
**C-1: <constraint title>**
<rationale>

### Out of Scope
- <item> — <rationale>

### Dependencies
- <dependency> — <impact on implementation>

### Open Questions
- Q-1: <unresolved item — what needs investigation>

### References
- `plans/<job-name>/reports/explore-<topic>.md` — codebase exploration findings
- `plans/reports/<topic>.md` — grounding research synthesis
- [External Paper Title](url) — informed FR-2 scope decision
```

**Section rules:**
- Omit empty sections entirely (don't scaffold structure)
- Number identifiers sequentially within each section (FR-1, FR-2, ... not FR-1, FR-3)
- Open Questions captures items conversation didn't resolve → become Design Phase A research targets
- Dependencies flags blocking work, prerequisite plans, or external dependencies
- References track provenance — what research, external sources, or project artifacts informed the requirements. Include exploration reports, grounding research, external papers, prior plan reports. Omit if requirements came entirely from conversation.

## Skill Dependency Scanning

After writing artifact, scan requirements text for skill dependency indicators:

| Indicator | Skill to Flag |
|-----------|---------------|
| "sub-agent", "delegate to agent", "agent definition" | `plugin-dev:agent-development` |
| "skill", "invoke skill", "skill preloaded" | `plugin-dev:skill-development` |
| "hook", "PreToolUse", "PostToolUse" | `plugin-dev:hook-development` |
| "plugin", "MCP server" | `plugin-dev:plugin-structure` |

If indicators found, append to artifact:

```markdown
### Skill Dependencies (for /design)
- Load `plugin-dev:hook-development` before design (hooks mentioned in FR-2)
```

**Rationale:** Artifact-scoped scanning reduces A.0 scan time — planner reads requirements.md first, loads indicated skills immediately rather than scanning entire codebase.

## Default Exit

Present artifact path and suggest next step based on completeness:

```
Requirements written to: plans/<job>/requirements.md

Next steps (decision criteria):
- 0-2 open questions, all critical sections populated → `/design plans/<job>/`
- 3+ open questions or empty critical sections → Standalone (revisit when clearer)
- Very clear scope + simple (Tier 1/2) → `/runbook plans/<job>/requirements.md`
- User stated explicit next step → Use that path
```

**Workflow positioning:**
```
/requirements <job> → /design plans/<job>/ (seeds A.0)
/requirements <job> → /handoff (document intent for later)
/requirements <job> → /runbook plans/<job>/requirements.md (direct to planning)
/requirements <job> (standalone — capture intent, no immediate follow-up)
```

## Key Principles

- Extract from conversation, do not infer (hallucination risk)
- Gap-fill, not interrogation: max 3 questions (extract) or 4-6 (elicit)
- Omit empty sections — do not scaffold structure nobody will fill
- See `references/empirical-grounding.md` for research basis
