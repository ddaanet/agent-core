# agent-core

Workflow infrastructure for [Claude Code][claude-code] agents. Without
structure, agent sessions drift: incomplete implementations, skipped reviews,
scope creep, lost context between sessions. agent-core imposes a pipeline —
design, planning, TDD, orchestration, review, handoff — and a memory system
that persists decisions across sessions.

18 skills, 14 specialized sub-agents, 23 instruction fragments, 4 hooks, and
scripts for runbook preparation, session recovery, and batch operations.

Currently installed as a git submodule; converting to a [Claude Code
plugin][plugin-docs] (`edify-plugin`).

Requires [just] for task running. Scripts in `bin/` use Python 3.

## Installation

```bash
git submodule add <repo-url> agent-core
cd agent-core && just sync-to-parent
```

`just sync-to-parent` creates symlinks in the parent project's `.claude/`
directory so Claude Code discovers skills, agents, and hooks. It also
configures hooks in `.claude/settings.json`. Changes to agent-core are
reflected immediately without re-syncing.

Set up your `CLAUDE.md` to reference fragments — use
`templates/CLAUDE.template.md` as a starting point, or add `@` references to
an existing file:

```markdown
@agent-core/fragments/communication.md
@agent-core/fragments/execution-routing.md
```

These are loaded into every conversation as ambient context.

## Structured Workflow

The core pipeline:

```
/design → /runbook → [runbook-corrector] → /orchestrate → [corrector] → /handoff
```

`/design` triages complexity. Simple tasks execute directly. Moderate tasks skip
to planning. Complex tasks get Opus architectural design with outline iteration
and design review.

`/runbook` produces step-by-step execution plans with per-phase typing — TDD
cycles or general steps, mixed within a single runbook. `runbook-corrector` checks
TDD discipline, step quality, and LLM failure modes before execution.

`/orchestrate` dispatches each step to a sub-agent in isolated context.
Executing agents receive only their step file plus the design — no access to
other steps, so scope is enforced structurally rather than by prose
instructions. Review follows every production artifact.

`/handoff` captures completed work, pending tasks, and blockers for the next
session. `/commit` handles structured commit messages with gitmoji.

The pipeline is not mandatory. Any skill works independently. But the full
sequence prevents the failure mode where a task succeeds in one session and
leaves wreckage for the next.

### Session Modes

Agents start in one of five modes, triggered by shortcuts:

| Shortcut | Mode | Behavior |
|----------|------|----------|
| `s` | Status | List pending tasks with metadata, wait |
| `x` | Execute | Resume in-progress or start first pending |
| `xc` | Execute+Commit | Execute, then handoff and commit |
| `r` | Resume | Strict: resume only, error if nothing in progress |
| `wt` | Worktree | Set up parallel execution via git worktrees |

## Memory Management

Claude Code sessions are stateless. The memory system persists project
knowledge in an `agents/` directory in the consuming project:

- **session.md** — pending tasks, in-progress work, blockers. The handoff
  document. Agents read it at startup, update it at `/handoff`
- **learnings.md** — institutional knowledge from mistakes and discoveries.
  Append-only, consolidated via `/remember` when approaching the 80-line limit
- **memory-index.md** — keyword catalog pointing to detailed documentation.
  Agents scan the index to decide what to load on demand
