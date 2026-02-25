---
name: runbook
description: |
  This skill should be used when the user invokes /runbook or needs a design
  decomposed into executable steps. Creates runbooks with per-phase typing
  (TDD cycles, general steps, or inline pass-through) for weak orchestrator execution.
allowed-tools: Task, Read, Write, Edit, Skill, Bash(mkdir:*, agent-core/bin/prepare-runbook.py, agent-core/bin/recall-diff.sh, echo:*|pbcopy)
requires:
  - Design document from /design
  - CLAUDE.md for project conventions (if exists)
outputs:
  - Execution runbook at plans/<job-name>/runbook.md
  - Ready for prepare-runbook.py processing
user-invocable: true
---

# Create Execution Runbooks

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
- Open decisions: none / [list]
- Components: N (sequential / parallel / mixed)
- Cycles/steps estimated: ~N (rough count from design)
- Model requirements: single / multiple
- Session span: single / multi

**Tier: [1/2/3] — [Direct Implementation / Lightweight Delegation / Full Runbook]**
**Rationale:** [1-2 sentences]
```

When uncertain between tiers, prefer the lower tier (less overhead). Ask user only if genuinely ambiguous.

### Tier 1: Direct Implementation

**Criteria:**
- Design complete (no open decisions)
- All edits straightforward (<100 lines each)
- Total scope: <6 files
- Single session, single model
- No parallelization benefit

**Recall context:** Read `plans/<job>/recall-artifact.md` if it exists. If no artifact exists (moderate path skipped design), do lightweight recall before exploring:

1. `agent-core/bin/when-resolve.py "when <trigger>" "how <trigger>" ...` — resolve domain-relevant entries using keywords from design/user request (single call, multiple entries). Read `memory-index.md` first if triggers not known from context.

Include review-relevant entries in corrector prompt — rationale format for sonnet/opus reviewers.

**Sequence:**
1. Implement changes directly using Read/Write/Edit tools
2. Delegate to review agent for review
3. Apply all fixes from review
4. Tail-call `/handoff --commit`

**Behavioral code changes:** Write one RED test, make it GREEN, verify, then write the next RED test. Per-cycle sequencing applies even without runbook ceremony — batching all REDs then all GREENs skips the incremental verification that catches wiring mistakes between layers.

### Tier 2: Lightweight Delegation

**Criteria:**
- Design complete, scope moderate (6-15 files or 2-4 logical components)
- Work benefits from agent isolation but not full orchestration
- Components are sequential (no parallelization benefit)
- No model switching needed

**Recall context:** Read `plans/<job>/recall-artifact.md` if it exists. If no artifact exists, do lightweight recall before exploring:

1. `agent-core/bin/when-resolve.py "when <trigger>" "how <trigger>" ...` — resolve domain-relevant entries using keywords from design/user request. Read `memory-index.md` first if triggers not known from context.

Include relevant entries in each delegation prompt — format per consumer model tier (constraint format for haiku, rationale for sonnet/opus). Include review-relevant entries in corrector prompt.

**For TDD work (~4-10 cycles):**
- Plan cycle descriptions (lightweight — no full runbook format)
- For each cycle: delegate via `Task(subagent_type="test-driver", model="haiku", prompt="...")` with context included in prompt (requires test-driver agent definition)
- Per-cycle sequencing: one RED → one GREEN → verify, then next cycle. Do not batch multiple REDs before GREENs.
- Intermediate checkpoints: every 3-5 delegated cycles, run tests and review accumulated changes

**For general work (6-15 files):**
- Delegate work via `Task(subagent_type="artisan", model="haiku", prompt="...")` with relevant context from design included in prompt (standard delegation pattern — agent executes and reports to file)
- Single agent for cohesive work; break into 2-4 components only if logically distinct

**Common tail:**
- After delegation complete: delegate to review agent for review
- Apply all fixes from review
- Tail-call `/handoff --commit`

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
- >15 files or complex coordination
- >10 TDD cycles with cross-component dependencies

**Sequence:** Planning process below — existing pipeline unchanged.

---

## Planning Process (Tier 3 Only)

**Full process detail:** Read `references/tier3-planning-process.md` for Phases 0.5-3.5 (discovery, outline generation, consolidation gates, simplification, complexity check, sufficiency check, phase-by-phase expansion, assembly, holistic review, pre-execution validation).

**Process overview:**
- Phase 0.5: Discover codebase structure, augment recall artifact, verify file locations
- Phase 0.75: Generate runbook outline with quality verification and corrector review
- Phase 0.85: Consolidation gate — merge trivial phases with adjacent complexity
- Phase 0.86: Simplification pass — delegate to `runbook-simplifier`
- Phase 0.9: Complexity check with callback mechanism
- Phase 0.95: Outline sufficiency check (lightweight orchestration exit if `## Execution Model` present)
- Phase 1: Phase-by-phase expansion with per-phase type-aware review
- Phase 2: Assembly validation and metadata preparation
- Phase 2.5: Consolidation gate — merge isolated trivial items post-assembly
- Phase 3: Final holistic cross-phase review via `runbook-corrector`
- Phase 3.5: Pre-execution validation via `validate-runbook.py`
- Phase 4: Prepare artifacts and handoff

