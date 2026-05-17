#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path


LAUNCHER = Path("tools/game_editorial/scripts/launch_seeded_raw_remix_batch.py")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    completed = subprocess.run(
        [
            "python3",
            str(LAUNCHER),
            "--game-limit",
            "2",
            "--prompts-per-game",
            "2",
            "--source-mode",
            "copy",
            "--json",
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    payload = json.loads(completed.stdout)
    run_dir = Path(payload["workflow_result"]["run_dir"])
    time.sleep(5)

    run_state = load_json(run_dir / "run_state.json")
    result = {
        "launch_payload": payload,
        "run_state_after_5s": {
            "run_id": run_state.get("run_id"),
            "status": run_state.get("status"),
            "current_phase": run_state.get("current_phase"),
            "games_total": run_state.get("games_total"),
            "games_mirrored": run_state.get("games_mirrored"),
            "games_integrity_passed": run_state.get("games_integrity_passed"),
            "games_integrity_failed": run_state.get("games_integrity_failed"),
            "source_mode": run_state.get("source_mode"),
        },
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()