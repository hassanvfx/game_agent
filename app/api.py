from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.celery_app import celery_app
from app.tasks import run_game_actor_mock, run_game_refactoring_workflow
from tools.game_actor_mock.game_actor_mock.mock_actor import (
    RUNS_ROOT,
    default_run_id,
    initialize_run,
    read_json,
    resolve_runs_root,
    result_path,
    run_dir_for,
    run_state_path,
    write_json,
)

app = FastAPI(title="game_agent API", version="0.1.0")


class SubmitJobRequest(BaseModel):
    prompt: str = Field(..., min_length=1)
    games: list[str] = Field(..., min_length=1)
    run_id: str | None = None
    runs_root: str | None = None


class SubmitJobResponse(BaseModel):
    run_id: str
    run_dir: str
    celery_task_id: str
    status: str
    status_url: str


class JobStatusResponse(BaseModel):
    run_id: str
    run_dir: str
    status: str
    current_phase: str
    games_total: int
    games_completed: int
    celery_task_id: str | None
    celery_state: str | None
    updated_at: str
    result: dict[str, Any] | None


class AdvancedWorkflowRequest(BaseModel):
    workflow_id: str = Field(..., alias="id")
    raw_game_ids: list[str] = Field(..., min_length=1)
    source_mode: str = "copy"
    pipeline: str = "v2"
    model: str = "gpt-5.4"
    agent_timeout: int = 3600
    max_concurrency: int = 2
    poll_seconds: float = 5.0
    stale_heartbeat_seconds: int = 900
    remix_prompt: str | None = None
    remix_prompt_file: str | None = None
    playwright_port_base: int | None = None
    playwright_port_pool_size: int | None = None
    playwright_port_lease_ttl_seconds: int | None = None
    dry_run_operators: bool = False
    dry_run_spec_adaptor: bool = False

    model_config = {"populate_by_name": True}


class AdvancedWorkflowResponse(BaseModel):
    task_id: str
    workflow_id: str
    submitted: bool
    status: str
    comment: str
    result_url: str | None = None
    matched_ids: list[str] = Field(default_factory=list)


def _read_mock_status(run_id: str, runs_root: str | None = None) -> JobStatusResponse:
    root_path = resolve_runs_root(runs_root) if runs_root else RUNS_ROOT
    run_dir = run_dir_for(run_id, root_path)
    if not run_dir.exists():
        raise HTTPException(status_code=404, detail=f"Run directory not found: {run_dir}")

    state = read_json(run_state_path(run_dir))
    celery_task_id = state.get("celery_task_id")
    celery_state = None
    if celery_task_id:
        celery_state = celery_app.AsyncResult(celery_task_id).state

    result = read_json(result_path(run_dir)) if result_path(run_dir).exists() else None
    return JobStatusResponse(
        run_id=state["run_id"],
        run_dir=str(run_dir),
        status=state["status"],
        current_phase=state["current_phase"],
        games_total=state["games_total"],
        games_completed=state["games_completed"],
        celery_task_id=celery_task_id,
        celery_state=celery_state,
        updated_at=state["updated_at"],
        result=result,
    )


