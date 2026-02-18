---
name: design
description: >-
  This skill should be used when the user asks to "design", "architect",
  "plan implementation", "/design", or presents an implementation task
  that needs complexity triage. Entry point for implementation tasks —
  triages complexity (simple/moderate/complex), then produces design
  documents for complex jobs or routes to planning for moderate ones.
allowed-tools: Task, Read, Write, Bash, Grep, Glob, WebSearch, WebFetch
user-invocable: true
---

# Design Skill

Produce dense design documents that guide implementation by downstream agents (Sonnet/Haiku).

## Downstream Consumer

All planning routes to `/runbook` (unified — handles both TDD and general phases).

Note which phases are behavioral (TDD) vs infrastructure (general) to guide per-phase type tagging during planning.

## Process

### 0. Complexity Triage

Before doing design work, assess whether design is actually needed.

**Artifact check:** Read plan directory (`plans/<job-name>/`) for existing artifacts:
- `design.md` exists → route to `/runbook`
- `outline.md` sufficient (concrete approach, no open questions, explicit scope, ≤3 files) → skip to Phase B
- `outline.md` insufficient → resume from A.5 (revise) or A.6 (review)
- Otherwise → triage below

**Simple (no design needed):**
- Single file, obvious implementation, no architectural decisions
- → Check for applicable skills and project recipes first. Skip design — all other operational rules (skills, project tooling, communication) remain in effect. Update session.md with what was done.

**Moderate (planning needed, not design):**
- Clear requirements, no architectural uncertainty, well-defined scope
- → Skip design. Route to `/runbook`, which has its own tier assessment.

**Complex (design needed):**
- Architectural decisions, multiple valid approaches, uncertain requirements, significant codebase impact
- → Proceed with Phases A-C below.

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
| 1. Local knowledge | `memory-index.md` for keyword discovery → read referenced files. `agents/decisions/*.md` always. `agents/plan-archive.md` when design overlaps with previously completed plans (prior art, integration points, affected modules). `agent-core/fragments/*.md` only when memory-index entries reference them. For small doc volumes, quiet-explore or Grep on decision/fragment directories is also valid. | Direct Read, quiet-explore, or Grep | Always (core), flexible method |
| 2. Key skills | `plugin-dev:*` skills | Skill invocation | When design touches plugin components (hooks, agents, skills, MCP) |
| 3. Context7 | Library documentation via Context7 MCP tools | Designer calls directly from main session (MCP tools unavailable in sub-agents), writes results to report file | When design involves external libraries/frameworks |
| 4. Local explore | Codebase exploration | Delegate to quiet-explore agent | Always for complex designs |
| 5. Web research | External patterns, prior art, specifications | WebSearch/WebFetch (direct in main session) | When local sources insufficient |

**Not all levels needed for every task.** Level 1 is always loaded. Levels 2-5 are conditional on task domain.

**Level 1 clarification:** Memory-index is an ambient awareness index — keyword-rich entries that surface relevant knowledge. It is NOT the only way to discover local knowledge. For targeted doc collection (e.g., "what do we know about agent patterns?"), the designer can also:
- Delegate quiet-explore to read and summarize `agents/decisions/` and `agent-core/fragments/`
- Use Grep to search for specific topics across decision/fragment files
- These approaches work well when the doc volume is small enough to read completely

**Flexibility:** The checkpoint is domain-aware, not prescriptive. Designer identifies what domain the task touches and loads relevant docs for that domain. No fixed "always read X" list beyond level 1 core.

**Design decision escalation does NOT apply here.** `/opus-design-question` is for planning/execution phases that hit unexpected architectural choices. Design sessions exist to make those decisions — the designer reasons through them directly.

#### A.2. Explore Codebase

**Delegate exploration when scope is open-ended or spans multiple unknown files.** Read directly when files are known and few (≤3 files). The goal is cost control — opus tokens on open-ended browsing are expensive, but launching an agent to read a known file costs more than reading it directly.

For delegated exploration: Use Task tool with `subagent_type="quiet-explore"`. Specify report path: `plans/<job-name>/reports/explore-<topic>.md`. Agent writes findings to file and returns filepath.

