---
name: plan-adhoc
description: Create execution runbooks for weak orchestrator agents using 4-point planning process (general workflow)
model: sonnet
allowed-tools: Task, Read, Write, Edit, Skill, Bash(mkdir:*, agent-core/bin/prepare-runbook.py, echo:*|pbcopy)
requires:
  - Design document from /design
  - CLAUDE.md for project conventions (if exists)
outputs:
  - Execution runbook at plans/<job-name>/runbook.md
  - Ready for prepare-runbook.py processing
user-invocable: true
---

# Plan Ad-hoc Skill

Create detailed execution runbooks suitable for weak orchestrator agents using a formalized 4-point planning process. This skill transforms high-level tasks into structured runbooks that haiku or sonnet agents can execute with minimal judgment.

**Workflow Context:** Part of general workflow (design → planning → execution). Contrast with `/plan-tdd` (TDD feature dev emphasis).

## When to Use

**Use this skill when:**
- Creating execution runbooks for multi-step tasks
- Delegating work to weak orchestrator agents (haiku/sonnet)
- Complex tasks need explicit design decisions documented
- Tasks require clear error escalation and validation criteria
- Ad-hoc one-off work (vs iterative feature development)

**Do NOT use when:**
- Task requires user input or interactive decisions
- Plan already exists and just needs execution
- Feature development requiring TDD approach (use `/plan-tdd` when available)

## Three-Tier Assessment

**Evaluate implementation complexity before proceeding. Assessment runs first, before any other work.**

### Assessment Criteria

Analyze the task and produce explicit assessment output:

