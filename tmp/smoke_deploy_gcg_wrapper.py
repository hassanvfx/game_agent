#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = REPO_ROOT / "tmp" / "deploy_gcg_wrapper_smoke_report.json"
RUNTIME_MANIFEST_PATH = REPO_ROOT / "tmp" / "deploy_gcg_wrapper_smoke_runtime_manifest.json"
SCRIPT_PATH = REPO_ROOT / "tools" / "game_publish_pipeline" / "scripts" / "deploy_gcg.py"


def parse_json_payload(stdout: str) -> dict | None:
    text = stdout.strip()
    if not text:
        return None
    try:
        payload = json.loads(text)
        return payload if isinstance(payload, dict) else None
    except json.JSONDecodeError:
        pass

    open_brace_positions = [index for index, char in enumerate(text) if char == "{"]
    for index in reversed(open_brace_positions):
        candidate = text[index:]
        try:
            payload = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            return payload
    return None


def main() -> int:
    command = [
        sys.executable,
        str(SCRIPT_PATH),
        "--dry-run",
        "--verbose",
        "--report-path",
        str(REPORT_PATH),
        "--runtime-manifest-path",
        str(RUNTIME_MANIFEST_PATH),
    ]
    completed = subprocess.run(command, capture_output=True, text=True)
    if completed.stdout:
        print(completed.stdout)
    if completed.stderr:
        print(completed.stderr, file=sys.stderr)
    if completed.returncode != 0:
        return completed.returncode

    payload = parse_json_payload(completed.stdout) or {}
    summary = {
        "report_path": str(REPORT_PATH),
        "runtime_manifest_path": str(RUNTIME_MANIFEST_PATH),
        "wrapper_status": payload.get("status"),
        "runtime_entry_count": payload.get("runtime_entry_count"),
        "sanitize_changed_file_count": payload.get("sanitize_changed_file_count"),
        "requires_confirmation_for_apply": payload.get("requires_confirmation_for_apply"),
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())