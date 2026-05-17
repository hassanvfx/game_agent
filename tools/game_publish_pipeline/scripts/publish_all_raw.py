#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
import tempfile
import time
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve()
TOOL_ROOT = SCRIPT_PATH.parents[1]
REPO_ROOT = TOOL_ROOT.parents[1]

DEFAULT_RAW_ROOT = REPO_ROOT / "games" / "raw"
DEFAULT_PUBLIC_ROOT = REPO_ROOT / "games" / "published" / "public"
DEFAULT_OBFUSCATED_ROOT = REPO_ROOT / "games" / "published" / "obfuscated"
DEFAULT_RUNS_ROOT = REPO_ROOT / "games" / "published" / "runs"
DEFAULT_REPORT_DIR = REPO_ROOT / "tmp" / "publish_all_raw_reports"

PUBLISH_SCRIPT = TOOL_ROOT / "scripts" / "publish_games.py"
SYNC_TO_GCS_SCRIPT = TOOL_ROOT / "scripts" / "sync_to_gcs.py"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Publish raw game folders that are not already present in published/public, "
            "then run the existing GCS sync step."
        )
    )
    parser.add_argument(
        "--raw-root",
        default=str(DEFAULT_RAW_ROOT),
        help="Root directory containing raw game folders. Defaults to games/raw.",
    )
    parser.add_argument(
        "--published-public-root",
        default=str(DEFAULT_PUBLIC_ROOT),
        help="Published public output root used for delta detection. Defaults to games/published/public.",
    )
    parser.add_argument(
        "--published-obfuscated-root",
        default=str(DEFAULT_OBFUSCATED_ROOT),
        help="Published obfuscated output root forwarded to the publish pipeline.",
    )
    parser.add_argument(
        "--published-runs-root",
        default=str(DEFAULT_RUNS_ROOT),
        help="Published runs root forwarded to the publish pipeline.",
    )
    parser.add_argument(
        "--report-path",
        help="Optional explicit report path for the underlying publish pipeline run.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Optional maximum number of selected delta games to publish.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Forward --overwrite to publish_games.py.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the computed delta manifest and planned commands without executing them.",
    )
    parser.add_argument(
        "--include-existing-public",
        action="store_true",
        help="Disable delta filtering and publish every raw game discovered, even if its game ID already exists in published/public.",
    )
    parser.add_argument(
        "--sync-gcs-project",
        default="jabali-prod",
        help="Google Cloud project forwarded to the final GCS sync step.",
    )
    parser.add_argument(
        "--sync-gcs-dry-run",
        action="store_true",
        help="Forward dry-run behavior to the final GCS sync step.",
    )
    return parser


