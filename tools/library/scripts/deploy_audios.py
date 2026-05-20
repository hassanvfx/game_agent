#!/usr/bin/env python3
"""Deploy canonical and compatibility audio views into the sibling game_agent_library tree."""

from __future__ import annotations

import argparse
import filecmp
import json
import shutil
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SOURCE_ROOT = ROOT / "tools" / "library" / "assets" / "audios"
DEFAULT_TARGET_ROOT = (ROOT.parent / "game_agent_library" / "assets" / "audios").resolve()
DEFAULT_MANIFEST_PATH = SOURCE_ROOT / "deploy_audio_mappings.json"
CANONICAL_DIR_NAMES = ("ambience", "bgm", "music", "sfx", "ui")


@dataclass
class CopyStats:
    copied: int = 0
    unchanged: int = 0
    missing_sources: int = 0


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_files(source_root: Path) -> list[Path]:
    files: list[Path] = []
    for directory_name in CANONICAL_DIR_NAMES:
        directory = source_root / directory_name
        if not directory.is_dir():
            continue
        files.extend(sorted(directory.rglob("*.mp3")))
    return files


def copy_if_needed(source: Path, target: Path, dry_run: bool) -> str:
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and filecmp.cmp(source, target, shallow=False):
        return "unchanged"
    if not dry_run:
        shutil.copy2(source, target)
    return "copied"


def deploy_canonical_files(source_root: Path, target_root: Path, dry_run: bool) -> CopyStats:
    stats = CopyStats()
    for source in canonical_files(source_root):
        relative = source.relative_to(source_root)
        outcome = copy_if_needed(source, target_root / relative, dry_run)
        if outcome == "copied":
            stats.copied += 1
        else:
            stats.unchanged += 1
    return stats


def deploy_aliases(
    alias_rows: list[dict],
    *,
    source_root: Path,
    target_root: Path,
    dry_run: bool,
) -> CopyStats:
    stats = CopyStats()
    for row in alias_rows:
        source_location = row.get("source_location")
        requested_path = row.get("requested_path")
        if not isinstance(source_location, str) or not isinstance(requested_path, str):
            stats.missing_sources += 1
            continue
        source = source_root / source_location
        if not source.is_file():
            stats.missing_sources += 1
            continue
        outcome = copy_if_needed(source, target_root / requested_path, dry_run)
        if outcome == "copied":
            stats.copied += 1
        else:
            stats.unchanged += 1
    return stats


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Deploy canonical library audio files and compatibility aliases into the sibling game_agent_library tree."
    )
    parser.add_argument(
        "--target-root",
        default=str(DEFAULT_TARGET_ROOT),
        help="Deploy root. Defaults to ../game_agent_library/assets/audios.",
    )
    parser.add_argument(
        "--manifest",
        default=str(DEFAULT_MANIFEST_PATH),
        help="Path to deploy_audio_mappings.json.",
    )
    parser.add_argument(
        "--stage",
        choices=("reduced", "enriched", "all"),
        default="all",
        help="Deployment stage: reduced = canonical + reduced aliases, enriched = enriched aliases only, all = canonical + reduced + enriched.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Preview file operations without copying.")
    parser.add_argument(
        "--report-path",
        help="Optional JSON report path. Defaults to <target-root>/deploy_audio_report.json.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    target_root = Path(args.target_root).resolve()
    manifest_path = Path(args.manifest).resolve()
    report_path = Path(args.report_path).resolve() if args.report_path else target_root / "deploy_audio_report.json"

    manifest = load_json(manifest_path)
    reduced_aliases = list(manifest.get("reduced_aliases", []))
    enriched_aliases = list(manifest.get("enriched_aliases", []))

    canonical_stats = CopyStats()
    reduced_stats = CopyStats()
    enriched_stats = CopyStats()

    if args.stage in {"reduced", "all"}:
        canonical_stats = deploy_canonical_files(SOURCE_ROOT, target_root, args.dry_run)
        reduced_stats = deploy_aliases(
            reduced_aliases,
            source_root=SOURCE_ROOT,
            target_root=target_root,
            dry_run=args.dry_run,
        )

    if args.stage in {"enriched", "all"}:
        enriched_stats = deploy_aliases(
            enriched_aliases,
            source_root=SOURCE_ROOT,
            target_root=target_root,
            dry_run=args.dry_run,
        )

    payload = {
        "source_root": str(SOURCE_ROOT),
        "target_root": str(target_root),
        "manifest_path": str(manifest_path),
        "stage": args.stage,
        "dry_run": bool(args.dry_run),
        "canonical": canonical_stats.__dict__,
        "reduced_aliases": reduced_stats.__dict__,
        "enriched_aliases": enriched_stats.__dict__,
        "sanitize_to_empty_prefixes": manifest.get("sanitize_to_empty_prefixes", []),
    }

    if not args.dry_run:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(payload, ensure_ascii=False, indent=2))
    if not args.dry_run:
        print(f"wrote {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
