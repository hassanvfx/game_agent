#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    script_path = repo_root / "tools" / "game_publish_pipeline" / "scripts" / "materialize_artifact_view.py"
    report_path = repo_root / "tmp" / "materialize_final_state_validation_real_report.json"

    command = [
        sys.executable,
        str(script_path),
        "--validation-report-path",
        str(report_path),
    ]

    completed = subprocess.run(command, cwd=repo_root, capture_output=True, text=True)

    summary = {
        "command": command,
        "return_code": completed.returncode,
        "report_path": str(report_path),
        "report_exists": report_path.is_file(),
        "stdout_tail": completed.stdout[-12000:],
        "stderr": completed.stderr,
    }

    if report_path.is_file():
        report = json.loads(report_path.read_text(encoding="utf-8"))
        summary["validation_report_summary"] = {
            "entry_count": report.get("entry_count"),
            "failure_count": report.get("failure_count"),
            "same_html_count": report.get("same_html_count"),
            "valid_public_count": report.get("valid_public_count"),
            "valid_obfuscated_count": report.get("valid_obfuscated_count"),
            "missing_public_folder_count": report.get("missing_public_folder_count"),
            "missing_public_index_count": report.get("missing_public_index_count"),
            "missing_obfuscated_folder_count": report.get("missing_obfuscated_folder_count"),
            "missing_obfuscated_index_count": report.get("missing_obfuscated_index_count"),
            "cache_key": report.get("cache_key"),
        }

    print(json.dumps(summary, indent=2))
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())