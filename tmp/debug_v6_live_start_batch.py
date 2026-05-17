#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from pathlib import Path


def main() -> None:
    manifest = Path(
        "tools/game_refactoring/runs/_workflow_manifests/"
        "creative_remix_v6__compare_single_game_ed25c3d5_manifest.json"
    )
    if not manifest.exists():
        print(json.dumps({"error": "manifest_not_found", "manifest": str(manifest)}, indent=2))
        return

    cmd = [
        "python3",
        "tools/game_refactoring/scripts/creative_refactor_cli.py",
        "--json",
        "start-batch",
        "--manifest",
        str(manifest),
        "--pipeline",
        "v2",
        "--model",
        "gpt-5.5",
        "--agent-timeout",
        "3600",
        "--max-concurrency",
        "1",
        "--poll-seconds",
        "5.0",
        "--stale-heartbeat-seconds",
        "900",
        "--source-mode",
        "copy",
        "--remix-prompt",
        "True Rick and Morty inspired game",
    ]
    completed = subprocess.run(cmd, text=True, capture_output=True)
    print(
        json.dumps(
            {
                "returncode": completed.returncode,
                "stdout": completed.stdout,
                "stderr": completed.stderr,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
