#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path("/Users/hassan/repos/game_agent")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.game_deploy.game_deploy.deployer import compute_folder_content_hash
from tools.game_deploy.game_deploy.metadata_extractor import extract_game_metadata


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Quick test harness for shared game metadata extraction.")
    parser.add_argument("inputs", nargs="+", help="One or more game output folders to inspect.")
    return parser


def summarize(input_path: Path) -> dict:
    remix_uuid = compute_folder_content_hash(input_path)[:32]
    extracted = extract_game_metadata(source_dir=input_path, remix_uuid=remix_uuid, repo_root=REPO_ROOT)
    metadata = extracted.metadata_payload
    return {
        "source": str(input_path),
        "game_id": extracted.game_id,
        "remix_uuid": remix_uuid,
        "index_html": str(extracted.index_path),
        "assets_dir": str(extracted.assets_dir) if extracted.assets_dir else None,
        "screenshot_files_count": len(extracted.screenshot_files),
        "screenshots_png_count": len(metadata.get("screenshots_png") or []),
        "screenshots_jpg_count": len(metadata.get("screenshots_jpg") or []),
        "semantic_tags_keys": sorted((metadata.get("semantic_tags") or {}).keys()),
        "identity_keys": sorted((metadata.get("identity") or {}).keys()),
        "mechanics_keys": sorted((metadata.get("mechanics_classification") or {}).keys()),
        "has_recreation_prompt": bool((metadata.get("recreation_prompt_markdown") or "").strip()),
        "has_blueprint": bool((metadata.get("blueprint_markdown") or "").strip()),
        "deploy_source_output_dir": ((metadata.get("deploy") or {}).get("source_output_dir")),
    }


def main() -> None:
    args = build_parser().parse_args()
    results = [summarize(Path(value).resolve()) for value in args.inputs]
    print(json.dumps({"results": results}, indent=2))


if __name__ == "__main__":
    main()