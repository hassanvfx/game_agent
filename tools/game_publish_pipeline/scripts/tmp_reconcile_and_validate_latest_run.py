#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str]) -> None:
    print(f"[tmp] running: {' '.join(cmd)}", flush=True)
    result = subprocess.run(cmd, text=True)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def main() -> None:
    tool_root = Path(__file__).resolve().parents[1]
    repo_root = tool_root.parents[1]

    run_id = "run_20260517T045748Z"
    manifest_path = repo_root / "games" / "published" / "runs" / run_id / "artifacts_manifest.json"
    report_path = repo_root / "tmp" / f"{run_id}_validation_after_reconcile.json"

    refresh_cmd = [
        sys.executable,
        str(tool_root / "scripts" / "refresh_app_artifacts.py"),
        "--manifest",
        str(manifest_path),
        "--run-id",
        run_id,
        "--reconcile-mode",
        "replace",
    ]
    run(refresh_cmd)

    validate_cmd = [
        sys.executable,
        str(tool_root / "scripts" / "validate_published_outputs.py"),
        "--manifest",
        str(manifest_path),
        "--public-root",
        str(repo_root / "games" / "published" / "public"),
        "--obfuscated-root",
        str(repo_root / "games" / "published" / "obfuscated"),
        "--runs-root",
        str(repo_root / "games" / "published" / "runs"),
        "--run-id",
        run_id,
        "--collection-slug",
        "vatsal_app_alpha",
        "--report-path",
        str(report_path),
    ]
    run(validate_cmd)

    report = json.loads(report_path.read_text(encoding="utf-8"))
    summary = report.get("summary", {})
    payload = {
        "run_id": run_id,
        "validation_report": str(report_path),
        "status": summary.get("status"),
        "entries_passed": summary.get("entries_passed"),
        "entries_total": summary.get("entries_total"),
        "app_artifacts_failed": summary.get("app_artifacts_failed"),
        "app_artifacts_total": summary.get("app_artifacts_total"),
        "dashboard_artifacts_failed": summary.get("dashboard_artifacts_failed"),
        "dashboard_artifacts_total": summary.get("dashboard_artifacts_total"),
        "failure_categories": summary.get("failure_categories"),
    }
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
