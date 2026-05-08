#!/usr/bin/env python3
"""Observer CLI for persisted pipeline runs."""

from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
PIPELINE_RUNS_DIR = ROOT / "pipeline_runs"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_recent_events(path: Path, limit: int = 15) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in lines[-limit:]][::-1]


def resolve_run_dir(run_dir: str | None, run_id: str | None) -> Path:
    if run_dir:
        return Path(run_dir).resolve()
    if run_id:
        return (PIPELINE_RUNS_DIR / run_id).resolve()
    raise ValueError("pass either --run-dir or --run-id")


def normalize_dashboard_payload(run_dir: Path) -> dict[str, Any]:
    run_state_path = run_dir / "run_state.json"
    dashboard_data_path = run_dir / "dashboard" / "dashboard_data.json"
    events_path = run_dir / "events.jsonl"

    if dashboard_data_path.exists():
        payload = read_json(dashboard_data_path)
    elif run_state_path.exists():
        run_state = read_json(run_state_path)
        payload = {
            "run_id": run_state.get("run_id"),
            "prompt": run_state.get("prompt"),
            "status": run_state.get("status"),
            "current_step": run_state.get("current_step"),
            "updated_at": run_state.get("updated_at"),
            "started_at": run_state.get("started_at"),
            "obfuscation_enabled": run_state.get("obfuscation_enabled", False),
            "steps": [
                {
                    "id": step_id,
                    "label": step_id.replace("_", " ").title(),
                    "status": step.get("status", "unknown"),
                    "details": step,
                }
                for step_id, step in run_state.get("steps", {}).items()
            ],
            "links": run_state.get("artifacts", {}),
            "error": run_state.get("error"),
        }
    else:
        raise FileNotFoundError(f"run state not found in {run_dir}")

    payload["recent_events"] = read_recent_events(events_path, limit=15)
    payload.setdefault("links", {})
    payload["links"]["run_dir"] = str(run_dir)
    payload["links"]["dashboard_path"] = str(run_dir / "dashboard" / "index.html")
    return payload


def render_terminal(payload: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append(f"Pipeline Run: {payload.get('run_id', 'unknown')}")
    lines.append(f"Prompt: {payload.get('prompt', '')}")
    lines.append(f"Status: {str(payload.get('status', 'unknown')).upper()}")
    lines.append(f"Current Step: {payload.get('current_step', 'unknown')}")
    lines.append(f"Updated: {payload.get('updated_at', 'unknown')}")
    lines.append("")

    lines.append("Steps")
    for step in payload.get("steps", []):
        status = step.get("status", "unknown")
        details = step.get("details", {})
        summary_parts = []
        if isinstance(details, dict):
            if "selected_game_ids" in details:
                summary_parts.append(f"selected={len(details['selected_game_ids'])}")
            if "last_known_status" in details:
                summary_parts.append(f"upstream={details['last_known_status']}")
            if "destination" in details:
                summary_parts.append(f"destination={details['destination']}")
            if "reason" in details:
                summary_parts.append(f"reason={details['reason']}")
            if "error" in details:
                error_message = details["error"].get("message") if isinstance(details["error"], dict) else details["error"]
                summary_parts.append(f"error={error_message}")
        summary = ", ".join(summary_parts)
        lines.append(f"- {step.get('id', 'unknown'):15} {status:10} {summary}".rstrip())

    lines.append("")
    lines.append("Recent Events")
    recent_events = payload.get("recent_events", [])
    if recent_events:
        for event in recent_events:
            lines.append(
                f"- [{event.get('ts', '?')}] {event.get('step', '?')} {event.get('event', '?')} "
                f"{json.dumps(event.get('details', {}), ensure_ascii=False)}"
            )
    else:
        lines.append("- none")

    lines.append("")
    lines.append("Links")
    for key, value in payload.get("links", {}).items():
        lines.append(f"- {key}: {value}")

    if payload.get("error") is not None:
        lines.append("")
        lines.append("Error")
        lines.append(json.dumps(payload["error"], indent=2, ensure_ascii=False))

    return "\n".join(lines)


def clear_screen() -> None:
    os.system("clear")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Observe a persisted game pipeline run.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--run-dir", help="Absolute or relative pipeline run directory.")
    group.add_argument("--run-id", help="Pipeline run id under pipeline_runs/.")
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
    run_dir = resolve_run_dir(args.run_dir, args.run_id)

    if not args.watch:
        emit_once(normalize_dashboard_payload(run_dir), args.json)
        return 0

    while True:
        payload = normalize_dashboard_payload(run_dir)
        if not args.json:
            clear_screen()
        emit_once(payload, args.json)
        time.sleep(args.interval)


if __name__ == "__main__":
    raise SystemExit(main())