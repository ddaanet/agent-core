# Research Protocol

Phases A.3-A.5 of the design process: external research, grounding, and outline production.

## A.3-4. External Research (if needed)

**Context7:** Call MCP tools directly from main session (unavailable in sub-agents). Write results to report file: `plans/<job-name>/reports/context7-<topic>.md`.

**Web research:** WebSearch/WebFetch for external patterns, prior art, or specifications.

**Grounding:** When the design will produce a methodology, framework, scoring system, or taxonomy, invoke `/ground` to prevent confabulated structures. The ground skill runs parallel internal+external research branches and produces a grounded reference document in `plans/reports/`.

## A.5. Produce Plan Outline

**Recall diff:** `Bash: agent-core/bin/recall-diff.sh <job-name>`

Review the changed files list. Codebase findings, external research, and Context7 results make different recall entries relevant than what A.1 selected from the initial problem description. If files changed that affect which recall entries are relevant, update the artifact: add entries surfaced by changes, remove entries that proved irrelevant. Write updated artifact back.

**Output:** Write outline to `plans/<job>/outline.md` (create directory if needed).

**Content:**
- Approach summary
- Key decisions
- Open questions
- Scope boundaries

**Example outline** (for reference -- adapt to task):
```
Approach: Add rate limiting middleware to API gateway using token bucket algorithm.
Key decisions: Per-user limits (not global), Redis-backed counters, 429 response with Retry-After header.
Open questions: Should rate limits vary by endpoint? Should admin users be exempt?
Scope: API gateway only. Dashboard/monitoring out of scope.
```

**Escape hatch:** If user input already specifies approach, decisions, and scope (e.g., detailed problem.md), compress A+B by presenting outline and asking for validation in a single message.
