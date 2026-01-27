# Learnings Consolidation Patterns

Guidance for consolidating session learnings into permanent documentation.

## Target Selection by Domain

Route learnings to appropriate documentation based on domain:

### Workflow Patterns → decisions/workflows.md

**Examples:**
- Handoff workflow changes
- Planning methodology improvements
- TDD cycle patterns
- Design phase optimization
- Commit squashing strategies

**Pattern:** Document as decision with date, rationale, implementation, and impact

### Architecture Decisions → decisions/architecture.md

**Examples:**
- Module structure changes
- Path handling algorithms
- Rule file systems
- Model terminology standards
- Code quality standards

**Pattern:** Document as decision with date, rationale, and impact

### CLI Patterns → decisions/cli.md

**Examples:**
- Command-line interface conventions
- Flag handling patterns
- Output formatting decisions
- Error reporting standards

**Pattern:** Document as decision with date, rationale, and impact

### Testing Patterns → decisions/testing.md

**Examples:**
- Test structure decisions
- Assertion patterns
- Mock/fixture strategies
- Coverage requirements

**Pattern:** Document as decision with date, rationale, and impact

### Skill-Specific → skill references/

**Anti-pattern:** Consolidate to CLAUDE.md or decisions/ (always loaded, low discoverability)

**Correct pattern:** Consolidate to skill reference files (progressive disclosure via skill triggering)

**Examples:**
- Handoff mechanics → `.claude/skills/handoff/references/learnings.md`
- Commit patterns → `.claude/skills/commit/references/learnings.md`
- Planning techniques → `.claude/skills/plan-adhoc/references/learnings.md`

**Rationale:** Skills have built-in discoverability via triggering conditions. Documentation requires grep to discover.

**Format:** Append to skill's `references/learnings.md` (create if needed)

## Progressive Disclosure Principle

**Rule:** Learnings should live where they're most likely to be needed.

**Always loaded (use sparingly):**
- CLAUDE.md - Cross-cutting concerns, critical constraints
- Context.md - Current work only (temporary)

**Loaded by path trigger:**
- decisions/ files - Via path-based rule files
- Triggered by editing specific file types

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

## Validation Checklist

Before consolidating:

- [ ] Learning is non-trivial (not obvious or one-time issue)
- [ ] Target file identified clearly
- [ ] Update includes rationale and examples
- [ ] Format matches target file's conventions
- [ ] No duplication with existing content
- [ ] Commit message clearly documents the update
