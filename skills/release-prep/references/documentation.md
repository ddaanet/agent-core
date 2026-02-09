# Documentation Update Guide

Detailed guidance for the documentation update step in release-prep. Documentation updates are batched at the end of the development cycle — hack → hack → hack → prep → release.

## Two Audiences

### Human-Facing Documentation (README.md)

**Quality bar:** Thoughtful, polished, highly informative, easy to read. README.md is the project's public face — it must reflect craft.

**Style corpus:** Check for project-specific `tmp/STYLE_CORPUS` first. If it exists, use it — the project owner has curated style samples specific to their voice. If not, fall back to the bundled `references/default-style-corpus.md`. Either way, read the corpus before writing to internalize the conventions.

**Update process:**

1. Read style corpus once at start (`tmp/STYLE_CORPUS` or `references/default-style-corpus.md`) to internalize conventions
2. Read current `README.md`
3. Identify stale sections by comparing against:
   - Commits since last release (from step 5 scope assessment)
   - Current CLI commands: `<tool> --help` for each subcommand
   - Current project structure: `src/` layout, test files
   - Current dependencies: `pyproject.toml` / `package.json`
4. Rewrite stale sections applying style corpus conventions
5. Verify all code examples actually work (commands, flags, output)
6. Check internal consistency (features list matches usage sections)

**Common staleness patterns:**
- New CLI subcommands not documented
- Changed flags or arguments
- Outdated project structure trees
- Version requirements changed
- New dependencies undocumented
- Removed features still listed
- Example output doesn't match current behavior

**Style principles (apply from corpus):**
- Lead with what the tool does, not implementation details
- Show real usage before explaining internals
- Keep code examples minimal and runnable
- Group related features logically
- Avoid jargon where plain language works
- Every section should earn its place — remove filler

### Agent-Facing Documentation

Agent documentation targets LLMs and automation. Different quality bar: precision, discoverability, structured triggers.

**What to update:**

**Skill descriptions** (`agent-core/skills/*/SKILL.md` frontmatter):
- Verify trigger phrases match actual usage patterns observed during the development cycle
- Add new trigger phrases discovered during hack sessions
- Remove triggers for deprecated features

**CLAUDE.md and fragments:**
- Verify `@` references point to existing files
- Check that behavioral rules match current implementation
- Confirm workflow descriptions are current

**Memory index** (`agents/memory-index.md`):
- Verify entries point to existing files
- Check that descriptions are keyword-rich for discovery
- No duplicate entries for same concept

**Templates and examples:**
- Verify templates work with current tool versions
- Check that example commands produce expected output
- Update sample data if formats changed

**Skip agent doc updates** when nothing agent-related changed during the development cycle. Focus updates on areas affected by actual changes.

## Diff-Driven Audit

Rather than auditing all documentation, focus on what changed:

1. Get commits since last release (already available from step 5)
2. Categorize changes: new features, changed APIs, removed features, infrastructure
3. For each category, identify affected documentation sections
4. Update only affected sections

This prevents unnecessary churn in stable documentation.

## Commit Strategy

Documentation updates from this step should be committed before running the release command:

1. Complete all documentation updates
2. Stage documentation files
3. Commit with descriptive message (e.g., "Update README and agent docs for release")
4. Proceed to readiness report (step 7)

The release recipe expects a clean working tree — documentation must be committed first.