- **decisions/** — permanent architectural and implementation decisions, one
  heading per topic. Where learnings graduate to
- **jobs.md** — plan lifecycle tracking (`requirements` → `designed` → `planned`
  → `complete`)

Validators (`bin/validate-*.py`) enforce cross-reference integrity, format
conventions, and key uniqueness across these files.

## Skills

Skills are slash-command procedures that inject instructions into the current
conversation when invoked. Agents (next section) are separate processes with
isolated context, spawned via the Task tool. Each skill lives in
`skills/<name>/SKILL.md`.

**Workflow pipeline:**

| Skill | Purpose |
|-------|---------|
| `/design` | Entry point — triages complexity, routes to appropriate workflow |
| `/runbook` | Creates execution plans with per-phase TDD or general typing |
| `/review-plan` | Reviews runbook quality, TDD discipline, LLM failure modes |
| `/orchestrate` | Dispatches runbook steps to sub-agents |
| `/review` | Reviews production artifacts for quality |

**Session management:**

| Skill | Purpose |
|-------|---------|
| `/handoff` | Updates session.md with completed work and pending tasks |
| `/commit` | Structured commit messages with gitmoji |
| `/next` | Shows pending work when no context is loaded |
| `/shelve` | Archives session context to task list, resets for new work |
| `/remember` | Consolidates learnings into permanent documentation |

**Specialized:**

| Skill | Purpose |
|-------|---------|
| `/reflect` | Root cause analysis of agent behavior deviations |
| `/opus-design-question` | Delegates architectural decisions to Opus |
| `/worktree` | Git worktree lifecycle for parallel task execution |
| `/release-prep` | Pre-release validation and documentation updates |
| `/token-efficient-bash` | `set -xeuo pipefail` pattern for 40-60% token reduction |
| `/gitmoji` | Semantic emoji matching for commit messages |
| `/handoff-haiku` | Mechanical handoff for Haiku orchestrators |
| `/plugin-dev-validation` | Domain validation criteria for plugin components |

## Agents

Sub-agents are invoked via the Task tool for isolated work. Each is defined in
`agents/<name>.md` with a system prompt and tool access list.

**Execution:**

| Agent | Purpose |
|-------|---------|
| `artisan` | General task execution (reports to files, terse returns) |
| `test-driver` | TDD cycle execution with RED/GREEN/REFACTOR phases |
| `refactor` | Escalated refactoring with sonnet-level evaluation |

**Review:**

| Agent | Purpose |
|-------|---------|
| `corrector` | Reviews changes, applies all fixes, returns report |
| `design-corrector` | Opus architectural review for design documents |
| `runbook-corrector` | Runbook quality and TDD discipline review |
| `outline-corrector` | Design outline validation before user discussion |
| `runbook-outline-corrector` | Runbook outline validation before expansion |
| `tdd-auditor` | Post-execution TDD quality analysis |

**Utilities:**

| Agent | Purpose |
|-------|---------|
| `scout` | Codebase exploration with results persisted to files |
| `remember-task` | Learnings consolidation during handoff |
| `memory-refactor` | Splits documentation files exceeding 400 lines |
| `hooks-tester` | Tests all configured hooks after modifications |

## Fragments

Instruction fragments are reusable markdown files loaded into every conversation
via `@` references in `CLAUDE.md`. They define behavioral rules, operational
patterns, and project conventions.

Fragments are ambient context — agents don't need to explicitly load them.

**Behavioral:**
`communication.md`, `deslop.md`, `execute-rule.md`, `error-handling.md`,
`no-estimates.md`, `code-removal.md`, `token-economy.md`,
`design-decisions.md`, `commit-skill-usage.md`

**Operational:**
`execution-routing.md`, `delegation.md`, `tool-batching.md`,
`review-requirement.md`, `sandbox-exemptions.md`, `bash-strict-mode.md`,
`tmp-directory.md`, `project-tooling.md`, `claude-config-layout.md`

**Workflow:**
`workflows-terminology.md`, `continuation-passing.md`, `commit-delegation.md`,
`error-classification.md`, `prerequisite-validation.md`

## Hooks

Hook scripts intercept tool calls and prompt submissions:

| Hook | Event | Purpose |
|------|-------|---------|
| `pretooluse-block-tmp.sh` | PreToolUse (Write\|Edit) | Blocks writes to `/tmp/` |
| `submodule-safety.py` | PreToolUse + PostToolUse (Bash) | Enforces cwd at project root |
| `userpromptsubmit-shortcuts.py` | UserPromptSubmit | Expands shortcut vocabulary (`x`, `s`, `r`, etc.) |
| `pretooluse-symlink-redirect.sh` | PreToolUse (Edit) | Resolves symlink targets for edits |

## Scripts

Utility scripts in `bin/`:

| Script | Purpose |
|--------|---------|
| `prepare-runbook.py` | Assembles runbook from phase files, injects metadata |
| `assemble-runbook.py` | Concatenates step files into single runbook |
| `batch-edit.py` | Applies marker-format batch edits to files |
| `focus-session.py` | Creates focused session.md for specific task |
| `task-context.sh` | Recovers session context from git history |
| `add-learning.py` | Appends structured learning entries |
| `learning-ages.py` | Reports learning entry ages for consolidation |

**Validators (also in `bin/`):**

| Script | Purpose |
|--------|---------|
| `validate-memory-index.py` | Validates memory index format and cross-references |
| `validate-decisions.py` | Validates decision file format and key uniqueness |
| `validate-jobs.py` | Validates jobs.md format and status values |
| `validate-learnings.py` | Validates learnings.md format and line limits |
| `validate-tasks.py` | Validates session.md task format and metadata |

## Project Templates

`templates/` provides scaffolding for new projects:

- `CLAUDE.template.md` — starter CLAUDE.md with fragment references
- `dotenvrc` — direnv configuration for Python projects

`configs/` provides shared tool configurations:

- `ruff-base.toml`, `mypy-base.toml`, `docformatter-base.toml` — linter baselines
- `justfile-base.just` — common justfile recipes
- `claude-env.sh` — environment setup for Claude Code sessions

## Development

```bash
just help           # available recipes
just sync-to-parent # sync skills/agents/hooks to parent .claude/
just precommit      # validation (stub — no build requirements)
```

### Adding a Skill

Create `skills/<name>/SKILL.md` with the procedure. Run `just sync-to-parent`
in the parent project to create the symlink. Restart Claude Code.

### Adding an Agent

Create `agents/<name>.md` with frontmatter (model, tools, description) and
system prompt. Run `just sync-to-parent`. Restart Claude Code.

### Adding a Fragment

Create `fragments/<name>.md`. Add an `@agent-core/fragments/<name>.md` reference
in the parent project's `CLAUDE.md`. No restart needed — fragments load on next
conversation.

## License

MIT

[claude-code]: https://github.com/anthropics/claude-code
[just]: https://just.systems
[plugin-docs]: https://docs.anthropic.com/en/docs/claude-code/plugins
