# Scoring Tables

Detailed criteria for each WSJF-adapted component. All components use Fibonacci-capped relative estimation — the smallest item anchors at 1.

**Research foundation:** Adapted from Reinertsen's WSJF. CoD decomposed into project-specific components replacing User-Business Value, Time Criticality, and Risk Reduction/Opportunity Enablement. See `plans/reports/task-prioritization-methodology.md` for full research basis.

---

## Cost of Delay Components

### Workflow Friction (replaces User-Business Value)

How frequently the unresolved problem is encountered during normal operation. "Users" are agents and the developer. "Value" is friction removed from recurring workflows.

| Score | Criteria | Examples |
|-------|----------|----------|
| 8 | Every task execution (inner loop) | Commit flow, precommit, vet delegation, orchestration step |
| 5 | Every session boundary | Handoff, status display, context recovery |
| 3 | Weekly or per-task-type | Worktree setup, design sessions, memory consolidation |
| 2 | Monthly or per-plan | Plugin migration, formal analysis |
| 1 | One-time or rarely invoked | External PR, infrastructure script used once |

**Evidence source:** Count occurrences in recent session transcripts or estimate from workflow step frequency.

### Decay Pressure (replaces Time Criticality)

How much more expensive the task becomes per unit time deferred.

Combines two observable phenomena:
- **Knowledge decay:** Design artifacts reference file structures, counts, or interfaces that change as other work lands
- **Decision lock-in:** Architectural decisions become load-bearing as dependent work accumulates on top

| Score | Criteria | Examples |
|-------|----------|----------|
| 8 | Design flagged stale; target files changed in 3+ of last 10 commits; OR decisions 5+ future tasks build on | Plugin migration (stale Feb 9, drift in counts); memory redesign (blocks 3+ tasks) |
| 5 | Target files changed in 1-2 of last 10 commits; design references shifting structures; OR decisions affect 2-4 future tasks | Error handling design (outline exists, codebase evolving) |
| 3 | Target area relatively stable; design references durable abstractions; limited blast radius | Commit CLI tool (commit patterns stable) |
| 2 | Self-contained with minimal external references | Precommit improvements (validators are stable) |
| 1 | No external references that can drift; fully reversible | Upstream skills field (external PR); infrastructure scripts |

**Evidence source:** `git log --oneline -10 -- <target-files>` for churn; count blocked tasks in session.md for lock-in.

### Compound Risk Reduction (replaces Risk Reduction / Opportunity Enablement)

Degree to which completing this task prevents recurring defects, unblocks downstream work, or improves agent execution reliability across ALL future work.

Three sub-dimensions — take the **maximum**:

**A. Defect compounding** — Does the task fix a pattern that propagates through orchestrated execution?

| Score | Criteria |
|-------|----------|
| 8 | Pattern in 3+ RCA findings (tmp/ refs, skill drift, confabulated methodology) |
| 5 | Pattern appeared twice or in high-throughput path |
| 3 | Pattern appeared once |
| 1 | Not a defect fix |

**B. Downstream unblock** — How many other tasks does this unblock?

| Score | Criteria |
|-------|----------|
| 8 | Unblocks 4+ tasks |
| 5 | Unblocks 2-3 tasks |
| 3 | Unblocks 1 task |
| 1 | No dependents |

**C. Agent reliability delta** — Does completing this reduce agent execution failures?

| Score | Criteria |
|-------|----------|
| 8 | Directly reduces measured failure mode (3+ occurrences) |
| 5 | Addresses failure mode observed 1-2 times |
| 3 | Proactive catch for a class of errors |
| 1 | No impact on agent reliability |

**Evidence source:** Search RCA reports in `plans/*/reports/`; count blockers in session.md; grep for failure patterns in learnings.md history.

---

## Job Size Components

### Marginal Effort (inverse of artifact readiness)

| Score | Criteria |
|-------|----------|
| 1 | `planned` — runbook exists, ready for orchestration |
| 2 | `designed` — design.md vetted, needs runbook |
| 3 | `requirements` — requirements.md exists, needs design |
| 5 | Problem statement only, no disk artifact |
| 8 | Greenfield + requires external research |

**Evidence source:** `agents/jobs.md` status column.

### Context Recovery Cost

Capped at 5 — recovery cost rarely warrants an 8; the highest practical cost is cross-session research.

| Score | Criteria |
|-------|----------|
| 1 | All context loaded via CLAUDE.md @-references |
| 2 | Requires reading 1-3 known project files |
| 3 | Requires reading 4+ files or git archaeology |
| 5 | Requires external research or recovering conversation history across sessions |

**Evidence source:** Count file references in session.md task notes.

---

## Scheduling Modifiers

These do not affect priority score but constrain batching and ordering.

### Model Tier Cohort

Tasks requiring the same model tier batch together to amortize session setup cost (especially opus).

**Detection:** Read model annotation from session.md task metadata. Default is sonnet if omitted.

### Restart Cohort

Tasks requiring restart batch adjacently to minimize restart count.

**Detection:** Look for `restart` flag in session.md task metadata.

### Self-Referential Flag

Tasks that modify their own execution path (e.g., improving the prioritize skill itself) need special handling — cannot be validated by the system they change.

**Detection:** Check if task's target files overlap with workflow/skill definitions used during execution.

### Parallelizability

Tasks with no shared plan directory, no shared target files, and no dependency can run in concurrent worktrees.

**Conflict check:** Compare target file sets between tasks. Empty intersection = parallelizable.

---

## Worked Example

**Task: Precommit improvements**
- WF=8 (every commit, inner loop)
- DP=2 (validators are stable, minimal drift)
- CRR=5 (tmp/ ref pattern appeared 2+ times in RCA)
- CoD = 8+2+5 = 15
- ME=5 (problem statement only, no design artifact)
- CRC=1 (precommit scripts are in CLAUDE.md context)
- Size = 5+1 = 6
- **Priority = 15/6 = 2.5**
- Modifiers: sonnet, no restart
