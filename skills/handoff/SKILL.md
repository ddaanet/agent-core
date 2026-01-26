---
name: handoff
description: This skill should be used when the user asks to "handoff", "update session", "end session", "prepare for next agent", "finish up", or mentions switching agents or completing work. Updates session.md with completed tasks, pending work, blockers, learnings, and next steps for seamless agent continuation.
---

# Skill: handoff

Update session.md for agent handoff, preserving critical context for the next agent. The handoff protocol ensures next agent has complete context without reading full conversation history.

## Target Model
Haiku (simple file update)

## Protocol

When invoked, immediately update `session.md` with:

### 1. Gather Context
- Review conversation to identify completed tasks
- Identify any pending/remaining tasks
- Note any blockers or gotchas discovered

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

### 4. Process Learnings to Staging Area

If the session has learnings in the "Recent Learnings" section, stage them using add-learning.py. See **`references/learnings-staging.md`** for complete staging protocol and examples.

### 5. Session Size Check and Advice

After updating session.md, check size and provide advice:

**If session.md >150 lines OR all workflow tasks complete:**
```
"Session handoff complete.

Recommendation: Consider clearing session (new chat) before continuing.
Current session size: [X] lines (threshold: 150)

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
- These learnings inform future work across projects

**Git history is the archive**
- No separate archive files needed
- Handoff preserves actionable context, not full history
- File references point to detailed content when needed

## Additional Resources

### Reference Files

For detailed protocols and templates:
- **`references/template.md`** - Session handoff template structure and formatting guidelines
- **`references/learnings-staging.md`** - Learnings staging protocol with add-learning.py script usage

### Example Files

- **`examples/good-handoff.md`** - Real-world example demonstrating best practices
