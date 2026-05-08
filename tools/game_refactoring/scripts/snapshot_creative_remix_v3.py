#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_ROOT = ROOT / "snapshots" / "creative_remix_v3"


FILES_TO_CAPTURE = [
    "scripts/game_workflow.py",
    "scripts/retry_harry_potter_run.py",
    "prompts/operators_v2/00_creative_remix_v3_remix_inference.md",
    "prompts/operators_v2/03_creative_remix_v1_visuals.md",
    "prompts/operators_v2/05_creative_remix_v3_narrative_refine.md",
    "prompts/operators_v2/06_creative_remix_v3_gameplay_refine.md",
    "prompts/operators_v2/07_creative_remix_v3_visuals_refine.md",
    "prompts/operators_v2/08_creative_remix_v3_optional_config_refactor.md",
    "prompts/operators_v2/09_creative_remix_v3_final_mobile_repair.md",
    "docs/journals/creative-remix-v3-next-steps-plan.md",
    "fixtures/harry_potter_single_game_25b14fff_manifest.json",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Snapshot the current creative_remix_v3 pipeline/prompt set for later restoration."
    )
    parser.add_argument(
        "--comment",
        required=True,
        help="Short comment describing why this snapshot was taken.",
    )
    parser.add_argument(
        "--tag",
        help="Optional short slug to append to the snapshot directory name.",
    )
    return parser.parse_args()


def slugify(value: str) -> str:
    cleaned = "".join(ch.lower() if ch.isalnum() else "-" for ch in value.strip())
    compact = "-".join(part for part in cleaned.split("-") if part)
    return compact[:60] if compact else "snapshot"


def main() -> None:
    args = parse_args()
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    suffix = slugify(args.tag) if args.tag else slugify(args.comment)
    snapshot_dir = SNAPSHOT_ROOT / f"{timestamp}__{suffix}"
    files_dir = snapshot_dir / "files"

    files_dir.mkdir(parents=True, exist_ok=True)

    copied_files: list[str] = []
    missing_files: list[str] = []

    for relative_path in FILES_TO_CAPTURE:
        source = ROOT / relative_path
        destination = files_dir / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)

        if source.exists():
            shutil.copy2(source, destination)
            copied_files.append(relative_path)
        else:
            missing_files.append(relative_path)

    manifest = {
        "snapshot_type": "creative_remix_v3",
        "created_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "comment": args.comment,
        "tag": args.tag or "",
        "snapshot_dir": str(snapshot_dir),
        "captured_files": copied_files,
        "missing_files": missing_files,
    }

    (snapshot_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (snapshot_dir / "README.md").write_text(
        "# Creative Remix V3 Snapshot\n\n"
        f"- Created: {manifest['created_at']}\n"
        f"- Comment: {args.comment}\n"
        f"- Tag: {args.tag or '(none)'}\n\n"
        "## Captured Files\n\n"
        + "".join(f"- `{path}`\n" for path in copied_files)
        + (
            "\n## Missing Files\n\n" + "".join(f"- `{path}`\n" for path in missing_files)
            if missing_files
            else ""
        ),
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "snapshot_dir": str(snapshot_dir),
                "captured_count": len(copied_files),
                "missing_count": len(missing_files),
                "manifest_path": str(snapshot_dir / "manifest.json"),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()