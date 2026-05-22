#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path("/Users/hassan/repos/game_agent")
AUDIT_SCRIPT = ROOT / "tmp/audit_published_catalog_regressions.py"
MANIFEST_SCRIPT = ROOT / "tmp/build_may17_full_publish_manifest.py"
PUBLISH_SCRIPT = ROOT / "tools/game_publish_pipeline/scripts/publish_games.py"

BASELINE_AUDIT_PATH = ROOT / "tmp/may17_regression_baseline_audit.json"
AFTER_AUDIT_PATH = ROOT / "tmp/may17_regression_after_audit.json"
MANIFEST_PATH = ROOT / "tmp/may17_full_publish_manifest.json"
MANIFEST_REPORT_PATH = ROOT / "tmp/may17_full_publish_manifest_report.json"
PUBLISH_REPORT_PATH = ROOT / "tmp/may17_full_publish_report.json"
DELTA_REPORT_PATH = ROOT / "tmp/may17_full_regression_delta.json"


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def run_command(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=ROOT, capture_output=True, text=True)


def require_success(result: subprocess.CompletedProcess[str], step_name: str) -> None:
    if result.returncode != 0:
        raise SystemExit(
            json.dumps(
                {
                    "error": f"{step_name} failed",
                    "returncode": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                },
                indent=2,
            )
        )


def extract_counts(payload: dict[str, Any]) -> dict[str, int]:
    return {
        "public_zero_screenshots_count": int(payload["public"]["zero_screenshots_count"]),
        "public_generic_titles_count": int(payload["public"]["generic_titles_count"]),
        "public_no_tags_count": int(payload["public"]["no_tags_count"]),
        "public_candidate_for_removal_count": int(payload["public"]["candidate_for_removal_count"]),
        "obfuscated_zero_screenshots_count": int(payload["obfuscated"]["zero_screenshots_count"]),
        "obfuscated_generic_titles_count": int(payload["obfuscated"]["generic_titles_count"]),
        "obfuscated_no_tags_count": int(payload["obfuscated"]["no_tags_count"]),
        "obfuscated_candidate_for_removal_count": int(payload["obfuscated"]["candidate_for_removal_count"]),
    }


def compute_delta(before: dict[str, int], after: dict[str, int]) -> dict[str, int]:
    return {key: after[key] - before[key] for key in before}


def main() -> None:
    steps: list[dict[str, Any]] = []

    baseline_cmd = [sys.executable, str(AUDIT_SCRIPT), "--label", "baseline", "--report-path", str(BASELINE_AUDIT_PATH)]
    baseline_result = run_command(baseline_cmd)
    steps.append({"step": "baseline_audit", "command": baseline_cmd, "returncode": baseline_result.returncode})
    require_success(baseline_result, "baseline audit")

    manifest_cmd = [
        sys.executable,
        str(MANIFEST_SCRIPT),
        "--manifest-path",
        str(MANIFEST_PATH),
        "--report-path",
        str(MANIFEST_REPORT_PATH),
    ]
    manifest_result = run_command(manifest_cmd)
    steps.append({"step": "build_manifest", "command": manifest_cmd, "returncode": manifest_result.returncode})
    require_success(manifest_result, "manifest build")

    publish_cmd = [
        sys.executable,
        str(PUBLISH_SCRIPT),
        "--manifest",
        str(MANIFEST_PATH),
        "--report-path",
        str(PUBLISH_REPORT_PATH),
        "--overwrite",
        "--refresh-app-artifacts-collection-slug",
        "may17_full_regression",
    ]
    publish_result = run_command(publish_cmd)
    steps.append({"step": "publish_overwrite", "command": publish_cmd, "returncode": publish_result.returncode})
    require_success(publish_result, "full overwrite publish")

    after_cmd = [sys.executable, str(AUDIT_SCRIPT), "--label", "after_overwrite", "--report-path", str(AFTER_AUDIT_PATH)]
    after_result = run_command(after_cmd)
    steps.append({"step": "after_audit", "command": after_cmd, "returncode": after_result.returncode})
    require_success(after_result, "after audit")

    baseline_payload = load_json(BASELINE_AUDIT_PATH)
    after_payload = load_json(AFTER_AUDIT_PATH)
    baseline_counts = extract_counts(baseline_payload)
    after_counts = extract_counts(after_payload)
    delta_counts = compute_delta(baseline_counts, after_counts)

    delta_payload = {
        "timestamp": utc_timestamp(),
        "baseline_audit_path": str(BASELINE_AUDIT_PATH),
        "after_audit_path": str(AFTER_AUDIT_PATH),
        "manifest_path": str(MANIFEST_PATH),
        "manifest_report_path": str(MANIFEST_REPORT_PATH),
        "publish_report_path": str(PUBLISH_REPORT_PATH),
        "steps": steps,
        "baseline_counts": baseline_counts,
        "after_counts": after_counts,
        "delta_counts": delta_counts,
    }
    write_json(DELTA_REPORT_PATH, delta_payload)
    print(json.dumps({"delta_report_path": str(DELTA_REPORT_PATH), **delta_counts}, indent=2))


if __name__ == "__main__":
    main()