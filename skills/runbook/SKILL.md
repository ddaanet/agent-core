---
name: runbook
description: |
  Decompose a design into executable implementation steps. Triggers on /runbook or when
  a design needs step-by-step planning. Creates runbooks with per-phase typing
  (TDD cycles, general steps, or inline pass-through) for weak orchestrator execution.
allowed-tools: Task, Read, Write, Edit, Skill, Bash(mkdir:*, agent-core/bin/prepare-runbook.py, claudeutils _recall diff:*, echo:*|pbcopy)
requires:
  - Design document from /design
  - CLAUDE.md for project conventions (if exists)
outputs:
  - Execution runbook at plans/<job-name>/runbook.md
  - Ready for prepare-runbook.py processing
user-invocable: true
continuation:
  cooperative: true
  default-exit: ["/handoff --commit", "/commit"]
---

# Plan Implementation Steps

**Usage:** `/runbook plans/<job-name>/design.md`

Create detailed execution runbooks suitable for weak orchestrator agents. Transforms designs into structured runbooks with per-phase type tagging — behavioral phases get TDD cycles (RED/GREEN), infrastructure phases get general steps, prose/config phases pass through as inline.

**Workflow context:** Part of implementation workflow (see `agents/decisions/pipeline-contracts.md` for full pipeline): `/design` → `/runbook` → [runbook-corrector] → prepare-runbook.py → `/orchestrate`

## Per-Phase Type Model

Each phase in a runbook declares its type: `type: tdd`, `type: general` (default), or `type: inline`.

**Type determines:**
- **Expansion format:** TDD → RED/GREEN cycles. General → task steps with script evaluation. Inline → pass-through (no decomposition, no step files).
- **Review criteria:** TDD → TDD discipline. General → step quality. Inline → vacuity, density, dependency ordering (no step/script/TDD checks). LLM failure modes for ALL phases.
- **Orchestration:** TDD/general → per-step agent delegation. Inline → orchestrator-direct (no Task dispatch).

**Type does NOT affect:** Tier assessment, outline generation, consolidation gates, assembly (prepare-runbook.py auto-detects), checkpoints.

**Phase type tagging format in outlines:**
```markdown
### Phase 1: Core behavior (type: tdd)
- Cycle 1.1: Load configuration
- Cycle 1.2: Parse entries

### Phase 2: Skill definition updates (type: general)
- Step 2.1: Update SKILL.md frontmatter
- Step 2.2: Add new section

### Phase 3: Contract updates (type: inline)
- Add inline type row to pipeline-contracts.md type table
- Update eligibility criteria in workflow-optimization.md
```

prepare-runbook.py auto-detects per-file via headers (`## Cycle X.Y:` vs `## Step N.M:`). Inline phases have no step/cycle headers — detected by `(type: inline)` tag in phase heading. prepare-runbook.py skips step-file generation for inline phases and marks them `Execution: inline` in orchestrator-plan.md.

## Model Assignment

**Default heuristic:** Match model to task complexity.
- **Haiku:** File operations, scripted tasks, mechanical edits
- **Sonnet:** Semantic analysis, judgment, standard implementation
- **Opus:** Architecture, complex design decisions

**Artifact-type override:** Steps editing architectural artifacts require opus regardless of task complexity:
- Skills (`agent-core/skills/`)
- Fragments (`agent-core/fragments/`)
- Agent definitions (`agent-core/agents/`)
- Workflow decisions (`agents/decisions/workflow-*.md`)

These are prose instructions consumed by LLMs — wording directly determines downstream agent behavior. "Simple" edits to these files require nuanced understanding that haiku/sonnet cannot reliably provide.

This override applies to Tier 2 delegation (model parameter), Tier 3 step assignment (Execution Model field), and the Execution Model in Weak Orchestrator Metadata.

---

## Three-Tier Assessment

**Evaluate implementation complexity before proceeding. Assessment runs first, before any other work.**

### Assessment Criteria

Analyze the task and produce explicit assessment output:

```
**Tier Assessment:**
- Files affected: ~N
- Artifact destination: [production / agentic-prose / exploration / investigation / ephemeral]
- Open decisions: none / [list]
- Components: N (sequential / parallel / mixed)
- Cycles/steps estimated: ~N (rough count from design)
- Model requirements: single / multiple
- Session span: single / multi

**Tier: [1/2/3] — [Direct Implementation / Lightweight Delegation / Full Runbook]**
**Rationale:** [1-2 sentences]
```

**Destination-aware file counting:** Artifact destination (from Phase 0 classification or design) determines which convention set applies to file counting:

| Destination | File Count Basis | Cycle Conventions |
|-------------|-----------------|-------------------|
| Production (`src/`) | Include test mirrors, lint, module split | Full TDD cycles |
| Exploration (`plans/prototypes/`) | Script files only, no test mirrors | General steps (write, verify, iterate) |
| Agentic-prose (`agent-core/skills/`, `agent-core/fragments/`, `agents/`) | Skill files + behavior verification | Prose review cycles |
| Investigation (`plans/reports/`) | Report files only | General steps |

