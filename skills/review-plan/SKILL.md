---
name: review-plan
description: |
  Review runbook quality for TDD discipline, step clarity, and LLM failure modes.
  Detects prescriptive code in GREEN phases, validates RED/GREEN
  sequencing, checks prerequisite validation, script evaluation, and step clarity.

  Use when reviewing runbooks after generation by /plan. Use when the user asks to "review runbook",
  "check runbook for prescriptive code", "validate RED/GREEN discipline", "check for implementation
  anti-patterns", "check LLM failure modes", or when /plan Phase 1/3 delegates to runbook-corrector agent.
user-invocable: false
model: sonnet
---

# Review Runbook Quality

Review runbook phase files, fix all issues, and report findings (audit trail + escalation).

---

## Purpose

**Review agent behavior:** Write review (audit trail) → Fix ALL issues → Escalate unfixable

**What this skill does:**
- Detects prescriptive implementation code in GREEN phases (TDD)
- Identifies RED/GREEN sequencing violations (TDD)
- Validates prerequisite validation and step clarity (general)
- Checks script evaluation and conformance (general)
- Detects LLM failure modes: vacuity, ordering, density, checkpoints, file growth (all)
- Validates file references and metadata accuracy (all)
- **Fixes ALL issues directly** (critical, major, minor)
- **Reports unfixable issues** for caller escalation

**Why review even when fixing:** The review report is an audit trail. It documents what was wrong and what was fixed, enabling process improvement and deviation monitoring.

---

## Document Validation

Accept TDD, general, and inline artifacts:
- **TDD:** `type: tdd` in phase metadata or `## Cycle` / `### Cycle` headers
- **General:** `## Step` / `### Step` headers or no type marker (default: general)
- **Inline:** `(type: inline)` tag in phase heading — no step/cycle headers expected
- **Mixed:** Multiple header types or inline + non-inline phases — valid (per-phase type tagging)

---

## Layered Context Model

Runbook execution uses three context layers. Review criteria apply to step/cycle content — do NOT flag content present in a higher layer as missing.

- **Baseline agent** (`agent-core/agents/artisan.md` or `test-driver.md`) — tool usage, execution protocol, error handling. Combined with all steps via prepare-runbook.py.
- **Common Context** (`## Common Context` in runbook) — project paths, constraints, cross-step dependencies. Available to all steps.
- **Step/cycle content** — step-specific instructions, validation, outcomes.

**False positive prevention:** Before flagging "missing tool reminders", "missing project paths", or "missing error escalation" in steps, verify the content isn't in baseline or Common Context. These are the three most common false positives.

---

## Recall Context

Before applying review criteria, load project-specific quality patterns:

1. **Infer plan directory** from the reviewed file path — if reviewing `plans/foo/runbook-phase-1.md` or `plans/foo/runbook.md`, the plan directory is `plans/foo/`. If no `plans/` prefix, skip recall.
2. **Recall context:** `Bash: agent-core/bin/recall-resolve.sh plans/<job>/recall-artifact.md` — if recall-resolve.sh succeeds, its output contains resolved decision content (failure modes, quality anti-patterns). Caller-provided entries take precedence; skip if already provided in the delegation prompt.
3. **If artifact absent or recall-resolve.sh fails**: do lightweight recall — Read `memory-index.md` (skip if already in context), identify review-relevant entries (quality patterns, failure modes, testing conventions), batch-resolve via `agent-core/bin/when-resolve.py "when <trigger>" ...`. Proceed with whatever recall yields.

Recall supplements, does not replace, the review criteria below.

---

## Review Criteria

### 1. GREEN Phase Anti-Pattern (CRITICAL) — TDD phases only

**Violation:** GREEN phase contains implementation code — prescribes exact code, agent becomes copier. See `references/review-examples.md` Section 1 for violation/correct examples.

### 2. RED/GREEN Sequencing — TDD phases only

