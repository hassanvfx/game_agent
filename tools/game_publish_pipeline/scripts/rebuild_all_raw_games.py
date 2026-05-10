#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve()
TOOL_ROOT = SCRIPT_PATH.parents[1]
REPO_ROOT = TOOL_ROOT.parents[1]
DEFAULT_RAW_ROOT = REPO_ROOT / "games" / "raw"
DEFAULT_PUBLIC_ROOT = REPO_ROOT / "games" / "published" / "public"
DEFAULT_OBFUSCATED_ROOT = REPO_ROOT / "games" / "published" / "obfuscated"
PUBLISH_SCRIPT = TOOL_ROOT / "scripts" / "publish_games.py"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Rebuild public and obfuscated outputs for all raw games using game_publish_pipeline."
    )
    parser.add_argument(
        "--raw-root",
        default=str(DEFAULT_RAW_ROOT),
        help="Root directory containing raw game folders. Defaults to games/raw.",
    )
    parser.add_argument(
        "--published-public-root",
        default=str(DEFAULT_PUBLIC_ROOT),
        help="Published public output root. Defaults to games/published/public.",
    )
    parser.add_argument(
        "--published-obfuscated-root",
        default=str(DEFAULT_OBFUSCATED_ROOT),
        help="Published obfuscated output root. Defaults to games/published/obfuscated.",
    )
    parser.add_argument(
        "--report-dir",
        default=str(REPO_ROOT / "tmp" / "rebuild_all_raw_games_reports"),
        help="Directory where per-game pipeline reports will be written.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Optional maximum number of raw games to process.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the discovered raw games and planned commands without executing them.",
    )
    return parser


def discover_raw_games(raw_root: Path) -> list[Path]:
    if not raw_root.exists():
        raise FileNotFoundError(f"Raw root does not exist: {raw_root}")

    game_dirs = []
    for path in sorted(raw_root.iterdir()):
        if path.is_dir() and path.name.startswith("gamezone-"):
            game_dirs.append(path.resolve())
    return game_dirs


def write_manifest(game_dirs: list[Path]) -> Path:
    payload = [str(path) for path in game_dirs]
    handle = tempfile.NamedTemporaryFile(prefix="rebuild-all-raw-games-", suffix=".json", delete=False)
    manifest_path = Path(handle.name)
    handle.close()
    manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return manifest_path


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    raw_root = Path(args.raw_root).resolve()
    public_root = Path(args.published_public_root).resolve()
    obfuscated_root = Path(args.published_obfuscated_root).resolve()
    report_dir = Path(args.report_dir).resolve()

    game_dirs = discover_raw_games(raw_root)
    if args.limit is not None:
        game_dirs = game_dirs[: args.limit]

    if not game_dirs:
        print(f"No raw game directories found under {raw_root}", file=sys.stderr)
        return 1

    print("== Rebuild All Raw Games ==")
    print(f"Raw root: {raw_root}")
    print(f"Published public root: {public_root}")
    print(f"Published obfuscated root: {obfuscated_root}")
    print(f"Games discovered: {len(game_dirs)}")
    for index, game_dir in enumerate(game_dirs, start=1):
        print(f"  [{index:03d}/{len(game_dirs):03d}] {game_dir}")

    manifest_path = write_manifest(game_dirs)
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "rebuild_all_raw_games_report.json"

    command = [
        sys.executable,
        str(PUBLISH_SCRIPT),
        "--manifest",
        str(manifest_path),
        "--published-public-root",
        str(public_root),
        "--published-obfuscated-root",
        str(obfuscated_root),
        "--report-path",
        str(report_path),
        "--overwrite",
    ]

    if args.dry_run:
        print("\nDry run only. Command:")
        print(" ".join(command))
        print(f"Manifest written to: {manifest_path}")
        print(f"Report would be written to: {report_path}")
        return 0

    print("\n== Running publish pipeline ==")
    print(" ".join(command))
    print("")

    result = subprocess.run(command, text=True)
    if result.returncode != 0:
        print(f"\nRebuild failed with exit code {result.returncode}", file=sys.stderr)
        print(f"Manifest: {manifest_path}", file=sys.stderr)
        print(f"Report target: {report_path}", file=sys.stderr)
        return result.returncode

    print("\n== Rebuild complete ==")
    print(f"Manifest: {manifest_path}")
    print(f"Final report: {report_path}")
    print(f"Published public root: {public_root}")
    print(f"Published obfuscated root: {obfuscated_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())