---
name: deliverable-review
description: >-
  This skill should be used when the user asks to "review deliverables",
  "deliverable review", "review implementation quality", "review plan output",
  "check design conformance", "artifact review", "quality review", or after
  completing a plan execution that produced production artifacts. Delegates to
  parallel opus agents partitioned by artifact type, consolidates findings into
  a severity-classified report grounded in ISO 25010 / IEEE 1012.
allowed-tools:
  - Task
  - Read
  - Grep
  - Glob
  - Bash
  - Write
---

# Deliverable Review

Review production artifacts against a design specification to identify conformance gaps, correctness issues, coverage holes, and excess artifacts.

## When to Use

- After plan execution completes (all phases done, commits landed)
- When session.md lists a deliverable review as pending task
- On explicit user request to review implementation quality

**Not for:** In-progress work (use vet-fix-agent), design documents (use design-vet-agent), or planning artifacts (use plan-reviewer).

## Prerequisites

Before starting, gather:
- **Design document** — the conformance baseline (`plans/<plan>/design.md`)
- **Plan directory** — for report output (`plans/<plan>/reports/`)

## Process

### Phase 1: Inventory

1. Read the design's Scope section (IN/OUT) to establish expected deliverables
2. Glob for all files matching the scope patterns
3. Measure line counts per file (`wc -l`)
4. Classify each deliverable by artifact type:

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

Partition deliverables by type and launch parallel opus review agents:

**Agent partitioning strategy:**
- **Code agent** — all source modules against design spec
- **Test agent** — all test files against design test requirements + gap analysis table
- **Prose/config agent** — agentic prose, human docs, configuration against design

Each agent receives:
- Files to review (with line counts)
- Design reference path
- Applicable review axes for its artifact types
- Specific design requirements to check conformance against
- Output report path (by partition):

| Agent | Report filename |
|-------|----------------|
| Code | `deliverable-review-code.md` |
| Test | `deliverable-review-tests.md` |
| Prose/config | `deliverable-review-prose.md` |

**Agent prompt template:**

```
Review [artifact type] for the [plan-name] implementation. RESEARCH/REVIEW task — do NOT modify files except the report.

## Methodology
[List applicable axes with questions from deliverable-review.md]

## Files to Review
[File list with line counts]

## Design Reference
Read: plans/<plan>/design.md
[Extract specific design requirements relevant to this artifact type]

## Report Format
Per finding: file:line, axis violated, severity (Critical/Major/Minor), description.
Write to: plans/<plan>/reports/deliverable-review-<type>.md
Return filepath.
```

Use `run_in_background=true` for all parallel agents.

### Phase 4: Synthesis

After all agents complete:
1. Read all sub-reports
2. Write consolidated report to `plans/<plan>/reports/deliverable-review.md`

**Consolidated report structure:**

```markdown
# Deliverable Review: <plan-name>

**Date:** <date>
**Methodology:** agents/decisions/deliverable-review.md

## Inventory
[Table: type, file, lines]
[Design conformance summary]

## Critical Findings
[Numbered, with source report reference, file:line, design requirement, impact]

## Major Findings
[Same format]

## Minor Findings
[Grouped by category, brief]

## Gap Analysis
[Table: design requirement, status (covered/missing), reference]

## Summary
[Severity counts, assessment, sub-report paths]
```

**Severity classification:**
- **Critical** — incorrect behavior, data loss, security, unimplemented design requirement
- **Major** — missing functionality, broken references, vacuous artifact, test gap for specified scenario
- **Minor** — style, clarity, naming, robustness edge case

**Next steps:** The consolidated report becomes input for recovery work. Critical + Major findings → design session for fix planning. Minor findings → address inline or defer.

## Partitioning Heuristics

Scale review agents to deliverable volume:

| Total lines | Strategy |
|-------------|----------|
| < 500 | Single sonnet agent, all types |
| 500–2000 | Two opus agents: code+test, prose+config |
| > 2000 | Three opus agents: code, test, prose+config |

Opus is used because review requires architectural judgment against design specifications. For small deliverable sets (< 500 lines), sonnet provides sufficient judgment at lower cost.

## References

- **Methodology** — full axis definitions, ISO/IEEE sources: `agents/decisions/deliverable-review.md`
- **Example report** — completed review with all sections: `references/example-report.md`
