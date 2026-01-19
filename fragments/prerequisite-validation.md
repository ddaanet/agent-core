## Prerequisite Validation for Plans

Prerequisite validation catches ~80% of escalation-triggering errors before execution starts. Validation happens in two phases: during planning (recommended) and during execution (defensive).

### When to Validate

**Planning Phase (RECOMMENDED):**
- **When:** During plan review by sonnet, before execution starts
- **Benefit:** Catches prerequisite failures before agents run
- **Cost:** ~15 minutes planning time saves 1+ escalation cycles
- **Impact:** Prevents ~80% of execution-time prerequisite failures

**Execution Phase (DEFENSIVE):**
- **When:** If planning validation missed an issue, or if prerequisites are dynamic
- **Benefit:** Final safety check before expensive operations
- **Cost:** Agent reports error, orchestrator escalates to sonnet
- **Impact:** Limits damage, forces escalation for recovery

### Validation Checklist (4 Categories)

#### 1. File Resources

**What to check:** All files referenced in plan steps

**Validation methods:**

```bash
# Method 1: Bash file check (quick, planning phase)
test -f /absolute/path/to/file
echo "✓ File exists" or "✗ File missing"

# Method 2: Read tool (execution phase, detailed)
# Use Read tool to actually open file
# If Read fails, file doesn't exist or isn't readable

# Method 3: Size check (verification)
test -s /path/to/file  # True if file exists and has size > 0
```

**Example from Phase 2:**
```
File: /Users/david/code/pytest-md/AGENTS.md
Validation: ✓ File exists (152 lines)
Verification: Read tool successfully opened file
Status: READY
```

**Common pitfalls:**
- Using relative paths without verifying working directory
- Assuming file exists because it's in source control (might not be checked out)
- Not checking file read permissions (exists ≠ readable)
- Checking symlink target instead of symlink itself

#### 2. Directory Resources

**What to check:** All directories where files will be created or searched

**Validation methods:**

```bash
# Method 1: Bash directory check
test -d /absolute/path/to/dir
echo "✓ Directory exists" or "✗ Directory missing"

# Method 2: Glob tool (execution phase, discover resources)
# Use Glob to list files in directory
# If Glob returns empty, directory doesn't have expected resources

# Method 3: Write permission check
test -w /path/to/dir  # True if directory is writable
```

**Example validation:**
```
Directory: /Users/david/code/agent-core/fragments/
Expected: Directory exists and is writable for new fragments
Validation: ✓ Directory exists, ✓ Writable, ✓ Contains 10 existing fragments
Status: READY
```

**Common pitfalls:**
- Not verifying directory is writable (not just readable)
- Assuming nested directories exist without explicit check
- Not checking available disk space for large operations
- Using relative directory paths without setting working directory first

#### 3. External Dependencies

**What to check:** External tools, services, or resources required by plan

**Validation methods:**

```bash
# Method 1: Command existence check (planning phase)
which python || echo "✗ Python not found"
python --version

# Method 2: Service availability check
curl -s https://api.example.com/health | grep -q "ok"

# Method 3: Import/module check (for programming tasks)
python -c "import module_name" 2>/dev/null || echo "✗ Module missing"
```

**Example validation checklist:**
```
Dependency: Python 3.8+
Validation: python3 --version → Python 3.11.7 ✓

Dependency: Git with main branch available
Validation: git branch -a | grep -q main ✓

Dependency: External API (GitHub)
Validation: ping api.github.com → success ✓
```

**Common pitfalls:**
- Not checking version (tool exists but wrong version)
- Assuming tool in PATH without explicit check
- Not verifying access credentials for external services
- Not checking network connectivity for remote resources
- Assuming tool behaves same way across OS versions

#### 4. Environment

**What to check:** Environment variables, configuration, working directory state

**Validation methods:**

```bash
# Method 1: Environment variable check
test -n "$MY_VAR" || echo "✗ Environment variable MY_VAR not set"

# Method 2: Working directory state
pwd  # Verify current directory is as expected
ls -la  # Check for expected files/structure

# Method 3: Configuration validation
test -f ~/.config/myapp/config.json || echo "✗ Config missing"
```

