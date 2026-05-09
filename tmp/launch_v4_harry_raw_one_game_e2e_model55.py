#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_MANIFEST = ROOT / "tmp/game_refactoring_experiments/fixtures/top107_vatsal_raw_backed_harry_potter_manifest.json"
SINGLE_MANIFEST = ROOT / "tmp/game_refactoring_experiments/fixtures/v4_harry_potter_raw_one_game_manifest.json"
RUNS_ROOT = Path("/Volumes/HDD2026/output")
RUN_ID = "run_v4_harry_potter_raw_one_game_model55_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
MODEL = "gpt-5.5"


def build_single_manifest() -> dict:
    source = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    games = source.get("games")
    if not isinstance(games, list) or not games:
        raise RuntimeError(f"No games found in {SOURCE_MANIFEST}")

    selected_game = games[0]
    manifest = {
        "run_label": "v4-harry-potter-raw-one-game-model55",
        "games": [selected_game],
    }
    SINGLE_MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    SINGLE_MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def launch() -> int:
    manifest = build_single_manifest()
    selected_game = manifest["games"][0]
    command = [
        "python3",
        str(ROOT / "tools/game_refactoring/scripts/game_workflow.py"),
        "--json",
        "--id",
        "creative_remix_v4",
        "--games-manifest-source",
        str(SINGLE_MANIFEST),
        "--run-id",
        RUN_ID,
        "--runs-root",
        str(RUNS_ROOT),
        "--source-mode",
        "copy",
        "--pipeline",
        "v2",
        "--model",
        MODEL,
        "--agent-timeout",
        "3600",
        "--max-concurrency",
        "1",
        "--poll-seconds",
        "5",
        "--stale-heartbeat-seconds",
        "900",
        "--remix-prompt",
        "Harry Potter",
    ]

    print(json.dumps({
        "mode": "launch_v4_harry_raw_one_game_e2e_model55",
        "run_id": RUN_ID,
        "model": MODEL,
        "selected_game": selected_game,
        "single_manifest": str(SINGLE_MANIFEST),
        "runs_root": str(RUNS_ROOT),
    }, indent=2))

    completed = subprocess.run(command, cwd=ROOT, text=True)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(launch())