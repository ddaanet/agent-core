---
name: inline
description: >-
  Sequence inline execution lifecycle: pre-work, execute, post-work.
  Triggers on /inline, "execute inline", "run task", or when /design and
  /runbook route Tier 1/2 execution-ready work. Wraps corrector dispatch,
  triage feedback, and deliverable-review chaining.
allowed-tools: Task, Read, Write, Edit, Bash, Grep, Glob, Skill
user-invocable: true
continuation:
  cooperative: true
  default-exit: ["/handoff", "/commit"]
---

# Inline Execution Lifecycle

Sequence the lifecycle for execution-ready work: context loading, implementation, corrector review, triage feedback, deliverable-review chaining. Replaces ad-hoc execution sequences in /design Phase B/C.5 and /runbook Tier 1/2.

Covers Tier 1 (direct) and Tier 2 (delegated) execution — same lifecycle, different scale. Tier 3 uses /orchestrate.

## Entry Points

| Entry | Args pattern | Caller | Pre-work |
|-------|-------------|--------|----------|
| Default | `plans/<job>` | Cold start (`x` from session.md) | Full |
| Execute | `plans/<job> execute` | /design, /runbook (context loaded) | Skip |

Check for `execute` token in args → chained invocation (skip Phase 2). Absent → cold start (full workflow).

## Phase 1: Entry Gate

**Git state (D+B anchor):**

```bash
git status --porcelain
```

Non-empty → STOP: "Dirty tree. Commit or stash before /inline."

```bash
just precommit
```

Failure → STOP: "Precommit failing. Fix before /inline."

**Capture baseline** — before any edits:

```bash
BASELINE=$(git rev-parse HEAD)
```

Store for Phase 4b (triage feedback script input).

## Phase 2: Pre-Work (cold start only)

Skip entirely when entry point is `execute` — caller has loaded all context.

### 2.1 Task Context Recovery

```bash
plugin/bin/task-context.sh '<task-name>'
```

### 2.2 Brief Check

Read `plans/<job>/brief.md` if present (cross-tree context from other sessions). In worktrees: `git show main:plans/<job>/brief.md 2>/dev/null`.

### 2.3 Recall (D+B anchor — tool call required)

1. Read `agents/memory-index.md` (skip if already in context). Select execution-domain triggers — patterns for implementing this, not classifying it.
2. If `plans/<job>/recall-artifact.md` exists: `edify _recall resolve plans/<job>/recall-artifact.md` — artifact mode resolves all entry keys in one call.
3. Resolve additional triggers from memory-index not in artifact: `edify _recall resolve "when <trigger>" ...`
4. No relevant entries (no artifact, no triggers selected): `edify _recall resolve null` — proves gate was reached.

### 2.4 Reference Loading

Load domain-relevant skills and reference files specified in the task description (e.g., `plugin-dev:skill-development` for skill work, `plugin/fragments/continuation-passing.md` for cooperative skills).

## Phase 3: Execute

Perform implementation: edits, TDD cycles for behavioral code, prose changes. This skill provides lifecycle wrapper only — execution approach comes from caller's design/plan.

### Direct Execution (Tier 1)

Edits performed in current session. No delegation.

### Delegated Execution (Tier 2)

When execution dispatches sub-agents (artisan, test-driver):

**Sub-agent recall:** Curate subset of plan recall-artifact entries relevant to delegation target. Write separate artifact per type (e.g., `plans/<job>/tdd-recall-artifact.md`). Include in each prompt: "Read `plans/<job>/<type>-recall-artifact.md`, then batch-resolve via `edify _recall resolve`."

**Piecemeal TDD dispatch:** One cycle per invocation. Resume same agent between cycles (preserves context). Fresh agent when context nears 150k.

**Cycle-scoped prompt composition:** Extract only the current cycle's section from the runbook (`## Cycle X.Y:` to next `---` or `## Cycle`). Include the runbook's Common Context section and recall entries alongside the cycle spec. Do NOT include adjacent or future cycles in the test-driver prompt — scope enforced by context absence, not prose instruction. The executing session holds the full runbook for sequencing; test-driver sees only its cycle.

**Context isolation:** Parent does cognitive work (selecting entries, curating context). Child does mechanical work (resolving entries, executing). Sub-agents have no parent context.

**test-driver commit contract:** test-driver commits each cycle. Caller does not add commit instructions. Expect clean tree on resume.

**Post-step verification (single compound command — do not split):**

```bash
git status --porcelain && just lint
```

After each delegated step. Dirty tree or lint failure → diagnose before continuing.

