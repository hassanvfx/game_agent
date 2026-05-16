#!/usr/bin/env python3
"""Serve the game generator simulator with a simple local HTTP server."""

from __future__ import annotations

import argparse
import http.server
import socketserver
import webbrowser
from pathlib import Path


class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Serve index.html for the standalone game matcher locally.")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to.")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to.")
    parser.add_argument(
        "--no-open",
        action="store_true",
        help="Do not automatically open the browser.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(__file__).resolve().parent

    handler = http.server.SimpleHTTPRequestHandler
    with ReusableTCPServer((args.host, args.port), handler) as httpd:
        httpd.directory = str(root)
        url = f"http://{args.host}:{args.port}/index.html"
        print(f"Serving {root} at {url}", flush=True)
        if not args.no_open:
            webbrowser.open(url)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())