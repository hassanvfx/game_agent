from __future__ import annotations

import json
from pathlib import Path


ROOT = Path("/Users/hassan/repos/game_agent")
RUN_ROOT = Path("/Volumes/HDD2026/output-May17th/run_game_remixer_20260517T132133Z/output")
TARGET_GAME_ID = "gamezone-577959e6-a8d8-4fa9-a894-8544de02aa16"
TARGET_REMIX_ID = "remix-49f979f1666148b922e7051c56563dc1"
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}


def load_json(path: Path):
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def inspect_source_dir(path: Path) -> dict:
    identity = None
    for candidate in [path / "Identity.json", path / "identity.json"]:
        if candidate.exists() and not candidate.name.startswith("._"):
            try:
                identity = json.loads(candidate.read_text(encoding="utf-8"))
            except Exception:
                identity = None
            break
    top_level_images = [
        child.name
        for child in sorted(path.iterdir())
        if child.is_file() and child.suffix.lower() in IMAGE_SUFFIXES and not child.name.startswith("._")
    ]
    return {
        "path": str(path),
        "dir_name": path.name,
        "identity_title": (identity or {}).get("title"),
        "identity_game_id": (identity or {}).get("game_id"),
        "top_level_images": top_level_images,
        "top_level_png_count": sum(1 for name in top_level_images if name.lower().endswith(".png")),
        "has_recreation_prompt": (path / "RecreationPrompt.md").exists() or (path / "recreation_prompt.md").exists(),
        "has_blueprint": (path / "Blueprint.md").exists() or (path / "blueprint.md").exists(),
    }


def find_source_dirs() -> list[Path]:
    if not RUN_ROOT.exists():
        return []
    return sorted(path for path in RUN_ROOT.iterdir() if path.is_dir() and path.name.startswith(TARGET_GAME_ID))


def extract_record_summary(record: dict | None) -> dict | None:
    if not isinstance(record, dict):
        return None
    return {
        "game_id": record.get("game_id"),
        "remix_id": record.get("remix_id"),
        "published_path": record.get("published_path"),
        "title": record.get("title"),
        "description": record.get("description"),
        "screenshots_count": len(record.get("screenshots") or []),
        "screenshots_sample": (record.get("screenshots") or [])[:5],
    }


def find_catalog_record(path: Path) -> dict:
    payload = load_json(path) or {}
    key = f"{TARGET_GAME_ID}__{TARGET_REMIX_ID}"
    direct = payload.get(key)
    matched_keys = sorted(k for k in payload.keys() if TARGET_GAME_ID in k)
    return {
        "catalog_path": str(path),
        "direct_key": key,
        "direct_match": extract_record_summary(direct),
        "matched_keys": matched_keys[:20],
        "matched_key_count": len(matched_keys),
    }


def find_published_dirs(root: Path) -> dict:
    game_dir = root / TARGET_GAME_ID
    remix_dir = game_dir / TARGET_REMIX_ID
    summary = {
        "root": str(root),
        "game_dir_exists": game_dir.exists(),
        "remix_dir_exists": remix_dir.exists(),
        "metadata_files": [],
        "screenshot_files": [],
    }
    if remix_dir.exists():
        summary["metadata_files"] = sorted(path.name for path in remix_dir.glob("game-obfuscated-*.json"))
        shots_dir = remix_dir / "screenshots"
        if shots_dir.exists():
            summary["screenshot_files"] = sorted(path.name for path in shots_dir.iterdir() if path.is_file())[:10]
    return summary


def main() -> None:
    source_dirs = find_source_dirs()
    payload = {
        "target_game_id": TARGET_GAME_ID,
        "target_remix_id": TARGET_REMIX_ID,
        "source_dirs_found": [inspect_source_dir(path) for path in source_dirs],
        "public_catalog": find_catalog_record(ROOT / "games/published/public/app.json"),
        "obfuscated_catalog": find_catalog_record(ROOT / "games/published/obfuscated/app.json"),
        "public_dirs": find_published_dirs(ROOT / "games/published/public"),
        "obfuscated_dirs": find_published_dirs(ROOT / "games/published/obfuscated"),
    }
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()