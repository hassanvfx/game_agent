#!/bin/zsh
set -euo pipefail

RUNS_DIR="runs"

latest_run="$(find "$RUNS_DIR" -mindepth 1 -maxdepth 1 -type d -name 'run_*' | sort | tail -n 1)"

if [[ -z "${latest_run}" ]]; then
  echo "No run directories found under $RUNS_DIR" >&2
  exit 1
fi

python3 scripts/build_dashboard.py --run-dir "$latest_run" >/tmp/game_obfuscator_dashboard_path.txt
dashboard_path="$(cat /tmp/game_obfuscator_dashboard_path.txt)"

if [[ ! -f "$dashboard_path" ]]; then
  echo "Dashboard was not generated: $dashboard_path" >&2
  exit 1
fi

open "$dashboard_path"
echo "$dashboard_path"