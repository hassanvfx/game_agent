#!/usr/bin/env python3

import argparse
import json
import subprocess
from pathlib import Path


def run_build(run_dir: Path, game_key: str, worker_id: str, timeout_seconds: int) -> dict:
    completed = subprocess.run(
        [
            "python3",
            "mirror_system.py",
            "build-local-mirror",
            "--run-dir",
            str(run_dir),
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
    parser = argparse.ArgumentParser(description="Rebuild an already-processed batch of replay_pending games.")
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--count", type=int, default=25)
    parser.add_argument("--worker-id", default="batch-001")
    parser.add_argument("--timeout-seconds", type=int, default=30)
    args = parser.parse_args()

    run_dir = Path(args.run_dir)
    queue_dir = run_dir / "queue" / "replay_pending"
    game_keys = sorted(path.stem for path in queue_dir.glob("*.json"))[: args.count]

    results = []
    for index, game_key in enumerate(game_keys, start=1):
        print(f"[rebuild] {index}/{len(game_keys)} {game_key}")
        results.append(run_build(run_dir, game_key, args.worker_id, args.timeout_seconds))

    print(json.dumps({"rebuilt_count": len(results), "results": results}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())