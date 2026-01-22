---
description: Update agent documentation and rules
allowed-tools: Read, Write, Edit, Bash(git:*)
user-invocable: true
---

# Remember Skill

Transform session learnings into persistent, actionable documentation. Updates CLAUDE.md, context files, and related docs to capture rules and patterns.

## When to Use

**Use when:** Workflow improvement discovered • Missing constraint identified • Compliance failure resolved • User requests update (#remember) • Completed work reveals patterns

**Skip when:** Trivial update (fix directly) • No learnings • Temporary/experimental change

## Execution Protocol

### 1. Understand Learning
- Problem/gap? Solution/rule? Why important? Category?
- Read: `agents/context.md` (state) • `CLAUDE.md` (rules) • `agents/design-decisions.md` (architecture, if exists)

### 2. File Selection

**CLAUDE.md**: Communication rules • Error handling • Session mgmt • Delegation • Tool usage • Project structure • Hashtags
**agents/context.md**: Active tasks/decisions • Handoff info • Temporary state • Blockers
**agents/design-decisions.md**: Tech choices+rationale • Design patterns • Tradeoffs • Long-term architecture
**Other**: `.claude/skills/*/skill.md` • `.claude/agents/*.md` • Plan files (historical only)
**Never**: `README.md` • Test files • Temp files

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
**Handoff** (if context.md): Note update, explain significance, reference commit

## Rule Management

### Tiering (Critical First)
**Tier 1** (~20%, top): Violations cause immediate problems • Non-negotiable • Critical constraints
**Tier 2** (~60%, middle): Quality-important • Standard practices • Regular reference
**Tier 3** (~20%, bottom): Nice-to-have • Edge cases • Style • Optional guidance

**Rationale**: Recency bias → place must-follow rules early

### Budgeting
**Target**: CLAUDE.md ~40-60 rules. Fewer better. Strong models → terse explanations.

**Add if**: Necessary? Can't combine? Specific/actionable? Will agents follow?
**Remove if**: Obsolete? Never violated? Redundant? Too vague?

### Maintenance
**Promote**: Repeated violations • Severe impacts • Steep learning curve
**Demote**: Edge cases only • Never violated • Obvious to strong models
**Delete**: Obsolete • Redundant • Never referenced
**Refine**: Vague→examples • Specific→generalize • Long→distill • Abstract→application

## Tool Constraints
- **Read** current docs • **Edit** existing (preferred) • **Write** new only • **Bash** git ops
- Minimal scope/diffs • Preserve structure • Verify actionable+concrete • Imperative tone

## Patterns

**Error handling after failure**: Read section → Add constraint+example → Commit w/failure context
**Workflow improvement**: Read section → Add/update description → Before/after if major → Update context.md if affects current
**Design decision**: Check design-decisions.md exists → Create if needed → Add problem/options/choice/rationale → Reference from CLAUDE.md if affects rules
**Remove obsolete**: Verify obsolete → Check dependencies → Edit remove → Commit w/reason

## Integration
**Invocations**: During work (#remember [rule]) • After completion (capture learnings) • After failure (prevent recurrence)
**Related**: `/vet` (may ID patterns) • `/design` (decisions→rules) • `/commit` (often follows remember)

## References
**Targets**: `/Users/david/code/claudeutils/CLAUDE.md` • `agents/context.md` • `agents/design-decisions.md`
**Historical**: `agents/role-remember.md` (git: 56929e2^)
