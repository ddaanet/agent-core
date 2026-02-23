---
name: ground
description: >-
  This skill should be used when producing output that contains methodological
  claims ("the best way to X is Y"), framework claims ("the dimensions of X
  are"), taxonomic claims ("there are N types of X"), or best-practice claims
  ("established practice is to X"). Also when the user asks to "create a
  scoring system", "design a methodology", "build a framework", "define a
  taxonomy", "synthesize best practices", or "ground this claim".
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
  - Internal branch type: **brainstorm** (prescriptive — "how should we X") or **explore** (descriptive — "what do we currently do about X")
  - Model tier for internal branch: brainstorm → always opus; explore → sonnet
  - Research breadth: narrow (1-2 searches) or broad (3-5 searches)
  - Output format: reference document, skill body, or decision entry

### Phase 2: Diverge

Execute two branches in parallel. Neither is optional — both are required.

**Branch A — Internal:**
- **Brainstorm mode:** Delegate to Task agent (subagent_type: general-purpose, model: opus). Generate project-specific dimensions, constraints, desiderata, evaluation axes. Output: list of dimensions with rationale, written to tmp file. Focus on what no external source would surface.
- **Explore mode:** Delegate to scout agent. Surface existing codebase patterns, prior decisions, current conventions. Output: inventory of existing patterns with file references, written to tmp file.

Write internal branch output to `tmp/ground-internal-<topic>.md`.

**Branch B — External:**
- Execute web searches using query templates from `references/grounding-criteria.md`
- Evaluate each source: relevant to project context? Actionable methodology? Named framework with structure?
- Extract from surviving sources: framework names, component structures, scoring mechanics, known limitations

Write external branch output to `tmp/ground-external-<topic>.md`.

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

**Branch file retention:** Move internal branch to `plans/reports/` if substantial (>100 lines or >10 file reads). Delete if short brainstorm. Substantial inventories are evidence artifacts supporting the synthesis — needed for audit through the design lifecycle. Delete external branch files (web search results are reproducible).

## Integration Points

**From /design:** Phase A.3-4 (external research) can invoke `/ground` when the design will produce a new methodology or framework as part of its output.

**From ad-hoc work:** Any task producing methodological claims should consider loading this skill. The trigger is claim type (see `references/grounding-criteria.md` for mandatory vs optional criteria).

**Not needed for:** Applying an already-grounded framework to data, project-specific logical analysis, mechanical execution of defined procedures.

## Additional Resources

### Reference Files

For detailed trigger criteria, quality label definitions, parameterization guidance, and templates:
- **`references/grounding-criteria.md`** — Trigger criteria, quality labels, parameter selection, search query templates, convergence template