**Design constraints non-negotiable:** When design specifies explicit classifications or patterns, include LITERALLY in delegation prompt. Agents apply design rules, not invent alternatives.

**Artifact-type model override:** opus for edits to skills, fragments, agents, design documents — regardless of task complexity.

**No mid-execution checkpoints.** Corrector (Phase 4a) is the sole semantic review. Post-step lint catches mechanical issues. Triage feedback (Phase 4b) collects uninterrupted execution data. Revisit after 10+ Tier 2 executions show compounding drift.

## Phase 4: Post-Work

### 4a: Review Gate (D+B anchor)

**Both paths require a tool call on `plans/<job>/reports/`. Neither is skippable.**

#### Path A: Review Dispatch (default)

Route changed files to the appropriate reviewer per `plugin/fragments/review-requirement.md` routing table.

**Dispatch process:**
1. List changed files: `git diff --name-only $BASELINE`
2. Group by artifact type (code/tests/plans, skill definitions, agent definitions, design documents)
3. Look up reviewer per group from routing table
4. Dispatch each group to its reviewer using `references/review-dispatch-template.md` for prompt structure

**Two dispatch patterns:**
- **Fix-capable reviewers** (corrector, agent-creator, design-corrector): Delegate, read report, grep UNFIXABLE. Agent applies fixes directly.
- **Report-only reviewers** (skill-reviewer): Delegate, read report, apply fixes in calling session. Agent has Read/Grep/Glob only.

**Common fields per dispatch:**
- **Scope:** uncommitted changes for this artifact group — implementation only
- **Design context:** `plans/<job>/outline.md` or `design.md`
- **Recall artifact:** `plans/<job>/recall-artifact.md` (reviewer resolves entries)
- **Report:** `plans/<job>/reports/review.md` (or `review-<type>.md` when multiple groups)

Planning artifacts → runbook-corrector (not this gate).

If recall artifact absent: lightweight recall fallback (template details in reference file).

**Structural proof (D+B anchor):** After review completes, verify report exists:

```
Read(plans/<job>/reports/review.md)
```

This Read proves reviewer produced output. Without it, Phase 4b cannot proceed.

**Handle result:** Read each review report. If UNFIXABLE issues present → STOP, surface to user with report path. Do not proceed to 4b until all issues are resolved or accepted.

#### Path B: Review Skip (gated escape hatch)

When review is genuinely unnecessary (trivial session.md-only edits, plan artifact cleanup), skip is permitted — but requires an auditable artifact:

```
Write(plans/<job>/reports/review-skip.md)
```

Content must include: what was changed, why review adds no value for this specific change, what verification was performed instead. The justification must be specific enough to survive deliverable-review scrutiny.

**Skip is not confidence-gated.** "Scope is small" or "well-tested" are not valid skip justifications — review exists precisely to catch issues confidence misses.

### 4b: Triage Feedback

```bash
plugin/bin/triage-feedback.sh plans/<job> $BASELINE
```

Read script output. On divergence message → surface inline. On match or no-classification → proceed silently.

### 4c: Deliverable-Review Chain

Final phase before continuation. Write the pending task directly to `agents/session.md`:

`- [ ] **Deliverable review: <job>** — /deliverable-review plans/<job> | opus | restart`

**Section targeting:** On main → Worktree Tasks. In a worktree → In-tree Tasks. Detect via `git rev-parse --git-dir` (`.git` = main, otherwise worktree).

Write explicitly — do not rely on handoff to capture from conversation context.

## Delegation Protocol Summary

| Aspect | Rule |
|--------|------|
| Recall | Parent curates, child resolves |
| TDD dispatch | Piecemeal — one cycle per invocation, resume between, cycle-scoped prompt |
| Context | Sub-agents have no parent context |
| Commits | test-driver commits; caller omits commit instructions |
| Post-step | `git status --porcelain` clean + `just lint` |
| Model | opus for skills/fragments/agents/design edits |
| Checkpoints | None mid-execution; corrector is sole review |

## Continuation

As the **final action** of this skill:

1. Read continuation from `additionalContext` (first skill in chain) or from `[CONTINUATION: ...]` suffix in Skill args (chained skills)
2. If skill needs a subroutine before continuing: prepend entries to continuation (existing entries stay in original order — append-only invariant)
3. If continuation present: peel first entry from (possibly modified) continuation, tail-call with remainder
4. If no continuation: default-exit — `/handoff` → `/commit`

**CRITICAL:** Do NOT include continuation metadata in Task tool prompts.

**On failure:** Abort remaining continuation. Record in session.md Blockers: which phase failed, error category, remaining continuation orphaned.
