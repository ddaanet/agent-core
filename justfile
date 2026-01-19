# Agent Core Justfile

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

    # Sync skills (create symlinks)
    echo "Syncing skills..."
    for skill in skills/*/; do
        skill_name=$(basename "$skill")
        target="$CLAUDE_DIR/skills/$skill_name"

        # Remove existing symlink or directory
        rm -rf "$target"

        # Create symlink
        ln -s "$(pwd)/$skill" "$target"
        echo "  ✓ $skill_name"
    done

    # Sync agents (copy files - Claude Code doesn't follow symlinks for agents)
    echo "Syncing agents..."
    for agent in agents/*.md; do
        if [ -f "$agent" ]; then
            agent_name=$(basename "$agent")
            cp "$agent" "$CLAUDE_DIR/agents/$agent_name"
            echo "  ✓ $agent_name"
        fi
    done

    echo "Sync complete!"
