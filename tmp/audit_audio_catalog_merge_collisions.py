#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIBRARY_AUDIO_PATH = ROOT / "tools" / "library" / "audio_library" / "audios.json"
REFACTORING_AUDIO_PATH = ROOT / "tools" / "game_refactoring" / "catalogs" / "audios.json"
REPORT_PATH = ROOT / "tmp" / "audio_catalog_merge_collision_report.json"

ROLE_TO_INTENT = {
    "character footsteps movement action": "movement",
    "enemy attack hit danger": "enemy_attack",
    "npc interaction voice talk": "npc_interaction",
    "item pickup treasure resource": "item_pickup",
    "wind ambience environment air": "wind_ambience",
    "defeat fail death loss": "defeat",
}


def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value


def strip_variant_suffix(name: str) -> str:
    return re.sub(r"_\d+$", "", name)


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def build_library_records() -> list[dict[str, object]]:
    library = load_json(LIBRARY_AUDIO_PATH)
    records: list[dict[str, object]] = []
    for group, items in library.items():
        for item in items:
            name = item["name"]
            base_name = strip_variant_suffix(name)
            location = item.get("location", "")
            top_dir = Path(location).parts[0] if location else None
            category = "sfx" if top_dir in {"sfx", "ui"} else "music"
            records.append(
                {
                    "source": "library",
                    "group": group,
                    "name": name,
                    "base_name": base_name,
                    "candidate_id": base_name,
                    "category": category,
                    "location": location,
                    "usage": item.get("usage", ""),
                }
            )
    return records


def build_refactoring_records() -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for entry in load_json(REFACTORING_AUDIO_PATH):
        query = entry.get("query", "")
        tokens = query.split()
        biome = tokens[0] if tokens else "unknown"
        role = " ".join(tokens[1:]) if len(tokens) > 1 else "unknown"
        item_type = None
        items = entry.get("items", [])
        if items and isinstance(items[0], dict):
            item_type = items[0].get("type")
        intent = ROLE_TO_INTENT.get(role)
        if intent is None:
            if role.startswith("bgm ambient"):
                intent = "bgm"
            else:
                intent = slugify(role)
        candidate_id = f"{slugify(biome)}_{slugify(intent)}"
        records.append(
            {
                "source": "refactoring",
                "query": query,
                "biome": biome,
                "role": role,
                "intent": intent,
                "candidate_id": candidate_id,
                "category": "sfx" if item_type == "sfx" else "music",
                "usage": entry.get("usage", ""),
            }
        )
    return records


def main() -> int:
    library_records = build_library_records()
    refactoring_records = build_refactoring_records()

    library_candidate_map: dict[str, list[dict[str, object]]] = defaultdict(list)
    for record in library_records:
        library_candidate_map[str(record["candidate_id"])] .append(record)

    refactoring_candidate_map: dict[str, list[dict[str, object]]] = defaultdict(list)
    for record in refactoring_records:
        refactoring_candidate_map[str(record["candidate_id"])] .append(record)

    library_internal_collisions = {
        key: value for key, value in library_candidate_map.items() if len({r["group"] for r in value}) > 1
    }
    refactoring_internal_collisions = {
        key: value for key, value in refactoring_candidate_map.items() if len(value) > 1
    }

    direct_cross_id_overlaps = sorted(set(library_candidate_map).intersection(refactoring_candidate_map))

    report = {
        "paths": {
            "library": str(LIBRARY_AUDIO_PATH.relative_to(ROOT)),
            "refactoring": str(REFACTORING_AUDIO_PATH.relative_to(ROOT)),
        },
        "summary": {
            "library_variant_count": len(library_records),
            "library_candidate_id_count": len(library_candidate_map),
            "refactoring_record_count": len(refactoring_records),
            "refactoring_candidate_id_count": len(refactoring_candidate_map),
            "library_internal_collision_count": len(library_internal_collisions),
            "refactoring_internal_collision_count": len(refactoring_internal_collisions),
            "direct_cross_id_overlap_count": len(direct_cross_id_overlaps),
        },
        "library_internal_collisions": library_internal_collisions,
        "refactoring_internal_collisions": refactoring_internal_collisions,
        "direct_cross_id_overlaps": direct_cross_id_overlaps,
        "sample_library_ids": sorted(list(library_candidate_map))[:20],
        "sample_refactoring_ids": sorted(list(refactoring_candidate_map))[:20],
    }

    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"], ensure_ascii=False, indent=2))
    print(f"wrote {REPORT_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
