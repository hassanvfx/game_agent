#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run materialize_artifact_view.py across discovered run dirs.")
    parser.add_argument("--dry-run", action="store_true", help="Forward --dry-run to materialize_artifact_view.py")
    parser.add_argument(
        "--limit",
        type=int,
        help="Optional limit to newest N runs (after sorting by run_id). If omitted, include all runs.",
    )
    parser.add_argument(
        "--precedence",
        choices=("latest-wins", "first-wins"),
        default="latest-wins",
        help="Merge precedence forwarded to materialize_artifact_view.py",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()

    tool_root = Path(__file__).resolve().parents[1]
    repo_root = tool_root.parents[1]
    runs_root = repo_root / "games" / "published" / "runs"
    materialize_script = tool_root / "scripts" / "materialize_artifact_view.py"

    run_dirs = sorted(
        [path for path in runs_root.iterdir() if path.is_dir() and path.name.startswith("run_")],
        key=lambda p: p.name,
    )
    if args.limit is not None:
        run_dirs = run_dirs[-args.limit :]

    if not run_dirs:
        print(f"No run directories found under: {runs_root}")
        return 1

    command = [
        sys.executable,
        str(materialize_script),
        "--runs",
        *[str(path) for path in run_dirs],
        "--public-root",
        str(repo_root / "games" / "published" / "public"),
        "--obfuscated-root",
        str(repo_root / "games" / "published" / "obfuscated"),
        "--precedence",
        str(args.precedence),
    ]
    if args.dry_run:
        command.append("--dry-run")

    print("[tmp-materialize] run_count:", len(run_dirs))
    print("[tmp-materialize] first_run:", run_dirs[0].name)
    print("[tmp-materialize] last_run:", run_dirs[-1].name)
    print("[tmp-materialize] command:")
    print(" ".join(command))

    result = subprocess.run(command, text=True)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
