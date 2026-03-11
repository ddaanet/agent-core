---
name: proof
description: >-
  This skill should be used when a planning artifact needs structured user
  validation. Invoked by hosting skills (/design, /runbook, /requirements) at
  review integration points. Triggers on "proof", "validate artifact",
  "review loop", or when a hosting skill reaches a review stage. Replaces
  ad-hoc single-turn validation with reword-accumulate-sync protocol.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, Task, AskUserQuestion, Skill
user-invocable: true
---

# Proof — Structured Artifact Validation

Structured review loop for planning artifacts. Replaces single-turn "does this look right?" with iterative reword-validate-accumulate protocol. Invoked inline by hosting skills (/design, /runbook, /requirements) at review integration points.

**Why a skill, not a reference file:** Structure requires enforcement. Enforcement requires gates. Gates require tool calls (codified in "When Anchoring Gates With Tool Calls"). The Skill tool invocation is the gate — forces protocol steps into attention focus. The previous 21-line `discussion-protocol.md` reference file failed to enforce (Bootstrap session evidence).

## Invocation

```
/proof <artifact-path>
```

Runs inline (no `context: fork`) — shares the hosting skill's context window, sees all loaded artifacts and discussion history. The hosting skill invokes `/proof` via the Skill tool at its review stage.

## Loop Mechanics

### Entry

**Planstate (D+B anchor):** Write review-pending state to lifecycle:

```bash
echo "$(date +%Y-%m-%d) review-pending — /proof <artifact>" >> plans/<job>/lifecycle.md
```

**Read the artifact under review.** If the artifact path contains a glob pattern (e.g., `runbook-phase-*.md`), expand via Glob and read all matching files — present as a single composite review target. A runbook is one artifact composed of multiple phase files; /proof treats the collection as a unit.

Present a concise summary: key decisions, scope boundaries, structure. Then enter the loop — wait for user feedback.

### Reword

Restate user feedback as an understanding statement:

> "Understanding: [restatement]. Correct?"

Wait for user confirmation or correction before proceeding. Do not apply changes based on unvalidated interpretation. This step catches misunderstandings before they compound.

### Accumulate

Each validated round adds to a running decision list (in-memory, not file):

```
- D-1: [validated understanding] -> [artifact impact]
- D-2: [validated understanding] -> [artifact impact]
```

Track: decision number, the validated understanding, which artifact section is affected.

### Sync

On user request ("sync", "resync", "show decisions"), output the full accumulated decision list with artifact impacts. Useful after multiple rounds to verify accumulated state.

### Terminal Actions

Loop continues until user issues a terminal action:

**"proceed" / "apply":**
1. Apply all accumulated decisions to the artifact
2. If artifact is a planning artifact: dispatch lifecycle-appropriate corrector (see Corrector Dispatch below)
3. Present corrector findings before returning control to hosting skill (gate, not pass-through)
4. Update planstate: `echo "$(date +%Y-%m-%d) reviewed — /proof <artifact>" >> plans/<job>/lifecycle.md`
5. Return control to hosting skill

**"learn":**
Capture insight to `agents/learnings.md`. Resume loop (not terminal unless user also says proceed).

**"suspend":**
Prepend `/design plans/<skill-fix>` to current continuation (existing continuation-prepend mechanism). Route to /design for skill update before resuming current work.

## Corrector Dispatch

When terminal action is "apply" and artifact is a planning artifact, dispatch the lifecycle-appropriate corrector as a sub-agent (Task tool, clean context). This makes corrector dispatch lifecycle-driven: artifact type + "edits applied" -> corrector fires. The user does not say "run correctors."

| Artifact Pattern | Corrector | subagent_type |
|-----------------|-----------|---------------|
| outline.md | outline-corrector | outline-corrector |
| design.md | design-corrector | design-corrector |
| runbook-outline.md | runbook-outline-corrector | runbook-outline-corrector |
| runbook-phase-*.md | runbook-corrector (/review-plan) | runbook-corrector |
| requirements.md | -- (user-validated directly) | -- |

**Corrector prompt includes:**
- Artifact path under review
- Accumulated decisions (context on what changed)
- Review-relevant entries from `plans/<job>/recall-artifact.md` if present
- Report path: `plans/<job>/reports/<artifact-stem>-proof-review.md`

**Handle corrector result:**
- Read review report from returned filepath
- If UNFIXABLE issues: present to user, re-enter loop for resolution
- If all fixed: return control to hosting skill

**Skip corrector when:** Artifact is requirements.md (user-validated directly via AskUserQuestion), accumulated decision list is empty (no changes to apply — "proceed" with no feedback), or accumulated decisions are documentation-only (no structural changes to the artifact).

## Author-Corrector Coupling

When /proof's hosting skill is /design and the design modifies an "author" skill (a skill whose output is reviewed by a corrector), check coupled dependencies using the Author-Corrector Coupling section in `/design` SKILL.md (dependency mapping table and visible output requirement). Source of truth: T1-T6.5 in `agents/decisions/pipeline-contracts.md`.

## Layered Defect Model

- **/requirements** = prevention layer. Captures domain context before design, preventing defect classes entirely.
- **Post-expansion /proof** = detection layer. Catches systemic defects correctors cannot — novel defect classes not yet in corrector rules.

Evidence: wrong-RED/bootstrap defect passed all correctors, detectable only by human review at expansion point. The two layers are complementary, not redundant.

## Integration Points

Invoked at 5 points across 3 hosting skills:

| Hosting Skill | Stage | Artifact | Defect Layer |
|---------------|-------|----------|-------------|
| /requirements | Step 5 | requirements.md | Prevention |
| /design | Phase B (Post-outline) | outline.md | Approach validation |
| /design | Phase C.4.5 (Post-design review) | design.md | Design validation |
| /runbook | Phase 0.75 step 5 | runbook-outline.md | Structural validation |
| /runbook | Post-Phase 3 (Post-holistic review) | runbook-phase-*.md | Systemic detection |

## Anti-Patterns

- **Single-turn validation:** "Does this look right?" -> "yes" -> proceed. No reword, no accumulation. Misses misunderstandings.
- **File-edit-centric loop:** Apply changes inline during discussion without accumulation. Loses track of decisions vs changes.
- **Skipping corrector after apply:** Decisions applied but no corrector review. Planning artifacts need lifecycle-appropriate review after modification.
- **Reference file instead of skill:** A reference file cannot enforce protocol steps. The Skill tool invocation is the structural gate.
