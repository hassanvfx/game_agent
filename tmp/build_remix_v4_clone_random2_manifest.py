#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_MANIFEST = ROOT / "tmp" / "game_refactoring_experiments" / "fixtures" / "remix_v4_clone_random5_raw_manifest.json"
OUTPUT_MANIFEST = ROOT / "tmp" / "game_refactoring_experiments" / "fixtures" / "remix_v4_clone_random2_raw_manifest.json"


def main() -> None:
    payload = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    games = payload.get("games")
    if not isinstance(games, list) or len(games) < 2:
        raise SystemExit(f"Need at least 2 games in source manifest: {SOURCE_MANIFEST}")

    kept = games[:2]
    omitted = games[2:]

    output_payload = {
        "run_label": "remix-v4-clone-random2-raw",
        "games": kept,
        "omitted_games_from_random5_source": [game.get("game_id") for game in omitted],
        "source_manifest": str(SOURCE_MANIFEST),
    }

    OUTPUT_MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_MANIFEST.write_text(json.dumps(output_payload, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "output_manifest": str(OUTPUT_MANIFEST),
                "kept_games": [game.get("game_id") for game in kept],
                "omitted_games": [game.get("game_id") for game in omitted],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()