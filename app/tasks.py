import json
import logging
import os

from app.celery_app import celery_app
from tools.tool_game_generator import run_game_generator_check

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.run_mock_workflow")
def run_mock_workflow() -> dict:
    logger.info("Starting real workflow via game_generator orchestrator")
    result = run_game_generator_check()
    logger.info("game_generator result: %s", json.dumps(result))
    if result.get("status") != "completed":
        raise RuntimeError(f"game_generator finished with non-success status: {result.get('status')}")
    workflow_result = {"status": "success", "steps": [result]}
    logger.info("Workflow finished: %s", json.dumps(workflow_result))
    return workflow_result