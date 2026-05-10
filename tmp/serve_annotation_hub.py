#!/usr/bin/env python3
from __future__ import annotations

import argparse
import http.server
import os
import signal
import socketserver
import subprocess
import sys
from pathlib import Path

ROOT = Path("/Users/hassan/repos/game_agent")
PUBLIC_ROOT = ROOT / "games" / "published" / "public"
DEFAULT_PORT = 8787


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Serve the annotation hub on an exclusive fixed port and release that port on exit."
    )
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"Port to bind. Defaults to {DEFAULT_PORT}.")
    return parser.parse_args()


def kill_existing_port_users(port: int) -> None:
    completed = subprocess.run(
        ["lsof", "-ti", f"tcp:{port}"],
        capture_output=True,
        text=True,
        check=False,
    )
    pids = [line.strip() for line in completed.stdout.splitlines() if line.strip()]
    for pid in pids:
        subprocess.run(["kill", "-TERM", pid], check=False)
    if pids:
        subprocess.run(["sleep", "1"], check=False)
        for pid in pids:
            subprocess.run(["kill", "-KILL", pid], check=False)


def build_handler():
    return lambda *args, **kwargs: http.server.SimpleHTTPRequestHandler(
        *args,
        directory=str(PUBLIC_ROOT),
        **kwargs,
    )


def main() -> None:
    args = parse_args()
    port = args.port
    kill_existing_port_users(port)

    handler = build_handler()

    class ReusableTCPServer(socketserver.TCPServer):
        allow_reuse_address = True

    httpd = ReusableTCPServer(("0.0.0.0", port), handler)

    def shutdown_handler(signum, frame):  # type: ignore[unused-argument]
        httpd.shutdown()

    signal.signal(signal.SIGTERM, shutdown_handler)
    signal.signal(signal.SIGINT, shutdown_handler)

    print(f"Serving annotation hub from {PUBLIC_ROOT} on http://127.0.0.1:{port}/565a0bf4-5160-47b8-a905-2f4362475cdf-annotator.html")
    try:
        httpd.serve_forever()
    finally:
        httpd.server_close()


if __name__ == "__main__":
    main()