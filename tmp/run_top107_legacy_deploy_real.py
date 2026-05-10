#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path("/Users/hassan/repos/game_agent")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.game_deploy.game_deploy.deployer import deploy_one


MANIFEST_PATH = REPO_ROOT / "tmp/retry_manifests/top107_legacy_deploy_manifest.json"
PUBLISHED_ROOT = REPO_ROOT / "games/published/public"
SUMMARY_PATH = REPO_ROOT / "tmp/deploy_real_top107_legacy_summary.json"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_sources(path: Path) -> list[Path]:
    payload = load_json(path)
    entries = payload["entries"] if isinstance(payload, dict) and isinstance(payload.get("entries"), list) else payload
    return [Path(item["source"]).resolve() if isinstance(item, dict) else Path(item).resolve() for item in entries]


def main() -> None:
    sources = load_sources(MANIFEST_PATH)

    results = []
    for source in sources:
        result = deploy_one(source=source, published_root=PUBLISHED_ROOT, overwrite=False, dry_run=False)
        results.append(
            {
                "source": str(source),
                "game_id": result.game_id,
                "remix_uuid": result.remix_uuid,
                "deploy_dir": str(result.deploy_dir),
                "metadata_path": str(result.metadata_path),
            }
        )

    summary = {
        "manifest": str(MANIFEST_PATH),
        "published_root": str(PUBLISHED_ROOT),
        "entry_count": len(results),
        "results": results,
    }
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"summary_output": str(SUMMARY_PATH), "entry_count": len(results)}, indent=2))


if __name__ == "__main__":
    main()