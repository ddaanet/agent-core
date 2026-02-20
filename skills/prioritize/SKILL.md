---
name: prioritize
description: This skill should be used when the user asks to "prioritize tasks", "score the backlog", "what should I work on next", "rank pending tasks", "reprioritize", "reorder backlog", or needs to determine task ordering from session.md. Applies WSJF-adapted scoring to produce priority-ordered tables with parallel batches.
allowed-tools: Read, Grep, Glob, Bash
user-invocable: true
---

# Score and Rank Pending Tasks

Score pending tasks using WSJF-adapted methodology. Produce a priority-ordered table with scheduling modifiers and parallel batch identification.

**Formula:** `Priority = Cost_of_Delay / Job_Size`

- **Cost of Delay** = Workflow Friction + Decay Pressure + Compound Risk Reduction
- **Job Size** = Marginal Effort + Context Recovery Cost

All components scored on Fibonacci scale (1, 2, 3, 5, 8). Higher priority score = do first.

## Procedure

### 1. Load Task Inventory

Read `agents/session.md` Pending Tasks section. Extract each task with:
- Task name
- Command/skill reference
- Model tier
- Plan directory (if any)
- Notes and context

Call `list_plans(Path('plans'))` for plan status of each task (requirements/designed/planned/ready).

### 2. Score Each Task

For each pending task, score five components on a Fibonacci scale. Consult `references/scoring-tables.md` for detailed criteria, evidence collection methods, and worked examples.

**Cost of Delay components:**
- **Workflow Friction** (1-8)
- **Decay Pressure** (1-8)
- **Compound Risk Reduction** (1-8): Max of defect compounding, downstream unblock, agent reliability delta

**Job Size components:**
- **Marginal Effort** (1-8): Driven by jobs.md status
- **Context Recovery Cost** (1-5)

**Evidence-based scoring:** Use observable evidence, not intuition — each scoring table in the reference file includes an evidence source annotation.

### 3. Calculate Priority

```
CoD = Workflow_Friction + Decay_Pressure + Compound_Risk_Reduction
Size = Marginal_Effort + Context_Recovery_Cost
Priority = CoD / Size
```

Round to one decimal place. For equal scores, prefer higher Compound Risk Reduction (defect fixes compound).

### 4. Apply Scheduling Modifiers

After scoring, annotate each task with scheduling constraints (do not affect score):

- **Model tier cohort:** Group opus tasks together, sonnet tasks together (amortize session setup)
- **Restart cohort:** Tasks requiring restart should be batched adjacently
- **Self-referential flag:** Tasks modifying their own execution path need manual verification
- **Parallelizability:** Tasks with no shared plan directory, no shared target files, no dependency can run in concurrent worktrees

### 5. Generate Output

Produce two artifacts:

**Priority Table:**

```
| Rank | Task | WF | DP | CRR | CoD | ME | CRC | Size | Priority | Modifiers |
|------|------|----|----|-----|-----|----|-----|------|----------|-----------|
| 1    | ...  | 8  | 2  | 5   | 15  | 2  | 1   | 3    | 5.0      | sonnet    |
```

Column key: WF=Workflow Friction, DP=Decay Pressure, CRR=Compound Risk Reduction, ME=Marginal Effort, CRC=Context Recovery Cost.

**Parallel Batches:**

Identify groups of 2+ tasks that can execute concurrently:
- No shared plan directory
- No shared target files
- No logical dependency
- Compatible model tier

```
Parallel batch (sonnet, no restart):
- Task A (priority 3.2)
- Task B (priority 2.8)

Parallel batch (opus):
- Task C (priority 2.5)
- Task D (priority 2.0)
```

### 6. Write Report

Write the scored output to `plans/reports/prioritization-<date>.md` where `<date>` is YYYY-MM-DD.

Include:
- Priority table (sorted descending)
- Parallel batches
- Top 5 recommendations with brief rationale
- Scoring assumptions or judgment calls made

## Tiebreaking

When priority scores are equal:
1. Higher Compound Risk Reduction wins (defect fixes compound)
2. Lower Job Size wins (smaller work items unblock faster)
3. Higher Workflow Friction wins (more frequent pain)

## When to Re-Score

Re-run prioritization when:
- 5+ new tasks added since last scoring
- Major work completed that changes dependency graph
- Design or plan status changes (affects Marginal Effort scores)

## Additional Resources

### Reference Files

For detailed scoring criteria and evidence sources:
- **`references/scoring-tables.md`** — Full Fibonacci scoring tables for all five components, evidence source guidance, and worked examples
