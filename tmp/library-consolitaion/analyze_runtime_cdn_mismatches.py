#!/usr/bin/env python3
"""Analyze runtime CDN/name mismatches from the published audio audit."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUDIT_PATH = ROOT / "tmp" / "library-consolitaion" / "published_game_audio_ref_audit.json"
AUDIOS_PATH = ROOT / "tools" / "library" / "assets" / "audios" / "audios.json"
CATALOG_FINAL_PATH = ROOT / "tools" / "library" / "assets" / "audios" / "catalog_final.json"
OUTPUT_PATH = ROOT / "tmp" / "library-consolitaion" / "runtime_cdn_mismatch_analysis.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_basename_index() -> dict[str, dict[str, list[str]]]:
    audios = load_json(AUDIOS_PATH)
    catalog_final = load_json(CATALOG_FINAL_PATH)

    audios_by_basename: dict[str, list[str]] = defaultdict(list)
    catalog_by_basename: dict[str, list[str]] = defaultdict(list)

    for items in audios.values():
        if not isinstance(items, list):
            continue
        for item in items:
            location = item.get("location")
            if isinstance(location, str) and location:
                audios_by_basename[Path(location).name].append(location)

    for record in catalog_final.get("records", []):
        if not isinstance(record, dict):
            continue
        for variant in record.get("variants", []) or []:
            location = variant.get("location")
            if isinstance(location, str) and location:
                catalog_by_basename[Path(location).name].append(location)

    return {
        "audios": {key: sorted(set(value)) for key, value in audios_by_basename.items()},
        "catalog": {key: sorted(set(value)) for key, value in catalog_by_basename.items()},
    }


def main() -> int:
    audit = load_json(AUDIT_PATH)
    index = build_basename_index()

    runtime_mismatches = audit.get("runtime_mismatches", [])
    focus = [
        item
        for item in runtime_mismatches
        if item.get("classification") in {
            "cdn_library_path_missing_from_catalog",
            "basename_only_audios_match",
        }
    ]

    by_location: dict[str, dict] = {}
    for item in focus:
        key = item.get("normalized_location") or item.get("reference")
        if key not in by_location:
            basename = item.get("basename") or ""
            by_location[key] = {
                "normalized_location": item.get("normalized_location"),
                "basename": basename,
                "classifications": Counter(),
                "gamezone_folders": set(),
                "source_files": set(),
                "audios_locations_for_basename": index["audios"].get(basename, []),
                "catalog_locations_for_basename": index["catalog"].get(basename, []),
            }
        entry = by_location[key]
        entry["classifications"][item.get("classification", "unknown")] += 1
        entry["gamezone_folders"].add(item.get("gamezone_folder"))
        entry["source_files"].add(item.get("source_file"))

    ranked = sorted(
        by_location.values(),
        key=lambda item: (-len(item["gamezone_folders"]), item.get("normalized_location") or ""),
    )

    payload = {
        "runtime_summary": audit.get("runtime_summary", {}),
        "focus_summary": {
            "focused_mismatch_reference_count": len(focus),
            "unique_normalized_location_count": len(ranked),
        },
        "top_locations": [
            {
                "normalized_location": item["normalized_location"],
                "basename": item["basename"],
                "classification_counts": dict(item["classifications"]),
                "game_count": len(item["gamezone_folders"]),
                "sample_games": sorted(item["gamezone_folders"])[:10],
                "sample_files": sorted(item["source_files"])[:10],
                "audios_locations_for_basename": item["audios_locations_for_basename"],
                "catalog_locations_for_basename": item["catalog_locations_for_basename"],
            }
            for item in ranked[:100]
        ],
    }

    OUTPUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload["runtime_summary"], ensure_ascii=False, indent=2))
    print(json.dumps(payload["focus_summary"], ensure_ascii=False, indent=2))
    for item in payload["top_locations"][:15]:
        print(json.dumps(item, ensure_ascii=False))
    print(f"wrote {OUTPUT_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