**Example validation:**
```
Environment Variable: PROJECT_ROOT
Validation: test -n "$PROJECT_ROOT" ✓
Value: /Users/david/code/agent-core

Working Directory: Must be project root
Current: /Users/david/code/agent-core ✓

Configuration: .claude/settings.json
Status: ✓ Exists and readable
```

**Common pitfalls:**
- Not setting expected environment variables
- Assuming working directory is correct
- Not validating configuration file format (existence ≠ validity)
- Using hardcoded paths instead of environment-relative paths
- Not checking timezone or locale when relevant

### Integration with Planning Phase

When planning agent creates a plan:

1. **Add Prerequisite Section** to plan metadata:
```markdown
## Weak Orchestrator Metadata

**Prerequisites**:
- [Resource 1] (✓ verified via [method])
- [Resource 2] (path: /absolute/path/to/resource)
- [Environment] (✓ verified)
```

2. **Include Verification Method** for each prerequisite:
```markdown
**Prerequisites**:
- File: /Users/david/code/pytest-md/AGENTS.md
  Verified: ✓ Read tool (152 lines)

- Directory: /Users/david/code/agent-core/fragments/
  Verified: ✓ Bash check (exists, writable)

- External: Python 3.8+
  Verified: ✓ python3 --version → 3.11.7
```

3. **Plan Review includes prerequisite check**:
```
Review prompt to sonnet:
"Review prerequisites in plan metadata.
Verify all files, directories, and external dependencies exist.
Report any missing prerequisites before execution starts."
```

### Common Pitfalls and Prevention

| Pitfall | Symptom | Prevention |
|---------|---------|-----------|
| Relative paths used | Different working directories cause failures | Always use absolute paths; verify with `pwd` in plan |
| Assumptions not verified | File exists in source control but not checked out | Use Read or Glob tool; verify actual filesystem state |
| Version mismatches | Tool exists but wrong version causes errors | Check version explicitly (e.g., `python --version`) |
| Permission issues | File exists but not readable/writable | Check with `test -r` / `test -w` during planning |
| Network assumptions | External service assumed available | Test connectivity; include timeout/retry in plan |
| Timing/dependencies | Resource not yet created when plan runs | Document plan order; verify resource creation before use |

### Phase 2 Lesson: File Path Mismatch

**What happened:**
- Step 2.3 referenced `/Users/david/code/pytest-md/CLAUDE.md`
- Plan author assumed file existed at that path
- No validation performed during planning
- During execution, Read tool failed with "file not found"
- Error escalated to sonnet, sonnet diagnosed: correct file is AGENTS.md
- Step had to be re-executed with corrected path

**Impact:**
- One escalation cycle required
- Sonnet time spent on diagnostic instead of forward progress
- Could have been prevented with 30-second Bash check during planning

**Prevention:**
```bash
# Add to plan review checklist:
test -f /Users/david/code/pytest-md/CLAUDE.md || \
  echo "✗ CLAUDE.md not found - check actual filename"

# Output would show: ✗ CLAUDE.md not found
# Trigger follow-up: "What's the actual filename?"
# Response: "AGENTS.md"
# Result: Plan updated before execution, zero escalations
```

### Validation as Part of Task Agent Responsibility

**When task agents validate prerequisites:**

1. **Read phase:** Use Read tool to verify files exist and are readable
2. **Glob phase:** Use Glob to verify directory structure matches expectations
3. **Plan context:** Re-read plan prerequisites section before starting step
4. **Stop on validation failure:** If prerequisite check fails, report immediately (don't continue)

**Task agent error message format:**
```
"Error: Prerequisite validation failed - [resource] not found at [path]
 Expected: [what should be there]
 Actual: [what was found]
 Escalating to sonnet for diagnostic."
```

This enables orchestrator to route error to sonnet for diagnosis and correction.
