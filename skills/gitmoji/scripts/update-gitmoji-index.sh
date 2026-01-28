#\!/usr/bin/env bash
# Downloads gitmoji database and creates searchable index file

set -euo pipefail

# Determine cache directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
CACHE_DIR="${SKILL_DIR}/cache"
INDEX_FILE="${CACHE_DIR}/gitmojis.txt"

# Create cache directory if it does not exist
mkdir -p "$CACHE_DIR"

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
