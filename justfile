# Agent Core Justfile

# Show available recipes
help:
    @just --list --unsorted

# Sync skills and agents to parent project's .claude directory
sync-to-parent:
    #!/usr/bin/env bash
    set -euo pipefail

    # Determine parent project directory (one level up from agent-core)
    PARENT_DIR="$(cd .. && pwd)"
    CLAUDE_DIR="$PARENT_DIR/.claude"

    echo "Syncing agent-core to $PARENT_DIR/.claude"

    # Create .claude directories if they don't exist
    mkdir -p "$CLAUDE_DIR/skills"
    mkdir -p "$CLAUDE_DIR/agents"

    # Sync skills (copy directories - symlinks work but copying is safer)
    echo "Syncing skills..."
    for skill in skills/*/; do
        skill_name=$(basename "$skill")
        target="$CLAUDE_DIR/skills/$skill_name"

        # Remove existing directory or symlink
        rm -rf "$target"

        # Copy skill directory
        cp -r "$skill" "$target"
        echo "  ✓ $skill_name"
    done

    # Sync agents (copy files - Claude Code doesn't follow symlinks)
    echo "Syncing agents..."
    for agent in agents/*.md; do
        if [ -f "$agent" ]; then
            agent_name=$(basename "$agent")
            cp "$agent" "$CLAUDE_DIR/agents/$agent_name"
            echo "  ✓ $agent_name"
        fi
    done

    echo "Sync complete!"
