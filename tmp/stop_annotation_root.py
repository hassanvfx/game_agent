#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from serve_annotation_root import kill_existing_port_users, kill_pid_file_process, pid_file_path

ROOT = Path("/Users/hassan/repos/game_agent")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Stop a managed annotation root server.")
    parser.add_argument("--root", choices=["public", "obfuscated"], required=True)
    parser.add_argument("--port", type=int, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    kill_pid_file_process(args.root)
    kill_existing_port_users(args.port)
    pid_path = pid_file_path(args.root)
    pid_path.unlink(missing_ok=True)
    print(
        json.dumps(
            {
                "root": args.root,
                "port": args.port,
                "pid_file": str(pid_path),
                "stopped": True,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()