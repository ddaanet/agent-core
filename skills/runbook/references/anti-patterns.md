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
| **Missing integration cycles** | Components created in isolation, no wiring cycle | Explicit integration cycle: `Cycle 3.16: Wire providers to keychain` with mocked I/O |
| **Empty-first ordering** | Cycle 1: "empty list returns []" → stub committed | Start with simplest happy path. Only test empty case if it requires special handling. |

---

## General Step Anti-Patterns

| Anti-Pattern | Bad Example | Correct Pattern |
|--------------|-------------|-----------------|
| **Missing investigation prerequisite** | `Step 2.1: Create new taxonomy file` with no prerequisite reads | Add prerequisite: `Read existing-taxonomy.md (understand current structure and naming conventions)` |
| **Vague success criteria** | Expected Outcome: "Analysis complete" | Expected Outcome: "Analysis has 6 sections covering each status code, with line number references to source" |
| **Structure-only validation** | Expected Outcome: "File has 3 sections" (ignores content quality) | Expected Outcome: "Each section defines detection criteria with concrete heuristics and at least one example" |
| **Missing Expected Outcome** | Step lists Implementation but no Expected Outcome section | Every step needs Expected Outcome with verifiable statements about post-step state |
| **Ambiguous Error Conditions** | Error Conditions: "If something goes wrong, fix it" | Error Conditions: "If target section not found -> Grep file for heading variants, update section name in step" |
| **Downstream reference in bootstrapping** | "Apply same criteria as outline-review-agent" (agent not yet updated) | "Apply criteria from runbook-review.md" (upstream source where criteria are defined) |

---
