# agent-core

A shared repository for unified agent rule fragments, configurations, and templates used across multiple projects.

## Purpose

The `agent-core` repository provides a centralized location for:
- Workflow documentation (oneshot, TDD)
- Baseline agent templates (task execution, TDD cycles)
- Workflow skills (design, planning, execution, review)
- Runbook preparation tooling
- Pattern documentation (weak orchestrator, plan-specific agents)
- Shared instruction fragments and configuration templates

This enables consistent workflow execution across projects while allowing project-specific customization.

## Directory Structure

```
agent-core/
├── agents/              # Baseline agent templates
│   ├── quiet-task.md               # Base task execution agent (quiet pattern)
│   └── tdd-task.md                 # TDD cycle execution agent
├── bin/                 # Runbook preparation scripts
│   └── prepare-runbook.py          # Runbook → step artifacts generator
├── docs/                # Workflow and pattern documentation
│   ├── oneshot-workflow.md         # General implementation workflow
│   ├── tdd-workflow.md             # TDD methodology workflow
│   ├── pattern-weak-orchestrator.md # Weak orchestrator pattern
│   └── pattern-plan-specific-agent.md # Plan-specific agent pattern
├── fragments/           # Reusable content fragments
│   ├── justfile-base.just          # Base justfile recipes
│   ├── ruff.toml                   # Ruff linter configuration
│   ├── mypy.toml                   # Mypy type checker configuration
│   ├── communication.md            # Communication guidelines
│   ├── delegation.md               # Delegation patterns
│   ├── tool-preferences.md         # Tool usage preferences
│   ├── hashtags.md                 # Hashtag conventions
│   └── AGENTS-framework.md         # Framework for AGENTS.md files
├── skills/              # Workflow skills
│   ├── design/          # Design session skill (TDD/general mode)
│   ├── oneshot/         # Oneshot entry point skill
│   ├── orchestrate/     # Runbook execution skill
│   ├── plan-adhoc/      # General runbook planning skill
│   ├── plan-tdd/        # TDD runbook planning skill
│   ├── remember/        # Documentation update skill
│   └── vet/             # Code review skill
└── README.md            # This file
```

## Development Setup

When developing agent-core itself (not as a submodule), copy the local configuration template:

```bash
cp .claude/CLAUDE.local.md.example CLAUDE.local.md
```

This provides development-specific context that won't be loaded when agent-core is used as a submodule in other projects.

## Usage

Projects consume `agent-core` via git submodule:

```bash
git submodule add <agent-core-repo-url> agent-core
```

**Sync to project's .claude directory:**
```bash
cd agent-core
just sync-to-parent
```

This copies skills and agents to the parent project's `.claude/` directory for Claude Code to discover.

**Workflows:**
- Read `docs/oneshot-workflow.md` for general implementation tasks
- Read `docs/tdd-workflow.md` for test-driven development
- Use `/oneshot` skill as entry point (auto-detects methodology)

## Documentation

**Workflow guides** (read when executing):
- `docs/oneshot-workflow.md` - General implementation workflow (6 stages)
- `docs/tdd-workflow.md` - TDD methodology workflow (RED/GREEN/REFACTOR)

**Pattern guides** (read when implementing similar patterns):
- `docs/pattern-weak-orchestrator.md` - Weak orchestrator execution pattern
- `docs/pattern-plan-specific-agent.md` - Plan-specific agent generation pattern

**Skills** - Available via `/skill-name` in projects that sync agent-core

## Technical Decisions

- **Fragment granularity**: Single source files with clear composition points (split in later phases if needed)
- **Python baseline**: py312 (documented override mechanism in use)
- **Script location**: Consumer projects manage composition via `agents/compose.sh`
- **Remote hosting**: Local only during Phase 1, GitHub integration planned for Phase 2

## Development

**Plan archival policy:** Plans are NOT archived to `plans/archive/`. Git is the archive. Delete completed plans after extracting key decisions to documentation.

**Key decisions go to:**
- Parent project's `agents/design-decisions.md` - Architectural patterns
- This README - Structure and usage
- Workflow docs - Process improvements

## Adding New Workflows

1. Create workflow doc in `docs/<workflow-name>-workflow.md`
2. Create baseline agent template in `agents/<agent-type>-task.md`
3. Update `bin/prepare-runbook.py` if new runbook structure needed
4. Create planning skill in `skills/plan-<workflow-name>/`
5. Update parent project's CLAUDE.md workflow selection section
