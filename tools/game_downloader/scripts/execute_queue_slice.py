#!/usr/bin/env python3

import argparse
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORE_CLI = ROOT / "game_downloader" / "core" / "mirror_system.py"


QUEUE_STATES = ["pending", "leased", "capturing", "replay_pending", "completed", "failed_retryable", "failed_terminal"]


def run_json(command: list[str]) -> dict:
    completed = subprocess.run(command, text=True, capture_output=True, check=False)
    if completed.returncode != 0:
        raise RuntimeError(
            f"Command failed ({completed.returncode}): {' '.join(command)}\nSTDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}"
        )
    return json.loads(completed.stdout)


def state_keys(run_dir: Path, state: str) -> list[str]:
    return sorted(path.stem for path in (run_dir / "queue" / state).glob("*.json"))


def build_game(run_dir: Path, game_key: str, worker_id: str, timeout_seconds: int) -> dict:
    return run_json(
        [
            "python3",
            str(CORE_CLI),
            "build-local-mirror",
            "--run-dir",
            str(run_dir),
            "--game-key",
            game_key,
            "--worker-id",
            worker_id,
            "--timeout-seconds",
            str(timeout_seconds),
        ]
    )


def transition_to_pending_if_needed(run_dir: Path, game_key: str, worker_id: str) -> dict | None:
    for state in QUEUE_STATES:
        queue_file = run_dir / "queue" / state / f"{game_key}.json"
        if not queue_file.exists():
            continue
        if state == "pending":
            return None
        if state in {"leased", "capturing", "failed_retryable"}:
            return run_json(
                [
                    "python3",
                    str(CORE_CLI),
                    "transition-game",
                    "--run-dir",
                    str(run_dir),
                    "--game-key",
                    game_key,
                    "--target-state",
                    "pending",
                    "--worker-id",
                    worker_id,
                ]
            )
        raise RuntimeError(f"Game {game_key} is in unsupported source state '{state}' for direct slice execution.")
    raise RuntimeError(f"Could not find queue file for {game_key}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Execute an exact slice of queue items by state and offset.")
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--from-state", choices=["pending", "leased", "capturing", "failed_retryable"], required=True)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--count", type=int, default=25)
    parser.add_argument("--worker-id", default="batch-001")
    parser.add_argument("--timeout-seconds", type=int, default=30)
    args = parser.parse_args()

    run_dir = Path(args.run_dir)
    all_keys = state_keys(run_dir, args.from_state)
    selected_keys = all_keys[args.offset : args.offset + args.count]

    results = []
    transitions = []

    for index, game_key in enumerate(selected_keys, start=1):
        print(f"[slice] {index}/{len(selected_keys)} {game_key}")
        transition = transition_to_pending_if_needed(run_dir, game_key, args.worker_id)
        if transition:
            transitions.append(transition)
        results.append(build_game(run_dir, game_key, args.worker_id, args.timeout_seconds))

    progress = run_json(
        [
            "python3",
            str(CORE_CLI),
            "rebuild-report",
            "--run-dir",
            str(run_dir),
        ]
    )

    print(
        json.dumps(
            {
                "run_dir": str(run_dir),
                "from_state": args.from_state,
                "offset": args.offset,
                "count": args.count,
                "selected_count": len(selected_keys),
                "selected_keys": selected_keys,
                "transitions": transitions,
                "results": results,
                "progress": progress,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
