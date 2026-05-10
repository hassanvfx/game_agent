from __future__ import annotations

import argparse
import json
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

TOOL_ROOT = Path(__file__).resolve().parents[1]
RUNS_ROOT = TOOL_ROOT / "runs"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def default_run_id() -> str:
    return f"run_game_actor_mock_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}_{uuid.uuid4().hex[:8]}"


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(path.suffix + ".tmp")
    temp_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    temp_path.replace(path)


def append_event(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload) + "\n")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def run_dir_for(run_id: str, runs_root: Path) -> Path:
    return runs_root / run_id


def request_path(run_dir: Path) -> Path:
    return run_dir / "request.json"


def result_path(run_dir: Path) -> Path:
    return run_dir / "result.json"


def run_state_path(run_dir: Path) -> Path:
    return run_dir / "run_state.json"


def event_log_path(run_dir: Path) -> Path:
    return run_dir / "events.jsonl"


def game_state_path(run_dir: Path, game_id: str) -> Path:
    return run_dir / "games" / game_id / "game_state.json"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Mock async actor with game_refactoring-like run persistence.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    submit = subparsers.add_parser("submit", help="Create a mock async run and enqueue it.")
    submit.add_argument("--prompt", required=True, help="Creative prompt for the mock run.")
    submit.add_argument("--game", dest="games", action="append", required=True, help="Game id to include.")
    submit.add_argument("--run-id", help="Optional explicit run id.")
    submit.add_argument("--runs-root", help="Optional custom runs root.")

    status = subparsers.add_parser("status", help="Inspect run state by run id.")
    status.add_argument("--run-id", required=True)
    status.add_argument("--runs-root", help="Optional custom runs root.")

    return parser


def initialize_run(prompt: str, games: list[str], run_id: str, runs_root: Path) -> Path:
    run_dir = run_dir_for(run_id, runs_root)
    if run_dir.exists():
        raise SystemExit(f"Run directory already exists: {run_dir}")

    (run_dir / "input").mkdir(parents=True, exist_ok=True)
    (run_dir / "output").mkdir(parents=True, exist_ok=True)
    (run_dir / "games").mkdir(parents=True, exist_ok=True)
    (run_dir / "dashboard").mkdir(parents=True, exist_ok=True)

    request_payload = {
        "run_id": run_id,
        "prompt": prompt,
        "games": [{"game_id": game_id} for game_id in games],
        "created_at": utc_now(),
    }
    write_json(request_path(run_dir), request_payload)

    run_state = {
        "run_id": run_id,
        "run_dir": str(run_dir),
        "runs_root": str(runs_root),
        "status": "queued",
        "current_phase": "queued_for_mock_execution",
        "created_at": utc_now(),
        "updated_at": utc_now(),
        "games_total": len(games),
        "games_completed": 0,
        "games_failed": 0,
        "prompt": prompt,
        "notes": [
            "Game actor mock run scaffold created.",
            "Execution will be simulated by a Celery worker.",
        ],
    }
    write_json(run_state_path(run_dir), run_state)

    for game_id in games:
        game_dir = run_dir / "games" / game_id
        game_dir.mkdir(parents=True, exist_ok=True)
        game_state = {
            "game_id": game_id,
            "status": "queued",
            "current_phase": "waiting_for_worker",
            "attempt_count": 0,
            "last_error": None,
            "updated_at": utc_now(),
        }
        write_json(game_state_path(run_dir, game_id), game_state)

    append_event(
        event_log_path(run_dir),
        {
            "ts": utc_now(),
            "type": "run_created",
            "run_id": run_id,
            "games_total": len(games),
        },
    )
    return run_dir


def update_run_state(run_dir: Path, **changes: Any) -> dict[str, Any]:
    state = read_json(run_state_path(run_dir))
    state.update(changes)
    state["updated_at"] = utc_now()
    write_json(run_state_path(run_dir), state)
    return state


