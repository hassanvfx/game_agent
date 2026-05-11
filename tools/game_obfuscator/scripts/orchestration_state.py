#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_name(f"{path.name}.tmp")
    temp_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    os.replace(temp_path, path)


def sanitize_entry_key(value: str) -> str:
    sanitized = re.sub(r"[^A-Za-z0-9._-]+", "__", value.strip("/"))
    sanitized = sanitized.strip("._-")
    if not sanitized:
        raise ValueError("Could not derive a valid entry key.")
    return sanitized


def entry_key_from_output_path(output_path: str | Path) -> str:
    path = Path(output_path)
    parts = [part for part in path.parts if part not in {"/", ""}]
    if len(parts) >= 2:
        return sanitize_entry_key("__".join(parts[-2:]))
    if parts:
        return sanitize_entry_key(parts[-1])
    raise ValueError(f"Could not derive entry key from output path: {output_path}")


def game_state_path(run_dir: Path, entry_key: str) -> Path:
    return run_dir / "games" / entry_key / "game_state.json"


def run_state_path(run_dir: Path) -> Path:
    return run_dir / "run_state.json"


def ensure_game_timestamps(game_state: dict[str, Any]) -> dict[str, Any]:
    now = utc_now()
    game_state.setdefault("started_at", None)
    game_state.setdefault("updated_at", now)
    game_state.setdefault("completed_at", None)
    game_state.setdefault("heartbeat_at", None)
    game_state.setdefault("last_progress_at", None)
    game_state.setdefault("attempt_count", 0)
    game_state.setdefault("last_error", None)
    game_state.setdefault("phase_history", [])
    return game_state


def ensure_run_timestamps(run_state: dict[str, Any]) -> dict[str, Any]:
    now = utc_now()
    run_state.setdefault("created_at", now)
    run_state.setdefault("started_at", None)
    run_state.setdefault("updated_at", now)
    run_state.setdefault("completed_at", None)
    run_state.setdefault("heartbeat_at", None)
    run_state.setdefault("last_progress_at", None)
    run_state.setdefault("resume_supported", True)
    run_state.setdefault("games_pending", 0)
    run_state.setdefault("games_running", 0)
    run_state.setdefault("games_succeeded", 0)
    run_state.setdefault("games_failed", 0)
    run_state.setdefault("games_stalled", 0)
    return run_state


def update_game_state(
    run_dir: Path,
    entry_key: str,
    *,
    status: str | None = None,
    phase: str | None = None,
    last_error: str | None = None,
    heartbeat: bool = False,
    progress: bool = False,
    mark_started: bool = False,
    mark_completed: bool = False,
    increment_attempt: bool = False,
    artifacts: dict[str, Any] | None = None,
    extra_fields: dict[str, Any] | None = None,
) -> dict[str, Any]:
    path = game_state_path(run_dir, entry_key)
    game_state = ensure_game_timestamps(load_json(path))
    now = utc_now()

    previous_phase = game_state.get("current_phase")
    if status is not None:
        game_state["status"] = status
    if phase is not None:
        game_state["current_phase"] = phase
        if phase != previous_phase:
            game_state.setdefault("phase_history", []).append(
                {
                    "phase": phase,
                    "entered_at": now,
                }
            )
    if last_error is not None or status in {"failed", "stalled", "verification_failed"}:
        game_state["last_error"] = last_error
    if mark_started and not game_state.get("started_at"):
        game_state["started_at"] = now
    if mark_completed:
        game_state["completed_at"] = now
    if increment_attempt:
        game_state["attempt_count"] = int(game_state.get("attempt_count", 0)) + 1
    if heartbeat:
        game_state["heartbeat_at"] = now
    if progress:
        game_state["last_progress_at"] = now
    if artifacts:
        game_state["artifacts"] = {
            **game_state.get("artifacts", {}),
            **artifacts,
        }
    if extra_fields:
        game_state.update(extra_fields)

    game_state["updated_at"] = now
    write_json(path, game_state)
    return game_state


def recompute_run_state(run_dir: Path, *, current_phase: str | None = None, note: str | None = None) -> dict[str, Any]:
    run_state = ensure_run_timestamps(load_json(run_state_path(run_dir)))
    manifest = load_json(run_dir / "input_manifest.json")
    game_states = [
        ensure_game_timestamps(load_json(game_state_path(run_dir, game["entry_key"])))
        for game in manifest.get("games", [])
    ]

    counts = {
        "pending": 0,
        "running": 0,
        "succeeded": 0,
        "failed": 0,
        "stalled": 0,
    }

    for state in game_states:
        status = state.get("status")
        if status in {"created", "ready", "analyzed", "bundled", "pending"}:
            counts["pending"] += 1
        elif status in {"running"}:
            counts["running"] += 1
        elif status in {"succeeded", "verification_passed"}:
            counts["succeeded"] += 1
        elif status in {"stalled"}:
            counts["stalled"] += 1
        elif status in {"failed", "verification_failed"}:
            counts["failed"] += 1
        else:
            counts["pending"] += 1

    if counts["running"] > 0:
        aggregate_status = "running"
    elif counts["stalled"] > 0 and counts["succeeded"] == 0 and counts["failed"] == 0 and counts["pending"] == 0:
        aggregate_status = "stalled"
    elif counts["failed"] > 0 or counts["stalled"] > 0:
        aggregate_status = "completed_with_failures" if counts["pending"] == 0 else "running"
    elif counts["pending"] == 0:
        aggregate_status = "completed"
    else:
        aggregate_status = "ready"

    now = utc_now()
    if aggregate_status == "running" and not run_state.get("started_at"):
        run_state["started_at"] = now
    if aggregate_status in {"completed", "completed_with_failures", "stalled"} and not run_state.get("completed_at"):
        run_state["completed_at"] = now

    if current_phase is not None:
        run_state["current_phase"] = current_phase
    run_state["status"] = aggregate_status
    run_state["games_total"] = len(game_states)
    run_state["games_pending"] = counts["pending"]
    run_state["games_running"] = counts["running"]
    run_state["games_succeeded"] = counts["succeeded"]
    run_state["games_failed"] = counts["failed"]
    run_state["games_stalled"] = counts["stalled"]
    run_state["heartbeat_at"] = now
    run_state["last_progress_at"] = now
    run_state["updated_at"] = now
    if note:
        notes = run_state.setdefault("notes", [])
        if note not in notes:
            notes.append(note)

    write_json(run_state_path(run_dir), run_state)
    return run_state


def detect_stale_game(
    run_dir: Path,
    entry_key: str,
    *,
    stale_after_seconds: int,
) -> dict[str, Any]:
    path = game_state_path(run_dir, entry_key)
    game_state = ensure_game_timestamps(load_json(path))
    heartbeat_at = game_state.get("heartbeat_at") or game_state.get("updated_at")
    if not heartbeat_at:
        return game_state

    heartbeat_dt = datetime.fromisoformat(heartbeat_at.replace("Z", "+00:00"))
    age_seconds = int((datetime.now(timezone.utc) - heartbeat_dt).total_seconds())
    if game_state.get("status") == "running" and age_seconds > stale_after_seconds:
        return update_game_state(
            run_dir,
            entry_key,
            status="stalled",
            phase=game_state.get("current_phase", "stalled"),
            last_error=f"No heartbeat detected for {age_seconds} seconds.",
            heartbeat=True,
            extra_fields={"stale_age_seconds": age_seconds},
        )

    return game_state