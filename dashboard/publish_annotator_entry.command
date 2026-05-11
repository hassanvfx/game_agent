#!/bin/zsh
set -euo pipefail

ROOT_DIR="/Volumes/Elements/games_top_gameplays"
cd "$ROOT_DIR"

TEMPLATE_FILE="annotator_template.html"

if [[ ! -f "$TEMPLATE_FILE" ]]; then
  echo "Missing template: $TEMPLATE_FILE"
  exit 1
fi

OLD_ENTRY="$(find . -maxdepth 1 -type f -name '*annotator*.html' ! -name "$TEMPLATE_FILE" -print | head -n 1 | sed 's#^\./##')"
if [[ -n "$OLD_ENTRY" ]]; then
  rm -f "$OLD_ENTRY"
fi

NEW_UUID="$(python3 - <<'PY'
import uuid
print(uuid.uuid4())
PY
)"

NEW_FILE="${NEW_UUID}-annotator.html"
cp "$TEMPLATE_FILE" "$NEW_FILE"

echo "Published annotator entry: $NEW_FILE"