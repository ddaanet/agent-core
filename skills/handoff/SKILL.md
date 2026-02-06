---
name: handoff
description: This skill should be used when the user asks to "handoff", "update session", "end session", or mentions switching agents. Updates session.md with completed tasks, pending work, blockers, and learnings for seamless agent continuation. NOT for Haiku model orchestrators - use /handoff-haiku instead.
allowed-tools: Read, Write, Edit, Bash(wc:*, agent-core/bin/learning-ages.py:*), Task, Skill
user-invocable: true
---

# Skill: handoff

Update session.md for agent handoff, preserving critical context for the next agent. The handoff protocol ensures next agent has complete context without reading full conversation history.

## Target Model
Standard (Sonnet)

**CRITICAL:** This skill is for standard agent handoffs. If you are a Haiku orchestrator, use `/handoff-haiku` instead.

## Flags

- `--commit` — After completing handoff, tail-call `/commit` as the final action. Use when changes need committing after session handoff (e.g., post-planning workflows).

**Flag parsing:** Flags are exact tokens, not substrings. `/handoff --commit` has the flag. `/handoff describe the commit process` does NOT — that's prose guidance for handoff content. When in doubt, no flag was provided.

## Protocol

When invoked, immediately update `session.md` with:

### 1. Gather Context
- Review conversation to identify completed tasks
- Identify any pending/remaining tasks
- Note any blockers or gotchas discovered
- If reviewing an efficient-model handoff (handoff-haiku), process Session Notes for learnings
- **Check for uncommitted prior handoff:** Read `agents/session.md` from working tree. If it contains content from a prior handoff that hasn't been committed yet (look for handoff structure: `# Session Handoff: [Date]` header, Completed This Session section, or pending tasks not from this conversation), that content is authoritative base state that must be preserved in Step 2

### 2. Update session.md

Write a handoff note following the template structure. See **`references/template.md`** for complete template and formatting guidelines.

**Multiple handoffs before commit:** If Step 1 detected uncommitted prior handoff content in session.md, merge this conversation's work into the existing content rather than replacing it. Use Edit to update sections incrementally:
- Completed This Session: Append new completed work to existing categories or add new categories
- Pending Tasks: Add new tasks to list, update or remove tasks modified in this conversation
- Blockers/Gotchas: Append new blockers, update existing if resolved
- Next Steps: Replace with current next action

Do NOT Write a fresh session.md that discards the prior handoff's completed tasks, pending tasks, or blockers.

**Task naming:** Task names serve as prose key identifiers and must be unique across session.md and disjoint from learning keys in learnings.md. This enables `task-context.sh` to find the session.md where a task was introduced.

**Format:** `- [ ] **Task Name** — description | model | restart?`

**Field rules:**
- Task Name: Prose key serving as identifier (must be unique across session.md and disjoint from learning keys)
- Description: Brief description of the task
- Model: `haiku`, `sonnet`, or `opus` (default: sonnet if omitted)
- Restart: Optional flag — only include if restart needed (omit = no restart)

**Haiku task requirements:**

When scheduling implementation work for haiku, provide execution criteria — haiku cannot infer intent or verify alignment without explicit specification.

| Task type | Required | Example |
|-----------|----------|---------|
| Runbook execution | Plan reference | `Plan: statusline-parity` in nested line |
| Ad-hoc implementation | Acceptance criteria | Bullet list of specific outcomes |
| Script/tool enhancement | Test command or expected behavior | `Verify: just test passes` |

**Why:** Without criteria, haiku cannot verify alignment, vet cannot check drift, and quality issues surface only at commit time.

**Example (good):**
```markdown
- [ ] **Enhance prepare-runbook.py** — Add phase file assembly | haiku
  - Accept directory input, detect runbook-phase-*.md files
  - Sort by phase number, prepend TDD frontmatter
  - Verify: `prepare-runbook.py plans/statusline-parity/` succeeds
```

**Example (bad):**
```markdown
- [ ] **Enhance prepare-runbook.py** — Accept directory, detect phase files | haiku
```
The bad example has no acceptance criteria — haiku must guess at implementation details.

### 3. Context Preservation

**session.md allowed sections:**
- `## Completed This Session`
- `## Pending Tasks`
- `## Blockers / Gotchas`
- `## Reference Files`
- `## Next Steps`

**NEVER create other sections.** No "Learnings", "New Learnings", "Recent Learnings", or "Key Design Decisions". Learnings and design decisions go to `agents/learnings.md`. Session.md is work state only.

