#!/usr/bin/env python3
import json
from pathlib import Path

RUNS = [
    "run_v4_brainrot_momsday_vatsal107_model55_c1_20260509T084144Z",
    "run_v4_flappy_bird_vatsal107_model55_c1_20260509T085122Z",
    "run_v4_harry_potter_vatsal107_model55_c1_20260509T083751Z",
    "run_v4_rick_morty_vatsal107_model55_c1_20260509T083929Z",
    "run_v4_trump_xmusk_vatsal107_model55_c1_20260509T082454Z",
]

BASE = Path("/Volumes/HDD2026/output")
OUT_DIR = Path("tmp/retry_manifests")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def load_json(path: Path):
    return json.loads(path.read_text())


def normalize_game_id(entry):
    if isinstance(entry, str):
        return entry
    if isinstance(entry, dict):
        return entry.get("game_id") or entry.get("id") or entry.get("name")
    return None


def build_retry_manifest(run_name: str):
    run_dir = BASE / run_name
    dashboard = load_json(run_dir / "dashboard" / "dashboard_data.json")
    input_manifest = load_json(run_dir / "input_manifest.json")
    run_state = load_json(run_dir / "run_state.json")

    failed_ids = {
        normalize_game_id(game)
        for game in dashboard.get("games", [])
        if isinstance(game, dict)
        and "fail" in str(game.get("status") or game.get("state") or "").lower()
    }
    failed_ids.discard(None)

    pending_ids = set(run_state.get("pending_game_ids", []))
    retry_ids = failed_ids | pending_ids

    manifest_games = []
    for game in input_manifest.get("games", []):
        game_id = normalize_game_id(game)
        if game_id in retry_ids:
            manifest_games.append(game)

    retry_manifest = {
        "source_run": run_name,
        "retry_game_ids": sorted(retry_ids),
        "games": manifest_games,
    }

    out_path = OUT_DIR / f"{run_name}_retry_manifest.json"
    out_path.write_text(json.dumps(retry_manifest, indent=2) + "\n")

    print(f"{run_name}")
    print(f"  failed_ids: {len(failed_ids)}")
    print(f"  pending_ids: {len(pending_ids)}")
    print(f"  retry_ids: {len(retry_ids)}")
    print(f"  manifest_games: {len(manifest_games)}")
    print(f"  manifest_path: {out_path}")


def main():
    for run in RUNS:
        build_retry_manifest(run)


if __name__ == "__main__":
    main()