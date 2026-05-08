"""Status normalization for KIE task responses."""

from __future__ import annotations

import json
from typing import Any


MARKET_STATUS_MAP = {
    "waiting": "queued",
    "queuing": "queued",
    "generating": "running",
    "success": "succeeded",
    "fail": "failed",
}

VEO_STATUS_MAP = {
    0: "running",
    1: "succeeded",
    2: "failed",
    3: "failed",
}

SUNO_MUSIC_STATUS_MAP = {
    "PENDING": "queued",
    "TEXT_SUCCESS": "running",
    "FIRST_SUCCESS": "running",
    "SUCCESS": "succeeded",
    "CREATE_TASK_FAILED": "failed",
    "GENERATE_MUSIC_FAILED": "failed",
    "CALLBACK_EXCEPTION": "failed",
    "SENSITIVE_WORD_ERROR": "failed",
}

SUNO_LYRICS_STATUS_MAP = {
    "PENDING": "queued",
    "SUCCESS": "succeeded",
    "CREATE_TASK_FAILED": "failed",
    "GENERATE_LYRICS_FAILED": "failed",
    "CALLBACK_EXCEPTION": "failed",
    "SENSITIVE_WORD_ERROR": "failed",
}


def normalize_submit(response: dict[str, Any], *, model: str) -> dict[str, Any]:
    task_id = ((response.get("data") or {}).get("taskId"))
    if response.get("code") != 200 or not task_id:
        return {
            "ok": False,
            "status": "failed",
            "model": model,
            "error": {
                "code": response.get("code"),
                "message": response.get("msg") or "Task submission failed",
            },
            "raw": response,
        }
    return {"ok": True, "jobId": task_id, "status": "queued", "model": model}


def normalize_market_status(response: dict[str, Any]) -> dict[str, Any]:
    data = response.get("data") or {}
    task_id = data.get("taskId")
    state = data.get("state")
    status = MARKET_STATUS_MAP.get(state, "unknown")

    output_urls = _extract_market_urls(data.get("resultJson"))
    result = {
        "ok": status != "failed",
        "jobId": task_id,
        "status": status,
        "model": data.get("model"),
    }
    if output_urls:
        result["outputUrls"] = output_urls
        result["outputUrl"] = output_urls[0]
    if status == "failed":
        result["error"] = {
            "code": data.get("failCode") or response.get("code"),
            "message": data.get("failMsg") or response.get("msg") or "Task failed",
        }
    return result


def normalize_veo_status(response: dict[str, Any]) -> dict[str, Any]:
    data = response.get("data") or {}
    task_id = data.get("taskId")
    flag = data.get("successFlag")
    status = VEO_STATUS_MAP.get(flag, "unknown")
    response_payload = data.get("response") or {}
    output_urls = []
    for key in ("resultUrls", "fullResultUrls", "originUrls"):
        values = response_payload.get(key)
        if isinstance(values, list):
            output_urls.extend(values)

    result = {"ok": status != "failed", "jobId": task_id, "status": status, "kind": "veo"}
    if output_urls:
        result["outputUrls"] = output_urls
        result["outputUrl"] = output_urls[0]
    if status == "failed":
        result["error"] = {
            "code": data.get("errorCode") or response.get("code"),
            "message": data.get("errorMessage") or response.get("msg") or "Veo task failed",
        }
    return result


def normalize_suno_music_status(response: dict[str, Any], *, model: str | None = None) -> dict[str, Any]:
    data = response.get("data") or {}
    task_id = data.get("taskId")
    raw_status = data.get("status")
    status = SUNO_MUSIC_STATUS_MAP.get(raw_status, "unknown")
    response_payload = data.get("response") or {}
    output_urls = _extract_suno_urls(response_payload)

    result: dict[str, Any] = {
        "ok": status != "failed",
        "jobId": task_id,
        "status": status,
        "model": model or data.get("type"),
    }
    if output_urls:
        result["outputUrls"] = output_urls
        result["outputUrl"] = output_urls[0]
    if response_payload:
        result["response"] = response_payload
    if status == "failed":
        result["error"] = {
            "code": data.get("errorCode") or response.get("code"),
            "message": data.get("errorMessage") or response.get("msg") or "Suno task failed",
        }
    return result


def normalize_suno_lyrics_status(response: dict[str, Any], *, model: str | None = None) -> dict[str, Any]:
    data = response.get("data") or {}
    task_id = data.get("taskId")
    raw_status = data.get("status")
    status = SUNO_LYRICS_STATUS_MAP.get(raw_status, "unknown")
    response_payload = data.get("response") or {}

    result: dict[str, Any] = {
        "ok": status != "failed",
        "jobId": task_id,
        "status": status,
        "model": model or data.get("type"),
    }
    if response_payload:
        result["response"] = response_payload
        lyrics = response_payload.get("data")
        if isinstance(lyrics, list):
            result["lyrics"] = lyrics
    if status == "failed":
        result["error"] = {
            "code": data.get("errorCode") or response.get("code"),
            "message": data.get("errorMessage") or response.get("msg") or "Lyrics task failed",
        }
    return result


def _extract_market_urls(result_json: str | None) -> list[str]:
    if not result_json:
        return []
    try:
        parsed = json.loads(result_json)
    except json.JSONDecodeError:
        return []

    urls: list[str] = []
    result_urls = parsed.get("resultUrls")
    if isinstance(result_urls, list):
        urls.extend(str(item) for item in result_urls)

    for key in ("firstFrameUrl", "lastFrameUrl"):
        values = parsed.get(key)
        if isinstance(values, list):
            urls.extend(str(item) for item in values)

    return urls


def _extract_suno_urls(response_payload: dict[str, Any]) -> list[str]:
    urls: list[str] = []

    suno_data = response_payload.get("sunoData")
    if isinstance(suno_data, list):
        for item in suno_data:
            if not isinstance(item, dict):
                continue
            for key in ("audioUrl", "sourceAudioUrl", "streamAudioUrl", "imageUrl", "videoUrl"):
                value = item.get(key)
                if isinstance(value, str) and value:
                    urls.append(value)

    for key in ("resultUrls", "audioUrls"):
        values = response_payload.get(key)
        if isinstance(values, list):
            urls.extend(str(item) for item in values)

    deduped: list[str] = []
    seen: set[str] = set()
    for url in urls:
        if url in seen:
            continue
        seen.add(url)
        deduped.append(url)
    return deduped
