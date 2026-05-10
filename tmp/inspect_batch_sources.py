#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path("/Users/hassan/repos/game_agent")
SELECTED_50 = ROOT / "tmp/retry_manifests/latest_selected_remix_deploy_manifest.json"
TOP107 = ROOT / "tmp/game_refactoring_experiments/fixtures/top107_vatsal_raw_backed_full_manifest.json"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    selected = load_json(SELECTED_50)
    top107 = load_json(TOP107)

    selected_count = len(selected) if isinstance(selected, list) else 0
    top107_games = top107.get("games", []) if isinstance(top107, dict) else []
    top107_count = len(top107_games)

    selected_ids = sorted(Path(item["source"]).name for item in selected if isinstance(item, dict) and item.get("source"))
    top107_ids = sorted(item["game_id"] for item in top107_games if isinstance(item, dict) and item.get("game_id"))

    overlap = sorted(set(selected_ids) & set(top107_ids))
    selected_only = sorted(set(selected_ids) - set(top107_ids))
    top107_only = sorted(set(top107_ids) - set(selected_ids))

    payload = {
        "selected_50_count": selected_count,
        "top107_count": top107_count,
        "union_count": len(set(selected_ids) | set(top107_ids)),
        "overlap_count": len(overlap),
        "selected_ids_sample": selected_ids[:10],
        "top107_ids_sample": top107_ids[:10],
        "overlap_ids_sample": overlap[:10],
        "selected_only_sample": selected_only[:10],
        "top107_only_sample": top107_only[:10],
    }

    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()