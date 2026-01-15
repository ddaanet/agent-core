# Tool Preferences

Guidance for consistent tool usage across agent projects:

## File Operations

**Use specialized tools** instead of shell commands:
- `Read` tool instead of `cat`, `head`, `tail`
- `Write` tool instead of `echo >`, `cat <<EOF`
- `Edit` tool instead of `sed`, `awk`
- `Glob` tool instead of `find`, `ls`
- `Grep` tool instead of `grep`, `rg` shell commands

**Rationale**: Specialized tools provide:
- Proper permission handling
- Consistency across platforms
- Better error reporting
- Simpler syntax for complex operations

## Code Search

- Use `Grep` tool for pattern searching
- Use `Glob` tool for file discovery
- Chain tools for complex queries
- Provide context flags (-C, -B, -A) for understanding

## Parallel Execution

- Run independent commands in parallel using single Bash call
- Use `&&` to chain dependent commands
- Use `;` when order matters but failures don't prevent continuation
- Document dependencies clearly

## Git Operations

- Use Bash tool with git commands
- Follow git safety protocols
- Commit only when explicitly requested
- Never force-push to main/master without confirmation

## Error Handling

- Stop on unexpected results
- Report exact error messages
- Check prerequisites before proceeding
- Provide diagnostic steps for debugging
