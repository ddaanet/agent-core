---
name: memory-index
description: |
  This skill should be used when sub-agents need memory recall capabilities. Provides index of when/how entries with Bash transport for agents without Skill tool access.
user-invocable: false
---

# Memory Index

Active knowledge retrieval for sub-agents. Sub-agents lack the Skill tool and cannot invoke `/when` or `/how` skills directly. Instead, use Bash transport to access indexed decision documents.

**Sub-agent invocation (via Bash):**
```bash
agent-core/bin/when-resolve.py when "<trigger>"
agent-core/bin/when-resolve.py how "<trigger>"
```

**Examples:**
```bash
# Behavioral knowledge
agent-core/bin/when-resolve.py when "using oneshot workflow"

# Procedural knowledge
agent-core/bin/when-resolve.py how "format token count output"

# Section navigation
agent-core/bin/when-resolve.py when ".Section Title"

# Full file access
agent-core/bin/when-resolve.py when "..file.md"
```

**Index syntax:** Triggers below are the same keys used by the `/when` skill. Invoke via Bash as shown above.

<!-- Synced from agents/memory-index.md — update both when index changes -->

---

## agents/decisions/cli.md

/when getting current working directory
/how output errors to stderr
/how configure script entry points
/when choosing feedback output format
/how format token count output

## agents/decisions/data-processing.md

/how write init files
/when placing helper functions
/when splitting large modules
/how encode file paths
/how resolve history directories
/how extract session titles
/how format session titles
/how detect trivial messages
/how layer feedback extraction
/how validate session uuid files
/when sorting glob results
/how parse first line metadata
/how resolve agent ids to sessions
/how extract agent ids from sessions
/when handling malformed session data
/how handle optional field defaults

## agents/decisions/pipeline-contracts.md

/when transformation table | T1-T6 pipeline stages defect types review gates criteria
/how review delegation scope template | scope IN OUT changed files requirements
/when UNFIXABLE escalation | fix-all pattern grep UNFIXABLE stop escalate
/when phase type model | tdd general per-phase typing expansion review criteria
/when vet escalation calibration | over-escalation pattern-matching not design
/when vet flags out-of-scope items | DEFERRED vs UNFIXABLE distinction
/when vet receives execution context | filesystem vs execution-time state
/when vet-fix-agent rejects planning artifacts | plan-reviewer routing
/when expansion reintroduces defects | LLM failure modes at both levels

## agents/decisions/deliverable-review.md

/when identifying deliverable artifacts

## agents/decisions/implementation-notes.md

/when using at-sign references
/when placing skill constraint rules
/when using session start hooks
/how filter user prompt submit hooks
/when using hooks in subagents
/when needing mcp tools in subagents
/when skill is already loaded
/when treating commits as sync points
/when deciding to commit interactively
/when choosing naming convention format
/when formatting index entry lines
/when classifying section headers
/when reading design classification tables
/when writing memory index entry keys
/how format runbook phase headers
/how implement prose gates
/when choosing hard or soft limits
/when marking organizational sections
/when shortening index entry keys
/how format batch edits efficiently
/when removing stale learnings on commit

## agents/decisions/markdown-tooling.md

/how pass model as cli argument
/how handle model alias resolution
/how integrate with anthropic api
/when counting tokens in empty files
/when expanding file glob patterns
/when fixing consecutive emoji lines
/how clean markdown before formatting
/when extending vs creating cleanup functions
/when handling invalid markdown patterns
/how order markdown processing steps
/how detect markdown line prefixes
/how indent nested markdown lists
/when evolving markdown processing
/when choosing markdown formatter tool

## agents/decisions/project-config.md

/how manage memory index growth
/how inject context with rule files
/when naming model capability tiers
/how surface skills through discovery layers
/when writing agent yaml frontmatter
/when verifying symlinks after operations
/when using heredocs in sandbox
/when parsing cli flags as tokens
/when finding project root in scripts

## agents/decisions/prompt-structure-research.md

/when ordering content for position bias
/when formatting rules for adherence
/when writing rules for different models
/when managing rule count budget
/when loading context for llm processing
/when evaluating prompt structure tools
/when applying prompt research
/how order fragments by position bias

## agents/decisions/runbook-review.md

/when detecting vacuous tdd cycles
/when ordering runbook dependencies
/when evaluating cycle density
/when spacing runbook checkpoints
/when planning for file growth | lines-per-cycle projection split points

## agents/decisions/testing.md

/how split test modules
/how apply mock patches correctly
/how test markdown cleanup
/when evaluating test success metrics
/when writing red phase assertions
/when testing presentation vs behavior
/when writing integration test assertions
/how validate migration conformance
/when preferring e2e over mocked subprocess | real git repos tmp_path
/when asserting pipeline idempotency | preprocessor remark roundtrip
/when detecting vacuous assertions from skipped RED | assertion strength

