#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from pathlib import Path


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


def read_manifest_nodes(path: str) -> dict:
    manifest = json.loads(Path(path).read_text(encoding="utf-8"))
    nodes = manifest.get("nodes", [])
    return {
        "node_ids": [n.get("id") for n in nodes],
        "prompt_files": [n.get("prompt_file") for n in nodes],
    }


def main() -> None:
    dry = run_cmd(
        [
            "python3",
            "tools/game_refactoring/scripts/game_workflow.py",
            "--json",
            "--id",
            "creative_remix_v6",
            "--games-manifest-source",
            "tools/game_refactoring/fixtures/specimen_single_game_ed25c3d5_manifest.json",
            "--remix-prompt",
            "Remix this game into a clearly different but mechanically faithful themed experience.",
            "--dry-run-operators",
            "--dry-run-spec-adaptor",
            "--max-concurrency",
            "1",
        ]
    )
    dry_nodes = read_manifest_nodes(dry["workflow_manifest_path"])

    live = None
    live_nodes = None
    status = None
    live_error = None
    try:
        live = run_cmd(
            [
                "python3",
                "tools/game_refactoring/scripts/game_workflow.py",
                "--json",
                "--id",
                "creative_remix_v6",
                "--games-manifest-source",
                "tmp/compare_single_game_ed25c3d5_manifest.json",
                "--remix-prompt",
                "True Rick and Morty inspired game",
                "--max-concurrency",
                "1",
            ]
        )
        live_nodes = read_manifest_nodes(live["workflow_manifest_path"])
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
    except RuntimeError as exc:
        live_error = str(exc)

    result = {
        "dry_run": {
            "run_id": dry.get("run_id"),
            "run_dir": dry.get("run_dir"),
            "output_root": dry.get("output_root"),
            "workflow_manifest_path": dry.get("workflow_manifest_path"),
            **dry_nodes,
        },
        "live_run": None
        if live is None
        else {
            "run_id": live.get("run_id"),
            "run_dir": live.get("run_dir"),
            "output_root": live.get("output_root"),
            "workflow_manifest_path": live.get("workflow_manifest_path"),
            **(live_nodes or {}),
        },
        "live_status": None
        if status is None
        else {
            "status": status.get("status"),
            "current_phase": status.get("current_phase"),
            "dashboard_path": status.get("dashboard_path"),
        },
        "live_error": live_error,
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
