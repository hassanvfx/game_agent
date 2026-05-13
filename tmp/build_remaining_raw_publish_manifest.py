#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SUMMARY_PATH = REPO_ROOT / "tmp" / "remaining_raw_from_231_summary.json"
OUTPUT_PATH = REPO_ROOT / "tmp" / "remaining_raw_publish_manifest.json"


def main() -> None:
    summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    remaining_ids = summary["remaining_ids"]

    manifest = {
        "batch_name": "remaining_raw_not_in_vatsal_app_alpha_231",
        "collection_slug": "vatsal_app_alpha_remaining_raw",
        "generated_from": {
            "raw_root": summary["raw_root"],
            "excluded_manifest": summary["manifest_path"],
            "excluded_unique_gamezone_ids": summary["covered_unique_gamezone_ids"],
        },
        "entry_count": len(remaining_ids),
        "entries": [
            {
                "game_id": game_id,
                "published_path": game_id,
                "source": str(REPO_ROOT / "games" / "raw" / game_id),
            }
            for game_id in remaining_ids
        ],
    }

    OUTPUT_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    preview = {
        "output_path": str(OUTPUT_PATH),
        "entry_count": manifest["entry_count"],
        "first_25_game_ids": remaining_ids[:25],
    }
    print(json.dumps(preview, indent=2))


if __name__ == "__main__":
    main()