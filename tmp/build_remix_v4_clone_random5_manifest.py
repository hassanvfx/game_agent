#!/usr/bin/env python3
from __future__ import annotations

import json
import random
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW_GAMES_DIR = ROOT / "games" / "raw"
OUTPUT_PATH = ROOT / "tmp" / "game_refactoring_experiments" / "fixtures" / "remix_v4_clone_random5_raw_manifest.json"


def valid_game_dirs() -> list[Path]:
    if not RAW_GAMES_DIR.exists():
        raise SystemExit(f"Raw games directory not found: {RAW_GAMES_DIR}")
    candidates = [
        path
        for path in sorted(RAW_GAMES_DIR.iterdir())
        if path.is_dir() and (path / "index.html").exists()
    ]
    if len(candidates) < 5:
        raise SystemExit(f"Need at least 5 valid raw game folders with index.html, found {len(candidates)}")
    return candidates


def build_manifest(selected: list[Path]) -> dict:
    return {
        "run_label": "remix-v4-clone-random5-raw",
        "games": [
            {
                "game_id": path.name,
                "display_name": path.name,
                "source_path": str(path.resolve()),
            }
            for path in selected
        ],
    }


def main() -> None:
    candidates = valid_game_dirs()
    selected = random.sample(candidates, 5)
    payload = build_manifest(selected)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "manifest_path": str(OUTPUT_PATH),
                "selected_games": [path.name for path in selected],
                "candidate_count": len(candidates),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()