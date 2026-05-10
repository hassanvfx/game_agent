#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path("/Users/hassan/repos/game_agent")
PYTHON = sys.executable

PUBLISHED_ROOT = ROOT / "games/published/public"
OBFUSCATOR_MANIFEST = ROOT / "tmp/retry_manifests/latest_selected_remix_obfuscator_manifest.json"
CATALOG_MANIFEST = ROOT / "tmp/retry_manifests/latest_selected_remix_catalog_manifest.json"
RERUN_SCRIPT = ROOT / "tmp/rerun_shipped_50_publish.py"
GENERATOR_SCRIPT = ROOT / "scripts/generate_published_app_metadata.py"
QA_SCRIPT = ROOT / "tmp/check_generated_metadata_quality.py"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def metadata_timestamp(remix_dir: Path) -> tuple[str, float, str]:
    metadata_files = sorted(remix_dir.glob("game-obfuscated-*.json"))
    if not metadata_files:
        return ("", 0.0, remix_dir.name)
    metadata = load_json(metadata_files[0])
    aggregated_at = str(metadata.get("aggregated_at") or "")
    return (aggregated_at, metadata_files[0].stat().st_mtime, remix_dir.name)


def build_catalog_manifest(source_manifest_path: Path, output_manifest_path: Path) -> Path:
    payload = load_json(source_manifest_path)
    games = payload.get("games") if isinstance(payload, dict) else payload
    if not isinstance(games, list):
        raise ValueError("Obfuscator manifest must contain a top-level 'games' list or be a list itself")

    entries = []
    for item in games:
        if not isinstance(item, dict):
            continue
        source_path = Path(str(item.get("source_path") or ""))
        inferred_game_id = source_path.parts[-2] if len(source_path.parts) >= 2 else ""
        game_id = str(item.get("game_id") or inferred_game_id).strip()
        if not game_id.startswith("gamezone-"):
            raise ValueError(f"Invalid game_id in manifest item: {item}")

        game_dir = PUBLISHED_ROOT / game_id
        remix_dirs = sorted(path for path in game_dir.iterdir() if path.is_dir() and path.name.startswith("remix-"))
        if not remix_dirs:
            raise ValueError(f"No published remix directories found for {game_id}")

        best_remix_dir = max(remix_dirs, key=metadata_timestamp)
        entries.append(
            {
                "game_id": game_id,
                "remix_id": best_remix_dir.name,
                "published_path": f"{game_id}/{best_remix_dir.name}",
            }
        )

    write_json(
        output_manifest_path,
        {
            "batch_name": "shipped_50_deploy_qa",
            "generated_from": str(source_manifest_path),
            "entry_count": len(entries),
            "entries": entries,
        },
    )
    return output_manifest_path


def run_step(name: str, command: list[str]) -> None:
    print(f"\n=== {name} ===")
    print(json.dumps({"command": command}, indent=2))
    completed = subprocess.run(command, capture_output=True, text=True)
    if completed.stdout:
        print(completed.stdout.rstrip())
    if completed.stderr:
        print(completed.stderr.rstrip())
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def main() -> None:
    catalog_manifest = build_catalog_manifest(OBFUSCATOR_MANIFEST, CATALOG_MANIFEST)
    print(
        json.dumps(
            {
                "published_root": str(PUBLISHED_ROOT),
                "obfuscator_manifest": str(OBFUSCATOR_MANIFEST),
                "catalog_manifest": str(catalog_manifest),
            },
            indent=2,
        )
    )

    run_step(
        "republish shipped 50",
        [PYTHON, str(RERUN_SCRIPT)],
    )
    run_step(
        "regenerate shipped 50 catalogs",
        [
            PYTHON,
            str(GENERATOR_SCRIPT),
            "--manifest",
            str(catalog_manifest),
            "--published-root",
            str(PUBLISHED_ROOT),
            "--strict",
        ],
    )
    run_step(
        "qa shipped 50 catalogs",
        [
            PYTHON,
            str(QA_SCRIPT),
            "--manifest",
            str(catalog_manifest),
            "--strict",
        ],
    )


if __name__ == "__main__":
    main()