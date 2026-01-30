#!/usr/bin/env bash
# Adapted from skills/gitmoji/scripts/update-gitmoji-index.sh
# Downloads gitmoji database and creates searchable index file

set -euo pipefail

# Determine references directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
REFERENCES_DIR="${SKILL_DIR}/references"
INDEX_FILE="${REFERENCES_DIR}/gitmoji-index.txt"

# Create references directory if it does not exist
mkdir -p "$REFERENCES_DIR"

echo "Downloading gitmoji database from https://gitmoji.dev/api/gitmojis..."

# Download and process gitmoji data
curl -s https://gitmoji.dev/api/gitmojis | \
  jq -r '.gitmojis[] | "\(.emoji) - \(.name) - \(.description)"' \
  > "$INDEX_FILE"

# Append custom gitmojis
cat >> "$INDEX_FILE" << 'EOF'
🗜️ - compress - Reducing file size, condensing content, or optimizing for brevity
🤖 - robot - Add or update agent skills, instructions, or guidance
EOF

echo "✅ Gitmoji index created successfully at: $INDEX_FILE"
echo "📊 Total gitmojis: $(wc -l < "$INDEX_FILE")"
