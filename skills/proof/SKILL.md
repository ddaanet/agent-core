---
name: proof
description: >-
  This skill should be used when a planning artifact needs structured user
  validation. Invoked by hosting skills (/design, /runbook, /requirements) at
  review integration points. Triggers on "proof", "validate artifact",
  "review loop", or when a hosting skill reaches a review stage. Replaces
  ad-hoc single-turn validation with item-by-item review protocol.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, Task, AskUserQuestion
user-invocable: true
---

# Proof — Structured Artifact Validation

Item-by-item review loop for planning artifacts. Presents discrete items with per-item verdicts, accumulates decisions, applies as batch. Replaces single-turn "does this look right?" with forced-verdict iteration grounded in Fagan inspection (per-item detection, reader-paraphrase) and cognitive load research (segmentation, forced verdict).

**Why a skill, not a reference file:** Structure requires enforcement. Enforcement requires gates. Gates require tool calls. The Skill tool invocation is the gate — forces protocol steps into attention focus.

## Invocation

```
/proof <artifact-path>
```

Runs inline (no `context: fork`) — shares the hosting skill's context window, sees all loaded artifacts and discussion history. The hosting skill invokes `/proof` via the Skill tool at its review stage.

## Item Review Loop

### State Output (D+B anchor)

Emit a state line at every transition point. The act of generating the state line forces the agent to know which state it's in and what actions are available — protocol adherence becomes a side effect of producing the output.

**Format:**

```
[proof: <state> <artifact> | decisions: <N> | actions: <action-list>]
```

- **State:** `reviewing`, `applying`, `complete`
- **Artifact:** filename under review (e.g., `outline.md`)
- **Decisions:** count of accumulated decisions
- **Actions:** available user actions at this point

**Emission rules:**

| Transition | State | Actions shown |
|-----------|-------|---------------|
| Entry (after summary) | `reviewing` | Full: `feedback, proceed, learn, suspend, sync` |
| After accumulate | `reviewing` | Compact: omit actions (user has seen them) |
| After sync | `reviewing` | Compact |
| Terminal apply | `applying N decisions` | None |
| Terminal no-change | `complete — no changes` | None |

**Example (entry):**

```
[proof: reviewing outline.md | decisions: 0 | actions: feedback, proceed, learn, suspend, sync]
```

**Example (after 2 decisions accumulated):**

```
[proof: reviewing outline.md | decisions: 2]
```

**Example (terminal):** Self-contained sentence form — no pipe-separated segments:

```
[proof: applying 3 decisions to outline.md]
[proof: complete — no changes to outline.md]
```

### Entry

**Planstate (D+B anchor):** Write review-pending state to lifecycle:

```bash
echo "$(date +%Y-%m-%d) review-pending — /proof <artifact>" >> plans/<job>/lifecycle.md
```

**Read the artifact under review.** If the artifact path contains a glob pattern (e.g., `runbook-phase-*.md`), expand via Glob and read all matching files — present as a single composite review target.

**Detect items.** Parse artifact structure to identify reviewable items. See `references/item-review.md` for granularity detection table and splitting indicators. When artifact has no detectable sub-items, it is one item — the loop runs once.

### Orientation

Before item iteration, present:

- **Preamble:** Artifact under review, total item count, detected granularity
- **Item list:** Numbered list with per-item title + agent-generated one-line summary
- **Checkpoint:** Wait for user response before first item. User may: reorder items, skip sections, adjust scope, or proceed as-is

### Item Iteration

Present items in document order. Each item:

```
**Item N of M: [item title]**

[item content — plain text, not blockquote]

Recall: [domain-relevant context if any, or omitted if none]

Verdict? (a)pprove (r)evise (k)ill (s)kip
```

**Per-item recall (FR-3):** Before presenting each item, resolve domain-relevant recall entries for that item's topic. Null recall is silent — no "no relevant context found" noise.

**Verdicts** — 4 explicit, uniform across all artifact types:
- **approve** (a) — item correct, no changes
- **revise** (r) — user states fix, recorded for batch-apply
- **kill** (k) — item removed; sub-action prompt for planning artifacts: "Delete only, or absorb into another artifact?" If absorb: user names target, content transfer recorded in verdict list
- **skip** (s) — explicit deferral, item persists unchanged

**Non-verdict input is implicit discussion.** Any response that isn't a recognized verdict shortcut enters the discussion sub-loop for that item. The conversational medium makes explicit "discuss" actions unnecessary.

### Discussion Sub-Loop

When user provides non-verdict input on an item, enter discussion scoped to that item:

**Reword:** Restate user feedback as understanding statement: "Understanding: [restatement]. Correct?" Wait for confirmation before proceeding.

**Accumulate:** Each validated round adds to a per-item decision list (in-memory). Returns to verdict prompt with accumulated understanding when discussion concludes.

**Sync:** On user request ("sync", "show decisions"), output the full accumulated verdict list across all items.

### Iteration Guards

**No direct edits during iteration.** Refuse execution-oriented requests (file edits, skill chains to /runbook, /deliverable-review, /codify, external plugins). This gate prevents bare-directive bypass of the review workflow.

