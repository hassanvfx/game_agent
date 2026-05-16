#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNS_ROOT = ROOT / "runs"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def default_run_id() -> str:
    return f"run_game_remixer_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a timestamped Game Remixer run scaffold.")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--run-id")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_id = args.run_id or default_run_id()
    run_dir = RUNS_ROOT / run_id
    if run_dir.exists():
        raise SystemExit(f"Run directory already exists: {run_dir}")

    manifest_path = Path(args.manifest).resolve()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    (run_dir / "input").mkdir(parents=True, exist_ok=True)
    (run_dir / "output").mkdir(parents=True, exist_ok=True)
    (run_dir / "games").mkdir(parents=True, exist_ok=True)
    (run_dir / "dashboard").mkdir(parents=True, exist_ok=True)

    selected_games = manifest.get("games", [])
    manifest_copy = {
        **manifest,
        "source_manifest_path": str(manifest_path),
    }
    write_json(run_dir / "input_manifest.json", manifest_copy)

    run_state = {
        "run_id": run_id,
        "status": "created",
        "current_phase": "run_created",
        "created_at": utc_now(),
        "updated_at": utc_now(),
        "games_total": len(selected_games),
        "games_mirrored": 0,
        "games_integrity_passed": 0,
        "games_integrity_failed": 0,
        "games_transform_completed": 0,
        "games_transform_failed": 0,
        "notes": [
            "Game Remixer run scaffold created.",
            "No transform execution has occurred yet.",
        ],
    }
    write_json(run_dir / "run_state.json", run_state)

    for game in selected_games:
        game_id = game["game_id"]
        game_dir = run_dir / "games" / game_id
        game_dir.mkdir(parents=True, exist_ok=True)
        game_state = {
            "game_id": game_id,
            "display_name": game.get("display_name"),
            "source_path": game.get("source_path"),
            "input_mirror_path": str(run_dir / "input" / game_id),
            "working_clone_path": str(game_dir / "working"),
            "output_path": str(run_dir / "output" / game_id),
            "status": "created",
            "current_phase": "pending_input_mirror",
            "integrity_status": None,
            "attempt_count": 0,
            "last_error": None,
            "updated_at": utc_now(),
        }
        write_json(game_dir / "game_state.json", game_state)

    print(run_dir)


if __name__ == "__main__":
    main()