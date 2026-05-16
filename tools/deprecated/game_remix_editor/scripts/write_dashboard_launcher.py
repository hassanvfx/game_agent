#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Write a per-run dashboard launcher script for Game Remixer.")
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--default-port", type=int, default=8058)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_dir = Path(args.run_dir).resolve()
    launcher_path = run_dir / "serve_dashboard.sh"
    dashboard_path = run_dir / "dashboard" / "index.html"

    script = """#!/bin/zsh
set -euo pipefail

PORT="${1:-DEFAULT_PORT}"
ROOT="ROOT_PATH"
DASHBOARD="DASHBOARD_PATH"

if lsof -ti tcp:"${PORT}" >/dev/null 2>&1; then
  lsof -ti tcp:"${PORT}" | xargs kill -9
fi

python3 "$ROOT/scripts/serve_dashboard.py" --port "${PORT}" >/tmp/game_remixer_dashboard_${PORT}.log 2>&1 &
SERVER_PID=$!

sleep 1

echo "Game Remixer dashboard server running on http://127.0.0.1:${PORT}${DASHBOARD}"
echo "Server PID: $SERVER_PID"
echo "Dashboard file: DASHBOARD_FILE"
open "http://127.0.0.1:${PORT}${DASHBOARD}"
"""
    script = script.replace("DEFAULT_PORT", str(args.default_port))
    script = script.replace("ROOT_PATH", str(ROOT))
    script = script.replace("DASHBOARD_PATH", f"/runs/{run_dir.name}/dashboard/index.html")
    script = script.replace("DASHBOARD_FILE", str(dashboard_path))
    launcher_path.write_text(script, encoding="utf-8")
    launcher_path.chmod(0o755)
    print(launcher_path)


if __name__ == "__main__":
    main()