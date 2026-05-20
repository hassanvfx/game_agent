#!/usr/bin/env python3
"""Compatibility wrapper for the library audio artifact reconciler."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECONCILE_SCRIPT = ROOT / "tools" / "library" / "scripts" / "reconcile_audio_artifacts.py"


def run(args: list[str]) -> None:
    subprocess.run(args, cwd=ROOT, check=True)


def main() -> int:
    python = sys.executable
    run(
        [
            python,
            str(RECONCILE_SCRIPT),
        ]
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())