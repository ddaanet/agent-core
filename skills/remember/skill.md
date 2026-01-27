---
name: remember
description: This skill should be used when the user asks to "remember this", "update rules", "add to documentation", "consolidate learnings", "#remember", or when workflow improvements are discovered. Processes pending learnings from session handoffs and updates CLAUDE.md, skill references, and documentation with rules and patterns.
allowed-tools: Read, Write, Edit, Bash(git:*), Glob
user-invocable: true
---

# Remember Skill

Transform session learnings into persistent, actionable documentation. Updates CLAUDE.md, context files, and related docs to capture rules and patterns.

## When to Use

**Use when:** Workflow improvement discovered • Missing constraint identified • Compliance failure resolved • User requests update (#remember) • Completed work reveals patterns

**Skip when:** Trivial update (fix directly) • No learnings • Temporary/experimental change

## Execution Protocol

### 0. Check for Pending Learnings (Optional)

If `agents/learnings/pending.md` exists and contains @ references:

**Process each learning:**
1. Read the learning file content
2. Infer target skill from keywords:
   - Handoff/session → handoff skill
   - Planning/runbook → plan-adhoc/plan-tdd skills
   - Commit/git → commit skill
   - Tool usage/sandbox → relevant tool skills
3. If target unclear, ask user: "Where should this learning be consolidated? [skill names]"
4. Append learning to `.claude/skills/{skill}/references/learnings.md` (create if needed)
5. Remove @ reference from `pending.md`
6. Delete processed learning file
7. Commit: "Consolidate learning: [title] to {skill} skill"

**If no pending learnings:** Proceed to step 1.

### 1. Understand Learning
- Problem/gap? Solution/rule? Why important? Category?
- Read: `agents/decisions/*.md` (relevant domain doc, if exists)

### 2. File Selection

**CLAUDE.md**: Cross-cutting rules • Communication • Error handling • Session mgmt • Delegation • Bash scripting • Tool usage
**agents/session.md**: Active tasks/decisions • Handoff info • Temporary state • Blockers
**agents/decisions/cli.md**: CLI patterns • Output formats • Entry points
**agents/decisions/testing.md**: Test organization • Mock patterns • TDD approach
**agents/decisions/workflows.md**: Oneshot workflow • TDD workflow • Runbook patterns • Handoff patterns
**agents/decisions/architecture.md**: Module structure • Path handling • Data models • Code quality • Rule files • Model terminology
**Skill references**: `.claude/skills/*/references/learnings.md` • Domain-specific patterns (progressive disclosure)
**Other**: `.claude/agents/*.md` • Plan files (historical only)
**Never**: `README.md` • Test files • Temp files

**For detailed routing guidance**, see `references/consolidation-patterns.md`

### 3. Draft Update

**Principles:**
- Precision over brevity (unambiguous, clear boundaries)
- Examples over abstractions (concrete, actual paths)
- Constraints over guidelines ("Do not" > "avoid", "Always" > "consider", "Must" > "should")
- Atomic changes (one concept, self-contained)
- Measured data over estimates

**Format:**
```markdown
### [Rule Name]
**[Imperative/declarative statement]**
[Supporting explanation if needed]
**Example:** [Concrete demonstration]
```

### 4. Apply + Verify
- **Edit** for modifications • **Write** for new files only (Read first if exists)
- Read updated section → Check formatting → Verify placement

### 5. Document
**Commit**: `Update [file]: [what]\n\n- [change 1]\n- [change 2]\n- [rationale]`
**Handoff** (if session.md): Note update, explain significance, reference commit

## Rule Management

For guidance on tiering, budgeting, and maintaining rules in CLAUDE.md, see **`references/rule-management.md`**.

## Tool Constraints
- **Read** current docs • **Edit** existing (preferred) • **Write** new only • **Bash** git ops
- Minimal scope/diffs • Preserve structure • Verify actionable+concrete • Imperative tone

## Common Patterns

For detailed usage patterns (error handling, workflow improvement, design decisions, pending learnings), see **`examples/remember-patterns.md`**.

## Integration
**Invocations**: During work (#remember [rule]) • After completion (capture learnings) • After failure (prevent recurrence)
**Related**: `/vet` (may ID patterns) • `/design` (decisions→rules) • `/commit` (often follows remember)

## Additional Resources

### Reference Files

For detailed guidance:
- **`references/rule-management.md`** - Tiering, budgeting, and maintenance strategies for CLAUDE.md rules
- **`references/consolidation-patterns.md`** - Routing learnings to appropriate documentation, progressive disclosure, anti-patterns

### Example Files

Working patterns for common scenarios:
- **`examples/remember-patterns.md`** - Error handling, workflow improvements, design decisions, pending learnings consolidation

### Target Files

**Primary targets**: `/Users/david/code/claudeutils/CLAUDE.md` • `agents/session.md` • `agents/design-decisions.md`
**Historical**: `agents/role-remember.md` (git: 56929e2^)
