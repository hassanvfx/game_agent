#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess


def run_cmd(args: list[str]) -> dict:
    completed = subprocess.run(args, text=True, capture_output=True)
    if completed.returncode != 0:
        raise RuntimeError(
            json.dumps(
                {
                    "command": args,
                    "returncode": completed.returncode,
                    "stdout": completed.stdout,
                    "stderr": completed.stderr,
                },
                indent=2,
            )
        )
    return json.loads(completed.stdout)


def main() -> None:
    live = run_cmd(
        [
            "python3",
            "tools/game_refactoring/scripts/game_workflow.py",
            "--json",
            "--id",
            "creative_remix_v5",
            "--games-manifest-source",
            "tmp/compare_single_game_ed25c3d5_manifest.json",
            "--remix-prompt",
            "True Rick and Morty inspired game",
            "--max-concurrency",
            "1",
        ]
    )
    status = run_cmd(
        [
            "python3",
            "tools/game_refactoring/scripts/creative_refactor_cli.py",
            "--json",
            "status",
            "--run-id",
            live["run_id"],
        ]
    )
    print(
        json.dumps(
            {
                "live_run": {
                    "run_id": live.get("run_id"),
                    "run_dir": live.get("run_dir"),
                    "output_root": live.get("output_root"),
                    "workflow_manifest_path": live.get("workflow_manifest_path"),
                },
                "live_status": {
                    "status": status.get("status"),
                    "current_phase": status.get("current_phase"),
                    "dashboard_path": status.get("dashboard_path"),
                },
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()