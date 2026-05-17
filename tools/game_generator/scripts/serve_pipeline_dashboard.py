#!/usr/bin/env python3
"""Serve a pipeline run dashboard over HTTP."""

from __future__ import annotations

import argparse
import hashlib
import http.server
import json
import os
import signal
import socketserver
import subprocess
import time
from pathlib import Path

from pipeline_dashboard_presenter import (
    build_dashboard_contract_extensions,
    generate_dashboard_html,
    resolve_dashboard_request_path,
)

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


def refresh_dashboard_assets(run_dir: Path, dashboard_dir: Path) -> None:
    dashboard_data_path = dashboard_dir / "dashboard_data.json"
    if dashboard_data_path.exists():
        payload = json.loads(dashboard_data_path.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            enriched_payload = {
                **payload,
                **build_dashboard_contract_extensions(run_dir, payload),
            }
            dashboard_data_path.write_text(
                json.dumps(enriched_payload, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
    (dashboard_dir / "index.html").write_text(generate_dashboard_html(), encoding="utf-8")


class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


class DashboardRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, run_dir: Path, directory: str, **kwargs):
        self.run_dir = run_dir
        super().__init__(*args, directory=directory, **kwargs)

    def do_GET(self) -> None:
        resolved_path = resolve_dashboard_request_path(self.run_dir, self.path)
        if resolved_path is not None:
            self.send_response(200)
            self.send_header("Content-type", self.guess_type(str(resolved_path)))
            self.send_header("Content-Length", str(resolved_path.stat().st_size))
            self.end_headers()
            with resolved_path.open("rb") as handle:
                self.wfile.write(handle.read())
            return
        super().do_GET()


def main() -> int:
    args = parse_args()
    run_dir = resolve_run_dir(args.run_dir, args.run_id)
    dashboard_dir = run_dir / "dashboard"
    if not dashboard_dir.exists():
        raise SystemExit(f"dashboard directory not found: {dashboard_dir}")
    refresh_dashboard_assets(run_dir, dashboard_dir)

    port = args.port or pick_dashboard_port(run_dir)
    replaced_pids = kill_processes_on_port(port)

    handler = lambda *handler_args, **handler_kwargs: DashboardRequestHandler(
        *handler_args,
        run_dir=run_dir,
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