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
    AGENT_CORE_ABS="$(pwd)"

    echo "Syncing agent-core to $PARENT_DIR/.claude via symlinks"

    # Create .claude directories if they don't exist
    mkdir -p "$CLAUDE_DIR/skills"
    mkdir -p "$CLAUDE_DIR/agents"

    # Sync skills (create symlinks to skill directories)
    echo "Syncing skills..."
    for skill in skills/*/; do
        skill_name=$(basename "$skill")
        target="$CLAUDE_DIR/skills/$skill_name"

        # Remove existing directory or symlink
        rm -rf "$target"

        # Create symlink to skill directory
        ln -s "$AGENT_CORE_ABS/skills/$skill_name" "$target"
        echo "  ✓ $skill_name → agent-core/skills/$skill_name"
    done

    # Sync agents (create symlinks to agent files)
    echo "Syncing agents..."
    for agent in agents/*.md; do
        if [ -f "$agent" ]; then
            agent_name=$(basename "$agent")
            target="$CLAUDE_DIR/agents/$agent_name"

            # Remove existing file or symlink
            rm -f "$target"

            # Create symlink to agent file
            ln -s "$AGENT_CORE_ABS/agents/$agent_name" "$target"
            echo "  ✓ $agent_name → agent-core/agents/$agent_name"
        fi
    done

    echo "Sync complete!"
