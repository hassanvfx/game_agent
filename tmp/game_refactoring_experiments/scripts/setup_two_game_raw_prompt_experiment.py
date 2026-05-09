#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
import shlex
import subprocess
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path("/Users/hassan/repos/game_agent")
TOP100_ROOT = ROOT / "games" / "top100_vatsal"
RAW_ROOT = ROOT / "games" / "raw"
EXPERIMENT_ROOT = ROOT / "tmp" / "game_refactoring_experiments"
DEFAULT_OUTPUT_ROOT = Path("/Volumes/HDD2026/output")
DEFAULT_WORKFLOW_ID = "creative_remix_v3"
DEFAULT_PIPELINE = "v2"
DEFAULT_SOURCE_MODE = "copy"
DEFAULT_MODEL = "gpt-5.4"
DEFAULT_MAX_CONCURRENCY = 1
DEFAULT_AGENT_TIMEOUT = 3600
DEFAULT_RANDOM_SEED = 20260508
PROMPTS = [
    "harry potter",
    "rick and morty",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Select 2 gamezone ids from games/top100_vatsal that also exist in games/raw, "
            "write one-game manifests, and optionally launch one run for 'harry potter' "
            "and one run for 'rick and morty' using copy mode by default."
        )
    )
    parser.add_argument("--seed", type=int, default=DEFAULT_RANDOM_SEED, help="Random seed used for raw-backed game sampling.")
    parser.add_argument(
        "--experiment-name",
        default="two_game_raw_prompt_experiment",
        help="Directory name under tmp/game_refactoring_experiments/experiments/.",
    )
    parser.add_argument(
        "--runs-root",
        default=str(DEFAULT_OUTPUT_ROOT),
        help="External runs root passed through to game_workflow.py.",
    )
    parser.add_argument("--workflow-id", default=DEFAULT_WORKFLOW_ID, help="Workflow id to launch.")
    parser.add_argument("--pipeline", default=DEFAULT_PIPELINE, choices=["v2", "legacy"], help="Pipeline to launch.")
    parser.add_argument(
        "--source-mode",
        default=DEFAULT_SOURCE_MODE,
        choices=["copy", "inplace"],
        help="Source mode passed through to game_workflow.py.",
    )
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Model passed through to game_workflow.py.")
    parser.add_argument(
        "--max-concurrency",
        type=int,
        default=DEFAULT_MAX_CONCURRENCY,
        help="Max concurrency per run.",
    )
    parser.add_argument(
        "--agent-timeout",
        type=int,
        default=DEFAULT_AGENT_TIMEOUT,
        help="Agent timeout in seconds for each launched run.",
    )
    parser.add_argument(
        "--playwright-port-base",
        type=int,
        default=None,
        help="Optional override forwarded to game_workflow.py.",
    )
    parser.add_argument(
        "--playwright-port-pool-size",
        type=int,
        default=None,
        help="Optional override forwarded to game_workflow.py.",
    )
    parser.add_argument(
        "--playwright-port-lease-ttl-seconds",
        type=int,
        default=None,
        help="Optional override forwarded to game_workflow.py.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite an existing experiment directory if present.",
    )
    parser.add_argument(
        "--launch",
        action="store_true",
        help="Actually launch the two runs after writing manifests/prompts/metadata.",
    )
    return parser.parse_args()


def utc_now_compact() -> str:
    return datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")


def slugify(value: str) -> str:
    cleaned = "".join(char.lower() if char.isalnum() else "-" for char in value.strip())
    parts = [part for part in cleaned.split("-") if part]
    return "-".join(parts) or "prompt"


def discover_raw_backed_games() -> list[Path]:
    top100_ids = sorted(path.name for path in TOP100_ROOT.iterdir() if path.is_dir() and path.name.startswith("gamezone-"))
    raw_dirs = {path.name: path for path in RAW_ROOT.iterdir() if path.is_dir()}
    return [raw_dirs[game_id] for game_id in top100_ids if game_id in raw_dirs]


def build_manifest_payload(game_dir: Path, run_label: str) -> dict[str, object]:
    return {
        "run_label": run_label,
        "games": [
            {
                "game_id": game_dir.name,
                "display_name": game_dir.name,
                "source_path": str(game_dir.resolve()),
            }
        ],
    }


def build_launch_command(
    *,
    manifest_path: Path,
    prompt_path: Path,
    run_id: str,
    args: argparse.Namespace,
) -> list[str]:
    command = [
        "python3",
        str(ROOT / "tools" / "game_refactoring" / "scripts" / "game_workflow.py"),
        "--json",
        "--id",
        args.workflow_id,
        "--games-manifest-source",
        str(manifest_path),
        "--run-id",
        run_id,
        "--runs-root",
        str(Path(args.runs_root).resolve()),
        "--pipeline",
        args.pipeline,
        "--source-mode",
        args.source_mode,
        "--model",
        args.model,
        "--max-concurrency",
        str(args.max_concurrency),
        "--agent-timeout",
        str(args.agent_timeout),
        "--remix-prompt-file",
        str(prompt_path),
    ]
    if args.playwright_port_base is not None:
        command.extend(["--playwright-port-base", str(args.playwright_port_base)])
    if args.playwright_port_pool_size is not None:
        command.extend(["--playwright-port-pool-size", str(args.playwright_port_pool_size)])
    if args.playwright_port_lease_ttl_seconds is not None:
        command.extend(["--playwright-port-lease-ttl-seconds", str(args.playwright_port_lease_ttl_seconds)])
    return command


