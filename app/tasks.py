import json
import logging
import os
import subprocess
from pathlib import Path

from app.celery_app import celery_app
from tools.game_actor_mock.game_actor_mock.mock_actor import run_game_actor_mock_task

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[1]
GAME_REFACTORING_ROOT = ROOT / "tools" / "game_refactoring"
GAME_WORKFLOW_SCRIPT = GAME_REFACTORING_ROOT / "scripts" / "game_workflow.py"


@celery_app.task(name="app.tasks.run_mock_workflow")
def run_mock_workflow() -> dict:
    workflow_result = {
        "status": "success",
        "steps": [
            {
                "name": "mock_workflow",
                "status": "completed",
                "message": "Legacy mock workflow placeholder executed successfully.",
            }
        ],
    }
    logger.info("Workflow finished: %s", json.dumps(workflow_result))
    return workflow_result


@celery_app.task(bind=True, name="app.tasks.run_game_actor_mock")
def run_game_actor_mock(self, run_id: str, runs_root_value: str) -> dict:
    logger.info("Starting game_actor_mock run_id=%s runs_root=%s", run_id, runs_root_value)
    result = run_game_actor_mock_task(self.request.id, run_id, runs_root_value)
    logger.info("game_actor_mock result: %s", json.dumps(result))
    return result


@celery_app.task(bind=True, name="app.tasks.run_game_refactoring_workflow")
def run_game_refactoring_workflow(self, workflow_args: dict) -> dict:
    logger.info("Starting game_refactoring workflow: %s", json.dumps(workflow_args))
    workflow_id = workflow_args.get("workflow_id") or workflow_args.get("id")
    if not workflow_id:
        raise ValueError("workflow_id is required")

    command = [
        "python3",
        str(GAME_WORKFLOW_SCRIPT),
        "--json",
        "--id",
        workflow_id,
        "--games-manifest-source",
        workflow_args["games_manifest_source"],
        "--pipeline",
        workflow_args.get("pipeline", "v2"),
        "--model",
        workflow_args.get("model", "gpt-5.4"),
        "--agent-timeout",
        str(workflow_args.get("agent_timeout", 3600)),
        "--max-concurrency",
        str(workflow_args.get("max_concurrency", 2)),
        "--poll-seconds",
        str(workflow_args.get("poll_seconds", 5.0)),
        "--stale-heartbeat-seconds",
        str(workflow_args.get("stale_heartbeat_seconds", 900)),
        "--source-mode",
        workflow_args.get("source_mode", "copy"),
    ]
    optional_pairs = [
        ("run_id", "--run-id"),
        ("runs_root", "--runs-root"),
        ("remix_prompt", "--remix-prompt"),
        ("remix_prompt_file", "--remix-prompt-file"),
        ("playwright_port_base", "--playwright-port-base"),
        ("playwright_port_pool_size", "--playwright-port-pool-size"),
        ("playwright_port_lease_ttl_seconds", "--playwright-port-lease-ttl-seconds"),
    ]
    for key, flag in optional_pairs:
        value = workflow_args.get(key)
        if value is not None:
            command.extend([flag, str(value)])
    if workflow_args.get("dry_run_operators"):
        command.append("--dry-run-operators")
    if workflow_args.get("dry_run_spec_adaptor"):
        command.append("--dry-run-spec-adaptor")

    completed = subprocess.run(
        command,
        cwd=str(GAME_REFACTORING_ROOT),
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(completed.stdout)
    payload["celery_task_id"] = self.request.id
    logger.info("game_refactoring workflow result: %s", json.dumps(payload))
    return payload