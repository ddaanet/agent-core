# Review Criteria Examples

Violation and correct examples for review-plan criteria.

---

## 1. GREEN Phase Anti-Pattern (CRITICAL) — TDD

**Violation:** GREEN phase contains implementation code

```markdown
**GREEN Phase:**

**Implementation**: Add load_config() function

```python
def load_config(config_path: Path) -> dict:
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config
```
```

**Why this is wrong:**
- Prescribes exact code
- Agent becomes code copier, not implementer
- Test doesn't drive implementation
- Violates TDD RED->GREEN discovery

**Correct approach:**

```markdown
**GREEN Phase:**

**Implementation**: Minimal load_config() to pass tests

**Behavior:**
- Read YAML file from config_path
- Return parsed dict
- Must pass test assertions from RED phase

**Hint**: Use yaml.safe_load(), Path.open()
```

## 3. Implementation Hints vs Prescription — TDD

**Acceptable:** Implementation hints for sequencing

```markdown
**Implementation Hint**: Happy path only - no error handling, no validation
```

**Violation:** Prescriptive code blocks

```python
# This tells agent EXACTLY what to write
def compose(fragments, output):
    # Implementation here
```

## 4. Test Specifications — TDD

**Good example:**
```markdown
**Expected failure:**
```
ImportError: cannot import name 'compose' from 'claudeutils.compose'
```

**Why it fails**: Function doesn't exist yet
```

## 5. Weak RED Phase Assertions (CRITICAL) — TDD

**Indicators (prose format):**
- Prose says "returns correct value" without specifying what value
- Prose says "handles error" without specifying error type/message
- Prose says "processes correctly" without expected output
- No specific values, patterns, or behaviors specified

**Indicators (legacy code format):**
- Test only checks `exit_code == 0` or `exit_code != 0`
- Test only checks key existence (`"KEY" in dict`) without value verification
- Test only checks class/method existence (would pass with `pass` body)
- Test has no mocking for I/O-dependent behavior

**Correct prose pattern:**
- Specific values: "returns string containing medal emoji"
- Specific errors: "raises ValueError with message 'invalid input'"
- Specific structure: "output dict contains 'count' key with integer > 0"
- Mock requirements: "mock keychain, verify get_password called with service='claude'"

## 5.5. Prose Test Quality — TDD

**Indicators of violation:**
- `def test_*():` pattern in RED phase code block
- `assert` statements in code blocks (not in prose)
- Complete test function with imports and fixtures

**Acceptable in RED:**
- Prose test descriptions with specific assertions
- Expected failure message/pattern (in code block OK)
- Fixture setup hints (prose, not code)

## 10.5. Inline Phase Review

**10.5.1 Vacuity (instruction specificity)**
- Each instruction must name a concrete target (file path) and operation
- Bad: "Update pipeline-contracts.md"
- Good: "Add inline type row to the type table in pipeline-contracts.md"

**10.5.2 Density (verifiable outcome)**
- Outcome must be unambiguous — completion is binary, not a judgment call
- Bad: "Improve the error handling section"
- Good: "Add 'inline' to the valid_types list in parse_frontmatter()"
