---
name: handoff
description: This skill should be used when the user asks to "handoff", "update session", "end session", or mentions switching agents. Updates session.md with completed tasks, pending work, blockers, and learnings for seamless agent continuation.
---

# Skill: handoff

Update session.md for agent handoff, preserving critical context for the next agent. The handoff protocol ensures next agent has complete context without reading full conversation history.

## Target Model
Standard (Sonnet)

## Protocol

When invoked, immediately update `session.md` with:

### 1. Gather Context
- Review conversation to identify completed tasks
- Identify any pending/remaining tasks
- Note any blockers or gotchas discovered
- If reviewing an efficient-model handoff (handoff-lite), process Session Notes for learnings

### 2. Update session.md

Write a handoff note following the template structure. See **`references/template.md`** for complete template and formatting guidelines.

### 3. Context Preservation

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

### 4. Include Recent Learnings

If the session has learnings, include them in the "Recent Learnings" section of session.md.

**Learning format:**

```markdown
## Recent Learnings

**[Learning title]:**
- Anti-pattern: [what NOT to do]
- Correct pattern: [what TO do]
- Rationale: [why]

**[Another learning]:**
- Anti-pattern: [what NOT to do]
- Correct pattern: [what TO do]
- Rationale: [why]
```

**Keep learnings inline:**
- Write learnings directly in session.md for easy editing
- All learnings stay in session.md (no separate files)
- Inline format makes it simple to add, update, or refine learnings
- Next agent can easily modify learnings without script complexity

### 5. Session Size Check and Advice

After updating session.md, check size and provide advice.

**Session size measurement:**
Count lines in session.md only:
```bash
wc -l agents/session.md
```

Recent learnings are included inline, making session.md self-contained.

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
- Recent Learnings

**Extract learnings first:** Before deleting, check if completed tasks contain patterns worth preserving as learnings.

**Why this works:** Claude Code injects recent git log at session start. Completed tasks from previous conversations that are already committed are redundant.

**Do NOT:**
- Create "Previous Session" headers
- Delete tasks completed in the current conversation
- Archive to separate files

## Principles

**session.md is for current work state, NOT persistent documentation**
- Focus on "what does the next agent need to know?"
- Include enough specifics to avoid re-work (commit hashes, file paths, root causes)
- Omit verbose execution logs (git history preserves everything)
- Balance: Complete context without bloat

**Recent Learnings section is critical**
- Capture anti-patterns and correct patterns discovered
- Document process improvements and workflow insights
- Provide concrete examples for clarity
- Write learnings inline for easy editing and updating
- All learnings stay in session.md (self-contained)
- These learnings inform future work across projects

**Git history is the archive**
- No separate archive files needed
- Handoff preserves actionable context, not full history
- File references point to detailed content when needed

**session.md is working memory, git is archive**
- Completed tasks: Kept until committed AND conversation ends
- Learnings: Preserved across conversations (semantic memory)
- Git log: Injected at conversation start, provides commit history

**Reviewing efficient-model handoffs**
- When following a handoff-lite session, Session Notes contain raw observations
- Process Session Notes to extract learnings (anti-patterns, process improvements)
- Move validated learnings to Recent Learnings section
- Apply judgment that efficient model skipped

## Additional Resources

### Reference Files

For detailed protocols and templates:
- **`references/template.md`** - Session handoff template structure and formatting guidelines

### Example Files

- **`examples/good-handoff.md`** - Real-world example demonstrating best practices
