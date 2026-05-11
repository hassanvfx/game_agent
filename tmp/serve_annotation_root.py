#!/usr/bin/env python3
from __future__ import annotations

import argparse
import http.server
import json
import os
import signal
import socketserver
import subprocess
import sys
from pathlib import Path

ROOT = Path("/Users/hassan/repos/game_agent")
PUBLIC_ROOT = ROOT / "games" / "published" / "public"
OBFUSCATED_ROOT = ROOT / "games" / "published" / "obfuscated"
PID_ROOT = ROOT / "tmp" / "annotation_servers"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Serve an annotation root on an exclusive fixed port with PID-file management."
    )
    parser.add_argument("--root", choices=["public", "obfuscated"], required=True)
    parser.add_argument("--port", type=int, required=True)
    return parser.parse_args()


def resolve_root(root_name: str) -> Path:
    if root_name == "public":
        return PUBLIC_ROOT
    if root_name == "obfuscated":
        return OBFUSCATED_ROOT
    raise ValueError(f"Unsupported root: {root_name}")


def pid_file_path(root_name: str) -> Path:
    PID_ROOT.mkdir(parents=True, exist_ok=True)
    return PID_ROOT / f"{root_name}.pid"


def process_exists(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def terminate_pid(pid: int) -> None:
    if not process_exists(pid):
        return
    try:
        os.kill(pid, signal.SIGTERM)
    except OSError:
        return
    subprocess.run(["sleep", "1"], check=False)
    if process_exists(pid):
        try:
            os.kill(pid, signal.SIGKILL)
        except OSError:
            return


def kill_pid_file_process(root_name: str) -> None:
    pid_path = pid_file_path(root_name)
    if not pid_path.exists():
        return
    try:
        pid = int(pid_path.read_text(encoding="utf-8").strip())
    except ValueError:
        pid_path.unlink(missing_ok=True)
        return
    terminate_pid(pid)
    pid_path.unlink(missing_ok=True)


def kill_existing_port_users(port: int) -> None:
    completed = subprocess.run(
        ["lsof", "-ti", f"tcp:{port}"],
        capture_output=True,
        text=True,
        check=False,
    )
    pids = [line.strip() for line in completed.stdout.splitlines() if line.strip()]
    for pid_text in pids:
        try:
            terminate_pid(int(pid_text))
        except ValueError:
            continue


def write_pid_file(root_name: str) -> Path:
    pid_path = pid_file_path(root_name)
    pid_path.write_text(str(os.getpid()) + "\n", encoding="utf-8")
    return pid_path


def build_handler(directory: Path):
    return lambda *args, **kwargs: http.server.SimpleHTTPRequestHandler(
        *args,
        directory=str(directory),
        **kwargs,
    )


def main() -> None:
    args = parse_args()
    directory = resolve_root(args.root)
    port = args.port

    kill_pid_file_process(args.root)
    kill_existing_port_users(port)

    handler = build_handler(directory)

    class ReusableTCPServer(socketserver.TCPServer):
        allow_reuse_address = True

    httpd = ReusableTCPServer(("0.0.0.0", port), handler)
    pid_path = write_pid_file(args.root)

    def shutdown_handler(signum, frame):  # type: ignore[unused-argument]
        httpd.shutdown()

    signal.signal(signal.SIGTERM, shutdown_handler)
    signal.signal(signal.SIGINT, shutdown_handler)

    annotator_url = f"http://127.0.0.1:{port}/565a0bf4-5160-47b8-a905-2f4362475cdf-annotator.html"
    print(
        json.dumps(
            {
                "root": args.root,
                "directory": str(directory),
                "port": port,
                "pid_file": str(pid_path),
                "annotator_url": annotator_url,
            },
            indent=2,
        )
    )
    try:
        httpd.serve_forever()
    finally:
        httpd.server_close()
        pid_path.unlink(missing_ok=True)


if __name__ == "__main__":
    main()