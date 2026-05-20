#!/usr/bin/env python3
"""
Generate a filter vocabulary manifest from app.json.

Outputs:
- home_filter_manifest.json

The manifest contains:
- distinct vocabularies per tag category
- per-game normalized memberships
- lightweight counts to power a pill-based pro filter UI
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


TAG_FIELDS = {
    "semantic_tags": "semantics",
    "mechanic_tags": "mechanics",
    "mood_tags": "moods",
    "franchise_tags": "franchises",
    "setting_tags": "settings",
    "character_tags": "characters",
    "games_tags": "references",
}


def normalize_list(value: Any) -> list[str]:
    if not value:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    string_value = str(value).strip()
    return [string_value] if string_value else []


def ensure_output_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("catalog_path", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("tmp/home_curation"))
    args = parser.parse_args()

    raw = json.loads(args.catalog_path.read_text())
    ensure_output_dir(args.output_dir)

    vocabulary_counters: dict[str, Counter[str]] = {
        manifest_key: Counter() for manifest_key in TAG_FIELDS.values()
    }
    game_memberships: dict[str, dict[str, list[str]]] = {}

    for game_id, payload in raw.items():
        memberships: dict[str, list[str]] = {}

        for source_key, manifest_key in TAG_FIELDS.items():
            values = normalize_list(payload.get(source_key))
            memberships[manifest_key] = values
            vocabulary_counters[manifest_key].update(values)

        game_memberships[game_id] = memberships

    vocabularies = {
        key: [
            {
                "value": value,
                "count": count
            }
            for value, count in counter.most_common()
        ]
        for key, counter in vocabulary_counters.items()
    }

    manifest = {
        "catalog_path": str(args.catalog_path),
        "categories": list(TAG_FIELDS.values()),
        "vocabularies": vocabularies,
        "games": game_memberships,
    }

    output_path = args.output_dir / "home_filter_manifest.json"
    output_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Wrote filter manifest to: {output_path}")
    for category, values in vocabularies.items():
        print(f"{category}: {len(values)} values")


if __name__ == "__main__":
    main()