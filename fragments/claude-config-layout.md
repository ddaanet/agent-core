## Claude Code Configuration Layout

**Standard file locations and conventions for Claude Code projects.**

### Hook Configuration

**Settings-level hooks:**
- Location: `.claude/settings.json`
- Format: Nested structure with optional `matcher` and `hooks` array
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python3 $CLAUDE_PROJECT_DIR/.claude/hooks/pretooluse.py"
          }
        ]
      }
    ]
  }
}
```

**Plugin-level hooks:**
- Location: `.claude/plugins/[plugin-name]/plugin.json`
- Format: Wrapped with `{"description": "...", "hooks": {...}}`
```json
{
  "description": "My plugin",
  "hooks": {
    "PreToolUse": [...]
  }
}
```

**Project-local hooks:**
- Location: `.claude/hooks/` directory (scripts directly, no separate config file)
- Format: Direct `{event: [...]}` structure (same as settings)
- NOT read from `.claude/hooks/hooks.json` — use settings.json instead

**Hook output for deny decisions:**
- Must write to stderr: `>&2 echo "Error message"`
- Must exit with code 2
- Plain text message works (no JSON wrapper needed)

**Hook activation:**
- Hook changes only take effect after restarting Claude Code session
- Test hooks after commit by restarting and running test procedure

### Agent Configuration

**Plan-specific agents:**
- Created by: `prepare-runbook.py`
- Location: `.claude/agents/[plan-name]-task.md`
- Discovery: Requires restart after creation
- Usage: Auto-selected by `/orchestrate` when plan name matches

**Symlinks in .claude/:**
- `.claude/agents/`, `.claude/skills/`, `.claude/hooks/` can contain symlinks to agent-core/
- Tracked in git (symlinks are portable across Unix systems)
- Recreate with: `just sync-to-parent` in agent-core/ directory (requires `dangerouslyDisableSandbox: true`)

### Bash Working Directory

**Main interactive agent:**
- `cwd` persists between Bash calls
- Can use relative paths safely

**Sub-agents (Task tool):**
- `cwd` does NOT persist between calls
- MUST use absolute paths or change directory within same command
- CLAUDE.md absolute path guidance targets sub-agents

**Hook enforcement:**
- `submodule-safety` hook blocks commands when cwd != project root
