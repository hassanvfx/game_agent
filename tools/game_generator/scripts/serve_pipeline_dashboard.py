#!/usr/bin/env python3
"""Serve a pipeline run dashboard over HTTP."""

from __future__ import annotations

import argparse
import hashlib
import http.server
import os
import signal
import socketserver
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PIPELINE_RUNS_DIR = ROOT / "pipeline_runs"


def resolve_run_dir(run_dir: str | None, run_id: str | None) -> Path:
    if run_dir:
        return Path(run_dir).resolve()
    if run_id:
        return (PIPELINE_RUNS_DIR / run_id).resolve()
    raise ValueError("pass either --run-dir or --run-id")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Serve a pipeline dashboard over local HTTP.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--run-dir", help="Absolute or relative pipeline run directory.")
    group.add_argument("--run-id", help="Pipeline run id under pipeline_runs/.")
    parser.add_argument("--port", type=int, help="Override the deterministic local HTTP port.")
    return parser.parse_args()


def pick_dashboard_port(run_dir: Path) -> int:
    digest = hashlib.sha256(str(run_dir).encode("utf-8")).hexdigest()
    return 8200 + (int(digest[:8], 16) % 500)


def find_pids_on_port(port: int) -> list[int]:
    completed = subprocess.run(
        ["lsof", "-ti", f"tcp:{port}"],
        capture_output=True,
        text=True,
        check=False,
    )
    pids: list[int] = []
    for line in completed.stdout.splitlines():
        value = line.strip()
        if value.isdigit():
            pids.append(int(value))
    return sorted(set(pids))


def wait_for_port_to_clear(port: int, timeout_seconds: float) -> bool:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        if not find_pids_on_port(port):
            return True
        time.sleep(0.1)
    return not find_pids_on_port(port)


def kill_processes_on_port(port: int) -> list[int]:
    pids = find_pids_on_port(port)
    if not pids:
        return []

    for pid in pids:
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            continue

    if wait_for_port_to_clear(port, timeout_seconds=1.5):
        return pids

    remaining = find_pids_on_port(port)
    for pid in remaining:
        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            continue

    wait_for_port_to_clear(port, timeout_seconds=1.0)
    return pids


class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


def main() -> int:
    args = parse_args()
    run_dir = resolve_run_dir(args.run_dir, args.run_id)
    dashboard_dir = run_dir / "dashboard"
    if not dashboard_dir.exists():
        raise SystemExit(f"dashboard directory not found: {dashboard_dir}")

    port = args.port or pick_dashboard_port(run_dir)
    replaced_pids = kill_processes_on_port(port)

    handler = lambda *handler_args, **handler_kwargs: http.server.SimpleHTTPRequestHandler(
        *handler_args,
        directory=str(dashboard_dir),
        **handler_kwargs,
    )

    if find_pids_on_port(port):
        raise SystemExit(f"port {port} is still in use after attempted eviction")

    with ReusableTCPServer(("127.0.0.1", port), handler) as httpd:
        if replaced_pids:
            print(f"Replaced existing process(es) on port {port}: {', '.join(str(pid) for pid in replaced_pids)}.")
        print(f"Serving dashboard for {run_dir.name} at http://127.0.0.1:{port}/index.html")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())