#### A.3-4. External Research (if needed)

**Context7:** Call MCP tools directly from main session (unavailable in sub-agents). Write results to report file: `plans/<job-name>/reports/context7-<topic>.md`.

**Web research:** WebSearch/WebFetch for external patterns, prior art, or specifications.

**Grounding:** When the design will produce a methodology, framework, scoring system, or taxonomy, invoke `/ground` to prevent confabulated structures. The ground skill runs parallel internal+external research branches and produces a grounded reference document in `plans/reports/`.

#### A.5. Produce Plan Outline

**Output:** Write outline to `plans/<job>/outline.md` (create directory if needed).

**Content:**
- Approach summary
- Key decisions
- Open questions
- Scope boundaries

**Example outline** (for reference — adapt to task):
```
Approach: Add rate limiting middleware to API gateway using token bucket algorithm.
Key decisions: Per-user limits (not global), Redis-backed counters, 429 response with Retry-After header.
Open questions: Should rate limits vary by endpoint? Should admin users be exempt?
Scope: API gateway only. Dashboard/monitoring out of scope.
```

**Escape hatch:** If user input already specifies approach, decisions, and scope (e.g., detailed problem.md), compress A+B by presenting outline and asking for validation in a single message.

#### Post-Outline Complexity Re-check

The outline resolves the architectural uncertainty that justified "complex" classification. Re-assess before continuing ceremony.

**Downgrade criteria (all must hold):**
- ≤3 files affected, changes additive
- No open questions remain
- Scope boundaries explicit (IN/OUT enumerated)
- No cross-module coordination

**If met:** Skip A.6. Proceed to Phase B with sufficiency assessment.

**If not met:** Continue to A.6.

#### A.6. FP-1 Checkpoint: Review Outline

**Objective:** Validate outline before presenting to user.

**Process:**

Delegate to `outline-review-agent` using Task tool with `subagent_type="outline-review-agent"`:

