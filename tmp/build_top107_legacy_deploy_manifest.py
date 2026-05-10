#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path("/Users/hassan/repos/game_agent")
SOURCE_MANIFEST = REPO_ROOT / "tmp/retry_manifests/top107_legacy_raw_manifest.json"
OUTPUT_MANIFEST = REPO_ROOT / "tmp/retry_manifests/top107_legacy_deploy_manifest.json"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    source_payload = load_json(SOURCE_MANIFEST)
    source_entries = (
        source_payload["entries"]
        if isinstance(source_payload, dict) and isinstance(source_payload.get("entries"), list)
        else source_payload
    )

    entries: list[dict[str, str]] = []
    for item in source_entries:
        source = item["source"] if isinstance(item, dict) else item
        entries.append({"source": str(Path(source).resolve())})

    payload = {
        "batch_name": "top107_legacy_deploy",
        "generated_from": str(SOURCE_MANIFEST),
        "entry_count": len(entries),
        "entries": entries,
    }
    write_json(OUTPUT_MANIFEST, payload)
    print(json.dumps({"output": str(OUTPUT_MANIFEST), "entry_count": len(entries)}, indent=2))


if __name__ == "__main__":
    main()