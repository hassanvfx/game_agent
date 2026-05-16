#!/usr/bin/env python3
from __future__ import annotations

import argparse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Serve Game Remixer runs from the remixer root.")
    parser.add_argument("--port", type=int, default=8058)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    handler = lambda *a, **kw: SimpleHTTPRequestHandler(*a, directory=str(ROOT), **kw)
    server = ThreadingHTTPServer(("127.0.0.1", args.port), handler)
    print(f"Serving Game Remixer from {ROOT} at http://127.0.0.1:{args.port}/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()