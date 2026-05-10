#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path("/Users/hassan/repos/game_agent")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.game_deploy.game_deploy.deployer import deploy_one


MANIFEST_PATH = REPO_ROOT / "tmp/retry_manifests/top107_legacy_deploy_manifest.json"
PUBLISHED_ROOT = REPO_ROOT / "tmp/deploy_smoke_top107_legacy_public"
SUMMARY_PATH = REPO_ROOT / "tmp/deploy_smoke_top107_legacy_summary.json"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_sources(path: Path) -> list[Path]:
    payload = load_json(path)
    entries = payload["entries"] if isinstance(payload, dict) and isinstance(payload.get("entries"), list) else payload
    return [Path(item["source"]).resolve() if isinstance(item, dict) else Path(item).resolve() for item in entries]


def summarize_result(record: dict[str, Any]) -> dict[str, Any]:
    metadata = record["metadata"]
    return {
        "source": record["source"],
        "game_id": record["game_id"],
        "remix_uuid": record["remix_uuid"],
        "deploy_dir": record["deploy_dir"],
        "index_exists": record["index_exists"],
        "assets_dir_exists": record["assets_dir_exists"],
        "screenshot_file_count": record["screenshot_file_count"],
        "screenshots_png_count": len(metadata.get("screenshots_png") or []),
        "screenshots_jpg_count": len(metadata.get("screenshots_jpg") or []),
        "has_semantic_tags": bool(metadata.get("semantic_tags")),
        "has_identity": bool(metadata.get("identity")),
        "has_mechanics": bool(metadata.get("mechanics_classification")),
        "has_recreation_prompt": bool((metadata.get("recreation_prompt_markdown") or "").strip()),
        "has_blueprint": bool((metadata.get("blueprint_markdown") or "").strip()),
    }


def main() -> None:
    sources = load_sources(MANIFEST_PATH)

    if PUBLISHED_ROOT.exists():
        shutil.rmtree(PUBLISHED_ROOT)
    PUBLISHED_ROOT.mkdir(parents=True, exist_ok=True)

    detailed_results: list[dict[str, Any]] = []
    for source in sources:
        result = deploy_one(source=source, published_root=PUBLISHED_ROOT, overwrite=True, dry_run=False)
        metadata = json.loads(result.metadata_path.read_text(encoding="utf-8"))
        screenshots_dir = result.deploy_dir / "screenshots"
        assets_dir = result.deploy_dir / "assets"
        detailed_results.append(
            {
                "source": str(source),
                "game_id": result.game_id,
                "remix_uuid": result.remix_uuid,
                "deploy_dir": str(result.deploy_dir),
                "metadata_path": str(result.metadata_path),
                "index_exists": (result.deploy_dir / "index.html").exists(),
                "assets_dir_exists": assets_dir.exists(),
                "screenshot_file_count": len(sorted(screenshots_dir.glob("*"))) if screenshots_dir.exists() else 0,
                "metadata": metadata,
            }
        )

    summary_results = [summarize_result(item) for item in detailed_results]
    summary = {
        "manifest": str(MANIFEST_PATH),
        "published_root": str(PUBLISHED_ROOT),
        "entry_count": len(summary_results),
        "with_index": sum(1 for item in summary_results if item["index_exists"]),
        "with_assets_dir": sum(1 for item in summary_results if item["assets_dir_exists"]),
        "with_screenshots": sum(1 for item in summary_results if item["screenshot_file_count"] > 0),
        "with_semantic_tags": sum(1 for item in summary_results if item["has_semantic_tags"]),
        "with_identity": sum(1 for item in summary_results if item["has_identity"]),
        "with_mechanics": sum(1 for item in summary_results if item["has_mechanics"]),
        "with_recreation_prompt": sum(1 for item in summary_results if item["has_recreation_prompt"]),
        "with_blueprint": sum(1 for item in summary_results if item["has_blueprint"]),
        "missing_assets_examples": [item["game_id"] for item in summary_results if not item["assets_dir_exists"]][:10],
        "missing_screenshot_examples": [item["game_id"] for item in summary_results if item["screenshot_file_count"] == 0][:10],
        "results": summary_results,
    }

    SUMMARY_PATH.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "summary_output": str(SUMMARY_PATH),
                "published_root": str(PUBLISHED_ROOT),
                "entry_count": len(summary_results),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()