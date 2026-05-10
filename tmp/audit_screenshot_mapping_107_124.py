#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path("/Users/hassan/repos/game_agent")
MERGED_APP_PATH = ROOT / "games/published/public/vatsal_app_alpha-app.json"
MERGED_MANIFEST_PATH = ROOT / "tmp/retry_manifests/vatsal_app_alpha_231_manifest.json"
ADAPTED_124_PATH = ROOT / "tmp/adapted_game_json_124.json"
OUTPUT_PATH = ROOT / "tmp/screenshot_mapping_107_124_audit.json"

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def list_images(path: Path) -> list[str]:
    if not path.exists() or not path.is_dir():
        return []
    return sorted(
        p.relative_to(path).as_posix()
        for p in path.rglob("*")
        if p.is_file() and not p.name.startswith("._") and p.suffix.lower() in IMAGE_SUFFIXES
    )


def load_124_source_map() -> dict[str, dict[str, Any]]:
    payload = load_json(ADAPTED_124_PATH)
    return {entry["composite_key"] if "composite_key" in entry else f'{entry["game_id"]}__{entry["remix_id"]}': entry for entry in payload["results"]}


def main() -> None:
    merged_app = load_json(MERGED_APP_PATH)
    merged_manifest = load_json(MERGED_MANIFEST_PATH)
    manifest_entries = {entry["composite_key"]: entry for entry in merged_manifest["entries"]}
    source_124 = load_124_source_map()

    empty_items = []
    for composite_key, item in merged_app.items():
        screenshots = item.get("screenshots") or []
        if screenshots:
            continue

        manifest_entry = manifest_entries.get(composite_key, {})
        published_path = manifest_entry.get("published_path", "")
        variant_group = manifest_entry.get("variant_group", "unknown")
        published_dir = ROOT / "games/published/public" / published_path if published_path else None
        published_images = list_images(published_dir) if published_dir else []

        if variant_group == "legacy_107":
            source_dir = ROOT / "games/raw" / manifest_entry["game_id"]
        else:
            source_entry = source_124.get(composite_key)
            source_dir = Path(source_entry["source"]) if source_entry else None

        source_images = list_images(source_dir) if source_dir else []
        metadata_path = None
        metadata = {}
        if published_dir and published_dir.exists():
            candidates = sorted(published_dir.glob("game-obfuscated-*.json"))
            if candidates:
                metadata_path = candidates[0]
                metadata = load_json(metadata_path)

        empty_items.append(
            {
                "composite_key": composite_key,
                "variant_group": variant_group,
                "published_path": published_path,
                "source_dir": str(source_dir) if source_dir else None,
                "published_dir": str(published_dir) if published_dir else None,
                "source_image_count": len(source_images),
                "published_image_count": len(published_images),
                "source_images_sample": source_images[:20],
                "published_images_sample": published_images[:20],
                "metadata_screenshots_png": metadata.get("screenshots_png", []),
                "metadata_screenshots_jpg": metadata.get("screenshots_jpg", []),
            }
        )

    payload = {
        "empty_screenshot_entry_count": len(empty_items),
        "items": empty_items,
    }
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(OUTPUT_PATH), "empty_screenshot_entry_count": len(empty_items)}, indent=2))


if __name__ == "__main__":
    main()