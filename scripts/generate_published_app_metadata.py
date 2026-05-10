#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path("/Users/hassan/repos/game_agent")
DEFAULT_PUBLISHED_PUBLIC_ROOT = ROOT / "games/published/public"
DEFAULT_OUTPUT_ROOT = ROOT / "games/published"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate published app metadata catalogs from published remix folders."
    )
    parser.add_argument(
        "--published-root",
        default=str(DEFAULT_PUBLISHED_PUBLIC_ROOT),
        help="Published public remix root. Defaults to games/published/public.",
    )
    parser.add_argument(
        "--output-root",
        default=str(DEFAULT_OUTPUT_ROOT),
        help="Output root for index.json, app_tags.json, and app.json. Defaults to games/published.",
    )
    parser.add_argument(
        "--manifest",
        help="Optional batch manifest with explicit remix entries. If omitted, full-scan mode is used.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail if a referenced remix folder or metadata file is missing.",
    )
    return parser


def composite_key(game_id: str, remix_id: str) -> str:
    return f"{game_id}__{remix_id}"


def find_metadata_path(remix_dir: Path, remix_id: str) -> Path | None:
    exact = remix_dir / f"game-obfuscated-{remix_id.removeprefix('remix-')}.json"
    if exact.exists():
        return exact

    preferred = sorted(
        path
        for path in remix_dir.glob("game-obfuscated-*.json")
        if path.name != "game-obfuscated-appended-metadata.json"
    )
    if preferred:
        return preferred[0]

    matches = sorted(remix_dir.glob("game-obfuscated-*.json"))
    return matches[0] if matches else None


def normalize_tag_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def first_non_empty_string(*values: Any) -> str:
    for value in values:
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def semantic_tag_bucket(metadata: dict[str, Any], key: str) -> list[str]:
    semantic = metadata.get("semantic_tags")
    if isinstance(semantic, dict):
        return normalize_tag_list(semantic.get(key))
    return []


def identity_value(metadata: dict[str, Any], key: str) -> Any:
    identity = metadata.get("identity")
    if isinstance(identity, dict):
        return identity.get(key)
    return None


def identity_tag_bucket(metadata: dict[str, Any], key: str) -> list[str]:
    return normalize_tag_list(identity_value(metadata, key))


def derive_mechanic_tags(metadata: dict[str, Any]) -> list[str]:
    mechanics = metadata.get("mechanics_classification")
    if isinstance(mechanics, dict):
        for key in ["selected_top_5", "selected_top_5_categories"]:
            selected = mechanics.get(key)
            if isinstance(selected, list):
                tags = []
                for item in selected:
                    if isinstance(item, dict):
                        category = item.get("category")
                        if isinstance(category, str) and category.strip():
                            tags.append(category.strip())
                if tags:
                    return tags
        direct = mechanics.get("mechanic_tags")
        if isinstance(direct, list):
            direct_tags = normalize_tag_list(direct)
            if direct_tags:
                return direct_tags

    semantic_mechanics = semantic_tag_bucket(metadata, "mechanics")
    if semantic_mechanics:
        return semantic_mechanics

    return []


def derive_title(metadata: dict[str, Any], fallback_game_id: str) -> str:
    return first_non_empty_string(identity_value(metadata, "title"), metadata.get("title"), fallback_game_id)


def derive_description(metadata: dict[str, Any]) -> str:
    return first_non_empty_string(
        identity_value(metadata, "description"),
        identity_value(metadata, "premise"),
        identity_value(metadata, "objective"),
        metadata.get("description"),
    )


def derive_prompt(metadata: dict[str, Any]) -> str:
    return first_non_empty_string(metadata.get("recreation_prompt_markdown"), identity_value(metadata, "recreation_prompt"))


def derive_blueprint(metadata: dict[str, Any]) -> str:
    return first_non_empty_string(metadata.get("blueprint_markdown"))


def list_relative_files(remix_dir: Path) -> list[str]:
    return sorted(path.relative_to(remix_dir).as_posix() for path in remix_dir.rglob("*") if path.is_file())


