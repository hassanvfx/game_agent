#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path("/Users/hassan/repos/game_agent")
PUBLISHED_PUBLIC_ROOT = ROOT / "games/published/public"
REAL_107_SUMMARY = ROOT / "tmp/deploy_real_top107_legacy_summary.json"
ADAPTED_124 = ROOT / "tmp/adapted_game_json_124.json"
OUTPUT_PATH = ROOT / "tmp/retry_manifests/vatsal_app_alpha_231_manifest.json"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def composite_key(game_id: str, remix_id: str) -> str:
    return f"{game_id}__{remix_id}"


def normalize_107_entries() -> list[dict[str, Any]]:
    payload = load_json(REAL_107_SUMMARY)
    entries = payload["results"]
    normalized: list[dict[str, Any]] = []
    for item in entries:
        game_id = str(item["game_id"])
        remix_id = f"remix-{str(item['remix_uuid']).removeprefix('remix-')}"
        normalized.append(
            {
                "game_id": game_id,
                "remix_id": remix_id,
                "composite_key": composite_key(game_id, remix_id),
                "published_path": f"{game_id}/{remix_id}",
                "variant_group": "legacy_107",
                "source": str(item["source"]),
            }
        )
    return normalized


def normalize_124_entries() -> list[dict[str, Any]]:
    payload = load_json(ADAPTED_124)
    entries = payload["results"]
    normalized: list[dict[str, Any]] = []
    for item in entries:
        game_id = str(item["game_id"])
        remix_id = str(item["remix_id"])
        normalized.append(
            {
                "game_id": game_id,
                "remix_id": remix_id,
                "composite_key": composite_key(game_id, remix_id),
                "published_path": f"{game_id}/{remix_id}",
                "variant_group": "run_124",
                "source": str(item["source"]),
            }
        )
    return normalized


def main() -> None:
    entries_107 = normalize_107_entries()
    entries_124 = normalize_124_entries()
    entries = entries_107 + entries_124

    seen: set[str] = set()
    duplicates: dict[str, int] = {}
    for entry in entries:
        key = entry["composite_key"]
        if key in seen:
            duplicates[key] = duplicates.get(key, 1) + 1
        seen.add(key)

    payload = {
        "batch_name": "vatsal_app_alpha_231",
        "collection_slug": "vatsal_app_alpha",
        "generated_at": "2026-05-10T00:00:00Z",
        "published_root": str(PUBLISHED_PUBLIC_ROOT),
        "entries": entries,
        "summary": {
            "legacy_107_count": len(entries_107),
            "run_124_count": len(entries_124),
            "total_entries": len(entries),
            "unique_composite_keys": len(seen),
            "duplicate_keys": duplicates,
        },
    }

    OUTPUT_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output_path": str(OUTPUT_PATH), **payload["summary"]}, indent=2))


if __name__ == "__main__":
    main()