#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path


SOURCE_ROOT_DEFAULT = Path("/Volumes/Elements/game_remix_editor/runs/run_game_remixer_20260505T223213Z/output")
OUTPUT_MANIFEST_DEFAULT = Path("fixtures/specimen_random10_manifest.json")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a random 10-game specimen manifest from a sibling output directory.")
    parser.add_argument("--source-root", type=Path, default=SOURCE_ROOT_DEFAULT)
    parser.add_argument("--output-manifest", type=Path, default=OUTPUT_MANIFEST_DEFAULT)
    parser.add_argument("--count", type=int, default=10)
    parser.add_argument("--seed", type=int, default=20260506)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source_root = args.source_root.resolve()

    candidates = sorted(
        path for path in source_root.iterdir()
        if path.is_dir() and (path / "index.html").exists()
    )

    if len(candidates) < args.count:
        raise SystemExit(f"Need at least {args.count} game directories with index.html, found {len(candidates)}")

    rng = random.Random(args.seed)
    selected = rng.sample(candidates, args.count)

    payload = {
        "manifest_version": "2.0.0",
        "run_label": "specimen-random10-analytic-chain",
        "created_at": "2026-05-06T00:00:00Z",
        "nodes": [
            {
                "id": "inference_outputs",
                "prompt_file": "prompts/operators_v2/01_specimen_inference_outputs.md",
                "accepted_upstream_statuses": ["ok", "warning", "error"],
                "requires_contract": False,
            },
            {
                "id": "model_delta_fix",
                "prompt_file": "prompts/operators_v2/02_specimen_model_delta_fix.md",
                "accepted_upstream_statuses": ["ok"],
                "requires_contract": True,
            },
            {
                "id": "creative_code_refactor",
                "prompt_file": "prompts/operators_v2/03_specimen_creative_code_refactor.md",
                "accepted_upstream_statuses": ["ok"],
                "requires_contract": True,
            },
        ],
        "games": [
            {
                "game_id": path.name,
                "source_path": str(path),
                "display_name": path.name,
            }
            for path in selected
        ],
    }

    output_manifest = args.output_manifest
    output_manifest.parent.mkdir(parents=True, exist_ok=True)
    output_manifest.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    print(output_manifest)
    for path in selected:
        print(path.name)


if __name__ == "__main__":
    main()