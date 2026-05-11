#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve()
TOOL_ROOT = SCRIPT_PATH.parents[1]
REPO_ROOT = TOOL_ROOT.parents[1]

DEFAULT_PUBLIC_ROOT = REPO_ROOT / "games" / "published" / "public"
DEFAULT_OBFUSCATED_ROOT = REPO_ROOT / "games" / "published" / "obfuscated"
ANNOTATOR_ENTRY_UUID = "9f1c3b7e-6a2d-4d55-a2b8"
ANNOTATOR_ENTRY_NAME = f"{ANNOTATOR_ENTRY_UUID}-annotator.html"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 43177
STARTUP_TIMEOUT_SECONDS = 10.0
POLL_INTERVAL_SECONDS = 0.2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Launch the published annotator dashboard with an exclusive local HTTP server."
    )
    parser.add_argument(
        "--target",
        choices=("public", "obfuscated"),
        default="public",
        help="Which published root should be served.",
    )
    parser.add_argument(
        "--public-root",
        default=str(DEFAULT_PUBLIC_ROOT),
        help="Published public root.",
    )
    parser.add_argument(
        "--obfuscated-root",
        default=str(DEFAULT_OBFUSCATED_ROOT),
        help="Published obfuscated root.",
    )
    parser.add_argument(
        "--entry-name",
        default=ANNOTATOR_ENTRY_NAME,
        help="Annotator entry filename to open.",
    )
    parser.add_argument(
        "--host",
        default=DEFAULT_HOST,
        help="HTTP server host.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help="Exclusive HTTP server port.",
    )
    parser.add_argument(
        "--open-browser",
        action="store_true",
        help="Open the annotator URL in the default browser after the server is ready.",
    )
    return parser


def read_pid(pid_file: Path) -> int | None:
    try:
        value = pid_file.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return None
    if not value:
        return None
    try:
        return int(value)
    except ValueError:
        return None


def pid_is_running(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def terminate_existing_server(pid_file: Path, *, target_label: str) -> None:
    existing_pid = read_pid(pid_file)
    if existing_pid is None:
        return

    if not pid_is_running(existing_pid):
        pid_file.unlink(missing_ok=True)
        return

    print(f"[annotator] releasing exclusive port by stopping previous {target_label} server pid={existing_pid}")
    os.kill(existing_pid, signal.SIGTERM)

    deadline = time.time() + 5.0
    while time.time() < deadline:
        if not pid_is_running(existing_pid):
            pid_file.unlink(missing_ok=True)
            print(f"[annotator] released pid={existing_pid}")
            return
        time.sleep(0.1)

    print(f"[annotator] pid={existing_pid} did not exit after SIGTERM; sending SIGKILL")
    os.kill(existing_pid, signal.SIGKILL)

    deadline = time.time() + 2.0
    while time.time() < deadline:
        if not pid_is_running(existing_pid):
            pid_file.unlink(missing_ok=True)
            print(f"[annotator] released pid={existing_pid}")
            return
        time.sleep(0.1)

    raise SystemExit(f"Could not release previous annotator server pid={existing_pid}")


def wait_for_http_ready(url: str, *, timeout_seconds: float) -> None:
    deadline = time.time() + timeout_seconds
    last_error: Exception | None = None

    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=1.0) as response:
                if 200 <= response.status < 500:
                    return
        except urllib.error.URLError as exc:
            last_error = exc
        except Exception as exc:  # pragma: no cover - defensive
            last_error = exc
        time.sleep(POLL_INTERVAL_SECONDS)

    if last_error is None:
        raise SystemExit(f"Timed out waiting for annotator server readiness at {url}")
    raise SystemExit(f"Timed out waiting for annotator server readiness at {url}: {last_error}")


def main() -> None:
    args = build_parser().parse_args()

    root = Path(args.public_root if args.target == "public" else args.obfuscated_root).resolve()
    entry_name = str(args.entry_name)
    entry_path = root / entry_name

    if not root.is_dir():
        raise SystemExit(f"Published root does not exist: {root}")
    if not entry_path.is_file():
        raise SystemExit(f"Annotator entry does not exist: {entry_path}")

    pid_file = root / ".annotator_server_pid"
    port_file = root / ".annotator_server_port"
    log_file = root / ".annotator_server.log"

    terminate_existing_server(pid_file, target_label=args.target)

    port_file.write_text(f"{args.port}\n", encoding="utf-8")
    server_command = [
        sys.executable,
        "-m",
        "http.server",
        str(args.port),
        "--bind",
        args.host,
    ]

    print(f"[annotator] target={args.target}")
    print(f"[annotator] root={root}")
    print(f"[annotator] entry={entry_path}")
    print(f"[annotator] log_file={log_file}")
    print(f"[annotator] starting server on exclusive port {args.port}")

    with log_file.open("w", encoding="utf-8") as log_handle:
        process = subprocess.Popen(
            server_command,
            cwd=root,
            stdout=log_handle,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )

    pid_file.write_text(f"{process.pid}\n", encoding="utf-8")

    annotator_url = f"http://{args.host}:{args.port}/{entry_name}"
    wait_for_http_ready(annotator_url, timeout_seconds=STARTUP_TIMEOUT_SECONDS)

    print(f"[annotator] server ready pid={process.pid}")
    print(f"[annotator] dashboard={annotator_url}")
    print(f"[annotator] tail logs with: tail -f {log_file}")

    if args.open_browser:
        open_command = ["open", annotator_url]
        subprocess.run(open_command, check=True)
        print(f"[annotator] browser opened for {annotator_url}")
    else:
        print("[annotator] browser not opened automatically; re-run with --open-browser if desired")

    print("[annotator] server will keep running until replaced by a new launch or manually stopped")


if __name__ == "__main__":
    main()