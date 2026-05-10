#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path("/Users/hassan/repos/game_agent")
MANIFEST_PATH = ROOT / "tmp/retry_manifests/vatsaltop100_app_alpha_batch_manifest.json"
INDEX_PATH = ROOT / "games/published/index.json"
APP_TAGS_PATH = ROOT / "games/published/app_tags.json"
APP_PATH = ROOT / "games/published/app.json"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    manifest = load_json(MANIFEST_PATH)
    entries = manifest["entries"]
    manifest_keys = {entry["composite_key"] for entry in entries}

    output = {
        "manifest_entries": len(entries),
        "manifest_unique_keys": len(manifest_keys),
    }

    for name, path in {
        "index": INDEX_PATH,
        "app_tags": APP_TAGS_PATH,
        "app": APP_PATH,
    }.items():
        payload = load_json(path)
        keys = set(payload.keys())
        sample_record = payload[next(iter(sorted(keys)))] if keys else {}
        output[f"{name}_entries"] = len(payload)
        output[f"{name}_matches_manifest"] = keys == manifest_keys
        output[f"{name}_has_lineage_fields"] = all(
            field in sample_record
            for field in ["game_id", "remix_id", "published_path", "remix_parent_id", "root_game_id", "lineage_depth"]
        )

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()