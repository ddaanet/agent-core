---
name: prioritize
description: Score and rank pending tasks by priority. Triggers on "prioritize", "score the backlog", "rank tasks", "reprioritize", or task ordering needs. WSJF-adapted scoring producing priority-ordered tables with parallel batches.
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

Run `claudeutils _worktree ls` for plan statuses. Output includes per-plan status (`requirements`, `outlined`, `designed`, `planned`, `ready`, `review-pending`, `rework`, `reviewed`, `delivered`) and next actions.

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

Construct a JSON array with one object per task containing the scored components, then pipe to the scoring script:

```bash
echo '<json>' | python3 plans/prototypes/score.py
```

**JSON input format** (per task):
```json
{"task": "Task Name", "wf": 5, "dp": 3, "crr": 5, "me": 2, "crc": 1, "modifiers": "sonnet"}
```

The script computes CoD, Size, Priority (rounded to 1 decimal), applies tiebreaking (CRR → Size → WF), and sorts descending.

### 4. Apply Scheduling Modifiers

After scoring, annotate each task with scheduling constraints (do not affect score):

- **Model tier cohort:** Group opus tasks together, sonnet tasks together (amortize session setup)
- **Restart cohort:** Tasks requiring restart should be batched adjacently
- **Self-referential flag:** Tasks modifying their own execution path need manual verification
- **Parallelizability:** Tasks with no shared plan directory, no shared target files, no dependency can run in concurrent worktrees

### 5. Generate Output

Produce two artifacts:

**Priority Table:** Use the markdown table output from Step 3 (`plans/prototypes/score.py`). The script produces a ranked table with columns: Rank, Task, WF, DP, CRR, CoD, ME, CRC, Size, Priority, Modifiers.

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

## References

- **`references/scoring-tables.md`** — Full Fibonacci scoring tables for all five components, evidence source guidance, and worked examples
