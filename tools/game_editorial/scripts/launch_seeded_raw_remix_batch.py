#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from game_editorial.deterministic_remix_manifest import (  # noqa: E402
    DEFAULT_OUTPUT_RUNS_ROOT,
    DEFAULT_WORKFLOW_ID,
    DEFAULT_WORKSPACE_ROOT,
    generate_batch_artifacts,
)


ROOT = Path(__file__).resolve().parents[3]
GAME_WORKFLOW_SCRIPT = ROOT / "tools" / "game_refactoring" / "scripts" / "game_workflow.py"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate a deterministic creative_remix_v5 manifest from games/raw using game_editorial remix ideas, "
            "then optionally launch it through game_refactoring."
        )
    )
    parser.add_argument(
        "--prompts-per-game",
        type=int,
        default=1,
        help="How many deterministic prompt variants to generate per raw game. Each variant becomes its own manifest entry.",
    )
    parser.add_argument(
        "--game-limit",
        type=int,
        help="Optional limit on how many raw games to include from the stable sorted corpus.",
    )
    parser.add_argument(
        "--seed-offset",
        type=int,
        default=0,
        help="Optional starting offset added to the expanded-entry index before prompt selection.",
    )
    parser.add_argument(
        "--raw-game-offset",
        type=int,
        default=0,
        help="Optional starting offset into the stable sorted raw-game corpus before applying game-limit.",
    )
    parser.add_argument(
        "--runs-root",
        default=str(DEFAULT_OUTPUT_RUNS_ROOT),
        help="External runs root passed through to game_refactoring.",
    )
    parser.add_argument(
        "--workspace-root",
        default=str(DEFAULT_WORKSPACE_ROOT),
        help="Workspace directory for generated manifest and trace artifacts.",
    )
    parser.add_argument("--run-id", help="Optional explicit run id for game_refactoring.")
    parser.add_argument("--model", default="gpt-5.5", help="Model passed through to game_refactoring.")
    parser.add_argument("--agent-timeout", type=int, default=3600, help="Per-game worker timeout in seconds.")
    parser.add_argument("--max-concurrency", type=int, default=2, help="Maximum active workers.")
    parser.add_argument("--poll-seconds", type=float, default=5.0, help="Scheduler poll interval.")
    parser.add_argument(
        "--stale-heartbeat-seconds",
        type=int,
        default=900,
        help="Heartbeat age threshold after which a worker is considered stale.",
    )
    parser.add_argument(
        "--source-mode",
        choices=["copy", "inplace"],
        default="copy",
        help="How source game directories should be prepared before execution.",
    )
    parser.add_argument("--pipeline", choices=["v2", "legacy"], default="v2", help="Batch pipeline to use.")
    parser.add_argument("--dry-run-operators", action="store_true", help="Simulate operator execution.")
    parser.add_argument("--dry-run-spec-adaptor", action="store_true", help="Simulate spec-adaptor execution.")
    parser.add_argument("--no-launch", action="store_true", help="Only generate artifacts; do not start the workflow.")
    parser.add_argument("--json", action="store_true", help="Emit structured JSON output.")
    return parser.parse_args()


def build_launch_command(args: argparse.Namespace, manifest_path: str) -> list[str]:
    command = [
        "python3",
        str(GAME_WORKFLOW_SCRIPT),
        "--json",
        "--id",
        DEFAULT_WORKFLOW_ID,
        "--games-manifest-source",
        manifest_path,
        "--runs-root",
        args.runs_root,
        "--source-mode",
        args.source_mode,
        "--pipeline",
        args.pipeline,
        "--model",
        args.model,
        "--agent-timeout",
        str(args.agent_timeout),
        "--max-concurrency",
        str(args.max_concurrency),
        "--poll-seconds",
        str(args.poll_seconds),
        "--stale-heartbeat-seconds",
        str(args.stale_heartbeat_seconds),
    ]
    if args.run_id:
        command.extend(["--run-id", args.run_id])
    if args.dry_run_operators:
        command.append("--dry-run-operators")
    if args.dry_run_spec_adaptor:
        command.append("--dry-run-spec-adaptor")
    return command


def emit(payload: dict[str, object], as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, indent=2))
        return
    print(json.dumps(payload, indent=2))


def main() -> None:
    args = parse_args()
    summary = generate_batch_artifacts(
        prompts_per_game=args.prompts_per_game,
        workspace_root=Path(args.workspace_root).resolve(),
        game_limit=args.game_limit,
        seed_offset=args.seed_offset,
        raw_game_offset=args.raw_game_offset,
        source_mode=args.source_mode,
    )
    payload: dict[str, object] = {
        "workflow_id": DEFAULT_WORKFLOW_ID,
        "prompts_per_game": args.prompts_per_game,
        "game_limit": args.game_limit,
        "raw_game_offset": args.raw_game_offset,
        "seed_mode": "expanded_entry_index",
        "seed_offset": args.seed_offset,
        "source_mode": args.source_mode,
        "artifact_summary": summary,
        "launched": False,
    }
    if args.no_launch:
        emit(payload, args.json)
        return

    command = build_launch_command(args, str(summary["manifest_path"]))
    completed = subprocess.run(command, check=True, capture_output=True, text=True, cwd=str(ROOT))
    workflow_payload = json.loads(completed.stdout)
    payload["launched"] = True
    payload["launch_command"] = command
    payload["workflow_result"] = workflow_payload
    emit(payload, args.json)


if __name__ == "__main__":
    main()