#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import time
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PUBLIC_ROOT = REPO_ROOT / "games" / "published" / "public"
OBFUSCATED_ROOT = REPO_ROOT / "games" / "published" / "obfuscated"
SYNC_SCRIPT = REPO_ROOT / "tools" / "game_publish_pipeline" / "scripts" / "sync_to_gcs.py"


def parse_composite_key(value: str) -> tuple[str, str]:
    parts = value.split("__", 1)
    if len(parts) != 2:
        raise ValueError(f"Invalid composite key (expected gamezone-...__remix-...): {value}")
    game_id, remix_id = parts
    if not game_id.startswith("gamezone-"):
        raise ValueError(f"Invalid game_id in composite key: {value}")
    if not remix_id.startswith("remix-"):
        raise ValueError(f"Invalid remix_id in composite key: {value}")
    return game_id, remix_id


def remix_path(root: Path, composite_key: str) -> Path:
    game_id, remix_id = parse_composite_key(composite_key)
    return root / game_id / remix_id


def ensure_dir(path: Path, label: str) -> None:
    if not path.is_dir():
        raise SystemExit(f"[fail] Missing required directory for {label}: {path}")


def print_check(label: str, path: Path) -> None:
    status = "OK" if path.is_dir() else "MISSING"
    print(f"[check] {label}: {status} :: {path}")


def copy_directory_contents(src: Path, dst: Path) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    for child in dst.iterdir():
        if child.is_dir() and not child.is_symlink():
            shutil.rmtree(child)
        else:
            child.unlink()
    for child in src.iterdir():
        target = dst / child.name
        if child.is_dir():
            shutil.copytree(child, target, symlinks=True)
        else:
            shutil.copy2(child, target, follow_symlinks=False)


def backup_target(src: Path, backup_root: Path, bucket: str) -> Path:
    destination = backup_root / bucket / src.parent.name / src.name
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, destination, symlinks=True)
    return destination


def run_command(command: list[str], dry_run: bool) -> int:
    print(f"[cmd] {' '.join(command)}")
    if dry_run:
        return 0
    completed = subprocess.run(command)
    return completed.returncode


def build_sync_command(target_game_id: str, project: str, dry_run: bool) -> list[str]:
    command = [
        sys.executable,
        str(SYNC_SCRIPT),
        "--target",
        "both",
        "--mode",
        "per-item",
        "--only-item",
        target_game_id,
        "--project",
        project,
    ]
    if dry_run:
        command.append("--dry-run")
    return command


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Safely copy one published remix folder into another in both public/obfuscated, "
            "with validation, temp backups, and optional selective GCS sync."
        )
    )
    parser.add_argument("--source", required=True, help="Source composite key: gamezone-...__remix-...")
    parser.add_argument("--target", required=True, help="Target composite key: gamezone-...__remix-...")
    parser.add_argument("--dry-run", action="store_true", help="Print planned actions without changing files.")
    parser.add_argument(
        "--sync-gcs",
        action="store_true",
        help="After local swap, invoke selective sync_to_gcs.py for the target gamezone id.",
    )
    parser.add_argument(
        "--sync-dry-run",
        action="store_true",
        help="Pass --dry-run to sync_to_gcs.py. Useful with or without local --dry-run.",
    )
    parser.add_argument(
        "--project",
        default="jabali-prod",
        help="GCloud project forwarded to sync_to_gcs.py --project.",
    )
    args = parser.parse_args()

    source_game_id, source_remix_id = parse_composite_key(args.source)
    target_game_id, target_remix_id = parse_composite_key(args.target)

    public_source = PUBLIC_ROOT / source_game_id / source_remix_id
    public_target = PUBLIC_ROOT / target_game_id / target_remix_id
    obfuscated_source = OBFUSCATED_ROOT / source_game_id / source_remix_id
    obfuscated_target = OBFUSCATED_ROOT / target_game_id / target_remix_id

    print("[plan] validating required directories")
    print_check("public source", public_source)
    print_check("public target", public_target)
    print_check("obfuscated source", obfuscated_source)
    print_check("obfuscated target", obfuscated_target)

    ensure_dir(public_source, "public source")
    ensure_dir(public_target, "public target")
    ensure_dir(obfuscated_source, "obfuscated source")
    ensure_dir(obfuscated_target, "obfuscated target")

    timestamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    backup_root = REPO_ROOT / "tmp" / f"swap_backup_{target_game_id}_{target_remix_id}_{timestamp}"

    print("[plan] source -> target copy")
    print(f"        public:      {public_source} -> {public_target}")
    print(f"        obfuscated:  {obfuscated_source} -> {obfuscated_target}")
    print(f"[plan] backup root: {backup_root}")

    if args.dry_run:
        print("[dry-run] no files changed")
    else:
        public_backup = backup_target(public_target, backup_root, "public")
        obfuscated_backup = backup_target(obfuscated_target, backup_root, "obfuscated")
        print(f"[backup] public target backed up to: {public_backup}")
        print(f"[backup] obfuscated target backed up to: {obfuscated_backup}")

        copy_directory_contents(public_source, public_target)
        print(f"[copy] public target replaced from source: {public_target}")

        copy_directory_contents(obfuscated_source, obfuscated_target)
        print(f"[copy] obfuscated target replaced from source: {obfuscated_target}")

    if args.sync_gcs:
        print("[plan] selective GCS sync requested")
        sync_command = build_sync_command(
            target_game_id=target_game_id,
            project=args.project,
            dry_run=args.sync_dry_run or args.dry_run,
        )
        code = run_command(sync_command, dry_run=False)
        if code != 0:
            return code

    print("[done] helper finished successfully")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())