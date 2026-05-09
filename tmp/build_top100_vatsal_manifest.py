#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path("/Users/hassan/repos/game_agent")
SOURCE_ROOT = ROOT / "games" / "top100_vatsal"
OUTPUT_PATH = ROOT / "tmp" / "game_refactoring_experiments" / "fixtures" / "top100_vatsal_full_manifest.json"

games = []
for source_dir in sorted(path for path in SOURCE_ROOT.iterdir() if path.is_dir()):
    games.append(
        {
            "game_id": source_dir.name,
            "display_name": source_dir.name,
            "source_path": str(source_dir.resolve()),
        }
    )

payload = {
    "run_label": "top100-vatsal-full-harry-potter",
    "games": games,
}

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
OUTPUT_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

print(OUTPUT_PATH)
print(len(games))