#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUMMARY_CLI = ROOT / "scripts" / "summarize_batch_run.py"
RUNS_ROOT = ROOT / "runs"

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Summarize a downloader run.")
    parser.add_argument("--run-id", required=True, help="Run id under runs/.")
    return parser

def main() -> int:
    args = build_parser().parse_args()
    run_dir = RUNS_ROOT / args.run_id
    completed = subprocess.run([sys.executable, str(SUMMARY_CLI), "--run-dir", str(run_dir)])
    return completed.returncode

if __name__ == "__main__":
    raise SystemExit(main())
