#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from orchestration_state import ensure_game_timestamps, ensure_run_timestamps, write_json


ROOT = Path(__file__).resolve().parents[1]
RUNS_ROOT = ROOT / "runs"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def default_run_id() -> str:
    return f"run_game_obfuscator_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a timestamped Game Obfuscator run scaffold.")
    parser.add_argument("--manifest", required=True, help="Path to the input manifest JSON file.")
    parser.add_argument("--run-id", help="Optional explicit run id. Defaults to a UTC timestamped id.")
    parser.add_argument(
        "--output-root",
        help="Optional explicit output root directory. Defaults to <run_dir>/output.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_id = args.run_id or default_run_id()
    run_dir = RUNS_ROOT / run_id
    if run_dir.exists():
        raise SystemExit(f"Run directory already exists: {run_dir}")

    manifest_path = Path(args.manifest).resolve()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    selected_games = manifest.get("games", [])

    output_root = Path(args.output_root).resolve() if args.output_root else (run_dir / "output").resolve()

    (run_dir / "input").mkdir(parents=True, exist_ok=True)
    output_root.mkdir(parents=True, exist_ok=True)
    (run_dir / "games").mkdir(parents=True, exist_ok=True)
    (run_dir / "dashboard").mkdir(parents=True, exist_ok=True)

    manifest_copy = {
        **manifest,
        "source_manifest_path": str(manifest_path),
    }
    write_json(run_dir / "input_manifest.json", manifest_copy)

    run_state = ensure_run_timestamps(
        {
            "run_id": run_id,
            "status": "created",
            "current_phase": "run_created",
            "created_at": utc_now(),
            "updated_at": utc_now(),
            "games_total": len(selected_games),
            "output_root": str(output_root),
            "games_prepared": 0,
            "games_integrity_passed": 0,
            "games_integrity_failed": 0,
            "games_completed": 0,
            "games_failed": 0,
            "games_pending": len(selected_games),
            "games_running": 0,
            "games_succeeded": 0,
            "games_stalled": 0,
            "resume_supported": True,
            "notes": [
                "Game Obfuscator run scaffold created.",
                "No input preparation or transformation execution has occurred yet.",
            ],
        }
    )
    write_json(run_dir / "run_state.json", run_state)

    for game in selected_games:
        game_id = game["game_id"]
        game_dir = run_dir / "games" / game_id
        game_dir.mkdir(parents=True, exist_ok=True)
        game_state = ensure_game_timestamps(
            {
                "game_id": game_id,
                "display_name": game.get("display_name"),
                "source_path": game.get("source_path"),
                "input_mirror_path": str(run_dir / "input" / game_id),
                "working_path": str(game_dir / "working"),
                "output_path": str(output_root / game_id),
                "artifacts_path": str(output_root / game_id / "artifacts"),
                "status": "pending",
                "current_phase": "pending_input_prepare",
                "integrity_status": None,
                "attempt_count": 0,
                "last_error": None,
                "artifacts": {},
            }
        )
        write_json(game_dir / "game_state.json", game_state)

    print(run_dir)


if __name__ == "__main__":
    main()