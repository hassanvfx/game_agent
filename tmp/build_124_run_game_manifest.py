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
OUTPUT_PATH = Path("/Users/hassan/repos/game_agent/tmp/retry_manifests/run_game_124_manifest.json")


def main() -> None:
    entries = []
    missing_runs = []

    for run_id in RUNS:
        output_dir = RUNS_ROOT / run_id / "output"
        if not output_dir.exists():
            missing_runs.append(run_id)
            continue

        for child in sorted(output_dir.iterdir()):
            if not child.is_dir() or not child.name.startswith("gamezone-"):
                continue
            entries.append(
                {
                    "run_id": run_id,
                    "game_id": child.name,
                    "source": str(child.resolve()),
                }
            )

    payload = {
        "runs_checked": len(RUNS),
        "missing_runs": missing_runs,
        "entry_count": len(entries),
        "entries": entries,
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(OUTPUT_PATH), "entry_count": len(entries), "missing_runs": missing_runs}, indent=2))


if __name__ == "__main__":
    main()