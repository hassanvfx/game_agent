"""Durable job record helpers for asynchronous KIE jobs."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .routes import route_for_model


SCHEMA_VERSION = 1


@dataclass(frozen=True)
class JobRecord:
    schemaVersion: int
    jobId: str
    model: str
    status: str
    submittedAt: str
    submitEndpoint: str
    statusEndpoint: str
    submittedPayload: dict[str, Any]
    resolvedMedia: list[dict[str, Any]]
    rawSubmitResponse: dict[str, Any]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def build_job_record(
    *,
    job_id: str,
    model: str,
    status: str = "queued",
    submitted_payload: dict[str, Any] | None = None,
    resolved_media: list[dict[str, Any]] | None = None,
    raw_submit_response: dict[str, Any] | None = None,
) -> JobRecord:
    route = route_for_model(model)
    return JobRecord(
        schemaVersion=SCHEMA_VERSION,
        jobId=job_id,
        model=model,
        status=status,
        submittedAt=utc_now(),
        submitEndpoint=route.submit_endpoint,
        statusEndpoint=route.status_endpoint,
        submittedPayload=submitted_payload or {},
        resolvedMedia=resolved_media or [],
        rawSubmitResponse=raw_submit_response or {},
    )


def write_job_record(record: JobRecord, path: str | Path) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(asdict(record), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return output_path


def read_job_record(path: str | Path) -> JobRecord:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return JobRecord(**data)