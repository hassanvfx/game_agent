#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from orchestration_state import load_json, write_json

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"


def run_python_script(
    script_name: str,
    *args: str,
    env: dict[str, str] | None = None,
    python_executable: str | None = None,
) -> None:
    import subprocess

    executable = python_executable or sys.executable
    command = [executable, str(SCRIPTS_DIR / script_name), *args]
    result = subprocess.run(command, capture_output=True, text=True, env=env)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or f"Stage failed: {script_name}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Game Obfuscator pipeline for an existing run directory.")
    parser.add_argument("--run-dir", required=True, help="Path to the existing run directory.")
    parser.add_argument(
        "--timeout-ms",
        type=int,
        default=8000,
        help="Playwright verification timeout in milliseconds.",
    )
    parser.add_argument(
        "--max-game-seconds",
        type=int,
        default=300,
        help="Maximum allowed wall-clock time for one game during separate obfuscation.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_dir = Path(args.run_dir).resolve()
    if not run_dir.exists():
        raise SystemExit(f"Run directory does not exist: {run_dir}")

    venv_python = ROOT / ".venv" / "bin" / "python"
    python_executable = str(venv_python) if venv_python.exists() else sys.executable

    run_state_path = run_dir / "run_state.json"
    run_state = load_json(run_state_path)
    run_state["status"] = "running"
    run_state["current_phase"] = "pipeline_launching"
    run_state["launcher"] = {
        **run_state.get("launcher", {}),
        "pipeline_script": str((SCRIPTS_DIR / "run_game_obfuscator_pipeline.py").resolve()),
        "python_executable": python_executable,
    }
    write_json(run_state_path, run_state)

    stage_scripts = [
        "prepare_inputs.py",
        "analyze_inputs.py",
        "plan_rewrites.py",
        "apply_rewrites.py",
        "bundle_outputs.py",
    ]

    try:
        for script_name in stage_scripts:
            run_state = load_json(run_state_path)
            run_state["status"] = "running"
            run_state["current_phase"] = script_name.removesuffix(".py")
            write_json(run_state_path, run_state)
            run_python_script(script_name, "--run-dir", str(run_dir), python_executable=python_executable)

        env = dict(os.environ)
        existing_pythonpath = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = str(SCRIPTS_DIR) if not existing_pythonpath else f"{SCRIPTS_DIR}:{existing_pythonpath}"
        env["GAME_OBFUSCATOR_PYTHON"] = python_executable

        run_state = load_json(run_state_path)
        run_state["status"] = "running"
        run_state["current_phase"] = "obfuscate_separate_outputs"
        write_json(run_state_path, run_state)

        run_python_script(
            "obfuscate_separate_outputs.py",
            "--run-dir",
            str(run_dir),
            "--timeout-ms",
            str(args.timeout_ms),
            "--max-game-seconds",
            str(args.max_game_seconds),
            env=env,
            python_executable=python_executable,
        )
    except Exception as exc:
        run_state = load_json(run_state_path)
        run_state["status"] = "failed"
        run_state["current_phase"] = "pipeline_failed"
        run_state["last_error"] = str(exc)
        write_json(run_state_path, run_state)
        raise

    run_state = load_json(run_state_path)
    launcher = {
        **run_state.get("launcher", {}),
        "completed_by_pipeline_wrapper": True,
    }
    run_state["launcher"] = launcher
    write_json(run_state_path, run_state)


if __name__ == "__main__":
    main()