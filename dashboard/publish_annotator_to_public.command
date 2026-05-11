#!/bin/zsh
set -euo pipefail

ROOT_DIR="/Volumes/Elements/games_top_gameplays"
cd "$ROOT_DIR"

TEMPLATE_FILE="annotator_template.html"
DEFAULT_PUBLIC_DIR="tag_and_fix_1k_export/runs/20260507T205404Z--full-run-semantic-pack/public"

TARGET_PUBLIC_DIR="${1:-$DEFAULT_PUBLIC_DIR}"

if [[ ! -f "$TEMPLATE_FILE" ]]; then
  echo "Missing template: $TEMPLATE_FILE"
  exit 1
fi

if [[ ! -d "$TARGET_PUBLIC_DIR" ]]; then
  echo "Missing public directory: $TARGET_PUBLIC_DIR"
  exit 1
fi

python3 - "$ROOT_DIR" "$TEMPLATE_FILE" "$TARGET_PUBLIC_DIR" <<'PY'
from pathlib import Path
import sys
import uuid

root_dir = Path(sys.argv[1])
template_file = Path(sys.argv[2])
target_public_dir = Path(sys.argv[3])

template_text = template_file.read_text()

existing = list(target_public_dir.glob("*annotator*.html"))
for path in existing:
    path.unlink()

existing_app_json = list(target_public_dir.glob("*app*.json"))
for path in existing_app_json:
    path.unlink()

new_name = f"{uuid.uuid4()}-annotator.html"
app_json_name = f"{uuid.uuid4()}-app.json"

app_json_source = target_public_dir.parent / "app.json"
app_json_target = target_public_dir / app_json_name

rewritten = template_text.replace(
    'const APP_DATA_PATH = "tag_and_fix_1k_export/runs/20260507T205404Z--full-run-semantic-pack/app.json";',
    f'const APP_DATA_PATH = "./{app_json_name}";'
).replace(
    'const PLAY_ROOT = "tag_and_fix_1k_export/runs/20260507T205404Z--full-run-semantic-pack/public/";',
    'const PLAY_ROOT = "./";'
)

if app_json_source.exists():
    app_json_target.write_text(app_json_source.read_text())

(target_public_dir / new_name).write_text(rewritten)

launcher = '''#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

PID_FILE=".annotator_server_pid"
PORT_FILE=".annotator_server_port"

if [[ -f "$PID_FILE" ]]; then
  OLD_PID="$(cat "$PID_FILE" 2>/dev/null || true)"
  if [[ -n "$OLD_PID" ]] && kill -0 "$OLD_PID" 2>/dev/null; then
    kill "$OLD_PID" 2>/dev/null || true
    sleep 1
  fi
fi

PORT="$(python3 - <<'EOFPORT'
import socket
sock = socket.socket()
sock.bind(("127.0.0.1", 0))
print(sock.getsockname()[1])
sock.close()
EOFPORT
)"

echo "$PORT" > "$PORT_FILE"

python3 -m http.server "$PORT" > /tmp/tag_and_fix_public_annotator_server.log 2>&1 &
SERVER_PID=$!
echo "$SERVER_PID" > "$PID_FILE"

sleep 2

ANNOTATOR_FILE="$(find . -maxdepth 1 -type f -name '*annotator*.html' | head -n 1 | sed 's#^\\./##')"

if [[ -z "$ANNOTATOR_FILE" ]]; then
  echo "No annotator entry found in $SCRIPT_DIR"
  exit 1
fi

URL="http://127.0.0.1:$PORT/$ANNOTATOR_FILE"

echo "Server PID: $SERVER_PID"
echo "Serving from: $SCRIPT_DIR"
echo "See live at: $URL"

open "$URL"
'''
(target_public_dir / "launch_annotator.command").write_text(launcher)
print(new_name)
print(app_json_name)
PY