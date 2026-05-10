#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

DEFAULT_BASE_MANIFEST = "tmp/game_refactoring_experiments/fixtures/top107_vatsal_raw_backed_harry_potter_manifest.json"
DEFAULT_RUNS_ROOT = "/Volumes/HDD2026/output"
DEFAULT_OUTPUT_PATH = "tmp/retry_manifests/pending_counts_summary.json"

PROMPT_RUNS: dict[str, dict[str, Any]] = {
    "rick_morty": {
        "remix_prompt": "rick and morty",
        "runs": [
            "run_v4_rick_morty_vatsal107_model55_c1_20260509T083929Z",
            "run_v4_rick_morty_retry_20260509T161119Z",
            "run_v4_rick_morty_retry2_20260509T174740Z",
            "run_v4_rick_morty_retry2_20260510T054341Z",
            "run_v4_rick_morty_retry2_20260510T080658Z",
            "run_v4_rick_morty_retry2_20260510T082742Z",
        ],
    },
    "brainrot_momsday": {
        "remix_prompt": "brainrot 3d art mom's day",
        "runs": [
            "run_v4_brainrot_momsday_vatsal107_model55_c1_20260509T084144Z",
            "run_v4_brainrot_momsday_retry_20260509T160832Z",
            "run_v4_brainrot_momsday_retry2_20260509T174740Z",
        ],
    },
    "flappy_bird": {
        "remix_prompt": "flappy bird",
        "runs": [
            "run_v4_flappy_bird_vatsal107_model55_c1_20260509T085122Z",
            "run_v4_flappy_bird_retry_20260509T160602Z",
            "run_v4_flappy_bird_retry2_20260509T174740Z",
        ],
    },
    "harry_potter": {
        "remix_prompt": "harry potter",
        "runs": [
            "run_v4_harry_potter_vatsal107_model55_c1_20260509T083751Z",
            "run_v4_harry_potter_retry_20260509T160354Z",
            "run_v4_harry_potter_retry2_20260509T174740Z",
        ],
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Report pending counts per prompt from curated run folders.")
    parser.add_argument("--base-manifest", default=DEFAULT_BASE_MANIFEST)
    parser.add_argument("--runs-root", default=DEFAULT_RUNS_ROOT)
    parser.add_argument("--output", default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--json", action="store_true", help="Print JSON to stdout")
    return parser.parse_args()


def parse_json_text(text: str) -> Any:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        decoder = json.JSONDecoder()
        obj, _ = decoder.raw_decode(text.lstrip())
        return obj


def load_json(path: Path) -> Any:
    return parse_json_text(path.read_text(encoding="utf-8"))


def load_json_if_exists(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return load_json(path)


def normalize_game_id(entry: Any) -> str | None:
    if isinstance(entry, str):
        return entry
    if isinstance(entry, dict):
        value = entry.get("game_id") or entry.get("id") or entry.get("name")
        if value is not None:
            return str(value)
    return None


def classify_run(run_dir: Path) -> dict[str, Any]:
    completed_ids: set[str] = set()
    output_dir = run_dir / "output"
    if output_dir.exists():
        for child in output_dir.iterdir():
            if child.is_dir():
                completed_ids.add(child.name)

    return {
        "completed_ids": completed_ids,
        "exists": run_dir.exists(),
    }


def compute_prompt_summary(prompt_key: str, family: dict[str, Any], base_ids: set[str], runs_root: Path) -> dict[str, Any]:
    resolved_ids: set[str] = set()
    run_summaries: list[dict[str, Any]] = []

    for run_name in family["runs"]:
        run_dir = runs_root / run_name
        classified = classify_run(run_dir)
        resolved_ids |= classified["completed_ids"]
        run_summaries.append(
            {
                "run_name": run_name,
                "exists": classified["exists"],
                "completed_count": len(classified["completed_ids"] & base_ids),
            }
        )

    pending_ids = sorted(base_ids - resolved_ids)
    return {
        "prompt": prompt_key,
        "remix_prompt": family["remix_prompt"],
        "pending_count": len(pending_ids),
        "resolved_count": len(resolved_ids & base_ids),
        "pending_game_ids": pending_ids,
        "source_runs": list(family["runs"]),
        "run_summaries": run_summaries,
    }


def main() -> int:
    args = parse_args()
    base_manifest = load_json(Path(args.base_manifest))
    base_ids = {
        gid
        for gid in (normalize_game_id(game) for game in base_manifest.get("games", []))
        if gid
    }
    runs_root = Path(args.runs_root)

    results = [compute_prompt_summary(prompt, family, base_ids, runs_root) for prompt, family in PROMPT_RUNS.items()]
    payload = {
        "base_manifest": str(Path(args.base_manifest)),
        "runs_root": str(runs_root),
        "prompts": results,
    }

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        for item in results:
            print(f"{item['prompt']}: pending={item['pending_count']} resolved={item['resolved_count']}")
            for run_summary in item["run_summaries"]:
                print(
                    f"  - {run_summary['run_name']}: "
                    f"exists={run_summary['exists']} "
                    f"completed={run_summary['completed_count']}"
                )
        print(f"\nWrote {output_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())