```
Review plans/<job>/outline.md for completeness, clarity, and alignment with requirements.

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

**Objective:** Validate approach with user before expensive design generation.

**Process:**
1. Open outline for user review: `open plans/<job>/outline.md`
2. User reads outline in editor, provides feedback in chat
3. Designer applies deltas to outline.md file (not inline conversation)
4. Re-review via outline-review-agent if significant changes made
5. Loop until user validates approach

**Plugin-topic detection (reminder):** If design involves Claude Code plugin components (hooks, agents, skills), note which skill to load before planning: "Plugin-topic: [component type] — load plugin-dev:[skill-name] before planning."

**Termination:** If user feedback fundamentally changes the approach (not refining it), restart Phase A with updated understanding. Phase B is for convergence, not exploration of new directions.

**Convergence guidance:** If after 3 rounds the outline is not converging, ask user whether to proceed with current state or restart with different constraints.

### Outline Sufficiency Gate

After user validates the outline, assess whether it already contains enough specificity to skip design generation.

**Sufficiency criteria (all must hold):**
- Approach is concrete (specific algorithm/pattern chosen, not "explore options")
- Key decisions are resolved (no open questions remaining)
- Scope boundaries are explicit (IN/OUT enumerated)
- Affected files are identified
- No architectural uncertainty remains

**If sufficient** — present sufficiency assessment to user. The outline IS the design; confirm user agrees to skip design generation. On confirmation:
1. Commit `outline.md` as the design artifact (no rename — `/runbook` accepts either `design.md` or `outline.md`)
2. Invoke `/handoff [CONTINUATION: /commit]` — records design completion, then commits

**If insufficient** — proceed to Phase C (full design generation).

**When to apply:** Small-to-moderate jobs where research (Phase A) fully resolved the approach and user discussion (Phase B) confirmed without introducing new complexity.

---

### Phase C: Generate Design

**Objective:** Produce full design document, review, fix, commit.

#### C.1. Create Design Document

**Output:** `plans/<job-name>/design.md`

**Content principles:**
- Dense, not verbose - downstream agents are intelligent
- Decisions with rationale, not just conclusions
- Concrete file paths and integration points
- Explicit scope boundaries (in/out)

**Density checkpoint:**

Before generating design, validate outline item granularity:
- **Too granular:** >8 items per phase, or adjacent items with <20 LOC delta each → collapse into parent item or merge adjacents
- **Too coarse:** Single item handling >3 unrelated concerns or spanning multiple module boundaries → split by concern
- **Heuristic:** items-per-phase x avg-LOC-per-item should fall in the 100-300 range. Below 100 suggests items are trivially small; above 300 suggests items are overloaded.
- Flag and fix before proceeding to design generation.

**Repetition helper prescription:**

When design specifies 5+ operations following the same pattern (e.g., "update field X in files A, B, C, D, E, F"), recommend extracting a helper function or script. Rationale: repeated manual operations multiply both token cost (each repetition consumes expansion + execution budget) and error rate (drift between repetitions increases with count). The 5-repetition threshold balances extraction overhead against repetition cost.

**Agent-name validation:**

Before finalizing design, verify all referenced agent names exist on disk:
- Glob `agent-core/agents/*.md`, `.claude/agents/*.md`, and `.claude/plugins/*/agents/*.md`
- Every agent name in the design must resolve to an actual file
- If an agent name doesn't exist: flag as design error, not an implementation detail to defer
- Prevention: catches naming mismatches (e.g., `outline-review-agent` vs `runbook-outline-review-agent`) before they propagate to planning and execution

**Late-addition completeness check:**

Requirements added after outline review (Phase B) must be re-validated before design generation:
- **Traceability:** Does the new requirement map to a specific outline item or design section?
- **Mechanism:** Does the new requirement specify a concrete implementation approach, not just a goal?
- If a late-added requirement lacks either: flag for completion before proceeding.
- Grounding: FR-18 added during a design session bypassed outline-level validation, resulting in a mechanism-free specification that downstream planners could not implement.

**Classification tables are binding:**

When design includes classification tables (e.g., "X is type A, Y is type B"), these are LITERAL constraints for downstream planners/agents, not interpretable guidelines. Planners must pass classifications through verbatim to delegated agents.

Format classification tables with explicit scope:
- Default behavior (what happens without markers)
- Opt-out mechanism (how to deviate from default)
- Complete enumeration (all cases covered)

**Structure guidance (adapt as needed):**
- Problem statement
- Requirements (functional, non-functional, out of scope)
- Architecture/approach
- Key design decisions with rationale
- Implementation notes (affected files, testing strategy)
- References (see below)
- Documentation Perimeter (see below)
- Next steps

**Requirements section format:**

When requirements.md exists in job directory, include traceability mapping:

```markdown
## Requirements

**Source:** `plans/<job-name>/requirements.md` (or inline if documented during design)

**Functional:**
- FR-1: [requirement] — addressed by [design decision/section]
- FR-2: [requirement] — addressed by [design decision/section]

**Non-functional:**
- NFR-1: [requirement] — addressed by [design decision/section]

**Out of scope:**
- [item] — rationale
```

Each requirement should map to a design element for downstream validation.

**TDD mode additions:** For designs with behavioral phases, include spike test strategy, confirmation markers for uncertain decisions, "what might already work" analysis.

**References section:**

Track research artifacts and external references that informed the design. Backward-looking provenance (what shaped this design), distinct from Documentation Perimeter (forward-looking — what the planner should read).

```markdown
## References

- `plans/<job-name>/reports/explore-<topic>.md` — codebase exploration findings
- `plans/reports/<topic>.md` — grounding research (if `/ground` invoked)
- [External Paper Title](url) — informed decision D-3
- Context7: `/org/project` — queried for hook configuration patterns
```

**Include when:** Any Phase A research produced reports, external sources were consulted, or `/ground` was invoked. Omit if design was based entirely on loaded internal documentation.

**Documentation Perimeter section:**

Include this section specifying what the planner should read before starting:

```markdown
## Documentation Perimeter

**Required reading (planner must load before starting):**
- `agents/decisions/architecture.md` — module patterns, path handling
- `agent-core/fragments/delegation.md` — quiet execution pattern
- `plans/{job-name}/reports/explore-{topic}.md` — exploration results

**Context7 references:**
- `/anthropics/claude-code` — hook configuration patterns (query: "PostToolUse hooks")

**Pipeline contracts:** `agents/decisions/pipeline-contracts.md` (for tasks producing runbooks)

**Additional research allowed:** Planner may do additional Context7 queries or exploration for technical implementation details not covered above.
```

**Rationale:** Designer has deepest understanding of what knowledge the task requires. Encoding this explicitly prevents planner from either under-reading (missing critical context) or over-reading (wasting tokens on irrelevant docs).

**Skill-loading directives:**

**Plugin-related topics (hooks, agents, skills, plugins):**
When the design involves Claude Code plugin components, include a skill-loading directive in "Next steps":
- Hooks → `Load plugin-dev:hook-development before planning`
- Agents → `Load plugin-dev:agent-development before planning`
- Skills → `Load plugin-dev:skill-development before planning`
- Plugin structure → `Load plugin-dev:plugin-structure before planning`
- MCP integration → `Load plugin-dev:mcp-integration before planning`

This ensures the planner has domain-specific guidance loaded before creating the runbook.

**Execution model directives:**

When the design involves modifying workflow definitions (`agents/decisions/workflow-*.md`), skill files (`agent-core/skills/`), or agent procedures (`agent-core/agents/`), include an execution directive in "Next steps":
- Workflow/skill/agent edits: opus required

Ensures architectural artifacts get appropriate scrutiny during execution, not just planning.

#### C.2. Checkpoint Commit

**Objective:** Commit the design document before vet review.

**Process:** Stage and commit `plans/<job-name>/design.md` (and any reports from Phase A).

**Why:** Preserves design state before vet review cycle. Enables diffing original vs post-vet version. Isolates vet changes in separate commit for audit trail.

#### C.3. Vet Design

**CRITICAL: Delegate to design-vet-agent for review.**

Use Task tool with `subagent_type="design-vet-agent"`:

```
Review plans/<job-name>/design.md for completeness, clarity, feasibility, and consistency.

Write detailed review to: plans/<job-name>/reports/design-review.md

Return only the filepath on success, or 'Error: [description]' on failure.
```

The design-vet-agent (opus model) performs comprehensive architectural review and writes a structured report with critical/major/minor issues categorized.

#### C.4. Check for Unfixable Issues

**Read the review report** from the filepath returned by design-vet-agent.

The design-vet-agent applies all fixes (critical, major, minor) directly. This step handles residual issues:

- **No UNFIXABLE issues:** Proceed to C.5.
- **UNFIXABLE issues found:** Address manually or escalate to user.

**Re-vet if needed:** If user manually addresses UNFIXABLE issues, re-delegate to design-vet-agent for verification.

#### C.5. Handoff and Commit

**CRITICAL: As the final action, invoke `/handoff --commit`.**

This tail-call chains:
1. `/handoff` updates session.md with completed design work
2. Tail-calls `/commit` which commits the design document
3. `/commit` displays STATUS showing next pending task

The next pending task will typically be the planning phase (`/runbook`).

**Why:** Universal tail behavior ensures consistent workflow termination. User always sees what's next.

## Output Expectations

Design documents are consumed by the planning skill (`/runbook`).

**Minimize designer output tokens** by relying on planner inference:
- Omit obvious details planners can infer
- Focus on non-obvious decisions and constraints
- Provide enough context for autonomous planning
- Flag areas requiring user confirmation

Large tasks require planning anyway - dense design output naturally aligns with planning needs.

**Binding constraints for planners:**

Design documents contain two types of content:
1. **Guidance** — Rationale, context, recommendations (planners may adapt)
2. **Constraints** — Classification tables, explicit rules, scope boundaries (planners must follow literally)

Classification tables are constraints. When the table says "### Title is semantic," that's not a suggestion — it's a specification the planner must enforce.

## Constraints

- High-capability model only (deep reasoning required)
- Delegate exploration (cost/context management)
- Dense output (minimize designer output tokens)