**Target: 75-150 lines**
- Below 75 lines: Likely missing important context
- 75-150 lines: Sweet spot for rich context without bloat
- Above 150 lines: Review if all details are necessary

**Preserve specifics that save time:**
- Commit hashes for traceability (e.g., "Fixed in a7f38c2")
- File paths for reference (e.g., "See plans/project/reports/analysis.md")
- Line numbers for precision (e.g., "Bug at lines 451-467")
- Metrics for context (e.g., "6/11 cycles affected, 55%")
- Root causes, not just symptoms (e.g., "WHY it failed")
- Failed approaches to avoid repeating (e.g., "Tried X, caused Y")

**Preserve decision context:**
- WHY decisions were made, not just WHAT
- Tradeoffs considered and rejected approaches
- Anti-patterns discovered during work
- Process improvements identified

**Omit verbose details:**
- Step-by-step execution logs (git history has this)
- Obvious outcomes (e.g., "tests passed")
- Intermediate debugging steps that led nowhere
- Repetitive information already in file references

**The goal: Complete context without bloat**
- Next agent should understand: what happened, why, what's next
- Next agent should NOT need to: search for files, re-discover root causes, repeat failed approaches

**NEVER reference commits as pending anywhere in session.md:**
- Not in Pending Tasks, Next Steps, Status line, or footer
- No "ready to commit", "pending commit", "commit changes" language
- When `--commit` flag is used, the tail-call makes commit atomic with handoff — write status assuming commit succeeds
- Obvious mechanical steps (restart, paste command) — only track substantive work

### 4. Write Learnings to Separate File

If the session has learnings, append them to `agents/learnings.md` (not session.md).

**Learning format:**

```markdown
## [Learning title]
- Anti-pattern: [what NOT to do]
- Correct pattern: [what TO do]
- Rationale: [why]

## [Another learning]
- Anti-pattern: [what NOT to do]
- Correct pattern: [what TO do]
- Rationale: [why]
```

**Note:** No blank line after `## Title` header.

**Design decisions are learnings.** When the session produced significant design decisions (architectural choices, trade-offs, anti-patterns discovered), write them to `agents/learnings.md` using the standard learning format. learnings.md is a staging area — `/remember` consolidates to permanent locations (fragments/, decisions/, skill references/).

**Learnings file is append-only:**
- Append new learnings to `agents/learnings.md` (do NOT overwrite)
- Never trim or remove learnings (separate from session.md lifecycle)
- Learnings accumulate across sessions as institutional knowledge
- When file reaches 80+ lines, note to user: "Learnings file at X/80 lines. Consider running /remember to consolidate."

### 4b. Check for Invalidated Learnings

**Trigger:** Session work modified enforcement (validators, scripts, precommit) or behavioral rules (fragments, skills, constraints).

**Action:** Review loaded `agents/learnings.md` context (already in memory via CLAUDE.md @-reference — no Read/Grep needed). If any learning claims something now false (e.g., "X not enforced" when enforcement was just added), remove that learning.

**Rationale:** Learnings load into every session. Stale learnings cause agents to act on false beliefs. Changes and learning cleanup must be atomic within the same commit.

### 4c. Consolidation Trigger Check

Run `agent-core/bin/learning-ages.py agents/learnings.md` to get age data.

**Trigger conditions (any one sufficient):**
- File exceeds 150 lines (size trigger)
- 14+ active days since last consolidation (staleness trigger)

**If triggered:**
1. Filter entries with age ≥ 7 active days
2. Check batch size ≥ 3 entries
3. If sufficient: delegate to remember-task agent with filtered entry list
4. Read report from returned filepath
5. If report contains escalations:
   - **Contradictions**: Note in handoff output under Blockers/Gotchas
   - **File limits**: Execute refactor flow (see below)

**Refactor flow (when file at 400-line limit):**

Handoff executes these steps after reading remember-task report with file-limit escalation:

1. Delegate to memory-refactor agent for the specific target file
2. Memory-refactor agent splits file, runs `validate-memory-index.py` autofix
3. Re-invoke remember-task with only the entries that were skipped due to file limit
4. Read second report
5. Check for remaining escalations (contradictions or additional file limits)

Note: This is handoff's perspective. Design D-6 describes the full 7-step flow including remember-task's internal steps (detect → skip → report).

**If not triggered or batch insufficient:**
- Skip consolidation (no action needed)
- Continue to step 5

