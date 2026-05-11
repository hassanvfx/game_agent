#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


RAW_SOURCE = Path("/Users/hassan/repos/game_agent/games/raw/gamezone-0f3dc736-8159-48cf-93d0-bd78a54b8cd0")
HDD_SOURCE = Path("/Volumes/HDD2026/output/run_v4_brainrot_momsday_retry_20260509T160832Z/output/gamezone-0f3dc736-8159-48cf-93d0-bd78a54b8cd0")

RAW_RETRY_PUBLIC = Path("tmp/publisher_probe_10_retry/public/gamezone-0f3dc736-8159-48cf-93d0-bd78a54b8cd0/remix-4037302139cfa7befef5d711f08f4b82")
RAW_RETRY_OBF = Path("tmp/publisher_probe_10_retry/obfuscated/gamezone-0f3dc736-8159-48cf-93d0-bd78a54b8cd0/remix-4037302139cfa7befef5d711f08f4b82")

HDD_RETRY_PUBLIC = Path("tmp/publisher_probe_10_retry/public/gamezone-0f3dc736-8159-48cf-93d0-bd78a54b8cd0/remix-c2e0f95e77955251616baff7b6f0c66e")
HDD_RETRY_OBF = Path("tmp/publisher_probe_10_retry/obfuscated/gamezone-0f3dc736-8159-48cf-93d0-bd78a54b8cd0/remix-c2e0f95e77955251616baff7b6f0c66e")


def describe_dir(path: Path) -> dict[str, object]:
    if not path.exists():
        return {"exists": False}
    top = sorted(p.name for p in path.iterdir())
    screenshots = sorted(p.name for p in path.glob("screens*"))
    postvisual = sorted(p.name for p in path.glob("postvisual*"))
    assets_exists = (path / "assets").exists()
    amp_exists = (path / "amp").exists()
    catalogs_exists = (path / "catalogs").exists()
    screenshots_dir = path / "screenshots"
    jpgs = sorted(p.name for p in screenshots_dir.glob("*.jpg")) if screenshots_dir.exists() else []
    return {
        "exists": True,
        "top_level": top,
        "screens_like_files": screenshots,
        "postvisual_files": postvisual,
        "assets_exists": assets_exists,
        "amp_exists": amp_exists,
        "catalogs_exists": catalogs_exists,
        "screenshots_dir_exists": screenshots_dir.exists(),
        "screenshots_jpgs": jpgs,
    }


def main() -> None:
    payload = {
        "raw_source": describe_dir(RAW_SOURCE),
        "hdd_source": describe_dir(HDD_SOURCE),
        "raw_retry_public": describe_dir(RAW_RETRY_PUBLIC),
        "raw_retry_obfuscated": describe_dir(RAW_RETRY_OBF),
        "hdd_retry_public": describe_dir(HDD_RETRY_PUBLIC),
        "hdd_retry_obfuscated": describe_dir(HDD_RETRY_OBF),
    }
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()