#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = ROOT.parent.parent
RUN_ID = "run_pipeline_20260517T134546Z"
GAME_ID = "gamezone-29e7c3b5-974b-47c7-b7bf-585b6d5cc301"
REMIX_ID = "remix-2d9ceef4234dc323cd850ecec55d170a"


def find_entries(payload: object, *, game_id: str, remix_id: str) -> list[dict[str, object]]:
    matches: list[dict[str, object]] = []
    if isinstance(payload, list):
        for item in payload:
            if not isinstance(item, dict):
                continue
            item_game_id = item.get("game_id")
            item_url = item.get("url")
            if item_game_id != game_id:
                continue
            if isinstance(item_url, str) and remix_id in item_url:
                matches.append(item)
    elif isinstance(payload, dict):
        for key, value in payload.items():
            if game_id not in str(key) and not isinstance(value, dict):
                continue
            if not isinstance(value, dict):
                continue
            item_game_id = value.get("game_id")
            item_url = value.get("url")
            if item_game_id == game_id or game_id in str(key):
                if isinstance(item_url, str) and remix_id in item_url:
                    matches.append({"_key": key, **value})
    return matches


def main() -> int:
    pipeline_run_dir = ROOT / "pipeline_runs" / RUN_ID
    parsed_matches_path = pipeline_run_dir / "matcher" / "parsed_matches.json"
    root_public_dir = REPO_ROOT / "games" / "published" / "public" / GAME_ID / REMIX_ID
    root_public_index = root_public_dir / "index.html"
    root_public_root = REPO_ROOT / "games" / "published" / "public"
    root_app_json = root_public_root / "app.json"
    root_index_json = root_public_root / "index.json"
    root_app_tags_json = root_public_root / "app_tags.json"
    published_runs_root = REPO_ROOT / "games" / "published" / "runs"

    parsed_matches = json.loads(parsed_matches_path.read_text())
    first_match = parsed_matches["matches"][0]
    url = first_match["url"]

    quarantine_hits = sorted(
        published_runs_root.glob(f"*/quarantine/{GAME_ID}/{REMIX_ID}/index.html")
    )
    public_hits = sorted(
        published_runs_root.glob(f"*/public/{GAME_ID}/{REMIX_ID}/index.html")
    )

    root_app_payload = json.loads(root_app_json.read_text())
    root_index_payload = json.loads(root_index_json.read_text())
    root_app_tags_payload = json.loads(root_app_tags_json.read_text())

    root_app_matches = find_entries(root_app_payload, game_id=GAME_ID, remix_id=REMIX_ID)
    root_index_matches = find_entries(root_index_payload, game_id=GAME_ID, remix_id=REMIX_ID)
    root_app_tags_matches = find_entries(root_app_tags_payload, game_id=GAME_ID, remix_id=REMIX_ID)

    report = {
        "run_id": RUN_ID,
        "selected_match": {
            "game_id": first_match["game_id"],
            "name": first_match.get("name"),
            "url": url,
        },
        "root_public_candidate": {
            "dir": str(root_public_dir),
            "dir_exists": root_public_dir.is_dir(),
            "index_path": str(root_public_index),
            "index_exists": root_public_index.is_file(),
        },
        "run_snapshot_hits": {
            "quarantine": [str(path) for path in quarantine_hits],
            "public": [str(path) for path in public_hits],
        },
        "root_artifact_matches": {
            "app": {
                "count": len(root_app_matches),
                "preview": root_app_matches[:1],
            },
            "index": {
                "count": len(root_index_matches),
                "preview": root_index_matches[:1],
            },
            "app_tags": {
                "count": len(root_app_tags_matches),
                "preview": root_app_tags_matches[:1],
            },
        },
        "materialize_artifact_view_summary": "materialize_artifact_view.py merges JSON artifact views only; it does not copy game asset directories into games/published/public",
        "preliminary_conclusion": (
            "The matcher selected an entry from the merged root app.json view, but the actual asset directory exists only in run-scoped quarantine snapshots, not at the root public path expected by resolve_refactoring_source_path()."
        ),
    }
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())