**On error:**
- Catch exception during script execution or agent delegation
- Log error to stderr: `echo "Consolidation skipped: [error-message]" >&2`
- Note in handoff output: "Consolidation skipped: [brief-reason]"
- Continue to step 5 (consolidation failure must not block handoff per NFR-1)

### 5. Session Size Check and Advice

After updating session.md and learnings.md, check sizes and provide advice.

**Session size measurement:**
Count lines in both files:
```bash
wc -l agents/session.md agents/learnings.md
```

Session.md contains volatile state; learnings.md contains institutional knowledge.

### 6. Update jobs.md

When plan status changes during this session, update `agents/jobs.md`:

**Status transitions:**
- Plan completed → Move from current section to "Complete (Archived)"
- Design created → Move from Requirements to Designed
- Runbook created → Move from Designed to In Progress (planned)

**Format for Complete section:**
Add one-line entry: `- plan-name — brief description of what was delivered`

**Note:** jobs.md tracks plan lifecycle, session.md tracks task execution. They're complementary.

### 7. Trim Completed Tasks

**Rule:** Delete completed tasks only if BOTH conditions are true:
1. Completed before this conversation started (from previous conversation)
2. AND their work has been committed

**This prevents:**
- Deleting tasks completed in current conversation (even if just committed)
- Deleting uncommitted tasks from previous conversations

**Task-commit relationship is flexible:**
- One commit may contain multiple completed tasks
- One large task may span multiple commits

**Always keep:**
- Pending Tasks, Blockers, Next Steps

**Extract learnings first:** Before deleting, check if completed tasks contain patterns worth preserving. Append learnings to `agents/learnings.md`, never to session.md.

**Why this works:** Claude Code injects recent git log at session start. Completed tasks from previous conversations that are already committed are redundant.

**Do NOT list:**
- Create "Previous Session" headers
- Delete tasks completed in the current conversation
- Archive to separate files

### 8. Display STATUS (unless --commit)

**If `--commit` flag was NOT specified:**

Display STATUS following the format in `agent-core/fragments/execute-rule.md` (MODE 1: STATUS section).

**Key points:**
- Read session.md Pending Tasks, scan plans/ for job status
- Copy first pending task's command to clipboard (requires `dangerouslyDisableSandbox: true`)

**If `--commit` flag WAS specified:**

Skip STATUS display. The `/commit` skill will show it after committing.

## Principles

**session.md is for current work state, NOT persistent documentation**
- Focus on "what does the next agent need to know?"
- Include enough specifics to avoid re-work (commit hashes, file paths, root causes)
- Omit verbose execution logs (git history preserves everything)
- Balance: Complete context without bloat

**Learnings file is critical**
- Capture anti-patterns and correct patterns discovered
- Document process improvements and workflow insights
- Provide concrete examples for clarity
- Append learnings to `agents/learnings.md` (never overwrite, never trim)
- Learnings accumulate across sessions as institutional knowledge
- These learnings inform future work across projects

**Git history is the archive**
- No separate archive files needed
- Handoff preserves actionable context, not full history
- File references point to detailed content when needed

**session.md is working memory, learnings.md is semantic memory, git is archive**
- Completed tasks (session.md): Kept until committed AND conversation ends
- Learnings (learnings.md): Preserved across conversations, never trimmed
- Git log: Injected at conversation start, provides commit history

**Reviewing efficient-model handoffs**
- When following a handoff-haiku session, Session Notes contain raw observations
- Process Session Notes to extract learnings (anti-patterns, process improvements)
- Append validated learnings to `agents/learnings.md`
- Apply judgment that efficient model skipped

## Tail-Call: --commit Flag

**If `--commit` flag was provided:** As the **final action** of this skill, invoke `/commit` using the Skill tool.

This is a tail-call — handoff is complete, and `/commit` takes over. The commit skill will:
- Commit all staged/unstaged changes
- Display the next pending task from session.md

**If `--commit` flag was NOT provided:** Do not invoke `/commit`. End normally.

**Why tail-calls work:** Skills terminate when another skill is invoked. A tail-call (invoking a skill as the very last action) is safe because the current skill was done anyway. This enables skill composition without the mid-execution termination problem.

## Additional Resources

### Reference Files

For detailed protocols and templates:
- **`references/template.md`** - Session handoff template structure and formatting guidelines

### Example Files

- **`examples/good-handoff.md`** - Real-world example demonstrating best practices