**Check:** Will test actually fail in RED phase before GREEN implementation?

**Common violations:**
- Complete function signatures in first cycle (tests pass immediately)
- All parameters/features added at once (no incremental RED→GREEN)
- Error handling in "minimal" implementation (should be separate cycle)

**Correct pattern:**
- Cycle X.1: Minimal happy path only
- Cycle X.2: Add error handling
- Cycle X.3: Add optional parameters
- Cycle X.4: Add validation modes

### 3. Implementation Hints vs Prescription — TDD phases only

Hints for sequencing are acceptable; prescriptive code blocks are violations. See `references/review-examples.md` Section 3 for examples.

### 4. Test Specifications — TDD phases only

**Must have:** Specific test name, expected failure message, file location, why it will fail. See `references/review-examples.md` Section 4 for good example.

### 5. Weak RED Phase Assertions (CRITICAL) — TDD phases only

**Violation:** RED test prose only verifies structure, not behavior.

**Check:** For each RED phase, ask: "Could an executor write different tests that all satisfy this description?" If yes → VIOLATION: prose too vague.

Read `references/review-examples.md` Section 5 for indicator lists and correct prose patterns.

### 5.5. Prose Test Quality — TDD phases only

**Violation:** RED phase uses full test code instead of prose description.

**Check:** Scan RED phases for python code blocks containing `def test_*():` or multiple `assert` statements.

Read `references/review-examples.md` Section 5.5 for acceptable vs unacceptable patterns.

### 6. Metadata Accuracy — all phases

**Check:** `Total Steps` in Weak Orchestrator Metadata matches actual cycle/step count
- Count all `## Cycle X.Y:` / `### Cycle X.Y:` headers (TDD)
- Count all `## Step N.M:` / `### Step N.M:` headers (general)
- Compare to metadata value
- If mismatch → VIOLATION: metadata inaccurate

**Check:** Restart-reason verification
- For each phase claiming "Restart required: Yes", verify the stated reason matches restart trigger rules
- **Restart triggers:** agent definitions (`.claude/agents/`), hook configuration, plugin changes, MCP server configuration
- **NOT restart triggers:** decision documents, skills, fragments loaded on-demand via `/when` recall
- **Distinction:** `@`-referenced files have content loaded at startup (restart needed); indexed-but-recalled files load on-demand (no restart)
- **Detection:** Grep phase headers for "Restart required: Yes", cross-reference artifact type against trigger rules
- If reason invalid → VIOLATION: incorrect restart metadata (false restart delays execution)

### 7. Empty-First Cycle Ordering — TDD phases only

**Warning:** First cycle in a phase tests empty/degenerate case

**Check:** Does Cycle X.1 test empty input, no-op, or missing data?
- If empty case requires special handling → acceptable
- If empty case arises naturally from list processing → WARNING: reorder to test simplest happy path first

### 8. Consolidation Quality — all phases

**Check:** Merged cycles/steps maintain isolation

**Indicators of bad consolidation:**
- Merged item has >5 assertions (overloaded)
- Setup/teardown conflicts in same cycle/step
- Unrelated domains merged (forced grouping)
- Phase preamble contains testable behavior (should be a cycle/step)

**Check:** Trivial work placement

**Good patterns:**
- Config constants as phase preamble
- Import additions as setup instructions
- Single-file trivial changes merged with adjacent same-file item

**Bad patterns:**
- Trivial items left isolated (should merge or inline)
- Testable behavior hidden in preamble (needs assertion/verification)
- Cross-phase merges (never allowed)

### 9. File Reference Validation (CRITICAL) — all phases

**Violation:** Runbook references file paths that don't exist in the codebase

**Check:** Extract all file paths from:
- Common Context "Project Paths" section
- RED phase "Verify RED" commands / step verification commands
- GREEN phase "Changes" file references / step implementation paths
- Verification commands (pytest, grep, etc.)

**For each path:** Use Glob to verify the file exists. If not found, try fuzzy match.

