# Hook Testing Agent

**Purpose:** Test PreToolUse hooks to prevent regressions.

**Prerequisites:**
- If hooks were just modified, restart Claude Code session before testing
- Working directory must be project root

---

## Test Procedure

Execute each test case sequentially. Record results in `agent-core/hooks/test-results.md`.

### Test 1: Block /tmp writes

**Objective:** Verify pretooluse-block-tmp.sh blocks writes to /tmp/

**Action:**
```
Write tool: /tmp/test-file.txt
Content: "This should be blocked"
```

**Expected outcome:**
- **Hook behavior:** Blocks operation (permissionDecision: deny)
- **System message:** "🚫 **BLOCKED: Do not write to /tmp/. Use project-local tmp/ instead.**"
- **Tool execution:** Write tool does NOT execute

**Actual outcome:** [AGENT FILLS IN]

---

### Test 2: Allow project tmp/ writes

**Objective:** Verify pretooluse-block-tmp.sh allows writes to project tmp/

**Action:**
```
Write tool: tmp/test-file.txt
Content: "This should be allowed"
```

**Expected outcome:**
- **Hook behavior:** Allows operation (no warning)
- **System message:** None
- **Tool execution:** Write tool executes successfully, file created at tmp/test-file.txt

**Actual outcome:** [AGENT FILLS IN]

**Cleanup:**
```bash
rm -f tmp/test-file.txt
```

---

### Test 3: Warn on non-root cwd (any command)

**Objective:** Verify submodule-safety.py warns when cwd != project root

**Action:**
```bash
cd agent-core && pwd
```

**Expected outcome:**
- **Hook behavior:** Warns (non-blocking)
- **System message contains:** "⚠️  Working directory is not project root: agent-core" and "After this command, consider returning to project root."
- **Tool execution:** Bash tool executes (warning is non-blocking)

**Actual outcome:** [AGENT FILLS IN]

**Cleanup:**
```bash
cd "$CLAUDE_PROJECT_DIR"
```

---

### Test 4: Warn on git operation referencing submodule

**Objective:** Verify submodule-safety.py warns when git operation references submodule path from project root

**Setup:**
```bash
# Ensure at project root
pwd  # Should show project root path
```

**Action:**
```bash
git status agent-core/
```

**Expected outcome:**
- **Hook behavior:** Warns (non-blocking)
- **System message contains:** "⚠️  Git operation references 'agent-core/' from project root." and "Consider: (cd agent-core && git ...) to avoid path confusion."
- **Tool execution:** Bash tool executes (warning is non-blocking)

**Actual outcome:** [AGENT FILLS IN]

---

### Test 5: No warning at project root

