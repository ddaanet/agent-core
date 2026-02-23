---
name: doc-writing
description: This skill should be used when the user asks to "write a README", "rewrite the README", "update README", "write documentation", "rewrite documentation", "document this project", "write project docs", "docs are stale", "improve the README", or when creating, rewriting, or improving project-facing documentation (READMEs, guides, overviews). Covers exploration, drafting, reader testing with a fresh agent, gap fixing, and vet review.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(git:*), Task
user-invocable: true
---

# Write Project Documentation

Write project documentation through a structured cycle: explore the subject, draft with audience awareness, reader-test with a fresh agent, fix gaps, vet.

## When to Use

- Writing or rewriting a README
- Creating project guides or overviews
- Documenting a subsystem, library, or tool for external readers
- Any documentation that will be read by people without your current context

**Not for:** API reference docs (auto-generated), inline code comments, session handoffs, internal agent procedures.

## Process

### 1. Explore

Understand what you're documenting before writing anything.

**Codebase exploration:**
- Use Read, Glob, Grep to understand structure, components, key abstractions
- Read existing documentation to understand current state and gaps
- Identify the document's audience and their entry questions

**Style corpus (if available):**
- Check for style corpus at `tmp/STYLE_CORPUS.md` (conventional location, user may provide)
- The corpus is reference material — the model matches voice from examples without explicit style rules
- If no corpus exists, match the project's existing documentation voice

**Current doc audit (for rewrites):**
- What's accurate vs stale?
- What's missing entirely?
- What's present but serves no reader need?

**Output:** Understanding of subject, audience, and voice. Proceed to writing — no explore report needed.

### 2. Write

Draft the document applying these structural principles:

**Motivation-first opener.** Lead with the problem the project solves, not a feature list. Reader testing consistently shows feature-list openers leave readers unable to articulate why the project exists.

- Before: "agent-core is a framework providing skills, agents, fragments, and hooks for Claude Code"
- After: "Claude Code agents drift — inconsistent decisions, forgotten context, repeated mistakes. agent-core is a pipeline and memory layer that fixes this."
- The opener should make a reader who has the problem think "yes, that's my problem"

**Audience-appropriate depth.** Match detail level to who reads this:
- README: scanning developers evaluating whether to use this. Short sections, concrete examples, quick orientation.
- Guide: developers actively using this. Longer sections, complete examples, edge cases.
- Overview: mixed audience. Layer information — summary first, details after.

**Structure for scanning.** Most readers scan before reading:
- Front-load each section's key point in the first sentence
- Use headings as an outline that works standalone
- Keep sections short enough that scrolling reveals the next heading

**Concrete over abstract.** Show what things look like:
- Command examples with realistic output
- Configuration snippets that actually work
- File paths that exist in the project

**Omit what doesn't serve the reader:**
- No project structure trees unless the structure is the point
- No links to internal/agent documentation
- No implementation details unless they affect usage
- No badges, shields, or decoration

### 3. Reader-Test

Spawn a fresh Task agent with zero prior context. Feed it only the finished document. Ask 8-10 predicted reader questions.

**Implementation:** Use Task tool with:
- **description:** "Reader test: fresh-context evaluation of documentation"
- **prompt:** Include the full document text and 8-10 numbered questions. The agent must answer based ONLY on the document content. Format:

```
You are a developer encountering this project for the first time.
Read the following document, then answer each question based ONLY
on what the document tells you. If the document doesn't answer a
question, say "Not covered."

[full document text]

Questions:
1. What problem does this project solve?
2. How do I install it?
3. [audience-specific questions...]
```

**Question design:**
- Start with the universal questions (what, why, how to install, how to start)
- Add audience-specific questions (what are the key abstractions? how does X work?)
- Include at least one question about something you deliberately omitted — confirms the omission doesn't create a gap

**Interpreting results:**
- "Not covered" → gap in the document (fix in step 4)
- Wrong answer → document is misleading (fix in step 4)
- Correct answer → document communicates this successfully
- Hedged/uncertain answer → document is ambiguous (fix in step 4)

### 4. Fix Gaps

Address issues found by reader testing. Typical fixes:

- **Missing context:** Add a sentence or short section
- **Misleading phrasing:** Rewrite the ambiguous passage
- **Structural gap:** Reader couldn't find information that exists — reorganize or add a heading
- **Unnecessary detail surfaced:** Reader's wrong answer came from over-explaining an edge case — simplify

Re-run reader test only if fixes were substantial (>30% of document changed). Otherwise, proceed to vet.

### 5. Vet

Delegate to `corrector` for quality review. The review catches mechanical issues (broken paths, inconsistencies, formatting) that reader testing misses.

**Execution context for vet delegation:**
- **IN:** The documentation file written/rewritten
- **OUT:** Other project files not being documented — do NOT flag issues outside the document
- **Changed files:** The documentation file path
- **Requirements:** Accurate, complete for audience, matches project voice, no stale references, all paths/commands verified against actual project

## Constraints

- **Do not fabricate examples.** Every command, path, and code snippet must work against the actual project.
- **Do not document aspirational state.** Write about what exists now, not what's planned.
- **Style corpus is reference, not template.** Match voice and density, don't copy structure.
- **Reader test is mandatory.** Skip only for trivial updates (typo fixes, single-sentence additions).
- **One document per invocation.** Writing multiple documents in one pass produces shallow results.

## Example

**User:** "Write a README for agent-core"

**Agent:**

1. **Explore:** Use Glob to catalog agent-core components (skills, agents, fragments, hooks, scripts). Read existing README. Load style corpus from tmp/STYLE_CORPUS.md.

2. **Write:** Draft README with motivation opener ("Claude Code agents drift — inconsistent decisions, forgotten context, repeated mistakes. agent-core is a pipeline and memory layer that fixes this."). Document all component categories with counts. Include installation and configuration.

3. **Reader-test:** Spawn fresh agent with 10 questions. Agent correctly answers 7, flags 3 gaps: prerequisites unclear, memory file location not stated, skill vs agent distinction missing.

4. **Fix gaps:** Add prerequisites section, state memory file paths, add comparison sentence distinguishing skills from agents.

5. **Review:** Delegate to corrector. 2 minor fixes applied (expand inline list to table, fix relative path).

6. **Commit.**
