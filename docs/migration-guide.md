# Migration Guide: Adopting agent-core

Guide for projects adding agent-core as a submodule or updating to the latest structure.

## Quick Start for New Projects

**For projects starting from scratch (no existing structure to migrate):**

1. **Add agent-core submodule**
   ```bash
   git submodule add <agent-core-repo-url> agent-core
   git submodule update --init --recursive
   ```

2. **Sync symlinks to .claude/**
   ```bash
   cd agent-core
   just sync-to-parent
   cd ..
   ```

3. **Copy CLAUDE.md template**
   ```bash
   cp agent-core/templates/CLAUDE.template.md CLAUDE.md
   ```
   Customize the template (see [templates/README.md](../templates/README.md) for guidance).

4. **Configure settings.json**
   Add hooks and sandbox configuration from Phase 2 below (steps 2.1-2.4).

5. **Create session.md**
   ```bash
   touch session.md
   ```
   Add initial session header:
   ```markdown
   # Session: [Project Name]

   **Status:** Initial setup

   ## Pending Tasks

   ## Blockers / Gotchas
   ```

6. **Restart Claude Code** to load hooks and symlinked skills/agents.

**That's it!** You now have Tier 1 (minimal) structure. See [Tiered Adoption](#tiered-adoption) below to determine if you need agents/ directory and additional structure.

**Next steps:**
- Read [general-workflow.md](general-workflow.md) or [tdd-workflow.md](tdd-workflow.md) to understand development workflows
- Use `/design` skill as entry point for implementation tasks (auto-detects workflow type)

---

## Prerequisites

- Git repository with Claude Code configured (`.claude/` directory exists)
- agent-core added as submodule: `git submodule add <url> agent-core`

---

## Migration Checklist

**For existing projects with structure to migrate:**

### Phase 1: Submodule and Symlinks

- [ ] **1.1** Add agent-core submodule (if not already present)
  ```bash
  git submodule add <agent-core-repo-url> agent-core
  ```

- [ ] **1.2** Sync symlinks to `.claude/`
  ```bash
  cd agent-core && just sync-to-parent
  ```
  This creates symlinks in `.claude/agents/`, `.claude/skills/`, `.claude/hooks/` pointing to agent-core sources.

- [ ] **1.3** Verify symlinks resolve
  ```bash
  file .claude/agents/*.md .claude/skills/* .claude/hooks/*
  ```
  All should show resolved file types, not "broken symbolic link".

### Phase 2: Settings Configuration

See [fragments/claude-config-layout.md](../fragments/claude-config-layout.md) for detailed hook configuration patterns.

- [ ] **2.1** Update `.claude/settings.json` with hook configuration
  ```json
  {
    "hooks": {
      "PreToolUse": [
        {
          "matcher": "Write|Edit",
          "hooks": [
            {
              "type": "command",
              "command": "bash $CLAUDE_PROJECT_DIR/.claude/hooks/pretooluse-block-tmp.sh"
            },
            {
              "type": "command",
              "command": "bash $CLAUDE_PROJECT_DIR/.claude/hooks/pretooluse-symlink-redirect.sh"
            }
          ]
        },
        {
          "matcher": "Bash",
          "hooks": [
            {
              "type": "command",
              "command": "python3 $CLAUDE_PROJECT_DIR/.claude/hooks/submodule-safety.py"
            }
          ]
        }
      ],
      "PostToolUse": [
        {
          "matcher": "Bash",
          "hooks": [
            {
              "type": "command",
              "command": "python3 $CLAUDE_PROJECT_DIR/.claude/hooks/submodule-safety.py"
            }
          ]
        }
      ],
      "UserPromptSubmit": [
        {
          "hooks": [
            {
              "type": "command",
              "command": "python3 $CLAUDE_PROJECT_DIR/agent-core/hooks/userpromptsubmit-shortcuts.py",
              "timeout": 5
            }
          ]
        }
      ]
    }
  }
  ```

- [ ] **2.2** Add sandbox configuration
  ```json
  {
    "sandbox": {
      "enabled": true,
      "autoAllowBashIfSandboxed": true,
      "excludedCommands": ["git", "agent-core/bin/prepare-runbook.py"]
    }
  }
  ```

- [ ] **2.3** Expand permissions to match agent-core conventions
  ```json
  {
    "permissions": {
      "allow": [
        "Bash(git:*)",
        "Bash(wc:*)",
        "Bash(claudeutils:*)",
        "Bash(just:*)",
        "Bash(pbcopy:*)",
        "Bash(agent-core/bin/prepare-runbook.py:*)",
        "Skill",
        "WebSearch"
      ],
      "deny": [
        "NotebookEdit",
        "Bash(git push:*)"
      ]
    }
  }
  ```
  Add project-specific tool permissions (pytest, ruff, mypy, etc.) to the allow list.

- [ ] **2.4** Set plansDirectory for built-in plan mode
  ```json
  {
    "plansDirectory": "plans/claude/"
  }
  ```

### Phase 3: Directory Structure

**Note:** Steps in this phase are conditional based on your tier (see Tiered Adoption section). Tier 1 projects can skip this entire phase and use root-level session.md.

- [ ] **3.1** Create `agents/` directory (skip for Tier 1)
  ```bash
  mkdir -p agents/decisions
  ```

- [ ] **3.2** Move session.md to `agents/session.md` (skip for Tier 1 or if already at `agents/session.md`)
  ```bash
  git mv session.md agents/session.md
  ```

- [ ] **3.3** Create `agents/learnings.md` with standard header (Tier 2+)
  ```markdown
  # Learnings

  Institutional knowledge accumulated across sessions. Append new learnings at the bottom.

  **Soft limit: 80 lines.** When approaching this limit, use `/codify` to consolidate older learnings into permanent documentation (behavioral rules → `agent-core/fragments/*.md`, technical details → `agents/decisions/*.md` or `agents/decisions/implementation-notes.md`). Keep the 3-5 most recent learnings for continuity.

  ---
  ```
  Skip for Tier 1 (keep learnings inline in session.md).

- [ ] **3.4** Extract existing learnings from session.md (Tier 2+)
  If session.md has a `## Recent Learnings` section, move its content to `agents/learnings.md` (after the header). Remove the section from session.md.
  Skip for Tier 1.

- [ ] **3.5** Create `agents/jobs.md` (Tier 3 recommended, optional for Tier 2)
  ```markdown
  # Jobs

  Plan lifecycle tracking. Updated when plans change status. Used by STATUS command to display plan metadata.

  **Status:** `requirements` → `designed` → `planned` → `complete`

  ## Plans

  | Plan | Status | Notes |
  |------|--------|-------|
  ```
  Skip for Tier 1.

- [ ] **3.6** Migrate decision documents (if applicable)
  Move project-specific architectural docs to `agents/decisions/`:
  ```bash
  git mv dev/architecture.md agents/decisions/architecture.md
  git mv dev/design-decisions.md agents/decisions/design-decisions.md
  ```
  Adjust paths based on your project's existing structure. Skip if no existing decision documents.

### Phase 4: CLAUDE.md Update

- [ ] **4.1** Update session.md `@` reference path (if moved in Phase 3.2)
  Change `@session.md` to `@agents/session.md` in the Current Work section.
  Skip if keeping root-level session.md (Tier 1).

- [ ] **4.2** Add learnings.md `@` reference (Tier 2+)
  ```markdown
  ### Current Work
  - @agents/session.md - Current session handoff context (update only on handoff)
  - @agents/learnings.md - Accumulated learnings (append-only, soft limit 80 lines)
  ```
  Skip for Tier 1 (no separate learnings file).

- [ ] **4.3** Update Architecture & Design section (if decision documents migrated)
  ```markdown
  ### Architecture & Design
  - **agents/decisions/architecture.md** - Module structure, implementation details
  - **agents/decisions/design-decisions.md** - Design rationale and trade-offs
  ```
  Skip if keeping existing paths or no decision documents.

- [ ] **4.4** Remove stale context management rules
  Remove or update any rules that reference the old structure:
  - "When to create agents/ directory" guidance (no longer relevant once agents/ exists)
  - Old learnings inline guidance (if migrated to separate file)
  - Root-level session.md references (if moved to agents/)

- [ ] **4.5** (Optional) Add memory index reference (Tier 3)
  For larger projects with many learnings/decisions, add a memory index file that maps topics to relevant files:
  ```markdown
  @agents/memory-index.md
  ```
  The memory-index.md file lists key topics with references to where they're documented (format: topic → file path + brief description). Enables quick context discovery without reading all files.

### Phase 5: Verification

- [ ] **5.1** Restart Claude Code session (hooks require restart)
- [ ] **5.2** Test hooks work: run a bash command, verify submodule-safety doesn't block at project root
- [ ] **5.3** Test shortcut expansion: type `s` and verify STATUS format appears
- [ ] **5.4** Test `/handoff` writes learnings to `agents/learnings.md` (not session.md) — skip for Tier 1
- [ ] **5.5** Verify `@` references resolve in CLAUDE.md

---

## Tiered Adoption

Not every project needs the full structure. Choose the tier matching your project's complexity.

### Decision Flowchart

```
Which tier do I need?

├─ Single developer, infrequent sessions?
│  └─ Tier 1 (Minimal)
│
├─ Active development, regular handoffs?
│  └─ Tier 2 (Standard)
│
└─ Multiple plans, complex architecture, specialized agents?
   └─ Tier 3 (Full)
```

**Still unsure?** Start with Tier 1. You can always upgrade later as needs grow.

### Tier 1: Minimal (small projects, infrequent development)

**Use case:** Single developer, occasional sessions, simple structure needs.

**Required:**
- Phase 1 (submodule + symlinks)
- Phase 2 (settings with hooks)
- CLAUDE.md from template (`agent-core/templates/CLAUDE.template.md`)

**Structure:**
- Root-level `session.md` (no agents/ directory)
- Learnings kept inline in session.md `## Recent Learnings` section
- No jobs.md or decision documents

**Skip:** Phase 3, most of Phase 4 (only update @ references if customizing template)

### Tier 2: Standard (active projects, regular sessions)

**Use case:** Active development, regular handoffs, growing context needs.

**Everything in Tier 1, plus:**
- Phase 3 steps 3.1–3.4 (create agents/, move session.md, separate learnings)
- Phase 4 steps 4.1–4.4 (update @ references for new paths)

**Structure:**
- `agents/session.md` with handoff context
- `agents/learnings.md` for accumulated knowledge
- Optional `agents/decisions/` for architectural docs
- Optional `agents/jobs.md` if tracking multiple plans

### Tier 3: Full (complex projects, multi-plan, multi-agent)

**Use case:** Complex architecture, multiple plans, specialized agents.

**Everything in Tier 2, plus:**
- Phase 3 steps 3.5–3.6 (jobs.md for plan tracking, decision documents)
- Phase 4 step 4.5 (memory index)
- Plan-specific agents (auto-generated by `/orchestrate`)
- Custom fragments (project-specific rules in agent-core/fragments/)

**Structure:**
- Full agents/ directory with session.md, learnings.md, jobs.md, memory-index.md
- `agents/decisions/` with architectural documentation
- `.claude/agents/` with plan-specific agents
- Potentially custom skills in `.claude/skills/`

---

## Common Issues

**Hooks don't fire:** Restart Claude Code after adding hook configuration. Hooks load at session start.

**Submodule-safety blocks commands:** Working directory drifted from project root. Run `cd <project-root>` to restore.

**Symlinks broken or pointing to wrong paths:** The `just sync-to-parent` command must be run from within the `agent-core/` directory. Run `cd agent-core && just sync-to-parent` from project root.

**Symlink-redirect blocks edits:** You're editing a file symlinked to agent-core. Edit the source file in `agent-core/` directly instead (or the upstream repo).

**Handoff fails to write learnings:** `agents/learnings.md` doesn't exist. Create it with the standard header (Phase 3, step 3.3). Or, if using Tier 1, learnings should remain inline in session.md.

**`@` references don't resolve:** Ensure paths are relative to project root and files exist. `@agents/session.md` requires `agents/session.md` to exist.

---

## Reference

**Setup and configuration:**
- [templates/CLAUDE.template.md](../templates/CLAUDE.template.md) — Base CLAUDE.md template
- [templates/README.md](../templates/README.md) — Template customization guide
- [fragments/claude-config-layout.md](../fragments/claude-config-layout.md) — Hook and config conventions
- [migrations/001-separate-learnings.md](../migrations/001-separate-learnings.md) — Learnings separation migration

**Workflows and patterns:**
- [docs/general-workflow.md](general-workflow.md) — General implementation workflow (6 stages)
- [docs/tdd-workflow.md](tdd-workflow.md) — TDD methodology workflow (RED/GREEN/REFACTOR)
- [docs/pattern-plan-specific-agent.md](pattern-plan-specific-agent.md) — Plan-specific agent pattern
- [docs/pattern-weak-orchestrator.md](pattern-weak-orchestrator.md) — Weak orchestrator pattern