**Classification:**
- File doesn't exist and no similar file found → CRITICAL: path fabricated
- File doesn't exist but similar files found → CRITICAL: wrong path (suggest correct files)
- Test function referenced doesn't exist in target file → CRITICAL: function not found (use Grep to locate)

### 10. General Phase Step Quality — general phases only

**10.1 Prerequisite Validation**
- Creation steps (new code touching existing paths) MUST have investigation prerequisites
- Format: `**Prerequisite:** Read [file:lines] — understand [behavior/flow]`
- Transformation steps (delete, move, rename) are exempt

**10.2 Script Evaluation**
- Steps classify size: small (≤25 lines inline), medium (25-100 prose), large (>100 separate planning)
- Verify classification matches actual step complexity
- Flag steps claiming "small" with >25 lines of inline content

**10.3 Step Clarity**
- Each step has: Objective, Implementation, Expected Outcome
- No "determine"/"evaluate options"/"choose between" language (decisions resolved at planning)
- Error conditions and validation criteria specified

**10.4 Conformance Validation**
- When design references external spec: validation steps verify conformance
- Exact expected strings from reference, not abstracted descriptions

### 10.5. Inline Phase Review — inline phases only

**Detection:** Scan phase headings for `(type: inline)` tag.

**Apply these criteria:**

**10.5.1 Vacuity (instruction specificity)**
- Each instruction must name a concrete target (file path) and operation (add/update/remove specific content)

**10.5.2 Density (verifiable outcome)**
- Outcome must be unambiguous — completion is binary, not a judgment call

See `references/review-examples.md` Section 10.5 for good/bad examples of both.

**10.5.3 Dependency ordering**
- Instructions within an inline phase must sequence correctly
- Later instructions may reference content added by earlier ones
- Fix: Reorder within phase. Cross-phase ordering issues: UNFIXABLE.

**Skip for inline phases:** GREEN/RED validation, prescriptive code detection, prerequisite validation, script evaluation, step clarity checks. These criteria apply only to TDD/general phases.

**Relationship to Section 11 (LLM Failure Modes):** For inline phases, Section 10.5 criteria supersede the type-specific (TDD/General) sub-bullets in Section 11. The type-neutral rules in Section 11 (foundation-first ordering, checkpoint spacing, file growth) still apply.

### 11. LLM Failure Modes (CRITICAL) — all phases

Five structural axes that cause execution failures. Apply regardless of phase type.

**11.1 Vacuity**
- **TDD:** Cycles where RED can pass with `assert callable(X)` or `import X`
- **TDD:** Integration wiring items where called function already tested
- **General:**
  - Scaffolding-only steps (file creation, directory setup) without functional outcome
  - Step N+1 produces outcome achievable by extending step N alone — merge
  - Consecutive steps modifying same artifact with composable changes
- **Heuristic (tdd + general):** items > LOC/20 signals consolidation needed
- **Behavioral vacuity detection (TDD):** For each cycle pair (N, N+1) on the same function, verify N+1's RED assertion would fail given N's GREEN implementation. If not, N+1 adds no constraint beyond N.
- **Behavioral vacuity detection (General):** For consecutive steps modifying the same artifact, verify N+1 produces an outcome not achievable by extending step N alone. If achievable, merge.
- Fix: Merge into nearest behavioral cycle/step
- *Grounding: LLMs produce "syntactically correct but irrelevant" code at 13.6–31.7% rate, scaling inversely with model size (Jiang et al., 2024).*

**11.2 Dependency Ordering**
- Foundation-first within phases (all types): existence → structure → behavior → refinement
- **TDD:** Item N tests behavior depending on structure from item N+k (k>0)
- **General:**
  - Steps referencing structures or output from later steps
  - Prerequisites not validated before use (step assumes prior state without check)
  - Foundation-after-behavior inversions (behavioral step before the foundational step it depends on)
