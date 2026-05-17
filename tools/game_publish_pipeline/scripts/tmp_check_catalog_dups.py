#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def analyze_catalog(path: Path, manifest_keys: set[str], manifest_game_ids: set[str]) -> dict:
    payload = load_json(path)
    if not isinstance(payload, dict):
        raise SystemExit(f"Catalog is not a JSON object: {path}")

    keys = set(payload.keys())
    extra_keys = sorted(keys - manifest_keys)
    missing_keys = sorted(manifest_keys - keys)

    game_to_keys: dict[str, list[str]] = defaultdict(list)
    for composite_key, record in payload.items():
        game_id = ""
        if isinstance(record, dict):
            value = record.get("game_id")
            if isinstance(value, str):
                game_id = value
        if not game_id:
            game_id = composite_key.split("__", 1)[0]
        game_to_keys[game_id].append(composite_key)

    game_ids_with_multiple_records = {gid: recs for gid, recs in game_to_keys.items() if len(recs) > 1}

    extra_by_game = Counter(key.split("__", 1)[0] for key in extra_keys)
    stale_same_game = {gid: count for gid, count in extra_by_game.items() if gid in manifest_game_ids}

    return {
        "catalog_path": str(path),
        "total_records": len(payload),
        "manifest_records": len(manifest_keys),
        "extra_keys": len(extra_keys),
        "missing_keys": len(missing_keys),
        "game_ids_with_multiple_records": len(game_ids_with_multiple_records),
        "extra_keys_for_game_ids_in_manifest": sum(stale_same_game.values()),
        "sample_extra_keys": extra_keys[:10],
        "sample_stale_game_ids": sorted(stale_same_game.items(), key=lambda it: (-it[1], it[0]))[:15],
        "sample_multi_record_game_ids": sorted(
            ((gid, len(recs)) for gid, recs in game_ids_with_multiple_records.items()),
            key=lambda it: (-it[1], it[0]),
        )[:15],
    }


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    run_id = "run_20260517T045748Z"

    manifest_path = repo_root / "games" / "published" / "runs" / run_id / "artifacts_manifest.json"
    public_index_path = repo_root / "games" / "published" / "public" / "index.json"
    obfuscated_index_path = repo_root / "games" / "published" / "obfuscated" / "index.json"

    manifest_payload = load_json(manifest_path)
    entries = manifest_payload.get("entries") if isinstance(manifest_payload, dict) else None
    if not isinstance(entries, list):
        raise SystemExit(f"Invalid manifest entries in: {manifest_path}")

    manifest_keys = {
        str(entry.get("composite_key"))
        for entry in entries
        if isinstance(entry, dict) and isinstance(entry.get("composite_key"), str)
    }
    manifest_game_ids = {
        str(entry.get("game_id"))
        for entry in entries
        if isinstance(entry, dict) and isinstance(entry.get("game_id"), str)
    }

    report = {
        "run_id": run_id,
        "manifest_path": str(manifest_path),
        "manifest_entry_count": len(manifest_keys),
        "public_index": analyze_catalog(public_index_path, manifest_keys, manifest_game_ids),
        "obfuscated_index": analyze_catalog(obfuscated_index_path, manifest_keys, manifest_game_ids),
    }
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
