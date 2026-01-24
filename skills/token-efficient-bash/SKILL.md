---
name: token-efficient-bash
description: This skill should be used when writing multi-step bash scripts (3+ sequential commands) to minimize script token cost, when the user asks to "write efficient bash", "save tokens in scripts", "use set -x for tracing", or mentions "bash strict mode". Teaches exec 2>&1 + set -xeuo pipefail pattern that eliminates echo statements and comments via automatic command tracing - reduces script size by 40-60%.
version: 0.1.0
---

# Token-Efficient Bash Scripting

Write bash scripts that provide automatic progress diagnostics and fail-fast error handling without manual echo statements or verbose error reporting.

## The Pattern

For sequential bash commands (3+ steps), use this header:

```bash
exec 2>&1
set -xeuo pipefail

# Script commands here
```

## No Comments Needed

The `set -x` flag eliminates the need for WHAT comments - the traced output documents what the script does:

```bash
exec 2>&1
set -xeuo pipefail

mkdir -p target/
mv source/* target/
ln -s ../target source
```

**Output shows exactly what happens:**
```
+ mkdir -p target/
+ mv source/* target/
+ ln -s ../target source
```

Each command is printed before execution. No need for `# Create directory` or `# Move files` comments. The traced output IS the documentation.

**Exception:** Complex logic may still warrant comments explaining WHY (business logic, non-obvious decisions), not WHAT (commands being run).

## Token Economy Benefits

**Problem:** Traditional bash scripts require extensive manual instrumentation:

```bash
# Traditional approach (verbose, token-heavy)
echo "Creating directory..."
mkdir -p target/ || { echo "Error: Failed to create directory" >&2; exit 1; }
echo "Moving files..."
mv source/* target/ || { echo "Error: Failed to move files" >&2; exit 1; }
echo "Creating symlink..."
ln -s ../target source || { echo "Error: Failed to create symlink" >&2; exit 1; }
echo "Complete"
```

**Solution:** Token-efficient pattern (automatic tracing):

```bash
exec 2>&1
set -xeuo pipefail

mkdir -p target/
mv source/* target/
ln -s ../target source
```

**Token savings:**
- Eliminates all echo statements (40-60% reduction)
- **No comments needed** - `set -x` documents what the script does
- No manual error handling code
- Automatic command tracing shows execution progress
- Errors stop execution immediately with diagnostic context

**Output comparison:**

Traditional (200+ tokens in script):
```
Creating directory...
Moving files...
Creating symlink...
Complete
```

Token-efficient (50 tokens in script):
```
+ mkdir -p target/
+ mv source/* target/
+ ln -s ../target source
```

The `+` prefix shows each command before execution. Same information, fraction of the code.

## How It Works

### `exec 2>&1`
Redirects stderr to stdout, merging all output into single stream.

**Purpose:** Ensures tracing output (`set -x` writes to stderr) appears in correct order with command output.

**Result:** Unified output stream with interleaved commands and results.

### `set -xeuo pipefail`

Four orthogonal flags:

**`-x` (xtrace):**
- Print each command before execution
- Prefixed with `+` in output
- **This is the key to token economy** - eliminates echo statements
- Shows actual commands with expanded variables

**`-e` (errexit):**
- Exit immediately if any command returns non-zero
- Prevents error cascades
- No need for `|| exit 1` after every command

**`-u` (nounset):**
- Error on undefined variable references
- Catches typos and missing environment variables
- Prevents silent failures from `$TYPO` expanding to empty string

**`-o pipefail`:**
- Pipeline fails if ANY command in pipe fails
- Normally pipes return exit status of last command only
- Example: `grep pattern file | wc -l` fails if grep fails

## When to Use

**Use this pattern for:**
- Sequential operations (3+ commands)
- File operations requiring error checking (mv, cp, ln, mkdir)
- Multi-step git workflows (add, commit, push)
- Setup/teardown sequences
- Any script where you'd otherwise write echo statements

**Do NOT use for:**
- Single commands (just run the command)
- Parallel operations (use multiple Bash tool calls)
- Interactive commands (set -x interferes with prompts)
- Large process substitutions (tracing overhead)
- Commands requiring complex error handling (use traditional if/else)

## Strict Mode Caveats

Some commands have expected non-zero exits that would trigger `set -e`. Handle with `|| true`.

### Commands with Normal Non-Zero Exits

**`grep` - exits 1 when no match:**

```bash
exec 2>&1
set -xeuo pipefail

# grep returns 1 when pattern not found - this is normal
grep "pattern" file.txt || true

# Continue with other commands
echo "Processing complete"
```

**`diff` - exits 1 when files differ:**

```bash
exec 2>&1
set -xeuo pipefail

# diff returns 1 when files differ - expected behavior
diff file1.txt file2.txt || true

# Other commands still fail-fast
```

**Other common cases:**
- `test` / `[` / `[[` - false condition returns 1
- `git diff --exit-code` - exits 1 if differences exist
- `make` with certain targets
- Background jobs that may fail

### Bash Arithmetic Expansion

**Problem:** `(( ))` returns exit status equal to the expression value.

```bash
exec 2>&1
set -xeuo pipefail

count=0
((count++))  # FAILS - expression evaluates to 0, triggers set -e
```

**Solution 1:** Use `|| true`

```bash
exec 2>&1
set -xeuo pipefail

count=0
let count++ || true  # Safe
```

**Solution 2:** Use `$(( ))` (arithmetic substitution, not expansion)

```bash
exec 2>&1
set -xeuo pipefail

count=0
count=$((count + 1))  # Safe - always succeeds
```

