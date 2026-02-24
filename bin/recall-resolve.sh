#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: recall-resolve.sh <artifact-path>" >&2
  exit 1
fi

ARTIFACT="$1"

if [[ ! -f "$ARTIFACT" ]]; then
  echo "recall-resolve.sh: artifact not found: ${ARTIFACT}" >&2
  exit 1
fi

if [[ ! -r "$ARTIFACT" ]]; then
  echo "recall-resolve.sh: artifact not readable: ${ARTIFACT}" >&2
  exit 1
fi

# Parse manifest: strip annotations, skip blanks and comments, collect triggers
triggers=()
while IFS= read -r line; do
  # Strip annotation (everything after first ' — ')
  line="${line% — *}"
  # Trim trailing whitespace
  line="${line%"${line##*[![:space:]]}"}"
  # Skip blank lines and comment lines
  [[ -z "$line" ]] && continue
  [[ "$line" == \#* ]] && continue
  # Determine prefix: use as-is if starts with 'when' or 'how', else prepend 'when'
  first_word="${line%% *}"
  if [[ "$first_word" == "when" || "$first_word" == "how" ]]; then
    triggers+=("$line")
  else
    triggers+=("when $line")
  fi
done < "$ARTIFACT"

if [[ ${#triggers[@]} -eq 0 ]]; then
  echo "recall-resolve.sh: no triggers found in artifact: ${ARTIFACT}" >&2
  exit 0
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"${SCRIPT_DIR}/when-resolve.py" "${triggers[@]}"
