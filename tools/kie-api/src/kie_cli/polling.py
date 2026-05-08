"""Polling helpers for asynchronous KIE jobs."""

from __future__ import annotations

import time
from typing import Any, Protocol

from .jobs import JobRecord
from .routes import route_for_model


class StatusClient(Protocol):
    def get_market_task(self, task_id: str) -> dict[str, Any]:
        ...

    def get_veo_task(self, task_id: str) -> dict[str, Any]:
        ...

    def get_suno_music_task(self, task_id: str) -> dict[str, Any]:
        ...

    def get_suno_lyrics_task(self, task_id: str) -> dict[str, Any]:
        ...


def get_status_once(
    *,
    client: StatusClient,
    job_id: str,
    model: str,
    market_normalizer,
    veo_normalizer,
    suno_music_normalizer=None,
    suno_lyrics_normalizer=None,
) -> dict[str, Any]:
    route = route_for_model(model)
    if route.route == "veo":
        result = veo_normalizer(client.get_veo_task(job_id))
    elif route.route == "suno_music":
        if suno_music_normalizer is None:
            raise ValueError("suno_music_normalizer is required for Suno music/sounds polling")
        result = suno_music_normalizer(client.get_suno_music_task(job_id), model=model)
    elif route.route == "suno_lyrics":
        if suno_lyrics_normalizer is None:
            raise ValueError("suno_lyrics_normalizer is required for Suno lyrics polling")
        result = suno_lyrics_normalizer(client.get_suno_lyrics_task(job_id), model=model)
    else:
        result = market_normalizer(client.get_market_task(job_id))
    result["model"] = result.get("model") or model
    return result


def poll_until_complete(
    *,
    client: StatusClient,
    job_id: str,
    model: str,
    market_normalizer,
    veo_normalizer,
    suno_music_normalizer=None,
    suno_lyrics_normalizer=None,
    poll_interval: float = 5.0,
    timeout: float = 900.0,
    sleep=time.sleep,
    clock=time.monotonic,
) -> dict[str, Any]:
    started = clock()
    polls = 0
    last: dict[str, Any] | None = None

    while True:
        polls += 1
        last = get_status_once(
            client=client,
            job_id=job_id,
            model=model,
            market_normalizer=market_normalizer,
            veo_normalizer=veo_normalizer,
            suno_music_normalizer=suno_music_normalizer,
            suno_lyrics_normalizer=suno_lyrics_normalizer,
        )
        status = last.get("status")
        elapsed = clock() - started

        if status in {"succeeded", "failed"}:
            last["polls"] = polls
            last["elapsedSeconds"] = round(elapsed, 3)
            return last

        if elapsed >= timeout:
            return {
                "ok": False,
                "jobId": job_id,
                "model": model,
                "status": "timeout",
                "polls": polls,
                "elapsedSeconds": round(elapsed, 3),
                "lastStatus": last,
                "error": {
                    "code": "POLL_TIMEOUT",
                    "message": f"Task did not complete within {timeout:g} seconds",
                },
            }

        sleep(poll_interval)


def poll_job_record(
    *,
    client: StatusClient,
    record: JobRecord,
    market_normalizer,
    veo_normalizer,
    suno_music_normalizer=None,
    suno_lyrics_normalizer=None,
    poll_interval: float = 5.0,
    timeout: float = 900.0,
) -> dict[str, Any]:
    return poll_until_complete(
        client=client,
        job_id=record.jobId,
        model=record.model,
        market_normalizer=market_normalizer,
        veo_normalizer=veo_normalizer,
        suno_music_normalizer=suno_music_normalizer,
        suno_lyrics_normalizer=suno_lyrics_normalizer,
        poll_interval=poll_interval,
        timeout=timeout,
    )
