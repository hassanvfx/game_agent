#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.report_pending_counts import PROMPT_RUNS, compute_prompt_summary, load_json, normalize_game_id

DEFAULT_BASE_MANIFEST = "tmp/game_refactoring_experiments/fixtures/top107_vatsal_raw_backed_harry_potter_manifest.json"
DEFAULT_RUNS_ROOT = "/Volumes/HDD2026/output"
DEFAULT_OUTPUT_DIR = "tmp/game_refactoring_cli_queue_pending_manifests"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate pending-only manifests per prompt from scripted run reconciliation.")
    parser.add_argument("--base-manifest", default=DEFAULT_BASE_MANIFEST)
    parser.add_argument("--runs-root", default=DEFAULT_RUNS_ROOT)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--json", action="store_true", help="Print JSON summary to stdout")
    return parser.parse_args()


def slugify(value: str) -> str:
    cleaned = []
    for char in value.lower():
        if char.isalnum():
            cleaned.append(char)
        else:
            cleaned.append("-")
    slug = "".join(cleaned)
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug.strip("-") or "job"


def main() -> int:
    args = parse_args()
    base_manifest_path = Path(args.base_manifest)
    base_manifest = load_json(base_manifest_path)
    base_games = base_manifest.get("games", [])
    base_by_id = {}
    for game in base_games:
        game_id = normalize_game_id(game)
        if game_id:
            base_by_id[game_id] = game

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    results = []
    for prompt_key, family in PROMPT_RUNS.items():
        summary = compute_prompt_summary(prompt_key, family, set(base_by_id.keys()), Path(args.runs_root))
        pending_games = [base_by_id[game_id] for game_id in summary["pending_game_ids"] if game_id in base_by_id]
        payload = dict(base_manifest)
        payload["games"] = pending_games
        payload["pending_context"] = {
            "prompt_key": prompt_key,
            "generated_from": str(base_manifest_path),
            "source_runs": summary["source_runs"],
            "pending_count": summary["pending_count"],
            "resolved_count": summary["resolved_count"],
        }

        manifest_path = output_dir / f"{slugify(prompt_key)}.json"
        manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

        results.append(
            {
                "prompt": prompt_key,
                "manifest_path": str(manifest_path),
                "pending_count": summary["pending_count"],
                "resolved_count": summary["resolved_count"],
            }
        )

    summary_payload = {
        "base_manifest": str(base_manifest_path),
        "runs_root": str(Path(args.runs_root)),
        "output_dir": str(output_dir),
        "results": results,
    }

    if args.json:
        print(json.dumps(summary_payload, indent=2))
    else:
        for item in results:
            print(f"{item['prompt']}: pending={item['pending_count']} resolved={item['resolved_count']} manifest={item['manifest_path']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())