#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

ROOT = Path("/Users/hassan/repos/game_agent")
TOP100_ROOT = ROOT / "games" / "top100_vatsal"
RAW_ROOT = ROOT / "games" / "raw"
FIXTURES_ROOT = ROOT / "tmp" / "game_refactoring_experiments" / "fixtures"
DEFAULT_SEED = 20260508
DEFAULT_SAMPLE_SIZE = 4


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build a reusable Vatsal100 id list, resolve those ids against games/raw, "
            "and optionally emit a sampled raw-backed manifest."
        )
    )
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED, help="Random seed for sampling.")
    parser.add_argument("--sample-size", type=int, default=DEFAULT_SAMPLE_SIZE, help="How many resolved ids to sample.")
    parser.add_argument(
        "--manifest-name",
        default="top100_vatsal_raw_backed_random4_manifest.json",
        help="Output manifest filename under tmp/game_refactoring_experiments/fixtures/.",
    )
    parser.add_argument(
        "--run-label",
        default="top100-vatsal-raw-backed-random4",
        help="run_label value to write into the sampled manifest.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    FIXTURES_ROOT.mkdir(parents=True, exist_ok=True)

    top100_ids = sorted(
        path.name for path in TOP100_ROOT.iterdir() if path.is_dir() and path.name.startswith("gamezone-")
    )
    raw_dirs = {path.name: path for path in RAW_ROOT.iterdir() if path.is_dir()}
    resolved_ids = [game_id for game_id in top100_ids if game_id in raw_dirs]

    if len(resolved_ids) < args.sample_size:
        raise SystemExit(
            f"Requested sample_size={args.sample_size}, but only {len(resolved_ids)} Vatsal100 ids exist in games/raw."
        )

    top100_list_path = FIXTURES_ROOT / "top100_vatsal_gamezone_ids.json"
    top100_list_path.write_text(
        json.dumps(
            {
                "source": str(TOP100_ROOT),
                "game_ids": top100_ids,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    resolved_list_path = FIXTURES_ROOT / "top100_vatsal_raw_resolved_ids.json"
    resolved_list_path.write_text(
        json.dumps(
            {
                "source_top100": str(TOP100_ROOT),
                "source_raw": str(RAW_ROOT),
                "game_ids": resolved_ids,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    selected_ids = random.Random(args.seed).sample(resolved_ids, args.sample_size)
    manifest = {
        "run_label": args.run_label,
        "games": [
            {
                "game_id": game_id,
                "display_name": game_id,
                "source_path": str(raw_dirs[game_id].resolve()),
            }
            for game_id in selected_ids
        ],
    }

    manifest_path = FIXTURES_ROOT / args.manifest_name
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(
        {
            "top100_list_path": str(top100_list_path),
            "resolved_list_path": str(resolved_list_path),
            "manifest_path": str(manifest_path),
            "top100_count": len(top100_ids),
            "resolved_raw_count": len(resolved_ids),
            "selected_ids": selected_ids,
        },
        indent=2,
    ))


if __name__ == "__main__":
    main()