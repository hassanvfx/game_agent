#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLI_PATH = ROOT / "scripts" / "creative_refactor_cli.py"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def run_command(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI_PATH), *args],
        check=True,
        capture_output=True,
        text=True,
    )


def require_batch_cli_support() -> None:
    completed = subprocess.run(
        [sys.executable, str(CLI_PATH), "--help"],
        check=True,
        capture_output=True,
        text=True,
    )
    help_text = completed.stdout
    required_commands = ["start-batch", "status", "result"]
    missing = [command for command in required_commands if command not in help_text]
    if missing:
        raise RuntimeError(
            "creative_refactor_cli.py does not yet implement the manifest-driven batch commands required by this live test harness. "
            f"Missing commands: {', '.join(missing)}"
        )


def parse_json_output(completed: subprocess.CompletedProcess[str]) -> dict:
    stdout = completed.stdout.strip()
    if not stdout:
        raise RuntimeError("CLI returned empty stdout where JSON was expected.")
    return json.loads(stdout)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Live contract test harness for the manifest-driven creative refactor batch CLI."
    )
    parser.add_argument("--manifest", required=True, help="Manifest file to use for the live batch run.")
    parser.add_argument("--run-id", required=True, help="Explicit run id for the live test.")
    parser.add_argument("--style", default="neutral_prototype", help="Style preset to use.")
    parser.add_argument("--model", default="gpt-5.4", help="Model to use for the batch run.")
    parser.add_argument("--agent-timeout", type=int, default=900, help="Per-game worker timeout.")
    parser.add_argument("--max-concurrency", type=int, default=2, help="Maximum concurrent workers.")
    parser.add_argument("--poll-seconds", type=float, default=5.0, help="Status polling interval.")
    parser.add_argument("--stale-heartbeat-seconds", type=int, default=900, help="Stale heartbeat cutoff.")
    parser.add_argument("--status-timeout", type=int, default=1800, help="Maximum seconds to wait for terminal status.")
    parser.add_argument("--remix-prompt", default=None, help="Optional remix prompt.")
    parser.add_argument("--remix-prompt-file", default=None, help="Optional remix prompt file.")
    return parser.parse_args()


def build_start_args(args: argparse.Namespace) -> list[str]:
    start_args = [
        "start-batch",
        "--manifest",
        args.manifest,
        "--run-id",
        args.run_id,
        "--style",
        args.style,
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
    if args.remix_prompt and args.remix_prompt_file:
        raise ValueError("Pass only one of --remix-prompt or --remix-prompt-file.")
    if args.remix_prompt:
        start_args.extend(["--remix-prompt", args.remix_prompt])
    if args.remix_prompt_file:
        start_args.extend(["--remix-prompt-file", args.remix_prompt_file])
    return start_args


def assert_start_payload(payload: dict) -> None:
    required = ["run_id", "run_dir", "status_path", "dashboard_path", "output_root"]
    missing = [key for key in required if key not in payload]
    if missing:
        raise AssertionError(f"Start payload missing keys: {missing}")
    for key in ["run_dir", "status_path", "dashboard_path", "output_root"]:
        if not Path(payload[key]).exists() and key != "output_root":
            raise AssertionError(f"Expected path for {key} to exist: {payload[key]}")
    if not Path(payload["output_root"]).exists():
        raise AssertionError(f"Expected output_root to exist: {payload['output_root']}")


def assert_status_payload(payload: dict, run_id: str) -> None:
    required = [
        "run_id",
        "run_dir",
        "status",
        "current_phase",
        "updated_at",
        "games_total",
        "games_transform_completed",
        "games_transform_failed",
        "dashboard_path",
        "output_root",
        "completed",
    ]
    missing = [key for key in required if key not in payload]
    if missing:
        raise AssertionError(f"Status payload missing keys: {missing}")
    if payload["run_id"] != run_id:
        raise AssertionError(f"Unexpected run_id in status payload: {payload['run_id']} != {run_id}")


def assert_result_payload(payload: dict, run_id: str) -> None:
    required = ["run_id", "status", "run_dir", "dashboard_path", "output_root", "final_output_dirs"]
    missing = [key for key in required if key not in payload]
    if missing:
        raise AssertionError(f"Result payload missing keys: {missing}")
    if payload["run_id"] != run_id:
        raise AssertionError(f"Unexpected run_id in result payload: {payload['run_id']} != {run_id}")
    if not Path(payload["run_dir"]).exists():
        raise AssertionError(f"run_dir does not exist: {payload['run_dir']}")
    if not Path(payload["dashboard_path"]).exists():
        raise AssertionError(f"dashboard_path does not exist: {payload['dashboard_path']}")
    if not Path(payload["output_root"]).exists():
        raise AssertionError(f"output_root does not exist: {payload['output_root']}")
    for output_dir in payload["final_output_dirs"]:
        if not Path(output_dir).exists():
            raise AssertionError(f"final output directory does not exist: {output_dir}")


def wait_for_terminal_status(run_id: str, poll_seconds: float, status_timeout: int) -> dict:
    deadline = time.time() + status_timeout
    while time.time() < deadline:
        status_payload = parse_json_output(run_command("--json", "status", "--run-id", run_id))
        assert_status_payload(status_payload, run_id)
        if status_payload["completed"]:
            return status_payload
        time.sleep(max(0.2, poll_seconds))
    raise TimeoutError(f"Timed out waiting for terminal status for run_id={run_id}")


def main() -> None:
    args = parse_args()
    require_batch_cli_support()

    start_payload = parse_json_output(run_command("--json", *build_start_args(args)))
    assert_start_payload(start_payload)

    status_payload = wait_for_terminal_status(args.run_id, args.poll_seconds, args.status_timeout)
    result_payload = parse_json_output(run_command("--json", "result", "--run-id", args.run_id))
    assert_result_payload(result_payload, args.run_id)

    summary = {
        "start": start_payload,
        "final_status": status_payload,
        "result": result_payload,
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()