#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path("/Users/hassan/repos/game_agent")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.game_deploy.game_deploy.deployer import compute_folder_content_hash
from tools.game_deploy.game_deploy.metadata_extractor import extract_game_metadata

DEFAULT_MANIFEST = REPO_ROOT / "tmp/retry_manifests/latest_selected_remix_deploy_manifest.json"
DEFAULT_OUTPUT = REPO_ROOT / "tmp/adapted_game_json_sample.json"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build adapted normalized game JSON from selected game output folders.")
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    return parser


def adapt_source(source_dir: Path) -> dict[str, Any]:
    remix_uuid = compute_folder_content_hash(source_dir)[:32]
    extracted = extract_game_metadata(source_dir=source_dir, remix_uuid=remix_uuid, repo_root=REPO_ROOT)
    metadata = extracted.metadata_payload
    return {
        "source": str(source_dir),
        "run_id": extracted.run_id,
        "game_id": extracted.game_id,
        "remix_id": extracted.remix_id,
        "remix_uuid": remix_uuid,
        "remix_parent_id": extracted.remix_parent_id,
        "root_game_id": extracted.root_game_id,
        "lineage_depth": extracted.lineage_depth,
        "index_html": str(extracted.index_path),
        "assets_dir": str(extracted.assets_dir) if extracted.assets_dir else None,
        "screenshot_files": [str(path) for path in extracted.screenshot_files],
        "metadata": metadata,
    }


def main() -> None:
    args = build_parser().parse_args()
    manifest = load_json(Path(args.manifest))
    if isinstance(manifest, dict) and isinstance(manifest.get("entries"), list):
        items = manifest["entries"]
    else:
        items = manifest
    sources = [Path(item["source"]).resolve() for item in items[: args.limit]]

    payload = {
        "source_manifest": str(Path(args.manifest)),
        "sample_count": len(sources),
        "results": [adapt_source(source) for source in sources],
    }
    write_json(Path(args.output), payload)
    print(json.dumps({"output": str(Path(args.output)), "sample_count": len(sources)}, indent=2))


if __name__ == "__main__":
    main()