---
name: design
description: >-
  This skill should be used when the user invokes /design, requests
  architecture or implementation planning, or presents a task needing
  complexity triage. Triages simple/moderate/complex, produces design
  documents for complex jobs, routes moderate to /runbook.
allowed-tools: Task, Read, Write, Bash, Grep, Glob, WebSearch, WebFetch
user-invocable: true
---

# Triage Implementation Complexity

Produce dense design documents that guide implementation by downstream agents (Sonnet/Haiku).

## Downstream Consumer

All planning routes to `/runbook` (unified — handles both TDD and general phases).

Note which phases are behavioral (TDD) vs infrastructure (general) to guide per-phase type tagging during planning.

## Process

### 0. Complexity Triage

**Requirements-clarity gate:** Before any artifact reading or triage, validate requirements are actionable.

- If `requirements.md` exists: verify each FR/NFR has a concrete mechanism (not just a goal)
- If user request only: verify intent is clear enough to triage (ask if not)
- If requirements are vague or mechanism-free: route to `/requirements` before proceeding

**Rationale:** Triage reads artifacts that depend on requirements being clear. Vague requirements propagate through design into planning, producing mechanism-free specifications downstream agents cannot implement.

Before doing design work, assess whether design is actually needed.

**Artifact check:** Read plan directory (`plans/<job-name>/`) for existing artifacts:
- `design.md` exists → route to `/runbook`
- `outline.md` sufficient (concrete approach, no open questions, explicit scope, low coordination complexity) → skip to Phase B
- `outline.md` insufficient → resume from A.5 (revise) or A.6 (review)
- Otherwise → classify below

#### Triage Recall (D+B anchor)

Load triage-relevant decisions before classifying. This tool call is the structural anchor — prevents classification from being skipped or rationalized.

```bash
agent-core/bin/when-resolve.py "when behavioral code" "when complexity" "when triage" "when <domain-keyword>" ...
```

- Derive domain keywords from the task/problem description
- Always include: behavioral code, complexity, triage
- Add domain-specific keywords from the task context
- Purpose: surface codified decisions that constrain classification before it happens

#### Classification Criteria

Assess the task against these criteria. Classify only — do not route yet.

**Complex:**
- Architectural decisions, multiple valid approaches, uncertain requirements, significant codebase impact

**Moderate:**
- Clear requirements, no architectural uncertainty, well-defined scope
- Behavioral code changes: new functions, changed logic paths, conditional branches

**Simple:**
- Single file, obvious implementation, no architectural decisions
- **No behavioral code changes** — new functions, changed logic paths, conditional branches are Moderate regardless of conceptual simplicity

#### Classification Gate

**Structural check (D+B anchor):** If classification is borderline Simple/Moderate, verify with `Glob` or `Grep` on affected files to confirm whether behavioral code changes are involved (new functions, changed logic paths).

Produce this classification block before routing (visible output, not internal reasoning):
- **Classification:** [Simple / Moderate / Complex]
- **Behavioral code check:** Does this task add functions, change logic paths, or add conditional branches? [Yes → Moderate minimum / No]
- **Evidence:** Which criteria matched and which recall entries informed the decision

#### Routing

- **Simple →** Check for applicable skills and project recipes first. Skip design — all other operational rules (skills, project tooling, communication) remain in effect. Update session.md with what was done.
- **Moderate →** Skip design. Route to `/runbook`, which has its own tier assessment.
- **Complex →** Proceed with Phases A-C below.

**Companion tasks:** If session notes bundle additional work into this /design invocation ("address X during /design"), each companion task gets its own pass through Phase 0 — recall, classification, routing. The /design invocation is the venue; process is not optional. Route each workstream independently.

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
| 1. Local knowledge | Read `memory-index.md` (skip if already in context), keyword discovery → batch-resolve via `agent-core/bin/when-resolve.py` or read referenced files directly. `agents/decisions/*.md` always. `agents/plan-archive.md` when design overlaps with previously completed plans (prior art, integration points, affected modules). `agent-core/fragments/*.md` only when memory-index entries reference them. For small doc volumes, scout or Grep on decision/fragment directories is also valid. | Direct Read, agent-core/bin/when-resolve.py, scout, or Grep | Always (core), flexible method |
| 2. Key skills | `plugin-dev:*` skills | Skill invocation | When design touches plugin components (hooks, agents, skills, MCP) |
| 3. Context7 | Library documentation via Context7 MCP tools | Designer calls directly from main session (MCP tools unavailable in sub-agents), writes results to report file | When design involves external libraries/frameworks |
| 4. Local explore | Codebase exploration | Delegate to scout agent | Always for complex designs |
| 5. Web research | External patterns, prior art, specifications | WebSearch/WebFetch (direct in main session) | When local sources insufficient |

**Not all levels needed for every task.** Level 1 is always loaded. Levels 2-5 are conditional on task domain.