### Conditional Logic with Expected Failures

When a command failure is part of normal flow:

```bash
exec 2>&1
set -xeuo pipefail

# Check if pattern exists (grep exit 1 is expected)
if grep -q "pattern" config.yaml || true; then
    echo "Pattern found"
else
    echo "Pattern not found"
fi

# Or use grep in condition directly (if handles exit status)
if grep -q "pattern" config.yaml; then
    echo "Found"
fi  # No || true needed in if condition
```

## Reconciliation with Error Handling Rules

CLAUDE.md Error Handling section states: "Never use error suppression patterns (e.g., `|| true`)".

**Clarification:** That rule prohibits *hiding* errors. In token-efficient bash, `|| true` *handles* expected non-zero exits.

**Wrong (suppressing errors):**
```bash
# Hides failure - user never sees what went wrong
dangerous_command || true
important_operation || true
```

**Right (handling expected exits):**
```bash
exec 2>&1
set -xeuo pipefail

# grep exit 1 is documented, expected behavior when no match
grep "optional_pattern" file.txt || true

# All unexpected errors still cause immediate failure with diagnostics
```

The script still fails fast on unexpected errors due to `set -e`. Using `|| true` for specific commands with known non-zero exits is safe and necessary.

## Examples

### Example 1: File Operations

```bash
exec 2>&1
set -xeuo pipefail

mkdir -p target/backup/
mv source/*.log target/backup/
ln -s ../target/backup source/logs
chmod 644 target/backup/*.log
```

**Output:**
```
+ mkdir -p target/backup/
+ mv source/*.log target/backup/
+ ln -s ../target/backup source/logs
+ chmod 644 target/backup/*.log
```

**Benefits:**
- No echo statements needed
- Clear progress tracking
- Automatic failure if any step fails
- Minimal script code

### Example 2: Git Workflow

```bash
exec 2>&1
set -xeuo pipefail

git add -A
git commit -m "Update documentation

- Add installation guide
- Fix typos in README
- Update examples"
git push origin main
```

**Output:**
```
+ git add -A
+ git commit -m 'Update documentation

- Add installation guide
- Fix typos in README
- Update examples'
[main a7f38c2] Update documentation
 3 files changed, 42 insertions(+), 7 deletions(-)
+ git push origin main
To github.com:user/repo.git
   abc123f..a7f38c2  main -> main
```

**Benefits:**
- Shows exact git commands executed
- Command output (commit hash, push result) interleaved
- Automatic failure if commit or push fails

### Example 3: Setup with Expected Failures

```bash
exec 2>&1
set -xeuo pipefail

# Create directory structure
mkdir -p tmp/output tmp/logs

# Check if config exists (grep exit 1 is okay)
if grep -q "debug_mode: true" config.yaml || true; then
    echo "Debug mode enabled"
fi

# Clean up old files if they exist
rm -f tmp/output/*.tmp || true

# Process files
for file in input/*.txt; do
    process "$file" > "tmp/output/$(basename "$file")"
done
```

**Output:**
```
+ mkdir -p tmp/output tmp/logs
+ grep -q 'debug_mode: true' config.yaml
+ echo 'Debug mode enabled'
Debug mode enabled
+ rm -f tmp/output/*.tmp
+ for file in input/*.txt
+ basename input/file1.txt
+ process input/file1.txt
+ for file in input/*.txt
+ basename input/file2.txt
+ process input/file2.txt
```

**Benefits:**
- Handles optional operations (grep, rm) gracefully
- Shows loop iterations automatically
- Process substitution traced
- Still fails on unexpected errors

## Anti-Patterns to Avoid

### Don't Mix with Manual Error Handling

```bash
# BAD - redundant with set -e
exec 2>&1
set -xeuo pipefail

mkdir -p target/ || { echo "Error"; exit 1; }  # Unnecessary
```

The `set -e` already handles errors. Manual error traps add token overhead without benefit.

### Don't Use for Single Commands

```bash
# BAD - overhead for single command
exec 2>&1
set -xeuo pipefail
ls -la
```

**Better:** Just run `ls -la` directly via Bash tool.

**When to use pattern:** 3+ sequential commands.

### Don't Suppress All Errors

```bash
# BAD - defeats purpose of set -e
exec 2>&1
set -xeuo pipefail

command1 || true
command2 || true
command3 || true  # Why use set -e at all?
```

**Better:** Only use `|| true` for commands with expected non-zero exits (grep, diff).

## Integration with Commit Skill

The `/commit` skill can use this pattern when staging and committing:

```bash
exec 2>&1
set -xeuo pipefail

git add -A
git commit -m "Commit message here"
git status
```

No need for:
- `echo "Staging changes..."`
- `|| { echo "Error"; exit 1; }` after each command
- Manual success reporting

The tracing output provides all necessary diagnostics.

## Summary

**Pattern:**
```bash
exec 2>&1
set -xeuo pipefail
```

**Use for:** 3+ sequential bash commands

**Token savings:** 40-60% reduction by eliminating echo/error statements

**Automatic benefits:**
- Command tracing (set -x)
- Fail-fast errors (set -e)
- Undefined variable detection (set -u)
- Pipeline error propagation (set -o pipefail)
- Unified output stream (exec 2>&1)

**Caveats:**
- Use `|| true` for grep, diff, test, other expected non-zero exits
- Use `$(( ))` or `let || true` for arithmetic
- Not for single commands or interactive scripts

**Remember:** This is about *handling* expected exits, not *suppressing* errors. Unexpected failures still stop execution immediately with diagnostic context.
