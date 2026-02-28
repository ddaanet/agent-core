---
name: design
description: >-
  Triage complexity and design implementation approach. Triggers on /design,
  architecture or implementation planning requests, or tasks needing
  complexity assessment. Triages simple/moderate/complex, produces design
  documents for complex jobs, routes moderate to /runbook.
allowed-tools: Task, Read, Write, Bash, Grep, Glob, WebSearch, WebFetch, Skill
user-invocable: true
---

# Design Implementation Approach

Produce dense design documents that guide implementation by downstream agents (Sonnet/Haiku).

## Downstream Consumers

- **Planning:** `/runbook` (unified — handles both TDD and general phases). Note which phases are behavioral (TDD) vs infrastructure (general) to guide per-phase type tagging.
- **Execution:** `/inline` when work is execution-ready (Phase B sufficiency gate, Phase C.5 execution readiness). Handles execution lifecycle: corrector, triage feedback, deliverable-review chain.

## Process

### 0. Complexity Triage

**Requirements-clarity gate (D+B anchor):** Before any artifact reading or triage, assess requirements completeness. Produce this assessment block (visible output, not internal reasoning):

- **Requirements source:** [requirements.md / user request / problem.md / brief.md]
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
- `outline.md` sufficient (concrete approach, no open questions, explicit scope, low coordination complexity) → skip to Phase B
- `outline.md` insufficient → resume from A.5 (revise) or A.6 (review)
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

#### Classification Gate

**Structural check (D+B anchor):** If classification is borderline Simple/Moderate, verify with `Glob` or `Grep` on affected files to confirm whether behavioral code changes are involved (new functions, changed logic paths).

Produce this classification block before routing (visible output, not internal reasoning):
- **Classification:** [Simple / Moderate / Complex / Defect]
- **Implementation certainty:** [High / Moderate / Low] — is approach known?
- **Requirement stability:** [High / Moderate / Low] — are FRs mechanism-specified?
- **Behavioral code check:** Does this task add functions, change logic paths, or add conditional branches? [Yes → Moderate minimum / No]
- **Work type:** [Production / Exploration / Investigation] — what does this deliver?
- **Artifact destination:** [production / agentic-prose / exploration / investigation / ephemeral]
- **Evidence:** Which criteria and recall entries informed the decision

**Classification persistence (C-2):** Write the classification block verbatim to `plans/<job>/classification.md`. This file is consumed by `triage-feedback.sh` for post-execution comparison (FR-5/FR-6).

#### Routing

- **Simple →** Lightweight recall-explore-execute:
  1. Recall: `claudeutils _recall resolve "when <domain-keyword>" ...` — resolve domain-relevant entries (single call, triggers from task context)
  2. Explore: if affected files not already known, `Glob`/`Grep` to identify targets
  3. Execute: check for applicable skills and project recipes first, then implement directly
  4. Update session.md with what was done
  Skip design — all other operational rules (skills, project tooling, communication) remain in effect.
- **Moderate →** Skip design. Route to `/runbook`, which has its own tier assessment.
- **Complex →** Proceed with Phases A-C below.
- **Defect →** Route to structured-bugfix workflow: reproduce → root-cause → fix → verify. Skip design — the investigation structure replaces architectural design.

**Companion tasks:** If session notes bundle additional work into this /design invocation ("address X during /design"), enumerate all bundled tasks before processing any:

1. List all bundled tasks explicitly
2. Each task gets its own Phase 0 pass with visible output block (Requirements-clarity → Triage Recall → Classification → Routing)
3. Only after all tasks are classified, proceed with execution per routing

The enumeration is the structural anchor — forces explicit acknowledgment of each task rather than silently merging them into the primary task's classification.

**Session state check:** If session has significant pending work (>5 tasks), suggest `/shelve` before proceeding.

---

### Phase A: Research + Outline

**Objective:** Load context, explore codebase, research external resources, produce plan outline.

#### A.0. Requirements Checkpoint

