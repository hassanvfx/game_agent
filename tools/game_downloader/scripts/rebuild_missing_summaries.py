#!/usr/bin/env python3

import argparse
import json
import subprocess
from pathlib import Path


def load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def find_latest_attempt_name(path: Path) -> str | None:
    if not path.exists():
        return None
    candidates = sorted(child.name for child in path.iterdir() if child.is_dir() and child.name.startswith("attempt_"))
    return candidates[-1] if candidates else None


def find_missing_summary_game_keys(run_dir: Path) -> list[str]:
    missing = []
    for game_dir in sorted(path for path in (run_dir / "games").iterdir() if path.is_dir()):
        replay_root = game_dir / "replay"
        latest_replay_attempt = find_latest_attempt_name(replay_root)
        if latest_replay_attempt is None:
            missing.append(game_dir.name)
            continue
        summary_path = replay_root / latest_replay_attempt / "mirror_build_summary.json"
        if not summary_path.exists():
            missing.append(game_dir.name)
    return missing


def classify_game_state(run_dir: Path, game_key: str) -> dict:
    game_dir = run_dir / "games" / game_key
    attempts_root = game_dir / "attempts"
    replay_root = game_dir / "replay"
    latest_attempt = find_latest_attempt_name(attempts_root)
    latest_replay_attempt = find_latest_attempt_name(replay_root)
    attempt_dir = attempts_root / latest_attempt if latest_attempt else None
    replay_dir = replay_root / latest_replay_attempt if latest_replay_attempt else None
    return {
        "game_key": game_key,
        "latest_attempt": latest_attempt,
        "latest_replay_attempt": latest_replay_attempt,
        "has_attempt_dir": bool(attempt_dir and attempt_dir.exists()),
        "has_replay_dir": bool(replay_dir and replay_dir.exists()),
        "has_replay_index": bool(replay_dir and (replay_dir / "index.html").exists()),
        "has_summary": bool(replay_dir and (replay_dir / "mirror_build_summary.json").exists()),
    }


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


def rebuild_progress(run_dir: Path) -> dict:
    completed = subprocess.run(
        [
            "python3",
            "mirror_system.py",
            "rebuild-report",
            "--run-dir",
            str(run_dir),
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"rebuild-report failed\nSTDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}"
        )
    return json.loads(completed.stdout)


def main() -> int:
    parser = argparse.ArgumentParser(description="Rebuild games missing replay summary outputs.")
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--count", type=int, default=100)
    parser.add_argument("--worker-id", default="batch-001")
    parser.add_argument("--timeout-seconds", type=int, default=30)
    parser.add_argument(
        "--inventory-only",
        action="store_true",
        help="Only print the missing-summary inventory without rebuilding.",
    )
    args = parser.parse_args()

    run_dir = Path(args.run_dir)
    missing_keys = find_missing_summary_game_keys(run_dir)
    selected_keys = missing_keys[args.offset : args.offset + args.count]

    inventory = [classify_game_state(run_dir, game_key) for game_key in selected_keys]

    if args.inventory_only:
        print(
            json.dumps(
                {
                    "run_dir": str(run_dir),
                    "missing_summary_total": len(missing_keys),
                    "offset": args.offset,
                    "count": args.count,
                    "selected_count": len(selected_keys),
                    "selected_keys": selected_keys,
                    "inventory": inventory,
                },
                indent=2,
            )
        )
        return 0

    results = []
    failures = []

    for game_key in selected_keys:
        try:
            results.append(run_build(run_dir, game_key, args.worker_id, args.timeout_seconds))
        except Exception as exc:
            failures.append({"game_key": game_key, "error": str(exc)})

    progress = rebuild_progress(run_dir)
    remaining_missing = find_missing_summary_game_keys(run_dir)

    print(
        json.dumps(
            {
                "run_dir": str(run_dir),
                "missing_summary_total_before": len(missing_keys),
                "offset": args.offset,
                "count": args.count,
                "selected_count": len(selected_keys),
                "selected_keys": selected_keys,
                "inventory": inventory,
                "rebuilt_count": len(results),
                "failure_count": len(failures),
                "results": results,
                "failures": failures,
                "remaining_missing_summary_count": len(remaining_missing),
                "remaining_missing_sample": remaining_missing[:20],
                "progress": progress,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())