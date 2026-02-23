# Anti-Patterns to Avoid

Common mistakes in runbook creation and how to fix them.

## TDD Anti-Patterns

---

| Anti-Pattern | Bad Example | Good Example |
|--------------|-------------|--------------|
| **Setup-only cycles** | `Cycle 1.1: Create test fixture` (no test, just fixture) | `Cycle 1.1: Test fixture works correctly` - RED: Fixture doesn't exist, GREEN: Create fixture, Verify: Fixture behaves as expected |
| **God cycles** | `Cycle 2.1: Implement entire auth system` - Tests login + logout + token refresh + password reset + 2FA | Split: `2.1: Basic login`, `2.2: Logout`, `2.3: Token refresh`, `2.4: Password reset`, `2.5: 2FA` |
| **Unclear RED** | `Expected failure: Something will fail` | `Expected failure: ModuleNotFoundError: No module named 'auth'` + Why: Auth module not created yet |
| **Missing regression** | `Verify GREEN: pytest tests/test_new.py` (stops here) | `Verify GREEN: pytest tests/test_new.py` (must pass) + `Verify no regression: pytest tests/` (all existing tests pass) |
| **Coupled cycles** | `3.1: Modify shared state`, `3.2: Test that state was modified` (implicit dependency) | `3.1: Test state modification [sets up state]`, `3.2: Test state query [DEPENDS: 3.1]` - Explicit dependency, clear order |
| **Presentation tests** | `Cycle 1.1: Test help text contains "recursively"` - RED: Word not in help, GREEN: Add word to help | Skip cycle entirely. Help text is presentation, not behavior. Test that `--recursive` flag works, not that help mentions it. |
| **Weak RED assertions** | `assert result.exit_code == 0` (passes with stub) | Mock filesystem/keychain, assert output content: `assert "Mode: plan" in result.output` |
| **Missing integration cycles** | Components created in isolation, no wiring cycle | Integration cycle exercising production call path: `Cycle 3.16: Wire providers to keychain` with real subprocesses; mocks only for error injection (see Testing Strategy in SKILL.md) |
| **Empty-first ordering** | Cycle 1: "empty list returns []" → stub committed | Start with simplest happy path. Only test empty case if it requires special handling. |
| **Split prose edits across cycles** | `Cycle 3.1: Update section A of SKILL.md`, `Cycle 3.4: Update section B of SKILL.md` — same file split across cycles | All edits to a prose artifact in one cycle. Prose has no automated tests; editor context is the only quality lever. Fragmenting context degrades quality. |
| **Unit-test-only coverage** | All cycles test individual functions; no cycle exercises the production call path | Plan integration test cycles first. Unit cycles supplement for combinatorial or edge-case coverage only. See Testing Strategy in SKILL.md. |
| **Mocked subprocess when real is fast** | `mock.patch("subprocess.run")` for git/CLI operations completing in milliseconds with `tmp_path` fixtures | Use real subprocesses in `tmp_path`. Mocks only for error injection (lock files, permission errors). See Testing Strategy in SKILL.md. |

---

## General Step Anti-Patterns

| Anti-Pattern | Bad Example | Correct Pattern |
|--------------|-------------|-----------------|
| **Missing investigation prerequisite** | `Step 2.1: Create new taxonomy file` with no prerequisite reads | Add prerequisite: `Read existing-taxonomy.md (understand current structure and naming conventions)` |
| **Vague success criteria** | Expected Outcome: "Analysis complete" | Expected Outcome: "Analysis has 6 sections covering each status code, with line number references to source" |
| **Structure-only validation** | Expected Outcome: "File has 3 sections" (ignores content quality) | Expected Outcome: "Each section defines detection criteria with concrete heuristics and at least one example" |
| **Missing Expected Outcome** | Step lists Implementation but no Expected Outcome section | Every step needs Expected Outcome with verifiable statements about post-step state |
| **Ambiguous Error Conditions** | Error Conditions: "If something goes wrong, fix it" | Error Conditions: "If target section not found -> Grep file for heading variants, update section name in step" |
| **Downstream reference in bootstrapping** | "Apply same criteria as outline-corrector" (agent not yet updated) | "Apply criteria from review-plan skill Section 11" (upstream source where criteria are defined) |
| **Self-modification without expand/contract** | Step modifies pipeline artifact (skill, executor, review agent) and later step uses the modified tool without compatibility consideration | When modifying a tool used by later steps: apply improvement completely first (bootstrapping ordering), or use expand/contract — forward-compatible edit, transition, remove backward compatibility. |

---
