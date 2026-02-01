# RCA Report Template

Use this template for Exit Path 2 (RCA Complete, Handoff for Fixes) when creating RCA reports in `plans/reflect-rca-<slug>/rca.md`.

---

# Root Cause Analysis: [Deviation Description]

**Session:** [Date or session identifier]
**Model:** [haiku / sonnet / opus]
**Context:** [Brief description of what agent was doing when deviation occurred]

---

## Deviation Summary

**Observed Behavior:**
[What the agent actually did]

**Expected Behavior:**
[What the agent should have done according to rules]

**Violated Rule:**
- **Rule name:** [Name or identifier]
- **Location:** `[file path]`, section "[section name]"
- **Directive:** "[Quoted text of violated rule]"

**Message Location:**
[Turn number, timestamp, or contextual marker where deviation occurred]

---

## Root Cause Analysis

### Proximal Cause

[What directly caused the deviation to occur]

**Evidence:**
- [Specific message or decision point]
- [Relevant context or loaded directives]
- [Agent reasoning if visible]

### Contributing Factors

[What made the deviation plausible or likely]

**Factor 1:** [Description]
**Factor 2:** [Description]
**Factor 3:** [Description]

### Rule Gap Analysis

**Is the rule ambiguous?**
[Yes/No — explain if yes]

**Is the rule missing?**
[Yes/No — explain if yes]

**Is the rule contradicted elsewhere?**
[Yes/No — identify contradictions if yes]

**Is the rule clear but ignored?**
[Yes/No — behavioral rationalization if yes]

---

## Classification

**Primary Classification:** [Rule fix / Input fix / Behavioral / Systemic]

**Secondary Classifications:** [If applicable]

**Justification:**
[Why this classification applies]

---

## Recommended Fixes

### Immediate Fixes

**Fix 1:**
- **Type:** [Rule edit / Input correction / Language strengthening]
- **File:** `[path]`
- **Change:** [Specific edit description]
- **Priority:** [Critical / Major / Minor]

**Fix 2:**
- **Type:** [Description]
- **File:** `[path]`
- **Change:** [Specific edit description]
- **Priority:** [Critical / Major / Minor]

### Systemic Fixes (If Applicable)

**Fragment Creation:**
- **Proposed file:** `agent-core/fragments/[name].md`
- **Purpose:** [What pattern this addresses]
- **Scope:** [When this fragment should be loaded]

**Hook Creation:**
- **Proposed hook:** [PreToolUse / PostToolUse / UserPromptSubmit]
- **Purpose:** [What this hook prevents]
- **Trigger:** [What condition activates this hook]

**Memory Index Entry:**
- **Entry text:** [Proposed one-line entry with file reference]
- **Section:** [Behavioral Rules / Workflow Patterns / Technical Decisions / Tool & Infrastructure]

---

## Pattern Analysis

**Has this pattern occurred before?**
[Yes/No]

**If yes, previous occurrences:**
- [Reference to learnings.md entry, git commit, or session.md]
- [Reference to related RCA if exists]

**Is this systemic?**
[Yes/No — explain if yes]

**Recurrence risk:**
[Low / Medium / High]

**Mitigation strategy:**
[How to prevent recurrence]

---

## Learning

**Anti-pattern:**
[What NOT to do — specific behavior to avoid]

**Correct pattern:**
[What to do instead — specific behavior to follow]

**Rationale:**
[Why the correct pattern matters — consequences of anti-pattern]

**Example (if applicable):**
```
[Concrete example demonstrating correct pattern]
```

---

## Implementation Notes

**Context budget status:** [Exhausted / Tight / Available]

**Fix complexity:** [Simple / Moderate / Complex]

**Coordination needed:** [None / Multiple files / Cross-system]

**Estimated effort:** [Minutes / Hours / Session]

**Recommended approach:**
[Direct implementation / Lightweight delegation / Full runbook]

---

## Pending Tasks

**Task 1: [Description]**
- **Command:** `[command to start if applicable]`
- **Model:** [haiku / sonnet / opus]
- **Restart needed:** [yes / no]
- **Priority:** [Critical / Major / Minor]

**Task 2: [Description]**
- **Command:** `[command to start if applicable]`
- **Model:** [haiku / sonnet / opus]
- **Restart needed:** [yes / no]
- **Priority:** [Critical / Major / Minor]

---

## References

**Violated rule location:**
`[full path to file containing violated rule]`

**Related documentation:**
- `[path to related fragment/skill/decision doc]`
- `[path to related fragment/skill/decision doc]`

**Relevant learnings:**
- `agents/learnings.md` - [line reference if specific entry exists]
- `agents/memory-index.md` - [related entry if exists]

**Prior RCA reports (if applicable):**
- `plans/reflect-rca-[slug]/rca.md` - [related deviation]

---

## Metadata

**RCA performed by:** [opus / sonnet]
**Date:** [YYYY-MM-DD]
**Duration:** [Approximate time spent on RCA]
**Status:** [Complete / Partial - pending upstream fix]

---

## Notes

[Additional observations, edge cases, or context that doesn't fit above sections]
