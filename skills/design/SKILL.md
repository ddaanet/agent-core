---
name: design
description: >-
  Triage complexity and design implementation approach. Triggers on /design,
  architecture or implementation planning requests, or tasks needing
  complexity assessment. Triages simple/moderate/complex, produces design
  documents for complex jobs, routes moderate to /runbook.
allowed-tools: Task, Read, Write, Bash, Grep, Glob, WebSearch, WebFetch, Skill
user-invocable: true
continuation:
  cooperative: true
  default-exit: ["/handoff", "/commit"]
---

# Design Implementation Approach

Produce dense design documents that guide implementation by downstream agents (Sonnet/Haiku).

## Downstream Consumers

- **Planning:** `/runbook` (unified — handles both TDD and general phases). Note which phases are behavioral (TDD) vs infrastructure (general) to guide per-phase type tagging.
- **Execution:** `/inline` when work is execution-ready (Phase B sufficiency gate, Phase C.5 execution readiness). Handles execution lifecycle: corrector, triage feedback, deliverable-review chain.

## Process

### 0. Complexity Triage

**Requirements-clarity gate (D+B anchor):** Before any artifact reading or triage, assess requirements completeness. Produce this assessment block (visible output, not internal reasoning):

- **Requirements source:** [requirements.md / user request / brief.md]
- **Completeness:** [Each FR has concrete mechanism: Y/N] [Each NFR has measurable criterion: Y/N]
- **Routing:** [Proceed to triage / Route to `/requirements`]

Assessment rules:
- `requirements.md` exists: verify each FR/NFR has a concrete mechanism (not just a goal)
- User request only: verify intent is clear enough to triage (ask if not)
- Vague or mechanism-free: route to `/requirements` before proceeding

**Rationale:** Triage reads artifacts that depend on requirements being clear. Vague requirements propagate through design into planning, producing mechanism-free specifications downstream agents cannot implement. Structured output anchors the routing decision in observable evidence (IEEE 29148 validation activity principle).

Before doing design work, assess whether design is actually needed.

**Artifact check:** Read plan directory (`plans/<job-name>/`) for existing artifacts:
- `design.md` exists → route to `/runbook`
- `outline.md` is multi-sub-problem (contains individually-scoped sub-problems with dependency graph and per-sub-problem readiness routing) → Read `references/write-outline.md`, skip to multi-sub-problem sufficiency gate
- `outline.md` sufficient (concrete approach, no open questions, explicit scope, low coordination complexity) → Read `references/write-outline.md`, skip to outline sufficiency gate
- `outline.md` insufficient → Read `references/write-outline.md`, resume from A.5 (revise) or A.6 (review)
- Otherwise → classify below

#### Triage Recall (D+B anchor)

Load triage-relevant decisions before classifying. This tool call is the structural anchor — prevents classification from being skipped or rationalized.

```bash
claudeutils _recall resolve "when behavioral code" "when complexity" "when triage" "when <domain-keyword>" ...
```

- Derive domain keywords from the task/problem description
- Always include: behavioral code, complexity, triage
- Add domain-specific keywords from the task context
- Purpose: surface codified decisions that constrain classification before it happens

#### Classification Criteria

Assess two axes (Stacey Matrix-grounded), then classify. Classify only — do not route yet.

**Axes:**
1. **Implementation certainty** — is the approach known? Prior art in codebase? Known technique?
2. **Requirement stability** — are FRs agreed and mechanism-specified? Scope bounded?

**Complex:** Either axis low. Architectural decisions with multiple valid approaches, uncertain or evolving requirements, significant codebase impact.

**Moderate:** Both axes moderate-to-high. Clear requirements, no architectural uncertainty, well-defined scope. Behavioral code changes: new functions, changed logic paths, conditional branches.

**Simple:** Both axes high. Single file, obvious implementation, no architectural decisions. **No behavioral code changes** — new functions, changed logic paths, conditional branches are Moderate regardless of conceptual simplicity.

**Defect:** Observed behavior ≠ expected behavior. Route to structured-bugfix regardless of apparent complexity — the investigation structure replaces architectural design. Cynefin Complicated domain: cause analyzable, fix knowable, but analysis must be structured to prevent premature-closure bias.