@app.get("/")
def root() -> dict[str, str]:
    return {
        "service": "game_agent",
        "mode": "api",
        "status": "ok",
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/jobs", response_model=SubmitJobResponse)
def submit_job(request: SubmitJobRequest) -> SubmitJobResponse:
    run_id = request.run_id or default_run_id()
    runs_root = resolve_runs_root(request.runs_root)
    run_dir = initialize_run(request.prompt, request.games, run_id, runs_root)
    async_result = run_game_actor_mock.delay(run_id, str(runs_root))
    state = read_json(run_state_path(run_dir))
    state["celery_task_id"] = async_result.id
    write_json(run_state_path(run_dir), state)
    return SubmitJobResponse(
        run_id=run_id,
        run_dir=str(run_dir),
        celery_task_id=async_result.id,
        status=state["status"],
        status_url=f"/jobs/{run_id}",
    )


@app.get("/jobs/{run_id}", response_model=JobStatusResponse)
def job_status(run_id: str, runs_root: str | None = None) -> JobStatusResponse:
    return _read_mock_status(run_id, runs_root)


RAW_GAMES_ROOT = Path("/app/games/raw")


def _resolve_raw_games(raw_game_ids: list[str]) -> tuple[list[dict[str, str]], list[str]]:
    matched: list[dict[str, str]] = []
    missing: list[str] = []
    for raw_game_id in raw_game_ids:
        candidate = RAW_GAMES_ROOT / raw_game_id
        if candidate.exists() and candidate.is_dir():
            matched.append(
                {
                    "game_id": raw_game_id,
                    "display_name": raw_game_id,
                    "source_path": str(candidate),
                }
            )
        else:
            missing.append(raw_game_id)
    return matched, missing


def _write_internal_manifest(workflow_id: str, task_id: str, games: list[dict[str, str]]) -> Path:
    manifest_dir = Path("/app/tools/game_refactoring/runs/_api_manifests")
    manifest_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = manifest_dir / f"{workflow_id}__{task_id}.json"
    write_json(
        manifest_path,
        {
            "run_label": f"{workflow_id}-{task_id}",
            "games": games,
        },
    )
    return manifest_path


def _new_task_id() -> str:
    return celery_app.backend.get_key_for_task(__import__("uuid").uuid4().hex).decode().split("celery-task-meta-")[-1]


def _summarize_game_results(run_dir: Path) -> list[dict[str, str]]:
    games_dir = run_dir / "games"
    if not games_dir.exists():
        return []
    results: list[dict[str, str]] = []
    for game_dir in sorted(path for path in games_dir.iterdir() if path.is_dir()):
        game_state_file = game_dir / "game_state.json"
        if not game_state_file.exists():
            continue
        game_state = read_json(game_state_file)
        results.append(
            {
                "game_id": game_state.get("game_id", game_dir.name),
                "status": game_state.get("status", "unknown"),
            }
        )
    return results


def _normalize_status(
    task_state: str,
    result_payload: dict[str, Any] | None = None,
    error: str | None = None,
    run_state_payload: dict[str, Any] | None = None,
) -> tuple[str, str]:
    if run_state_payload:
        current_phase = run_state_payload.get("current_phase")
        run_status = run_state_payload.get("status")
        if current_phase == "parallel_batch_finished":
            if run_status == "transform_completed":
                return "completed", "parallel batch finished successfully"
            if run_status in {"transform_failed", "transform_incomplete", "transform_timeout"}:
                return "failed", f"parallel batch finished with status {run_status}"
            return "completed", "parallel batch finished"
        if run_status in {"created", "running"} or task_state in {"PENDING", "RECEIVED", "STARTED", "RETRY"}:
            return "wip", f"workflow phase: {current_phase}"
    if task_state == "PENDING":
        return "idle", "waiting for worker pickup"
    if task_state in {"RECEIVED", "STARTED", "RETRY"}:
        return "wip", "workflow is running"
    if task_state == "SUCCESS":
        workflow_status = None
        if isinstance(result_payload, dict):
            workflow_status = result_payload.get("status")
        if workflow_status == "failed":
            return "failed", "workflow reported failure"
        return "completed", "workflow completed successfully"
    if error:
        return "failed", error
    return "failed", "workflow failed"


@app.post("/jobs/game-refactoring", response_model=AdvancedWorkflowResponse)
def submit_game_refactoring_job(request: AdvancedWorkflowRequest) -> AdvancedWorkflowResponse:
    matched_games, missing_ids = _resolve_raw_games(request.raw_game_ids)
    if missing_ids:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "raw_game_ids_not_found",
                "missing_ids": missing_ids,
                "matched_ids": [entry["game_id"] for entry in matched_games],
            },
        )

    payload = request.model_dump(by_alias=True)
    payload.pop("raw_game_ids", None)

    task_id_value = _new_task_id()
    manifest_path = _write_internal_manifest(payload["id"], task_id_value, matched_games)
    payload["games_manifest_source"] = str(manifest_path)
    payload["run_id"] = task_id_value

    last_error: str | None = None
    for _ in range(5):
        try:
            async_result = run_game_refactoring_workflow.apply_async(args=[payload], task_id=task_id_value)
            status, comment = _normalize_status("PENDING")
            return AdvancedWorkflowResponse(
                task_id=async_result.id,
                workflow_id=payload["id"],
                submitted=True,
                status=status,
                comment=f"{comment}; validated {len(matched_games)} raw game ids",
                result_url=f"/jobs/celery/{async_result.id}",
                matched_ids=[entry["game_id"] for entry in matched_games],
            )
        except Exception as exc:
            last_error = str(exc)
            time.sleep(1)

    raise HTTPException(
        status_code=503,
        detail={
            "error": "celery_enqueue_failed",
            "comment": "unable to reach redis/celery after retries",
            "details": last_error,
        },
    )


@app.get("/jobs/celery/{task_id}")
def get_celery_task(task_id: str) -> dict[str, Any]:
    result = celery_app.AsyncResult(task_id)
    state = result.state
    result_payload: dict[str, Any] | None = None
    error: str | None = None
    run_state_payload: dict[str, Any] | None = None
    game_results: list[dict[str, str]] = []

    if result.successful():
        try:
            if isinstance(result.result, dict):
                result_payload = result.result
            else:
                result_payload = {"value": result.result}
        except Exception:
            result_payload = None
    elif result.failed():
        error = str(result.result)

    run_dir_value = result_payload.get("run_dir") if isinstance(result_payload, dict) else None
    if isinstance(run_dir_value, str):
        run_dir = Path(run_dir_value)
        run_state_file = run_dir / "run_state.json"
        if run_state_file.exists():
            run_state_payload = read_json(run_state_file)
            game_results = _summarize_game_results(run_dir)

    status, comment = _normalize_status(state, result_payload, error, run_state_payload)

    payload: dict[str, Any] = {
        "taskId": task_id,
        "state": state,
        "status": status,
        "comment": comment,
    }
    if result_payload is not None:
        payload["result"] = result_payload
    if run_state_payload is not None:
        payload["run_state"] = run_state_payload
        payload["results"] = game_results
    if error is not None:
        payload["error"] = error
    return payload
