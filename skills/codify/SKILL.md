---
name: codify
description: This skill should be used when consolidating learnings into permanent documentation, updating rules or decision files, or when learnings.md approaches its soft limit. Transforms session learnings into persistent CLAUDE.md fragments, decision files, and skill references.
allowed-tools: Read, Write, Edit, Bash(git:*), Glob
user-invocable: true
---

# Codify Learnings into Permanent Docs

Transform session learnings into persistent, actionable documentation. Updates CLAUDE.md, context files, and related docs to capture rules and patterns.

**Prerequisite:** Execute in a clean session (fresh start). Runs inline — no delegation to sub-agents.

## Execution Protocol

### 1. Assess Learnings
- Run `agent-core/bin/learning-ages.py` to get the ages report
- Entries ≥7 active days → eligible for consolidation
- Entries <7 active days → keep in staging (do not consolidate)
- Read the eligible entries in `agents/learnings.md` for context
- Read: `agents/decisions/*.md` (relevant domain doc, if exists)

### 2. File Selection

For each eligible learning, search candidate target files for related headings:
```bash
Grep pattern="<keyword from learning>" path="agent-core/fragments/" glob="*.md"
Grep pattern="<keyword from learning>" path="agents/decisions/" glob="*.md"
```

Use Grep results to ground routing — match the learning to the file that already contains related content.

**Behavioral rules** → `agent-core/fragments/*.md`: Workflow patterns • Anti-patterns • Directive conflicts • Agent behavior
**Technical details** → `agents/decisions/*.md`: Architecture • Implementation patterns • Technology choices (consult `agents/decisions/README.md` for domain → file routing)
**Implementation patterns** → `agents/decisions/implementation-notes.md`: Mock patterns • Python quirks • API details
**agents/session.md**: Active tasks/decisions • Handoff info • Temporary state • Blockers
**Skill references**: `.claude/skills/*/references/learnings.md` • Domain-specific patterns (progressive disclosure)
**Agent templates** → `agent-core/agents/*.md`: Execution patterns • Tool usage • Error handling • Domain-specific guidance. Route when learning is actionable for a specific agent role (execution pattern, stop condition, tool preference, error handling heuristic). Eligible agents: artisan, brainstorm-name, corrector, design-corrector, hooks-tester, outline-corrector, refactor, runbook-corrector, runbook-outline-corrector, runbook-simplifier, scout, tdd-auditor, test-driver. Exclude plan-specific agents (generated per-runbook by prepare-runbook.py)
**Other**: Plan files (historical only)
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
- **File splitting (if needed):** After Write/Edit to a decision file, check `wc -l`. If >400 lines, split by H2/H3 boundaries into 100-300 line sections. Run `agent-core/bin/validate-memory-index.py --fix` after split

**Step 4a: Update discovery mechanisms**

After consolidating a learning:

1. **Append to memory index**: Generate `/when` or `/how` entry in `agents/memory-index.md`:
   - **Trigger derivation** (mechanical — no rephrasing):
     - `## When X Y Z` → `/when x y z`
     - `## How to X Y` → `/how x y`
     - Title IS the trigger. Lowercase, preserve all words after operator prefix
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

### Title Format Requirements

Titles must follow the validation rules enforced by precommit:

- **Prefix required:** Start with `When ` or `How to `
- **Min 2 content words after prefix:** `## When choosing review gate` (2 content words — pass). `## When testing` (1 content word — fail)

**Anti-pattern examples:**
- `## transformation table` → missing prefix, jargon title
- `## When testing` → prefix OK, but only 1 content word
- `## How encode` → must be `How to`, not bare `How`

**Correct pattern examples:**
- `## When choosing review gate` — situation at decision point
- `## How to encode file paths` — procedural knowledge
- `## When haiku rationalizes test failures` — specific behavioral pattern

Titles become `/when` and `/how` triggers mechanically — name after the activity at the decision point, not the outcome or jargon.

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

For detailed usage patterns (error handling, workflow improvement, design decisions, pending learnings), see **`examples/codify-patterns.md`**.