**TDD cycle planning:** When expanding TDD phases in Phase 1, Read `references/tdd-cycle-planning.md` for RED/GREEN specification formats, assertion quality requirements, cycle numbering, investigation prerequisites, dependency assignment, and stop conditions.

**Conformance validation:** When design includes external references, Read `references/conformance-validation.md` for mandatory validation item requirements.

---

### Phase 4: Prepare Artifacts and Handoff

**CRITICAL: This step is MANDATORY. Use `prepare-runbook.py` to create execution artifacts.**

**Why:** Context isolation. Each step gets a fresh agent with ONLY common context and the specific step — no accumulated transcript.

**Step 1: Run prepare-runbook.py** with sandbox bypass:
```bash
agent-core/bin/prepare-runbook.py plans/{name}/runbook.md
# MUST use dangerouslyDisableSandbox: true (writes to .claude/agents/)
```
If script fails: STOP and report error.

**Step 2: Copy orchestrate command to clipboard:**
```bash
echo -n "/orchestrate {name}" | pbcopy
```

**Step 3: Tail-call `/handoff --commit`**

This:
- Hands off session context (marks planning complete, adds orchestration as pending)
- Then tail-calls `/commit` which commits everything and displays next pending task

Next pending task instructs: "Restart session, paste `/orchestrate {name}` from clipboard."

**Why restart:** prepare-runbook.py creates a new agent in `.claude/agents/`. Claude Code discovers agents at session start.

---

## Checkpoints

Checkpoints are verification points between phases. They validate accumulated work and create commit points.

**Two checkpoint tiers:**

**Light checkpoint** (Fix + Functional):
- **Placement:** Every phase boundary
- **Process:**
  1. **Fix:** Run `just dev`, sonnet artisan diagnoses and fixes, commit when passing
  2. **Functional:** Sonnet reviews implementations against design
     - Check: Real implementations or stubs? Functions compute or return constants?
     - If stubs found: STOP, report which need real behavior
     - If all functional: proceed

**Full checkpoint** (Fix + Review + Functional):
- **Placement:** Final phase boundary, or phases marked `checkpoint: full`
- **Process:**
  1. **Fix:** Run `just dev`, sonnet fixes, commit when passing
  2. **Review:** Sonnet reviews accumulated changes (presentation, clarity, alignment). Apply all fixes. Commit.
  3. **Functional:** Same checks as light checkpoint

**Integration tests (TDD composition tasks):**
- Phase start: xfail integration test calling top-level entry point
- Phase end: Remove xfail, verify passes
- Catches gaps unit tests miss (results consumed, not just functions called)

**When to mark `checkpoint: full`:**
- Phase introduces new public API surface
- Phase crosses module boundaries (3+ packages)
- Runbook exceeds 20 items total

---

## What NOT to Test (TDD phases)

TDD tests **behavior**, not **presentation**:

| Category | Skip Testing | Test Instead |
|----------|--------------|--------------|
| CLI help text | Exact phrasing | Command parses correctly, options work |
| Error messages | Exact wording | Error raised, exit code, error type |
| Log output | Format, phrasing | Logged events occur, data captured |
| Documentation | Generated content | Generation process works |

**Exceptions:** Regulatory requirements, complex generated content, machine-parsed output.

---

## Testing Strategy

**Applied during TDD cycle planning and general step design. Shapes test layer selection across all phases.**

### Integration-First (Diamond Shape)

Integration tests are the default test layer. Every key behavior is tested through its production call path — the same entry point, wiring, and data flow production code uses.

**Why:** The recurring failure mode is missing wiring — components built and unit-tested in isolation, production call path never connected. Integration-first makes wiring the default thing verified. A component cannot be "done" while its wiring is absent because the integration test stays RED.

**Cycle planning impact:**
- Integration cycles planned first, not as unit-test follow-up
- Each phase should include at least one cycle exercising the production call path
- The phase-boundary xfail integration test pattern (Checkpoints section) continues unchanged

### Unit Tests as Surgical Supplement

Unit tests are not the primary layer. Add unit cycles only when:
- **Combinatorial explosion** — too many input combinations to cover at integration level
- **Hard-to-isolate edge cases** — error paths requiring fault injection
- **Internal contract verification** — key invariants not observable through the integration surface

If a behavior is reachable through the production call path and the path is fast, test it there.

### Real Subprocesses for Subprocess Domains