**Objective:** Verify submodule-safety.py does NOT warn for commands at project root (that don't reference submodules)

**Setup:**
```bash
# Ensure at project root
pwd  # Should show project root path
```

**Action:**
```bash
ls -la
```

**Expected outcome:**
- **Hook behavior:** Suppresses output (suppressOutput: true, no warning)
- **System message:** None
- **Tool execution:** Bash tool executes normally

**Actual outcome:** [AGENT FILLS IN]

---

### Test 6: Block /private/tmp writes

**Objective:** Verify pretooluse-block-tmp.sh blocks writes to /private/tmp/ (macOS symlink)

**Action:**
```
Write tool: /private/tmp/test-file.txt
Content: "This should be blocked"
```

**Expected outcome:**
- **Hook behavior:** Blocks operation (permissionDecision: deny)
- **System message:** "🚫 **BLOCKED: Do not write to /tmp/. Use project-local tmp/ instead.**"
- **Tool execution:** Write tool does NOT execute

**Actual outcome:** [AGENT FILLS IN]

---

### Test 7: Subshell pattern preserves cwd

**Objective:** Verify subshell pattern works as suggested in hook warnings

**Setup:**
```bash
# Ensure at project root
pwd  # Should show project root
```

**Action:**
```bash
(cd agent-core && pwd) && pwd
```

**Expected outcome:**
- **Hook behavior:** Warns on cd inside subshell, suppresses on second pwd
- **System message:** First command gets warning about non-root cwd; second command gets no message
- **Tool execution:** Both commands execute; second pwd shows project root (cwd preserved)

**Actual outcome:** [AGENT FILLS IN]

---

### Test 8: False positive - commit message containing submodule name

**Objective:** Verify hook warns on git commit messages containing "agent-core" (known limitation)

**Setup:**
```bash
# Ensure at project root
pwd  # Should show project root
```

**Action:**
```bash
git commit --allow-empty -m "Update agent-core documentation"
```

**Expected outcome:**
- **Hook behavior:** Warns (false positive - commit message contains "agent-core" keyword)
- **System message contains:** "⚠️  Git operation references 'agent-core/' from project root."
- **Tool execution:** Bash tool executes (warning is non-blocking), commit succeeds

**Actual outcome:** [AGENT FILLS IN]

**Note:** This is a known limitation. The hook uses regex `\bagent-core\b` which matches word boundaries but cannot distinguish between paths and commit message content.

---

### Test 9: Multiple submodule references

**Objective:** Verify hook detects multiple submodules in single command

**Setup:**
```bash
# Ensure at project root
pwd  # Should show project root
```

**Action:**
```bash
git diff agent-core/ pytest-md/
```

**Expected outcome:**
- **Hook behavior:** Warns for BOTH submodules (non-blocking)
- **System message contains:** Two warnings (one for agent-core, one for pytest-md), both suggesting subshell pattern
- **Tool execution:** Bash tool executes (warning is non-blocking)

**Actual outcome:** [AGENT FILLS IN]

---

### Test 10: Empty command robustness

**Objective:** Verify submodule-safety.py handles empty Bash commands gracefully

**Action:**
```bash
# Empty command (edge case)
true
```

**Expected outcome:**
- **Hook behavior:** Suppresses output (suppressOutput: true, no warning at project root)
- **System message:** None
- **Tool execution:** Bash tool executes normally

**Actual outcome:** [AGENT FILLS IN]

---

## Hook Matcher Mutual Exclusivity

**Note:** The two hooks configured in hooks.json have mutually exclusive matchers:
- `pretooluse-block-tmp.sh`: Matches "Write" tool only
- `submodule-safety.py`: Matches "Bash" tool only

Since no tool call can be both Write AND Bash simultaneously, these hooks never interact. Hook interaction testing is not applicable.

**Implication:** Each test case triggers at most one hook. There are no multi-hook scenarios to test.

---

## Test Results Template

Create `tmp/hook-test-results-[timestamp].md` with this structure:

```markdown
# Hook Test Results

**Date:** [TIMESTAMP]
**Session ID:** [SESSION_ID]
**Hooks Version:** [GIT COMMIT HASH]

## Test 1: Block /tmp writes
- Status: ✅ PASS / ❌ FAIL
- Notes: [any deviations or observations]

## Test 2: Allow project tmp/ writes
- Status: ✅ PASS / ❌ FAIL
- Notes: [any deviations or observations]

## Test 3: Warn on non-root cwd
- Status: ✅ PASS / ❌ FAIL
- Notes: [any deviations or observations]

## Test 4: Warn on git operation referencing submodule
- Status: ✅ PASS / ❌ FAIL
- Notes: [any deviations or observations]

## Test 5: No warning at project root
- Status: ✅ PASS / ❌ FAIL
- Notes: [any deviations or observations]

## Test 6: Block /private/tmp writes
- Status: ✅ PASS / ❌ FAIL
- Notes: [any deviations or observations]

## Test 7: Subshell pattern preserves cwd
- Status: ✅ PASS / ❌ FAIL
- Notes: [any deviations or observations]

## Test 8: False positive - commit message
- Status: ✅ PASS / ❌ FAIL
- Notes: [expected false positive behavior]

## Test 9: Multiple submodule references
- Status: ✅ PASS / ❌ FAIL
- Notes: [any deviations or observations]

## Test 10: Empty command robustness
- Status: ✅ PASS / ❌ FAIL
- Notes: [any deviations or observations]

## Summary
- Total tests: 10
- Passed: X
- Failed: Y
- Regression risk: [HIGH/MEDIUM/LOW]
```

---

## Execution Instructions

**For agent executing this procedure:**

1. Read this file completely before starting
2. Execute tests in order (1-10)
3. Record each result immediately after test execution
4. Include actual hook output in notes if it deviates from expected
5. If ANY test fails, STOP and report to user immediately
6. After all tests complete, write summary to `tmp/hook-test-results-[timestamp].md`
7. Report final status to user with file path

**Note:** Hook modifications require session restart. If hooks were just modified, instruct user to restart Claude Code before running tests.