def classify_files(all_files: list[str]) -> tuple[list[str], list[str], list[str], list[str]]:
    screenshots_png = [path for path in all_files if path.startswith("screenshots/") and path.lower().endswith(".png")]
    screenshots_jpg = [
        path for path in all_files if path.startswith("screenshots/") and (path.lower().endswith(".jpg") or path.lower().endswith(".jpeg"))
    ]
    assets_css = [path for path in all_files if path.startswith("assets/") and path.lower().endswith(".css")]
    assets_js = [path for path in all_files if path.startswith("assets/") and path.lower().endswith(".js")]
    return screenshots_png, screenshots_jpg, assets_css, assets_js


def infer_lineage_fields(entry: dict[str, Any], metadata: dict[str, Any], game_id: str) -> tuple[str | None, str, int]:
    remix_parent_id = entry.get("remix_parent_id")
    root_game_id = entry.get("root_game_id") or game_id
    lineage_depth = int(entry.get("lineage_depth") or 0)

    if remix_parent_id is not None:
        return str(remix_parent_id), str(root_game_id), lineage_depth

    deploy = metadata.get("deploy") if isinstance(metadata.get("deploy"), dict) else {}
    source_output_dir = str(deploy.get("source_output_dir") or "")
    if "/remix-" in source_output_dir:
        parts = Path(source_output_dir).parts
        remix_indices = [i for i, part in enumerate(parts) if part.startswith("remix-")]
        if remix_indices:
            remix_index = remix_indices[-1]
            if remix_index > 0:
                parent_remix_id = parts[remix_index]
                parent_game_id = parts[remix_index - 1]
                candidate = composite_key(parent_game_id, parent_remix_id)
                current = composite_key(game_id, entry["remix_id"])
                if candidate != current:
                    return candidate, parent_game_id, 1

    return None, str(root_game_id), lineage_depth


def build_entry_from_remix(
    published_root: Path,
    relative_path: str,
    manifest_entry: dict[str, Any] | None,
    strict: bool,
) -> tuple[str, dict[str, Any], dict[str, Any], dict[str, Any]] | None:
    remix_dir = published_root / relative_path
    if not remix_dir.exists():
        if strict:
            raise FileNotFoundError(f"Missing remix directory: {remix_dir}")
        return None

    parts = Path(relative_path).parts
    if len(parts) != 2:
        if strict:
            raise ValueError(f"Expected relative remix path '<game_id>/<remix_id>', got: {relative_path}")
        return None

    game_id, remix_id = parts
    if not game_id.startswith("gamezone-") or not remix_id.startswith("remix-"):
        if strict:
            raise ValueError(f"Invalid game_id/remix_id pair in path: {relative_path}")
        return None

    metadata_path = find_metadata_path(remix_dir, remix_id)
    if not metadata_path:
        if strict:
            raise FileNotFoundError(f"Missing metadata json in {remix_dir}")
        return None

    metadata = load_json(metadata_path)
    all_files = list_relative_files(remix_dir)
    screenshots_png, screenshots_jpg, assets_css, assets_js = classify_files(all_files)
    metadata_screenshots_png = normalize_tag_list(metadata.get("screenshots_png"))
    metadata_screenshots_jpg = normalize_tag_list(metadata.get("screenshots_jpg"))
    if metadata_screenshots_png:
        screenshots_png = metadata_screenshots_png
    if metadata_screenshots_jpg:
        screenshots_jpg = metadata_screenshots_jpg
    screenshots = screenshots_jpg or screenshots_png

    entry = manifest_entry or {"remix_id": remix_id}
    remix_parent_id, root_game_id, lineage_depth = infer_lineage_fields(entry, metadata, game_id)

    composite = composite_key(game_id, remix_id)
    rel_prefix = Path(relative_path).as_posix()

    app_tags_record = {
        "game_id": game_id,
        "remix_id": remix_id,
        "published_path": rel_prefix,
        "remix_parent_id": remix_parent_id,
        "root_game_id": root_game_id,
        "lineage_depth": lineage_depth,
        "index_html": f"{rel_prefix}/index.html",
        "screenshots": [f"{rel_prefix}/{path}" for path in screenshots],
        "mechanic_tags": derive_mechanic_tags(metadata),
        "semantic_tags": semantic_tag_bucket(metadata, "theme") or semantic_tag_bucket(metadata, "semantic_tags"),
        "mood_tags": semantic_tag_bucket(metadata, "mood"),
        "setting_tags": semantic_tag_bucket(metadata, "setting"),
        "character_tags": semantic_tag_bucket(metadata, "characters") or identity_tag_bucket(metadata, "characters") or identity_tag_bucket(metadata, "character_tags"),
        "games_tags": semantic_tag_bucket(metadata, "similar_games") or identity_tag_bucket(metadata, "similar_games") or identity_tag_bucket(metadata, "games_tags"),
        "franchise_tags": semantic_tag_bucket(metadata, "similar_franchises") or identity_tag_bucket(metadata, "similar_franchises") or identity_tag_bucket(metadata, "franchise_tags"),
        "title": derive_title(metadata, game_id),
        "description": derive_description(metadata),
    }

    app_record = {
        **app_tags_record,
        "prompt": derive_prompt(metadata),
        "blueprint": derive_blueprint(metadata),
    }

    index_record = {
        "game_id": game_id,
        "remix_id": remix_id,
        "published_path": rel_prefix,
        "remix_parent_id": remix_parent_id,
        "root_game_id": root_game_id,
        "lineage_depth": lineage_depth,
        "game_root": rel_prefix,
        "index_html": f"{rel_prefix}/index.html",
        "game_json": f"{rel_prefix}/{metadata_path.relative_to(remix_dir).as_posix()}",
        "screenshots_png": [f"{rel_prefix}/{path}" for path in screenshots_png],
        "screenshots_jpg": [f"{rel_prefix}/{path}" for path in screenshots_jpg],
        "assets_css": [f"{rel_prefix}/{path}" for path in assets_css],
        "assets_js": [f"{rel_prefix}/{path}" for path in assets_js],
        "all_files": [f"{rel_prefix}/{path}" for path in all_files],
    }

    return composite, index_record, app_tags_record, app_record


