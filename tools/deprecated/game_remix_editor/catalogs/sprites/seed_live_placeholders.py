#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DEFAULT_RUN_ID = "premium-sample"
DEFAULT_PLACEHOLDER = ROOT / "runs" / DEFAULT_RUN_ID / "assets/images/sprites/runner/player_runner.png"
LIVE_DIR = ROOT / "live"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Seed the live sprite taxonomy with a placeholder image for all manifest entries."
    )
    parser.add_argument("--run-id", default=DEFAULT_RUN_ID)
    parser.add_argument("--placeholder", default=str(DEFAULT_PLACEHOLDER))
    parser.add_argument("--force", action="store_true", help="Overwrite existing live files.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_dir = ROOT / "runs" / args.run_id
    manifest = json.loads((run_dir / "manifest.json").read_text())
    placeholder = Path(args.placeholder).resolve()

    if not placeholder.exists():
        raise FileNotFoundError(f"Placeholder image not found: {placeholder}")

    copied = 0
    skipped = 0

    for item in manifest:
        live_path = LIVE_DIR / item["output_relpath"]
        live_path.parent.mkdir(parents=True, exist_ok=True)

        if live_path.exists() and not args.force:
            skipped += 1
            continue

        shutil.copy2(placeholder, live_path)
        copied += 1

    print(
        json.dumps(
            {
                "ok": True,
                "run_id": args.run_id,
                "placeholder": str(placeholder),
                "live_dir": str(LIVE_DIR),
                "copied": copied,
                "skipped": skipped,
                "total": len(manifest),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()