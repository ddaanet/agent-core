# Learnings Consolidation Patterns

Guidance for consolidating session learnings into permanent documentation.

## Target Selection by Domain

Route learnings to appropriate documentation based on domain.

**Project-specific routing:** Consult `agents/decisions/README.md` for domain → file mappings. Each project defines its own documentation structure and target files.

**Common domain categories:**
- Workflow patterns (handoff, planning methodology, TDD cycles, design optimization)
- Architecture decisions (module structure, path handling, rule systems, terminology, code quality)
- CLI patterns (command-line conventions, flag handling, output formatting, error reporting)
- Testing patterns (test structure, assertion patterns, mock strategies, coverage requirements)

**Documentation pattern:** Document as decision with date, rationale, implementation, and impact

### Skill-Specific → skill references/

**Anti-pattern:** Consolidate to CLAUDE.md or decisions/ (always loaded, low discoverability)

**Correct pattern:** Consolidate to skill reference files (progressive disclosure via skill triggering)

**Examples:**
- Handoff mechanics → `.claude/skills/handoff/references/learnings.md`
- Commit patterns → `.claude/skills/commit/references/learnings.md`
- Planning techniques → `.claude/skills/runbook/references/learnings.md`

**Rationale:** Skills have built-in discoverability via triggering conditions. Documentation requires grep to discover.

**Format:** Append to skill's `references/learnings.md` (create if needed)

## Progressive Disclosure Principle

**Rule:** Learnings should live where they're most likely to be needed.

**Always loaded (use sparingly):**
- CLAUDE.md - Cross-cutting concerns, critical constraints
- Session.md - Current work only (temporary)

**Loaded by path trigger:**
- decisions/ files - Via path-based rule files
- Triggered by editing specific file types
- Consult project's `agents/decisions/README.md` for routing

**Loaded by skill trigger:**
- Skill references/ - Via skill invocation
- Best discoverability for domain-specific patterns

**Loaded on demand:**
- Plan files - Historical reference only
- Archive - Background information

## Consolidation Workflow

1. **Categorize learning** by domain (workflow, architecture, CLI, testing, skill-specific)
2. **Select target file** using routing table above
3. **Draft update** following target file's format
4. **Apply update** using Edit tool (preserve structure)
5. **Verify** update is properly formatted and placed
6. **Commit** with clear message documenting what was added

## Memory Index Maintenance

**After consolidating a learning, update discovery mechanisms:**

### 1. Append to Memory Index

Add one-line entry to `agents/memory-index.md` in the appropriate domain section:

```markdown
- [Summary of learning] → `agent-core/fragments/file.md` or `agents/decisions/file.md`
```

**Examples:**
```markdown
- Sandbox bypass requires dangerouslyDisableSandbox + permissions.allow → `agent-core/fragments/sandbox-exemptions.md`
- Tier assessment determines runbook vs direct implementation → `agents/decisions/workflows.md`
```

**Append-only.** Never remove or consolidate entries. Each entry provides keyword discovery surface for on-demand knowledge — removal loses ambient awareness.

### 2. Discovery Routing

**CLAUDE.md @-reference:**
- Use when: Learning applies regardless of which files are being edited
- Examples: Communication rules, token economy, commit skill usage
- Format: `@agent-core/fragments/file.md`

**.claude/rules/ path-scoped entry:**
- Use when: Learning only applies to specific file types or directories
- Examples: Testing patterns (when editing test files), skill patterns (when editing .claude/skills/)
- Format: YAML frontmatter with `path:` array, then content
- Location: `.claude/rules/descriptive-name.md`

**Heuristic:** If the rule is "always active" → @-ref in CLAUDE.md. If it's "active when working with X" → path-scoped rule.

**Example path-scoped rule:**
```markdown
---
path:
  - .claude/skills/**/*.md
  - agent-core/skills/**/*.md
---

# Skill Development Patterns

When creating or modifying skills, follow these patterns:
- Use progressive disclosure (main SKILL.md loads references/ as needed)
- Include directive description for discoverability
- Add triggering conditions in frontmatter
```

### 3. Verify Consolidation

After updating memory index and discovery mechanisms:

- [ ] Memory index entry added to appropriate section
- [ ] Either CLAUDE.md @-ref OR .claude/rules/ entry exists (not both)
- [ ] Path-scoped rules have correct frontmatter
- [ ] Consolidated learnings removed from agents/learnings.md (keep 3-5 most recent)

## Anti-Patterns

**❌ Wrong:** Add everything to CLAUDE.md
- Causes: Context bloat, low discoverability, maintenance burden
- Fix: Route to domain-specific files

**❌ Wrong:** Keep learnings in session.md permanently
- Causes: Session file bloat, loss of historical context
- Fix: Consolidate to permanent docs, clear from session

**❌ Wrong:** Create new files for every learning
- Causes: Documentation sprawl, hard to discover
- Fix: Append to existing domain files or skill references

**❌ Wrong:** Document without context (just facts)
- Causes: Hard to understand when/why rule applies
- Fix: Include rationale, examples, and impact

**❌ Wrong:** Add to both CLAUDE.md and .claude/rules/
- Causes: Duplication, inconsistency risk
- Fix: Use routing heuristic (always-active vs path-scoped)

## Validation Checklist

Before consolidating:

- [ ] Learning is non-trivial (not obvious or one-time issue)
- [ ] Target file identified clearly
- [ ] Update includes rationale and examples
- [ ] Format matches target file's conventions
- [ ] No duplication with existing content
- [ ] Commit message clearly documents the update
