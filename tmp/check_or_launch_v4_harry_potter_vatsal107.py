#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "tmp/game_refactoring_experiments/fixtures/top107_vatsal_raw_backed_full_manifest.json"
RUNS_ROOT = Path("/Volumes/HDD2026/output")
RUN_PREFIX = "run_v4_harry_potter_vatsal107_model55_c1_"
MODEL = "gpt-5.5"
PROMPT = "Harry Potter"


def existing_runs() -> list[Path]:
    return sorted(RUNS_ROOT.glob(f"{RUN_PREFIX}*"))


def validate_manifest() -> dict:
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    games = payload.get("games")
    if not isinstance(games, list) or len(games) != 107:
        count = len(games) if isinstance(games, list) else "invalid"
        raise RuntimeError(f"Expected 107 games in {MANIFEST}, got {count}")
    return payload


def launch_new() -> int:
    manifest = validate_manifest()
    run_id = RUN_PREFIX + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    command = [
        "python3",
        str(ROOT / "tools/game_refactoring/scripts/game_workflow.py"),
        "--json",
        "--id",
        "creative_remix_v4",
        "--games-manifest-source",
        str(MANIFEST),
        "--run-id",
        run_id,
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
        "mode": "launch_v4_harry_potter_vatsal107_model55_c1",
        "run_id": run_id,
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


def main() -> None:
    before = existing_runs()
    print(json.dumps({
        "existing_matching_runs_before": [str(path) for path in before],
        "action": "launching_new_harry_potter_vatsal107_run",
    }, indent=2))
    raise SystemExit(launch_new())


if __name__ == "__main__":
    main()