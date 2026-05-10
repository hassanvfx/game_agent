#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path("/Users/hassan/repos/game_agent")
RUNS_ROOT = Path("/Volumes/HDD2026/output")
KNOWN_RUNS = [
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
DEPLOY_MANIFEST = ROOT / "tmp/retry_manifests/latest_selected_remix_deploy_manifest.json"
OUTPUT_MANIFEST = ROOT / "tmp/retry_manifests/latest_selected_remix_republish_manifest.json"
DEPLOY_SCRIPT = ROOT / "tools/game_deploy/scripts/deploy_games.py"
PUBLISHED_ROOT = ROOT / "games/published/public"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def resolve_run_source(source_path: str) -> str:
    source = Path(source_path)
    game_id = source.name
    matches = []
    for run in KNOWN_RUNS:
        candidate = RUNS_ROOT / run / "output" / game_id
        if candidate.exists():
            matches.append(str(candidate))
    if not matches:
        raise RuntimeError(f"No known run source found for {game_id}")
    # deterministically choose the lexicographically last run path
    return sorted(matches)[-1]


def main() -> None:
    deploy_manifest = load_json(DEPLOY_MANIFEST)
    republish_manifest = [{"source": resolve_run_source(item["source"])} for item in deploy_manifest]
    write_json(OUTPUT_MANIFEST, republish_manifest)

    command = [
        sys.executable,
        str(DEPLOY_SCRIPT),
        "--manifest",
        str(OUTPUT_MANIFEST),
        "--published-root",
        str(PUBLISHED_ROOT),
        "--overwrite",
    ]
    completed = subprocess.run(command, capture_output=True, text=True)
    print(completed.stdout or completed.stderr)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


if __name__ == "__main__":
    main()