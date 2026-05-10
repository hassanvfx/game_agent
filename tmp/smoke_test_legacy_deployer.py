#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path("/Users/hassan/repos/game_agent")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.game_deploy.game_deploy.deployer import deploy_one


SOURCE_DIR = REPO_ROOT / "games/raw/gamezone-0f3dc736-8159-48cf-93d0-bd78a54b8cd0"
PUBLISHED_ROOT = REPO_ROOT / "tmp/deploy_smoke_legacy_public"
SUMMARY_PATH = REPO_ROOT / "tmp/deploy_smoke_legacy_summary.json"


def main() -> None:
    if PUBLISHED_ROOT.exists():
        shutil.rmtree(PUBLISHED_ROOT)
    PUBLISHED_ROOT.mkdir(parents=True, exist_ok=True)

    result = deploy_one(
        source=SOURCE_DIR,
        published_root=PUBLISHED_ROOT,
        overwrite=True,
        dry_run=False,
    )

    deploy_dir = result.deploy_dir
    metadata_path = result.metadata_path
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    screenshots_dir = deploy_dir / "screenshots"
    assets_dir = deploy_dir / "assets"

    summary = {
        "source": str(SOURCE_DIR),
        "game_id": result.game_id,
        "remix_uuid": result.remix_uuid,
        "deploy_dir": str(deploy_dir),
        "metadata_path": str(metadata_path),
        "index_exists": (deploy_dir / "index.html").exists(),
        "assets_dir_exists": assets_dir.exists(),
        "screenshot_file_count": len(sorted(screenshots_dir.glob("*"))) if screenshots_dir.exists() else 0,
        "metadata_keys": sorted(metadata.keys()),
        "screenshots_png_count": len(metadata.get("screenshots_png") or []),
        "screenshots_jpg_count": len(metadata.get("screenshots_jpg") or []),
        "semantic_tags_keys": sorted((metadata.get("semantic_tags") or {}).keys()),
        "identity_keys": sorted((metadata.get("identity") or {}).keys()),
        "mechanics_keys": sorted((metadata.get("mechanics_classification") or {}).keys()),
        "deploy_source_output_dir": ((metadata.get("deploy") or {}).get("source_output_dir")),
    }

    SUMMARY_PATH.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()