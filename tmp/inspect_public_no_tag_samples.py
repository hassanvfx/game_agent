#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path("/Users/hassan/repos/game_agent")
DEFAULT_AUDIT_PATH = ROOT / "tmp/generated_metadata_repair_probe_20260521T2227Z/audit.json"
DEFAULT_PUBLIC_ROOT = ROOT / "games/published/public"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def candidate_metadata_path(public_root: Path, composite_key: str) -> Path:
    game_id, remix_id = composite_key.split("__remix-", 1)
    remix_id = f"remix-{remix_id}"
    remix_dir = public_root / game_id / remix_id
    return remix_dir / f"game-obfuscated-{remix_id.removeprefix('remix-')}.json"


def summarize_tags(metadata: dict) -> dict:
    semantic = metadata.get("semantic_tags") if isinstance(metadata.get("semantic_tags"), dict) else {}
    identity = metadata.get("identity") if isinstance(metadata.get("identity"), dict) else {}
    mechanics = metadata.get("mechanics_classification") if isinstance(metadata.get("mechanics_classification"), dict) else {}
    return {
        "semantic_keys": sorted(semantic.keys()),
        "semantic_tags_type": type(semantic.get("tags")).__name__ if "tags" in semantic else None,
        "identity_keys": sorted(identity.keys()),
        "mechanics_keys": sorted(mechanics.keys()),
        "ranked_mechanics_count": len(mechanics.get("ranked_mechanics", [])) if isinstance(mechanics.get("ranked_mechanics"), list) else 0,
        "selected_top_5_count": len(mechanics.get("selected_top_5", [])) if isinstance(mechanics.get("selected_top_5"), list) else 0,
    }


def preview_prompt(metadata: dict) -> str:
    prompt = str(metadata.get("recreation_prompt_markdown") or "").strip().splitlines()
    return " | ".join(line.strip() for line in prompt[:4] if line.strip())


def main() -> None:
    audit = load_json(DEFAULT_AUDIT_PATH)
    sample_keys = audit.get("public", {}).get("no_tags_sample", [])[:12]
    print(json.dumps({
        "audit_path": str(DEFAULT_AUDIT_PATH),
        "sample_count": len(sample_keys),
        "sample_keys": sample_keys,
    }, indent=2))
    print("\nDETAILS")
    for composite_key in sample_keys:
        path = candidate_metadata_path(DEFAULT_PUBLIC_ROOT, composite_key)
        metadata = load_json(path)
        print(json.dumps({
            "composite_key": composite_key,
            "metadata_path": str(path),
            "tag_summary": summarize_tags(metadata),
            "prompt_preview": preview_prompt(metadata),
        }, indent=2))


if __name__ == "__main__":
    main()