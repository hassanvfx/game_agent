#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path("/Users/hassan/repos/game_agent")
DEFAULT_SOURCE_ROOT = Path("/Volumes/HDD2026/output-May17th/run_game_remixer_20260517T132133Z/output")
DEFAULT_MANIFEST_PATH = ROOT / "tmp/may17_full_publish_manifest.json"
DEFAULT_REPORT_PATH = ROOT / "tmp/may17_full_publish_manifest_report.json"


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def list_source_dirs(source_root: Path) -> list[Path]:
    if not source_root.exists():
        raise FileNotFoundError(f"Source root does not exist: {source_root}")
    return sorted(
        path
        for path in source_root.iterdir()
        if path.is_dir() and not path.name.startswith(".") and path.name.startswith("gamezone-")
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a full publish manifest from the May 17 HDD run folders.")
    parser.add_argument("--source-root", default=str(DEFAULT_SOURCE_ROOT))
    parser.add_argument("--manifest-path", default=str(DEFAULT_MANIFEST_PATH))
    parser.add_argument("--report-path", default=str(DEFAULT_REPORT_PATH))
    return parser


def main() -> None:
    args = build_parser().parse_args()
    source_root = Path(args.source_root)
    manifest_path = Path(args.manifest_path)
    report_path = Path(args.report_path)

    source_dirs = list_source_dirs(source_root)
    manifest_payload = [str(path) for path in source_dirs]
    write_json(manifest_path, manifest_payload)

    report_payload = {
        "timestamp": utc_timestamp(),
        "source_root": str(source_root),
        "manifest_path": str(manifest_path),
        "source_dir_count": len(source_dirs),
        "source_dir_sample": [str(path) for path in source_dirs[:20]],
    }
    write_json(report_path, report_payload)
    print(json.dumps(report_payload, indent=2))


if __name__ == "__main__":
    main()