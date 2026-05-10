#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path("/Users/hassan/repos/game_agent")
TOP107_MANIFEST = ROOT / "tmp/game_refactoring_experiments/fixtures/top107_vatsal_raw_backed_full_manifest.json"
APP_ALPHA_50_MANIFEST = ROOT / "tmp/retry_manifests/latest_selected_remix_obfuscator_manifest.json"
PUBLISHED_PUBLIC_ROOT = ROOT / "games/published/public"
OUTPUT_PATH = ROOT / "tmp/retry_manifests/vatsaltop100_app_alpha_batch_manifest.json"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def composite_key(game_id: str, remix_id: str) -> str:
    return f"{game_id}__{remix_id}"


def find_metadata_path(remix_dir: Path, remix_id: str) -> Path | None:
    candidate = remix_dir / f"game-obfuscated-{remix_id.removeprefix('remix-')}.json"
    if candidate.exists():
        return candidate
    matches = sorted(remix_dir.glob("game-obfuscated-*.json"))
    return matches[0] if matches else None


def infer_lineage(metadata: dict, current_game_id: str, current_remix_id: str) -> tuple[str | None, str, int]:
    game_id = str(metadata.get("game_id") or current_game_id or "")
    deploy = metadata.get("deploy") if isinstance(metadata.get("deploy"), dict) else {}
    source_output_dir = str(deploy.get("source_output_dir") or "")
    remix_parent_id = None
    lineage_depth = 0
    root_game_id = game_id or current_game_id

    if "/remix-" in source_output_dir:
        parts = Path(source_output_dir).parts
        try:
            remix_index = next(i for i, part in enumerate(parts) if part.startswith("remix-"))
        except StopIteration:
            remix_index = -1
        if remix_index > 0:
            parent_remix_id = parts[remix_index]
            parent_game_id = parts[remix_index - 1]
            if parent_game_id.startswith("gamezone-") and parent_remix_id.startswith("remix-"):
                candidate_parent_id = composite_key(parent_game_id, parent_remix_id)
                current_composite = composite_key(current_game_id, current_remix_id)
                if candidate_parent_id != current_composite:
                    remix_parent_id = candidate_parent_id
                    root_game_id = parent_game_id
                    lineage_depth = 1

    return remix_parent_id, root_game_id, lineage_depth


def selected_app_alpha_paths_by_game() -> dict[str, set[str]]:
    payload = load_json(APP_ALPHA_50_MANIFEST)
    games = payload.get("games", [])
    result: dict[str, set[str]] = {}
    for item in games:
        game_id = item["game_id"]
        source_path = Path(item["source_path"])
        result.setdefault(game_id, set()).add(source_path.as_posix())
    return result


def build_top107_entries() -> list[dict]:
    payload = load_json(TOP107_MANIFEST)
    games = payload.get("games", [])
    selected_paths = selected_app_alpha_paths_by_game()
    entries: list[dict] = []

    for item in games:
        game_id = item["game_id"]
        remix_dirs = sorted((PUBLISHED_PUBLIC_ROOT / game_id).glob("remix-*"))
        if not remix_dirs:
            raise RuntimeError(f"No published remix found for top107 template {game_id}")

        selected_for_game = selected_paths.get(game_id, set())
        preferred = [path for path in remix_dirs if path.as_posix() not in selected_for_game]
        remix_dir = preferred[0] if preferred else remix_dirs[0]
        remix_id = remix_dir.name
        metadata_path = find_metadata_path(remix_dir, remix_id)
        metadata = load_json(metadata_path) if metadata_path else {}
        remix_parent_id, root_game_id, lineage_depth = infer_lineage(metadata, game_id, remix_id)

        entries.append(
            {
                "game_id": game_id,
                "remix_id": remix_id,
                "composite_key": composite_key(game_id, remix_id),
                "published_path": remix_dir.relative_to(PUBLISHED_PUBLIC_ROOT).as_posix(),
                "variant_group": "vatsal_top107",
                "remix_parent_id": remix_parent_id,
                "root_game_id": root_game_id,
                "lineage_depth": lineage_depth,
            }
        )

    return entries


def build_app_alpha_entries() -> list[dict]:
    payload = load_json(APP_ALPHA_50_MANIFEST)
    games = payload.get("games", [])
    entries: list[dict] = []

    for item in games:
        source_path = Path(item["source_path"])
        game_id = item["game_id"]
        remix_id = source_path.name
        metadata_path = find_metadata_path(source_path, remix_id)
        metadata = load_json(metadata_path) if metadata_path else {}
        remix_parent_id, root_game_id, lineage_depth = infer_lineage(metadata, game_id, remix_id)

        entries.append(
            {
                "game_id": game_id,
                "remix_id": remix_id,
                "composite_key": composite_key(game_id, remix_id),
                "published_path": source_path.relative_to(PUBLISHED_PUBLIC_ROOT).as_posix(),
                "variant_group": "app_alpha_50",
                "remix_parent_id": remix_parent_id,
                "root_game_id": root_game_id,
                "lineage_depth": lineage_depth,
            }
        )

    return entries


def main() -> None:
    top107_entries = build_top107_entries()
    app_alpha_entries = build_app_alpha_entries()
    entries = top107_entries + app_alpha_entries

    duplicates = {}
    seen = set()
    for entry in entries:
        key = entry["composite_key"]
        if key in seen:
            duplicates[key] = duplicates.get(key, 1) + 1
        seen.add(key)

    payload = {
        "batch_name": "Vatsaltop100_app_alpha_batch",
        "collection_slug": "vatsaltop100_app_alpha_batch",
        "generated_at": "2026-05-10T00:00:00Z",
        "entries": entries,
        "summary": {
            "top107_count": len(top107_entries),
            "app_alpha_50_count": len(app_alpha_entries),
            "total_entries": len(entries),
            "unique_composite_keys": len(seen),
            "duplicate_keys": duplicates,
        },
    }

    OUTPUT_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output_path": str(OUTPUT_PATH), **payload["summary"]}, indent=2))


if __name__ == "__main__":
    main()