#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parents[1]

for path in (ROOT, REPO_ROOT):
    path_value = str(path)
    if path_value not in sys.path:
        sys.path.insert(0, path_value)

from game_actor_mock.mock_actor import main


if __name__ == "__main__":
    raise SystemExit(main())