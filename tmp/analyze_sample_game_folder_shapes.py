#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path("/Users/hassan/repos/game_agent")
DEFAULT_MANIFEST = REPO_ROOT / "tmp/retry_manifests/latest_selected_remix_deploy_manifest.json"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Analyze common file/folder shapes across a sample of game output folders.")
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--limit", type=int, default=10)
    return parser


def summarize_source(source_dir: Path) -> dict[str, Any]:
    top_level_files = sorted(path.name for path in source_dir.iterdir() if path.is_file())
    top_level_dirs = sorted(path.name for path in source_dir.iterdir() if path.is_dir())
    all_files = sorted(path.relative_to(source_dir).as_posix() for path in source_dir.rglob("*") if path.is_file())
    return {
        "source": str(source_dir),
        "game_id": source_dir.name,
        "top_level_files": top_level_files,
        "top_level_dirs": top_level_dirs,
        "all_files_count": len(all_files),
    }


def main() -> None:
    args = build_parser().parse_args()
    manifest = load_json(Path(args.manifest))
    sources = [Path(item["source"]).resolve() for item in manifest[: args.limit]]

    summaries = [summarize_source(source) for source in sources]
    common_top_level_files = sorted(set(summaries[0]["top_level_files"]).intersection(*[set(item["top_level_files"]) for item in summaries[1:]])) if summaries else []
    common_top_level_dirs = sorted(set(summaries[0]["top_level_dirs"]).intersection(*[set(item["top_level_dirs"]) for item in summaries[1:]])) if summaries else []

    payload = {
        "sample_count": len(summaries),
        "sources": summaries,
        "common_top_level_files": common_top_level_files,
        "common_top_level_dirs": common_top_level_dirs,
    }
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()