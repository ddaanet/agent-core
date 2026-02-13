# Deliverable Review: worktree-update

**Date:** 2026-02-13
**Methodology:** `agents/decisions/deliverable-review.md` (ISO 25010 / IEEE 1012)
**Design reference:** `plans/worktree-update/design.md`

---

## Inventory

| Type | File | Lines |
|------|------|-------|
| Code | `src/claudeutils/worktree/cli.py` | 370 |
| Code | `src/claudeutils/worktree/merge.py` | 290 |
| Code | `src/claudeutils/worktree/utils.py` | 20 |
| Code | `src/claudeutils/worktree/__init__.py` | 1 |
| Test | 12 test files | 2854 |
| Agentic prose | `agent-core/skills/worktree/SKILL.md` | 123 |
| Configuration | `justfile` (wt-* recipes) | ~200 |
| Configuration | `agent-core/justfile` | ~20 |

**Design conformance:** All 8 design decisions (D1-D8) structurally satisfied. 4-phase merge ceremony complete. Exit codes match spec. 22/27 design test requirements covered.

---

## Critical Findings (5)

### C1. `wt-ls` still calls Python CLI (D8 violation)
- **Source:** Prose review #12
- **File:** `justfile:140-141`
- **Design:** D8 — "wt-ls: Replace `claudeutils _worktree ls` call with native bash"
- **Impact:** Last remaining coupling between justfile and Python CLI

### C2. `wt-merge` lacks THEIRS clean tree check (D8 violation)
- **Source:** Prose review #13
- **File:** `justfile:209-222`
- **Design:** D8 — "Both Python merge and justfile `wt-merge` must check both sides"
- **Impact:** Uncommitted worktree changes silently lost on merge

### C3. Missing `setup` recipe in agent-core justfile (D5 violation)
- **Source:** Prose review #16
- **File:** `agent-core/justfile`
- **Design:** D5 — "add `setup` recipe to agent-core justfile"
- **Impact:** Worktree env init silently fails for agent-core-only worktrees

### C4. No precommit failure test
- **Source:** Test review F-01
- **File:** `tests/test_worktree_merge_parent.py`
- **Design:** Phase 4 — "exit 1 with message 'Precommit failed after merge'"
- **Impact:** Specified behavior path with zero coverage. Docstring claims behavior the test body doesn't exercise.

### C5. No merge idempotency test
- **Source:** Test review F-02
- **File:** All merge test files
- **Design:** "Idempotency: re-running after manual fix resumes correctly"
- **Impact:** Recovery workflow untested — the only way to verify merge is safe to retry

---

## Major Findings (10)

### M1. `_filter_section` continuation line handling
- **Source:** Code review F2
- **File:** `cli.py:55-60`
- **Axis:** Functional correctness
- **Detail:** Non-bullet continuation lines of irrelevant entries leak into filtered output. Focused sessions may include irrelevant blocker sub-entries.

### M2. `plan_dir` regex case-sensitive but session.md uses title case
- **Source:** Code review F13
- **File:** `cli.py:73`
- **Axis:** Functional correctness
- **Detail:** `plan:\s*(\S+)` won't match `Plan:` (title case). Falls back to task-name-only filtering, missing plan-directory-referenced entries.

### M3. Mode B dependency analysis too cognitive
- **Source:** Prose review #8
- **File:** `SKILL.md:50-61`
- **Axis:** Determinism
- **Detail:** "mentions" and "ordering hints" are judgment words. Different agents produce different results. Duplicates `#status` parallel detection logic.

### M4. False idempotency claim in SKILL.md
- **Source:** Prose review #11
- **File:** `SKILL.md:119`
- **Axis:** Functional correctness
- **Detail:** Claims merge "detects partial completion and resumes from appropriate phase." No resume logic exists — it's incidental idempotency from git operations.

### M5. No exit code 2 for submodule failure
- **Source:** Test review F-03
- **File:** `tests/test_worktree_merge_validation.py`
- **Axis:** Coverage gap
- **Detail:** Exit code 2 tested for branch-not-found but not submodule failure scenarios.

### M6. test_merge_submodule_ancestry mocks away tested behavior
- **Source:** Test review F-04
- **File:** `tests/test_worktree_merge_submodule.py:15-96`
- **Axis:** Vacuity
- **Detail:** Sets up real git state then replaces `_git` with MagicMock. Assertions check function was called, not that ancestry checking works correctly.

### M7. test_merge_submodule_fetch implementation-coupled
- **Source:** Test review F-05
- **File:** `tests/test_worktree_merge_submodule.py:163-232`
- **Axis:** Independence
- **Detail:** Patches `subprocess.run` globally, tracks specific command patterns. Tests implementation details (specific git commands) not behavioral outcomes.

