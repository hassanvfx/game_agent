#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BATCH_CLI = ROOT / "scripts" / "batch_execute_run.py"
RUNS_ROOT = ROOT / "runs"

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a downloader batch against an existing run.")
    parser.add_argument("--run-id", required=True, help="Run id under runs/.")
    parser.add_argument("--count", type=int, default=25, help="How many games to process.")
    parser.add_argument("--worker-id", default="worker-001", help="Worker id recorded in history.")
    parser.add_argument("--timeout-seconds", type=int, default=30, help="Timeout for local mirror build.")
    parser.add_argument("--resume-leased", action="store_true", help="Resume already leased items.")
    return parser

def main() -> int:
    args = build_parser().parse_args()
    run_dir = RUNS_ROOT / args.run_id
    command = [
        sys.executable,
        str(BATCH_CLI),
        "--run-dir",
        str(run_dir),
        "--count",
        str(args.count),
        "--worker-id",
        args.worker_id,
        "--timeout-seconds",
        str(args.timeout_seconds),
    ]
    if args.resume_leased:
        command.append("--resume-leased")
    completed = subprocess.run(command)
    return completed.returncode

if __name__ == "__main__":
    raise SystemExit(main())
