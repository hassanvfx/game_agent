#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

DEFAULT_RUNS = [
    "run_v4_rick_morty_vatsal107_model55_c1_20260509T083929Z",
    "run_v4_brainrot_momsday_retry_20260509T160832Z",
    "run_v4_brainrot_momsday_retry2_20260509T174740Z",
    "run_v4_brainrot_momsday_vatsal107_model55_c1_20260509T084144Z",
    "run_v4_flappy_bird_pending_manual_20260510T113810Z",
    "run_v4_flappy_bird_pending_manual_20260510T121747Z",
    "run_v4_flappy_bird_retry_20260509T160602Z",
    "run_v4_flappy_bird_retry2_20260509T174740Z",
    "run_v4_flappy_bird_vatsal107_model55_c1_20260509T085122Z",
    "run_v4_harry_potter_retry_20260509T160354Z",
    "run_v4_harry_potter_retry2_20260509T174740Z",
    "run_v4_harry_potter_vatsal107_model55_c1_20260509T083751Z",
    "run_v4_rick_morty_retry_20260509T161119Z",
    "run_v4_rick_morty_retry2_20260509T174740Z",
    "run_v4_rick_morty_retry2_20260510T054341Z",
    "run_v4_rick_morty_retry2_20260510T080658Z",
    "run_v4_rick_morty_retry2_20260510T082742Z",
]

DEFAULT_RUNS_ROOT = Path("/Volumes/HDD2026/output")
DEFAULT_OUTPUT_PATH = Path("tmp/retry_manifests/latest_selected_remix_deploy_manifest.json")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build a deploy-ready manifest from the most recent valid remix outputs across historical runs."
    )
    parser.add_argument(
        "--runs-root",
        default=str(DEFAULT_RUNS_ROOT),
        help="Base directory containing historical run directories.",
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT_PATH),
        help="Path where the deploy-ready manifest JSON will be written.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the selected remix sources without writing the manifest.",
    )
    return parser


def discover_run_game_sources(run_dir: Path) -> dict[str, Path]:
    input_manifest_path = run_dir / "input_manifest.json"
    output_root = run_dir / "output"
    if not input_manifest_path.exists() or not output_root.exists():
        return {}

    input_manifest = load_json(input_manifest_path)
    games = input_manifest.get("games", []) if isinstance(input_manifest, dict) else []
    selected: dict[str, Path] = {}
    for game in games:
        if not isinstance(game, dict):
            continue
        game_id = game.get("game_id")
        if not isinstance(game_id, str) or not game_id:
            continue
        candidate = output_root / game_id
        if (candidate / "index.html").exists():
            selected[game_id] = candidate.resolve()
    return selected


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    runs_root = Path(args.runs_root).resolve()
    output_path = Path(args.output).resolve()

    print("== Build Deploy Manifest From Historical Runs ==")
    print(f"Runs root: {runs_root}")
    print(f"Output manifest: {output_path}")
    print(f"Historical runs supplied: {len(DEFAULT_RUNS)}")

    selected_sources: dict[str, Path] = {}
    selected_from_run: dict[str, str] = {}

    for index, run_name in enumerate(DEFAULT_RUNS, start=1):
        run_dir = runs_root / run_name
        print(f"\n[{index:02d}/{len(DEFAULT_RUNS):02d}] {run_name}")
        if not run_dir.exists():
            print("  - missing run directory")
            continue

        run_sources = discover_run_game_sources(run_dir)
        print(f"  - usable remix outputs found: {len(run_sources)}")
        for game_id, source_path in sorted(run_sources.items()):
            selected_sources[game_id] = source_path
            selected_from_run[game_id] = run_name
            print(f"    -> {game_id}")
            print(f"       {source_path}")

    manifest_payload = [{"source": str(path)} for _, path in sorted(selected_sources.items())]

    print("\n== Final Selection ==")
    print(f"Unique game ids selected: {len(manifest_payload)}")
    for game_id in sorted(selected_sources):
        print(f"  - {game_id}")
        print(f"    source: {selected_sources[game_id]}")
        print(f"    from:   {selected_from_run[game_id]}")

    if args.dry_run:
        print("\nDry run only. Manifest not written.")
        return 0

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(manifest_payload, indent=2) + "\n", encoding="utf-8")
    print(f"\nManifest written to: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())