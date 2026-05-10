#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

DEFAULT_RESTART_DELAY_SECONDS = 10.0
DEFAULT_MAX_RESTARTS = 1000
DEFAULT_LEDGER_PATH = "tmp/game_refactoring_cli_queue_ledger.json"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Top-level supervisor that keeps the sequential direct-CLI game_refactoring queue runner alive until all jobs finish."
    )
    parser.add_argument("config", help="Path to the same JSON config consumed by run_game_refactoring_queue.py")
    parser.add_argument(
        "--ledger-path",
        default=DEFAULT_LEDGER_PATH,
        help="Shared ledger path used by the queue runner",
    )
    parser.add_argument(
        "--workflow-script",
        default="tools/game_refactoring/scripts/game_workflow.py",
        help="Path to the direct CLI workflow launcher script",
    )
    parser.add_argument("--poll-seconds", type=float, default=60.0)
    parser.add_argument("--timeout-seconds", type=int, default=24 * 3600)
    parser.add_argument("--max-concurrency", type=int, default=2)
    parser.add_argument(
        "--max-attempts-per-job",
        type=int,
        default=3,
        help="Maximum total attempts per queue job, including the first run. Default 3 means 1 initial run plus 2 retries.",
    )
    parser.add_argument("--restart-delay-seconds", type=float, default=DEFAULT_RESTART_DELAY_SECONDS)
    parser.add_argument("--max-restarts", type=int, default=DEFAULT_MAX_RESTARTS)
    parser.add_argument("--dry-run", action="store_true")
    return parser


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def queue_is_finished(ledger: dict[str, Any]) -> bool:
    jobs = ledger.get("jobs", [])
    if not jobs:
        return False
    return all(job.get("status") == "completed" for job in jobs)


def queue_has_terminal_failure(ledger: dict[str, Any]) -> bool:
    for job in ledger.get("jobs", []):
        if job.get("status") == "failed":
            return True
    return False


def build_queue_command(args: argparse.Namespace) -> list[str]:
    return [
        "python3",
        "scripts/run_game_refactoring_queue.py",
        args.config,
        "--ledger-path",
        args.ledger_path,
        "--workflow-script",
        args.workflow_script,
        "--poll-seconds",
        str(args.poll_seconds),
        "--timeout-seconds",
        str(args.timeout_seconds),
        "--max-concurrency",
        str(args.max_concurrency),
        "--resume-running",
        "--max-attempts-per-job",
        str(args.max_attempts_per_job),
    ] + (["--dry-run"] if args.dry_run else [])


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    ledger_path = Path(args.ledger_path)

    if args.dry_run:
        payload = {
            "mode": "supervisor_dry_run",
            "queue_command": build_queue_command(args),
            "ledger_path": str(ledger_path),
            "restart_delay_seconds": args.restart_delay_seconds,
            "max_restarts": args.max_restarts,
        }
        print(json.dumps(payload, indent=2))
        return 0

    restart_count = 0
    while True:
        ledger = load_json(ledger_path, {})
        if queue_is_finished(ledger):
            print(json.dumps({"status": "completed", "restarts": restart_count}, indent=2))
            return 0
        if queue_has_terminal_failure(ledger):
            print(json.dumps({"status": "failed", "restarts": restart_count, "ledger": ledger}, indent=2))
            return 1
        if restart_count >= args.max_restarts:
            print(json.dumps({"status": "max_restarts_exceeded", "restarts": restart_count}, indent=2))
            return 2

        command = build_queue_command(args)
        completed = subprocess.run(command, text=True)
        restart_count += 1

        ledger = load_json(ledger_path, {})
        if queue_is_finished(ledger):
            print(json.dumps({"status": "completed", "restarts": restart_count}, indent=2))
            return 0
        if queue_has_terminal_failure(ledger):
            print(json.dumps({"status": "failed", "restarts": restart_count, "ledger": ledger}, indent=2))
            return 1

        if completed.returncode == 0:
            time.sleep(args.restart_delay_seconds)
            continue

        time.sleep(args.restart_delay_seconds)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))