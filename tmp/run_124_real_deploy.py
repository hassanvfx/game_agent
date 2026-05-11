#!/usr/bin/env python3
"""
DEPRECATED LEGACY SCRIPT.

This script only rebuilds public deploy outputs for the historical run-124
batch and does NOT run the canonical publish pipeline, obfuscation stage,
app-artifact refresh, or post-publish validation.

Do not use this script for the canonical Vatsal App Alpha workflow.
Use instead:
  python tools/game_publish_pipeline/scripts/publish_vatsal_app_alpha_231.py

Kept only as historical reference while the canonical pilot-scaled path is
rolled out.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path("/Users/hassan/repos/game_agent")
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.game_deploy.game_deploy.deployer import deploy_one

MANIFEST_PATH = ROOT / "tmp/retry_manifests/run_game_124_manifest.json"
PUBLISHED_ROOT = ROOT / "games/published/public"
SUMMARY_PATH = ROOT / "tmp/deploy_real_run124_summary.json"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_sources(path: Path) -> list[Path]:
    payload = load_json(path)
    entries = payload["entries"] if isinstance(payload, dict) and isinstance(payload.get("entries"), list) else payload
    return [Path(item["source"]).resolve() if isinstance(item, dict) else Path(item).resolve() for item in entries]


def main() -> None:
    sources = load_sources(MANIFEST_PATH)
    results = []
    skipped = []
    for source in sources:
        try:
            result = deploy_one(source=source, published_root=PUBLISHED_ROOT, overwrite=True, dry_run=False)
            results.append(
                {
                    "source": str(source),
                    "game_id": result.game_id,
                    "remix_uuid": result.remix_uuid,
                    "deploy_dir": str(result.deploy_dir),
                    "metadata_path": str(result.metadata_path),
                    "status": "deployed",
                }
            )
        except FileExistsError:
            skipped.append(str(source))

    payload = {
        "manifest": str(MANIFEST_PATH),
        "published_root": str(PUBLISHED_ROOT),
        "entry_count": len(results),
        "skipped_existing_count": len(skipped),
        "skipped_existing_sources": skipped,
        "results": results,
    }
    SUMMARY_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "summary_output": str(SUMMARY_PATH),
                "entry_count": len(results),
                "skipped_existing_count": len(skipped),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()