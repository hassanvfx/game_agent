#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path


def find_latest_complete_run(runs_root: Path) -> Path:
    candidates = sorted(
        [path for path in runs_root.iterdir() if path.is_dir() and path.name.startswith("run_")],
        key=lambda path: path.name,
        reverse=True,
    )
    for run_dir in candidates:
        if (run_dir / "public" / "app.json").is_file() and (run_dir / "obfuscated" / "app.json").is_file():
            return run_dir
    raise SystemExit("No run_* directory with both public/app.json and obfuscated/app.json was found.")


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    runs_root = repo_root / "games" / "published" / "runs"
    script_path = repo_root / "tools" / "game_publish_pipeline" / "scripts" / "materialize_artifact_view.py"
    smoke_root = repo_root / "tmp" / "materialize_final_state_smoke"
    public_root = smoke_root / "public"
    obfuscated_root = smoke_root / "obfuscated"
    report_path = smoke_root / "validation_report.json"

    selected_run = find_latest_complete_run(runs_root)

    if smoke_root.exists():
        shutil.rmtree(smoke_root)
    public_root.mkdir(parents=True, exist_ok=True)
    obfuscated_root.mkdir(parents=True, exist_ok=True)

    command = [
        sys.executable,
        str(script_path),
        "--runs",
        str(selected_run),
        "--public-root",
        str(public_root),
        "--obfuscated-root",
        str(obfuscated_root),
        "--validation-report-path",
        str(report_path),
    ]

    completed = subprocess.run(command, cwd=repo_root, capture_output=True, text=True)

    summary = {
        "selected_run": selected_run.name,
        "smoke_root": str(smoke_root),
        "return_code": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "validation_report_exists": report_path.is_file(),
    }

    if report_path.is_file():
        report = json.loads(report_path.read_text(encoding="utf-8"))
        summary["validation_report_summary"] = {
            "entry_count": report.get("entry_count"),
            "failure_count": report.get("failure_count"),
            "same_html_count": report.get("same_html_count"),
            "valid_public_count": report.get("valid_public_count"),
            "valid_obfuscated_count": report.get("valid_obfuscated_count"),
            "cache_key": report.get("cache_key"),
        }

    print(json.dumps(summary, indent=2))
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())