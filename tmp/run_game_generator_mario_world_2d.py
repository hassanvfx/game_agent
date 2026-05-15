#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys


def main() -> int:
    command = [
        "python3",
        "tools/game_generator/scripts/run_pipeline.py",
        "mario world 2d game",
    ]
    completed = subprocess.run(command)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())