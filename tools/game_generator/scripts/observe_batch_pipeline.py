#!/usr/bin/env python3
"""Observer CLI for persisted batch pipeline runs."""

from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path
from typing import Any

from batch_pipeline_state import BATCH_RUNS_DIR, BatchRun, append_jsonl, read_json


def resolve_batch(batch_dir: str | None, batch_id: str | None) -> BatchRun:
    if batch_dir:
        path = Path(batch_dir).resolve()
        return BatchRun.load(path.name)
    if batch_id:
        return BatchRun.load(batch_id)
    raise ValueError("pass either --batch-dir or --batch-id")


def read_recent_events(path: Path, limit: int = 15) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in lines[-limit:]][::-1]


def normalize_payload(batch: BatchRun) -> dict[str, Any]:
    state = batch.refresh_summary()
    items = batch.read_items()
    return {
        **state,
        "items": items,
        "recent_events": read_recent_events(batch.paths.events_path, limit=15),
        "links": {
            "batch_dir": str(batch.paths.batch_dir),
            "batch_state_path": str(batch.paths.state_path),
            "events_path": str(batch.paths.events_path),
            "resolved_manifest_path": str(batch.paths.resolved_manifest_path),
            "items_dir": str(batch.paths.items_dir),
        },
    }


def render_terminal(payload: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append(f"Batch Run: {payload.get('batch_id', 'unknown')}")
    lines.append(f"Status: {str(payload.get('status', 'unknown')).upper()}")
    lines.append(f"Updated: {payload.get('updated_at', 'unknown')}")
    lines.append("")
    counts = payload.get("counts", {})
    lines.append(
        "Counts: total={total} pending={pending} running={running} completed={completed} failed={failed} blocked={blocked} skipped={skipped}".format(
            total=counts.get("total", 0),
            pending=counts.get("pending", 0),
            running=counts.get("running", 0),
            completed=counts.get("completed", 0),
            failed=counts.get("failed", 0),
            blocked=counts.get("blocked", 0),
            skipped=counts.get("skipped", 0),
        )
    )
    lines.append("")
    lines.append("Items")
    for item in payload.get("items", []):
        lines.append(
            "- {item_id} {status:10} limit={limit} run_id={run_id} prompt={prompt}".format(
                item_id=item.get("item_id", "????"),
                status=str(item.get("status", "unknown")),
                limit=item.get("limit", "?"),
                run_id=item.get("pipeline_run_id") or "-",
                prompt=json.dumps(item.get("prompt", ""), ensure_ascii=False),
            )
        )
    lines.append("")
    lines.append("Recent Events")
    recent_events = payload.get("recent_events", [])
    if recent_events:
        for event in recent_events:
            lines.append(
                f"- [{event.get('ts', '?')}] {event.get('event', '?')} item={event.get('item_id') or '-'} {json.dumps(event.get('details', {}), ensure_ascii=False)}"
            )
    else:
        lines.append("- none")
    lines.append("")
    lines.append("Links")
    for key, value in payload.get("links", {}).items():
        lines.append(f"- {key}: {value}")
    return "\n".join(lines)


def clear_screen() -> None:
    os.system("clear")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Observe a persisted batch pipeline run.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--batch-dir", help="Absolute or relative batch run directory.")
    group.add_argument("--batch-id", help="Batch run id under batch_runs/.")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of terminal text.")
    parser.add_argument("--watch", action="store_true", help="Refresh view continuously.")
    parser.add_argument("--interval", type=float, default=3.0, help="Refresh interval for --watch.")
    return parser.parse_args()


def emit_once(payload: dict[str, Any], as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(render_terminal(payload))


def main() -> int:
    args = parse_args()
    batch = resolve_batch(args.batch_dir, args.batch_id)
    if not args.watch:
        emit_once(normalize_payload(batch), args.json)
        return 0

    while True:
        payload = normalize_payload(batch)
        if not args.json:
            clear_screen()
        emit_once(payload, args.json)
        time.sleep(args.interval)


if __name__ == "__main__":
    raise SystemExit(main())