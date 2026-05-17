#!/bin/zsh
set -euo pipefail

PORT="${1:-8058}"
ROOT="/Users/hassan/repos/game_agent/tools/game_refactoring"
DASHBOARD="/runs/run_game_remixer_20260517T140948Z/dashboard/index.html"

if lsof -ti tcp:"${PORT}" >/dev/null 2>&1; then
  lsof -ti tcp:"${PORT}" | xargs kill -9
fi

python3 "$ROOT/scripts/serve_dashboard.py" --port "${PORT}" >/tmp/game_remixer_dashboard_${PORT}.log 2>&1 &
SERVER_PID=$!

sleep 1

echo "Game Remixer dashboard server running on http://127.0.0.1:${PORT}${DASHBOARD}"
echo "Server PID: $SERVER_PID"
echo "Dashboard file: /Users/hassan/repos/game_agent/tools/game_refactoring/runs/run_game_remixer_20260517T140948Z/dashboard/index.html"
open "http://127.0.0.1:${PORT}${DASHBOARD}"
