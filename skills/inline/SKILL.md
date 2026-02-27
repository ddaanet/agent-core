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
  default-exit: ["/handoff --commit", "/commit"]
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
agent-core/bin/task-context.sh '<task-name>'
```

### 2.2 Brief Check

Read `plans/<job>/brief.md` if present (cross-tree context from other sessions). In worktrees: `git show main:plans/<job>/brief.md 2>/dev/null`.

### 2.3 Recall

Read `plans/<job>/recall-artifact.md`. Batch-resolve design-related entries:

```bash
agent-core/bin/when-resolve.py "<entry-1>" "<entry-2>" ...
```

If no recall artifact: lightweight recall — Read `agents/memory-index.md`, identify domain-relevant entries, batch-resolve:

```bash
agent-core/bin/when-resolve.py "when <domain-keyword-1>" "when <domain-keyword-2>" ...
```

### 2.4 Reference Loading

Load domain-relevant skills and reference files specified in the task description (e.g., `plugin-dev:skill-development` for skill work, `agent-core/fragments/continuation-passing.md` for cooperative skills).

## Phase 3: Execute

Perform implementation: edits, TDD cycles for behavioral code, prose changes. This skill provides lifecycle wrapper only — execution approach comes from caller's design/plan.

### Direct Execution (Tier 1)

Edits performed in current session. No delegation.

### Delegated Execution (Tier 2)

When execution dispatches sub-agents (artisan, test-driver):

**Sub-agent recall:** Curate subset of plan recall-artifact entries relevant to delegation target. Write separate artifact per type (e.g., `plans/<job>/tdd-recall-artifact.md`). Include in each prompt: "Read `plans/<job>/<type>-recall-artifact.md`, then batch-resolve via `agent-core/bin/when-resolve.py`."

**Piecemeal TDD dispatch:** One cycle per invocation. Resume same agent between cycles (preserves context). Fresh agent when context nears 150k.

**Context isolation:** Parent does cognitive work (selecting entries, curating context). Child does mechanical work (resolving entries, executing). Sub-agents have no parent context.

**test-driver commit contract:** test-driver commits each cycle. Caller does not add commit instructions. Expect clean tree on resume.

**Post-step verification:**

```bash
git status --porcelain  # must be clean
just lint               # must pass
```

After each delegated step. Dirty tree or lint failure → diagnose before continuing.

**Design constraints non-negotiable:** When design specifies explicit classifications or patterns, include LITERALLY in delegation prompt. Agents apply design rules, not invent alternatives.

**Artifact-type model override:** opus for edits to skills, fragments, agents, design documents — regardless of task complexity.

**No mid-execution checkpoints.** Corrector (Phase 4a) is the sole semantic review. Post-step lint catches mechanical issues. Triage feedback (Phase 4b) collects uninterrupted execution data. Revisit after 10+ Tier 2 executions show compounding drift.

## Phase 4: Post-Work

### 4a: Corrector Dispatch

Read `references/corrector-template.md` for the full dispatch template and field rules.

Delegate to corrector agent (Task, `subagent_type: "corrector"`) with:
- **Scope:** uncommitted changes (`git diff --name-only $BASELINE`) — implementation only
- **Design context:** `plans/<job>/outline.md` or `design.md`
- **Recall context:** review-relevant entries from `plans/<job>/recall-artifact.md`
- **Report:** `plans/<job>/reports/review.md`

Corrector reviews implementation changes only. Planning artifacts → runbook-corrector.

If recall artifact absent: lightweight recall fallback (template details in reference file).

**Handle result:** Read the review report. If UNFIXABLE issues present → STOP, surface to user with report path. Do not proceed to 4b until all issues are resolved or accepted.

### 4b: Triage Feedback

```bash
agent-core/bin/triage-feedback.sh plans/<job> $BASELINE
```

Read script output. On divergence message → surface inline. On match or no-classification → proceed silently.

### 4c: Deliverable-Review Chain

Final phase before continuation. State the pending task in standard session.md format:

`- [ ] **Deliverable review: <job>** — /deliverable-review plans/<job> | opus | restart`

Handoff (invoked by default-exit in the Continuation section) captures this from conversation context and writes it to session.md.

## Delegation Protocol Summary

| Aspect | Rule |
|--------|------|
| Recall | Parent curates, child resolves |
| TDD dispatch | Piecemeal — one cycle per invocation, resume between |
| Context | Sub-agents have no parent context |
| Commits | test-driver commits; caller omits commit instructions |
| Post-step | `git status --porcelain` clean + `just lint` |
| Model | opus for skills/fragments/agents/design edits |
| Checkpoints | None mid-execution; corrector is sole review |

## Continuation

As the **final action** of this skill:

1. Read continuation from `additionalContext` (first skill in chain) or from `[CONTINUATION: ...]` suffix in Skill args (chained skills)
2. If continuation present: peel first entry, tail-call with remainder
3. If no continuation: default-exit — `/handoff --commit` → `/commit`

**CRITICAL:** Do NOT include continuation metadata in Task tool prompts.

**On failure:** Abort remaining continuation. Record in session.md Blockers: which phase failed, error category, remaining continuation orphaned.
