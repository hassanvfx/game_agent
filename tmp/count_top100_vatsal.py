#!/usr/bin/env python3
from pathlib import Path

root = Path("games/top100_vatsal")
dirs = sorted(path.name for path in root.iterdir() if path.is_dir())

print(len(dirs))
if dirs:
    print(dirs[0])
    print(dirs[-1])