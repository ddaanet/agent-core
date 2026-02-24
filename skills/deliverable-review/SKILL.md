---
name: deliverable-review
description: >-
  This skill should be used when the user asks to "review deliverables",
  "deliverable review", "review implementation quality", "review plan output",
  "check design conformance", "artifact review", "quality review", or after
  completing a plan execution that produced production artifacts. Two-layer
  review: optional delegated per-file depth for large deliverable sets,
  mandatory interactive review with full cross-project context. Severity-classified
  report grounded in ISO 25010 / IEEE 1012.
allowed-tools:
  - Task
  - Read
  - Grep
  - Glob
  - Bash
  - Write
user-invocable: true
---

# Review Production Artifacts

Review production artifacts against a design specification to identify conformance gaps, correctness issues, coverage holes, and excess artifacts.

## When to Use

- After plan execution completes (all phases done, commits landed)
- When session.md lists a deliverable review as pending task
- On explicit user request to review implementation quality

**Not for:** In-progress work (use corrector during phase execution), design documents (use design-corrector), or planning artifacts (use runbook-corrector). Deliverable review runs after all phases are committed.

## Prerequisites

Before starting, gather:
- **Design document** — the conformance baseline (`plans/<plan>/design.md`)
- **Plan directory** — for report output (`plans/<plan>/reports/`)

## Process

### Phase 1: Inventory

1. Read the design's Scope section (IN/OUT) to establish expected deliverables
2. Run exact command: `agent-core/bin/deliverable-inventory.py` (no arguments, no pipes, no redirect). Outputs markdown tables: per-file diff stats and summary by type
3. Classify each deliverable by artifact type (script auto-classifies, verify):

| Type | Pattern | Review axes |
|------|---------|-------------|
| Code | `*.py` source | Universal + robustness, modularity, testability, idempotency, error signaling |
| Test | `test_*.py` | Universal + specificity, coverage, independence |
| Agentic prose | `SKILL.md`, agent defs | Universal + actionability, constraint precision, determinism, scope boundaries |
| Human docs | Fragments, references | Universal + accuracy, consistency, completeness, usability |
| Configuration | Justfile, pyproject | Universal only |

Universal axes (all types): conformance, functional correctness, functional completeness, vacuity, excess.

Full axis definitions: `agents/decisions/deliverable-review.md`

### Phase 2: Gap Analysis

Compare inventory against design In-scope items:
- **Missing deliverables** — specified but not produced
- **Unspecified deliverables** — produced but not in design scope
- **Excess** in unspecified is acceptable if justified (edge case coverage, defensive tests)

### Phase 3: Per-Deliverable Review

Two-layer review. Layer 1 is optional (scales to large deliverable sets). Layer 2 is mandatory (catches what delegation cannot).

#### Layer 1: Delegated Per-File Review (optional)

Gate on total deliverable lines from Phase 1 inventory:

| Total lines | Strategy |
|-------------|----------|
| < 500 | **Skip Layer 1** — Layer 2 handles full review |
| 500–2000 | Two opus agents: code+test, prose+config |
| > 2000 | Three opus agents: code, test, prose+config |

When Layer 1 applies, partition deliverables by type and launch parallel review agents. Each agent receives:
- Files to review (with line counts)
- Design reference path
- Applicable review axes for its artifact types
- Output report path: `plans/<plan>/reports/deliverable-review-<type>.md`

Use `run_in_background=true` for parallel agents.

#### Layer 2: Interactive Full-Artifact Review (mandatory)

Always runs in main session with full cross-project context.

**Scope depends on whether Layer 1 ran:**

| Layer 1 | Layer 2 scope |
|---------|---------------|
| Skipped (< 500 lines) | Full review: per-file axes AND cross-cutting checks |
| Ran | Cross-cutting focus: issues delegation cannot catch |

**Cross-cutting checks (always):**
- Path consistency across documents
- API contract alignment between modules
- Naming convention uniformity
- Fragment convention compliance
- Memory index pattern verification
- Other skills' allowed-tools and frontmatter cross-reference validation
- Read `plans/<plan>/recall-artifact.md` if present — failure-mode entries (common review failures, quality anti-patterns) augment reviewer awareness of project-specific patterns. Supplements existing axes, does not replace them. If absent (design skipped, first use): do lightweight recall — Read `memory-index.md` (skip if already in context), identify review-relevant entries (quality patterns, failure modes, artifact-type conventions), batch-resolve via `agent-core/bin/when-resolve.py "when <trigger>" ...`. Proceed with whatever recall yields

**Per-file review (when Layer 1 skipped):**
- Read each deliverable and evaluate against type-specific axes
- Record findings with: file:line, axis violated, severity, description

**Why interactive is mandatory:** Delegated agents lack cross-project context — fragment conventions, memory index patterns, other skills' configurations, inter-file consistency. Layer 2 reads deliverables directly against the design spec, not delegation reports. The two layers are independent.

### Phase 4: Report

Write consolidated report to `plans/<plan>/reports/deliverable-review.md`.

**Report structure:**

```markdown
# Deliverable Review: <plan-name>

**Date:** <date>
**Methodology:** agents/decisions/deliverable-review.md

## Inventory
[Table: type, file, lines]
[Design conformance summary]

## Critical Findings
[Numbered, with file:line, design requirement, impact]

## Major Findings
[Same format]

## Minor Findings
[Grouped by category, brief]

## Gap Analysis
[Table: design requirement, status (covered/missing), reference]

## Summary
[Severity counts, assessment]
```

**Severity classification:**
- **Critical** — incorrect behavior, data loss, security, unimplemented design requirement
- **Major** — missing functionality, broken references, vacuous artifact, test gap for specified scenario
- **Minor** — style, clarity, naming, robustness edge case

**Next steps:**
1. **Lifecycle entry:** Append to `plans/<plan-name>/lifecycle.md`:
   - **Re-review:** If the plan's current lifecycle last entry is `rework`, first append `{YYYY-MM-DD} review-pending — /deliverable-review`
   - **Outcome:** `reviewed` if no Critical findings; `rework` if any Critical findings
     ```
     {YYYY-MM-DD} reviewed — /deliverable-review
     ```
     or
     ```
     {YYYY-MM-DD} rework — /deliverable-review
     ```
   - **In-main delivery:** If outcome is `reviewed` AND in the main repository (not a worktree — `git rev-parse --git-dir` returns `.git`), also append:
     ```
     {YYYY-MM-DD} delivered — /deliverable-review
     ```
2. For Critical + Major findings: create one pending task → `/design` with report reference
   - Task format: `- [ ] **Fix <plan-name> findings** — \`/design plans/<plan>/reports/deliverable-review.md\` | opus`
   - Unconditional `/design` routing — `/design` triage handles proportionality
3. Minor findings: note in report for inline fix or deferral
4. Report severity counts only. No merge-readiness language — user reads severity counts, user decides.

## References

- **Methodology** — full axis definitions, ISO/IEEE sources: `agents/decisions/deliverable-review.md`
- **Example report** — completed review with all sections: `references/example-report.md`
