#!/usr/bin/env python3

import argparse
import json
import subprocess


def run_build(run_dir: str, game_key: str, worker_id: str, timeout_seconds: int) -> dict:
    completed = subprocess.run(
        [
            "python3",
            "mirror_system.py",
            "build-local-mirror",
            "--run-dir",
            run_dir,
            "--game-key",
            game_key,
            "--worker-id",
            worker_id,
            "--timeout-seconds",
            str(timeout_seconds),
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"build-local-mirror failed for {game_key}\nSTDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}"
        )
    return json.loads(completed.stdout)


def main() -> int:
    parser = argparse.ArgumentParser(description="Rebuild specific mirror game keys.")
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--worker-id", default="batch-001")
    parser.add_argument("--timeout-seconds", type=int, default=30)
    parser.add_argument("game_keys", nargs="+")
    args = parser.parse_args()

    results = []
