#!/bin/bash
# Create plan-specific agent from baseline agent + plan context
#
# Usage: create-plan-agent.sh --plan <name> --output <dir> <plan-file>
#
# This script automates the creation of plan-specific agents by combining:
# 1. Baseline task-execute agent frontmatter and system prompt
# 2. Plan-specific context from the plan file
#
# The resulting agent can be used for executing plan steps with full plan context
# and is stored in .claude/agents/ for discovery by Claude Code.
#
# Arguments:
#   --plan <name>          Human-readable plan name (e.g., 'phase2', 'oauth2-auth')
#   --model <model>        Agent model (default: haiku)
#   --color <color>        YAML frontmatter color (default: cyan)
#   --output <dir>         Output directory for agent file
#   --help                 Show usage
#   <plan-file>            Path to plan markdown file
#
# Example:
#   ./create-plan-agent.sh --plan phase2 --output .claude/agents plans/phase2.md
#
# Output:
#   Creates: <output>/<plan>-task.md with full plan context

set -e

# Parse arguments
PLAN_NAME=""
MODEL="haiku"
COLOR="cyan"
OUTPUT_DIR=""
PLAN_FILE=""
SHOW_HELP=0

while [[ $# -gt 0 ]]; do
    case "$1" in
        --plan)
            PLAN_NAME="$2"
            shift 2
            ;;
        --model)
            MODEL="$2"
            shift 2
            ;;
        --color)
            COLOR="$2"
            shift 2
            ;;
        --output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --help)
            SHOW_HELP=1
            shift
            ;;
        *)
            if [[ ! "$1" =~ ^- ]]; then
                PLAN_FILE="$1"
                shift
            else
                echo "Unknown option: $1"
                SHOW_HELP=1
                shift
            fi
            ;;
    esac
done

# Show help if requested or if arguments missing
if [[ $SHOW_HELP -eq 1 ]] || [[ -z "$PLAN_NAME" ]] || [[ -z "$OUTPUT_DIR" ]] || [[ -z "$PLAN_FILE" ]]; then
    cat << 'EOF'
Create plan-specific agent from baseline agent + plan context

Usage: create-plan-agent.sh [options] <plan-file>

Options:
  --plan <name>          Human-readable plan name (required)
  --output <dir>         Output directory for agent file (required)
  --model <model>        Agent model (default: haiku)
  --color <color>        YAML frontmatter color (default: cyan)
  --help                 Show this help message

Arguments:
  <plan-file>            Path to plan markdown file (required)

Examples:
  ./create-plan-agent.sh --plan phase2 --output .claude/agents plans/phase2.md
  ./create-plan-agent.sh --plan oauth2 --model sonnet --output .claude/agents plans/oauth2.md

Output:
  Creates: <output>/<plan>-task.md
  Contains: YAML frontmatter + baseline agent + plan context

Benefits:
  - Context caching (plan context reused across steps)
  - Token efficiency (~4250 tokens saved on 3-step plan)
  - Consistency (all steps reference same plan definition)
  - Clean execution (fresh agent per step, no transcript bloat)
EOF
    exit 1
fi

# Validate inputs
if [ ! -f "$PLAN_FILE" ]; then
    echo "ERROR: Plan file not found: $PLAN_FILE"
    exit 1
fi

# Resolve agent-core baseline path
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
AGENT_CORE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BASELINE_AGENT="$AGENT_CORE_ROOT/agents/task-execute.md"

if [ ! -f "$BASELINE_AGENT" ]; then
    echo "ERROR: Baseline agent not found: $BASELINE_AGENT"
    exit 1
fi

# Create output directory if needed
mkdir -p "$OUTPUT_DIR"

# Determine output filename
AGENT_NAME="${PLAN_NAME}-task"
OUTPUT_FILE="$OUTPUT_DIR/$AGENT_NAME.md"

# Verify output file doesn't already exist (unless overwriting)
if [ -f "$OUTPUT_FILE" ]; then
    echo "WARNING: Output file already exists: $OUTPUT_FILE"
    echo "Overwriting..."
fi

# Report plan details
echo "Creating plan-specific agent..."
echo "  Plan name: $PLAN_NAME"
echo "  Agent name: $AGENT_NAME"
echo "  Model: $MODEL"
echo "  Color: $COLOR"
echo "  Baseline: $BASELINE_AGENT"
echo "  Plan file: $PLAN_FILE"
echo "  Output: $OUTPUT_FILE"
echo ""

# Generate agent file
# Step 1: Create YAML frontmatter
cat > "$OUTPUT_FILE" << FRONTMATTER_EOF
---
name: $AGENT_NAME
description: Execute $PLAN_NAME steps with full plan context
model: $MODEL
color: $COLOR
tools: ["Read", "Write", "Bash", "Grep", "Glob", "Edit"]
---

FRONTMATTER_EOF

# Step 2: Append baseline system prompt (skip frontmatter from baseline)
# Extract everything after the second --- marker
awk '/^---$/ {count++; next} count >= 2 {print}' "$BASELINE_AGENT" >> "$OUTPUT_FILE"

# Step 3: Append plan context separator
cat >> "$OUTPUT_FILE" << SEPARATOR_EOF

---

## PLAN CONTEXT: $PLAN_NAME

This section contains plan-specific context. The task execution behavior above still applies, with added plan knowledge.

SEPARATOR_EOF

# Step 4: Append plan context content
cat "$PLAN_FILE" >> "$OUTPUT_FILE"

# Verify output
OUTPUT_SIZE=$(wc -c < "$OUTPUT_FILE")
OUTPUT_LINES=$(wc -l < "$OUTPUT_FILE")

# Check frontmatter syntax (basic validation)
if head -5 "$OUTPUT_FILE" | grep -q "^---$"; then
    echo "✓ YAML frontmatter present"
else
    echo "✗ ERROR: YAML frontmatter not found"
    rm -f "$OUTPUT_FILE"
    exit 1
fi

# Check that content was appended
if grep -q "^## PLAN CONTEXT:" "$OUTPUT_FILE"; then
    echo "✓ Plan context separator found"
else
    echo "✗ ERROR: Plan context separator not found"
    rm -f "$OUTPUT_FILE"
    exit 1
fi

# Check baseline content
if grep -q "Task Agent - Baseline Template" "$OUTPUT_FILE"; then
    echo "✓ Baseline agent content found"
else
    echo "✗ ERROR: Baseline agent content not found"
    rm -f "$OUTPUT_FILE"
    exit 1
fi

echo ""
echo "✓ Successfully created plan-specific agent"
echo "  File: $OUTPUT_FILE"
echo "  Size: $OUTPUT_SIZE bytes ($OUTPUT_LINES lines)"
echo ""
echo "To use this agent:"
echo "  1. Ensure it's in .claude/agents/ directory (it is)"
echo "  2. Reference in task delegation: 'Use $AGENT_NAME agent to execute...'"
echo "  3. Agent will have full $PLAN_NAME context during execution"
echo ""
