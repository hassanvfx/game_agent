#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from game_deploy.deployer import build_parser, run_deploy


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return run_deploy(args)


if __name__ == "__main__":
    raise SystemExit(main())