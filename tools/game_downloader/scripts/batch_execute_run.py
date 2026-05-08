#!/usr/bin/env python3

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORE_CLI = ROOT / "game_downloader" / "core" / "mirror_system.py"


def run_json(command: list[str]) -> dict:
    completed = subprocess.run(command, text=True, capture_output=True)
    if completed.returncode != 0:
        stdout = completed.stdout or ""
        stderr = completed.stderr or ""
        if "No queue items available in state 'pending'" in stdout or "No queue items available in state 'pending'" in stderr:
            return {"queue_exhausted": True}
        sys.stderr.write(stdout)
        sys.stderr.write(stderr)
        raise RuntimeError(f"Command failed ({completed.returncode}): {' '.join(command)}")
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Expected JSON output from command: {' '.join(command)}\nSTDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}"
        ) from exc


def ensure_pending(run_dir: Path, game_key: str, worker_id: str) -> dict:
    state = "unknown"
    for queue_state in [
        "pending",
        "leased",
        "capturing",
        "replay_pending",
        "completed",
        "failed_retryable",
        "failed_terminal",
    ]:
        if (run_dir / "queue" / queue_state / f"{game_key}.json").exists():
            state = queue_state
            break

    if state == "pending":
        return {
            "game_key": game_key,
            "previous_state": "pending",
            "target_state": "pending",
            "skipped": True,
        }

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


def run_passthrough(command: list[str]) -> int:
    completed = subprocess.run(command)
    return completed.returncode


def leased_keys(run_dir: Path) -> list[str]:
    return sorted(path.stem for path in (run_dir / "queue" / "leased").glob("*.json"))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Execute a controlled batch for a mirror run without long shell commands."
    )
    parser.add_argument("--run-dir", required=True, help="Path to the mirror run directory.")
    parser.add_argument("--count", type=int, default=25, help="How many items to process.")
    parser.add_argument("--worker-id", default="batch-001", help="Worker ID to record in queue history.")
    parser.add_argument("--timeout-seconds", type=int, default=30, help="Timeout for build-local-mirror.")
    parser.add_argument(
        "--resume-leased",
        action="store_true",
        help="If leased items already exist, move them back to pending and execute those first.",
    )
    args = parser.parse_args()

    run_dir = Path(args.run_dir)
    selected_keys: list[str] = []

    existing_leased = leased_keys(run_dir)
    if existing_leased:
        print(f"[batch] found {len(existing_leased)} already leased item(s)")
        if not args.resume_leased:
            print("[batch] refusing to continue without --resume-leased", file=sys.stderr)
            return 2
        selected_keys = existing_leased[: args.count]
        for game_key in selected_keys:
            print(f"[batch] reset leased -> pending: {game_key}")
            ensure_pending(run_dir, game_key, args.worker_id)

    while len(selected_keys) < args.count:
        lease = run_json(
            [
                "python3",
                str(CORE_CLI),
                "lease-next",
                "--run-dir",
                str(run_dir),
                "--worker-id",
                args.worker_id,
            ]
        )
        if lease.get("queue_exhausted"):
            print("[batch] no more work available")
            break
        game_key = str(lease.get("game_key") or "").strip()
        if not game_key:
            print("[batch] no more work available")
            break
        print(f"[batch] leased {len(selected_keys) + 1}/{args.count}: {game_key}")
        selected_keys.append(game_key)

    if not selected_keys:
        print("[batch] nothing selected")
        return 0

    failures: list[dict[str, object]] = []

    for index, game_key in enumerate(selected_keys, start=1):
        print(f"[batch] build {index}/{len(selected_keys)}: {game_key}")
        transition = ensure_pending(run_dir, game_key, args.worker_id)
        print(
            f"[batch] normalized state for {game_key}: {transition.get('previous_state')} -> {transition.get('target_state')}"
        )
        exit_code = run_passthrough(
            [
                "python3",
                str(CORE_CLI),
                "build-local-mirror",
                "--run-dir",
                str(run_dir),
                "--game-key",
                game_key,
                "--worker-id",
                args.worker_id,
                "--timeout-seconds",
                str(args.timeout_seconds),
            ]
        )
        if exit_code != 0:
            failures.append({"game_key": game_key, "exit_code": exit_code})
            print(f"[batch] build failed: {game_key} exit={exit_code}", file=sys.stderr)

    report = run_json(
        [
            "python3",
            str(CORE_CLI),
            "rebuild-report",
            "--run-dir",
            str(run_dir),
        ]
    )

    summary = {
        "run_dir": str(run_dir),
        "requested_count": args.count,
        "selected_count": len(selected_keys),
        "processed_keys": selected_keys,
        "failure_count": len(failures),
        "failures": failures,
        "progress_report": report,
    }
    print(json.dumps(summary, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
