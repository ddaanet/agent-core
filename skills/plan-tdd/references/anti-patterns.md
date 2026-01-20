# Anti-Patterns to Avoid

This document catalogs common mistakes in TDD runbook creation and how to fix them.

---

## Anti-Pattern 1: Setup-Only Cycles

❌ **Bad:**
```
Cycle 1.1: Create test fixture (no test, just fixture code)
```

✅ **Good:**
```
Cycle 1.1: Test fixture works correctly
- RED: Fixture doesn't exist
- GREEN: Create fixture
- Verify: Fixture behaves as expected
```

---

## Anti-Pattern 2: God Cycles

❌ **Bad:**
```
Cycle 2.1: Implement entire authentication system
- Test login works
- Test logout works
- Test token refresh works
- Test password reset works
- Test 2FA works
```

✅ **Good:**
```
Cycle 2.1: Test basic login
Cycle 2.2: Test logout
Cycle 2.3: Test token refresh
Cycle 2.4: Test password reset
Cycle 2.5: Test 2FA
```

---

## Anti-Pattern 3: Unclear RED Expectations

❌ **Bad:**
```
**Expected failure:** Something will fail
```

✅ **Good:**
```
**Expected failure:**
```
ModuleNotFoundError: No module named 'auth'
```

**Why it fails:** Auth module not created yet
```

---

## Anti-Pattern 4: Missing Regression Verification

❌ **Bad:**
```
**Verify GREEN:** Run pytest tests/test_new.py
```

✅ **Good:**
```
**Verify GREEN:** Run pytest tests/test_new.py
- Must pass

**Verify no regression:** Run pytest tests/
- All existing tests must pass
```

---

## Anti-Pattern 5: Coupled Cycles

❌ **Bad:**
```
Cycle 3.1: Modify shared state
Cycle 3.2: Test that shared state was modified (implicit dependency)
```

✅ **Good:**
```
Cycle 3.1: Test state modification [sets up state]
Cycle 3.2: Test state query [DEPENDS: 3.1]
- Explicit dependency
- Clear execution order
```

---
