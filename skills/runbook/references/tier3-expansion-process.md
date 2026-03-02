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

**Step 3: Follow §Continuation**

Default-exit invokes `/handoff --commit` → `/commit` — hands off session context (marks planning complete, adds orchestration as pending), then commits. Next pending task instructs: "Restart session, paste `/orchestrate {name}` from clipboard."

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

## Recall Resolution Patterns

Two orchestration patterns resolve recall differently:

**Lightweight orchestration (Tier 2):** Orchestrator dispatches agents directly. Each agent runs `claudeutils _recall resolve` with keys from the recall artifact at execution time. Agent has Bash access and the artifact has pure keys. No preparation-time resolution needed.

**Full orchestration (Tier 3, prepare-runbook.py):** `prepare-runbook.py` reads `plans/<job>/recall-artifact.md` during assembly, resolves all entry keys via `claudeutils _recall resolve`, and injects resolved content into generated artifacts:
- Shared entries (no phase tag) → `## Resolved Recall` section appended to Common Context in agent definition
- Phase-tagged entries (`(phase N)` suffix) → `## Phase Recall` section appended to phase preamble in step files and phase agent

Step agents receive pre-resolved content. They do NOT run `claudeutils _recall resolve` themselves.

**Recall artifact phase tags:**

```
when writing recall artifacts — all phases
when editing skill files — phase 2 context (phase 2)
when testing patterns — phase 1 TDD (phase 1)
```

Entries without `(phase N)` suffix are shared. `prepare-runbook.py` errors if a phase tag references a nonexistent or inline phase.

**Conflicting signals constraint:** Common Context recall is ambient for all phase agents. Phase-tagged recall is scoped to one phase's agents. Do not place the same entry in both shared and phase-tagged locations with different framing — at haiku capability, persistent Common Context signal wins over step file input.

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

- Phase-neutral entries only here. Phase-specific entries use `(phase N)` tag in recall artifact — `prepare-runbook.py` resolves and injects them into phase preambles automatically.
- Format per consumer model tier:
  - Haiku/sonnet consumers: constraint format — DO/DO NOT rules with explicit applicability markers
  - Opus consumers: rationale format — key points with context
- Content baked at planning time — orchestrator does not filter recall at execution time. Planner resolves conflicting entries and removes least-specific entries when budget exceeded (eviction at planning time, not runtime). Cognitive work at the planner's model tier.
- Recall entries must avoid conflicting signals: at haiku capability, persistent ambient signal wins over per-step instructions. Curate carefully — Common Context recall is ambient for all task agents.
- DO NOT rules about recall content go here alongside the content guidance, not in a separate cleanup step.
- See "Recall Resolution Patterns" section for full two-pattern documentation.

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
