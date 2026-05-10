#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Any

MANIFEST_PATH = Path("/Users/hassan/repos/game_agent/tmp/retry_manifests/top107_legacy_raw_manifest.json")
OUTPUT_PATH = Path("/Users/hassan/repos/game_agent/tmp/top107_legacy_raw_sample_analysis.json")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Analyze a random sample of 10 legacy raw Vatsal top107 folders.")
    parser.add_argument("--seed", type=int, default=107)
    parser.add_argument("--count", type=int, default=10)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    payload = load_json(MANIFEST_PATH)
    entries = list(payload["entries"])
    rng = random.Random(args.seed)
    selected = rng.sample(entries, args.count)

    summaries = [summarize_source(Path(item["source"])) for item in selected]
    common_top_level_files = sorted(set(summaries[0]["top_level_files"]).intersection(*[set(item["top_level_files"]) for item in summaries[1:]])) if summaries else []
    common_top_level_dirs = sorted(set(summaries[0]["top_level_dirs"]).intersection(*[set(item["top_level_dirs"]) for item in summaries[1:]])) if summaries else []

    output = {
        "seed": args.seed,
        "sample_count": len(summaries),
        "samples": summaries,
        "common_top_level_files": common_top_level_files,
        "common_top_level_dirs": common_top_level_dirs,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(OUTPUT_PATH), "sample_count": len(summaries), "seed": args.seed}, indent=2))


if __name__ == "__main__":
    main()