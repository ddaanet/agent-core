# Agent Core Justfile

# Show available recipes
help:
    @just --list --unsorted

# Sync skills and agents to parent project's .claude directory via symlinks
sync-to-parent:
    #!/usr/bin/env bash
    set -euo pipefail

    # Determine parent project directory (one level up from agent-core)
    PARENT_DIR="$(cd .. && pwd)"
    CLAUDE_DIR="$PARENT_DIR/.claude"

    echo "Syncing agent-core to $PARENT_DIR/.claude via relative symlinks"

    # Create .claude directories if they don't exist
    mkdir -p "$CLAUDE_DIR/skills"
    mkdir -p "$CLAUDE_DIR/agents"

    # Remove stale skill symlinks (source deleted in agent-core)
    echo "Cleaning stale skill symlinks..."
    for target in "$CLAUDE_DIR/skills"/*/; do
        [ -d "$target" ] || continue
        skill_name=$(basename "$target")
        if [ -L "${target%/}" ] && [ ! -d "skills/$skill_name" ]; then
            rm -f "${target%/}"
            echo "  ✗ $skill_name (stale, removed)"
        fi
    done

    # Sync skills (create symlinks to skill directories)
    echo "Syncing skills..."
    for skill in skills/*/; do
        skill_name=$(basename "$skill")
        target="$CLAUDE_DIR/skills/$skill_name"

        # Remove existing directory or symlink
        rm -rf "$target"

        # Create relative symlink to skill directory
        ln -s "../../agent-core/skills/$skill_name" "$target"
        echo "  ✓ $skill_name → ../../agent-core/skills/$skill_name"
    done

    # Sync agents (create symlinks to agent files)
    echo "Syncing agents..."
    for agent in agents/*.md; do
        if [ -f "$agent" ]; then
            agent_name=$(basename "$agent")
            target="$CLAUDE_DIR/agents/$agent_name"

            # Remove existing file or symlink
            rm -f "$target"

            # Create relative symlink to agent file
            ln -s "../../agent-core/agents/$agent_name" "$target"
            echo "  ✓ $agent_name → ../../agent-core/agents/$agent_name"
        fi
    done

    # Sync hooks (create symlinks to hook files and hooks.json)
    if [ -d "hooks" ]; then
        echo "Syncing hooks..."
        mkdir -p "$CLAUDE_DIR/hooks"

        # Sync hooks.json if it exists
        if [ -f "hooks/hooks.json" ]; then
            target="$CLAUDE_DIR/hooks/hooks.json"
            rm -f "$target"
            ln -s "../../agent-core/hooks/hooks.json" "$target"
            echo "  ✓ hooks.json → ../../agent-core/hooks/hooks.json"
        fi

        # Sync hook scripts (.sh and .py files)
        for hook in hooks/*.sh hooks/*.py; do
            if [ -f "$hook" ]; then
                hook_name=$(basename "$hook")
                target="$CLAUDE_DIR/hooks/$hook_name"

                # Remove existing file or symlink
                rm -f "$target"

                # Create relative symlink to hook file
                ln -s "../../agent-core/hooks/$hook_name" "$target"
                chmod +x "$target"
                echo "  ✓ $hook_name → ../../agent-core/hooks/$hook_name"
            fi
        done
    fi

    echo "Syncing hook configuration..."
    python3 bin/sync-hooks-config.py

    echo "Sync complete!"

# Set up development environment (agent-core is documentation/skills only)
setup:
    @just sync-to-parent

# Stub precommit validation (agent-core has no validation requirements)
precommit:
    @echo "✓ Precommit OK"
