#!/usr/bin/env python3
"""Build a merged canonical audio catalog from library and semantic source views."""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in __import__("sys").path:
    __import__("sys").path.insert(0, str(SCRIPT_DIR))

from audio_paths import resolve_library_root  # type: ignore  # noqa: E402

LIBRARY_ROOT = resolve_library_root()
LIBRARY_AUDIOS_PATH = LIBRARY_ROOT / "audios.json"
LIBRARY_MANIFEST_PATH = LIBRARY_ROOT / "manifest.json"
LIBRARY_README_PATH = LIBRARY_ROOT / "README.md"
REFACTORING_AUDIOS_PATH = ROOT / "tools" / "game_refactoring" / "catalogs" / "audios.json"
DEFAULT_OUTPUT_PATH = LIBRARY_ROOT / "catalog.json"

PROMPT_KEY_ALIASES = {
    "failure": "fail",
}

ROLE_TO_INTENT = {
    "character footsteps movement action": "movement",
    "enemy attack hit danger": "enemy_attack",
    "npc interaction voice talk": "npc_interaction",
    "item pickup treasure resource": "item_pickup",
    "wind ambience environment air": "wind_ambience",
    "defeat fail death loss": "defeat",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value


def strip_variant_suffix(name: str) -> str:
    return re.sub(r"_\d+$", "", name)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build merged canonical audio catalog from library and semantic source views.")
    parser.add_argument("--library-audios", default=str(LIBRARY_AUDIOS_PATH))
    parser.add_argument("--library-manifest", default=str(LIBRARY_MANIFEST_PATH))
    parser.add_argument("--library-readme", default=str(LIBRARY_README_PATH))
    parser.add_argument("--refactoring-audios", default=str(REFACTORING_AUDIOS_PATH))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH))
    parser.add_argument("--write-library-view", action="store_true")
    parser.add_argument("--write-refactoring-view", action="store_true")
    return parser.parse_args()


def extract_prompt_blocks(readme_path: Path) -> dict[str, str]:
    text = readme_path.read_text(encoding="utf-8")
    pattern = re.compile(r"^#### `([^`]+)`\n\n```text\n(.*?)\n```", re.MULTILINE | re.DOTALL)
    return {match.group(1): match.group(2).strip() for match in pattern.finditer(text)}


def build_manifest_aliases(manifest: dict[str, Any]) -> dict[str, list[str]]:
    aliases: dict[str, list[str]] = defaultdict(list)
    for event_name, relative_path in (manifest.get("events") or {}).items():
        stem = Path(relative_path).stem
        aliases[stem].append(event_name)
    return {key: sorted(set(values)) for key, values in aliases.items()}


def generation_route_for_category(category: str) -> str:
    return "suno-sounds" if category == "sfx" else "suno-music"


def fallback_prompt(*, base_name: str, usage: str, category: str) -> str:
    if category == "sfx":
        return f"Very short game sound effect. {usage}. Clean, readable, original, game-ready. No voice, no song, no long tail."
    return f"Background game music. {usage}. Original, polished, game-ready. No vocals."


