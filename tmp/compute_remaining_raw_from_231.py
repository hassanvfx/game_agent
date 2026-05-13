#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = REPO_ROOT / "docs" / "publish_manifests" / "vatsal_app_alpha_231_manifest.json"
RAW_ROOT = REPO_ROOT / "games" / "raw"
OUTPUT_PATH = REPO_ROOT / "tmp" / "remaining_raw_from_231_summary.json"


def load_covered_gamezone_ids() -> list[str]:
    payload = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    return sorted({entry["game_id"] for entry in payload["entries"]})


def load_raw_gamezone_ids() -> list[str]:
    return sorted(
        path.name
        for path in RAW_ROOT.iterdir()
        if path.is_dir() and path.name.startswith("gamezone-")
    )


def main() -> None:
    covered_ids = load_covered_gamezone_ids()
    raw_ids = load_raw_gamezone_ids()
    remaining_ids = sorted(set(raw_ids) - set(covered_ids))

    payload = {
        "manifest_path": str(MANIFEST_PATH),
        "raw_root": str(RAW_ROOT),
        "manifest_entries": len(json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))["entries"]),
        "covered_unique_gamezone_ids": len(covered_ids),
        "raw_gamezone_ids": len(raw_ids),
        "remaining_raw_gamezone_ids": len(remaining_ids),
        "remaining_ids": remaining_ids,
    }

    OUTPUT_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()