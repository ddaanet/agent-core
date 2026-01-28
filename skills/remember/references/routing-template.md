# Decision Documentation Routing Template

This template shows how to structure `agents/decisions/README.md` for project-specific routing of learnings consolidation.

## Format

Use H3 headings with target file path, followed by description body with example topics.

## Template

```markdown
# Decision Documentation

This directory contains architectural and process decisions for the project.

## Domain Routing

### Workflow Patterns → `workflows.md`
Handoff workflow changes, planning methodology improvements, TDD cycle patterns, design phase optimization, commit squashing strategies.

### Architecture → `architecture.md`
Module structure, path handling algorithms, rule file systems, model terminology standards, code quality patterns.

### CLI Conventions → `cli.md`
Command-line interface patterns, flag handling, output formatting, error reporting, entry point organization.

### Testing → `testing.md`
Test structure decisions, assertion patterns, mock/fixture strategies, coverage requirements, TDD methodology.

## Adding New Domains

When a learning doesn't fit existing domains, create a new file and add a routing entry here.
```

## Why This Format

**H3 headings = scannable:**
- Grep with `^###` to extract routing rules
- Skim visually to find appropriate target
- Standard markdown parsing

**Description body = rich context:**
- Example topics disambiguate edge cases
- Helps determine best fit for borderline learnings
- Documents rationale for domain boundaries

**Standard markdown = tooling-friendly:**
- Works with existing tools and workflows
- Extensible for future needs
- No special parsing required
