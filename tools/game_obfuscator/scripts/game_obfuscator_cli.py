#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from orchestration_state import load_json, write_json

ROOT = Path(__file__).resolve().parents[1]
RUNS_ROOT = ROOT / "runs"
SCRIPTS_DIR = ROOT / "scripts"


def print_json(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2))


def resolve_run_dir(run_id: str | None, run_dir: str | None) -> Path:
    if run_id and run_dir:
        raise SystemExit("Provide either --run-id or --run-dir, not both.")
    if run_id:
        resolved = (RUNS_ROOT / run_id).resolve()
    elif run_dir:
        resolved = Path(run_dir).resolve()
    else:
        raise SystemExit("One of --run-id or --run-dir is required.")
    if not resolved.exists():
        raise SystemExit(f"Run directory does not exist: {resolved}")
    return resolved


def run_python_script(
    script_name: str,
    *args: str,
    env: dict[str, str] | None = None,
    python_executable: str | None = None,
) -> subprocess.CompletedProcess[str]:
    executable = python_executable or sys.executable
    command = [executable, str(SCRIPTS_DIR / script_name), *args]
    return subprocess.run(command, capture_output=True, text=True, env=env)


def extract_last_nonempty_line(text: str) -> str | None:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return lines[-1] if lines else None


def select_python_executable() -> str:
    venv_python = ROOT / ".venv" / "bin" / "python"
    return str(venv_python) if venv_python.exists() else sys.executable


def launcher_log_paths(run_dir: Path) -> tuple[Path, Path]:
    logs_dir = run_dir / "logs"
    return logs_dir / "launcher.stdout.log", logs_dir / "launcher.stderr.log"


def build_status_payload(run_dir: Path) -> dict[str, Any]:
    run_state = load_json(run_dir / "run_state.json")
    payload: dict[str, Any] = {
        "run_id": run_state.get("run_id"),
        "run_dir": str(run_dir),
        "status": run_state.get("status"),
        "current_phase": run_state.get("current_phase"),
        "created_at": run_state.get("created_at"),
        "started_at": run_state.get("started_at"),
        "completed_at": run_state.get("completed_at"),
        "updated_at": run_state.get("updated_at"),
        "heartbeat_at": run_state.get("heartbeat_at"),
        "last_progress_at": run_state.get("last_progress_at"),
        "games_total": run_state.get("games_total"),
        "games_pending": run_state.get("games_pending"),
        "games_running": run_state.get("games_running"),
        "games_succeeded": run_state.get("games_succeeded"),
        "games_failed": run_state.get("games_failed"),
        "games_stalled": run_state.get("games_stalled"),
        "dashboard_path": str((run_dir / "dashboard" / "index.html").resolve()),
        "output_root": str((run_dir / "output").resolve()),
        "completed": run_state.get("status") in {"completed", "completed_with_failures", "failed", "stalled"},
    }

    launcher = run_state.get("launcher")
    if isinstance(launcher, dict):
        payload["launcher"] = launcher

    if run_state.get("last_error"):
        payload["last_error"] = run_state.get("last_error")

    return payload


def build_result_payload(run_dir: Path, *, include_games: bool = False) -> dict[str, Any]:
    run_state = load_json(run_dir / "run_state.json")
    payload: dict[str, Any] = {
        "run_id": run_state.get("run_id"),
        "run_dir": str(run_dir),
        "status": run_state.get("status"),
        "current_phase": run_state.get("current_phase"),
        "output_path": str((run_dir / "output").resolve()),
        "completed": run_state.get("status") in {"completed", "completed_with_failures", "failed", "stalled"},
    }

    if include_games:
        manifest = load_json(run_dir / "input_manifest.json")
        payload["game_outputs"] = [
            {
                "game_id": game["game_id"],
                "output_path": str((run_dir / "output" / game["game_id"]).resolve()),
            }
            for game in manifest.get("games", [])
        ]

    if run_state.get("last_error"):
        payload["last_error"] = run_state.get("last_error")

    return payload


