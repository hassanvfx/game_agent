#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

RUNS_ROOT = Path("/Volumes/HDD2026/output")
PATTERN = "run_v4_rick_morty_vatsal107_model55_c1_*"


def read_state(run_dir: Path) -> dict:
    state_path = run_dir / "run_state.json"
    if not state_path.exists():
        return {}
    try:
        return json.loads(state_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"state_read_error": str(exc)}


def main() -> None:
    runs = sorted(RUNS_ROOT.glob(PATTERN))
    result = []
    for run_dir in runs[-10:]:
        state = read_state(run_dir)
        result.append(
            {
                "run_id": run_dir.name,
                "run_dir": str(run_dir),
                "status": state.get("status"),
                "current_phase": state.get("current_phase"),
                "games_total": state.get("games_total"),
                "updated_at": state.get("updated_at"),
                "dashboard": str(run_dir / "dashboard/index.html"),
            }
        )
    print(json.dumps({"count": len(runs), "runs": result}, indent=2))


if __name__ == "__main__":
    main()