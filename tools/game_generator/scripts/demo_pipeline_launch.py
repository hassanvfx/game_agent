#!/usr/bin/env python3
"""Cosmetic demo launcher for pipeline runs with immediate dashboard access."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PIPELINE_RUNS_DIR = ROOT / "pipeline_runs"
RUN_PIPELINE_SCRIPT = ROOT / "scripts" / "run_pipeline.py"
SERVE_DASHBOARD_SCRIPT = ROOT / "scripts" / "serve_pipeline_dashboard.py"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Launch a pipeline run, immediately serve its dashboard, and open a live watch URL."
    )
    parser.add_argument("prompt", help="Creative prompt for the pipeline run.")
    parser.add_argument(
        "--limit",
        type=int,
        default=2,
        help="Maximum number of matcher results to carry forward into refactoring.",
    )
    parser.add_argument(
        "--poll-seconds",
        type=float,
        default=5.0,
        help="Polling interval forwarded to scripts/run_pipeline.py.",
    )
    parser.add_argument(
        "--remix-prompt",
        help="Optional creative remix prompt override forwarded to scripts/run_pipeline.py.",
    )
    parser.add_argument(
        "--upload",
        action="store_true",
        help="Forward the upload flag to scripts/run_pipeline.py.",
    )
    parser.add_argument(
        "--publish",
        action="store_true",
        help="Forward the publish flag to scripts/run_pipeline.py.",
    )
    parser.add_argument(
        "--no-open",
        action="store_true",
        help="Do not auto-open the dashboard in the default browser.",
    )
    return parser.parse_args()


def list_run_dirs() -> set[str]:
    if not PIPELINE_RUNS_DIR.exists():
        return set()
    return {path.name for path in PIPELINE_RUNS_DIR.iterdir() if path.is_dir()}


def wait_for_new_run_id(before: set[str], timeout_seconds: float = 30.0) -> str:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        current = list_run_dirs()
        new_runs = sorted(current - before)
        if new_runs:
            return new_runs[-1]
        time.sleep(0.25)
    raise RuntimeError("Timed out while waiting for a new pipeline run directory to appear.")


def pick_dashboard_port(run_dir: Path) -> int:
    digest = hashlib.sha256(str(run_dir.resolve()).encode("utf-8")).hexdigest()
    return 8200 + (int(digest[:8], 16) % 500)


def launch_dashboard_server(run_id: str) -> subprocess.Popen[str]:
    return subprocess.Popen(
        [sys.executable, str(SERVE_DASHBOARD_SCRIPT), "--run-id", run_id],
        cwd=str(ROOT),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        text=True,
    )


def open_url(url: str) -> None:
    subprocess.Popen(["open", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def build_pipeline_command(args: argparse.Namespace) -> list[str]:
    command = [
        sys.executable,
        str(RUN_PIPELINE_SCRIPT),
        args.prompt,
        "--limit",
        str(args.limit),
        "--poll-seconds",
        str(args.poll_seconds),
    ]
    if args.remix_prompt:
        command.extend(["--remix-prompt", args.remix_prompt])
    if args.upload:
        command.append("--upload")
    if args.publish:
        command.append("--publish")
    return command


def main() -> int:
    PIPELINE_RUNS_DIR.mkdir(parents=True, exist_ok=True)

    args = parse_args()
    existing_runs = list_run_dirs()
    pipeline_command = build_pipeline_command(args)

    pipeline_process = subprocess.Popen(
        pipeline_command,
        cwd=str(ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    try:
        run_id = wait_for_new_run_id(existing_runs)
        run_dir = PIPELINE_RUNS_DIR / run_id
        port = pick_dashboard_port(run_dir)
        url = f"http://127.0.0.1:{port}/index.html"
        dashboard_process = launch_dashboard_server(run_id)

        print(f"run id: {run_id}", flush=True)
        print(f"run dir: {run_dir}", flush=True)
        print(f"watch live: {url}", flush=True)
        print(f"dashboard server pid: {dashboard_process.pid}", flush=True)

        if not args.no_open:
            open_url(url)

        assert pipeline_process.stdout is not None
        for line in pipeline_process.stdout:
            print(line, end="")

        return pipeline_process.wait()
    except KeyboardInterrupt:
        pipeline_process.terminate()
        try:
            return pipeline_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            pipeline_process.kill()
            return pipeline_process.wait()
    except Exception as exc:
        pipeline_process.terminate()
        try:
            pipeline_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            pipeline_process.kill()
            pipeline_process.wait()
        print(json.dumps({"status": "failed", "error": str(exc)}, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())