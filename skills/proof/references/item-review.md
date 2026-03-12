# Item Review Reference

Detailed patterns for item detection, granularity, accumulation, and presentation. Core loop mechanics are in SKILL.md — this file provides the detection and format specifications.

## Granularity Detection

Parse artifact structure to identify reviewable items. Detection is automatic based on artifact type:

| Artifact type | Pattern | Item granularity |
|--------------|---------|-----------------|
| requirements.md | `**FR-N:**` / `**NFR-N:**` / `**C-N:**` | Individual requirement/constraint |
| outline.md | `### D-N:` decision headings or `## Section` headings | Decision or section |
| design.md | `## Section` headings | Design section |
| runbook-phase-*.md | Cycle/step markers (`## Cycle`, `## Step`) | Individual cycle or step |
| Source files | Function/class definitions | Function or class |
| Diff output | Hunk markers (`@@`) | Individual hunk |

**Fallback:** No recognized pattern detected → artifact is one item. Loop runs once. Orientation shows "1 item."

## Hierarchical Splitting

Large items auto-split into sub-items. No metric-based threshold — judgment-based indicators:

- **Multiple independent concerns:** Item addresses 2+ unrelated topics (working memory overload — Cowan's ~4 concurrent items limit)
- **Visual context loss:** Item requires scrolling past a single screen of content
- **Internal structure:** Item contains sub-headings, enumerated sub-items, or other markers suggesting natural decomposition points

When splitting: present parent item title, then sub-items as "Item N.1 of N.K", "Item N.2 of N.K". Sub-items inherit the parent's position in the linear order.

## Accumulation Format

Verdicts accumulate in-memory during iteration. The verdict list is the structured input for batch-apply — the agent works from this list, not from memory of the discussion.

```
- V-1: [item identifier] — approve
- V-2: [item identifier] — revise: "[user's stated fix]"
- V-3: [item identifier] — kill (delete only)
- V-4: [item identifier] — kill (absorb → plans/foo/requirements.md)
- V-5: [item identifier] — skip
```

**Item identifier:** Use the item's title or heading text (e.g., "FR-3: Per-item recall pass", "D-1: Verdict Vocabulary"). Must be unambiguous within the artifact.

**Revise detail:** Capture the user's stated fix verbatim — this is the edit specification for batch-apply. The discussion sub-loop may refine the fix before the verdict is recorded.

**Kill sub-actions (planning artifacts only):** After `k` verdict, prompt: "Delete only, or absorb into another artifact?" If absorb: user names the target artifact, and the transfer is recorded in the verdict list. Both deletion and transfer execute during batch-apply.

## Batch-Apply Execution

On terminal action "apply" after user confirms the verdict summary:

- **approve** — no edit needed (item unchanged)
- **revise** — apply the stated fix to the item in the artifact file
- **kill (delete)** — remove the item from the artifact
- **kill (absorb)** — remove from source artifact, append to named target artifact
- **skip** — no edit needed (item unchanged, explicitly deferred)

Apply edits bottom-to-top within the file to avoid line-shift interference between edits. For multi-file composites (runbook phases), apply per-file independently.

## Cross-Item Outputs

During iteration, normal loop actions produce immediate side effects (distinct from verdict application which is batched):

- **learn** — appended to `agents/learnings.md` immediately
- **pending** — captured for handoff via `p:` semantics immediately
- **brief** — context transferred to worktree immediately

These are listed in the verdict summary under "Cross-item outputs" so the user sees the full picture before confirming apply.

## Revisit

After completing iteration through all items, user can revisit any previously-reviewed item:

- Identification is flexible: by number ("revisit 3"), by title ("revisit FR-3"), or by content description
- Agent matches semantically — no exact-match requirement
- Re-enter verdict prompt for the identified item
- New verdict replaces previous in the accumulation list
- Returns to post-iteration state (not back into the linear sequence)
