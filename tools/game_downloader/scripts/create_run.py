#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORE_CLI = ROOT / "game_downloader" / "core" / "mirror_system.py"
RUNS_ROOT = ROOT / "runs"

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create a downloader run from a manifest.")
    parser.add_argument("--input", required=True, help="Path to the input manifest JSON.")
    parser.add_argument("--run-id", help="Optional explicit run id.")
    parser.add_argument("--force", action="store_true", help="Allow overwriting an existing run id.")
    return parser

def main() -> int:
    args = build_parser().parse_args()
    command = [
        sys.executable,
        str(CORE_CLI),
        "create-run",
        "--input",
        args.input,
        "--runs-root",
        str(RUNS_ROOT),
    ]
    if args.run_id:
        command.extend(["--run-id", args.run_id])
    if args.force:
        command.append("--force")
    completed = subprocess.run(command)
    return completed.returncode

if __name__ == "__main__":
    raise SystemExit(main())