def discover_game_dirs(root: Path) -> list[Path]:
    if not root.exists():
        raise FileNotFoundError(f"Game root does not exist: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"Game root is not a directory: {root}")

    return [
        path.resolve()
        for path in sorted(root.iterdir())
        if path.is_dir() and path.name.startswith("gamezone-")
    ]


def discover_game_ids(root: Path) -> set[str]:
    if not root.exists():
        return set()
    if not root.is_dir():
        raise NotADirectoryError(f"Game root is not a directory: {root}")

    return {
        path.name
        for path in root.iterdir()
        if path.is_dir() and path.name.startswith("gamezone-")
    }


def select_publish_dirs(
    raw_game_dirs: list[Path],
    existing_public_ids: set[str],
    *,
    include_existing_public: bool,
) -> tuple[list[Path], list[Path]]:
    if include_existing_public:
        return list(raw_game_dirs), []

    selected_dirs: list[Path] = []
    skipped_dirs: list[Path] = []
    for path in raw_game_dirs:
        if path.name in existing_public_ids:
            skipped_dirs.append(path)
        else:
            selected_dirs.append(path)
    return selected_dirs, skipped_dirs


def write_manifest(game_dirs: list[Path]) -> Path:
    payload = [str(path) for path in game_dirs]
    handle = tempfile.NamedTemporaryFile(prefix="publish-all-raw-", suffix=".json", delete=False)
    manifest_path = Path(handle.name)
    handle.close()
    manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return manifest_path


def build_report_path(args: argparse.Namespace) -> Path:
    if args.report_path:
        return Path(args.report_path).resolve()

    timestamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    return (DEFAULT_REPORT_DIR / f"publish_all_raw_report_{timestamp}.json").resolve()


def build_publish_command(
    *,
    manifest_path: Path,
    report_path: Path,
    public_root: Path,
    obfuscated_root: Path,
    runs_root: Path,
    args: argparse.Namespace,
) -> list[str]:
    command = [
        sys.executable,
        str(PUBLISH_SCRIPT),
        "--manifest",
        str(manifest_path),
        "--published-public-root",
        str(public_root),
        "--published-obfuscated-root",
        str(obfuscated_root),
        "--published-runs-root",
        str(runs_root),
        "--report-path",
        str(report_path),
        "--gcg-sync",
        "--gcg-sync-project",
        str(args.sync_gcs_project),
    ]

    if args.overwrite:
        command.append("--overwrite")
    if args.dry_run:
        command.append("--dry-run")
    if args.sync_gcs_dry_run:
        command.append("--gcg-sync-dry-run")
    return command


def build_sync_command(*, public_root: Path, obfuscated_root: Path, args: argparse.Namespace) -> list[str]:
    command = [
        sys.executable,
        str(SYNC_TO_GCS_SCRIPT),
        "--target",
        "both",
        "--mode",
        "per-item",
        "--project",
        str(args.sync_gcs_project),
        "--public-root",
        str(public_root),
        "--obfuscated-root",
        str(obfuscated_root),
    ]
    if args.dry_run or args.sync_gcs_dry_run:
        command.append("--dry-run")
    return command


def print_examples(label: str, paths: list[Path], *, limit: int = 10) -> None:
    if not paths:
        return

    print(label)
    for path in paths[:limit]:
        print(f"  - {path.name}")
    remaining = len(paths) - limit
    if remaining > 0:
        print(f"  ... {remaining} more")


def main() -> int:
    args = build_parser().parse_args()

    raw_root = Path(args.raw_root).resolve()
    public_root = Path(args.published_public_root).resolve()
    obfuscated_root = Path(args.published_obfuscated_root).resolve()
    runs_root = Path(args.published_runs_root).resolve()

    raw_game_dirs = discover_game_dirs(raw_root)
    if not raw_game_dirs:
        print(f"No raw game directories found under {raw_root}", file=sys.stderr)
        return 1

    existing_public_ids = discover_game_ids(public_root)
    selected_dirs, skipped_dirs = select_publish_dirs(
        raw_game_dirs,
        existing_public_ids,
        include_existing_public=bool(args.include_existing_public),
    )

    total_selected_before_limit = len(selected_dirs)
    if args.limit is not None:
        selected_dirs = selected_dirs[: args.limit]

    print("== Publish All Raw ==")
    print(f"Raw root: {raw_root}")
    print(f"Published public root: {public_root}")
    print(f"Published obfuscated root: {obfuscated_root}")
    print(f"Published runs root: {runs_root}")
    print(f"Raw games discovered: {len(raw_game_dirs)}")
    print(f"Existing public game IDs: {len(existing_public_ids)}")

    if args.include_existing_public:
        print("Delta filter: disabled (--include-existing-public)")
    else:
        print(f"Skipped because already present in public: {len(skipped_dirs)}")

    print(f"Selected for publish before limit: {total_selected_before_limit}")
    if args.limit is not None:
        print(f"Selected for publish after limit: {len(selected_dirs)}")

    print_examples("Sample selected game IDs:", selected_dirs)
    if skipped_dirs and not args.include_existing_public:
        print_examples("Sample skipped game IDs already in public:", skipped_dirs)

    if not selected_dirs:
        sync_command = build_sync_command(public_root=public_root, obfuscated_root=obfuscated_root, args=args)
        print("No games selected for publish after delta filtering and limit application.")
        print("Sync command:")
        print(f"  {shlex.join(sync_command)}")

        if args.dry_run:
            print("Dry run only. Nothing will be executed.")
            return 0

        print("Running sync directly because there is no publish delta.")
        result = subprocess.run(sync_command, text=True)
        return result.returncode

    manifest_path = write_manifest(selected_dirs)
    report_path = build_report_path(args)
    publish_command = build_publish_command(
        manifest_path=manifest_path,
        report_path=report_path,
        public_root=public_root,
        obfuscated_root=obfuscated_root,
        runs_root=runs_root,
        args=args,
    )

    print(f"Generated delta manifest: {manifest_path}")
    print(f"Pipeline report target: {report_path}")
    print("Publish command:")
    print(f"  {shlex.join(publish_command)}")

    if args.dry_run:
        print("Dry run only. Nothing will be executed.")
        return 0

    result = subprocess.run(publish_command, text=True)
    if result.returncode != 0:
        print(f"\nPublish-all-raw failed with exit code {result.returncode}", file=sys.stderr)
        print(f"Manifest: {manifest_path}", file=sys.stderr)
        print(f"Report target: {report_path}", file=sys.stderr)
        return result.returncode

    print("\n== Publish-all-raw complete ==")
    print(f"Manifest: {manifest_path}")
    print(f"Final report: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())