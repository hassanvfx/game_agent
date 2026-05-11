#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
OBF_ROOT = REPO_ROOT / "tools" / "game_obfuscator"
VENV_PYTHON = OBF_ROOT / ".venv" / "bin" / "python"

MANIFEST = REPO_ROOT / "tmp" / "validate_obfuscator_preserved_folders_manifest.json"
RUN_ID = "run_game_obfuscator_validate_preserved_folders"
RUN_DIR = OBF_ROOT / "runs" / RUN_ID
REPORT_PATH = RUN_DIR / "output" / "gamezone-0a01fa77-8b8b-4c02-93db-07cf4e05ee06" / "artifacts" / "simple_obfuscation_report.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    if RUN_DIR.exists():
        shutil.rmtree(RUN_DIR)

    payload = {

def main() -> None:
    payload = {
        "run_label": "validate_preserved_folders",
        "description": "Single public deploy used to validate preserved surface folders in obfuscator prune.",
        "games": [
            {
                "game_id": "gamezone-0a01fa77-8b8b-4c02-93db-07cf4e05ee06",
                "display_name": "validate_preserved_folders",
                "source_path": str(
                    (
                        REPO_ROOT
                        / "games"
                        / "published"
                        / "public"
                        / "gamezone-0a01fa77-8b8b-4c02-93db-07cf4e05ee06"
                        / "remix-321f864173014c43aa4d4afad5e07111"
                    ).resolve()
                ),
            }
        ],
    }
    MANIFEST.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    command = [
        str(VENV_PYTHON),
        str(OBF_ROOT / "scripts" / "game_obfuscator_cli.py"),
        "start",
        "--manifest",
        str(MANIFEST),
        "--run-id",
        RUN_ID,
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)
    if result.returncode != 0:
        raise SystemExit(result.returncode)

    report = load_json(REPORT_PATH)
    prune_report = report.get("prune_report", {})
    kept_files = set(prune_report.get("kept_files", []))
    preserved_folders = prune_report.get("preserved_folders", [])
    validation = {
        "report_path": str(REPORT_PATH),
        "preserved_folders": preserved_folders,
        "kept_index_html": "index.html" in kept_files,
        "kept_assets": any(path.startswith("assets/") for path in kept_files),
        "kept_screenshots": any(path.startswith("screenshots/") for path in kept_files),
    }
    print(json.dumps(validation, indent=2))


if __name__ == "__main__":
    main()