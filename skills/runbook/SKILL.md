---
name: runbook
description: |
  This skill should be used when the user asks to "/runbook", "create a runbook",
  "plan the implementation", "expand the design into steps", or when a design
  document needs decomposition into executable steps. Creates execution runbooks
  with per-phase typing (TDD cycles, general steps, or inline pass-through).
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

## When to Use

**Use this skill when:**
- Creating execution runbooks for multi-step tasks
- Delegating work to weak orchestrator agents (haiku/sonnet)
- Complex tasks need explicit design decisions documented
- Tasks require clear error escalation and validation criteria
- Feature development requiring TDD approach (behavioral phases)
- Infrastructure, refactoring, migrations (general phases)
- Mixed work requiring TDD, general, and/or inline phases

**Do NOT use when:**
- Task requires user input or interactive decisions
- Plan already exists and just needs execution (use `/orchestrate`)

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

**Process overview:**
- Phase 0.5: Discover codebase structure
- Phase 0.75: Generate runbook outline
- Phase 0.85: Consolidation gate (outline)
- Phase 0.86: Simplification pass (pattern consolidation)
- Phase 0.9: Complexity check before expansion
- Phase 0.95: Outline sufficiency check
- Phase 1: Phase-by-phase expansion with reviews
- Phase 2: Assembly and metadata
- Phase 2.5: Consolidation gate (runbook)
- Phase 3: Final holistic review
- Phase 3.5: Pre-execution validation
- Phase 4: Prepare artifacts and handoff

---

### Phase 0.5: Discover Codebase Structure (REQUIRED)

**Before writing any runbook content:**

0. **Read documentation perimeter and requirements (if present):**

If design document includes "Documentation Perimeter" section:
- Read all files listed under "Required reading"
- Note Context7 references (may need additional queries)
- If "Skill-loading directives" subsection exists, invoke each listed skill (e.g., `/plugin-dev:skill-development`) before proceeding
- Factor knowledge into step design

If design document includes "Requirements" section:
- Read and summarize functional/non-functional requirements
- Note scope boundaries (in/out of scope)
- Carry requirements context into runbook Common Context

1. **Discover relevant prior knowledge:**
   - `agent-core/bin/when-resolve.py "when <trigger>" ...` — resolve entries related to the task domain. Read `memory-index.md` first if triggers not known from context.
   - Factor known constraints into step design and model selection

