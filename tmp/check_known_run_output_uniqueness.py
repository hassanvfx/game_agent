#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

RUNS = [
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
    "run_v4_rick_morty_vatsal107_model55_c1_20260509T083929Z",
]

RUNS_ROOT = Path("/Volumes/HDD2026/output")


def main() -> None:
    combos: list[str] = []
    runs_by_game: dict[str, list[str]] = {}
    missing_runs: list[str] = []

    for run_id in RUNS:
        output_dir = RUNS_ROOT / run_id / "output"
        if not output_dir.exists():
            missing_runs.append(run_id)
            continue

        for child in sorted(output_dir.iterdir()):
            if not child.is_dir() or not child.name.startswith("gamezone-"):
                continue
            game_id = child.name
            combos.append(f"{run_id}/{game_id}")
            runs_by_game.setdefault(game_id, []).append(run_id)

    duplicate_games = {
        game_id: sorted(run_ids)
        for game_id, run_ids in sorted(runs_by_game.items())
        if len(run_ids) > 1
    }

    payload = {
        "runs_checked": len(RUNS),
        "missing_runs": missing_runs,
        "unique_runid_gameid_combos_found": len(set(combos)),
        "unique_game_ids_found": len(runs_by_game),
        "game_ids_present_in_multiple_runs_count": len(duplicate_games),
        "sample_duplicate_games": dict(list(duplicate_games.items())[:20]),
    }
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()