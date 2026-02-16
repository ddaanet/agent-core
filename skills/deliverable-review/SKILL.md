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

# Deliverable Review

Review production artifacts against a design specification to identify conformance gaps, correctness issues, coverage holes, and excess artifacts.

## When to Use

- After plan execution completes (all phases done, commits landed)
- When session.md lists a deliverable review as pending task
- On explicit user request to review implementation quality

**Not for:** In-progress work (use vet-fix-agent during phase execution), design documents (use design-vet-agent), or planning artifacts (use plan-reviewer). Deliverable review runs after all phases are committed.

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

**Next steps:** The consolidated report becomes input for recovery work. Critical + Major findings → design session for fix planning. Minor findings → address inline or defer.

## References

- **Methodology** — full axis definitions, ISO/IEEE sources: `agents/decisions/deliverable-review.md`
- **Example report** — completed review with all sections: `references/example-report.md`
