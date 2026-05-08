#!/bin/zsh
set -euo pipefail

ROOT="/Volumes/Elements/game_remix_editor"
PORT="${1:-8058}"

latest_run="$(ls -td "$ROOT"/runs/run_game_remixer_* 2>/dev/null | head -n 1 || true)"
if [[ -z "${latest_run}" ]]; then
  echo "No Game Remixer runs found under $ROOT/runs" >&2
  exit 1
fi

dashboard_path="/runs/$(basename "$latest_run")/dashboard/index.html"
log_path="/tmp/game_remixer_dashboard_${PORT}.log"

if lsof -ti tcp:"${PORT}" >/dev/null 2>&1; then
  lsof -ti tcp:"${PORT}" | xargs kill -9
fi

python3 "$ROOT/scripts/serve_dashboard.py" --port "${PORT}" >"$log_path" 2>&1 &
server_pid=$!

sleep 1

url="http://127.0.0.1:${PORT}${dashboard_path}"

echo "Latest run: $latest_run"
echo "Dashboard URL: $url"
echo "Server PID: $server_pid"
echo "Server log: $log_path"

open "$url"