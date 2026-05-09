#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "tmp/game_refactoring_experiments/fixtures/top107_vatsal_raw_backed_full_manifest.json"
RUNS_ROOT = Path("/Volumes/HDD2026/output")
RUN_ID = "run_v4_rick_morty_vatsal107_model55_c1_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
MODEL = "gpt-5.5"
PROMPT = "Rick & Morty"


def validate_manifest() -> dict:
    if not MANIFEST.exists():
        raise FileNotFoundError(MANIFEST)

    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    games = payload.get("games")
    if not isinstance(games, list) or len(games) != 107:
        raise RuntimeError(f"Expected exactly 107 games in {MANIFEST}, got {len(games) if isinstance(games, list) else 'invalid'}")

    return payload


def launch() -> int:
    manifest = validate_manifest()
    command = [
        "python3",
        str(ROOT / "tools/game_refactoring/scripts/game_workflow.py"),
        "--json",
        "--id",
        "creative_remix_v4",
        "--games-manifest-source",
        str(MANIFEST),
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
        PROMPT,
    ]

    print(json.dumps({
        "mode": "launch_v4_rick_morty_vatsal107_model55_c1",
        "run_id": RUN_ID,
        "workflow": "creative_remix_v4",
        "model": MODEL,
        "prompt": PROMPT,
        "max_concurrency": 1,
        "manifest": str(MANIFEST),
        "manifest_run_label": manifest.get("run_label"),
        "game_count": len(manifest["games"]),
        "runs_root": str(RUNS_ROOT),
    }, indent=2))

    completed = subprocess.run(command, cwd=ROOT, text=True)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(launch())