**No-requirements case:** When no requirements.md exists, derive domain keywords from user request. Memory-index's keyword-rich entries amplify thin user input through cross-references. Cast a wider net on Level 1 to compensate for weaker signal.

**Design decision escalation does NOT apply here.** Design sessions exist to make architectural decisions directly.

**Recall Artifact Generation**

Documentation findings from A.1 exist only in the current context window — they do not survive to downstream pipeline stages (runbook planning, orchestration, execution, review). Persist them as a recall artifact so all downstream consumers receive the designer's curated documentation context.

**Process:** After documentation loading completes, write `plans/<job>/recall-artifact.md`. The artifact captures entries discovered and read during A.1 — memory-index hits, decision files, skill content, Context7 results, exploration reports. Do not re-read source files; content is already in context from A.1's loading passes.

**Artifact format:** Structured markdown, one section per entry:

```markdown
## <Entry Heading Name>

**Source:** `<path/to/file.md>`
**Relevance:** <Why this entry matters for this design — 1-2 sentences>

<Key content excerpt — dense, not full text. Focus on decisions, constraints, and patterns the downstream consumer needs.>
```

**Selection criteria:** Include entries that informed design decisions or constrain implementation. Do not include entries that were read but proved irrelevant — the artifact is curated, not exhaustive. Do not fabricate relevance notes for entries that had no bearing on the design.

**Staleness:** The artifact reflects corpus state at design time. If documentation changes between design and execution, the artifact becomes stale — this is accepted. Re-running the design pass is the refresh mechanism, not mid-pipeline updates.

**Output:** `plans/<job>/recall-artifact.md`, alongside other design artifacts in the job directory.

#### A.2. Explore Codebase

**Delegate exploration when scope is open-ended or spans multiple unknown files.** Read directly when files are known and few (≤3 files). The goal is cost control — opus tokens on open-ended browsing are expensive, but launching an agent to read a known file costs more than reading it directly.

For delegated exploration: Use Task tool with `subagent_type="scout"`. Specify report path: `plans/<job-name>/reports/explore-<topic>.md`. Agent writes findings to file and returns filepath.

#### A.3-5. Research and Outline

**When external research needed** (Context7, web, grounding): Read `references/research-protocol.md` for Context7 usage, web research, grounding invocation, recall diff, and outline content/format guidance.

**When no external research needed:** Proceed directly to outline generation.

**Recall diff:** `Bash: agent-core/bin/recall-diff.sh <job-name>` — update artifact if codebase findings changed relevance.

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
Review plans/<job>/outline.md for completeness, clarity, and alignment with requirements.

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

**Direct execution criteria (all must hold):**
- All decisions pre-resolved (no open questions requiring feedback)
- All changes are prose edits or additive (no behavioral code changes)
- Insertion points or edit targets are identified (line-level or section-level)
- No cross-file coordination (edits are independent per file)
- No implementation loops (no test/build feedback required)

**If execution-ready** — offer direct execution. On confirmation:
1. Execute edits in current session
2. Delegate to `corrector` — include review-relevant entries from `plans/<job>/recall-artifact.md` in corrector prompt (failure modes, quality anti-patterns)
3. Invoke `/handoff [CONTINUATION: /commit]`

**If not execution-ready** — route to `/runbook`:
1. Commit design artifact (`outline.md` or `design.md`)
2. Invoke `/handoff [CONTINUATION: /commit]` — next pending task is `/runbook`

**If insufficient** — proceed to Phase C (full design generation).

**When to apply:** Small-to-moderate jobs where research (Phase A) fully resolved the approach and user discussion (Phase B) confirmed without introducing new complexity.

---

### Phase C: Generate Design

**Objective:** Produce full design document, review, fix, commit.

#### C.1. Create Design Document

**Recall diff:** `Bash: agent-core/bin/recall-diff.sh <job-name>`

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
Review plans/<job-name>/design.md for completeness, clarity, feasibility, and consistency.

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

**Direct execution criteria (all must hold):**
- All decisions pre-resolved (no open questions requiring feedback)
- All changes are prose edits or additive (no behavioral code changes)
- Insertion points or edit targets are identified (line-level or section-level)
- No cross-file coordination (edits are independent per file)
- No implementation loops (no test/build feedback required)

- **If execution-ready:** Execute edits, review (include recall artifact review entries in corrector prompt), then `/handoff [CONTINUATION: /commit]`
- **If not execution-ready:** Commit design artifact, then `/handoff [CONTINUATION: /commit]` — next pending task is `/runbook`

## Constraints

- High-capability model only (deep reasoning required)
- Delegate exploration (cost/context management)
- Dense output — omit obvious details planners can infer, focus on non-obvious decisions and constraints
- Design documents contain guidance (planners may adapt) and constraints (planners must follow literally). Classification tables are constraints.
