#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]

    raw_root = repo_root / "games" / "raw"
    public_root = repo_root / "games" / "published" / "public"
    run_manifest = repo_root / "games" / "published" / "runs" / "run_20260517T045748Z" / "artifacts_manifest.json"
    app_json = public_root / "app.json"

    raw_ids = {p.name for p in raw_root.iterdir() if p.is_dir() and p.name.startswith("gamezone-")}
    public_ids = {p.name for p in public_root.iterdir() if p.is_dir() and p.name.startswith("gamezone-")}

    manifest_payload = json.loads(run_manifest.read_text(encoding="utf-8"))
    manifest_entries = manifest_payload.get("entries", []) if isinstance(manifest_payload, dict) else []
    manifest_game_ids = {
        str(entry.get("game_id"))
        for entry in manifest_entries
        if isinstance(entry, dict) and isinstance(entry.get("game_id"), str)
    }

    app_payload = json.loads(app_json.read_text(encoding="utf-8"))
    app_keys = set(app_payload.keys()) if isinstance(app_payload, dict) else set()

    missing_from_run = sorted(raw_ids - manifest_game_ids)

    print(f"raw_game_folders: {len(raw_ids)}")
    print(f"published_public_game_folders: {len(public_ids)}")
    print(f"run_manifest_entries: {len(manifest_entries)}")
    print(f"run_manifest_unique_game_ids: {len(manifest_game_ids)}")
    print(f"app_json_keys_now: {len(app_keys)}")
    print(f"game_ids_not_in_this_run_manifest: {len(missing_from_run)}")
    print(f"sample_game_ids_not_in_this_run_manifest: {missing_from_run[:10]}")


if __name__ == "__main__":
    main()