If `requirements.md` exists in job directory (`plans/<job-name>/requirements.md`):
- Read and summarize functional/non-functional requirements
- Note scope boundaries (in/out of scope)
- Carry requirements context into outline and design
- **Skill dependency scan:** Check if requirements mention creating agents, skills, hooks, or plugins → load corresponding `plugin-dev:*` skill immediately (don't defer to A.1)

If no requirements.md exists:
- Document requirements discovered during research
- Can be inline in design.md or separate requirements.md (designer's judgment)

**Skill dependency indicators:**
- "sub-agent", "delegate to agent", "agent definition" → `plugin-dev:agent-development`
- "skill", "invoke skill", "skill preloaded" → `plugin-dev:skill-development`
- "hook", "PreToolUse", "PostToolUse" → `plugin-dev:hook-development`
- "plugin", "MCP server" → `plugin-dev:plugin-structure`, `plugin-dev:mcp-integration`

**Anti-pattern:** Deferring skill loading to A.1 judgment when requirements explicitly mention agent/skill creation.

**Correct pattern:** Scan requirements for skill dependency indicators during A.0, load immediately.

**Rationale:** Skill content must be available for outline (A.5) and design (C.1) phases. Late loading causes missing context.

**Output:** Requirements summary + skill dependencies loaded, available for Phase A.5 (outline) and Phase C.1 (design).

#### A.1. Documentation Checkpoint

**Purpose:** Systematic documentation loading — replaces ad-hoc memory discovery.

**Hierarchy (each level is fallback when previous didn't answer):**

| Level | Source | How | When |
|-------|--------|-----|------|
| 1. Local knowledge | Execute `/recall all` protocol (deep + broad, topic-scoped). Covers memory-index, `agents/decisions/*.md`, `agents/plan-archive.md` when design overlaps with prior plans, `agent-core/fragments/*.md` when referenced. | `/recall all` | Always (core) |
| 2. Key skills | `plugin-dev:*` skills | Skill invocation | When design touches plugin components (hooks, agents, skills, MCP) |
| 3. Context7 | Library documentation via Context7 MCP tools | Designer calls directly from main session (MCP tools unavailable in sub-agents), writes results to report file | When design involves external libraries/frameworks |
| 4. Local explore | Codebase exploration | Delegate to scout agent | Always for complex designs |
| 5. Web research | External patterns, prior art, specifications | WebSearch/WebFetch (direct in main session) | When local sources insufficient |

**Not all levels needed for every task.** Level 1 is always loaded. Levels 2-5 are conditional on task domain.

**No-requirements case:** When no requirements.md exists, derive domain keywords from user request. Memory-index's keyword-rich entries amplify thin user input through cross-references. Cast a wider net on Level 1 to compensate for weaker signal.

**Design decision escalation does NOT apply here.** Design sessions exist to make architectural decisions directly.

**Recall Artifact Generation**

Documentation findings from A.1 exist only in the current context window — they do not survive to downstream pipeline stages (runbook planning, orchestration, execution, review). Persist them as a recall artifact so all downstream consumers resolve fresh content at consumption time.

**Process:** After documentation loading completes, write `plans/<job>/recall-artifact.md`. Entry keys only — no excerpts, no summaries. Downstream consumers batch-resolve via `claudeutils _recall resolve` to get current content.

**Artifact format:**

```markdown
# Recall Artifact: <Job Name>

Resolve entries via `claudeutils _recall resolve` — do not use inline summaries.

## Entry Keys

<trigger phrase> — <1-line relevance note>
<trigger phrase> — <1-line relevance note>
```

**Null artifact (no relevant entries):** Write `null — no relevant entries found` as the sole entry. Downstream consumers batch-resolve it via `claudeutils _recall resolve null` (silent exit) — the tool call anchors the gate without consumer-side empty-section handling. Augmenting consumers (/runbook Phase 0.5) remove the null entry when adding real ones.

**Selection criteria:** Include entries that informed design decisions or constrain implementation. Exclude entries read but proved irrelevant — the artifact is curated, not exhaustive.

**Output:** `plans/<job>/recall-artifact.md`, alongside other design artifacts in the job directory.

#### A.2. Explore Codebase

**Delegate exploration when scope is open-ended or spans multiple unknown files.** Read directly when files are known and few (≤3 files). The goal is cost control — opus tokens on open-ended browsing are expensive, but launching an agent to read a known file costs more than reading it directly.

For delegated exploration: Use Task tool with `subagent_type="scout"`. Specify report path: `plans/<job-name>/reports/explore-<topic>.md`. Agent writes findings to file and returns filepath.

#### A.2.5. Post-Explore Recall

Exploration surfaces codebase areas not caught by A.1's topic-based recall. Re-scan memory-index (already in context from A.1) for entries relevant to domains discovered during exploration.

**Gate anchor (mandatory tool call on both paths):**
- **New entries found:** `claudeutils _recall resolve "when <trigger>" ...` — resolve into context, then append entry keys to recall artifact via Edit if entries have forward value for downstream consumers (runbook planning, execution, review)
- **No new entries:** `claudeutils _recall resolve null` — no-op, proves gate was reached

#### A.3-4. Research

**When external research needed** (Context7, web, grounding): Read `references/research-protocol.md` for Context7 usage, web research, grounding invocation, and recall diff guidance.

**When no external research needed:** Skip to A.5.

**Research artifact (required when research conducted):** Write findings to `plans/<job>/reports/research-<topic>.md` — frameworks considered, findings per framework, gaps identified. This file is a cascading dependency: A.5 reads it, absence blocks outline generation.

**Recall diff:** `Bash: claudeutils _recall diff <job-name>` — update artifact if codebase findings changed relevance.

#### A.5. Outline

**Gate:** If research was conducted (A.3-4), verify `plans/<job>/reports/research-*.md` exists before proceeding.

Read `references/research-protocol.md` for outline content/format guidance.

**Output:** Write outline to `plans/<job>/outline.md` — approach, key decisions, open questions, scope boundaries.

**Escape hatch:** If user input already specifies approach, decisions, and scope (e.g., detailed problem.md), compress A+B by presenting outline and asking for validation in a single message.

#### Post-Outline Complexity Re-check

`Read plans/<job>/outline.md` — load the outline to ground re-assessment.

The outline resolves the architectural uncertainty that justified "complex" classification. Re-assess before continuing ceremony.

**Downgrade criteria (all must hold):**
- Changes additive, no implementation loops
- No open questions remain
- Scope boundaries explicit (IN/OUT enumerated)
- No cross-file coordination requiring sequencing

**If met:** Skip A.6. Proceed to Phase B with sufficiency assessment.

**If not met:** Continue to A.6.

#### A.6. FP-1 Checkpoint: Review Outline

**Objective:** Validate outline before presenting to user.

**Process:**

Delegate to `outline-corrector` using Task tool with `subagent_type="outline-corrector"`:

```
Review plans/<job>/outline.md — Preliminary Design Review (PDR) criteria:
- Approach meets requirements (traceability to FRs)
- Options selected with rationale (not "explore options")
- Risks and open questions identified
- Scope boundaries explicit (IN/OUT enumerated)

Include review-relevant entries from plans/<job>/recall-artifact.md if present (failure modes, quality anti-patterns).

Apply all fixes (critical, major, minor) directly to outline.md.

Write review report to: plans/<job>/reports/outline-review.md

Return only the filepath on success (with ESCALATION note if unfixable issues), or 'Error: [description]' on failure.
```

**Handle review outcome:**
- Read the review report from the returned filepath
- If ESCALATION noted: Address unfixable issues before proceeding to user presentation
- If all issues fixed: Proceed to Phase B (report is audit trail)

---

### Phase B: Iterative Discussion

**Protocol:** Read `references/discussion-protocol.md` for the full iterative discussion process (open outline, apply deltas, re-review, convergence guidance).

### Outline Sufficiency Gate

`Read plans/<job>/outline.md` — load the outline to ground sufficiency assessment.

After user validates the outline, assess whether it already contains enough specificity to skip design generation.

**Sufficiency criteria (all must hold):**
- Approach is concrete (specific algorithm/pattern chosen, not "explore options")
- Key decisions are resolved (no open questions remaining)
- Scope boundaries are explicit (IN/OUT enumerated)
- Affected files are identified
- No architectural uncertainty remains

**If sufficient** — present sufficiency assessment to user. The outline IS the design; confirm user agrees to skip design generation. On confirmation, assess execution readiness:

**Execution routing (work-type-aware):**

```
IF all prose edits, no implementation loops → direct execution
ELSE IF work type = Investigation → direct execution
ELSE IF work type = Exploration AND design resolved all questions → direct execution
ELSE (work type = Production AND behavioral code) → /runbook
```

**Direct execution criteria (all must hold for prose/investigation/exploration paths):**
- All decisions pre-resolved (no open questions requiring feedback)
- Insertion points or edit targets are identified (line-level or section-level)
- No cross-file coordination requiring sequencing
- No implementation loops (no test/build feedback required)
- Scope fits inline capacity (single session, single model)

Direct execution bypasses `/runbook` — this gate must assess both coordination complexity and capacity.

**If execution-ready** — offer direct execution. On confirmation, invoke `/inline plans/<job> execute`. Handles execution, corrector dispatch, triage feedback, and handoff continuation.

**If not execution-ready** — route to `/runbook`:
1. Commit design artifact (`outline.md` or `design.md`)
2. Invoke `/handoff [CONTINUATION: /commit]` — next pending task is `/runbook`

**If insufficient** — proceed to Phase C (full design generation).

**When to apply:** Small-to-moderate jobs where research (Phase A) fully resolved the approach and user discussion (Phase B) confirmed without introducing new complexity.

---

### Phase C: Generate Design

**Objective:** Produce full design document, review, fix, commit.

#### C.1. Create Design Document

**Recall diff:** `Bash: claudeutils _recall diff <job-name>`

Review the changed files list. Approach commitment, revised scope, or rejected alternatives change which implementation and testing entries are relevant. If files changed that affect which recall entries are relevant, update the artifact: add entries surfaced by the discussion, remove entries for approaches that were rejected. Write updated artifact back.

**Output:** `plans/<job-name>/design.md`

**Content rules:** Read `references/design-content-rules.md` for content principles, density checkpoint, agent-name validation, classification table format, structure guidance, requirements section format, TDD additions, references/documentation perimeter sections, and skill-loading/execution model directives.

#### C.2. Checkpoint Commit

**Objective:** Commit the design document before review.

**Process:** Stage and commit `plans/<job-name>/design.md` (and any reports from Phase A).

**Why:** Preserves design state before review cycle. Enables diffing original vs post-review version. Isolates review changes in separate commit for audit trail.

#### C.3. Review Design

**CRITICAL: Delegate to design-corrector for review.**

Use Task tool with `subagent_type="design-corrector"`:

```
Review plans/<job-name>/design.md — Critical Design Review (CDR) criteria:
- Decisions fully specified (implementer needs no inference)
- Interfaces and integration points defined
- Agent/tool names verified against disk
- Test strategy or verification approach specified
- Late-added requirements re-validated
- Each major decision includes accepted tradeoffs

Include review-relevant entries from plans/<job-name>/recall-artifact.md if present (failure modes, quality anti-patterns).

Write detailed review to: plans/<job-name>/reports/design-review.md

Return only the filepath on success, or 'Error: [description]' on failure.
```

The design-corrector (opus model) performs comprehensive architectural review and writes a structured report with critical/major/minor issues categorized.

#### C.4. Check for Unfixable Issues

**Read the review report** from the filepath returned by design-corrector.

The design-corrector applies all fixes (critical, major, minor) directly. This step handles residual issues:

- **No UNFIXABLE issues:** Proceed to C.5.
- **UNFIXABLE issues found:** Address manually or escalate to user.

**Re-review if needed:** If user manually addresses UNFIXABLE issues, re-delegate to design-corrector for verification.

#### C.5. Execution Readiness and Handoff

`Read plans/<job>/design.md` — load the design to ground execution-readiness assessment.

Design can resolve complexity — a job correctly classified as Complex may produce Simple execution. Assess whether the completed design can be executed directly or needs runbook planning.

**Execution routing (work-type-aware):**

```
IF all prose edits, no implementation loops → direct execution
ELSE IF work type = Investigation → direct execution
ELSE IF work type = Exploration AND design resolved all questions → direct execution
ELSE (work type = Production AND behavioral code) → /runbook
```

**Direct execution criteria (all must hold for prose/investigation/exploration paths):**
- All decisions pre-resolved (no open questions requiring feedback)
- Insertion points or edit targets are identified (line-level or section-level)
- No cross-file coordination requiring sequencing
- No implementation loops (no test/build feedback required)
- Scope fits inline capacity (single session, single model)

Direct execution bypasses `/runbook` — this gate must assess both coordination complexity and capacity.

- **If execution-ready:** Invoke `/inline plans/<job> execute`. Handles execution, corrector dispatch, triage feedback, and handoff continuation.
- **If not execution-ready:** Commit design artifact, then `/handoff [CONTINUATION: /commit]` — next pending task is `/runbook`

## Constraints

- High-capability model only (deep reasoning required)
- Delegate exploration (cost/context management)
- Dense output — omit obvious details planners can infer, focus on non-obvious decisions and constraints
- Design documents contain guidance (planners may adapt) and constraints (planners must follow literally). Classification tables are constraints.
