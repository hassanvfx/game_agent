#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "tmp/game_refactoring_experiments/fixtures/top100_vatsal_first_game_manifest.json"
RUNS_ROOT = ROOT / "tmp/game_refactoring_experiments/runs"
RUN_ID = "run_v4_harry_potter_one_game_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def main() -> None:
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
        "gpt-5.4",
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
    print(json.dumps({"launching": command, "run_id": RUN_ID, "runs_root": str(RUNS_ROOT)}, indent=2))
    completed = subprocess.run(command, cwd=ROOT, text=True)
    raise SystemExit(completed.returncode)


if __name__ == "__main__":
    main()