#### Work Type Assessment

Assess work type alongside complexity — independent dimension (XP spike/story, Boehm throwaway/evolutionary). Work type determines execution ceremony (quality obligations); complexity determines design ceremony.

| Work Type | Diagnostic Question | Deliverable | Done Criteria |
|-----------|-------------------|-------------|---------------|
| **Production** | Does this deliver capability to users/agents? | Working feature, behavior change | Tested, linted, reviewed, integrated |
| **Exploration** | Does this produce knowledge or validate an approach? | Prototype, spike, feasibility answer | Functional, produces intended learning |
| **Investigation** | Does this produce a decision or analysis? | Report, decision entry, requirements | Accurate, complete, actionable |

**Assessment signals:**
- Explicit constraints: "prototype first," "spike," "investigate," "explore"
- Artifact destination: `plans/prototypes/` → Exploration, `plans/reports/` → Investigation, `src/` → Production
- Requirement framing: "can we...?" → Exploration, "build X" → Production, "what is...?" → Investigation
- If ambiguous, default to Production (highest ceremony — safe default)

**Artifact destination** informs quality obligations (Boehm throwaway vs evolutionary prototype distinction):

| Destination | Paths | Quality Obligations |
|------------|-------|-------------------|
| **production** | `src/`, `agent-core/bin/`, `agent-core/lib/` | Tests, lint, module structure, review |
| **agentic-prose** | `agent-core/skills/`, `agent-core/fragments/`, `agent-core/agents/`, `agents/` | Wording quality, behavioral verification |
| **exploration** | `plans/prototypes/`, `plans/spikes/` | Functional, documented purpose, no test mirrors |
| **investigation** | `plans/reports/`, `agents/decisions/` | Accuracy, completeness, grounding |
| **ephemeral** | `tmp/` | None |

#### Composite Task Decomposition

**Before classifying:** If the input artifact contains multiple discrete work items (deliverable review findings, PR review comments, multi-FR implementation list), decompose into per-item classification:

1. Enumerate all discrete items from the input artifact
2. Produce a per-item behavioral code check (does this item add functions, change logic paths, or add conditional branches?)
3. Classify each item individually — any item that is behavioral elevates to Moderate minimum for that item
4. Route per-item: Simple items can batch, Moderate+ items get their own routing

**Why:** Batch classification averages heterogeneous items. A behavioral code change gets masked by non-behavioral siblings in the same group.

**Distinct from companion tasks** (below). Companion tasks handle explicit user bundling in session notes. Composite tasks handle implicit bundling by the task's nature — multiple items within a single input artifact.

#### Classification Gate

**Structural check (D+B anchor):** If classification is borderline Simple/Moderate, verify with `Glob` or `Grep` on affected files to confirm whether behavioral code changes are involved (new functions, changed logic paths).

Produce this classification block before routing (visible output, not internal reasoning — **per-item if composite**):
- **Classification:** [Simple / Moderate / Complex / Defect]
- **Implementation certainty:** [High / Moderate / Low] — is approach known?
- **Requirement stability:** [High / Moderate / Low] — are FRs mechanism-specified?
- **Behavioral code check:** Does this task add functions, change logic paths, or add conditional branches? [Yes → Moderate minimum / No]
- **Work type:** [Production / Exploration / Investigation] — what does this deliver?
- **Artifact destination:** [production / agentic-prose / exploration / investigation / ephemeral]
- **Evidence:** Which criteria and recall entries informed the decision

**Classification persistence (C-2):** Write the classification block verbatim to `plans/<job>/classification.md`. This file is consumed by `triage-feedback.sh` for post-execution comparison (FR-5/FR-6).

#### Routing

- **Simple →** Lightweight recall-explore, then chain to `/inline`:
  1. Recall: `claudeutils _recall resolve "when <domain-keyword>" ...` — resolve domain-relevant entries (single call, triggers from task context)
  2. Explore: if affected files not already known, `Glob`/`Grep` to identify targets
  3. Execute: check for applicable skills and project recipes first, then implement directly
  4. Follow §Continuation (prepends `/inline plans/<job> execute`)
  Skip design — all other operational rules (skills, project tooling, communication) remain in effect.