### M8. commit_file helper duplicated in 3 test files
- **Source:** Test review F-06
- **File:** `test_worktree_merge_parent.py:162`, `test_worktree_merge_conflicts.py:394`, `test_worktree_merge_jobs_conflict.py:141`
- **Axis:** Excess/duplication
- **Detail:** Identical function in 3 files despite existing as fixture in `fixtures_worktree.py`. Maintenance risk from divergent copies.

### M9. No source file conflict cleanup test
- **Source:** Test review F-08
- **File:** `tests/test_worktree_merge_validation.py`
- **Axis:** Coverage gap
- **Detail:** Tests abort happened but not `git clean -fd` debris removal.

### M10. Precommit test docstring claims untested behavior
- **Source:** Test review F-13
- **File:** `tests/test_worktree_merge_parent.py:89-159`
- **Axis:** Vacuity
- **Detail:** Docstring specifies 6 behavioral conditions including failure path. Test body only exercises happy path. Misleading coverage.

---

## Minor Findings (24)

### Code (14)
- `_git()` duplicated across cli.py and merge.py (modularity)
- THEIRS clean check runs on non-existent directory path (robustness — correct by accident)
- `_resolve_learnings_md_conflict` set-based dedup loses ordering context (correctness — matches design literally)
- `_probe_registrations` substring containment vs path matching (robustness)
- `_check_clean_for_merge` exempt_paths substring matching (robustness)
- `clean_tree` vs `_check_clean_for_merge` different parsing strategies (modularity)
- `add_sandbox_dir` no trailing newline (cosmetic)
- `initialize_environment` no warning when `just` unavailable (D5 conformance)
- `_phase4` exit code doesn't distinguish precommit failure from just-not-found (error signaling)
- `_phase3` `git clean -fd` may remove user's untracked files (robustness — F15/F16 interaction)
- `_check_clean_for_merge` uses `--untracked-files=no` inconsistent with `clean_tree` (robustness)
- No test for `focus_session` with continuation-line plan directory (testability)
- `_create_session_commit` tempfile context manager misleading scope (robustness)
- `rm` doesn't delete submodule branch — stale branches accumulate (completeness)

### Tests (5)
- Conditional submodule test silently passes if initialization fails
- No test for `--task` with custom `--session-md` path
- `test_rm_submodule_first_ordering` tests private function not CLI behavior
- No merge+rm integration test
- `_setup_repo_with_submodule` helper duplicated across 2 files

### Prose/Config (5)
- SKILL.md says "three-phase" but merge has four phases
- Mode C step 1 handoff rationale is explanatory prose (density)
- Mode B parallel detection duplicates `#status` logic (excess)
- Mode C amend recovery path may conflict with merge re-run
- `wt-merge` justfile learnings.md resolution is simplified stub
- `wt-merge` justfile unconditional commit may fail with `set -e`

---

## Gap Analysis

| Design Requirement | Status |
|---|---|
| Sibling paths, container detection | ✅ Covered |
| Worktree-based submodule | ✅ Covered |
| Sandbox registration | ✅ Covered |
| Existing branch reuse | ✅ Covered |
| `--task` mode (slug, session, tab output) | ✅ Covered |
| `rm` submodule-first ordering | ✅ Covered |
| Merge Phase 1-3 | ✅ Covered |
| Merge Phase 4 precommit failure | ❌ No test (C4) |
| Merge idempotency | ❌ No test (C5) |
| Merge exit code 2 (submodule) | ❌ No test (M5) |
| Merge cleanup after abort | ❌ No test (M9) |
| Justfile independence (wt-ls) | ❌ Not implemented (C1) |
| Justfile THEIRS clean tree | ❌ Not implemented (C2) |
| Agent-core setup recipe | ❌ Not implemented (C3) |

---

## Summary

| Severity | Count |
|----------|-------|
| Critical | 5 |
| Major | 10 |
| Minor | 24 |

The core Python implementation (cli.py, merge.py, utils.py) is structurally sound — all 8 design decisions satisfied. The 4-phase merge ceremony works correctly for the tested paths. The `focus_session` function has two correctness bugs (M1, M2) affecting filtering quality.

**Three unimplemented design requirements** (C1-C3) are all in Phase 8 non-code artifacts (justfile/config). These are the most straightforward to fix.

**Test gaps** concentrate in merge edge cases — precommit failure, idempotency, submodule exit code 2, and cleanup verification. The submodule merge tests (M6, M7) rely on mocking that defeats their purpose.

**Sub-reports:**
- `plans/worktree-update/reports/deliverable-review-code.md`
- `plans/worktree-update/reports/deliverable-review-tests.md`
- `plans/worktree-update/reports/deliverable-review-prose.md`
