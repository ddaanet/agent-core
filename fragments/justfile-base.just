# Base justfile recipes for agent projects
# This file is extracted and composed into project-specific justfiles
# Template variables: {{SRC_DIR}}, {{TEST_DIR}}, {{VENV}}

# Default target
_default:
    @echo "Available recipes:"
    @just --list

# Build and check targets will be customized per project
