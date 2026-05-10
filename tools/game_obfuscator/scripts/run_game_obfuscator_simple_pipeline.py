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
    parser = argparse.ArgumentParser(
        description="Run the simple deterministic Game Obfuscator pipeline for an existing run directory."
    )
    parser.add_argument("--run-dir", required=True, help="Path to the existing run directory.")
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
    run_state["current_phase"] = "simple_pipeline_launching"
    run_state["launcher"] = {
        **run_state.get("launcher", {}),
        "pipeline_script": str((SCRIPTS_DIR / "run_game_obfuscator_simple_pipeline.py").resolve()),
        "python_executable": python_executable,
        "pipeline_mode": "simple",
    }
    write_json(run_state_path, run_state)

    stage_scripts = [
        "prepare_inputs.py",
        "obfuscate_simple_outputs.py",
    ]

    try:
        env = dict(os.environ)
        existing_pythonpath = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = str(SCRIPTS_DIR) if not existing_pythonpath else f"{SCRIPTS_DIR}:{existing_pythonpath}"
        env["GAME_OBFUSCATOR_PYTHON"] = python_executable

        for script_name in stage_scripts:
            run_state = load_json(run_state_path)
            run_state["status"] = "running"
            run_state["current_phase"] = script_name.removesuffix(".py")
            write_json(run_state_path, run_state)
            run_python_script(script_name, "--run-dir", str(run_dir), env=env, python_executable=python_executable)
    except Exception as exc:
        run_state = load_json(run_state_path)
        run_state["status"] = "failed"
        run_state["current_phase"] = "simple_pipeline_failed"
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