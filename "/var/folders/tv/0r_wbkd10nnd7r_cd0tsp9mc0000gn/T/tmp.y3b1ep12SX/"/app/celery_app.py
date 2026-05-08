import os

from celery import Celery


def _env(name: str, default: str) -> str:
    return os.getenv(name, default)


celery_app = Celery(
    "mock_worker",
    broker=_env("CELERY_BROKER_URL", "redis://redis:6379/0"),
    backend=_env("CELERY_RESULT_BACKEND", "redis://redis:6379/1"),
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)