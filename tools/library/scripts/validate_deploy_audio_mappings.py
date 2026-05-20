#!/usr/bin/env python3
"""Validate and summarize deploy-audio compatibility mappings."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_MANIFEST = ROOT / "tools" / "library" / "assets" / "audios" / "deploy_audio_mappings.json"
DEFAULT_AUDIOS = ROOT / "tools" / "library" / "assets" / "audios" / "audios.json"
DEFAULT_MISMATCH_ANALYSIS = ROOT / "tmp" / "library-consolitaion" / "runtime_cdn_mismatch_analysis.json"

FOCUS_CLASSIFICATIONS = {
    "cdn_library_path_missing_from_catalog",
    "basename_only_audios_match",
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_known_locations(audios_payload: dict) -> set[str]:
    locations: set[str] = set()
    for items in audios_payload.values():
        if not isinstance(items, list):
            continue
        for item in items:
            location = item.get("location")
            if isinstance(location, str) and location:
                locations.add(location)
    return locations


def main() -> int:
    manifest = load_json(DEFAULT_MANIFEST)
    audios_payload = load_json(DEFAULT_AUDIOS)
    mismatch_analysis = load_json(DEFAULT_MISMATCH_ANALYSIS)

    known_locations = build_known_locations(audios_payload)
    reduced = manifest.get("reduced_aliases", [])
    enriched = manifest.get("enriched_aliases", [])
    all_aliases = reduced + enriched

    missing_sources = sorted(
        {
            item.get("source_location")
            for item in all_aliases
            if isinstance(item, dict)
            and isinstance(item.get("source_location"), str)
            and item["source_location"] not in known_locations
        }
    )

    covered_paths = {
        item.get("requested_path")
        for item in all_aliases
        if isinstance(item, dict) and isinstance(item.get("requested_path"), str)
    }

    focused_paths = {
        item.get("normalized_location")
        for item in mismatch_analysis.get("top_locations", [])
        if isinstance(item, dict)
        and isinstance(item.get("normalized_location"), str)
        and any(key in FOCUS_CLASSIFICATIONS for key in (item.get("classification_counts") or {}).keys())
    }

    uncovered_paths = sorted(path for path in focused_paths if path not in covered_paths)

    payload = {
        "manifest_path": str(DEFAULT_MANIFEST.relative_to(ROOT)),
        "reduced_alias_count": len(reduced),
        "enriched_alias_count": len(enriched),
        "covered_requested_path_count": len(covered_paths),
        "focused_runtime_unique_path_count": len(focused_paths),
        "focused_runtime_covered_count": len(focused_paths) - len(uncovered_paths),
        "focused_runtime_uncovered_paths": uncovered_paths,
        "missing_source_locations": missing_sources,
        "sanitize_to_empty_prefixes": manifest.get("sanitize_to_empty_prefixes", []),
    }

    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
