import json
import logging
import os
import time

from app.celery_app import celery_app
from tools.tool_cline import run_cline_check
from tools.tool_playwright import run_playwright_check

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.run_mock_workflow")
def run_mock_workflow() -> dict:
    delay_seconds = int(os.getenv("CELERY_TASK_DELAY_SECONDS", "2"))
    results = []

    logger.info("Starting mock workflow")

    for step_name, step_fn in (
        ("cline", run_cline_check),
        ("playwright", run_playwright_check),
    ):
        logger.info("Running step: %s", step_name)
        result = step_fn()
        logger.info("Step result for %s: %s", step_name, json.dumps(result))
        results.append(result)
        time.sleep(delay_seconds)

    workflow_result = {"status": "success", "steps": results}
    logger.info("Workflow finished: %s", json.dumps(workflow_result))
    return workflow_result