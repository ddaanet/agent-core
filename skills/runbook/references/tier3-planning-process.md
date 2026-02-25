# Tier 3 Planning Process

Full planning process for Tier 3 runbooks: Phase 0.5 through Phase 3.5.

## Phase 0.5: Discover Codebase Structure (REQUIRED)

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
   - `agent-core/bin/when-resolve.py "when <trigger>" ...` -- resolve entries related to the task domain. Read `memory-index.md` first if triggers not known from context.
   - Factor known constraints into step design and model selection

2. **Augment recall artifact** (`plans/<job>/recall-artifact.md`):
   - If artifact exists (design stage may have generated it via Pass 1): augment with implementation and testing learnings
     - Read `agents/decisions/implementation-notes.md` and `agents/decisions/testing.md`
     - Add entries relevant to the planned work -- planning-relevant only: model selection failures, phase typing decisions, checkpoint placement patterns, precommit gotchas
     - Do NOT add execution-level entries (mock patching, test structure details) -- those belong in step files, not recall
   - If artifact absent: generate initial artifact (Read `memory-index.md`, select entries by problem-domain matching, batch-resolve via `agent-core/bin/when-resolve.py`, write artifact -- same process as `/design` skill's Recall Artifact Generation section, but with implementation focus)
   - Write augmented artifact back to `plans/<job>/recall-artifact.md`
   - For multi-session pipelines where design-time artifact may be stale, planner can regenerate from scratch

3. **Verify actual file locations:**
   - Use Glob to find source files referenced by the design
   - Use Glob to find test files: `tests/test_*.py`, `tests/**/test_*.py`
   - Use Grep to find specific functions, classes, or patterns mentioned in the design
   - Record actual file paths for use in runbook steps
   - **NEVER assume file paths from conventions alone** -- always verify with Glob/Grep
   - STOP if expected files not found: report missing files to user

---

## Phase 0.75: Generate Runbook Outline

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
   - **Inline type selection criteria** -- tag a phase or item `inline` when ALL hold:
     - All decisions pre-resolved (no open questions requiring feedback)
     - All changes are prose edits or additive (no behavioral code changes)
     - Insertion points or edit targets are identified
     - No implementation loops (no test/build feedback required)
   - **Pattern batching** -- when N items share identical operation structure with different data (e.g., N fragment demotions each following "remove @-ref, verify skill coverage, shrink stub"), collapse into a single inline item with a variation table. Do not create N separate items.

2. **Verify outline quality:**
   - **All implementation choices resolved** -- No "choose between" / "decide" / "determine" / "select approach" / "evaluate which" language. Each item commits to one approach. If uncertain, use `/opus-design-question`.
   - **Inter-item dependencies declared** -- If item N.M depends on item N.K, declare `Depends on: [Cycle|Step] N.K`.
   - **Code fix items enumerate affected sites** -- For items fixing code: list all affected call sites (file:function or file:line).
   - **Later items reference post-phase state** -- Items in Phase N+1 that modify files changed in Phase N must note expected state.
   - **Phases <= 8 items each** -- Split phases with >8 items or add internal checkpoint.
   - **Cross-cutting issues scope-bounded** -- Partially addressed issues must note what's in vs out of scope.
   - **No vacuous items** -- Every item must produce a functional outcome. TDD: test a branch point. General: produce a behavioral change. Scaffolding-only items merge into nearest behavioral item.
   - **Foundation-first ordering** -- Order: existence -> structure -> behavior -> refinement. No forward dependencies.
   - **Collapsible item detection** -- Adjacent items modifying same file or testing edge cases of same function should collapse. Note candidates for Phase 0.85.
   - **Prose atomicity** -- All edits to a single prose artifact (skill, fragment, agent definition) land in one item. No splitting the same file across items or phases. Exception: expand/contract migration (FR-2a pattern).
   - **Self-modification ordering** -- When the runbook modifies pipeline tools it will later use (skills, review agents, executor), tool-improvement items precede tool-usage items. References `agents/decisions/workflow-advanced.md` "When Bootstrapping Self-Referential Improvements."

3. **Commit outline before review:**
   - Commit `runbook-outline.md` to create clean checkpoint
   - Review agents operate on filesystem state -- committed state prevents dirty-tree issues

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
- If outline has <= 3 phases and <= 10 total items -> generate entire runbook at once (skip phase-by-phase)
- Single review pass instead of per-phase
- See also Phase 0.95: if items are already execution-ready, skip expansion entirely

---

## Phase 0.85: Consolidation Gate -- Outline

**Objective:** Merge trivial phases with adjacent complexity before expensive expansion.

**Actions:**

1. **Scan outline for trivial phases:**
   - Phases with <= 2 items AND complexity marked "Low"
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

**When to skip:** No trivial phases, all have cross-cutting dependencies, or outline already compact (<= 3 phases).

---

## Phase 0.86: Simplification Pass

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
- Identical-pattern items (same function, varying data) -> parametrized single item
- Independent same-module functions -> batched single item
- Sequential additions to same structure -> merged single item

**Small outlines (<= 10 items):** Agent still runs but reports "no consolidation candidates" rather than skipping -- maintains mandatory gate while avoiding wasted effort.

---

## Phase 0.9: Complexity Check Before Expansion

**Objective:** Gate expensive expansion with callback mechanism.

**Actions:**

1. **Assess expansion scope:**
   - Count total items from outline
   - Identify pattern-based items (same structure, different inputs)
   - Identify algorithmic items (unique logic, edge cases)

2. **Apply fast-path if applicable:**
   - **Pattern items (>= 5 similar):** Generate pattern template + variation list
   - **Trivial phases (<= 2 items, low complexity):** Inline instructions
   - **Single constant change:** Skip item, add as inline task

3. **Callback mechanism -- if expansion too large:**

   **Callback triggers:**
   - Outline exceeds 25 items -> callback to design (scope too large)
   - Phase exceeds 10 items -> callback to outline (phase needs splitting)
   - Single item too complex -> callback to outline (decompose further)

   **Callback levels:**
   ```
   item -> runbook outline -> design -> design outline -> requirements
   ```

   **When callback triggered:**
   - STOP expansion
   - Document issue: "Phase N contains [issue]. Callback to [level] required."
   - Return to previous level with specific restructuring recommendation

4. **Proceed with expansion:** Only if complexity checks pass.

---

## Phase 0.95: Outline Sufficiency Check

**Objective:** Skip expensive expansion when the outline is already detailed enough to serve as the runbook.

**Sufficiency criteria -- ALL must hold:**
- Every item specifies target files/locations
- Every item has a concrete action (no "determine"/"evaluate options" language)
- Every item has verification criteria or is self-evidently complete
- No unresolved design decisions in item descriptions

**TDD threshold:** Also skip expansion when outline has <3 phases AND <10 cycles total (small TDD work doesn't need full cycle expansion).

**Inline phases:** Inline phases always satisfy sufficiency -- they have no expansion. In mixed runbooks (inline + general/TDD), inline phases pass through while non-inline phases are evaluated against the criteria above.

**LLM failure mode gate (before promotion):**
Check for common planning defects (criteria from review-plan skill Section 11):
- Vacuity: any items that only create scaffolding without functional outcome?
- Ordering: any items referencing structures from later items?
- Density: adjacent items on same target with minimal delta? (TDD: <1 branch difference; General: <20 LOC delta)
- Checkpoints: gaps >10 items without checkpoint?
Fix inline before promotion. If unfixable, fall through to Phase 1 expansion (lightweight orchestration exit is also unavailable -- a defect-laden outline cannot serve as the orchestration plan).

**If sufficient -- check for lightweight orchestration exit:**

**Discriminator:** The `## Execution Model` section encodes dispatch protocol (which agents, what context each receives, recall injection method, checkpoint sequencing). Its presence means the outline was designed as an orchestration plan, not as input to the runbook pipeline. Absence means the outline needs promotion to runbook format for prepare-runbook.py to generate step files and plan-specific agents.

If outline contains `## Execution Model` section with dispatch protocol:

1. Do not promote to runbook format, do not run prepare-runbook.py -- the outline IS the execution plan
2. Commit outline, then tail-call `/handoff --commit`
3. Set task command in session.md: orchestrate from outline + recall artifact per Execution Model and Recall Injection sections

**Otherwise -- promote outline to runbook:**

1. **Reformat headings:** Convert item headings to H2 (`## Step N.M:` or `## Cycle X.Y:`)
2. **Convert content:** Bullets become body content under each H2
3. **Add Common Context:** Extract from outline's Key Decisions, Requirements, design reference
4. **Add frontmatter:** name, model (from outline metadata or design)
5. **Preserve phase structure:** `### Phase N: title` kept as-is
6. **Write to:** `plans/<job>/runbook.md`
7. **Skip to Phase 4** -- expansion, assembly, consolidation gate, holistic review unnecessary

**If not sufficient -> proceed with Phase 1 expansion.**

---

## Phase 1: Phase-by-Phase Expansion

**For each phase identified in the outline, generate detailed content with review.**

**For each phase:**

1. **Generate phase content:**
   - **Read Expansion Guidance:** Check `plans/<job>/runbook-outline.md` for `## Expansion Guidance` section.
   - File: `plans/<job>/runbook-phase-N.md`
   - Every phase file MUST start with `### Phase N: title (type: TYPE, model: MODEL)` header. prepare-runbook.py uses this for model propagation and context extraction.
   - Check phase type tag from outline phase heading (e.g., `### Phase 1: Core behavior (type: tdd)`)

2. **Expand based on phase type:**

   **[TDD phases] -- Cycle Planning:**
   Read `references/tdd-cycle-planning.md` for cycle numbering, RED/GREEN specification formats, assertion quality requirements, investigation prerequisites, dependency assignment, and stop conditions.

   **[General phases] -- Script Evaluation:**
   - Classify each task: small (<= 25 lines inline), medium (25-100 prose), large (>100 separate planning)
   - Classify step type: transformation (self-contained) vs creation (needs investigation prerequisite)
   - For creation steps: `**Prerequisite:** Read [file:lines] -- understand [behavior/flow]`
   - Each step: Objective, Implementation, Expected Outcome, Error Conditions, Validation

   **[Inline phases] -- Pass-through:**
   - No decomposition or step-file generation
   - Phase content from outline IS the execution instruction
   - No phase file generated (`runbook-phase-N.md` not written for inline phases)
   - Inline phases skip per-phase review (reviewed at outline level via Phase 0.75)

3. **Commit phase file before review:**
   - Commit `runbook-phase-N.md` to create clean checkpoint
   - Review agents operate on filesystem state -- committed state prevents dirty-tree issues

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

## Phase 2: Assembly and Metadata

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

**IMPORTANT -- Do NOT manually assemble:** Phase files remain separate until prepare-runbook.py processes them. Manual concatenation bypasses validation logic.

**Fallback header injection:** prepare-runbook.py injects missing `### Phase N:` headers from filenames during assembly. This is a safety net -- phase files should include headers explicitly for model propagation.

Every assembled runbook MUST include this metadata section:

```markdown
## Weak Orchestrator Metadata

**Total Steps**: [N]

**Execution Model** (general phases only -- TDD cycles use phase-level model, inline phases use orchestrator-direct):
- Steps X-Y: Haiku (simple file operations, scripted tasks)
- Steps A-B: Sonnet (semantic analysis, judgment required)
- Steps C-D: Opus (architectural artifacts -- see Model Assignment)

**Step Dependencies**: [sequential | parallel | specific graph]

**Error Escalation**:
- Haiku -> Sonnet: [triggers]
- Sonnet -> User: [triggers]

**Report Locations**: [pattern]

**Success Criteria**: [overall runbook success]

**Prerequisites**:
- [Prerequisite 1] (verified via [method])
```

**Key principles:**
1. Orchestrator metadata is coordination info only -- not execution details
2. Validation is delegated -- if needed, it's a separate step
3. Planning happens before execution -- orchestrator doesn't decide during execution

---

## Phase 2.5: Consolidation Gate -- Runbook

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

## Phase 3: Final Holistic Review

**After assembly validation, perform final cross-phase review.**

Delegate to `runbook-corrector` (fix-all mode) for cross-phase consistency:
- Include review-relevant entries from `plans/<job>/recall-artifact.md` in delegation prompt (failure modes, quality anti-patterns)

**Review scope:**
- Cross-phase dependency ordering
- Item numbering consistency
- Metadata accuracy
- File path validation (all referenced paths exist -- use Glob)
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

## Phase 3.5: Pre-Execution Validation

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

**Graceful degradation:** If `validate-runbook.py` doesn't exist, skip Phase 3.5 and proceed to Phase 4 with warning. Supports incremental adoption -- Phase A lands skill references before Phase B implements the script.

**Validation checks:**
- `model-tags`: File path -> model mapping. Artifact-type files (skills/, fragments/, agents/, workflow-*.md) must have opus tag.
- `lifecycle`: Create->modify dependency graph. Flags modify-before-create, duplicate creation, future-phase reads.
- `test-counts`: Checkpoint "All N tests pass" claims vs actual test function count.
- `red-plausibility`: Prior GREENs vs RED expectations. Flags already-passing states.
