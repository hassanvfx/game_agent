#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


RUN_DIR = Path("/Volumes/hdd2026/output-May17th/run_game_remixer_20260517T132133Z")
INPUT_MANIFEST_PATH = RUN_DIR / "input_manifest.json"
GAMES_DIR = RUN_DIR / "games"
OUT_MANIFEST_PATH = RUN_DIR / "import_manifest.json"


def main() -> int:
    payload = json.loads(INPUT_MANIFEST_PATH.read_text(encoding="utf-8"))
    games = payload.get("games", [])
    if not isinstance(games, list):
        raise SystemExit("input_manifest.json missing 'games' array")

    entries: list[str] = []
    missing_game_ids: list[str] = []

    for item in games:
        if not isinstance(item, dict):
            continue
        game_id = item.get("game_id")
        if not isinstance(game_id, str) or not game_id:
            continue

        source_dir = GAMES_DIR / game_id
        if source_dir.is_dir():
            entries.append(str(source_dir.resolve()))
        else:
            missing_game_ids.append(game_id)

    effective_entries = sorted(dict.fromkeys(entries))
    OUT_MANIFEST_PATH.write_text(
        json.dumps(effective_entries, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    summary = {
        "run_dir": str(RUN_DIR),
        "input_game_count": len(games),
        "import_manifest_path": str(OUT_MANIFEST_PATH),
        "effective_import_item_count": len(effective_entries),
        "missing_game_dir_count": len(missing_game_ids),
        "sample_missing_game_ids": missing_game_ids[:10],
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
