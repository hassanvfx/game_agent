#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path("/Users/hassan/repos/game_agent")
DEFAULT_APP_TAGS_PATH = ROOT / "games/published/app_tags.json"
DEFAULT_APP_PATH = ROOT / "games/published/app.json"
DEFAULT_INDEX_PATH = ROOT / "games/published/index.json"
DEFAULT_BATCH_MANIFEST = ROOT / "tmp/retry_manifests/latest_selected_remix_catalog_manifest.json"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def required_keys_from_manifest(manifest_path: Path) -> list[str]:
    payload = load_json(manifest_path)
    if isinstance(payload, dict):
        entries = payload.get("entries")
        games = payload.get("games")
        items = entries if isinstance(entries, list) else games
    else:
        items = payload
    if not isinstance(items, list):
        raise ValueError("Manifest must contain a top-level 'entries' list, a 'games' list, or be a list itself")

    keys: list[str] = []
    for item in items:
        if not isinstance(item, dict):
            continue

        published_path = str(item.get("published_path") or "").strip()
        if published_path:
            parts = Path(published_path).parts
            if len(parts) == 2:
                game_id, remix_id = parts
            else:
                game_id = remix_id = ""
        else:
            source_path = Path(str(item.get("source_path") or ""))
            game_id = str(item.get("game_id") or source_path.parts[-2] if len(source_path.parts) >= 2 else "").strip()
            remix_id = source_path.name.strip()

        if game_id.startswith("gamezone-") and remix_id.startswith("remix-"):
            keys.append(f"{game_id}__{remix_id}")
    return sorted(set(keys))


def summarize_catalog(
    payload: dict[str, Any],
    required_keys: list[str],
    require_blueprint: bool = False,
    require_prompt: bool = False,
) -> dict[str, Any]:
    missing_entries = [key for key in required_keys if key not in payload]
    empty_titles: list[str] = []
    empty_descriptions: list[str] = []
    empty_screenshots: list[str] = []
    empty_mechanics: list[str] = []
    empty_semantics: list[str] = []
    empty_moods: list[str] = []
    empty_blurbs: list[str] = []
    empty_blueprints: list[str] = []

    for key in required_keys:
        record = payload.get(key)
        if not isinstance(record, dict):
            continue

        title = str(record.get("title") or "").strip()
        description = str(record.get("description") or "").strip()
        screenshots = normalize_string_list(record.get("screenshots"))
        mechanic_tags = normalize_string_list(record.get("mechanic_tags"))
        semantic_tags = normalize_string_list(record.get("semantic_tags"))
        mood_tags = normalize_string_list(record.get("mood_tags"))
        blueprint = str(record.get("blueprint") or "").strip()
        prompt = str(record.get("prompt") or "").strip()

        if not title:
            empty_titles.append(key)
        if not description:
            empty_descriptions.append(key)
        if not screenshots:
            empty_screenshots.append(key)
        if not mechanic_tags:
            empty_mechanics.append(key)
        if not semantic_tags:
            empty_semantics.append(key)
        if not mood_tags:
            empty_moods.append(key)
        if require_prompt and not prompt:
            empty_blurbs.append(key)
        if require_blueprint and not blueprint:
            empty_blueprints.append(key)

    return {
        "required_entry_count": len(required_keys),
        "present_entry_count": len([key for key in required_keys if key in payload]),
        "missing_entries_count": len(missing_entries),
        "missing_entries_sample": missing_entries[:10],
        "empty_titles_count": len(empty_titles),
        "empty_titles_sample": empty_titles[:10],
        "empty_descriptions_count": len(empty_descriptions),
        "empty_descriptions_sample": empty_descriptions[:10],
        "empty_screenshots_count": len(empty_screenshots),
        "empty_screenshots_sample": empty_screenshots[:10],
        "empty_mechanic_tags_count": len(empty_mechanics),
        "empty_mechanic_tags_sample": empty_mechanics[:10],
        "empty_semantic_tags_count": len(empty_semantics),
        "empty_semantic_tags_sample": empty_semantics[:10],
        "empty_mood_tags_count": len(empty_moods),
        "empty_mood_tags_sample": empty_moods[:10],
        "empty_prompt_count": len(empty_blurbs) if require_prompt else None,
        "empty_prompt_sample": empty_blurbs[:10] if require_prompt else None,
        "empty_blueprint_count": len(empty_blueprints) if require_blueprint else None,
        "empty_blueprint_sample": empty_blueprints[:10] if require_blueprint else None,
    }


