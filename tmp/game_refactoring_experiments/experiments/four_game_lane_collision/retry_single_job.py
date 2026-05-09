#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

PLAN_PATH = Path('/Users/hassan/repos/game_agent/tmp/game_refactoring_experiments/experiments/four_game_lane_collision/metadata/experiment_plan.json')


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Retry a single lane-collision experiment job from the saved plan.")
    parser.add_argument("job_id", help="Job id to relaunch, e.g. job_01")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    jobs = {job["job_id"]: job for job in plan["jobs"]}
    try:
        job = jobs[args.job_id]
    except KeyError as exc:
        valid = ", ".join(sorted(jobs))
        raise SystemExit(f"Unknown job_id={args.job_id}. Valid values: {valid}") from exc

    command = job["command"]
    completed = subprocess.run(command, check=True, capture_output=True, text=True, cwd='/Users/hassan/repos/game_agent')
    if completed.stdout:
        print(completed.stdout.strip())
    if completed.stderr:
        print(completed.stderr.strip())


if __name__ == "__main__":
    main()
