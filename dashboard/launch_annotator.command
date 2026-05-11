#!/bin/zsh
set -euo pipefail

ROOT_DIR="/Volumes/Elements/games_top_gameplays"
cd "$ROOT_DIR"

ANNOTATOR_ENTRY=""
for candidate in *.html; do
  if [[ "$candidate" == "annotator_template.html" ]]; then
    continue
  fi
  if [[ "$candidate" == *"annotator"* ]]; then
    ANNOTATOR_ENTRY="$candidate"
    break
  fi
done

if [[ -z "$ANNOTATOR_ENTRY" ]]; then
  ANNOTATOR_ENTRY="annotator_template.html"
fi

PORT_FILE=".annotator_server_port"
PID_FILE=".annotator_server_pid"

if [[ -f "$PID_FILE" ]]; then
  OLD_PID="$(cat "$PID_FILE" 2>/dev/null || true)"
  if [[ -n "$OLD_PID" ]] && kill -0 "$OLD_PID" 2>/dev/null; then
    kill "$OLD_PID" 2>/dev/null || true
    sleep 1
  fi
fi

PORT="8123"
echo "$PORT" > "$PORT_FILE"

python3 -m http.server "$PORT" > /tmp/games_top_gameplays_annotator_server.log 2>&1 &
SERVER_PID=$!
echo "$SERVER_PID" > "$PID_FILE"

sleep 2

open "http://127.0.0.1:$PORT/$ANNOTATOR_ENTRY"