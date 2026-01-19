---
description: Update agent documentation and rules
allowed-tools: Read, Write, Edit, Bash(git:*)
user-invocable: true
---

# Remember Skill

Maintain and evolve agent documentation based on session learnings, workflow improvements, and discovered constraints. This skill updates CLAUDE.md, context files, and related documentation to capture rules and patterns.

**Purpose:** Transform learnings into persistent, actionable documentation

## When to Use

**Use this skill when:**
- After discovering a workflow improvement
- After identifying a missing constraint or rule
- After resolving a compliance failure
- When user explicitly requests documentation updates (via `#remember` or directly)
- After completing work that reveals new patterns

**Do NOT use when:**
- Update is trivial (fix typo directly)
- No learnings to capture
- Change is temporary or experiment

## Update Process

### 1. Understand the Learning

**Gather context:**
- What was the problem or gap?
- What solution or rule addresses it?
- Why is this important to remember?
- What category does it belong to?

**Read current state:**
- Read `agents/context.md` for current project state
- Read `CLAUDE.md` for existing rules
- Read `agents/design-decisions.md` for architectural patterns (if exists)

### 2. Determine Update Location

**File selection:**

**CLAUDE.md** - Core agent instructions
- Communication rules
- Error handling principles
- Session management
- Delegation patterns
- Tool usage constraints
- Project structure rules
- Hashtag conventions

**agents/context.md** - Current work context
- Active tasks and decisions
- Session handoff information
- Temporary state
- Current blockers

**agents/design-decisions.md** - Architectural patterns
- Technology choices with rationale
- Design patterns used in project
- Trade-offs and constraints
- Long-term architectural decisions

**Other files:**
- Skill files (`.claude/skills/*/skill.md`) - Skill-specific updates
- Agent files (`.claude/agents/*.md`) - Agent-specific updates
- Plan files - Only if updating historical record

**Do NOT update:**
- `README.md` - User-facing documentation
- Test files - Implementation artifacts
- Temporary plan/scratch files

### 3. Draft the Update

**Follow principles:**

**Precision over brevity:**
- Rules must be unambiguous
- Clear boundary conditions
- Specific, not vague

**Examples over abstractions:**
- Show concrete examples
- Use actual file paths
- Demonstrate the pattern

**Constraints over guidelines:**
- "Do not X" beats "try to avoid X"
- "Always Y" beats "consider Y"
- "Must Z" beats "should Z"

**Atomic changes:**
- One concept per update
- Self-contained
- Clear intent

**Measured data over estimates:**
- Report only measured results
- Avoid predictions unless explicitly required

**Update formats:**

**Adding a new rule:**
```markdown
## [Section Name]

### [Rule Name]

**[Rule statement in imperative or declarative form]**

[Supporting explanation if needed]

**Example:**
[Concrete example demonstrating the rule]
```

**Adding to existing section:**
- Maintain section structure
- Add to appropriate subsection
- Keep related rules together

**Updating existing rule:**
- Preserve intent if possible
- Note what changed and why
- Keep history if significant

### 4. Apply the Update

**Use appropriate tool:**

**Edit tool:**
- For modifying existing content
- Preserves structure
- Clear before/after

**Write tool:**
- Only for new files
- Requires prior Read if file exists

**Verification:**
- Read updated section to confirm
- Check formatting
- Verify placement

### 5. Document the Change

**Commit message:**

If committing after update:
```
Update [file]: [what changed]

- [Specific change 1]
- [Specific change 2]
- [Rationale if not obvious]
```

**Handoff note:**

If updating context.md:
- Note the update in session handoff
- Explain significance
- Reference commit if applicable

## Rule Tiering

Structure documentation with critical rules prominent, optional guidance secondary.

**Placement strategy:**

**Tier 1 (~20%, top of section):**
- Violations cause immediate problems
- Non-negotiable rules
- Critical constraints
- Few in number, maximum impact

**Tier 2 (~60%, middle of section):**
- Important for quality
- Standard practices
- Most rules live here
- Regularly referenced

**Tier 3 (~20%, bottom of section):**
- Nice-to-have
- Edge cases
- Style preferences
- Optional guidance