## agents/decisions/validation-quality.md

/when choosing pydantic for validation
/how define feedback type enum
/when docstring formatting conflicts
/how manage cyclomatic complexity
/when tempted to suppress linting
/when adding strict type annotations
/how architect feedback pipeline
/how build reusable filtering module
/how detect noise in command output
/how categorize feedback by keywords
/how deduplicate feedback entries
/when filtering for rule extraction

## agents/decisions/workflow-advanced.md

/when seeding indexes before generation
/when adding entries without documentation
/how merge templates safely
/when requirements change during execution
/when embedding knowledge in context
/how name tasks as prose keys
/when committing rca fixes
/when running precommit validation
/how expand outlines into phases
/how review phases iteratively
/when assembling runbooks manually
/how use review agent fix all pattern
/how transmit recommendations inline
/how name review reports
/when writing test descriptions in prose
/when checking complexity before expansion
/when using consolidation gates
/when applying feedback loop insights
/when dogfooding process design
/when scanning requirements for skills
/when crossing phase boundaries
/how write green phase descriptions
/when verifying model analysis results
/how implement domain validation

## agents/decisions/workflow-core.md

/when using oneshot workflow
/how integrate tdd workflow
/how store learnings in handoffs
/when optimizing design phase output
/how document three stream planning
/how squash tdd cycle commits
/when setting orchestrator execution mode
/when assessing orchestration tier
/how checkpoint runbook execution
/how structure phase grouped runbooks
/when cycle numbering has gaps
/when refactoring needs escalation
/how verify commits defense in depth
/when delegating without plan

## agents/decisions/workflow-optimization.md

/how chain handoff tail calls
/when handoff includes commit flag
/when context already loaded for delegation
/when assessing routing layer efficiency
/when reusing vet agent context
/how design with outline first approach
/when selecting model for design guidance
/when choosing model for design review
/when vet catches structural issues
/when reviewing agent definitions
/when template context contradicts rules
/when orchestrator model differs from step
/when ordering tdd test cases
/how format runbook outlines
/how implement continuation passing
/when using hook based parsing

## agents/decisions/orchestration-execution.md

/when delegation requires commit instruction | agents leave tree dirty
/when context defines scope boundary | structural not prose constraints
/when deduplicating delegation prompts | shared file reference
/when managing orchestration context | handoff not delegatable
/when no post-dispatch communication available | fire-and-forget partitioning
/when running post-step verification | git status UNFIXABLE grep
/when planning is parallelizable | phase expansion concurrent agents
/when stabilizing orchestrator model | sonnet before haiku optimization
/when using opus for RCA delegation | primary source verification
/when sonnet inadequate for synthesis | opus for multi-turn extraction
/when no model tier introspection available | no API ask or use hook
/when always scripting non-cognitive solutions | deterministic pattern-based
/when script validates it should generate | metadata injection
/when bootstrapping around broken tools | design as execution plan
/when assessing RED pass blast radius | over-implementation test-flaw correct
/when unifying over patching | shared code bifurcation root cause
/when common context competes with step | phase-neutral only
/when capturing requirements from conversation | capture over interview

## agents/decisions/operational-practices.md

/when placing deliverable artifacts | plans vs tmp referenced later
/when requiring per-artifact vet coverage | batch momentum skip prevention
/when launching task agents in parallel | single message batch
/when background agents crash | check output files recovery
/when refactoring agents need quality directives | deslop factorization
/when exploration agents report false findings | verify file existence
/when scrubbing learnings before design input | validate against evidence
/when temporal validation required for analysis | git history correlation
/when behavioral triggers beat passive knowledge | when how only
/when enforcement cannot fix judgment | structural vs conversation-level
/when no-op merge orphans branch | always create merge commit
/when task names must be branch-suitable | alphanumeric constraint
/when classifyHandoffIfNeeded bug occurs | foreground Task calls fail background works
/when sub-agents cannot spawn sub-agents | Task MCP hooks unavailable
/when extracting git helper functions | _git pattern subprocess reduction
/when fixture shadowing creates dead code | pytest fixture vs local function
/when test corpus defines correct behavior | fixtures are spec not workaround
/when index keys must be exact | fuzzy only for runtime recovery
/when DP matrix has zero-ambiguity | -inf initialization impossible states
/when phase numbering is flexible | 0-based or 1-based detect from first
/when checking self-referential modification | exclude plan own directory
/when avoiding CLI skill name collision | check built-ins before naming
