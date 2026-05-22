#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path("/Users/hassan/repos/game_agent")
AUDIT_PATH = ROOT / "tmp/generated_metadata_public_tag_recovery_latest/audit.json"
PUBLIC_ROOT = ROOT / "games/published/public"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def metadata_path_for_key(composite_key: str) -> Path:
    game_id, remix_suffix = composite_key.split("__remix-", 1)
    remix_id = f"remix-{remix_suffix}"
    return PUBLIC_ROOT / game_id / remix_id / f"game-obfuscated-{remix_suffix}.json"


def prompt_preview(text: str) -> str:
    lines = [line.strip() for line in str(text or "").splitlines() if line.strip() and not line.strip().startswith("#")]
    return lines[0] if lines else ""


def main() -> None:
    audit = load_json(AUDIT_PATH)
    sample_keys = audit["public"]["no_tags_sample"][:20]
    rows = []
    for key in sample_keys:
        metadata = load_json(metadata_path_for_key(key))
        rows.append(
            {
                "key": key,
                "title": metadata.get("identity", {}).get("title") or metadata.get("title"),
                "prompt_preview": prompt_preview(metadata.get("recreation_prompt_markdown", "")),
            }
        )
    print(json.dumps({"audit_path": str(AUDIT_PATH), "sample_count": len(rows), "rows": rows}, indent=2))


if __name__ == "__main__":
    main()