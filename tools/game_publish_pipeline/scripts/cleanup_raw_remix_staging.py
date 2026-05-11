#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any

SCRIPT_PATH = Path(__file__).resolve()
TOOL_ROOT = SCRIPT_PATH.parents[1]
REPO_ROOT = TOOL_ROOT.parents[1]
DEFAULT_RAW_ROOT = REPO_ROOT / "games" / "raw"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Remove all staged games/raw/*/remix-* folders created by publish pipeline runs."
    )
    parser.add_argument(
        "--raw-root",
        default=str(DEFAULT_RAW_ROOT),
        help="Raw games root containing top-level gamezone folders.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually delete the discovered remix staging folders. Without this flag, runs in dry-run mode.",
    )
    return parser


def iter_remix_dirs(raw_root: Path) -> list[Path]:
    remix_dirs: list[Path] = []
    if not raw_root.exists():
        return remix_dirs
    for game_dir in sorted(raw_root.iterdir()):
        if not game_dir.is_dir():
            continue
        if not game_dir.name.startswith("gamezone-"):
            continue
        for child in sorted(game_dir.iterdir()):
            if child.is_dir() and child.name.startswith("remix-"):
                remix_dirs.append(child)
    return remix_dirs


def folder_size_bytes(root: Path) -> int:
    total = 0
    for path in root.rglob("*"):
        if path.is_file():
            total += path.stat().st_size
    return total


def main() -> None:
    args = build_parser().parse_args()
    raw_root = Path(args.raw_root).resolve()
    remix_dirs = iter_remix_dirs(raw_root)

    entries: list[dict[str, Any]] = []
    total_bytes = 0
    for remix_dir in remix_dirs:
        size_bytes = folder_size_bytes(remix_dir)
        total_bytes += size_bytes
        entries.append(
            {
                "game_id": remix_dir.parent.name,
                "remix_dir": str(remix_dir),
                "size_bytes": size_bytes,
            }
        )

    if args.apply:
        for remix_dir in remix_dirs:
            shutil.rmtree(remix_dir)
        action = "deleted"
    else:
        action = "would_delete"

    print(
        json.dumps(
            {
                "raw_root": str(raw_root),
                "apply": bool(args.apply),
                "action": action,
                "remix_dir_count": len(remix_dirs),
                "total_size_bytes": total_bytes,
                "entries": entries,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()