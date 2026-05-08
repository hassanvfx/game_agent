import json

from app.tasks import run_mock_workflow


if __name__ == "__main__":
    result = run_mock_workflow.delay()
    print(json.dumps({"task_id": result.id}))