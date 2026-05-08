#!/usr/bin/env python3
from __future__ import annotations

import argparse
import functools
import http.server
import socketserver
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Serve a downloader run dashboard locally.")
    parser.add_argument("--run-id", required=True, help="Run id under runs/.")
    parser.add_argument("--port", type=int, default=8123, help="Port to bind.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(__file__).resolve().parents[1]
    dashboard_dir = root / "runs" / args.run_id / "dashboard"
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(dashboard_dir))
    with socketserver.TCPServer(("127.0.0.1", args.port), handler) as httpd:
        print(f"http://127.0.0.1:{args.port}/")
        httpd.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
