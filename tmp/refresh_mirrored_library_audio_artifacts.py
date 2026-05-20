#!/usr/bin/env python3
"""Refresh generated library audio artifacts under the mirrored root."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def run_step(args: list[str]) -> None:
    completed = subprocess.run(args, cwd=ROOT, check=True)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def main() -> int:
    python = sys.executable
    run_step([python, "tools/library/scripts/build_audio_catalog.py"])
    run_step([python, "tools/library/scripts/build_audio_jobs_list.py"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())