- Fix: Reorder within phase. If cross-phase: UNFIXABLE (outline revision needed)
- *Grounding: WebApp1K identifies "API Call Mismatch" and "Scope Violation" as consequences of executing against wrong state (Fan et al., 2025).*

**11.3 Density**
- **TDD:** Adjacent cycles testing same function with <1 branch point difference; single edge cases expressible as parametrized row in prior cycle
- **General:**
  - Adjacent steps on same artifact with <20 LOC delta
  - Multi-step sequences collapsible to single step (shared validation, no intermediate checkpoint needed)
  - Over-granular decomposition without clear boundary (steps split by file section rather than behavioral concern)
- Entire phases with ≤3 items, all Low complexity
- Fix: Merge adjacent, parametrize edge cases, collapse trivial phases
- *Grounding: Instruction loss in long prompts — fidelity degrades as prompt grows. Trivial tests don't contribute signal (Mathews & Nagappan, 2024; Fan et al., 2025).*

**11.4 Checkpoint Spacing**
- Gaps >10 items or >2 phases without checkpoint
- Complex data manipulation phases without checkpoint
- Fix: Insert checkpoint recommendation
- *Grounding: Non-reasoning models write functional code that violates spec without remediation loops (Fan et al., 2025).*

**11.5 File Growth**
- Project lines added per item from descriptions
- Flag when projected size exceeds 350 lines (400-line enforcement threshold minus buffer)
- Fix: Insert proactive file split at phase boundary before projected threshold breach
- *Evidence: 7+ refactor escalations, >1hr wall-clock on line-limit fixes across worktree-update runbook.*

### 12. Model Assignment Review (ADVISORY) — all phases

**Check:** Model tag matches task complexity and artifact type.

**Artifact-type override violations (advisory):**
- Steps editing skills (`agent-core/skills/`), fragments (`agent-core/fragments/`),
  agents (`agent-core/agents/`), or workflow decisions (`agents/decisions/workflow-*.md`)
  assigned below opus → flag
- Pattern: Check `File:` references in `Changes` section against override paths

**Complexity-model mismatch (advisory):**
- Synthesis tasks (combining multiple source files into new artifact) assigned below sonnet → flag
- Mechanical grep-and-delete or single-line changes assigned above haiku → flag

**Advisory only.** Model assignment involves judgment — findings inform but don't block.
Do NOT mark as UNFIXABLE or CRITICAL. Report as Minor with suggested correction.

---

## Review Process

### Phase 1: Scan and Classify

**1a. Determine phase type(s):**
- Scan for `## Cycle` / `### Cycle` headers → TDD
- Scan for `## Step` / `### Step` headers → general
- Scan for `(type: inline)` in phase headings → inline
- Mixed is valid — apply type-appropriate criteria per phase

**1b. Check GREEN phases for implementation code (TDD):**

Use Grep tool to find code blocks in GREEN phases:

