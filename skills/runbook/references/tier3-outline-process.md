## Planning Process (Tier 3 Only)

**Full process detail:** Read `references/tier3-planning-process.md` for Phases 0.5-3.5 (discovery, outline generation, consolidation gates, simplification, complexity check, sufficiency check, phase-by-phase expansion, assembly, holistic review, user validation, pre-execution validation).

**Process overview:**
- Phase 0.5: Discover codebase structure, augment recall artifact, verify file locations
- Phase 0.75: Generate runbook outline with quality verification and corrector review
- Phase 0.85: Consolidation gate — merge trivial phases with adjacent complexity
- Phase 0.86: Simplification pass — delegate to `runbook-simplifier`
- Phase 0.9: Complexity check with callback mechanism
- Phase 0.95: Outline sufficiency check (lightweight orchestration exit if `## Execution Model` present)
- Phase 1: Phase-by-phase expansion with per-phase type-aware review
- Phase 2: Assembly validation and metadata preparation
- Phase 2.5: Consolidation gate — merge isolated trivial items post-assembly
- Phase 3: Final holistic cross-phase review via `runbook-corrector`
- Phase 3.25: User validation via `/proof` — systemic defect detection on expanded phase files
- Phase 3.5: Pre-execution validation via `validate-runbook.py`
- Phase 4: Prepare artifacts and handoff

**TDD cycle planning:** When expanding TDD phases in Phase 1, Read `references/tdd-cycle-planning.md` for RED/GREEN specification formats, assertion quality requirements, cycle numbering, investigation prerequisites, dependency assignment, and stop conditions.

**Conformance validation:** When design includes external references, Read `references/conformance-validation.md` for mandatory validation item requirements.

When past outline sufficiency (Phase 0.95), Read `references/tier3-expansion-process.md` for Phase 4 (artifact preparation), checkpoints, testing strategy, and runbook template structure.