**Rationale:** Recency bias means later content gets less attention. Place must-follow rules early where they won't be forgotten.

## Rule Budgeting

**Target:** CLAUDE.md ~40-60 rules total. Fewer is better.

**Brevity:** Strong models don't need verbose explanations. One clear sentence beats a paragraph of explanation.

**When adding rules:**
- Is this rule necessary?
- Can it be combined with existing rule?
- Is it specific enough to be actionable?
- Will agents actually follow it?

**When removing rules:**
- Made obsolete by project evolution?
- Never gets violated (too obvious)?
- Redundant with another rule?
- Too vague to be useful?

## Maintenance Heuristics

**Promote rules:**
- After repeated violations
- When impacts are severe
- When learning curve is steep

**Demote rules:**
- Apply only to edge cases
- Never get violated
- Obvious to strong models

**Delete rules:**
- Made obsolete by changes
- Redundant with other rules
- Never referenced

**Refine rules:**
- Too vague → Add concrete examples
- Too specific → Generalize pattern
- Too long → Distill to essence
- Too abstract → Show application

## Critical Constraints

**Tool Usage:**
- Use **Read** to check current documentation
- Use **Edit** to modify existing files (preferred)
- Use **Write** only for new files
- Use **Bash** for git operations if committing

**Scope:**
- Update only what's needed
- Don't reorganize unnecessarily
- Preserve existing structure
- Keep diffs minimal

**Validation:**
- Read updated section to confirm
- Check for formatting issues
- Verify rule is actionable
- Ensure examples are concrete

**Tone:**
- Imperative for rules ("Do X", "Never Y")
- Clear and direct
- No hedging or weasel words
- Specific, not vague

## Example Execution

**User:** `/remember` or "#remember always use ~/code/claudeutils/agent-core/"

**Agent:** "I'll update CLAUDE.md with this rule.

Reading current documentation...
*Reads CLAUDE.md*

This is a project structure rule. I'll add it to the Project Structure section.

*Uses Edit to add the rule*

Updated CLAUDE.md with agent-core path rule:

```markdown
### agent-core Path Rule

**CRITICAL:** Always make changes in `~/code/claudeutils/agent-core/`, NOT `~/code/agent-core/`

- `~/code/agent-core/` is a separate git repository (submodule source)
- `~/code/claudeutils/agent-core/` is the local working copy within this project
- All development work must happen in the claudeutils copy
- Never modify files in `~/code/agent-core/` directly
```

Rule added to CLAUDE.md:37-46. The rule is now part of project instructions for all future sessions.

Should I commit this change?"

## Common Patterns

**Pattern: Adding error handling rule after failure**
```
1. Read CLAUDE.md Error Handling section
2. Add specific constraint about the error
3. Include example of correct handling
4. Commit with message explaining the failure that prompted it
```

**Pattern: Documenting workflow improvement**
```
1. Read CLAUDE.md and relevant section
2. Add or update workflow description
3. Include before/after if significant change
4. Update agents/context.md if affects current work
```

**Pattern: Capturing design decision**
```
1. Check if agents/design-decisions.md exists
2. If not, consider creating it
3. Add decision with problem, options, choice, rationale
4. Reference from CLAUDE.md if it affects rules
```

**Pattern: Removing obsolete rule**
```
1. Verify rule is truly obsolete
2. Check if any other rules depend on it
3. Remove using Edit tool
4. Commit with message explaining why obsolete
```

## Integration with Oneshot Workflow

**Typical invocations:**
- During work: User discovers pattern, says "#remember [rule]"
- After completion: User wants to capture learnings
- After failure: System needs constraint to prevent recurrence

**Related skills:**
- `/vet` - May identify patterns worth remembering
- `/design` - Design decisions may become remembered rules
- `/commit` - Often commit after remember update

## References

**Target files:**
- `/Users/david/code/claudeutils/CLAUDE.md` - Core instructions
- `/Users/david/code/claudeutils/agents/context.md` - Current state
- `/Users/david/code/claudeutils/agents/design-decisions.md` - Architecture (if exists)

**Historical reference:**
- `agents/role-remember.md` (git history: 56929e2^) - Original remember role
