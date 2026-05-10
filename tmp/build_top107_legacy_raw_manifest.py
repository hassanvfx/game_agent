#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

SOURCE_MANIFEST = Path("/Users/hassan/repos/game_agent/tmp/game_refactoring_experiments/fixtures/top107_vatsal_raw_backed_harry_potter_manifest.json")
OUTPUT_MANIFEST = Path("/Users/hassan/repos/game_agent/tmp/retry_manifests/top107_legacy_raw_manifest.json")


def main() -> None:
    payload = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    games = payload.get("games", [])
    entries = [
        {
            "game_id": game["game_id"],
            "source": game["source_path"],
        }
        for game in games
    ]
    output = {
        "source_manifest": str(SOURCE_MANIFEST),
        "entry_count": len(entries),
        "entries": entries,
    }
    OUTPUT_MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_MANIFEST.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(OUTPUT_MANIFEST), "entry_count": len(entries)}, indent=2))


if __name__ == "__main__":
    main()