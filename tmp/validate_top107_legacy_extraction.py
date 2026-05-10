#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path("/Users/hassan/repos/game_agent")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tmp.build_adapted_game_json import adapt_source, load_json, write_json


MANIFEST_PATH = REPO_ROOT / "tmp/retry_manifests/top107_legacy_raw_manifest.json"
OUTPUT_PATH = REPO_ROOT / "tmp/adapted_game_json_top107_legacy.json"
SUMMARY_PATH = REPO_ROOT / "tmp/adapted_game_json_top107_legacy_summary.json"


def load_manifest_sources(path: Path) -> list[Path]:
    manifest = load_json(path)
    items = manifest["entries"] if isinstance(manifest, dict) and isinstance(manifest.get("entries"), list) else manifest
    return [Path(item["source"]).resolve() for item in items]


def summarize_results(results: list[dict[str, Any]]) -> dict[str, Any]:
    def metadata_for(result: dict[str, Any]) -> dict[str, Any]:
        return result.get("metadata") or {}

    return {
        "entry_count": len(results),
        "with_assets_dir": sum(1 for r in results if r.get("assets_dir")),
        "with_screenshot_files": sum(1 for r in results if r.get("screenshot_files")),
        "with_semantic_tags": sum(1 for r in results if metadata_for(r).get("semantic_tags")),
        "with_identity": sum(1 for r in results if metadata_for(r).get("identity")),
        "with_mechanics_classification": sum(1 for r in results if metadata_for(r).get("mechanics_classification")),
        "with_recreation_prompt": sum(
            1 for r in results if (metadata_for(r).get("recreation_prompt_markdown") or "").strip()
        ),
        "with_blueprint": sum(1 for r in results if (metadata_for(r).get("blueprint_markdown") or "").strip()),
        "missing_assets_dir_examples": [r["game_id"] for r in results if not r.get("assets_dir")][:10],
        "missing_screenshot_examples": [r["game_id"] for r in results if not r.get("screenshot_files")][:10],
        "missing_semantic_tags_examples": [
            r["game_id"] for r in results if not metadata_for(r).get("semantic_tags")
        ][:10],
        "missing_identity_examples": [r["game_id"] for r in results if not metadata_for(r).get("identity")][:10],
        "missing_mechanics_examples": [
            r["game_id"] for r in results if not metadata_for(r).get("mechanics_classification")
        ][:10],
    }


def main() -> None:
    sources = load_manifest_sources(MANIFEST_PATH)
    results = [adapt_source(source) for source in sources]

    payload = {
        "source_manifest": str(MANIFEST_PATH),
        "sample_count": len(results),
        "results": results,
    }
    summary = summarize_results(results)

    write_json(OUTPUT_PATH, payload)
    write_json(SUMMARY_PATH, summary)

    print(
        json.dumps(
            {
                "output": str(OUTPUT_PATH),
                "summary_output": str(SUMMARY_PATH),
                "entry_count": len(results),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()