def full_scan_entries(published_root: Path) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for game_dir in sorted(path for path in published_root.iterdir() if path.is_dir() and path.name.startswith("gamezone-")):
        for remix_dir in sorted(path for path in game_dir.iterdir() if path.is_dir() and path.name.startswith("remix-")):
            entries.append(
                {
                    "game_id": game_dir.name,
                    "remix_id": remix_dir.name,
                    "published_path": f"{game_dir.name}/{remix_dir.name}",
                }
            )
    return entries


def manifest_entries(manifest_path: Path) -> list[dict[str, Any]]:
    payload = load_json(manifest_path)
    entries = payload.get("entries") if isinstance(payload, dict) else payload
    if not isinstance(entries, list):
        raise ValueError("Manifest must contain a top-level 'entries' list or be a list itself")
    normalized = []
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("Manifest entries must be objects")
        published_path = entry.get("published_path")
        game_id = entry.get("game_id")
        remix_id = entry.get("remix_id")
        if not published_path and game_id and remix_id:
            published_path = f"{game_id}/{remix_id}"
        if not published_path:
            raise ValueError("Manifest entry must include published_path or both game_id and remix_id")
        normalized.append({**entry, "published_path": str(published_path)})
    return normalized


def main() -> None:
    args = build_parser().parse_args()
    published_root = Path(args.published_root).resolve()
    output_root = Path(args.output_root).resolve()

    entries = manifest_entries(Path(args.manifest).resolve()) if args.manifest else full_scan_entries(published_root)

    index_payload: dict[str, Any] = {}
    app_tags_payload: dict[str, Any] = {}
    app_payload: dict[str, Any] = {}

    for entry in entries:
        built = build_entry_from_remix(
            published_root=published_root,
            relative_path=entry["published_path"],
            manifest_entry=entry,
            strict=args.strict,
        )
        if built is None:
            continue
        composite, index_record, app_tags_record, app_record = built
        index_payload[composite] = index_record
        app_tags_payload[composite] = app_tags_record
        app_payload[composite] = app_record

    write_json(output_root / "index.json", index_payload)
    write_json(output_root / "app_tags.json", app_tags_payload)
    write_json(output_root / "app.json", app_payload)

    print(
        json.dumps(
            {
                "entries_written": len(index_payload),
                "index_json": str(output_root / "index.json"),
                "app_tags_json": str(output_root / "app_tags.json"),
                "app_json": str(output_root / "app.json"),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()