def update_game_state(run_dir: Path, game_id: str, **changes: Any) -> dict[str, Any]:
    state = read_json(game_state_path(run_dir, game_id))
    state.update(changes)
    state["updated_at"] = utc_now()
    write_json(game_state_path(run_dir, game_id), state)
    return state


def run_game_actor_mock_task(task_id: str | None, run_id: str, runs_root_value: str) -> dict[str, Any]:
    runs_root = Path(runs_root_value)
    run_dir = run_dir_for(run_id, runs_root)
    request_payload = read_json(request_path(run_dir))
    games = [entry["game_id"] for entry in request_payload["games"]]

    update_run_state(
        run_dir,
        status="running",
        current_phase="worker_started",
        celery_task_id=task_id,
    )
    append_event(event_log_path(run_dir), {"ts": utc_now(), "type": "worker_started", "task_id": task_id})

    completed = 0
    for index, game_id in enumerate(games, start=1):
        update_game_state(run_dir, game_id, status="running", current_phase="mock_processing", attempt_count=1)
        update_run_state(
            run_dir,
            current_phase=f"processing_{game_id}",
            games_completed=completed,
        )
        append_event(
            event_log_path(run_dir),
            {
                "ts": utc_now(),
                "type": "game_started",
                "game_id": game_id,
                "position": index,
                "games_total": len(games),
            },
        )
        time.sleep(1)
        completed += 1
        update_game_state(run_dir, game_id, status="completed", current_phase="mock_completed")
        update_run_state(run_dir, games_completed=completed)
        append_event(
            event_log_path(run_dir),
            {
                "ts": utc_now(),
                "type": "game_completed",
                "game_id": game_id,
                "position": index,
                "games_total": len(games),
            },
        )

    result_payload = {
        "run_id": run_id,
        "status": "completed",
        "prompt": request_payload["prompt"],
        "games": games,
        "completed_at": utc_now(),
        "mock_output_dir": str(run_dir / "output"),
    }
    write_json(result_path(run_dir), result_payload)
    update_run_state(run_dir, status="completed", current_phase="mock_finished", games_completed=completed)
    append_event(event_log_path(run_dir), {"ts": utc_now(), "type": "run_completed"})
    return result_payload


def resolve_runs_root(raw_value: str | None) -> Path:
    return Path(raw_value).resolve() if raw_value else RUNS_ROOT


def command_submit(args: argparse.Namespace) -> int:
    run_id = args.run_id or default_run_id()
    runs_root = resolve_runs_root(args.runs_root)
    run_dir = initialize_run(args.prompt, args.games, run_id, runs_root)
    from app.tasks import run_game_actor_mock

    async_result = run_game_actor_mock.delay(run_id, str(runs_root))
    state = update_run_state(run_dir, celery_task_id=async_result.id)
    output = {
        "run_id": run_id,
        "run_dir": str(run_dir),
        "celery_task_id": async_result.id,
        "status": state["status"],
    }
    print(json.dumps(output, indent=2))
    return 0


def command_status(args: argparse.Namespace) -> int:
    runs_root = resolve_runs_root(args.runs_root)
    run_dir = run_dir_for(args.run_id, runs_root)
    if not run_dir.exists():
        raise SystemExit(f"Run directory not found: {run_dir}")

    state = read_json(run_state_path(run_dir))
    celery_task_id = state.get("celery_task_id")
    celery_state = None
    if celery_task_id:
        from celery.result import AsyncResult
        from app.celery_app import celery_app

        celery_state = AsyncResult(celery_task_id, app=celery_app).state

    output = {
        "run_id": state["run_id"],
        "run_dir": str(run_dir),
        "status": state["status"],
        "current_phase": state["current_phase"],
        "games_total": state["games_total"],
        "games_completed": state["games_completed"],
        "celery_task_id": celery_task_id,
        "celery_state": celery_state,
        "updated_at": state["updated_at"],
        "result_path": str(result_path(run_dir)) if result_path(run_dir).exists() else None,
    }
    print(json.dumps(output, indent=2))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "submit":
        return command_submit(args)
    if args.command == "status":
        return command_status(args)
    raise SystemExit(f"Unsupported command: {args.command}")