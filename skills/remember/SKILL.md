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

### 1. Understand Learning
- Problem/gap? Solution/rule? Why important? Category?
- Read: `agents/learnings.md` for recent learnings to consolidate
- Read: `agents/decisions/*.md` (relevant domain doc, if exists)

### 2. File Selection

**Behavioral rules** → `agent-core/fragments/*.md`: Workflow patterns • Anti-patterns • Directive conflicts • Agent behavior
**Technical details** → `agents/decisions/*.md`: Architecture • Implementation patterns • Technology choices (consult `agents/decisions/README.md` for domain → file routing)
**Implementation patterns** → `agents/decisions/implementation-notes.md`: Mock patterns • Python quirks • API details
**agents/session.md**: Active tasks/decisions • Handoff info • Temporary state • Blockers
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
- **After consolidation**: Remove consolidated learnings from `agents/learnings.md`, but keep the 3-5 most recent learnings (at bottom of file) for continuity

**Step 4a: Update discovery mechanisms**

After consolidating a learning:

1. **Append to memory index**: Generate `/when` or `/how` entry in `agents/memory-index.md`:
   - **Trigger naming**:
     - Plain prose, no hyphens or special characters
     - 2-5 words typical
     - Optimize for discovery: what would agent type when facing this problem?
     - Use key compression tool (`agent-core/bin/compress-key.py`) to verify uniqueness
   - **Operator selection**:
     - `/when` for behavioral knowledge (when to do X, when X applies)
     - `/how` for procedural knowledge (how to do X, technique for X)
2. **If new fragment created**: Add `@`-reference to CLAUDE.md OR create `.claude/rules/` entry if path-scoped. **Heuristic:** If the learning applies regardless of which files are being edited → `@`-ref in CLAUDE.md. If it only applies when working with a specific file type or directory → `.claude/rules/` entry with path frontmatter.
3. **If existing fragment updated**: Ensure memory index entry reflects the updated content (add new entry or update existing one)
4. **If decision file updated**: Verify corresponding `.claude/rules/` entry exists for path trigger

### Learnings Quality Criteria

**Principle-level (consolidate):** ✅
- States a general constraint or pattern
- Applies beyond the specific incident
- Example: "Always load skill context before editing"

**Incident-specific (reject/revise):** ❌
- Describes what happened, not what to do
- Narrow to one case, not generalizable
- Example: "Edited skill without loading it" → revise to principle

**Meta-learnings (use sparingly):**
- Rules about rules — only when behavioral constraint required
- Example: "Soft limits normalize deviance" → consolidate if recurrent

### Staging Retention Guidance

**Keep in staging (do not consolidate):**
- Entries < 7 active days old (insufficient validation)
- Entries with pending cross-references (depend on other work)
- Entries under active investigation

**Consolidate:**
- Entries ≥ 7 active days with proven validity
- Entries that have been applied consistently
- Entries referenced by multiple sessions

**Drop (remove from staging):**
- Superseded by newer entry on same topic
- Contradicted by subsequent work
- Incident-specific without generalizable principle

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

**Primary targets**: Project's `CLAUDE.md` • `agents/session.md` • Domain-specific files per routing config
**Historical**: `agents/role-remember.md` (git: 56929e2^)