**Normal loop actions** available throughout iteration, resume review after:
- **learn** — capture insight to `agents/learnings.md`
- **pending** — capture task for handoff (`p:` semantics)
- **brief** — transfer context to worktree

**Emit state line** after showing decisions:

```
[proof: reviewing <artifact> | decisions: <N>]
```

### Terminal Actions

**"apply":**
1. Display full verdict summary: N approved, N revised, N killed, N skipped (unchanged), cross-item outputs (learnings, pending tasks, artifacts)
2. User confirms
3. Apply all verdicts as batch edits to artifact (revise edits, kill deletions, absorb transfers)
4. Dispatch lifecycle-appropriate corrector (see Corrector Dispatch below)
5. Present corrector findings
6. Update planstate: `echo "$(date +%Y-%m-%d) reviewed — /proof <artifact>" >> plans/<job>/lifecycle.md`
7. Return control to hosting skill

**Skip semantics:** Explicit deferral — affirmative decision to accept as-is without evaluation, not silent omission. Non-blocking — does not prevent apply. Listed prominently in summary with distinct count. No tracking obligation — skipped items do not carry forward as open items or generate pending tasks.

**"discard":** Abandon all verdicts. Artifact unchanged. Update planstate: `echo "$(date +%Y-%m-%d) review-abandoned — /proof <artifact>" >> plans/<job>/lifecycle.md`

**Skip corrector when:** Accumulated verdict list has no revise/kill verdicts (all approved/skipped — no artifact changes to review).

### Loop Actions

Available during and after item iteration (non-terminal — resume review after):

**"revisit":** Change verdict for a previously-reviewed item. Identification is flexible — by number, title, or content. Re-enter verdict prompt. Returns to post-iteration state (not back into the linear sequence).

## Corrector Dispatch

When terminal action is "apply" and verdicts include revise or kill, dispatch the lifecycle-appropriate corrector as a sub-agent (Task tool, clean context). Corrector dispatch is lifecycle-driven: artifact type + "edits applied" → corrector fires.

| Artifact Pattern | Corrector | subagent_type |
|-----------------|-----------|---------------|
| outline.md | outline-corrector | outline-corrector |
| design.md | design-corrector | design-corrector |
| runbook-outline.md | runbook-outline-corrector | runbook-outline-corrector |
| runbook-phase-*.md | runbook-corrector | runbook-corrector |
| requirements.md | -- (user-validated directly) | -- |
| inline-plan.md | -- (no corrector) | -- |

**Corrector prompt includes:**
- Artifact path under review
- Accumulated verdict list (context on what changed)
- Review-relevant entries from `plans/<job>/recall-artifact.md` if present
- Report path: `plans/<job>/reports/<artifact-stem>-proof-review.md`

**Handle corrector result:**
- Read review report from returned filepath
- If UNFIXABLE issues: present findings to user, enter scoped discussion on corrector findings (not full re-iteration of original items)
- If all fixed: return control to hosting skill

## Author-Corrector Coupling

When /proof's hosting skill is /design and the design modifies an "author" skill (a skill whose output is reviewed by a corrector), check coupled dependencies via T1-T6.5 in `agents/decisions/pipeline-contracts.md` (dependency mapping table and visible output requirement).

## Layered Defect Model

- **/requirements** = prevention layer. Captures domain context before design, preventing defect classes entirely.
- **Post-expansion /proof** = detection layer. Catches systemic defects correctors cannot — novel defect classes not yet in corrector rules.

Evidence: wrong-RED/bootstrap defect passed all correctors, detectable only by human review at expansion point. The two layers are complementary, not redundant.

## Integration Points

Invoked at 8 points across 3 hosting skills:

| Hosting Skill | Stage | Artifact | Defect Layer |
|---------------|-------|----------|-------------|
| /requirements | Step 5 | requirements.md | Prevention |
| /design | Moderate agentic-prose (Post-code-reading) | inline-plan.md | Moderate scope validation |
| /design | Moderate non-prose (Post-code-reading) | outline.md | Moderate scope validation |
| /design | Phase B (Post-outline) | outline.md | Approach validation |
| /design | Phase C.4.5 (Post-design review) | design.md | Design validation |
| /runbook | Tier 2 (Post-outline-corrector) | runbook-outline.md | Tier 2 scope validation |
| /runbook | Phase 0.87 (Post-simplification, unconditional) | runbook-outline.md | Pre-expansion validation |
| /runbook | Post-Phase 3 (Post-holistic review) | runbook-phase-*.md | Systemic detection |

## Anti-Patterns

- **Single-turn validation:** "Does this look right?" → "yes" → proceed. No reword, no accumulation. Misses misunderstandings.
- **Immediate edits during iteration:** Applying file edits inline during review instead of accumulating verdicts. Loses track of decisions, prevents batch-apply atomicity.
- **Skipping corrector after apply:** Verdicts applied but no corrector review. Planning artifacts need lifecycle-appropriate review after modification.
- **Silent skipping:** Advancing past an item without an explicit verdict. Every item gets a disposition — skip is the explicit "defer" action, not silence.
- **Random-access navigation:** Jumping to arbitrary items during iteration. Linear presentation prevents skip-ahead bias. Revisit is post-completion only.