def shell_join(parts: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in parts)


def main() -> None:
    args = parse_args()
    available_games = discover_raw_backed_games()
    if len(available_games) < 2:
        raise SystemExit(f"Expected at least 2 raw-backed Vatsal game directories, found {len(available_games)}.")

    experiment_dir = EXPERIMENT_ROOT / "experiments" / args.experiment_name
    if experiment_dir.exists() and not args.force:
        raise SystemExit(
            f"Experiment directory already exists: {experiment_dir}\n"
            "Pass --force to overwrite the disposable scaffold."
        )

    manifests_dir = experiment_dir / "manifests"
    prompts_dir = experiment_dir / "prompts"
    logs_dir = experiment_dir / "logs"
    metadata_dir = experiment_dir / "metadata"
    for directory in (manifests_dir, prompts_dir, logs_dir, metadata_dir):
        directory.mkdir(parents=True, exist_ok=True)

    sampler = random.Random(args.seed)
    selected_games = sampler.sample(available_games, 2)
    timestamp = utc_now_compact()
    jobs: list[dict[str, object]] = []

    for index, (game_dir, prompt_text) in enumerate(zip(selected_games, PROMPTS, strict=True), start=1):
        prompt_slug = slugify(prompt_text)
        job_id = f"job_{index:02d}"
        run_id = f"run_two_game_raw_{timestamp}_{job_id}_{prompt_slug}"
        run_label = f"{args.experiment_name}-{job_id}-{prompt_slug}"
        prompt_path = prompts_dir / f"{job_id}__{prompt_slug}.txt"
        manifest_path = manifests_dir / f"{job_id}__{game_dir.name}.json"
        log_path = logs_dir / f"{job_id}__launch.log"

        prompt_path.write_text(prompt_text.strip() + "\n", encoding="utf-8")
        manifest_payload = build_manifest_payload(game_dir, run_label)
        manifest_path.write_text(json.dumps(manifest_payload, indent=2) + "\n", encoding="utf-8")

        command = build_launch_command(
            manifest_path=manifest_path,
            prompt_path=prompt_path,
            run_id=run_id,
            args=args,
        )

        job: dict[str, object] = {
            "job_id": job_id,
            "prompt_text": prompt_text,
            "prompt_slug": prompt_slug,
            "game_id": game_dir.name,
            "game_source_path": str(game_dir.resolve()),
            "manifest_path": str(manifest_path),
            "prompt_path": str(prompt_path),
            "log_path": str(log_path),
            "run_id": run_id,
            "runs_root": str(Path(args.runs_root).resolve()),
            "command": command,
        }

        if args.launch:
            completed = subprocess.run(command, cwd=str(ROOT), capture_output=True, text=True)
            log_path.write_text(
                completed.stdout + ("\n" if completed.stdout and not completed.stdout.endswith("\n") else "")
                + completed.stderr,
                encoding="utf-8",
            )
            job["launch_exit_code"] = completed.returncode
            try:
                job["launch_result"] = json.loads(completed.stdout)
            except json.JSONDecodeError:
                job["launch_result"] = {"stdout": completed.stdout.strip(), "stderr": completed.stderr.strip()}
        else:
            log_path.write_text(shell_join(command) + "\n", encoding="utf-8")
            job["launch_exit_code"] = None

        jobs.append(job)

    plan = {
        "experiment_name": args.experiment_name,
        "created_at_utc": timestamp,
        "seed": args.seed,
        "source_top100_root": str(TOP100_ROOT),
        "source_raw_root": str(RAW_ROOT),
        "runs_root": str(Path(args.runs_root).resolve()),
        "workflow_id": args.workflow_id,
        "pipeline": args.pipeline,
        "source_mode": args.source_mode,
        "model": args.model,
        "max_concurrency": args.max_concurrency,
        "agent_timeout": args.agent_timeout,
        "selected_prompts": PROMPTS,
        "launch_requested": args.launch,
        "jobs": jobs,
    }

    plan_path = metadata_dir / "experiment_plan.json"
    plan_path.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(
        {
            "experiment_dir": str(experiment_dir),
            "plan_path": str(plan_path),
            "selected_game_ids": [job["game_id"] for job in jobs],
            "launch_requested": args.launch,
            "jobs": jobs,
        },
        indent=2,
    ))


if __name__ == "__main__":
    main()