A single-file prototype assessed against exploration conventions → Tier 1. Same script assessed against production conventions → inflated count from test mirrors, lint setup, module structure.

When uncertain between tiers, prefer the lower tier (less overhead). Ask user only if genuinely ambiguous.

### Tier 1: Direct Implementation

**Criteria:**
- Design complete (no open decisions)
- All edits straightforward (<100 lines each)
- Total scope: <6 files *(ungrounded threshold — needs empirical calibration, see `agents/decisions/execution-strategy.md`)*
- Single session, single model
- No parallelization benefit

**Recall context (D+B anchor — mandatory tool call on both paths):**

- **Artifact exists:** Read `plans/<job>/recall-artifact.md`. Batch-resolve entries via `claudeutils _recall resolve "when <trigger>" ...`
- **No artifact** (moderate path skipped design): Read `agents/memory-index.md`, identify domain-relevant entries, batch-resolve via `claudeutils _recall resolve "when <trigger>" "how <trigger>" ...`
- **No artifact AND no relevant entries:** `claudeutils _recall resolve null` — no-op, proves gate was reached

Include review-relevant entries in corrector prompt — rationale format for sonnet/opus reviewers.

**Sequence:** Follow §Continuation (prepends `/inline plans/<job> execute`).

### Tier 2: Lightweight Delegation

**Criteria:**
- Design complete, scope moderate (6-15 files or 2-4 logical components) *(file thresholds ungrounded — needs calibration)*
- Work benefits from agent isolation but not full orchestration
- Components are sequential (no parallelization benefit)
- No model switching needed

**Recall context (D+B anchor — mandatory tool call on both paths):**

- **Artifact exists:** Read `plans/<job>/recall-artifact.md`. Batch-resolve entries via `claudeutils _recall resolve "when <trigger>" ...`
- **No artifact** (moderate path skipped design): Read `agents/memory-index.md`, identify domain-relevant entries, batch-resolve via `claudeutils _recall resolve "when <trigger>" "how <trigger>" ...`
- **No artifact AND no relevant entries:** `claudeutils _recall resolve null` — no-op, proves gate was reached

Include relevant entries in each delegation prompt — format per consumer model tier (constraint format for haiku, rationale for sonnet/opus). Include review-relevant entries in corrector prompt.

**Planning (before execution):**
- **TDD work (~4-10 cycles):** Plan cycle descriptions (lightweight — no full runbook format). Per-cycle sequencing: one RED, one GREEN, verify, then next cycle.
- **General work (6-15 files):** Single agent for cohesive work; break into 2-4 components only if logically distinct.

**Sequence:** After planning, follow §Continuation (prepends `/inline plans/<job> execute`).

**Design constraints are non-negotiable:**

When design specifies explicit classifications (tables, rules, decision lists):
1. Include them LITERALLY in the delegation prompt
2. Delegated agents must NOT invent alternative heuristics
3. Agent "judgment" means applying design rules to specific cases, not creating new rules

**Artifact-type model override:** When delegated work edits architectural artifacts (skills, fragments, agents, workflow decisions), use `model="opus"` in the Task call. See Model Assignment section.

**Key distinction from Tier 3:** No prepare-runbook.py, no orchestrator plan, no plan-specific agent. The planner acts as ad-hoc orchestrator.

**Handling agent escalations:**

When delegated agent escalates "ambiguity" or "design gap":
1. **Verify against design source** — Re-read the design document section
2. **If design provides explicit rules:** Resolve using those rules, do not accept the escalation
3. **If genuinely ambiguous:** Use `/opus-design-question` or ask user
4. **Re-delegate with clarification** if agent misread design

### Tier 3: Full Runbook

**Criteria:**
- Multiple independent steps (parallelizable)
- Steps need different models
- Long-running / multi-session execution
- Complex error recovery
- >15 files or complex coordination *(file threshold ungrounded — needs calibration)*
- >10 TDD cycles with cross-component dependencies *(cycle threshold ungrounded — needs calibration)*

**Sequence:** Read `references/tier3-outline-process.md` for the planning process overview and outline generation (Phases 0.5-0.95). *(Verb-oriented name: action the agent takes, not the plan artifact produced.)*

---

## Continuation

As the **final action** of this skill:

1. Read continuation from `additionalContext` (first skill in chain) or from `[CONTINUATION: ...]` suffix in Skill args (chained skills)
2. Prepend entries based on tier:
   - Tier 1/2: prepend `/inline plans/<job> execute`
   - Tier 3: no prepend (Phase 4 prepares artifacts; orchestration requires session restart)
3. If continuation present: peel first entry from (possibly modified) continuation, tail-call with remainder
4. If no continuation: default-exit — `/handoff --commit` → `/commit`

**CRITICAL:** Do NOT include continuation metadata in Task tool prompts.

**On failure:** Abort remaining continuation. Record in session.md Blockers: which phase failed, error category, remaining continuation orphaned.

