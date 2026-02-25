# Anti-Patterns

Common mistakes when using the token-efficient bash pattern.

## Don't Mix with Manual Error Handling

```bash
# BAD - redundant manual error handling
exec 2>&1
set -xeuo pipefail

mkdir -p target/ || { echo "Error"; exit 1; }  # Unnecessary
```

The `set -e` already handles errors. Manual error traps add token overhead without benefit.

## Don't Use for Single Commands

```bash
# BAD - overhead for single command
exec 2>&1
set -xeuo pipefail
ls -la
```

Just run `ls -la` directly via Bash tool without the pattern. Use the pattern for 3+ sequential commands.

## Don't Suppress All Errors

```bash
# BAD - suppressing all errors defeats set -e
exec 2>&1
set -xeuo pipefail

command1 || true
command2 || true
command3 || true  # Why use set -e at all?
```

Only use `|| true` for commands with expected non-zero exits (grep, diff).
