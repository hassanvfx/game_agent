#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

ROOT = Path("/Users/hassan/repos/game_agent")
DEFAULT_PUBLISHED_PUBLIC_ROOT = ROOT / "games/published/public"
DEFAULT_OUTPUT_ROOT = ROOT / "games/published"
SEMANTIC_BUCKET_ALIASES = {
    "mechanics": ["mechanics", "mechanic_tags"],
    "theme": ["theme", "prompt_requested_tags", "presentation_tags", "theme_tags"],
    "mood": ["mood", "mood_tags", "tone_tags"],
    "setting": ["setting", "setting_tags"],
    "characters": ["characters", "character_tags"],
    "similar_games": ["similar_games", "games_tags"],
    "similar_franchises": ["similar_franchises", "franchise_tags"],
}


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
    parser.add_argument(
        "--approved",
        choices=("true", "false"),
        help="Optionally set approved on every generated app.json record.",
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


def normalize_tag_value(value: Any) -> list[str]:
    if isinstance(value, list):
        return normalize_tag_list(value)
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def merge_tag_lists(*values: Any) -> list[str]:
    merged: list[str] = []
    seen: set[str] = set()
    for value in values:
        for tag in normalize_tag_value(value):
            key = tag.casefold()
            if key in seen:
                continue
            seen.add(key)
            merged.append(tag)
    return merged


def first_non_empty_string(*values: Any) -> str:
    for value in values:
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def normalize_text(value: Any) -> str:
    return " ".join(str(value or "").strip().lower().split())


def semantic_payload(metadata: dict[str, Any]) -> dict[str, Any]:
    semantic = metadata.get("semantic_tags")
    return semantic if isinstance(semantic, dict) else {}


def semantic_nested_tags(metadata: dict[str, Any]) -> dict[str, Any]:
    tags = semantic_payload(metadata).get("tags")
    return tags if isinstance(tags, dict) else {}


def semantic_title(metadata: dict[str, Any]) -> str:
    return first_non_empty_string(semantic_payload(metadata).get("title"))


def semantic_value(metadata: dict[str, Any], key: str) -> Any:
    semantic = semantic_payload(metadata)
    if key in semantic:
        return semantic.get(key)
    return semantic_nested_tags(metadata).get(key)


def general_semantic_tags(metadata: dict[str, Any]) -> list[str]:
    semantic = semantic_payload(metadata)
    tags_value = semantic.get("tags")
    general_tags = tags_value if isinstance(tags_value, list) else []
    return merge_tag_lists(
        general_tags,
        semantic.get("preserve_tags"),
        semantic.get("transform_tags"),
    )


def semantic_tag_bucket(metadata: dict[str, Any], key: str) -> list[str]:
    aliases = SEMANTIC_BUCKET_ALIASES.get(key, [key])
    return merge_tag_lists(*(semantic_value(metadata, alias) for alias in aliases))


def identity_value(metadata: dict[str, Any], key: str) -> Any:
    identity = metadata.get("identity")
    if isinstance(identity, dict):
        return identity.get(key)
    return None


def identity_tag_bucket(metadata: dict[str, Any], key: str) -> list[str]:
    return normalize_tag_value(identity_value(metadata, key))


def prompt_text(metadata: dict[str, Any]) -> str:
    return first_non_empty_string(
        metadata.get("recreation_prompt_markdown"),
        identity_value(metadata, "recreation_prompt"),
        identity_value(metadata, "prompt"),
    )


def clean_extracted_title(value: str) -> str:
    return value.strip().strip("\"'“”‘’`*").strip()


def extract_title_from_text(text: Any) -> str:
    if not isinstance(text, str) or not text.strip():
        return ""
    patterns = (
        re.compile(r"recreate\s+\*\*([^*]{2,160})\*\*", re.IGNORECASE),
        re.compile(r"recreate\s+`([^`]{2,160})`", re.IGNORECASE),
        re.compile(r"recreate\s+[^\n]{0,120}?\s+as\s+\*\*([^*]{2,160})\*\*", re.IGNORECASE),
        re.compile(r"recreate\s+[^\n]{0,120}?\s+as\s+`([^`]{2,160})`", re.IGNORECASE),
        re.compile(r"recreate\s+(?!a\b|an\b|the\b)([^,\n]{2,160}?)\s+as\s+(?:a|an|the)\b", re.IGNORECASE),
        re.compile(r"source\s+as\s+\*\*([^*]{2,160})\*\*", re.IGNORECASE),
        re.compile(r"source\s+as\s+`([^`]{2,160})`", re.IGNORECASE),
        re.compile(r"presentation\s+as\s+\*\*([^*]{2,160})\*\*", re.IGNORECASE),
        re.compile(r"presentation\s+as\s+`([^`]{2,160})`", re.IGNORECASE),
        re.compile(r"named\s+\*\*([^*]{2,160})\*\*", re.IGNORECASE),
        re.compile(r"named\s+[\"“']([^\"”']{2,160})[\"”']", re.IGNORECASE),
        re.compile(r"named\s+([^\n]{2,160}?)\s+from\s+this\s+brief:", re.IGNORECASE),
        re.compile(r"named\s+([^\.\n]{2,160}?)(?:\.|\n)", re.IGNORECASE),
        re.compile(r"called\s+\*\*([^*]{2,160})\*\*", re.IGNORECASE),
        re.compile(r"called\s+[\"“']([^\"”']{2,160})[\"”']", re.IGNORECASE),
        re.compile(r"called\s+`([^`]{2,160})`", re.IGNORECASE),
        re.compile(r"theme\s+the\s+game\s+as\s+([^\.\n]{2,160}?)(?:\.|\n)", re.IGNORECASE),
        re.compile(r"should\s+be\s+\*\*([^*]{2,160})\*\*", re.IGNORECASE),
        re.compile(r"should\s+be\s+[\"“']([^\"”']{2,160})[\"”']", re.IGNORECASE),
        re.compile(r"should\s+be\s+`([^`]{2,160})`", re.IGNORECASE),
        re.compile(r"titled\s+\*\*([^*]{2,160})\*\*", re.IGNORECASE),
        re.compile(r"titled\s+[\"“']([^\"”']{2,160})[\"”']", re.IGNORECASE),
        re.compile(r"titled\s+`([^`]{2,160})`", re.IGNORECASE),
        re.compile(r"titled\s+([^\.\n]{2,160}?)(?:\.|\n)", re.IGNORECASE),
        re.compile(r"into\s+\*\*([^*]{2,160})\*\*", re.IGNORECASE),
        re.compile(r"into\s+[\"“']([^\"”']{2,160})[\"”']", re.IGNORECASE),
        re.compile(r"into\s+`([^`]{2,160})`", re.IGNORECASE),
        re.compile(r"^\s*(?:#\s+recreation prompt\s+)?create\s+([^,\n]{2,160}?),\s+a\b", re.IGNORECASE),
        re.compile(r"called\s+([^\.\n]{2,160}?)(?:\.|\n)", re.IGNORECASE),
    )
    for pattern in patterns:
        match = pattern.search(text)
        if not match:
            continue
        candidate = clean_extracted_title(match.group(1))
        if candidate:
            return candidate
    return ""


def selected_mechanic_categories(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    tags: list[str] = []
    for item in value:
        if isinstance(item, dict):
            candidate = first_non_empty_string(item.get("category"), item.get("name"), item.get("title"), item.get("tag"))
            if candidate:
                tags.append(candidate)
        elif isinstance(item, str) and item.strip():
            tags.append(item.strip())
    return tags


def mechanics_title(metadata: dict[str, Any]) -> str:
    mechanics = metadata.get("mechanics_classification")
    if isinstance(mechanics, dict):
        return first_non_empty_string(mechanics.get("game"), mechanics.get("title"))
    return ""


def is_placeholder_title(title: str, game_id: str, remix_id: str, published_path: str) -> bool:
    normalized_title = normalize_text(title)
    if not normalized_title:
        return True
    if title.strip().startswith("gamezone-"):
        return True

    raw_candidates = {
        normalize_text(game_id),
        normalize_text(remix_id),
        normalize_text(published_path),
        normalize_text(Path(published_path).name if published_path else ""),
        normalize_text(f"{game_id}__{remix_id}" if game_id and remix_id else ""),
    }
    raw_candidates.discard("")
    return normalized_title in raw_candidates


def derive_mechanic_tags(metadata: dict[str, Any]) -> list[str]:
    mechanics = metadata.get("mechanics_classification")
    selected_tags: list[str] = []
    ranked_tags: list[str] = []
    direct_tags: list[str] = []
    if isinstance(mechanics, dict):
        for key in ["selected_top_5", "selected_top_5_categories", "selected_categories"]:
            selected_tags.extend(selected_mechanic_categories(mechanics.get(key)))

        ranked_tags.extend(selected_mechanic_categories(mechanics.get("ranked_mechanics")))

        direct = mechanics.get("mechanic_tags")
        direct_tags = normalize_tag_value(direct)

    semantic_mechanics = semantic_tag_bucket(metadata, "mechanics")
    return merge_tag_lists(selected_tags, ranked_tags, direct_tags, semantic_mechanics)


def derive_title(metadata: dict[str, Any], fallback_game_id: str, remix_id: str, published_path: str) -> str:
    prompt_title = extract_title_from_text(prompt_text(metadata))
    candidates = [
        first_non_empty_string(identity_value(metadata, "title")),
        semantic_title(metadata),
        first_non_empty_string(identity_value(metadata, "short_title")),
        prompt_title,
        mechanics_title(metadata),
        first_non_empty_string(metadata.get("title")),
    ]
    for candidate in candidates:
        if candidate and not is_placeholder_title(candidate, fallback_game_id, remix_id, published_path):
            return candidate
    return first_non_empty_string(*candidates, fallback_game_id)


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
    return sorted(
        path.relative_to(remix_dir).as_posix()
        for path in remix_dir.rglob("*")
        if path.is_file() and not path.name.startswith("._")
    )


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


@lru_cache(maxsize=1)
def load_obfuscation_contract(published_root: Path) -> dict[str, dict[str, Any]]:
    if published_root.name != "public":
        return {}

    manifest_candidates = [
        ROOT / "tmp/retry_manifests/latest_selected_remix_obfuscator_manifest.json",
    ]
    contract: dict[str, dict[str, Any]] = {}

    for manifest_path in manifest_candidates:
        if not manifest_path.exists():
            continue
        payload = load_json(manifest_path)
        games = payload.get("games") if isinstance(payload, dict) else None
        if not isinstance(games, list):
            continue
        for item in games:
            if not isinstance(item, dict):
                continue
            source_path = item.get("source_path")
            if not isinstance(source_path, str) or not source_path.strip():
                continue
            source_dir = Path(source_path).resolve()
            try:
                relative_path = source_dir.relative_to(published_root).as_posix()
            except ValueError:
                continue
            contract[relative_path] = dict(item)

    return contract


def resolve_obfuscated_variant(
    published_root: Path, relative_path: str
) -> tuple[str | None, dict[str, Any]]:
    public_index_html = f"{relative_path}/index.html"
    game_id = Path(relative_path).parts[0]
    obfuscated_root = published_root.parent / "obfuscated"
    status = {
        "contract_source": "none",
        "contract_matched": False,
        "contract_has_output_path": False,
        "contract_expected_output_path": None,
        "contract_output_exists": False,
        "contract_index_exists": False,
        "resolved_index_html": None,
    }

    if published_root.name != "public":
        return None, status

    def evaluate_candidate(output_dir: Path, source: str, index_html: str) -> tuple[str | None, dict[str, Any]]:
        candidate_status = dict(status)
        candidate_status["contract_source"] = source
        candidate_status["contract_expected_output_path"] = str(output_dir.resolve())
        candidate_status["contract_output_exists"] = output_dir.exists()
        index_path = output_dir / "index.html"
        candidate_status["contract_index_exists"] = index_path.exists()
        if index_path.exists():
            candidate_status["resolved_index_html"] = index_html
            return index_html, candidate_status
        return None, candidate_status

    obfuscation_contract = load_obfuscation_contract(published_root)
    contract_entry = obfuscation_contract.get(relative_path)
    if contract_entry:
        status["contract_matched"] = True
        output_path = contract_entry.get("output_path")
        if isinstance(output_path, str) and output_path.strip():
            status["contract_has_output_path"] = True
            contract_variant, contract_status = evaluate_candidate(
                Path(output_path), "latest_selected_remix_obfuscator_manifest", public_index_html
            )
            contract_status["contract_matched"] = True
            contract_status["contract_has_output_path"] = True
            if contract_variant is not None:
                return contract_variant, contract_status
            status = contract_status

    game_level_variant, game_level_status = evaluate_candidate(
        obfuscated_root / game_id,
        "game_level_fallback",
        f"{game_id}/index.html",
    )
    game_level_status["contract_matched"] = status["contract_matched"]
    game_level_status["contract_has_output_path"] = status["contract_has_output_path"]
    if game_level_variant is not None:
        return game_level_variant, game_level_status

    remix_level_variant, remix_level_status = evaluate_candidate(
        obfuscated_root / relative_path,
        "relative_path_fallback",
        public_index_html,
    )
    remix_level_status["contract_matched"] = status["contract_matched"]
    remix_level_status["contract_has_output_path"] = status["contract_has_output_path"]
    if remix_level_variant is not None:
        return remix_level_variant, remix_level_status

    return None, status


def build_entry_from_remix(
    published_root: Path,
    relative_path: str,
    manifest_entry: dict[str, Any] | None,
    strict: bool,
    approved: bool | None,
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
    public_index_html = f"{rel_prefix}/index.html"
    obfuscated_index_html, obfuscation_status = resolve_obfuscated_variant(published_root, rel_prefix)
    has_obfuscated_variant = obfuscated_index_html is not None

    app_tags_record = {
        "game_id": game_id,
        "remix_id": remix_id,
        "published_path": rel_prefix,
        "remix_parent_id": remix_parent_id,
        "root_game_id": root_game_id,
        "lineage_depth": lineage_depth,
        "index_html": public_index_html,
        "public_index_html": public_index_html,
        "obfuscated_index_html": obfuscated_index_html,
        "has_obfuscated_variant": has_obfuscated_variant,
        "obfuscation_status": obfuscation_status,
        "screenshots": [f"{rel_prefix}/{path}" for path in screenshots],
        "mechanic_tags": derive_mechanic_tags(metadata),
        "semantic_tags": merge_tag_lists(
            semantic_tag_bucket(metadata, "theme"),
            general_semantic_tags(metadata),
            identity_tag_bucket(metadata, "theme"),
        ),
        "mood_tags": merge_tag_lists(
            semantic_tag_bucket(metadata, "mood"),
            identity_tag_bucket(metadata, "mood"),
            identity_tag_bucket(metadata, "tone"),
        ),
        "setting_tags": merge_tag_lists(semantic_tag_bucket(metadata, "setting")),
        "character_tags": merge_tag_lists(
            semantic_tag_bucket(metadata, "characters"),
            identity_tag_bucket(metadata, "characters"),
            identity_tag_bucket(metadata, "character_tags"),
            identity_tag_bucket(metadata, "teams"),
        ),
        "games_tags": merge_tag_lists(
            semantic_tag_bucket(metadata, "similar_games"),
            identity_tag_bucket(metadata, "similar_games"),
            identity_tag_bucket(metadata, "games_tags"),
        ),
        "franchise_tags": merge_tag_lists(
            semantic_tag_bucket(metadata, "similar_franchises"),
            identity_tag_bucket(metadata, "similar_franchises"),
            identity_tag_bucket(metadata, "franchise_tags"),
        ),
        "title": derive_title(metadata, game_id, remix_id, rel_prefix),
        "description": derive_description(metadata),
    }

    app_record = {
        **app_tags_record,
        "prompt": derive_prompt(metadata),
        "blueprint": derive_blueprint(metadata),
    }
    if approved is not None:
        app_record["approved"] = approved

    index_record = {
        "game_id": game_id,
        "remix_id": remix_id,
        "published_path": rel_prefix,
        "remix_parent_id": remix_parent_id,
        "root_game_id": root_game_id,
        "lineage_depth": lineage_depth,
        "game_root": rel_prefix,
        "index_html": public_index_html,
        "public_index_html": public_index_html,
        "obfuscated_index_html": obfuscated_index_html,
        "has_obfuscated_variant": has_obfuscated_variant,
        "obfuscation_status": obfuscation_status,
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
    approved = None if args.approved is None else args.approved == "true"

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
            approved=approved,
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