#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KIE_SRC = ROOT / "tools" / "kie-api" / "src"
if str(KIE_SRC) not in sys.path:
    sys.path.insert(0, str(KIE_SRC))

from kie_cli.jobs import build_job_record  # type: ignore  # noqa: E402
from kie_cli.payloads import (  # type: ignore  # noqa: E402
    SUNO_MUSIC_MODEL,
    SUNO_SOUNDS_MODEL,
    build_suno_music_payload,
    build_suno_sounds_payload,
)
from kie_cli.routes import route_for_model  # type: ignore  # noqa: E402


def main() -> int:
    sounds_route = route_for_model(SUNO_SOUNDS_MODEL)
    music_route = route_for_model(SUNO_MUSIC_MODEL)
    sounds_payload = build_suno_sounds_payload(prompt="Very short jump sound effect", model="V5")
    music_payload = build_suno_music_payload(prompt="Short magical menu music", instrumental=True)
    example_job = build_job_record(
        job_id="example_task_123",
        model=SUNO_SOUNDS_MODEL,
        submitted_payload=sounds_payload,
        resolved_media=[],
        raw_submit_response={"code": 200, "data": {"taskId": "example_task_123"}},
    )

    summary = {
        "routes": {
            "suno_sounds": {
                "model": SUNO_SOUNDS_MODEL,
                "submit_endpoint": sounds_route.submit_endpoint,
                "status_endpoint": sounds_route.status_endpoint,
                "route": sounds_route.route,
            },
            "suno_music": {
                "model": SUNO_MUSIC_MODEL,
                "submit_endpoint": music_route.submit_endpoint,
                "status_endpoint": music_route.status_endpoint,
                "route": music_route.route,
            },
        },
        "payload_examples": {
            "sounds": sounds_payload,
            "music": music_payload,
        },
        "workflow": [
            "submit task with kie-cli suno sounds|music",
            "normalize submit response to get jobId",
            "persist job record with build_job_record/write_job_record",
            "poll until terminal state via kie-cli wait or poll_until_complete",
            "read outputUrl/outputUrls from normalized Suno status payload",
            "download asset, rename to expected variant filename, move into library tree",
        ],
        "example_job_record": {
            "jobId": example_job.jobId,
            "model": example_job.model,
            "submitEndpoint": example_job.submitEndpoint,
            "statusEndpoint": example_job.statusEndpoint,
            "status": example_job.status,
        },
    }

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())