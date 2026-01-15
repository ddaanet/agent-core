# agent-core

A shared repository for unified agent rule fragments, configurations, and templates used across multiple projects.

## Purpose

The `agent-core` repository provides a centralized location for:
- Shared agent instruction fragments (AGENTS-framework.md)
- Configuration templates (ruff, mypy)
- Build automation (justfile recipes)
- Communication and delegation guidelines
- Tool preference documentation
- Hashtag conventions

This enables consistent agent behavior across projects while allowing project-specific customization through composition and templating.

## Directory Structure

```
agent-core/
├── fragments/           # Reusable content fragments
│   ├── justfile-base.just          # Base justfile recipes
│   ├── ruff.toml                   # Ruff linter configuration
│   ├── mypy.toml                   # Mypy type checker configuration
│   ├── communication.md            # Communication guidelines
│   ├── delegation.md               # Delegation patterns
│   ├── tool-preferences.md         # Tool usage preferences
│   ├── hashtags.md                 # Hashtag conventions
│   └── AGENTS-framework.md         # Framework for AGENTS.md files
├── agents/              # Reserved for Phase 2 - composition logic
├── composer/            # Reserved for future - composition tooling
└── README.md           # This file
```

## Usage

Projects consume `agent-core` fragments in two ways:

1. **Git Submodule**: Add as a submodule for version tracking
   ```bash
   git submodule add ../agent-core agent-core
   ```

2. **Fragment Composition**: Use composition scripts to generate project-specific files
   - Extract relevant fragments from `agent-core/fragments/`
   - Customize with project-specific values
   - Generate output files (AGENTS.md, justfile, configs)

## Fragment Composition

Each fragment is designed to be:
- **Self-contained**: Can be understood independently
- **Template-ready**: Supports variable substitution for project customization
- **Version-tracked**: Submodule pinning ensures consistency

See individual fragment files for composition points and customization options.

## Technical Decisions

- **Fragment granularity**: Single source files with clear composition points (split in later phases if needed)
- **Python baseline**: py312 (documented override mechanism in use)
- **Script location**: Consumer projects manage composition via `agents/compose.sh`
- **Remote hosting**: Local only during Phase 1, GitHub integration planned for Phase 2

## Development

This repository is part of the unified rules system. See the main claudeutils project for:
- Unification design and planning
- Test results and validation
- Integration with consuming projects

## References

- Phase 1 design: plans/unification/design.md
- Execution context: plans/unification/steps/phase1-execution-context.md
- Current implementation: claudeutils/agents/*