2. **Augment recall artifact** (`plans/<job>/recall-artifact.md`):
   - If artifact exists (design stage may have generated it via Pass 1): augment with implementation and testing learnings
     - Read `agents/decisions/implementation-notes.md` and `agents/decisions/testing.md`
     - Add entries relevant to the planned work — planning-relevant only: model selection failures, phase typing decisions, checkpoint placement patterns, precommit gotchas
     - Do NOT add execution-level entries (mock patching, test structure details) — those belong in step files, not recall
   - If artifact absent: generate initial artifact (Read `memory-index.md`, select entries by problem-domain matching, batch-resolve via `agent-core/bin/when-resolve.py`, write artifact — same process as `/design` skill's Recall Artifact Generation section, but with implementation focus)
   - Write augmented artifact back to `plans/<job>/recall-artifact.md`
   - For multi-session pipelines where design-time artifact may be stale, planner can regenerate from scratch

3. **Verify actual file locations:**
   - Use Glob to find source files referenced by the design
   - Use Glob to find test files: `tests/test_*.py`, `tests/**/test_*.py`
   - Use Grep to find specific functions, classes, or patterns mentioned in the design
   - Record actual file paths for use in runbook steps
   - **NEVER assume file paths from conventions alone** — always verify with Glob/Grep
   - STOP if expected files not found: report missing files to user

---

### Phase 0.75: Generate Runbook Outline

**Recall diff:** `Bash: agent-core/bin/recall-diff.sh <job-name>`

Review the changed files list. File locations, existing patterns, and structural constraints make different implementation learnings relevant than what Phase 0.5 initially selected. If files changed that affect which recall entries are relevant, update the artifact: add entries revealed by discovery (e.g., testing patterns for the discovered module structure), remove entries for patterns that don't apply to the actual codebase. Write updated artifact back.

**Before writing full runbook content, create a holistic outline for cross-phase coherence.**

1. **Create runbook outline:**
   - File: `plans/<job>/runbook-outline.md`
   - Include:
     - **Requirements mapping table:** Link each requirement from design to implementation phase
     - **Phase structure:** Break work into logical phases with item titles and type tags
     - **Key decisions reference:** Link to design sections with architectural decisions
     - **Complexity per phase:** Estimated scope and model requirements per phase
   - **Per-phase type tagging:** Each phase in the outline declares `type: tdd`, `type: general` (default), or `type: inline`
     - TDD phases use cycle titles (X.Y numbering), RED/GREEN markers
     - General phases use step titles, action descriptions
     - Inline phases use bullet items (no numbered steps/cycles)
   - **Inline type selection criteria** — tag a phase or item `inline` when ALL hold:
     - All decisions pre-resolved (no open questions requiring feedback)
     - All changes are prose edits or additive (no behavioral code changes)
     - Insertion points or edit targets are identified
     - No implementation loops (no test/build feedback required)
   - **Pattern batching** — when N items share identical operation structure with different data (e.g., N fragment demotions each following "remove @-ref, verify skill coverage, shrink stub"), collapse into a single inline item with a variation table. Do not create N separate items.

2. **Verify outline quality:**
   - **All implementation choices resolved** — No "choose between" / "decide" / "determine" / "select approach" / "evaluate which" language. Each item commits to one approach. If uncertain, use `/opus-design-question`.
   - **Inter-item dependencies declared** — If item N.M depends on item N.K, declare `Depends on: [Cycle|Step] N.K`.
   - **Code fix items enumerate affected sites** — For items fixing code: list all affected call sites (file:function or file:line).
   - **Later items reference post-phase state** — Items in Phase N+1 that modify files changed in Phase N must note expected state.
   - **Phases ≤8 items each** — Split phases with >8 items or add internal checkpoint.
   - **Cross-cutting issues scope-bounded** — Partially addressed issues must note what's in vs out of scope.
   - **No vacuous items** — Every item must produce a functional outcome. TDD: test a branch point. General: produce a behavioral change. Scaffolding-only items merge into nearest behavioral item.
   - **Foundation-first ordering** — Order: existence → structure → behavior → refinement. No forward dependencies.
   - **Collapsible item detection** — Adjacent items modifying same file or testing edge cases of same function should collapse. Note candidates for Phase 0.85.
   - **Prose atomicity** — All edits to a single prose artifact (skill, fragment, agent definition) land in one item. No splitting the same file across items or phases. Exception: expand/contract migration (FR-2a pattern).
   - **Self-modification ordering** — When the runbook modifies pipeline tools it will later use (skills, review agents, executor), tool-improvement items precede tool-usage items. References `agents/decisions/workflow-advanced.md` "When Bootstrapping Self-Referential Improvements."

3. **Commit outline before review:**
   - Commit `runbook-outline.md` to create clean checkpoint
   - Review agents operate on filesystem state — committed state prevents dirty-tree issues

4. **Review outline:**
   - Delegate to `runbook-outline-corrector` (fix-all mode)
   - Include review-relevant entries from `plans/<job>/recall-artifact.md` in delegation prompt (failure modes, quality anti-patterns)
   - Agent fixes all issues (critical, major, minor)
   - Agent returns review report path

5. **Validate and proceed:**
   - Read review report
   - If critical issues remain: STOP and escalate to user
   - Otherwise: proceed to phase-by-phase expansion

**Fallback for small runbooks:**
- If outline has ≤3 phases and ≤10 total items → generate entire runbook at once (skip phase-by-phase)
- Single review pass instead of per-phase
- See also Phase 0.95: if items are already execution-ready, skip expansion entirely

---

### Phase 0.85: Consolidation Gate — Outline

**Objective:** Merge trivial phases with adjacent complexity before expensive expansion.

**Actions:**

1. **Scan outline for trivial phases:**
   - Phases with ≤2 items AND complexity marked "Low"
   - Single-constant changes or configuration updates
   - Pattern: setup/cleanup work that could batch with adjacent feature work

2. **Evaluate merge candidates:**
   For each trivial phase, check:
   - Can it merge with preceding phase? (same domain, natural continuation)
   - Can it merge with following phase? (prerequisite relationship)
   - Would merging create >10 items in target phase? (reject if so)

3. **Apply consolidation:**
   ```markdown
   ## Phase N: [Combined Name]
   ### [Original feature items]
   ### [Trivial work as final items]
   ```

   **Do NOT merge if:**
   - Trivial phase has external dependencies
   - Merged phase would exceed 10 items
   - Domains are unrelated (forced grouping hurts coherence)

4. **Update traceability:**
   - Adjust requirements mapping table
   - Update phase structure in outline
   - Note consolidation decisions in Expansion Guidance

**When to skip:** No trivial phases, all have cross-cutting dependencies, or outline already compact (≤3 phases).

---

### Phase 0.86: Simplification Pass

**Objective:** Detect and consolidate redundant patterns before expensive expansion.

**Mandatory** for all Tier 3 runbooks.

**Actions:**

1. **Delegate to simplification agent:**
   - Agent: `runbook-simplifier`
   - Input: `plans/<job>/runbook-outline.md` (post-0.85 state)
   - Output: Consolidated outline + report at `plans/<job>/reports/simplification-report.md`

2. **Review simplification report:**
   - Read report filepath returned by agent
   - Check before/after item counts
   - Verify requirements mapping preserved

3. **Proceed to Phase 0.9** with simplified outline.

**Pattern categories detected:**
- Identical-pattern items (same function, varying data) → parametrized single item
- Independent same-module functions → batched single item
- Sequential additions to same structure → merged single item

**Small outlines (≤10 items):** Agent still runs but reports "no consolidation candidates" rather than skipping — maintains mandatory gate while avoiding wasted effort.

---

### Phase 0.9: Complexity Check Before Expansion

**Objective:** Gate expensive expansion with callback mechanism.

**Actions:**

1. **Assess expansion scope:**
   - Count total items from outline
   - Identify pattern-based items (same structure, different inputs)
   - Identify algorithmic items (unique logic, edge cases)

2. **Apply fast-path if applicable:**
   - **Pattern items (≥5 similar):** Generate pattern template + variation list
   - **Trivial phases (≤2 items, low complexity):** Inline instructions
   - **Single constant change:** Skip item, add as inline task

3. **Callback mechanism — if expansion too large:**

   **Callback triggers:**
   - Outline exceeds 25 items → callback to design (scope too large)
   - Phase exceeds 10 items → callback to outline (phase needs splitting)
   - Single item too complex → callback to outline (decompose further)

   **Callback levels:**
   ```
   item → runbook outline → design → design outline → requirements
   ```

   **When callback triggered:**
   - STOP expansion
   - Document issue: "Phase N contains [issue]. Callback to [level] required."
   - Return to previous level with specific restructuring recommendation

4. **Proceed with expansion:** Only if complexity checks pass.

---

### Phase 0.95: Outline Sufficiency Check

**Objective:** Skip expensive expansion when the outline is already detailed enough to serve as the runbook.

**Sufficiency criteria — ALL must hold:**
- Every item specifies target files/locations
- Every item has a concrete action (no "determine"/"evaluate options" language)
- Every item has verification criteria or is self-evidently complete
- No unresolved design decisions in item descriptions

**TDD threshold:** Also skip expansion when outline has <3 phases AND <10 cycles total (small TDD work doesn't need full cycle expansion).

**Inline phases:** Inline phases always satisfy sufficiency — they have no expansion. In mixed runbooks (inline + general/TDD), inline phases pass through while non-inline phases are evaluated against the criteria above.

**LLM failure mode gate (before promotion):**
Check for common planning defects (criteria from review-plan skill Section 11):
- Vacuity: any items that only create scaffolding without functional outcome?
- Ordering: any items referencing structures from later items?
- Density: adjacent items on same target with minimal delta? (TDD: <1 branch difference; General: <20 LOC delta)
- Checkpoints: gaps >10 items without checkpoint?
Fix inline before promotion. If unfixable, fall through to Phase 1 expansion (lightweight orchestration exit is also unavailable — a defect-laden outline cannot serve as the orchestration plan).

**If sufficient — check for lightweight orchestration exit:**

**Discriminator:** The `## Execution Model` section encodes dispatch protocol (which agents, what context each receives, recall injection method, checkpoint sequencing). Its presence means the outline was designed as an orchestration plan, not as input to the runbook pipeline. Absence means the outline needs promotion to runbook format for prepare-runbook.py to generate step files and plan-specific agents.

If outline contains `## Execution Model` section with dispatch protocol:

1. Do not promote to runbook format, do not run prepare-runbook.py — the outline IS the execution plan
2. Commit outline, then tail-call `/handoff --commit`
3. Set task command in session.md: orchestrate from outline + recall artifact per Execution Model and Recall Injection sections

**Otherwise — promote outline to runbook:**

1. **Reformat headings:** Convert item headings to H2 (`## Step N.M:` or `## Cycle X.Y:`)
2. **Convert content:** Bullets become body content under each H2
3. **Add Common Context:** Extract from outline's Key Decisions, Requirements, design reference
4. **Add frontmatter:** name, model (from outline metadata or design)
5. **Preserve phase structure:** `### Phase N: title` kept as-is
6. **Write to:** `plans/<job>/runbook.md`
7. **Skip to Phase 4** — expansion, assembly, consolidation gate, holistic review unnecessary

**If not sufficient → proceed with Phase 1 expansion.**

---

### Phase 1: Phase-by-Phase Expansion

**For each phase identified in the outline, generate detailed content with review.**

**For each phase:**

1. **Generate phase content:**
   - **Read Expansion Guidance:** Check `plans/<job>/runbook-outline.md` for `## Expansion Guidance` section.
   - File: `plans/<job>/runbook-phase-N.md`
   - Every phase file MUST start with `### Phase N: title (type: TYPE, model: MODEL)` header. prepare-runbook.py uses this for model propagation and context extraction.
   - Check phase type tag from outline phase heading (e.g., `### Phase 1: Core behavior (type: tdd)`)

2. **Expand based on phase type:**

   **[TDD phases] — Cycle Planning:**

   Use cycle planning guidance (see TDD Cycle Planning section below):
   - Number cycles X.Y format, sequential within phase
   - Generate RED specifications (prose test descriptions — NOT full code)
   - Generate GREEN specifications (behavior + hints — NOT prescriptive code)
   - Classify step type and add investigation prerequisites for creation cycles
   - Assign dependencies (sequential default, cross-phase with `[DEPENDS: X.Y]`)
   - Verify integration coverage

   **[General phases] — Script Evaluation:**

   - Classify each task: small (≤25 lines inline), medium (25-100 prose), large (>100 separate planning)
   - Classify step type: transformation (self-contained) vs creation (needs investigation prerequisite)
   - For creation steps: `**Prerequisite:** Read [file:lines] — understand [behavior/flow]`
   - Each step: Objective, Implementation, Expected Outcome, Error Conditions, Validation

   **[Inline phases] — Pass-through:**

   - No decomposition or step-file generation
   - Phase content from outline IS the execution instruction
   - No phase file generated (`runbook-phase-N.md` not written for inline phases)
   - Inline phases skip per-phase review (reviewed at outline level via Phase 0.75)

3. **Commit phase file before review:**
   - Commit `runbook-phase-N.md` to create clean checkpoint
   - Review agents operate on filesystem state — committed state prevents dirty-tree issues

4. **Review phase content:**
   - Delegate to `runbook-corrector` (fix-all mode)
   - Include review-relevant entries from `plans/<job>/recall-artifact.md` in delegation prompt (failure modes, quality anti-patterns)
   - Agent applies type-aware criteria: TDD discipline for TDD phases, step quality for general phases, vacuity/density/ordering for inline phases, LLM failure modes for ALL phases
   - Agent returns review report path

   **Background review pattern:** After writing and committing each phase file, launch review with `run_in_background=true` and proceed to generating next phase. Reviews run concurrently. Per-phase reviews are independent; cross-phase consistency checked in Phase 3.

   **Domain Validation:**

   When writing review checkpoint steps, check if a domain validation skill exists at `agent-core/skills/<domain>-validation/SKILL.md` for the artifact types being reviewed. If found, include domain validation in the review step:

   ```
   - **Domain validation:** Read and apply criteria from
     `agent-core/skills/<domain>-validation/SKILL.md`
     for artifact type: [skills|agents|hooks|commands|plugin-structure]
   ```

5. **Handle review outcome:**
   - Read review report
   - If ESCALATION: STOP, address unfixable issues
   - If all fixed: proceed to next phase

---

### TDD Cycle Planning Guidance

**Applied within TDD-type phases during Phase 1 expansion.**

**1. Number cycles:** X.Y format (1.1, 1.2, ..., 2.1, 2.2, ...)
   - Start at 1.1 (not 0.1 or 1.0)
   - Sequential within phases
   - No duplicates (error), gaps acceptable (warn)

**2. Generate RED specifications (prose format):**

```markdown
**RED Phase:**

**Test:** [test function name]
**Assertions:**
- [Specific assertion 1 — behavioral, not structural]
- [Specific assertion 2]
- [Expected values/behaviors]

**Expected failure:** [Error type or pattern]

**Why it fails:** [Missing implementation]

**Verify RED:** `pytest [file]::[test_function] -v`
```

**Prose Test Description Rules:**

RED phase uses **prose descriptions**, not full code blocks. Saves planning tokens while providing enough specificity for haiku.

**Assertion Quality Requirements:**

| Weak (vague) | Strong (specific) |
|---|---|
| "returns correct value" | "returns string containing 🥈 emoji" |
| "handles error case" | "raises ValueError with message 'invalid input'" |
| "processes input correctly" | "output dict contains 'count' key with integer > 0" |

**Validation rule:** Prose must specify exact expected values, patterns, or behaviors. If assertion could be satisfied by multiple implementations, it's too vague.

**3. Generate GREEN specifications:**

```markdown
**GREEN Phase:**

**Implementation:** [Brief description]

**Behavior:**
- [What the code must DO — not HOW to write it]

**Approach:** [Brief hint about algorithm/strategy]

**Changes:**
- File: [path]
  Action: [what to add/modify — describe, don't write code]
  Location hint: [where in file]

**Verify lint:** `just lint`
**Verify GREEN:** [Test command]
**Verify no regression:** [Full test suite]
```

**CRITICAL — No prescriptive code:** GREEN phases describe BEHAVIOR and provide HINTS. Do NOT include complete function implementations or code blocks that can be copied verbatim.

**Integration-first cycle ordering:** Default to integration test cycles that exercise production call paths. Add unit test cycles only when integration coverage is insufficient (combinatorial, fault injection, internal contracts — see Testing Strategy). Within a phase, plan integration cycles before or alongside unit cycles, not as follow-up.

**Wire-then-isolate:** When a phase builds a component, the first testable cycle should verify the component works through its production entry point. Subsequent cycles can isolate specific behaviors if edge-case coverage requires it.

**4. Classify and add investigation prerequisites:**
- **Transformation cycles** (delete, move, rename): Self-contained recipe sufficient
- **Creation cycles** (new test, new integration, touching existing paths): MUST include `**Prerequisite:** Read [file:lines] — understand [behavior/flow]`

**5. Assign dependencies:**
- **Default:** Sequential within phase (1.1 → 1.2 → 1.3)
- **Cross-phase:** `[DEPENDS: X.Y]`
- **Regression:** `[REGRESSION]`

**6. Stop conditions:**

Common TDD stop/error conditions (auto-injected by prepare-runbook.py into Common Context):
- RED fails to fail → STOP, diagnose test
- GREEN passes without implementation → STOP, test too weak
- Test requires mocking not yet available → STOP, add prerequisite cycle
- Implementation needs architectural decision → STOP, escalate to opus

Only add custom domain-specific stop conditions per-cycle when needed.

### Mandatory Conformance Validation

**Trigger:** When design includes external reference (shell prototype, API spec) in `Reference:` field.

**Requirement:** Runbook MUST include validation items that verify implementation conforms to the reference.

**Validation precision:**
- Use precise descriptions with exact expected strings from reference
- Example: "Output matches reference: `🥈 sonnet \033[35m…` with double-space separators"
- NOT abstracted: "Output contains formatted model with appropriate styling"

**Related:** See `agents/decisions/testing.md` "Conformance Validation for Migrations".

---

### Phase 2: Assembly and Metadata

**After all phases are finalized, validate phase files are ready, then delegate to prepare-runbook.py.**

**Actions:**

1. **Pre-assembly validation:**
   - Verify all phase files exist (`runbook-phase-1.md` through `runbook-phase-N.md`)
   - Check phase reviews completed (all reports in `reports/` directory)
   - Confirm no critical issues remain

2. **Metadata preparation:**
   - Count total items across all phases
   - Extract Common Context elements from design
   - Verify Design Decisions section ready

3. **Final consistency check:**
   - Cross-phase dependencies
   - Item numbering sequential
   - Phase boundary issues
   - No new content generation, only validation

**IMPORTANT — Do NOT manually assemble:** Phase files remain separate until prepare-runbook.py processes them. Manual concatenation bypasses validation logic.

**Fallback header injection:** prepare-runbook.py injects missing `### Phase N:` headers from filenames during assembly. This is a safety net — phase files should include headers explicitly for model propagation.

Every assembled runbook MUST include this metadata section:

```markdown
## Weak Orchestrator Metadata

**Total Steps**: [N]

**Execution Model** (general phases only — TDD cycles use phase-level model, inline phases use orchestrator-direct):
- Steps X-Y: Haiku (simple file operations, scripted tasks)
- Steps A-B: Sonnet (semantic analysis, judgment required)
- Steps C-D: Opus (architectural artifacts — see Model Assignment)

**Step Dependencies**: [sequential | parallel | specific graph]

**Error Escalation**:
- Haiku → Sonnet: [triggers]
- Sonnet → User: [triggers]

**Report Locations**: [pattern]

**Success Criteria**: [overall runbook success]

**Prerequisites**:
- [Prerequisite 1] (✓ verified via [method])
```

**Key principles:**
1. Orchestrator metadata is coordination info only — not execution details
2. Validation is delegated — if needed, it's a separate step
3. Planning happens before execution — orchestrator doesn't decide during execution

---

### Phase 2.5: Consolidation Gate — Runbook

**Objective:** Merge isolated trivial items with related features after assembly validation.

**Actions:**

1. **Identify isolated trivial items:**
   - Items marked for fast-path during Phase 0.9
   - Single-line changes or constant updates
   - Items with no validation assertions (pure configuration)

2. **Check merge candidates:**
   - **Same-file items:** Merge with adjacent item modifying same file
   - **Setup items:** Promote to phase preamble
   - **Cleanup items:** Demote to phase postamble

3. **Apply consolidation and update metadata** (Total Steps count, numbering).

**Constraints:**
- Never merge items across phases
- Preserve isolation when needed
- Keep merged items manageable

**When to skip:** No trivial items, all have substantial coverage, or runbook already compact (<15 items).

---

### Phase 3: Final Holistic Review

**After assembly validation, perform final cross-phase review.**

Delegate to `runbook-corrector` (fix-all mode) for cross-phase consistency:
- Include review-relevant entries from `plans/<job>/recall-artifact.md` in delegation prompt (failure modes, quality anti-patterns)

**Review scope:**
- Cross-phase dependency ordering
- Item numbering consistency
- Metadata accuracy
- File path validation (all referenced paths exist — use Glob)
- Requirements satisfaction
- **Type-specific criteria:**
  - TDD phases: Cross-phase RED/GREEN sequencing, no prescriptive code
  - General phases: Step clarity, script evaluation completeness
  - Inline phases: Vacuity, density, dependency ordering
- **LLM failure modes (all phases):** Vacuity, ordering, density, checkpoints

**Handle outcome:**
- Read review report
- If ESCALATION: STOP, address unfixable issues
- If all fixed: proceed to Phase 3.5

**Note:** Individual phase reviews already happened in Phase 1. This review checks holistic consistency only.

---

### Phase 3.5: Pre-Execution Validation

**Objective:** Validate assembled runbook structurally before artifact generation.

**Mandatory** for all Tier 3 runbooks.

**Actions:**

1. **Run validation checks:**
   ```bash
   agent-core/bin/validate-runbook.py model-tags plans/<job>/
   agent-core/bin/validate-runbook.py lifecycle plans/<job>/
   agent-core/bin/validate-runbook.py test-counts plans/<job>/
   agent-core/bin/validate-runbook.py red-plausibility plans/<job>/
   ```

   Each subcommand writes a report to `plans/<job>/reports/validation-{subcommand}.md`.

   **Exit codes:** 0 = pass, 1 = violations (blocking), 2 = ambiguous (optional semantic analysis).

2. **Handle results:**
   - All exit 0: proceed to Phase 4
   - Any exit 1: STOP, report violations to user
   - Any exit 2 (red-plausibility only): optionally delegate semantic analysis to runbook-corrector, then proceed

**Graceful degradation:** If `validate-runbook.py` doesn't exist, skip Phase 3.5 and proceed to Phase 4 with warning. Supports incremental adoption — Phase A lands skill references before Phase B implements the script.

**Validation checks:**
- `model-tags`: File path → model mapping. Artifact-type files (skills/, fragments/, agents/, workflow-*.md) must have opus tag.
- `lifecycle`: Create→modify dependency graph. Flags modify-before-create, duplicate creation, future-phase reads.
- `test-counts`: Checkpoint "All N tests pass" claims vs actual test function count.
- `red-plausibility`: Prior GREENs vs RED expectations. Flags already-passing states.

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

---

## Integration

**Workflow:**
```
/design → /runbook → runbook-corrector (fix-all) → prepare-runbook.py → /orchestrate
```

**Handoff:**
- Input: Design document from `/design`
- Output: Ready-to-execute artifacts (agent, steps, orchestrator plan), committed and handed off
- Next: User restarts session and pastes orchestrate command from clipboard
