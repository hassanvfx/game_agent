#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = ROOT.parent.parent
RUNS_ROOT = REPO_ROOT / "games" / "published" / "runs"
PUBLIC_APP_JSON = REPO_ROOT / "games" / "published" / "public" / "app.json"
TARGET_COMPOSITE_KEY = "gamezone-29e7c3b5-974b-47c7-b7bf-585b6d5cc301__remix-2d9ceef4234dc323cd850ecec55d170a"


def main() -> int:
    run_dirs = sorted(path for path in RUNS_ROOT.iterdir() if path.is_dir() and path.name.startswith("run_"))
    command = [
        sys.executable,
        str((ROOT.parent / "game_publish_pipeline" / "scripts" / "materialize_artifact_view.py").resolve()),
        "--runs",
        *[str(path.resolve()) for path in run_dirs],
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    if result.returncode != 0:
        return result.returncode

    payload = json.loads(PUBLIC_APP_JSON.read_text())
    report = {
        "run_count": len(run_dirs),
        "target_composite_key_present_after_materialize": TARGET_COMPOSITE_KEY in payload,
        "public_app_record_count": len(payload) if isinstance(payload, dict) else None,
    }
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())