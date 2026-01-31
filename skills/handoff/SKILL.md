---
name: handoff
description: This skill should be used when the user asks to "handoff", "update session", "end session", or mentions switching agents. Updates session.md with completed tasks, pending work, blockers, and learnings for seamless agent continuation. NOT for Haiku model orchestrators - use /handoff-haiku instead.
---

# Skill: handoff

Update session.md for agent handoff, preserving critical context for the next agent. The handoff protocol ensures next agent has complete context without reading full conversation history.

## Target Model
Standard (Sonnet)

**CRITICAL:** This skill is for standard agent handoffs. If you are a Haiku orchestrator, use `/handoff-haiku` instead.

## Protocol

When invoked, immediately update `session.md` with:

### 1. Gather Context
- Review conversation to identify completed tasks
- Identify any pending/remaining tasks
- Note any blockers or gotchas discovered
- If reviewing an efficient-model handoff (handoff-haiku), process Session Notes for learnings

### 2. Update session.md

Write a handoff note following the template structure. See **`references/template.md`** for complete template and formatting guidelines.

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

### 4. Write Learnings to Separate File

If the session has learnings, append them to `agents/learnings.md` (not session.md).

**Learning format:**

```markdown
**[Learning title]:**
- Anti-pattern: [what NOT to do]
- Correct pattern: [what TO do]
- Rationale: [why]

**[Another learning]:**
- Anti-pattern: [what NOT to do]
- Correct pattern: [what TO do]
- Rationale: [why]
```

**Design decisions are learnings.** When the session produced significant design decisions (architectural choices, trade-offs, anti-patterns discovered), write them to `agents/learnings.md` using the standard learning format. learnings.md is a staging area — `/remember` consolidates to permanent locations (fragments/, decisions/, skill references/).

**Learnings file is append-only:**
- Append new learnings to `agents/learnings.md` (do NOT overwrite)
- Never trim or remove learnings (separate from session.md lifecycle)
- Learnings accumulate across sessions as institutional knowledge
- When file reaches 80+ lines, note to user: "Learnings file at X/80 lines. Consider running /remember to consolidate."

### 5. Session Size Check and Advice

After updating session.md and learnings.md, check sizes and provide advice.

**Session size measurement:**
Count lines in both files:
```bash
wc -l agents/session.md agents/learnings.md
```

Session.md contains volatile state; learnings.md contains institutional knowledge.

**If session size >150 lines after trimming OR all workflow tasks complete:**
```
"Session handoff complete.

[If still >150 lines after trimming:]
session.md is [X] lines (threshold: 150) after trimming completed tasks.
Review pending tasks and learnings for further reduction.

[If workflow complete:]
All workflow tasks complete. Start fresh session for new work.

[If next task needs different model:]
Next task ([task name]) requires [model name]. Switch model when starting new session."
```

**If next pending task needs different model:**
- Design stage → Suggest Opus
- Execution stage → Suggest Haiku
- Planning/Review/Completion → Suggest Sonnet

Example: "Next task: Design stage. Switch to Opus model for architectural work."

### 6. Trim Completed Tasks

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
- Create "commit this" or "commit changes" as a pending task (commits don't update session.md to mark done)

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

## Additional Resources

### Reference Files

For detailed protocols and templates:
- **`references/template.md`** - Session handoff template structure and formatting guidelines

### Example Files

- **`examples/good-handoff.md`** - Real-world example demonstrating best practices