**Pattern:** `^\*\*GREEN Phase:\*\*`
**Context:** Use -A 20 to see 20 lines after each match
**Secondary check:** Look for ` ```python` markers in context

**For each code block found:**
1. Check if it's implementation code (not test code)
2. Check if it's in GREEN phase
3. Mark as VIOLATION

**1c. Check RED phases for full test code (TDD):**

**Pattern:** `^\*\*RED Phase:\*\*`
**Context:** Use -A 30 to see test content
**Check for:** `def test_.*\(\):` pattern inside code blocks

**1d. Check step quality (general):**
- Verify prerequisite validation for creation steps
- Check script evaluation size classification
- Verify step structure (Objective, Implementation, Expected Outcome)

### Phase 2: Validate File References

Extract all file paths referenced in the runbook. For each path:

1. Use Glob to check existence
2. If not found, search for similar files
3. Use Grep to verify referenced functions exist in their target files
4. Mark missing paths as CRITICAL violations with suggested corrections

### Phase 3: Analyze Items

**For TDD cycles:**
1. Extract RED phase: What test assertions (prose or code)?
2. Validate prose quality: Are assertions behaviorally specific?
3. Extract GREEN phase: What implementation guidance?
4. Verify RED can fail: Read the function under test, check whether expected failure actually occurs against current implementation. For `[REGRESSION]` cycles, verify assertions pass. Arithmetic verification required (e.g., compute output lengths against thresholds).

**For general steps:**
1. Check prerequisite validation presence
2. Verify step has clear objective and expected outcome
3. Check for deferred decisions ("determine", "evaluate options")
4. Validate conformance references if spec-based

**For all items:**
1. Check LLM failure modes (vacuity, ordering, density, checkpoints)
2. Verify metadata accuracy
3. Check consolidation quality

### Phase 4: Apply Fixes

**Fix-all policy:** Apply ALL fixes (critical, major, AND minor) directly to the runbook/phase file.

**Fix process:**
1. For each violation identified:
   - Determine if fixable (most are) or requires escalation (design gaps, scope issues)
   - Apply fix using Edit tool
   - Document fix in report with Status: FIXED
2. For unfixable issues:
   - Mark clearly in report with Status: UNFIXABLE
   - Explain why (missing design decision, scope conflict, etc.)
   - These require caller escalation

**Common fixes:**
- **Prescriptive code in GREEN:** Replace with behavior description + hints
- **Vague prose in RED:** Add specific expected values/patterns
- **Missing prerequisites (general):** Add investigation prerequisite
- **Deferred decisions (general):** Resolve inline or UNFIXABLE if design gap
- **Sequencing violation:** Note in report, suggest cycle restructuring (may need outline revision → UNFIXABLE)
- **Trivial items not consolidated:** Merge or inline trivial work
- **Metadata mismatch:** Update Total Steps count
- **File path errors:** Correct paths or mark for verification
- **Vacuous items:** Merge into nearest behavioral item
- **Density issues:** Collapse adjacent, parametrize edge cases

**Fix constraints:**
- Preserve item intent and scope
- Don't change requirements coverage
- Don't add new cycles/steps (escalate if needed)
- Keep behavioral descriptions accurate to design

### Phase 5: Generate Report

**Structure:**

```markdown
# Runbook Review: {name}

**Artifact**: [path]
**Date**: [ISO timestamp]
**Mode**: review + fix-all
**Phase types**: [TDD | General | Inline | Mixed (N TDD, M general, K inline)]

## Summary
- Total items: N (cycles: X, steps: Y)
- Issues found: N critical, N major, N minor
- Issues fixed: N
- Unfixable (escalation required): N
- Overall assessment: Ready | Needs Escalation

## Critical Issues

### Issue 1: [description]
**Location**: [cycle/step, line range]
**Problem**: [what's wrong]
**Fix**: [what was done]
**Status**: FIXED | UNFIXABLE (reason)

## Major Issues
[same format]

## Minor Issues
[same format]

## Fixes Applied
- [list of all fixes applied]

## Unfixable Issues (Escalation Required)
[numbered list with rationale, or "None — all issues fixed"]
```

---

## Output Format

**Report file:** `plans/<feature-name>/reports/runbook-review.md` (or `phase-N-review.md` for phase files)

Return filepath only (or with escalation note). Read `references/report-template.md` for full report structure and return format.

---

## Invocation

**Automatic:** /plan Phase 1 (per-phase) and Phase 3 (final) delegate to runbook-corrector agent
**Manual:** Delegate to runbook-corrector agent with runbook/phase file path

---

## Integration

**Workflow:**
```
/design → /plan → runbook-corrector agent (fix-all) → [escalate if needed] → prepare-runbook.py → /orchestrate
```

**Automatic review:** /plan Phase 1 triggers per-phase review, Phase 3 triggers final holistic review

**Escalation path:** If ESCALATION noted in return, caller must address unfixable issues before proceeding

