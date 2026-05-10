#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

REPO_ROOT = Path("/Users/hassan/repos/game_agent")
PUBLISHED_ROOT = REPO_ROOT / "games/published/public"
REAL_107_SUMMARY = REPO_ROOT / "tmp/deploy_real_top107_legacy_summary.json"
ADAPTED_124 = REPO_ROOT / "tmp/adapted_game_json_124.json"
OUTPUT_PATH = REPO_ROOT / "tmp/merged_107_124_uniqueness_audit.json"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_107_entries() -> list[dict[str, str]]:
    payload = load_json(REAL_107_SUMMARY)
    return payload["results"]


def build_124_entries() -> list[dict[str, str]]:
    payload = load_json(ADAPTED_124)
    raw_entries = payload["results"] if isinstance(payload, dict) and isinstance(payload.get("results"), list) else payload

    entries: list[dict[str, str]] = []
    for item in raw_entries:
        game_id = str(item["game_id"])
        remix_uuid = str(item["remix_uuid"]).replace("remix-", "")
        entries.append(
            {
                "source": str(item["source"]),
                "game_id": game_id,
                "remix_uuid": remix_uuid,
                "composite_key": f"{game_id}__remix-{remix_uuid}",
                "group": "run_124",
            }
        )
    return entries


def normalize_107_entries(raw_entries: list[dict[str, Any]]) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    for item in raw_entries:
        game_id = str(item["game_id"])
        remix_uuid = str(item["remix_uuid"]).replace("remix-", "")
        entries.append(
            {
                "source": str(item["source"]),
                "game_id": game_id,
                "remix_uuid": remix_uuid,
                "composite_key": f"{game_id}__remix-{remix_uuid}",
                "group": "legacy_107",
            }
        )
    return entries


def main() -> None:
    entries_107 = normalize_107_entries(load_107_entries())
    entries_124 = build_124_entries()
    merged = entries_107 + entries_124

    remix_counts = Counter(item["remix_uuid"] for item in merged)
    composite_counts = Counter(item["composite_key"] for item in merged)
    game_counts = Counter(item["game_id"] for item in merged)

    repeated_games = {key: count for key, count in game_counts.items() if count > 1}
    repeated_remix_ids = {key: count for key, count in remix_counts.items() if count > 1}
    repeated_composites = {key: count for key, count in composite_counts.items() if count > 1}

    by_game: dict[str, list[dict[str, str]]] = defaultdict(list)
    for item in merged:
        if game_counts[item["game_id"]] > 1:
            by_game[item["game_id"]].append(
                {
                    "group": item["group"],
                    "remix_uuid": item["remix_uuid"],
                    "composite_key": item["composite_key"],
                    "source": item["source"],
                }
            )

    summary = {
        "legacy_107_count": len(entries_107),
        "run_124_count": len(entries_124),
        "merged_total_count": len(merged),
        "unique_game_id_count": len(game_counts),
        "unique_remix_uuid_count": len(remix_counts),
        "unique_composite_key_count": len(composite_counts),
        "repeated_game_id_count": len(repeated_games),
        "repeated_remix_uuid_count": len(repeated_remix_ids),
        "repeated_composite_key_count": len(repeated_composites),
        "repeated_game_ids": repeated_games,
        "repeated_remix_ids": repeated_remix_ids,
        "repeated_composite_keys": repeated_composites,
        "sample_repeated_game_details": dict(list(by_game.items())[:20]),
    }

    OUTPUT_PATH.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(OUTPUT_PATH), **summary}, indent=2))


if __name__ == "__main__":
    main()