- **Moderate →** Read affected files to ground brief against actual codebase state, then generate execution artifact:

  **Agentic-prose path** (artifact destination = `agentic-prose`):
  1. **Code reading:** Read affected files enumerated in the brief. Resolve gaps between brief assumptions and actual codebase state.
  2. Read `references/write-inline-plan.md`. **Generate** `plans/<job>/inline-plan.md` using that format.
  3. **Proof:** Invoke `/proof plans/<job>/inline-plan.md` (no corrector — scope completeness is domain knowledge, not structural checking)
  4. **Route (after /proof approval):** follow §Continuation (prepends `/inline plans/<job> execute`)

  **Non-prose path** (all other artifact destinations):
  1. **Code reading:** Read affected files enumerated in the brief. Resolve gaps between brief assumptions and actual codebase state.
  2. **Generate** `plans/<job>/outline.md` using lightweight format (scope, per-file changes, dependencies, IN/OUT boundaries)
  3. **Proof:** Invoke `/proof plans/<job>/outline.md` (outline-corrector dispatched by /proof on revise/kill)
  4. **Route (after /proof approval):** follow §Continuation (prepends `/runbook plans/<job>`)
- **Complex →** Read `references/write-outline.md` for Phase A (research + outline) and Phase B (user validation + outline sufficiency gate). *(Verb-oriented name: action the agent takes, not the artifact produced.)*
- **Defect →** Route to structured-bugfix workflow: reproduce → root-cause → fix → verify. Skip design — the investigation structure replaces architectural design.

**Companion tasks:** If session notes bundle additional work into this /design invocation ("address X during /design"), enumerate all bundled tasks before processing any:

1. List all bundled tasks explicitly
2. Each task gets its own Phase 0 pass with visible output block (Requirements-clarity → Triage Recall → Classification → Routing)
3. Only after all tasks are classified, proceed with execution per routing

The enumeration is the structural anchor — forces explicit acknowledgment of each task rather than silently merging them into the primary task's classification.

**Session state check:** If session has significant pending work (>5 tasks), suggest `/shelve` before proceeding.

## Author-Corrector Coupling

When a design modifies an "author" skill (a skill whose output is reviewed by a corrector), check coupled dependencies before completing the design:

1. Identify the corrector from the transformation table (T1-T6.5 in `agents/decisions/pipeline-contracts.md`)
2. Check: does the corrector's review criteria need corresponding update?
3. Check: does any mechanical validator need update?
4. Include corrector/validator updates in the same design scope

**Dependency mapping:**

| Author Skill/Artifact | Corrector | Validator |
|----------------------|-----------|-----------|
| /design (outline format) | outline-corrector | -- |
| /runbook (tdd-cycle-planning.md) | runbook-corrector (/review-plan) | validate-runbook.py |
| /runbook (general-patterns.md) | runbook-corrector (/review-plan) | validate-runbook.py |
| /requirements (standard format) | -- (user-reviewed) | -- |

**Visible output (mandatory):** "Author change: X. Coupled corrector: Y. Update needed: yes/no." This block forces awareness of coupling — designers check the table, not silently skip it.

## Continuation

As the **final action** of this skill:

1. Read continuation from `additionalContext` (first skill in chain) or from `[CONTINUATION: ...]` suffix in Skill args (chained skills)
2. Prepend entries based on routing outcome:
   - Moderate (non-prose): prepend `/runbook plans/<job>`
   - Simple, Moderate (agentic-prose), or execution-ready (B gate or C.5): prepend `/inline plans/<job> execute`
   - Not execution-ready: no prepend
3. If continuation present: peel first entry from (possibly modified) continuation, tail-call with remainder
4. If no continuation: default-exit — `/handoff` → `/commit`

**CRITICAL:** Do NOT include continuation metadata in Task tool prompts.

**On failure:** Abort remaining continuation. Record in session.md Blockers: which phase failed, error category, remaining continuation orphaned.
