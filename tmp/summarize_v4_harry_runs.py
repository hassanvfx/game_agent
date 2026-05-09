#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNS_ROOT = ROOT / "tmp/game_refactoring_experiments/runs"


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"error": str(exc)}


def main() -> None:
    runs = sorted(RUNS_ROOT.glob("run_v4_harry_potter_one_game_*"))
    if not runs:
        print("no_v4_harry_runs_found")
        return

    for run_dir in runs[-10:]:
        state_path = run_dir / "run_state.json"
        state = load_json(state_path) if state_path.exists() else {}
        print(json.dumps({
            "run_id": run_dir.name,
            "status": state.get("status"),
            "current_phase": state.get("current_phase"),
            "games_total": state.get("games_total"),
            "games_transform_completed": state.get("games_transform_completed"),
            "games_transform_failed": state.get("games_transform_failed"),
            "updated_at": state.get("updated_at"),
            "run_dir": str(run_dir),
            "dashboard": str(run_dir / "dashboard/index.html"),
        }, indent=2))


if __name__ == "__main__":
    main()