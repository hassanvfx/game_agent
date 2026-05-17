#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess


PATTERN = r"run_operator_pipeline_batch.py|run_parallel_batch.py|game_workflow.py|creative_refactor_cli.py"


def main() -> None:
    completed = subprocess.run(
        ["pgrep", "-af", PATTERN],
        capture_output=True,
        text=True,
        check=False,
    )
    lines = [line for line in completed.stdout.splitlines() if line.strip()]
    payload = {
        "returncode": completed.returncode,
        "running": bool(lines),
        "matches": lines,
    }
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()