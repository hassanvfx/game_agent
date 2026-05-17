#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shlex
from pathlib import Path


if __package__ is None or __package__ == "":
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from game_editorial.deterministic_remix_manifest import (  # noqa: E402
    DEFAULT_OUTPUT_RUNS_ROOT,
    DEFAULT_RAW_ROOT,
    DEFAULT_WORKFLOW_ID,
    DEFAULT_WORKSPACE_ROOT,
    discover_raw_games,
    write_json,
)


ROOT = Path(__file__).resolve().parents[3]
LAUNCHER = ROOT / "tools" / "game_editorial" / "scripts" / "launch_seeded_raw_remix_batch.py"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Plan sequential creative_remix_v5 launches over the full raw corpus in fixed-size batches."
    )
    parser.add_argument("--batch-size", type=int, default=100, help="How many base raw games to include per batch.")
    parser.add_argument("--prompts-per-game", type=int, default=2, help="Deterministic prompt variants per raw game.")
    parser.add_argument("--seed-offset", type=int, default=0, help="Global additional seed offset.")
    parser.add_argument("--source-mode", choices=["copy", "inplace"], default="copy")
    parser.add_argument("--runs-root", default=str(DEFAULT_OUTPUT_RUNS_ROOT))
    parser.add_argument("--workspace-root", default=str(DEFAULT_WORKSPACE_ROOT))
    parser.add_argument("--model", default="gpt-5.5")
    parser.add_argument("--agent-timeout", type=int, default=3600)
    parser.add_argument("--max-concurrency", type=int, default=2)
    parser.add_argument("--poll-seconds", type=float, default=5.0)
    parser.add_argument("--stale-heartbeat-seconds", type=int, default=900)
    parser.add_argument("--pipeline", choices=["v2", "legacy"], default="v2")
    parser.add_argument("--limit-batches", type=int, help="Optional cap on how many planned batches to emit.")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def build_launch_command(args: argparse.Namespace, raw_game_offset: int, game_limit: int) -> list[str]:
    return [
        "python3",
        str(LAUNCHER),
        "--game-limit",
        str(game_limit),
        "--raw-game-offset",
        str(raw_game_offset),
        "--prompts-per-game",
        str(args.prompts_per_game),
        "--seed-offset",
        str(args.seed_offset),
        "--source-mode",
        args.source_mode,
        "--runs-root",
        args.runs_root,
        "--workspace-root",
        args.workspace_root,
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
        "--pipeline",
        args.pipeline,
        "--json",
    ]


def main() -> None:
    args = parse_args()
    if args.batch_size <= 0:
        raise SystemExit("--batch-size must be >= 1")
    if args.prompts_per_game <= 0:
        raise SystemExit("--prompts-per-game must be >= 1")

    raw_games = discover_raw_games(DEFAULT_RAW_ROOT)
    total_raw_games = len(raw_games)
    workspace_root = Path(args.workspace_root).resolve()
    plan_dir = workspace_root / "batch_plans" / f"creative-remix-v5-g{args.batch_size}-ppg-{args.prompts_per_game}"
    plan_dir.mkdir(parents=True, exist_ok=True)

    batches: list[dict[str, object]] = []
    for batch_index, start in enumerate(range(0, total_raw_games, args.batch_size), start=1):
        if args.limit_batches is not None and len(batches) >= args.limit_batches:
            break
        selected = raw_games[start : start + args.batch_size]
        command = build_launch_command(args, raw_game_offset=start, game_limit=len(selected))
        batches.append(
            {
                "batch_index": batch_index,
                "raw_game_offset": start,
                "game_limit": len(selected),
                "expected_manifest_entries": len(selected) * args.prompts_per_game,
                "first_game_id": selected[0].game_id,
                "last_game_id": selected[-1].game_id,
                "launch_command": command,
                "launch_command_shell": shlex.join(command),
            }
        )

    plan = {
        "workflow_id": DEFAULT_WORKFLOW_ID,
        "raw_root": str(DEFAULT_RAW_ROOT.resolve()),
        "runs_root": str(Path(args.runs_root).resolve()),
        "workspace_root": str(workspace_root),
        "batch_size": args.batch_size,
        "prompts_per_game": args.prompts_per_game,
        "seed_offset": args.seed_offset,
        "source_mode": args.source_mode,
        "pipeline": args.pipeline,
        "model": args.model,
        "max_concurrency": args.max_concurrency,
        "total_raw_games": total_raw_games,
        "planned_batches": len(batches),
        "batches": batches,
    }

    plan_path = plan_dir / "plan.json"
    launch_all_path = plan_dir / "launch_all_sequential.sh"
    write_json(plan_path, plan)
    shell_sections: list[str] = []
    for batch in batches:
        shell_sections.append(
            "\n".join(
                [
                    f"# Batch {batch['batch_index']:02d}: raw offset {batch['raw_game_offset']} limit {batch['game_limit']}",
                    str(batch["launch_command_shell"]),
                    "",
                ]
            )
        )
    launch_all_path.write_text(
        (
            "#!/bin/zsh\nset -euo pipefail\n\n" + "\n".join(shell_sections)
            if batches
            else "#!/bin/zsh\nset -euo pipefail\n"
        ),
        encoding="utf-8",
    )

    payload = {
        "plan_path": str(plan_path),
        "launch_all_path": str(launch_all_path),
        "planned_batches": len(batches),
        "total_raw_games": total_raw_games,
        "batch_size": args.batch_size,
        "prompts_per_game": args.prompts_per_game,
        "batches": batches[: min(3, len(batches))],
    }
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()