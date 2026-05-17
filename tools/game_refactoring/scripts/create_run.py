#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RUNS_ROOT = ROOT / "runs"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def default_run_id() -> str:
    return f"run_game_remixer_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def validate_optional_remix_prompt(value: Any, field_path: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise SystemExit(f"{field_path} must be a non-empty string when present")
    return value.strip()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a timestamped Game Remixer run scaffold.")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--run-id")
    parser.add_argument(
        "--runs-root",
        help="Optional custom root directory under which the run directory should be created. Defaults to the repo-local runs/ directory.",
    )
    parser.add_argument(
        "--source-mode",
        choices=["copy", "inplace"],
        default="copy",
        help="How source game directories should be prepared for execution.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_id = args.run_id or default_run_id()
    runs_root = Path(args.runs_root).resolve() if args.runs_root else RUNS_ROOT
    run_dir = runs_root / run_id
    if run_dir.exists():
        raise SystemExit(f"Run directory already exists: {run_dir}")

    manifest_path = Path(args.manifest).resolve()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    (run_dir / "input").mkdir(parents=True, exist_ok=True)
    (run_dir / "output").mkdir(parents=True, exist_ok=True)
    (run_dir / "games").mkdir(parents=True, exist_ok=True)
    (run_dir / "dashboard").mkdir(parents=True, exist_ok=True)

    selected_games = manifest.get("games", [])
    if not isinstance(selected_games, list):
        raise SystemExit(f"Manifest must contain a games list: {manifest_path}")

    manifest_remix_prompt = validate_optional_remix_prompt(manifest.get("remix_prompt"), "manifest field 'remix_prompt'")

    for index, game in enumerate(selected_games):
        if not isinstance(game, dict):
            raise SystemExit(f"games[{index}] must be an object in manifest: {manifest_path}")
        game_id = game.get("game_id", "<unknown>")
        game_remix_prompt = validate_optional_remix_prompt(game.get("remix_prompt"), f"games[{index}].remix_prompt")
        if game_remix_prompt is not None:
            game["remix_prompt"] = game_remix_prompt
        source_path_value = game.get("source_path")
        if not isinstance(source_path_value, str) or not source_path_value.strip():
            raise SystemExit(f"Game '{game_id}' is missing a non-empty source_path in manifest: {manifest_path}")
        source_path = Path(source_path_value).resolve()
        if not source_path.exists():
            raise SystemExit(f"Game '{game_id}' source_path does not exist: {source_path}")
        if not source_path.is_dir():
            raise SystemExit(f"Game '{game_id}' source_path is not a directory: {source_path}")
    manifest_copy = {
        **manifest,
        "source_manifest_path": str(manifest_path),
    }
    write_json(run_dir / "input_manifest.json", manifest_copy)

    run_state = {
        "run_id": run_id,
        "run_dir": str(run_dir),
        "runs_root": str(runs_root),
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
        "source_mode": args.source_mode,
        "manifest_remix_prompt": manifest_remix_prompt,
        "notes": [
            "Game Remixer run scaffold created.",
            "No transform execution has occurred yet.",
            f"Source mode configured: {args.source_mode}.",
            f"Runs root configured: {runs_root}.",
        ],
    }
    write_json(run_dir / "run_state.json", run_state)

    for game in selected_games:
        game_id = game["game_id"]
        game_dir = run_dir / "games" / game_id
        game_dir.mkdir(parents=True, exist_ok=True)
        game_state = {
            "game_id": game_id,
            "original_game_id": game.get("original_game_id"),
            "source_entry_id": game.get("source_entry_id"),
            "display_name": game.get("display_name"),
            "source_path": game.get("source_path"),
            "source_url": game.get("source_url"),
            "match_rank": game.get("match_rank"),
            "mechanic_name": game.get("mechanic_name"),
            "matcher_context": game.get("matcher_context"),
            "manifest_remix_prompt": game.get("remix_prompt"),
            "source_mode": args.source_mode,
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