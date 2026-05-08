#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import signal
import subprocess
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def iso_to_timestamp(value: str) -> float:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()


def stream_reader(stream, destination: Path, sink: list[str]) -> None:
    with destination.open("w", encoding="utf-8") as handle:
        for line in iter(stream.readline, ""):
            handle.write(line)
            handle.flush()
            sink.append(line)
    stream.close()


@dataclass
class WorkerExecutionResult:
    command: list[str]
    pid: int
    returncode: int
    stdout_text: str
    stderr_text: str
    timed_out: bool
    started_at: str
    finished_at: str
    duration_seconds: float

    @property
    def status(self) -> str:
        if self.timed_out:
            return "timeout"
        return "completed" if self.returncode == 0 else "failed"

    @property
    def stdout_bytes(self) -> int:
        return len(self.stdout_text.encode("utf-8"))

    @property
    def stderr_bytes(self) -> int:
        return len(self.stderr_text.encode("utf-8"))


def execute_worker_command(
    command: list[str],
    cwd: Path,
    stdout_path: Path,
    stderr_path: Path,
    timeout_seconds: int | None,
    heartbeat_callback: Callable[[], None] | None = None,
    heartbeat_interval_seconds: float = 5.0,
) -> WorkerExecutionResult:
    env = os.environ.copy()
    env.setdefault("NODE_PATH", "/Users/hassan/.nvm/versions/node/v24.15.0/lib/node_modules")

    process = subprocess.Popen(
        command,
        cwd=str(cwd),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=1,
        start_new_session=True,
        env=env,
    )

    stdout_chunks: list[str] = []
    stderr_chunks: list[str] = []

    stdout_thread = threading.Thread(
        target=stream_reader,
        args=(process.stdout, stdout_path, stdout_chunks),
        daemon=True,
    )
    stderr_thread = threading.Thread(
        target=stream_reader,
        args=(process.stderr, stderr_path, stderr_chunks),
        daemon=True,
    )
    stdout_thread.start()
    stderr_thread.start()

    started_at = utc_now()
    timed_out = False

    stop_heartbeat = threading.Event()
    heartbeat_thread: threading.Thread | None = None
    if heartbeat_callback is not None:

        def heartbeat_loop() -> None:
            while not stop_heartbeat.wait(heartbeat_interval_seconds):
                heartbeat_callback()

        heartbeat_thread = threading.Thread(target=heartbeat_loop, daemon=True)
        heartbeat_thread.start()

    try:
        returncode = process.wait(timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        timed_out = True
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        returncode = process.wait()
    finally:
        stop_heartbeat.set()
        if heartbeat_thread is not None:
            heartbeat_thread.join(timeout=1.0)

    stdout_thread.join(timeout=5.0)
    stderr_thread.join(timeout=5.0)

    finished_at = utc_now()
    return WorkerExecutionResult(
        command=command,
        pid=process.pid,
        returncode=returncode,
        stdout_text="".join(stdout_chunks),
        stderr_text="".join(stderr_chunks),
        timed_out=timed_out,
        started_at=started_at,
        finished_at=finished_at,
        duration_seconds=round(iso_to_timestamp(finished_at) - iso_to_timestamp(started_at), 3),
    )


def update_json_file(path: Path, mutator: Callable[[dict[str, Any]], None]) -> None:
    payload = load_json(path)
    mutator(payload)
    write_json(path, payload)