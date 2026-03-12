### Phase A: Research + Outline

**Objective:** Load context, explore codebase, research external resources, produce plan outline.

#### A.0. Requirements Checkpoint

If `requirements.md` exists in job directory (`plans/<job-name>/requirements.md`):
- Read and summarize functional/non-functional requirements
- Note scope boundaries (in/out of scope)
- Carry requirements context into outline and design
- **Skill dependency scan:** Check if requirements mention creating agents, skills, hooks, or plugins → load corresponding `plugin-dev:*` skill immediately (don't defer to A.1)

If no requirements.md exists:
- Document requirements discovered during research
- Can be inline in design.md or separate requirements.md (designer's judgment)

**Skill dependency indicators:**
- "sub-agent", "delegate to agent", "agent definition" → `plugin-dev:agent-development`
- "skill", "invoke skill", "skill preloaded" → `plugin-dev:skill-development`
- "hook", "PreToolUse", "PostToolUse" → `plugin-dev:hook-development`
- "plugin", "MCP server" → `plugin-dev:plugin-structure`, `plugin-dev:mcp-integration`

**Anti-pattern:** Deferring skill loading to A.1 judgment when requirements explicitly mention agent/skill creation.

**Correct pattern:** Scan requirements for skill dependency indicators during A.0, load immediately.

**Rationale:** Skill content must be available for outline (A.5) and design (C.1) phases. Late loading causes missing context.

**Output:** Requirements summary + skill dependencies loaded, available for Phase A.5 (outline) and Phase C.1 (design).

#### A.1. Documentation Checkpoint

**Purpose:** Systematic documentation loading — replaces ad-hoc memory discovery.

**Hierarchy (each level is fallback when previous didn't answer):**

| Level | Source | How | When |
|-------|--------|-----|------|
| 1. Local knowledge | Execute `/recall all` protocol (deep + broad, topic-scoped). Covers memory-index, `agents/decisions/*.md`, `agents/plan-archive.md` when design overlaps with prior plans, `agent-core/fragments/*.md` when referenced. | `/recall all` | Always (core) |
| 2. Key skills | `plugin-dev:*` skills | Skill invocation | When design touches plugin components (hooks, agents, skills, MCP) |
| 3. Context7 | Library documentation via Context7 MCP tools | Designer calls directly from main session (MCP tools unavailable in sub-agents), writes results to report file | When design involves external libraries/frameworks |
| 4. Local explore | Codebase exploration | Delegate to scout agent | Always for complex designs |
| 5. Web research | External patterns, prior art, specifications | WebSearch/WebFetch (direct in main session) | When local sources insufficient |

**Not all levels needed for every task.** Level 1 is always loaded. Levels 2-5 are conditional on task domain.

**No-requirements case:** When no requirements.md exists, derive domain keywords from user request. Memory-index's keyword-rich entries amplify thin user input through cross-references. Cast a wider net on Level 1 to compensate for weaker signal.

**Design decision escalation does NOT apply here.** Design sessions exist to make architectural decisions directly.

**Recall Artifact Generation**

Documentation findings from A.1 exist only in the current context window — they do not survive to downstream pipeline stages (runbook planning, orchestration, execution, review). Persist them as a recall artifact so all downstream consumers resolve fresh content at consumption time.

**Process:** After documentation loading completes, write `plans/<job>/recall-artifact.md`. Entry keys only — no excerpts, no summaries. Downstream consumers batch-resolve via `claudeutils _recall resolve` to get current content.

**Artifact format:**

```markdown
# Recall Artifact: <Job Name>

Resolve entries via `claudeutils _recall resolve` — do not use inline summaries.

## Entry Keys

<trigger phrase> — <1-line relevance note>
<trigger phrase> — <1-line relevance note>
```

**Null artifact (no relevant entries):** Write `null — no relevant entries found` as the sole entry. Downstream consumers batch-resolve it via `claudeutils _recall resolve null` (silent exit) — the tool call anchors the gate without consumer-side empty-section handling. Augmenting consumers (/runbook Phase 0.5) remove the null entry when adding real ones.

**Selection criteria:** Include entries that informed design decisions or constrain implementation. Exclude entries read but proved irrelevant — the artifact is curated, not exhaustive.

**Output:** `plans/<job>/recall-artifact.md`, alongside other design artifacts in the job directory.

#### A.2. Explore Codebase

**Delegate exploration when scope is open-ended or spans multiple unknown files.** Read directly when files are known and few (≤3 files). The goal is cost control — opus tokens on open-ended browsing are expensive, but launching an agent to read a known file costs more than reading it directly.

For delegated exploration: Use Task tool with `subagent_type="scout"`. Specify report path: `plans/<job-name>/reports/explore-<topic>.md`. Agent writes findings to file and returns filepath.

#### A.2.5. Post-Explore Recall

Exploration surfaces codebase areas not caught by A.1's topic-based recall. Re-scan memory-index (already in context from A.1) for entries relevant to domains discovered during exploration.

**Gate anchor (D+B — tool call required):**
- **New entries found:** `claudeutils _recall resolve "when <trigger>" ...` — resolve into context, then append entry keys to recall artifact via Edit if entries have forward value for downstream consumers (runbook planning, execution, review)
- **No new entries:** `claudeutils _recall resolve null` — proves gate was reached

#### A.3-4. Research

**When external research needed** (Context7, web, grounding): Read `references/research-protocol.md` for Context7 usage, web research, grounding invocation, and recall diff guidance.

**When no external research needed:** Skip to A.5.

**Research artifact (required when research conducted):** Write findings to `plans/<job>/reports/research-<topic>.md` — frameworks considered, findings per framework, gaps identified. This file is a cascading dependency: A.5 reads it, absence blocks outline generation.

**Recall diff:** `Bash: claudeutils _recall diff <job-name>` — update artifact if codebase findings changed relevance.

#### A.5. Outline

**Gate:** If research was conducted (A.3-4), verify `plans/<job>/reports/research-*.md` exists before proceeding.

Read `references/research-protocol.md` for outline content/format guidance.

**Output:** Write outline to `plans/<job>/outline.md` — approach, key decisions, open questions, scope boundaries.

**Escape hatch:** If user input already specifies approach, decisions, and scope (e.g., detailed brief.md), compress A+B by presenting outline and asking for validation in a single message.

#### Post-Outline Complexity Re-check

`Read plans/<job>/outline.md` — load the outline to ground re-assessment.

The outline resolves the architectural uncertainty that justified "complex" classification. Re-assess before continuing ceremony.

**Downgrade criteria (all must hold):**
- Changes additive, no implementation loops
- No open questions remain
- Scope boundaries explicit (IN/OUT enumerated)
- No cross-file coordination requiring sequencing

**If met:** Skip A.6. Proceed to Phase B with sufficiency assessment.

**If not met:** Continue to A.6.

#### A.6. FP-1 Checkpoint: Review Outline

**Objective:** Validate outline before presenting to user.

**Process:**

Delegate to `outline-corrector` using Task tool with `subagent_type="outline-corrector"`:

```
Review plans/<job>/outline.md — Preliminary Design Review (PDR) criteria:
- Approach meets requirements (traceability to FRs)
- Options selected with rationale (not "explore options")
- Risks and open questions identified
- Scope boundaries explicit (IN/OUT enumerated)

Include review-relevant entries from plans/<job>/recall-artifact.md if present (failure modes, quality anti-patterns).

Apply all fixes (critical, major, minor) directly to outline.md.

Write review report to: plans/<job>/reports/outline-review.md

Return only the filepath on success (with ESCALATION note if unfixable issues), or 'Error: [description]' on failure.
```

**Handle review outcome:**
- Read the review report from the returned filepath
- If ESCALATION noted: Address unfixable issues before proceeding to user presentation
- If all issues fixed: Proceed to Phase B (report is audit trail)

---

### Phase B: User Validation

**Protocol:** Invoke `/proof plans/<job>/outline.md` — structured reword-accumulate-sync loop on the outline. On terminal action "apply", /proof dispatches outline-corrector automatically and presents findings before returning control.

**Convergence guidance:** If after 3 rounds the outline is not converging, ask user whether to proceed with current state or restart with different constraints.

**Termination:** If user feedback fundamentally changes the approach (not refining it), restart Phase A with updated understanding. Phase B is for convergence, not exploration of new directions.

### Multi-Sub-Problem Sufficiency Gate

`Read plans/<job>/outline.md` — load the outline to ground sufficiency assessment.

When an outline decomposes the job into individually-scoped sub-problems (each with readiness level and pipeline routing), the outline IS the design artifact. Do not generate a single `design.md`.

**Detection:** Outline contains a sub-problems section where each entry specifies: scope (what/how), readiness level, pipeline routing, dependencies, and file sets.

**Multi-sub-problem sufficiency criteria (all must hold):**
- Each sub-problem has concrete scope (what/how specified, not "explore")
- Dependency graph is complete (edges and absent edges enumerated)
- Completeness check traces all FRs/NFRs/constraints to sub-problems
- Scope boundaries are explicit (IN/OUT enumerated)
- Each sub-problem has a readiness level and pipeline routing
- Tear points identified and justified where dependency edges are broken

**If sufficient** — present assessment to user. On confirmation:
- The outline is the terminal design artifact for this job
- Individual sub-problems enter the pipeline via their readiness-specified route (from the readiness summary)
- The caller (session task management) dispatches sub-problems as independent pending tasks
- Follow §Continuation (no prepend — dispatch is the caller's responsibility)

**If insufficient** — identify which criteria failed. Resume from A.5 (revise outline) or present gaps for discussion.

---

### Outline Sufficiency Gate

`Read plans/<job>/outline.md` — load the outline to ground sufficiency assessment.

After user validates the outline, assess whether it already contains enough specificity to skip design generation.

**Sufficiency criteria (all must hold):**
- Approach is concrete (specific algorithm/pattern chosen, not "explore options")
- Key decisions are resolved (no open questions remaining)
- Scope boundaries are explicit (IN/OUT enumerated)
- Affected files are identified
- No architectural uncertainty remains

**If sufficient** — present sufficiency assessment to user. The outline IS the design; confirm user agrees to skip design generation. On confirmation, assess execution readiness:

**Execution routing (work-type-aware):**

```
IF all prose edits, no implementation loops → INLINE (hard gate — file count irrelevant)
ELSE IF work type = Investigation → inline (criteria below)
ELSE IF work type = Exploration AND design resolved all questions → inline (criteria below)
ELSE (work type = Production AND behavioral code) → /runbook
```

**Prose path rationale:** Prose edits are commutative — editing file A before or after file B produces the same result. Multi-file prose does not constitute cross-file coordination. Coordination complexity arises from runtime ordering dependencies (test↔implementation, build↔verify), not from editing multiple files.

**Inline criteria (non-prose paths only — prose path bypasses these):**
- All decisions pre-resolved (no open questions requiring feedback)
- Insertion points or edit targets are identified (line-level or section-level)
- No runtime ordering dependencies between files
- No implementation loops (no test/build feedback required)
- Scope fits inline capacity (single session, single model)

Inline execution bypasses `/runbook` — this gate assesses coordination complexity and capacity. For prose, the first routing branch already decided.

**If execution-ready** — offer direct execution. On confirmation, follow §Continuation (prepends `/inline plans/<job> execute`).

**If not execution-ready** — commit design artifact, then follow §Continuation.

**If insufficient** — Read `references/write-design.md` for Phase C (full design generation) and design constraints.

**When to apply:** Small-to-moderate jobs where research (Phase A) fully resolved the approach and user discussion (Phase B) confirmed without introducing new complexity.
