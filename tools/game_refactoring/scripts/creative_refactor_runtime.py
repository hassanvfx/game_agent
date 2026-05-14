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


PROJECTED_PRICING_USD_PER_MILLION = {
    "inputTokens": 5.00,
    "cacheReadTokens": 0.50,
    "outputTokens": 30.00,
    "cacheWriteTokens": 0.00,
}


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
    run_result_event: dict[str, Any] | None
    usage_summary: dict[str, Any] | None

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


def parse_cline_run_result_event(stdout_text: str) -> dict[str, Any] | None:
    last_run_result: dict[str, Any] | None = None
    for raw_line in stdout_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict) and payload.get("type") == "run_result":
            last_run_result = payload
    return last_run_result


def normalize_cline_usage_summary(run_result_event: dict[str, Any] | None) -> dict[str, Any] | None:
    if not run_result_event:
        return None

    aggregate_usage = run_result_event.get("aggregateUsage")
    usage = run_result_event.get("usage")
    usage_payload = aggregate_usage if isinstance(aggregate_usage, dict) else usage if isinstance(usage, dict) else {}
    model_payload = run_result_event.get("model") if isinstance(run_result_event.get("model"), dict) else {}
    normalized_usage = {
        "inputTokens": usage_payload.get("inputTokens", 0),
        "outputTokens": usage_payload.get("outputTokens", 0),
        "cacheReadTokens": usage_payload.get("cacheReadTokens", 0),
        "cacheWriteTokens": usage_payload.get("cacheWriteTokens", 0),
        "totalCost": usage_payload.get("totalCost", 0),
    }
    projected_cost_breakdown = {
        key: round((normalized_usage.get(key, 0) / 1_000_000) * rate, 6)
        for key, rate in PROJECTED_PRICING_USD_PER_MILLION.items()
    }
    projected_cost_total = round(sum(projected_cost_breakdown.values()), 6)
    total_tokens = normalized_usage["inputTokens"] + normalized_usage["outputTokens"]
    total_tokens_including_cache = total_tokens + normalized_usage["cacheReadTokens"] + normalized_usage["cacheWriteTokens"]

    return {
        "source_event_type": "run_result",
        "finishReason": run_result_event.get("finishReason"),
        "iterations": run_result_event.get("iterations"),
        "durationMs": run_result_event.get("durationMs"),
        "provider": model_payload.get("provider"),
        "model": model_payload.get("id"),
        "usage": normalized_usage,
        "tokenTotals": {
            "totalTokens": total_tokens,
            "totalTokensIncludingCache": total_tokens_including_cache,
        },
        "projectedCost": {
            "currency": "USD",
            "pricingBasis": "GPT-5.5 standard API pricing",
            "ratesPerMillionTokens": PROJECTED_PRICING_USD_PER_MILLION,
            "breakdown": projected_cost_breakdown,
            "total": projected_cost_total,
        },
    }


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
    stdout_text = "".join(stdout_chunks)
    stderr_text = "".join(stderr_chunks)
    run_result_event = parse_cline_run_result_event(stdout_text)
    usage_summary = normalize_cline_usage_summary(run_result_event)
    return WorkerExecutionResult(
        command=command,
        pid=process.pid,
        returncode=returncode,
        stdout_text=stdout_text,
        stderr_text=stderr_text,
        timed_out=timed_out,
        started_at=started_at,
        finished_at=finished_at,
        duration_seconds=round(iso_to_timestamp(finished_at) - iso_to_timestamp(started_at), 3),
        run_result_event=run_result_event,
        usage_summary=usage_summary,
    )


def update_json_file(path: Path, mutator: Callable[[dict[str, Any]], None]) -> None:
    payload = load_json(path)
    mutator(payload)
    write_json(path, payload)