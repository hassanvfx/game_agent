#!/usr/bin/env python3
"""Persistent state helpers for serial batch pipeline orchestration."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from run_pipeline import DEFAULT_MATCHER_LIMIT, DEFAULT_MATCHER_MODE, DEFAULT_POLL_SECONDS


ROOT = Path(__file__).resolve().parent.parent
BATCH_RUNS_DIR = ROOT / "batch_runs"
PIPELINE_RUNS_DIR = ROOT / "pipeline_runs"

ITEM_TERMINAL_STATUSES = {"completed", "failed", "blocked", "skipped"}
ITEM_ACTIVE_STATUSES = {"pending", "running"}
CHILD_RUN_TERMINAL_STATUSES = {"completed", "failed"}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def append_jsonl(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True) + "\n")


def generate_batch_id() -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"batch_pipeline_{timestamp}"


def built_in_defaults() -> dict[str, Any]:
    return {
        "limit": DEFAULT_MATCHER_LIMIT,
        "remix_prompt": None,
        "publish": False,
        "upload": False,
        "poll_seconds": DEFAULT_POLL_SECONDS,
        "matcher_mode": DEFAULT_MATCHER_MODE,
    }


def validate_manifest_payload(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("batch manifest must be a JSON object")
    runs = payload.get("runs")
    if not isinstance(runs, list):
        raise ValueError("batch manifest must contain a 'runs' array")
    defaults = payload.get("defaults", {})
    if defaults is None:
        defaults = {}
    if not isinstance(defaults, dict):
        raise ValueError("batch manifest 'defaults' must be an object when provided")
    return {"defaults": defaults, "runs": runs}


def resolve_item_spec(raw_item: Any, defaults: dict[str, Any], index: int) -> dict[str, Any]:
    if not isinstance(raw_item, dict):
        raise ValueError(f"runs[{index}] must be an object")
    prompt = raw_item.get("prompt")
    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError(f"runs[{index}].prompt is required")

    spec = {**defaults, **raw_item}
    limit = spec.get("limit", DEFAULT_MATCHER_LIMIT)
    if not isinstance(limit, int) or limit < 1:
        raise ValueError(f"runs[{index}].limit must be an integer >= 1")
    poll_seconds = spec.get("poll_seconds", DEFAULT_POLL_SECONDS)
    if not isinstance(poll_seconds, (int, float)) or poll_seconds <= 0:
        raise ValueError(f"runs[{index}].poll_seconds must be > 0")
    matcher_mode = spec.get("matcher_mode", DEFAULT_MATCHER_MODE)
    if matcher_mode not in {"legacy", "v2"}:
        raise ValueError(f"runs[{index}].matcher_mode must be 'legacy' or 'v2'")
    remix_prompt = spec.get("remix_prompt")
    if remix_prompt is not None and not isinstance(remix_prompt, str):
        raise ValueError(f"runs[{index}].remix_prompt must be a string or null")

    return {
        "item_id": f"{index + 1:04d}",
        "prompt": prompt.strip(),
        "limit": limit,
        "remix_prompt": remix_prompt,
        "publish": bool(spec.get("publish", False)),
        "upload": bool(spec.get("upload", False)),
        "poll_seconds": float(poll_seconds),
        "matcher_mode": matcher_mode,
    }


def resolve_manifest(payload: dict[str, Any]) -> dict[str, Any]:
    validated = validate_manifest_payload(payload)
    resolved_defaults = {**built_in_defaults(), **validated["defaults"]}
    if not isinstance(resolved_defaults.get("limit"), int) or resolved_defaults["limit"] < 1:
        raise ValueError("manifest defaults.limit must be an integer >= 1")
    if resolved_defaults.get("matcher_mode") not in {"legacy", "v2"}:
        raise ValueError("manifest defaults.matcher_mode must be 'legacy' or 'v2'")
    poll_seconds = resolved_defaults.get("poll_seconds")
    if not isinstance(poll_seconds, (int, float)) or poll_seconds <= 0:
        raise ValueError("manifest defaults.poll_seconds must be > 0")
    items = [resolve_item_spec(item, resolved_defaults, index) for index, item in enumerate(validated["runs"])]
    return {"defaults": resolved_defaults, "runs": items}


def summarize_items(items: list[dict[str, Any]]) -> dict[str, int]:
    counts = {
        "total": len(items),
        "pending": 0,
        "running": 0,
        "completed": 0,
        "failed": 0,
        "blocked": 0,
        "skipped": 0,
    }
    for item in items:
        status = item.get("status", "pending")
        if status in counts:
            counts[status] += 1
    return counts


def derive_batch_status(items: list[dict[str, Any]]) -> str:
    if not items:
        return "completed"
    statuses = {str(item.get("status", "pending")) for item in items}
    if "running" in statuses:
        return "running"
    if "pending" in statuses:
        return "pending"
    if statuses <= {"completed"}:
        return "completed"
    if statuses & {"failed", "blocked"}:
        return "completed_with_failures"
    return "completed"


@dataclass
class BatchPaths:
    batch_id: str
    batch_dir: Path
    state_path: Path
    events_path: Path
    items_dir: Path
    original_manifest_path: Path
    resolved_manifest_path: Path


class BatchRun:
    def __init__(self, paths: BatchPaths) -> None:
        self.paths = paths

    @classmethod
    def create(cls, manifest_path: Path, manifest_payload: dict[str, Any]) -> "BatchRun":
        batch_id = generate_batch_id()
        batch_dir = BATCH_RUNS_DIR / batch_id
        items_dir = batch_dir / "items"
        items_dir.mkdir(parents=True, exist_ok=False)
        paths = BatchPaths(
            batch_id=batch_id,
            batch_dir=batch_dir,
            state_path=batch_dir / "batch_state.json",
            events_path=batch_dir / "events.jsonl",
            items_dir=items_dir,
            original_manifest_path=batch_dir / "manifest.original.json",
            resolved_manifest_path=batch_dir / "manifest.resolved.json",
        )
        batch = cls(paths)
        resolved_manifest = resolve_manifest(manifest_payload)
        write_json(paths.original_manifest_path, manifest_payload)
        write_json(paths.resolved_manifest_path, resolved_manifest)
        items: list[dict[str, Any]] = []
        for resolved_item in resolved_manifest["runs"]:
            item = {
                **resolved_item,
                "status": "pending",
                "attempts": 0,
                "pipeline_run_id": None,
                "pipeline_run_dir": None,
                "pipeline_status": None,
                "current_step": None,
                "child_pid": None,
                "child_command": None,
                "child_stdout_path": None,
                "child_stderr_path": None,
                "started_at": None,
                "completed_at": None,
                "last_error": None,
                "result_summary": None,
            }
            batch.write_item(item)
            items.append(item)
        now = utc_now()
        state = {
            "batch_id": batch_id,
            "status": derive_batch_status(items),
            "created_at": now,
            "updated_at": now,
            "source_manifest_path": str(manifest_path.resolve()),
            "batch_dir": str(batch_dir),
            "items_dir": str(items_dir),
            "item_order": [item["item_id"] for item in items],
            "defaults": resolved_manifest["defaults"],
            "preflight": None,
            "counts": summarize_items(items),
            "current_item_id": None,
        }
        write_json(paths.state_path, state)
        batch.append_event("batch_initialized", {"source_manifest_path": str(manifest_path.resolve())})
        return batch

    @classmethod
    def load(cls, batch_id: str) -> "BatchRun":
        batch_dir = BATCH_RUNS_DIR / batch_id
        return cls(
            BatchPaths(
                batch_id=batch_id,
                batch_dir=batch_dir,
                state_path=batch_dir / "batch_state.json",
                events_path=batch_dir / "events.jsonl",
                items_dir=batch_dir / "items",
                original_manifest_path=batch_dir / "manifest.original.json",
                resolved_manifest_path=batch_dir / "manifest.resolved.json",
            )
        )

    def read_state(self) -> dict[str, Any]:
        return read_json(self.paths.state_path)

    def save_state(self, state: dict[str, Any]) -> None:
        state["updated_at"] = utc_now()
        write_json(self.paths.state_path, state)

    def append_event(self, event: str, details: dict[str, Any] | None = None, *, item_id: str | None = None) -> None:
        append_jsonl(
            self.paths.events_path,
            {
                "ts": utc_now(),
                "event": event,
                "item_id": item_id,
                "details": details or {},
            },
        )

    def item_path(self, item_id: str) -> Path:
        return self.paths.items_dir / f"{item_id}.json"

    def read_item(self, item_id: str) -> dict[str, Any]:
        return read_json(self.item_path(item_id))

    def write_item(self, item: dict[str, Any]) -> None:
        write_json(self.item_path(str(item["item_id"])), item)

    def read_items(self) -> list[dict[str, Any]]:
        state = self.read_state()
        return [self.read_item(item_id) for item_id in state.get("item_order", [])]

    def refresh_summary(self, *, current_item_id: str | None = None) -> dict[str, Any]:
        state = self.read_state()
        items = self.read_items()
        state["counts"] = summarize_items(items)
        preflight = state.get("preflight")
        if isinstance(preflight, dict) and preflight.get("status") == "failed":
            state["status"] = "blocked"
        else:
            state["status"] = derive_batch_status(items)
        if current_item_id is not None:
            state["current_item_id"] = current_item_id
        elif state["status"] != "running":
            state["current_item_id"] = None
        self.save_state(state)
        return state
