---
name: ground
description: >-
  This skill should be used when producing methodological, framework, taxonomic,
  or best-practice claims, or when the user asks to "ground", "create a scoring
  system", "design a methodology", "build a framework", or "synthesize best
  practices". Parallel diverge-converge research preventing confabulated structures.
allowed-tools: Read, Write, Grep, Glob, Bash, WebSearch, WebFetch, Task
user-invocable: true
---

# Ground Claims with Research

Prevent ungrounded confabulation when producing methodologies, frameworks, scoring systems, taxonomies, or best-practice documents. Encode the diverge-converge research pattern proven during prioritization skill creation.

**Core principle:** Internal reasoning alone confabulates plausible structures. External research alone produces generic frameworks. Parallel diverge + synthesis produces grounded, project-adapted output.

## Procedure

### Phase 1: Scope

Frame the research question before searching.

- Define the topic: "What established frameworks exist for [X]?"
- Set inclusion criteria: relevance to project context, actionable methodology, procedural (not pure theory)
- Set exclusion criteria: wrong domain, no procedure, outdated
- Select parameters (consult `references/grounding-criteria.md` for guidance):
  - Internal scope: **codebase** (descriptive — "what patterns exist for X") or **conceptual** (generative — "what dimensions/constraints apply to X")
  - Model tier for internal branch: codebase → sonnet (scout); conceptual → opus (generative divergence)
  - Research breadth: narrow (1-2 searches) or broad (3-5 searches)
  - Output format: reference document, skill body, or decision entry

### Phase 2: Diverge

Execute two branches as parallel Task agents. Launch both in a single message. Neither is optional — both are required.

**Branch A — Internal explore:**
Scope determines agent type and model:
- **Codebase scope:** Delegate to scout agent. Surface existing codebase patterns, prior decisions, current conventions. Output: inventory of existing patterns with file references. Write to `plans/reports/<topic>-internal-codebase.md`.
- **Conceptual scope:** Delegate to Task agent (subagent_type: general-purpose, model: opus). Generate project-specific dimensions, constraints, desiderata, evaluation axes. Focus on what no external source would surface. Write to `plans/reports/<topic>-internal-conceptual.md`.

**Branch B — External research:**
Delegate to Task agent (subagent_type: general-purpose, model: sonnet). Model is always sonnet regardless of invoking workflow tier. Agent prompt includes:
- Research topic and framing question from Phase 1
- Search query templates from `references/grounding-criteria.md`
- Evaluation criteria: relevant to project context? Actionable methodology? Named framework with structure?
- Output contract: framework names, component structures, scoring mechanics, known limitations

Write to `plans/reports/<topic>-external-research.md`.

Both agents write reports and return filepath only (quiet execution pattern).

### Phase 3: Converge

Synthesize both branches into grounded output.

- Map internal dimensions onto external framework skeleton
- Adapt scoring criteria or structural elements using project-specific evidence
- Apply convergence template from `references/grounding-criteria.md` (Framework Mapping, Adaptations, Grounding Assessment, Sources)
- Attach grounding quality label (mandatory): Strong / Moderate / Thin / None. See `references/grounding-criteria.md` for label definitions and evidence requirements.

**Framing rule — general first:** State each principle as the general insight derived from external research. Project-specific implementation is an instance that validates the principle, not the principle itself. The internal branch confirms the principle applies locally; it does not define the principle.

- ❌ "Git state queries return booleans — `_git_ok(*args) -> bool`"
- ✅ "Expected states should return booleans, not raise exceptions — implemented as `_git_ok()` in this project"

### Phase 4: Output

Write the grounded reference document to `plans/reports/<topic>.md` (persistent, tracked).

Required sections:
- Research foundation (named sources with links)
- Adapted methodology — general principle per item, then project implementation as instance
- Grounding quality label with evidence basis
- Sources section with retrieval context

**Branch artifacts:** Both branch reports in `plans/reports/` are retained as audit evidence supporting the synthesis through the design lifecycle. The grounding report references both.

## References

- **`references/grounding-criteria.md`** — Trigger criteria, quality labels, parameter selection, search query templates, convergence template
