#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path("/Users/hassan/repos/game_agent")
AUDIT_PATH = ROOT / "tmp/generated_metadata_public_tag_recovery_latest/audit.json"
PUBLISHED_ROOT = ROOT / "games/published/public"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def published_metadata_path(composite_key: str) -> Path:
    game_id, remix_suffix = composite_key.split("__remix-", 1)
    remix_id = f"remix-{remix_suffix}"
    return PUBLISHED_ROOT / game_id / remix_id / f"game-obfuscated-{remix_suffix}.json"


def resolve_source_dir(source_output_dir: str) -> Path | None:
    if not source_output_dir:
        return None
    raw = Path(source_output_dir)
    candidates = []
    if raw.is_absolute():
        candidates.append(raw)
    else:
        candidates.extend(
            [
                ROOT / source_output_dir,
                ROOT / "games/raw" / source_output_dir,
                ROOT / "games/published/public" / source_output_dir,
            ]
        )
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def structured_files(source_dir: Path) -> list[str]:
    files: list[str] = []
    for path in sorted(source_dir.rglob("*")):
        if not path.is_file():
            continue
        if path.name.startswith("._"):
            continue
        if path.suffix.lower() != ".json":
            continue
        files.append(path.relative_to(source_dir).as_posix())
    return files


def summarize_json(path: Path) -> dict:
    payload = load_json(path)
    if isinstance(payload, dict):
        return {"type": "dict", "keys": sorted(payload.keys())[:20]}
    if isinstance(payload, list):
        return {"type": "list", "length": len(payload)}
    return {"type": type(payload).__name__}


def main() -> None:
    audit = load_json(AUDIT_PATH)
    sample_keys = audit["public"]["no_tags_sample"][:12]
    results = []
    for key in sample_keys:
        meta_path = published_metadata_path(key)
        metadata = load_json(meta_path)
        source_output_dir = str(metadata.get("deploy", {}).get("source_output_dir") or "")
        source_dir = resolve_source_dir(source_output_dir)
        json_files = structured_files(source_dir) if source_dir else []
        summaries = {}
        for rel_path in json_files[:12]:
            summaries[rel_path] = summarize_json(source_dir / rel_path)
        results.append(
            {
                "key": key,
                "published_metadata_path": str(meta_path),
                "source_output_dir": source_output_dir,
                "resolved_source_dir": str(source_dir) if source_dir else None,
                "structured_json_files": json_files,
                "structured_json_summaries": summaries,
            }
        )
    print(json.dumps({"audit_path": str(AUDIT_PATH), "results": results}, indent=2))


if __name__ == "__main__":
    main()