def handle_start(args: argparse.Namespace) -> None:
    python_executable = select_python_executable()

    create_result = run_python_script(
        "create_run.py",
        "--manifest",
        args.manifest,
        *(["--run-id", args.run_id] if args.run_id else []),
        python_executable=python_executable,
    )
    if create_result.returncode != 0:
        raise SystemExit(create_result.stderr.strip() or create_result.stdout.strip() or "Failed to create run.")

    run_dir_line = extract_last_nonempty_line(create_result.stdout)
    if not run_dir_line:
        raise SystemExit("Could not determine run directory from create_run.py output.")

    run_dir = Path(run_dir_line).resolve()
    if not run_dir.exists():
        raise SystemExit(f"Created run directory does not exist: {run_dir}")

    stdout_log, stderr_log = launcher_log_paths(run_dir)
    stdout_log.parent.mkdir(parents=True, exist_ok=True)

    env = dict(os.environ)
    existing_pythonpath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(SCRIPTS_DIR) if not existing_pythonpath else f"{SCRIPTS_DIR}:{existing_pythonpath}"
    env["GAME_OBFUSCATOR_PYTHON"] = python_executable

    pipeline_script_name = (
        "run_game_obfuscator_simple_pipeline.py" if args.pipeline == "simple" else "run_game_obfuscator_pipeline.py"
    )

    command = [
        python_executable,
        str(SCRIPTS_DIR / pipeline_script_name),
        "--run-dir",
        str(run_dir),
    ]
    if args.pipeline == "legacy":
        command.extend(
            [
                "--timeout-ms",
                str(args.timeout_ms),
                "--max-game-seconds",
                str(args.max_game_seconds),
            ]
        )

    with stdout_log.open("w", encoding="utf-8") as stdout_handle, stderr_log.open("w", encoding="utf-8") as stderr_handle:
        process = subprocess.Popen(
            command,
            stdout=stdout_handle,
            stderr=stderr_handle,
            env=env,
            start_new_session=True,
        )

    run_state_path = run_dir / "run_state.json"
    run_state = load_json(run_state_path)
    run_state["status"] = "created"
    run_state["current_phase"] = "batch_launched"
    run_state["accepted_at"] = run_state.get("accepted_at") or run_state.get("created_at")
    run_state["launcher"] = {
        "pid": process.pid,
        "command": command,
        "stdout_path": str(stdout_log.resolve()),
        "stderr_path": str(stderr_log.resolve()),
        "pipeline_mode": args.pipeline,
    }
    write_json(run_state_path, run_state)

    print_json(
        {
            "run_id": run_state["run_id"],
            "run_dir": str(run_dir),
            "status_path": str(run_state_path.resolve()),
            "dashboard_path": str((run_dir / "dashboard" / "index.html").resolve()),
            "output_root": str((run_dir / "output").resolve()),
            "status": run_state.get("status"),
            "current_phase": run_state.get("current_phase"),
            "accepted_at": run_state.get("accepted_at"),
            "pipeline_mode": args.pipeline,
            "launcher_pid": process.pid,
            "launcher_stdout_path": str(stdout_log.resolve()),
            "launcher_stderr_path": str(stderr_log.resolve()),
        }
    )


def handle_status(args: argparse.Namespace) -> None:
    run_dir = resolve_run_dir(args.run_id, args.run_dir)
    print_json(build_status_payload(run_dir))


def handle_output_path(args: argparse.Namespace) -> None:
    run_dir = resolve_run_dir(args.run_id, args.run_dir)
    print_json(build_result_payload(run_dir, include_games=args.include_games))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Game Obfuscator CLI wrapper.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    start_parser = subparsers.add_parser("start", help="Create a run, launch the pipeline in the background, and return immediately.")
    start_parser.add_argument("--manifest", required=True, help="Path to the input manifest JSON file.")
    start_parser.add_argument("--run-id", help="Optional explicit run id.")
    start_parser.add_argument(
        "--pipeline",
        choices=["simple", "legacy"],
        default="simple",
        help="Pipeline mode to launch. 'simple' is the new deterministic default; 'legacy' preserves the older multi-stage flow.",
    )
    start_parser.add_argument("--timeout-ms", type=int, default=8000, help="Playwright verification timeout in milliseconds.")
    start_parser.add_argument(
        "--max-game-seconds",
        type=int,
        default=300,
        help="Maximum allowed wall-clock time for one game during separate obfuscation.",
    )
    start_parser.set_defaults(func=handle_start)

    status_parser = subparsers.add_parser("status", help="Get canonical run status from run_state.json.")
    status_parser.add_argument("--run-id", help="Run id under runs/.")
    status_parser.add_argument("--run-dir", help="Explicit run directory path.")
    status_parser.set_defaults(func=handle_status)

    output_parser = subparsers.add_parser("output-path", help="Get final output path information for a run.")
    output_parser.add_argument("--run-id", help="Run id under runs/.")
    output_parser.add_argument("--run-dir", help="Explicit run directory path.")
    output_parser.add_argument(
        "--include-games",
        action="store_true",
        help="Include per-game output paths in the response.",
    )
    output_parser.set_defaults(func=handle_output_path)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()