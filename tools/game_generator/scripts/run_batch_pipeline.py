#!/usr/bin/env python3
"""Durable serial batch launcher for run_pipeline.py."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from batch_pipeline_state import (
    BATCH_RUNS_DIR,
    CHILD_RUN_TERMINAL_STATUSES,
    PIPELINE_RUNS_DIR,
    BatchRun,
    read_json,
)
from upload_auth_preflight import DEFAULT_GCLOUD_PROJECT, run_gcloud_auth_preflight


ROOT = Path(__file__).resolve().parent.parent
RUN_PIPELINE_SCRIPT = ROOT / "scripts" / "run_pipeline.py"


def print_batch(message: str) -> None:
    print(f"[batch] {message}", flush=True)


def get_item_progress(batch: BatchRun, item_id: str) -> tuple[int, int]:
    item_order = batch.read_state().get("item_order", [])
    if item_id in item_order:
        return item_order.index(item_id) + 1, len(item_order)
    return 0, len(item_order)


def describe_item(batch: BatchRun, item: dict[str, Any]) -> str:
    current, total = get_item_progress(batch, str(item.get("item_id")))
    return f"[{current}/{total}] {item.get('item_id')}"


def extract_clickable_urls(child_state: dict[str, Any]) -> list[str]:
    urls: list[str] = []
    for entry in child_state.get("projected_cdn_urls", []) or []:
        if not isinstance(entry, dict):
            continue
        for key in ("public_cdn_url", "play_cdn_url"):
            value = entry.get(key)
            if isinstance(value, str) and value and value not in urls:
                urls.append(value)
    return urls


def print_item_launch(batch: BatchRun, item: dict[str, Any]) -> None:
    descriptor = describe_item(batch, item)
    print_batch(f"{descriptor} launching")
    print_batch(f"prompt: {item.get('prompt', '')}")


def print_child_detected(batch: BatchRun, item: dict[str, Any], run_id: str) -> None:
    descriptor = describe_item(batch, item)
    print_batch(f"{descriptor} child run_id: {run_id}")
    if item.get("pipeline_run_dir"):
        print_batch(f"run dir: {item['pipeline_run_dir']}")


def print_child_transition(batch: BatchRun, item: dict[str, Any], child_state: dict[str, Any]) -> None:
    descriptor = describe_item(batch, item)
    status = child_state.get("status") or item.get("pipeline_status") or "unknown"
    current_step = child_state.get("current_step") or item.get("current_step") or "unknown"
    print_batch(f"{descriptor} status={status} step={current_step}")


def print_item_terminal(batch: BatchRun, item: dict[str, Any], child_state: dict[str, Any]) -> None:
    descriptor = describe_item(batch, item)
    status = child_state.get("status") or "unknown"
    print_batch(f"{descriptor} completed with status={status}")
    dashboard_path = child_state.get("artifacts", {}).get("dashboard_path")
    if isinstance(dashboard_path, str) and dashboard_path:
        print_batch(f"dashboard: {dashboard_path}")
    final_output_dir = child_state.get("final_output_dir")
    if isinstance(final_output_dir, str) and final_output_dir:
        print_batch(f"final output: {final_output_dir}")
    for url in extract_clickable_urls(child_state):
        print_batch(f"live url: {url}")
    if child_state.get("error"):
        print_batch(f"error: {json.dumps(child_state['error'], ensure_ascii=False)}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a durable serial batch of pipeline prompts from a manifest.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--manifest", help="Path to a new batch manifest JSON file.")
    group.add_argument("--resume-batch", help="Existing batch id under batch_runs/ to resume.")
    parser.add_argument(
        "--launch-timeout",
        type=float,
        default=30.0,
        help="Seconds to wait for a child pipeline run directory to appear after launch.",
    )
    parser.add_argument(
        "--status-interval",
        type=float,
        default=5.0,
        help="Seconds between child pipeline status polls while monitoring running items.",
    )
    return parser.parse_args()


def list_pipeline_run_dirs() -> set[str]:
    if not PIPELINE_RUNS_DIR.exists():
        return set()
    return {path.name for path in PIPELINE_RUNS_DIR.iterdir() if path.is_dir()}


def wait_for_new_pipeline_run(before: set[str], timeout_seconds: float) -> str:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        current = list_pipeline_run_dirs()
        new_runs = sorted(current - before)
        if new_runs:
            return new_runs[-1]
        time.sleep(0.25)
    raise RuntimeError("timed out while waiting for child pipeline run directory")


def build_child_command(item: dict[str, Any]) -> list[str]:
    command = [
        sys.executable,
        str(RUN_PIPELINE_SCRIPT),
        item["prompt"],
        "--limit",
        str(item["limit"]),
        "--poll-seconds",
        str(item["poll_seconds"]),
        "--matcher-mode",
        str(item["matcher_mode"]),
    ]
    remix_prompt = item.get("remix_prompt")
    if isinstance(remix_prompt, str) and remix_prompt:
        command.extend(["--remix-prompt", remix_prompt])
    if item.get("publish"):
        command.append("--publish")
    if item.get("upload"):
        command.append("--upload")
    return command


def batch_requires_upload(batch: BatchRun) -> bool:
    return any(bool(item.get("upload")) for item in batch.read_items())


def run_batch_upload_preflight(batch: BatchRun) -> dict[str, Any]:
    state = batch.read_state()
    if not batch_requires_upload(batch):
        state["preflight"] = {
            "status": "skipped",
            "project": DEFAULT_GCLOUD_PROJECT,
            "message": "upload auth preflight skipped because no batch items requested upload",
        }
        batch.save_state(state)
        batch.append_event("batch_preflight_skipped", {"reason": "no_upload_items"})
        print_batch("upload auth preflight skipped: no items requested upload")
        return state["preflight"]

    preflight = run_gcloud_auth_preflight(DEFAULT_GCLOUD_PROJECT)
    state["preflight"] = preflight
    if preflight.get("status") != "passed":
        state["status"] = "blocked"
    batch.save_state(state)
    batch.append_event(
        "batch_preflight_checked",
        {
            "status": preflight.get("status"),
            "project": preflight.get("project"),
            "active_account": preflight.get("active_account"),
        },
    )
    print_batch(
        f"upload auth preflight status={preflight.get('status')} project={preflight.get('project')} "
        f"active_account={preflight.get('active_account') or 'none'}"
    )
    return preflight


def child_run_state_path(run_id: str) -> Path:
    return PIPELINE_RUNS_DIR / run_id / "run_state.json"


def child_final_payload_path(run_id: str) -> Path:
    return PIPELINE_RUNS_DIR / run_id / "run_state.json"


def finalize_item_from_child_state(batch: BatchRun, item: dict[str, Any], child_state: dict[str, Any]) -> dict[str, Any]:
    child_status = child_state.get("status")
    item["pipeline_status"] = child_status
    item["current_step"] = child_state.get("current_step")
    item["pipeline_run_dir"] = child_state.get("artifacts", {}).get("run_dir") or item.get("pipeline_run_dir")
    item["completed_at"] = child_state.get("completed_at") or child_state.get("updated_at")
    item["result_summary"] = {
        "status": child_status,
        "final_output_dir": child_state.get("final_output_dir"),
        "final_output_dirs": child_state.get("final_output_dirs", []),
        "projected_cdn_urls": child_state.get("projected_cdn_urls", []),
        "error": child_state.get("error"),
        "dashboard_path": child_state.get("artifacts", {}).get("dashboard_path"),
    }
    if child_status == "completed":
        item["status"] = "completed"
        item["last_error"] = None
    else:
        item["status"] = "failed"
        item["last_error"] = child_state.get("error")
    batch.write_item(item)
    batch.append_event(
        "item_terminal",
        {
            "pipeline_run_id": item.get("pipeline_run_id"),
            "pipeline_status": child_status,
            "current_step": child_state.get("current_step"),
        },
        item_id=item["item_id"],
    )
    print_item_terminal(batch, item, child_state)
    batch.refresh_summary(current_item_id=None)
    return item


def monitor_existing_child_run(batch: BatchRun, item: dict[str, Any], status_interval: float) -> dict[str, Any]:
    run_id = item.get("pipeline_run_id")
    if not isinstance(run_id, str) or not run_id:
        item["status"] = "blocked"
        item["last_error"] = {"message": "running batch item is missing pipeline_run_id"}
        batch.write_item(item)
        batch.append_event("item_blocked", {"reason": "missing pipeline_run_id"}, item_id=item["item_id"])
        batch.refresh_summary(current_item_id=None)
        return item

    state_path = child_run_state_path(run_id)
    last_announced_status = item.get("pipeline_status")
    last_announced_step = item.get("current_step")
    while True:
        if not state_path.exists():
            item["status"] = "blocked"
            item["last_error"] = {"message": "child run_state.json is missing", "run_id": run_id, "run_state_path": str(state_path)}
            batch.write_item(item)
            batch.append_event("item_blocked", {"reason": "missing child run_state", "run_id": run_id}, item_id=item["item_id"])
            batch.refresh_summary(current_item_id=None)
            return item

        child_state = read_json(state_path)
        child_status = child_state.get("status")
        item["pipeline_status"] = child_status
        item["current_step"] = child_state.get("current_step")
        item["pipeline_run_dir"] = child_state.get("artifacts", {}).get("run_dir") or item.get("pipeline_run_dir")
        batch.write_item(item)
        batch.refresh_summary(current_item_id=item["item_id"])
        if child_status != last_announced_status or item.get("current_step") != last_announced_step:
            print_child_transition(batch, item, child_state)
            last_announced_status = child_status
            last_announced_step = item.get("current_step")
        if child_status in CHILD_RUN_TERMINAL_STATUSES:
            return finalize_item_from_child_state(batch, item, child_state)
        time.sleep(status_interval)


def launch_and_monitor_item(batch: BatchRun, item: dict[str, Any], *, launch_timeout: float, status_interval: float) -> dict[str, Any]:
    items_dir = batch.paths.items_dir
    stdout_path = items_dir / f"{item['item_id']}.child.stdout.txt"
    stderr_path = items_dir / f"{item['item_id']}.child.stderr.txt"
    command = build_child_command(item)
    before = list_pipeline_run_dirs()

    stdout_handle = stdout_path.open("w", encoding="utf-8")
    stderr_handle = stderr_path.open("w", encoding="utf-8")
    process = subprocess.Popen(command, cwd=str(ROOT), stdout=stdout_handle, stderr=stderr_handle, text=True)
    stdout_handle.close()
    stderr_handle.close()

    item["status"] = "running"
    item["attempts"] = int(item.get("attempts", 0)) + 1
    item["started_at"] = item.get("started_at") or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    item["child_pid"] = process.pid
    item["child_command"] = command
    item["child_stdout_path"] = str(stdout_path)
    item["child_stderr_path"] = str(stderr_path)
    batch.write_item(item)
    batch.append_event("item_launched", {"child_pid": process.pid, "command": command}, item_id=item["item_id"])
    batch.refresh_summary(current_item_id=item["item_id"])
    print_item_launch(batch, item)

    try:
        run_id = wait_for_new_pipeline_run(before, launch_timeout)
    except Exception as exc:
        process.wait(timeout=5)
        item["status"] = "blocked"
        item["last_error"] = {"message": str(exc)}
        batch.write_item(item)
        batch.append_event("item_blocked", {"reason": "launch_timeout", "message": str(exc)}, item_id=item["item_id"])
        batch.refresh_summary(current_item_id=None)
        return item

    item["pipeline_run_id"] = run_id
    item["pipeline_run_dir"] = str((PIPELINE_RUNS_DIR / run_id).resolve())
    batch.write_item(item)
    batch.append_event("child_run_detected", {"pipeline_run_id": run_id, "pipeline_run_dir": item["pipeline_run_dir"]}, item_id=item["item_id"])
    print_child_detected(batch, item, run_id)

    finalized = monitor_existing_child_run(batch, item, status_interval)
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        pass
    return finalized


def process_batch(batch: BatchRun, *, launch_timeout: float, status_interval: float) -> dict[str, Any]:
    batch.refresh_summary()
    items = batch.read_items()

    for item in items:
        if item.get("status") == "running":
            monitor_existing_child_run(batch, item, status_interval)

    while True:
        items = batch.read_items()
        next_item = next((item for item in items if item.get("status") == "pending"), None)
        if next_item is None:
            return batch.refresh_summary(current_item_id=None)
        launch_and_monitor_item(batch, next_item, launch_timeout=launch_timeout, status_interval=status_interval)


def main() -> int:
    args = parse_args()
    BATCH_RUNS_DIR.mkdir(parents=True, exist_ok=True)
    PIPELINE_RUNS_DIR.mkdir(parents=True, exist_ok=True)

    if args.manifest:
        manifest_path = Path(args.manifest).resolve()
        manifest_payload = read_json(manifest_path)
        batch = BatchRun.create(manifest_path, manifest_payload)
    else:
        batch = BatchRun.load(args.resume_batch)

    preflight = run_batch_upload_preflight(batch)
    if preflight.get("status") == "failed":
        print(json.dumps(batch.read_state(), indent=2))
        return 1

    final_state = process_batch(batch, launch_timeout=args.launch_timeout, status_interval=args.status_interval)
    print(json.dumps(final_state, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())