When production code's primary operation is subprocess calls (git, CLI tools, compilers), tests use real subprocesses in `tmp_path` fixtures. Mocks only for:
- Error injection (lock files, permission errors, network timeouts)
- Cases where the real subprocess is destructive or non-deterministic

Generalizes the project convention in `agents/decisions/testing.md` ("When Preferring E2E Over Mocked Subprocess") from git to all subprocess domains.

### Local Substitutes for External Dependencies

For external services (databases, APIs, cloud services):
- Use local substitutes preserving the production call path (SQLite for database tests, local HTTP server for API tests)
- Accept fidelity trade-offs (SQL dialect differences, simplified auth) with a few targeted e2e tests verifying the real service path
- Do not retreat to mocks simply because the real service is "slow" — manage latency at infrastructure level (parallelism, selective running)

---

## Cycle/Step Ordering Guidance

**TDD phases:**
- Start with simplest happy path, not empty/degenerate case
- Foundation-first: existence → structure → behavior → refinement
- Each cycle must test a branch point — if RED can pass with `assert callable(X)`, the cycle is vacuous

**General phases:**
- Order by dependency: prerequisite steps before dependent steps
- Group by file/module for efficient execution
- Place validation/verification after implementation

**Detailed guidance:** See `references/patterns.md` for TDD granularity criteria and numbering, `references/general-patterns.md` for general-step granularity and prerequisite validation patterns.

---

## Common Pitfalls

**Avoid:**
- Creating runbooks when direct implementation is better (skipping tier assessment)
- Assuming file paths from conventions without Glob/Grep verification (skipping Phase 0.5)
- Skipping outline generation for complex runbooks
- Generating entire runbook monolithically instead of phase-by-phase
- Leaving design decisions for "during execution"
- Vague success criteria ("analysis complete" vs "analysis has 6 sections with line numbers")
- Success criteria that only check structure ("file exists") when step should verify content/behavior
- Missing phase headers in phase files (causes model defaults and context loss)
- Forgetting to run prepare-runbook.py after review
- Prescriptive code in TDD GREEN phases (describe behavior, provide hints)
- Missing investigation prerequisites for creation steps

**Instead:**
- Verify prerequisites explicitly
- Match model to task complexity
- Make all decisions during planning
- Define measurable success criteria
- Document clear escalation triggers
- Always run prepare-runbook.py to create artifacts

---

## Runbook Template Structure

```markdown
---
name: runbook-name
model: haiku
---

# [Runbook Name]

**Context**: [Brief description]
**Design**: [Reference to design document]
**Status**: [Draft / Ready / Complete]
**Created**: YYYY-MM-DD

---

## Weak Orchestrator Metadata
[As defined in Phase 2]

---

## Common Context

**Requirements (from design):**
- FR-1: [summary] — addressed by [element]

**Scope boundaries:** [in/out]

**Key Constraints:**
- [Constraint]

**Recall (from artifact):**
Selected entries from `plans/<job>/recall-artifact.md`, curated for this runbook's task agents.
Token budget: ≤1.5K tokens (ungrounded — needs empirical calibration after first use).

- Phase-neutral entries only here (project conventions, cross-cutting failure modes). Phase-specific entries go in phase preambles instead.
- Format per consumer model tier:
  - Haiku/sonnet consumers: constraint format — DO/DO NOT rules with explicit applicability markers
  - Opus consumers: rationale format — key points with context
- Content baked at planning time — orchestrator does not filter recall at execution time. Planner resolves conflicting entries and removes least-specific entries when budget exceeded (eviction at planning time, not runtime). Cognitive work at the planner's model tier.
- Recall entries must avoid conflicting signals: at haiku capability, persistent ambient signal wins over per-step instructions. Curate carefully — Common Context recall is ambient for all task agents.
- DO NOT rules about recall content go here alongside the content guidance, not in a separate cleanup step.

**Project Paths:**
- [Path]: [Description]

---

## Cycle 1.1: [Name] (TDD phase)
[RED/GREEN content]

---

## Step 2.1: [Name] (General phase)

**Objective**: [Clear objective]
**Script Evaluation**: [Direct / Small / Prose / Separate]
**Execution Model**: [Haiku / Sonnet / Opus — see Model Assignment for artifact-type override]

**Implementation**: [Content]

**Expected Outcome**: [What happens on success]
**Error Conditions**: [Escalation actions]
**Validation**: [Checks]
```

---

## References

- **`references/patterns.md`** — TDD granularity criteria, numbering, common patterns
- **`references/general-patterns.md`** — General-step granularity, prerequisite validation, step structure
- **`references/anti-patterns.md`** — Patterns to avoid with corrections
- **`references/error-handling.md`** — Error catalog, edge cases, recovery protocols
- **`references/examples.md`** — Complete runbook examples (TDD and general)
- **`agents/decisions/pipeline-contracts.md`** — I/O contracts for pipeline transformations

