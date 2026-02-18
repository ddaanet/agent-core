## Sandbox Exemptions

### How Sandbox Bypass Works

Two independent layers control command execution:

| Setting | Controls | Reliable? |
|---------|----------|-----------|
| `permissions.allow` | Permission prompt (skips it) | Yes |
| `excludedCommands` | Sandbox bypass (supposed to) | Buggy — known issues |
| `dangerouslyDisableSandbox: true` | Sandbox bypass (per-call) | Yes |

**Practical pattern:** Use `permissions.allow` (no prompt) + `dangerouslyDisableSandbox: true` (reliable sandbox bypass). The combination runs without prompting AND bypasses sandbox.

`excludedCommands` is unreliable for filesystem/network bypass:
- https://github.com/anthropics/claude-code/issues/10767 (git SSH not bypassed)
- https://github.com/anthropics/claude-code/issues/14162 (DNS blocked despite excludedCommands)
- https://github.com/anthropics/claude-code/issues/19135 (logic conflict with allowUnsandboxedCommands)

### Prefix Matching Rule

When a command is in `permissions.allow`, invoke it with the **exact prefix** that matches the pattern. Do NOT add `python3` or other interpreter prefixes — this breaks the pattern match and triggers unnecessary permission prompts.

### prepare-runbook.py

- In `permissions.allow`: `Bash(agent-core/bin/prepare-runbook.py:*)`
- Invocation: `agent-core/bin/prepare-runbook.py <runbook>` (has shebang, runs directly)
- Requires `dangerouslyDisableSandbox: true` (writes to `.claude/agents/`)
- Do NOT use: `python3 agent-core/bin/prepare-runbook.py` (breaks permission match)

### just sync-to-parent

- Recipe: `just sync-to-parent` (in agent-core/ directory)
- Invocation: `just sync-to-parent` (no arguments)
- Requires `dangerouslyDisableSandbox: true` (creates/updates symlinks in `.claude/agents/`, `.claude/skills/`, `.claude/hooks/`)
- Fails in sandbox with: "Operation not permitted"

### Worktree Operations

**All mutation commands require bypass:** `claudeutils _worktree new`, `merge`, and `rm` write `.claude/settings.local.json` (sandbox allowlist management) and perform operations outside the project root. Always invoke with `dangerouslyDisableSandbox: true`.

**Additional bypass needs within worktree setup:**
- `uv sync` — Network access for package downloads + writes to `.venv/` inside worktree
- `direnv allow` — Writes to `.direnv/` outside the worktree directory structure

**Skill instrumentation:** The worktree skill (`agent-core/skills/worktree/SKILL.md`) annotates each mutation command with the bypass requirement. Read-only git commands do not need bypass.

### Commands Requiring `dangerouslyDisableSandbox: true`

- Commands writing to `.claude/` directory (except `.claude/debug/`)
- Commands writing to system config locations
- Commands requiring network access to non-whitelisted hosts
- Environment initialization in worktrees (`uv sync`, `direnv allow`)