def build_library_records(
    *,
    library_index: dict[str, list[dict[str, Any]]],
    manifest_aliases: dict[str, list[str]],
    prompt_blocks: dict[str, str],
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for group, items in library_index.items():
        if not items:
            continue
        sorted_items = sorted(items, key=lambda item: item["name"])
        base_name = strip_variant_suffix(sorted_items[0]["name"])
        prompt_key = PROMPT_KEY_ALIASES.get(base_name, base_name)
        target_dir = Path(sorted_items[0]["location"]).parts[0]
        category = "sfx" if target_dir in {"sfx", "ui"} else "music"
        usage = sorted_items[0].get("usage", "")
        audio_type = sorted_items[0].get("audio_type")
        prompt_template = prompt_blocks.get(prompt_key) or fallback_prompt(base_name=base_name, usage=usage, category=category)
        aliases = [base_name, base_name.replace("_", " ")]
        aliases.extend(manifest_aliases.get(base_name, []))

        records.append(
            {
                "record_type": "asset_family",
                "id": base_name,
                "category": category,
                "generation_route": generation_route_for_category(category),
                "group": group,
                "usage": usage,
                "audio_type": audio_type,
                "prompt_template": prompt_template,
                "aliases": sorted(set(aliases)),
                "target": {
                    "directory": target_dir,
                    "filename_prefix": base_name,
                    "existing_glob": f"{base_name}_*.mp3",
                },
                "variants": sorted_items,
                "sources": {
                    "library_group": group,
                    "manifest_event_aliases": manifest_aliases.get(base_name, []),
                    "prompt_key": prompt_key,
                },
            }
        )
    return sorted(records, key=lambda record: record["id"])


def build_semantic_prompt(*, query: str, usage: str, category: str) -> str:
    if category == "sfx":
        return f"Very short game sound effect. {usage} Context: {query}. Original, polished, game-ready. No voice, no song, no long tail."
    return f"Background game music. {usage} Context: {query}. Original, polished, game-ready. No vocals."


def build_semantic_records(refactoring_entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for entry in refactoring_entries:
        query = entry.get("query", "")
        tokens = query.split()
        biome = tokens[0] if tokens else "unknown"
        role = " ".join(tokens[1:]) if len(tokens) > 1 else "unknown"
        items = entry.get("items") or []
        item_type = items[0].get("type") if items and isinstance(items[0], dict) else None
        category = "sfx" if item_type == "sfx" else "music"
        intent = ROLE_TO_INTENT.get(role)
        if intent is None:
            intent = "bgm" if role.startswith("bgm ambient") else slugify(role)
        record_id = f"{slugify(biome)}_{slugify(intent)}"
        tags = [slugify(part) for part in tokens if part]
        usage = entry.get("usage", "")

        records.append(
            {
                "record_type": "semantic_query",
                "id": record_id,
                "category": category,
                "generation_route": generation_route_for_category(category),
                "query": query,
                "world": biome,
                "semantic_role": role,
                "intent": intent,
                "usage": usage,
                "tags": tags,
                "prompt_template": build_semantic_prompt(query=query, usage=usage, category=category),
                "reference_items": items,
                "sources": {
                    "refactoring_query": query,
                },
            }
        )
    return sorted(records, key=lambda record: record["id"])


def derive_library_view(catalog: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for record in catalog["records"]:
        if record.get("record_type") != "asset_family":
            continue
        grouped[record["group"]] = list(record["variants"])
    return grouped


def derive_refactoring_view(catalog: dict[str, Any]) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for record in catalog["records"]:
        if record.get("record_type") != "semantic_query":
            continue
        entries.append(
            {
                "query": record["query"],
                "usage": record["usage"],
                "random_pick": "Preserved from canonical semantic record; regenerate explicitly when needed.",
                "items": record["reference_items"],
            }
        )
    return entries


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    library_audios_path = Path(args.library_audios)
    library_manifest_path = Path(args.library_manifest)
    library_readme_path = Path(args.library_readme)
    refactoring_audios_path = Path(args.refactoring_audios)
    output_path = Path(args.output)

    library_index = load_json(library_audios_path)
    manifest = load_json(library_manifest_path)
    refactoring_entries = load_json(refactoring_audios_path)
    prompt_blocks = extract_prompt_blocks(library_readme_path)
    manifest_aliases = build_manifest_aliases(manifest)

    asset_records = build_library_records(
        library_index=library_index,
        manifest_aliases=manifest_aliases,
        prompt_blocks=prompt_blocks,
    )
    semantic_records = build_semantic_records(refactoring_entries)

    catalog = {
        "schema_version": 1,
        "generated_at": utc_now(),
        "source_paths": {
            "library_audios": str(library_audios_path.relative_to(ROOT)),
            "library_manifest": str(library_manifest_path.relative_to(ROOT)),
            "library_readme": str(library_readme_path.relative_to(ROOT)),
            "refactoring_audios": str(refactoring_audios_path.relative_to(ROOT)),
        },
        "summary": {
            "asset_family_count": len(asset_records),
            "semantic_query_count": len(semantic_records),
            "record_count": len(asset_records) + len(semantic_records),
        },
        "records": [*asset_records, *semantic_records],
    }

    write_json(output_path, catalog)

    if args.write_library_view:
        write_json(library_audios_path, derive_library_view(catalog))
    if args.write_refactoring_view:
        write_json(refactoring_audios_path, derive_refactoring_view(catalog))

    print(json.dumps(catalog["summary"], ensure_ascii=False, indent=2))
    print(f"wrote {output_path.relative_to(ROOT)}")
    if args.write_library_view:
        print(f"updated {library_audios_path.relative_to(ROOT)}")
    if args.write_refactoring_view:
        print(f"updated {refactoring_audios_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