```
**Tier Assessment:**
- Files affected: ~N
- Open decisions: none / [list]
- Components: N (sequential / parallel / mixed)
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

**Sequence:**
1. Implement changes directly using Read/Write/Edit tools
2. Delegate to vet agent for review
3. Apply all fixes from vet review
4. Tail-call `/handoff --commit`

### Tier 2: Lightweight Delegation

**Criteria:**
- Design complete, scope moderate (6-15 files or 2-4 logical components)
- Work benefits from agent isolation (context management) but not full orchestration
- Components are sequential (no parallelization benefit)
- No model switching needed

**Sequence:**
1. Delegate work via `Task(subagent_type="quiet-task", model="haiku", prompt="...")` with relevant context from design included in prompt (file paths, design decisions, conventions). Single agent for cohesive work; break into 2-4 components only if logically distinct.
2. After delegation complete: delegate to vet agent for review
3. Apply all fixes from vet review
4. Tail-call `/handoff --commit`

**Design constraints are non-negotiable:**

When design specifies explicit classifications (tables, rules, decision lists):
1. Include them LITERALLY in the delegation prompt
2. Delegated agents must NOT invent alternative heuristics
3. Agent "judgment" means applying design rules to specific cases, not creating new rules

Example: If design says "all ## headers are semantic," agent uses judgment to write good index entries for each header — NOT to reclassify some headers as structural.

**Key distinction from Tier 3:** No prepare-runbook.py, no orchestrator plan, no plan-specific agent. The planner acts as ad-hoc orchestrator, delegating directly via Task tool.

**Handling agent escalations:**

When delegated agent escalates "ambiguity" or "design gap":

1. **Verify against design source** — Re-read the design document section in question
2. **If design provides explicit rules** (classification tables, decision lists): Resolve using those rules, do not accept the escalation
3. **If genuinely ambiguous** (design silent on the case): Use `/opus-design-question` or ask user
4. **Re-delegate with clarification** if agent misread design

Common false escalations:
- "Which items are X vs Y?" when design table already classifies
- "Should we do A or B?" when design explicitly chose A
- "This seems like a lot" when design rationale explains why it's acceptable

### Tier 3: Full Runbook

**Criteria:**
- Multiple independent steps (parallelizable)
- Steps need different models
- Long-running / multi-session execution
- Complex error recovery
- >15 files or complex coordination

**Sequence:** 4-point process (see below) — existing pipeline unchanged.

## Planning Process (Tier 3 Only)

**Use this process only after assessment determines Tier 3 is needed.**

**Process overview:**
- Point 0.5: Discover codebase structure
- Point 0.75: Generate runbook outline
- Point 0.85: Consolidation gate (outline)
- Point 0.9: Complexity check before expansion
- Point 0.95: Outline sufficiency check (skip expansion if outline is execution-ready)
- Point 1: Phase-by-phase expansion with reviews
- Point 2: Assembly and metadata
- Point 2.5: Consolidation gate (runbook)
- Point 3: Final holistic review
- Point 4: Prepare artifacts and handoff

### Point 0.5: Discover Codebase Structure (REQUIRED)

**Before writing any runbook content:**

0. **Read documentation perimeter and requirements (if present):**

If design document includes "Documentation Perimeter" section:
- Read all files listed under "Required reading"
- Note Context7 references (may need additional queries)
- Factor knowledge into step design

If design document includes "Requirements" section:
- Read and summarize functional/non-functional requirements
- Note scope boundaries (in/out of scope)
- Carry requirements context into runbook Common Context

This provides designer's recommended context. Still perform discovery steps 1-2 below for path verification and memory discovery.

1. **Discover relevant prior knowledge:**
   - Check loaded memory-index context (already in CLAUDE.md) for entries related to the task domain
   - When entry is relevant, Read the referenced file
   - Factor known constraints into step design and model selection
   - **Do NOT grep memory-index.md** — it's already loaded, scan it mentally

2. **Verify actual file locations:**
   - Use Glob to find source files referenced by the design
   - Use Glob to find test files: `tests/test_*.py`, `tests/**/test_*.py`
   - Use Grep to find specific functions, classes, or patterns mentioned in the design
   - Record actual file paths for use in runbook steps
   - **NEVER assume file paths from conventions alone** — always verify with Glob/Grep
   - STOP if expected files not found: report missing files to user

**Why:** Runbooks with fabricated file paths fail immediately at execution. This is a complete blocker.

---

### Point 0.75: Generate Runbook Outline

**Before writing full runbook content, create a holistic outline for cross-phase coherence.**

1. **Create runbook outline:**
   - File: `plans/<job>/runbook-outline.md`
   - Include:
     - **Requirements mapping table:** Link each requirement from design to implementation phase/step
     - **Phase structure:** Break work into logical phases with step titles (no full content yet)
     - **Key decisions reference:** Link to design sections with architectural decisions
     - **Complexity per phase:** Estimated scope and model requirements per phase

2. **Verify outline quality:**
   - **All implementation choices resolved** — No "choose between" / "decide" / "determine" / "select approach" / "evaluate which" language. Each step commits to one approach. If uncertain, use `/opus-design-question` to resolve.
   - **Inter-step dependencies declared** — If step N.M depends on step N.K having created a file/module/function, declare `Depends on: Step N.K`.
   - **Code fix steps enumerate affected sites** — For steps fixing code: list all affected call sites (file:function or file:line). If different sites need different treatment, specify per-site decision tree.
   - **Later steps reference post-phase state** — Steps in Phase N+1 that modify files changed in Phase N must note expected state after Phase N (e.g., "After Phase 3 consolidation, helpers are in conftest.py").
   - **Phases ≤8 steps each** — Split phases with >8 steps or add an internal checkpoint. Large phases without checkpoints make diagnosis difficult when early steps break things.
   - **Cross-cutting issues scope-bounded** — If a cross-cutting issue is only partially addressed, explicitly note what's in scope and what's deferred. Prevents executing agent from attempting unscoped refactors.
   - **No vacuous steps** — Every step must produce a functional outcome (behavior change, data transformation, verified state). Steps that only create scaffolding (directory, import, registration) without functional result merge into the nearest behavioral step.
   - **Foundation-first ordering within phases** — Order steps: existence → structure → behavior → refinement. If step N operates on a structure, that structure must exist from step N-k, not step N+k.
   - **Collapsible step detection** — Adjacent steps modifying the same file or testing edge cases of the same function should collapse. Note collapse candidates for Point 0.85 consolidation gate.

3. **Review outline:**
   - Delegate to `runbook-outline-review-agent` (fix-all mode)
   - Agent fixes all issues (critical, major, minor)
   - Agent returns review report path

4. **Validate and proceed:**
   - Read review report
   - If critical issues remain: STOP and escalate to user
   - Otherwise: proceed to phase-by-phase expansion

**Why outline-first:**
- Establishes cross-phase structure before expensive content generation
- Enables early feedback on phase boundaries and dependencies
- Catches requirements gaps before implementation details
- Provides roadmap for phase-by-phase expansion

**Fallback for small runbooks:**
- If outline has ≤3 phases and ≤10 total steps → generate entire runbook at once (skip phase-by-phase)
- Single review pass instead of per-phase
- Simpler workflow for simple tasks
- See also Point 0.95: if steps are already execution-ready, skip expansion entirely

---

### Point 0.85: Consolidation Gate — Outline

**Objective:** Merge trivial phases with adjacent complexity before expensive expansion.

**Actions:**

1. **Scan outline for trivial phases:**
   - Phases with ≤2 steps AND complexity marked "Low"
   - Single-constant changes or configuration updates
   - Pattern: setup/cleanup work that could batch with adjacent feature work

2. **Evaluate merge candidates:**

   For each trivial phase, check:
   - Can it merge with preceding phase? (same domain, natural continuation)
   - Can it merge with following phase? (prerequisite relationship)
   - Would merging create >10 steps in target phase? (reject if so)

3. **Apply consolidation:**

   **Merge pattern:**
   ```markdown
   ## Phase N: [Combined Name]

   ### [Original feature steps]
   ### [Trivial work as final steps]
   ```

   **Do NOT merge if:**
   - Trivial phase has external dependencies (blocking other work)
   - Merged phase would exceed 10 steps
   - Domains are unrelated (forced grouping hurts coherence)

4. **Update traceability:**
   - Adjust requirements mapping table
   - Update phase structure in outline
   - Note consolidation decisions in Expansion Guidance

**When to skip:**
- Outline has no trivial phases
- All trivial phases have cross-cutting dependencies
- Outline is already compact (≤3 phases)

**Rationale:** Rather than standalone trivial steps that fragment execution, batch simple work with adjacent complexity. This reduces orchestrator overhead and creates natural commit boundaries.

---

### Point 0.9: Complexity Check Before Expansion

**Objective:** Assess expansion complexity BEFORE generating step content. Gate expensive expansion with callback mechanism.

**Actions:**

1. **Assess expansion scope:**
   - Count total steps from outline
   - Identify pattern-based steps (same structure, different inputs)
   - Identify algorithmic steps (unique logic, edge cases)
   - Estimate token cost of full expansion

2. **Apply fast-path if applicable:**
   - **Pattern steps (≥5 similar):** Generate pattern template + variation list instead of per-step expansion
   - **Trivial phases (≤2 steps, low complexity):** Inline instructions instead of full step format
   - **Single constant change:** Skip step, add as inline task

3. **Callback mechanism -- if expansion too large:**

   **Callback triggers:**
   - Outline exceeds 25 steps → callback to design (scope too large)
   - Phase exceeds 10 steps → callback to outline (phase needs splitting)
   - Single step too complex → callback to outline (decompose further)

   **Callback levels:**
   ```
   `step` → `runbook outline` → `design` → `design outline` → `requirements`
   ```

   **When callback triggered:**
   - STOP expansion
   - Document issue: "Phase N contains [issue]. Callback to [level] required."
   - Return to previous level with specific restructuring recommendation
   - DO NOT proceed with expensive expansion of poorly-structured work

4. **Proceed with expansion:**
   - Only if complexity checks pass
   - Fast-path applied where appropriate
   - Callback mechanism available for discovered issues

**Rationale:** Complexity assessment is a planning concern (sonnet/opus). Don't delegate to haiku executor — they optimize for completion, not scope management. Catch structural problems before expensive expansion.

---

### Point 0.95: Outline Sufficiency Check

**Objective:** Skip expensive expansion when the outline is already detailed enough to serve as the runbook.

**Sufficiency criteria — ALL must hold:**
- Every step specifies target files/locations
- Every step has a concrete action (no "determine"/"evaluate options"/"choose between" language remaining)
- Every step has verification criteria or is self-evidently complete (deletion, path correction)
- No unresolved design decisions in step descriptions

**If sufficient → promote outline to runbook:**

1. **Reformat step headings:** Convert `**Step N.M: title**` → `## Step N.M: title` (prepare-runbook.py requires H2 headers)
2. **Convert step content:** Step bullets become body content under each H2 heading
3. **Add Common Context:** Extract from outline's Key Decisions, Requirements Mapping, and design reference into `## Common Context` section
4. **Add frontmatter:** name, model (from outline metadata or design)
5. **Preserve phase structure:** `### Phase N: title` headers kept as-is (prepare-runbook.py skips them, uses for grouping)
6. **Write to:** `plans/<job>/runbook.md`
7. **Skip to Point 4** — Points 1, 2, 2.5, 3 are unnecessary (expansion adds boilerplate around content that's already there; assembly is N/A for single-file promotion; reviews already happened at outline level)

**If not sufficient → proceed with normal Point 1 expansion.**

**Rationale:** Outlines that have been through quality checklist (Point 0.75 step 2) and review (Point 0.75 step 3) often contain execution-ready detail. Expansion rewrites the same information in a different format. The sufficiency check prevents this waste while ensuring under-specified outlines still get full expansion.

---

### Point 1: Phase-by-Phase Runbook Expansion

**For each phase identified in the outline, generate detailed content with review.**

**For each phase:**

1. **Generate phase content:**
   - **Read Expansion Guidance:** Check for `## Expansion Guidance` section at end of `plans/<job>/runbook-outline.md`. If present, incorporate recommendations (consolidation candidates, step expansion notes, checkpoint guidance) into phase content generation.
   - File: `plans/<job>/runbook-phase-N.md`
   - Include full step details for this phase
   - Use script evaluation for each task (see section 1.1-1.3 below)

2. **Review phase content:**
   - Delegate to `vet-fix-agent` (fix-all mode)
   - Agent reviews, applies all fixes, writes report
   - Agent returns review report path

   **Domain Validation:**

   When writing vet checkpoint steps, check if a domain validation skill exists at `agent-core/skills/<domain>-validation/SKILL.md` for the artifact types being reviewed. If found, include domain validation in the vet step:

   - Add "Domain validation" instruction to vet-fix-agent delegation
   - Reference the skill file path
   - Specify artifact type (e.g., skills, agents, hooks, commands, plugin-structure)
   - Domain criteria are additive — generic quality + alignment checks still apply

   Example: For plugin development work, include:
   ```
   - **Domain validation:** Read and apply criteria from
     `agent-core/skills/plugin-dev-validation/SKILL.md`
     for artifact type: [skills|agents|hooks|commands|plugin-structure]
   ```

3. **Apply fixes:**
   - Read review report
   - Apply all fixes (critical, major, minor)
   - Update phase file with fixes

4. **Finalize phase:**
   - Phase content approved
   - Proceed to next phase

**Script evaluation for tasks within each phase:**

**1.1 Small Tasks (≤25 lines)**: Write complete script inline

**Criteria:**
- Script is short and standalone
- Logic is straightforward
- No complex dependencies

**Example:**
```bash
#!/usr/bin/env bash
# Compare two files and output diff
diff -u /path/to/file1 /path/to/file2 > output.patch || true
echo "Diff size: $(wc -c < output.patch) bytes"
```

**Step type classification:**

Before writing step content, classify each step:

- **Transformation** (delete, move, rename, replace pattern): Self-contained recipe sufficient. Executor applies mechanically.
- **Creation** (new test for existing behavior, new integration, new code touching existing paths): MUST include investigation prerequisite: `**Prerequisite:** Read [file:lines] — understand [behavior/flow]`

**Why:** Executors in throughput mode treat all steps as recipes. Creation steps attempted without understanding the target code produce trial-and-error failures. The planner encodes the investigation the executor would otherwise skip.

**1.2 Medium Tasks**: Provide prose description of implementation

**Criteria:**
- Implementation requires 25-100 lines
- Logic is clear but too long for inline script
- Steps are sequential and well-defined

**Example:**
```
Implementation:
1. Verify source files exist (provide error if missing)
2. Read both files using Read tool
3. Compare content line-by-line
4. Document differences in structured format
5. Write analysis to specified output path
```

**1.3 Large/Complex Tasks**: Separate planning session required

**Criteria:**
- Task requires >100 lines or complex logic
- Multiple design decisions needed
- Significant architectural choices
- Requires human review before implementation

**Action:** Mark task as requiring separate planning session. Delegate planning to sonnet or opus depending on complexity.

### Mandatory Conformance Validation Steps

**Trigger:** When design document includes external reference (shell prototype, API spec, visual mockup) in `Reference:` field or spec sections.

**Requirement:** Runbook MUST include validation steps that verify implementation conforms to the reference specification.

**Mechanism:**
- Reference is consumed during planning
- Expected behavior from reference becomes validation criteria in runbook steps
- Validation can be: conformance test cycles, manual comparison steps, or automated conformance checks

**Validation precision (from Gap 4):**
- When using test-based validation: Use precise prose descriptions with exact expected strings
- Example validation criterion: "Output matches shell reference: `🥈 sonnet \033[35m…` with double-space separators"
- NOT abstracted: "Output contains formatted model with appropriate styling"

**Rationale:** Conformance validation closes the gap between specification and implementation. Exact expected strings prevent abstraction drift.

**Related:** See testing.md "Conformance Validation for Migrations" for detailed guidance.

---

### Point 1.4: Planning-Time File Size Awareness

**Convention:** When a step adds content to an existing file, note current file size and plan splits proactively.

**Process:**

1. **For each step adding content to existing file:** Note `(current: ~N lines, adding ~M)`
2. **Check threshold:** If `N + M > 350`, include a split step in the same phase
3. **Threshold rationale:** The 400-line limit is a hard fail at commit time. Planning to 350 leaves a 50-line margin for vet fixes and minor additions

**Why 350:** Planning to the exact 400-line limit creates brittleness. A 50-line margin is pragmatic — accounts for vet review additions, formatting changes, and minor refactoring that happen during execution.

**Example:**
- Step 2.3 adds authentication handlers to routes.py (current: ~330 lines, adding ~35)
- Step 2.3: Implement authentication handlers (~365 lines total)
- Step 2.4: Split routes.py into routes_auth.py + routes_core.py

**No runtime enforcement:** This is a planning convention. The commit-time `check_line_limits.sh` remains the hard gate. This prevents write-then-split rework loops.

---

### Point 2: Assembly and Weak Orchestrator Metadata

**After all phases are finalized, validate phase files are ready for assembly, then delegate to prepare-runbook.py.**

**Actions:**

1. **Pre-assembly validation:**
   - Verify all phase files exist (`runbook-phase-1.md` through `runbook-phase-N.md`)
   - Check phase reviews completed (all phase review reports in `reports/` directory)
   - Confirm no critical issues remain in review reports

2. **Metadata preparation:**
   - Count total steps across all phases
   - Extract Common Context elements from design
   - Verify Design Decisions section ready for inclusion

3. **Final consistency check:**
   - Review cross-phase dependencies
   - Verify step numbering is sequential
   - Check for phase boundary issues
   - No new content generation, only validation

**IMPORTANT — Do NOT manually assemble:**
- Phase files remain separate until prepare-runbook.py processes them
- Manual concatenation bypasses validation logic (step numbering, metadata calculation)
- prepare-runbook.py will handle assembly in Point 4

Every assembled runbook MUST include this metadata section at the top:

```markdown
## Weak Orchestrator Metadata

**Total Steps**: [N]

**Execution Model**:
- Steps X-Y: Haiku (simple file operations, scripted tasks)
- Steps A-B: Sonnet (semantic analysis, judgment required)
- Steps M-N: Opus (only if explicitly required for complex design)

**Step Dependencies**:
- Sequential | Parallel | [specific dependency graph]

**Error Escalation**:
- Haiku → Sonnet: [triggers]
- Sonnet → User: [triggers]

**Report Locations**: [pattern for where reports go]

**Success Criteria**: [overall runbook success, not per-step]

**Prerequisites**:
- [Prerequisite 1] (✓ verified via [method])
- [Prerequisite 2] (path: /absolute/path/to/resource)
```

**Critical Requirements:**
- **Total Steps**: Exact count for tracking
- **Execution Model**: Match model capability to task complexity
- **Step Dependencies**: Enable orchestrator to parallelize when possible
- **Error Escalation**: Clear triggers for when to escalate
- **Success Criteria**: Overall runbook success (step-level criteria go in step sections)
- **Prerequisites**: Verified before execution starts
- **Report Locations**: Where execution reports will be written

**What DOES NOT belong in orchestrator metadata:**
- Inline scripts or prose step descriptions (those go in step sections)
- Objective/expected outcome for each step (those go in step sections)
- Per-step validation/error handling (those go in step sections)
- Per-step success criteria (those go in step sections)

**Key Principles:**
1. **Orchestrator metadata is coordination info only** - not execution details
2. **Orchestrator trusts agents to report accurately** - no inline validation logic
3. **Validation is delegated** - if needed, it's a separate plan step
4. **Planning happens before execution** - orchestrator doesn't make decisions during execution

---

### Point 2.5: Consolidation Gate — Runbook

**Objective:** Merge isolated trivial steps with related features after assembly validation.

**Actions:**

1. **Identify isolated trivial steps:**
   - Steps marked for fast-path during Point 0.9
   - Single-line changes or constant updates
   - Steps with no validation assertions (pure configuration)

2. **Check merge candidates:**

   For each trivial step:
   - **Same-file steps:** Merge with adjacent step modifying same file
   - **Setup steps:** Promote to phase preamble (not separate step)
   - **Cleanup steps:** Demote to phase postamble

3. **Apply step consolidation:**

   **Merge into adjacent step:**
   ```markdown
   ## Step N: [Feature Name]

   **Additional setup:** [trivial work folded in — e.g., update constant, add import]

   **Objective**: [Original step objective]

   **Implementation:**
   [Standard implementation content including merged trivial work]
   ```

   **Convert to inline instruction:**
   ```markdown
   **Pre-phase setup:**
   - Update config constant to X
   - Add import statement for Y

   ## Step N: [First real step]
   ```

4. **Update metadata:**
   - Adjust Total Steps count
   - Update step numbering if merges occurred
   - Note consolidations in runbook header

**Constraints:**
- Never merge steps across phases
- Preserve isolation when needed (don't merge if steps would conflict)
- Keep merged steps manageable (avoid overloading single step)

**When to skip:**
- No trivial steps identified in Point 0.9
- All steps have substantial validation coverage
- Runbook is already compact (<15 steps)

**Rationale:** Trivial steps add orchestrator overhead. A haiku executor can handle "update constant X and then implement feature Y" in one delegation. Consolidation reduces round-trips without losing coverage.

---

### Point 3: Final Holistic Review

**After assembly, perform final cross-phase review of complete runbook.**

**Delegation Pattern:**

```
Task(
  subagent_type="vet-agent",
  model="sonnet",
  prompt="Review the assembled runbook at [runbook-path] for completeness, correctness, and executability.

  Focus on cross-phase issues:
  - Step numbering consistency
  - Dependency ordering across phases
  - Metadata accuracy (step counts, model assignments)
  - Overall coherence

  CRITICAL: Also validate all file paths referenced in the runbook exist in the codebase.
  Use Glob to verify each path. Flag missing files as critical issues.

  If runbook includes requirements context: Verify implementation steps satisfy requirements.

  Write detailed review to: [review-path]

  Return only the filepath on success, or 'Error: [description]' on failure."
)
```

**Agent responsibilities:**
1. Review assembled runbook using vet protocol
2. Focus on cross-phase consistency (individual phases already reviewed)
3. Validate all referenced file paths exist
4. Write review report to specified path
5. Return filepath or error to orchestrator

**Orchestrator receives:**
- Filepath: `plans/foo/reports/runbook-review.md` (success)
- Error: `Error: Runbook file not found at [path]` (failure)

**Revision Loop:**
1. Read review report from filepath
2. Check assessment status (Ready / Needs Minor Changes / Needs Significant Changes)
3. If "Needs Minor Changes" or "Needs Significant Changes":
   - **REQUIRED:** Apply all fixes (critical, major, minor)
   - Update runbook with fixes
   - Delegate re-review if changes are significant
   - Iterate until assessment is "Ready"
4. If "Ready":
   - Proceed to Point 4 (artifact preparation)
5. If error returned:
   - Escalate to user

**Fix Application Policy:**
- All issues (critical, major, minor) MUST be fixed before proceeding
- Never proceed with unaddressed issues

**Note:** Individual phase reviews already happened (Point 1). This final review checks holistic consistency only.

---

### Point 4: Prepare Runbook Artifacts

**CRITICAL: This step is MANDATORY. Use `prepare-runbook.py` to create execution artifacts.**

**Why artifact preparation is fundamental:**

The entire point of the plan-specific agent pattern is **context isolation**. Each step gets a fresh agent invocation with ONLY:
- Common context (metadata, prerequisites, design decisions)
- The specific step to execute
- NO execution transcript from previous steps

**Benefits of preparation:**
- Prevents context bloat from accumulating across steps
- Each step starts with clean slate (no noise from previous steps)
- Execution logs stay in report files, not in agent context
- Enables plan-specific agent pattern with context caching
- Sequential steps ESPECIALLY need splitting (to prevent cumulative bloat)

**When NOT to prepare:**
- Never. Always prepare. This is not negotiable.

After runbook is reviewed and ready, use the preparation script to create artifacts.

**Use prepare-runbook.py Script:**

The script is located at: `agent-core/bin/prepare-runbook.py`

**Script Features:**
- Parses runbook with optional YAML frontmatter
- Extracts Common Context section
- Extracts individual Step sections (## Step N: or ## Step N.M:)
- Creates plan-specific agent (baseline + common context)
- Generates step files for execution
- Creates orchestrator plan
- Validates structure and reports errors clearly

**Usage:**
```bash
agent-core/bin/prepare-runbook.py <runbook-file.md>
```

**Example:**
```bash
agent-core/bin/prepare-runbook.py plans/oauth2-auth/runbook.md
```

**Script automatically derives paths:**
- Runbook name: From parent directory (e.g., `oauth2-auth` from `plans/oauth2-auth/runbook.md`)
- Plan-specific agent: `.claude/agents/<runbook-name>-task.md`
- Step files: `plans/<runbook-name>/steps/step-N.md` or `step-N-M.md`
- Orchestrator plan: `plans/<runbook-name>/orchestrator-plan.md`

**Runbook Format Requirements:**

**Optional YAML frontmatter:**
```yaml
---
name: custom-name  # Override derived name
model: sonnet      # Default model for plan-specific agent
---
```

**Required sections:**
- Steps: `## Step N:` or `## Step N.M:` headings
- At least one step must be present

**Optional sections:**
- `## Common Context` - Shared context for all steps
  - **Output optimization:** Factorize repetitive content (stop conditions, dependencies, conventions) to Common Context
  - Reduces planner token output by eliminating per-step boilerplate
  - Steps inherit context automatically during runbook compilation
- `## Orchestrator Instructions` - Custom orchestrator guidance

**Benefits of prepare-runbook.py:**
- Automatic path derivation (no manual file creation)
- Validation (fails on missing baseline, duplicate steps, etc.)
- Idempotent (re-runnable after runbook updates)
- Consistent artifact structure
- Plan-specific agent with cached context

### 4.1: Automated Post-Processing

**After prepare-runbook.py succeeds, perform these steps automatically.**

**Step 1: Run prepare-runbook.py** with sandbox bypass:
```bash
agent-core/bin/prepare-runbook.py plans/{name}/runbook.md
# MUST use dangerouslyDisableSandbox: true (writes to .claude/agents/)
```
- If script fails: STOP and report error to user

**Step 2: Copy orchestrate command to clipboard:**
```bash
echo -n "/orchestrate {name}" | pbcopy
```

**Step 3: Tail-call `/handoff --commit`**

As the **final action** of this skill, invoke `/handoff --commit`. This:
- Hands off session context (marks planning complete, adds orchestration as pending)
- Then tail-calls `/commit` which commits everything and displays the next pending task

The next pending task (written by handoff) will instruct: "Restart session, switch to haiku model, paste `/orchestrate {name}` from clipboard."

**Why restart:** prepare-runbook.py creates a new agent in `.claude/agents/`. Claude Code only discovers agents at session start.

---

## Checkpoints

Checkpoints are verification points inserted between phases. They validate accumulated work and create commit points.

**Two checkpoint tiers:**

**Light checkpoint** (Fix + Functional):
- **Placement:** Every phase boundary
- **Process:**
  1. **Fix:** Run `just dev`, sonnet quiet-task diagnoses and fixes failures, commit when passing
  2. **Functional:** Sonnet reviews implementations against design
     - Check: Are implementations real or stubs? Do functions compute or return constants?
     - If stubs found: STOP, report which implementations need real behavior
     - If all functional: Proceed to next phase

**Full checkpoint** (Fix + Vet + Functional):
- **Placement:** Final phase boundary, or phases marked `checkpoint: full` in runbook
- **Process:**
  1. **Fix:** Run `just dev`, sonnet quiet-task diagnoses and fixes failures, commit when passing
  2. **Vet:** Sonnet reviews accumulated changes (presentation, clarity, design alignment)
     - **REQUIRED:** Apply all fixes (critical, major, minor)
     - Commit when complete
  3. **Functional:** Sonnet reviews implementations against design (same checks as light checkpoint)

**When to mark `checkpoint: full` during planning:**
- Phase introduces new public API surface or contract
- Phase crosses module boundaries (changes span 3+ packages)
- Runbook expected to exceed 20 steps total

**Rationale:** Light checkpoints catch dangerous issues (broken tests, stubs) at low cost. Full checkpoints catch quality debt (naming, duplication, abstraction) at boundaries where accumulated changes justify the vet review cost.

**Example:**
```markdown
## Step 3: Add error handling (final step of Phase 2)
[standard implementation content]

---

**Light Checkpoint** (end of Phase 2)
1. Fix: Run `just dev`. Sonnet quiet-task fixes failures. Commit when green.
2. Functional: Review Phase 2 implementations against design. Check for stubs.

---

## Step 4: Add validation (Phase 3 begins)
[standard implementation content]

---

**Full Checkpoint** (end of Phase 3 - final phase)
1. Fix: Run `just dev`. Sonnet quiet-task fixes failures. Commit when green.
2. Vet: Review all changes for quality, clarity, design alignment. Apply all fixes. Commit.
3. Functional: Review all implementations against design. Check for stubs.
```

---

## Critical Constraints

**Tool Usage:**
- Use **Task** to delegate review and complex steps
- Use **Read** to check existing files
- Use **Write** to create runbook files
- Use **Bash** for mkdir and python3 script execution
- Use **Edit** if modifying existing runbooks

**Model Selection:**
- **Haiku**: Simple execution, scripted tasks, file operations
- **Sonnet**: Default for planning and review, semantic analysis
- **Opus**: Only when explicitly required for complex architecture

**Error Handling:**
- Report all errors explicitly
- Never suppress errors with `|| true` unless intentional
- Define clear escalation triggers
- Document recovery protocol

**Output Locations:**
- Runbook: `plans/[runbook-name]/runbook.md` or `[name]-plan.md`
- Execution logs: `plans/[runbook-name]/reports/`
- Step files: `plans/[runbook-name]/steps/` (created by script)
- Plan-specific agent: `.claude/agents/[runbook-name]-task.md` (created by script)
- Orchestrator plan: `plans/[runbook-name]/orchestrator-plan.md` (created by script)

**Validation:**
- Success criteria must be measurable
- Use specific file paths (absolute)
- Include size/count checks
- Specify required sections/format

## Example Execution Flow

### Example 1: Direct Implementation (Point 0 Bypass)

**User:** `/plan-adhoc` for learnings consolidation

**Agent:**

**Point 0: Orchestration Assessment**

Analyzing task:
- Design complete: `plans/learnings-consolidation/design.md`
- Components: 4 files (directory, script, 2 skill updates)
- All straightforward (<100 lines each)
- No complex coordination
- Can implement + test in single session

**Assessment: Implement directly** (orchestration overhead not justified)

Proceeding with direct implementation...

*[Agent implements components directly]*
*[Agent delegates to vet agent for review]*

### Example 2: Runbook Creation (Orchestration Needed)

**User:** `/plan-adhoc` for implementing authentication feature

**Agent:**

**Point 0: Orchestration Assessment**

Analyzing task:
- Multiple independent components (config, routes, session, profile, tests)
- Steps could be parallelized
- Tests require separate planning session
- Long-running execution across multiple phases

**Assessment: Create runbook** (orchestration justified)

**Point 0.5: Discover Codebase**

*Uses Glob/Grep to verify file paths from design*
*Scans memory-index.md for related constraints*

**Point 0.75: Generate Runbook Outline**

*Creates runbook outline with 3 phases, 8 steps*
*Delegates to runbook-outline-review-agent (fix-all)*
*Receives: "plans/oauth2-auth/reports/outline-review.md"*

**Point 1: Phase-by-Phase Expansion**

*Phase 1: Configuration and Setup*
- Generates runbook-phase-1.md
- Delegates to vet-agent (review-only)
- Applies all fixes

*Phase 2: Core Implementation*
- Generates runbook-phase-2.md
- Delegates to vet-agent (review-only)
- Applies fixes

*Phase 3: Testing*
- Generates runbook-phase-3.md
- Marks for separate planning session
- Delegates to vet-agent (review-only)

**Point 2: Assembly and Metadata**

*Concatenates phases into runbook.md*
*Adds Weak Orchestrator Metadata*
*Final consistency check*

**Point 3: Final Holistic Review**

*Delegates to vet-agent for cross-phase review*
*Receives: "Review complete - All checks passed - READY"*

**Point 4: Prepare Artifacts**

*Runs prepare-runbook.py to create execution artifacts*

```bash
agent-core/bin/prepare-runbook.py plans/oauth2-auth/runbook.md
```

Artifacts created:
- Plan-specific agent: `.claude/agents/oauth2-auth-task.md`
- Steps: `plans/oauth2-auth/steps/step-{1,2,3,4,5,6,7,8}.md`
- Orchestrator plan: `plans/oauth2-auth/orchestrator-plan.md`

Ready for execution. Use `/orchestrate` to execute the runbook."

## Runbook Template Structure

**Main Runbook File:**

```markdown
---
name: runbook-name  # Optional: override directory-based name
model: haiku        # Optional: default model for plan-specific agent
---

# [Runbook Name]

**Context**: [Brief description of what this runbook accomplishes]

**Source**: [Reference to requirements, design docs, or parent plan]
**Design**: [Reference to design decisions document if applicable]

**Status**: [Draft / In Review / Ready / Complete]
**Created**: YYYY-MM-DD
**Reviewed**: YYYY-MM-DD ([reviewer], [assessment])
**Revised**: YYYY-MM-DD (if applicable)

---

## Weak Orchestrator Metadata

[Metadata section as defined in Point 2]

---

## Common Context

[Shared information for all steps]

**Requirements (from design):**
- FR-1: [summary] — addressed by [design element]
- FR-2: [summary] — addressed by [design element]
- NFR-1: [summary] — addressed by [design element]

**Scope boundaries:** [in/out of scope]

**Key Constraints:**
- [Constraint 1]
- [Constraint 2]

**Project Paths:**
- [Path 1]: [Description]
- [Path 2]: [Description]

**Conventions:**
- [Convention 1]
- [Convention 2]

---

## Step 1: [Step Name]

**Objective**: [Clear, concise objective]

**Script Evaluation**: [Direct execution / Small script / Prose description / Separate planning]

**Execution Model**: [Haiku / Sonnet / Opus]

**Implementation**:
[Inline script OR prose steps OR reference to separate plan]

**Expected Outcome**: [What should happen when successful]

**Unexpected Result Handling**:
- If [condition]: [Action to take]

**Error Conditions**:
- [Error type] → [Escalation action]

**Validation**:
- [Validation check 1]
- [Validation check 2]

**Success Criteria**:
- [Measurable criterion 1]
- [Measurable criterion 2]

**Report Path**: [Absolute path to execution log]

---

[Repeat for each step]

---

## Orchestrator Instructions

[Optional: Custom instructions for weak orchestrator]

Default behavior if omitted:
- Execute steps sequentially using [runbook-name]-task agent
- Stop on error and escalate to sonnet

---

## Design Decisions

[Document key decisions made during planning]

---

## Dependencies

**Before This Runbook**:
- [Prerequisite 1]
- [Prerequisite 2]

**After This Runbook**:
- [What can be done next]
- [Artifacts available for downstream work]

---

## Revision History

**Revision 1 (YYYY-MM-DD)** - [Summary of changes]
**Revision 2 (YYYY-MM-DD)** - [Summary of changes]

**Review report**: [Path to review report]

---

## Notes

[Additional context, assumptions, or important details]
```

## Common Pitfalls

**Avoid:**
- Creating runbooks when direct implementation is better (skipping Point 0)
- Assuming file paths from conventions without Glob/Grep verification (skipping Point 0.5)
- Skipping outline generation (Point 0.75) for complex runbooks
- Generating entire runbook monolithically instead of phase-by-phase
- Assuming prerequisites are met without verification
- Assigning semantic analysis tasks to haiku
- Leaving design decisions for "during execution"
- Vague success criteria ("analysis complete" vs "analysis has 6 sections with line numbers")
- Writing success criteria that only check structure ("file exists", "exit code 0") when the step should produce functional output. Verify content/behavior, not just existence.
- Missing error escalation triggers
- Conflating execution logs and analysis artifacts
- Using relative paths instead of absolute
- Deferring validation to future phases
- Forgetting to run prepare-runbook.py after review

**Instead:**
- Verify prerequisites explicitly
- Match model to task complexity
- Make all decisions during planning
- Define measurable success criteria
- Document clear escalation triggers
- Separate execution logs from output artifacts
- Use absolute paths consistently
- Include validation in each step
- Always run prepare-runbook.py to create artifacts

## References

**Example Runbook**: `/Users/david/code/claudeutils/plans/unification/phase2-execution-plan.md`
**Example Review**: `/Users/david/code/claudeutils/plans/unification/reports/phase2-plan-review.md`
**Preparation Script**: `/Users/david/code/claudeutils/agent-core/bin/prepare-runbook.py`
**Baseline Agent**: `/Users/david/code/claudeutils/agent-core/agents/quiet-task.md`

These demonstrate the complete 4-point process in practice.

## Integration with General Workflow

**Workflow stages:**
1. `/design` - Opus creates design document
2. `/plan-adhoc` - Sonnet creates execution runbook (THIS SKILL) → auto-runs prepare-runbook.py → tail-calls `/handoff --commit`
3. `/handoff` updates session.md → tail-calls `/commit`
4. `/commit` commits everything → displays next pending task (restart instructions)
5. User restarts session, switches to haiku, pastes `/orchestrate {name}` from clipboard
6. `/orchestrate` - Haiku executes runbook steps
7. vet-fix-agent - Review and fix changes before commit
8. Complete job

**Handoff:**
- Input: Design document from `/design` skill
- Output: Ready-to-execute artifacts (agent, steps, orchestrator plan), committed and handed off
- Next: User restarts session and pastes orchestrate command from clipboard