def summarize_index(payload: dict[str, Any], required_keys: list[str]) -> dict[str, Any]:
    missing_entries = [key for key in required_keys if key not in payload]
    empty_game_json: list[str] = []
    empty_screenshots: list[str] = []

    for key in required_keys:
        record = payload.get(key)
        if not isinstance(record, dict):
            continue
        game_json = str(record.get("game_json") or "").strip()
        screenshots = normalize_string_list(record.get("screenshots_jpg")) or normalize_string_list(record.get("screenshots_png"))
        if not game_json:
            empty_game_json.append(key)
        if not screenshots:
            empty_screenshots.append(key)

    return {
        "required_entry_count": len(required_keys),
        "present_entry_count": len([key for key in required_keys if key in payload]),
        "missing_entries_count": len(missing_entries),
        "missing_entries_sample": missing_entries[:10],
        "empty_game_json_count": len(empty_game_json),
        "empty_game_json_sample": empty_game_json[:10],
        "empty_index_screenshots_count": len(empty_screenshots),
        "empty_index_screenshots_sample": empty_screenshots[:10],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Deterministic QA checks for generated published metadata.")
    parser.add_argument("--app-tags", default=str(DEFAULT_APP_TAGS_PATH))
    parser.add_argument("--app-json", default=str(DEFAULT_APP_PATH))
    parser.add_argument("--index-json", default=str(DEFAULT_INDEX_PATH))
    parser.add_argument("--manifest", default=str(DEFAULT_BATCH_MANIFEST))
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero if any required field coverage is missing for the target batch.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    app_tags = load_json(Path(args.app_tags))
    app = load_json(Path(args.app_json))
    index = load_json(Path(args.index_json))
    required_keys = required_keys_from_manifest(Path(args.manifest))

    payload = {
        "manifest": {
            "path": str(Path(args.manifest)),
            "required_entry_count": len(required_keys),
            "required_keys_sample": required_keys[:10],
        },
        "app_tags": summarize_catalog(app_tags, required_keys, require_blueprint=False, require_prompt=False),
        "app": summarize_catalog(app, required_keys, require_blueprint=True, require_prompt=True),
        "index": summarize_index(index, required_keys),
    }

    print(json.dumps(payload, indent=2))

    if args.strict:
        failures = []
        for section_name in ("app_tags", "app", "index"):
            section = payload[section_name]
            for key, value in section.items():
                if key.endswith("_count") and value not in (0, None, len(required_keys)):
                    if key == "present_entry_count":
                        continue
            if section.get("missing_entries_count"):
                failures.append(f"{section_name}:missing_entries")
        if payload["app_tags"]["empty_mechanic_tags_count"]:
            failures.append("app_tags:empty_mechanic_tags")
        if payload["app_tags"]["empty_screenshots_count"]:
            failures.append("app_tags:empty_screenshots")
        if payload["app_tags"]["empty_semantic_tags_count"]:
            failures.append("app_tags:empty_semantic_tags")
        if payload["app_tags"]["empty_mood_tags_count"]:
            failures.append("app_tags:empty_mood_tags")
        if payload["app_tags"]["empty_descriptions_count"]:
            failures.append("app_tags:empty_descriptions")
        if payload["app"]["empty_prompt_count"]:
            failures.append("app:empty_prompt")
        if payload["app"]["empty_blueprint_count"]:
            failures.append("app:empty_blueprint")
        if payload["index"]["empty_game_json_count"]:
            failures.append("index:empty_game_json")
        if payload["index"]["empty_index_screenshots_count"]:
            failures.append("index:empty_screenshots")
        if failures:
            raise SystemExit("QA failures: " + ", ".join(failures))


if __name__ == "__main__":
    main()