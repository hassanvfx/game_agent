"""Model-based routing for KIE asynchronous jobs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .payloads import SUNO_LYRICS_MODEL, SUNO_MUSIC_MODEL, SUNO_SOUNDS_MODEL

JobRoute = Literal["market", "veo", "suno_music", "suno_lyrics"]

MARKET_STATUS_ENDPOINT = "/api/v1/jobs/recordInfo"
MARKET_SUBMIT_ENDPOINT = "/api/v1/jobs/createTask"
VEO_STATUS_ENDPOINT = "/api/v1/veo/record-info"
VEO_SUBMIT_ENDPOINT = "/api/v1/veo/generate"
SUNO_MUSIC_STATUS_ENDPOINT = "/api/v1/generate/record-info"
SUNO_MUSIC_SUBMIT_ENDPOINT = "/api/v1/generate"
SUNO_LYRICS_STATUS_ENDPOINT = "/api/v1/lyrics/record-info"
SUNO_LYRICS_SUBMIT_ENDPOINT = "/api/v1/lyrics"
SUNO_SOUNDS_SUBMIT_ENDPOINT = "/api/v1/generate/sounds"

MARKET_MODELS = {
    "nano-banana-pro",
    "gpt-image-2-text-to-image",
    "gpt-image-2-image-to-image",
    "grok-imagine/text-to-video",
    "grok-imagine/image-to-video",
}

VEO_MODELS = {
    "veo3",
    "veo3_fast",
    "veo3_lite",
}

SUNO_MUSIC_MODELS = {SUNO_MUSIC_MODEL, SUNO_SOUNDS_MODEL}
SUNO_LYRICS_MODELS = {SUNO_LYRICS_MODEL}


@dataclass(frozen=True)
class ModelRoute:
    model: str
    route: JobRoute
    submit_endpoint: str
    status_endpoint: str


def route_for_model(model: str) -> ModelRoute:
    """Return deterministic status routing metadata for a submitted model."""

    if model in MARKET_MODELS:
        return ModelRoute(
            model=model,
            route="market",
            submit_endpoint=MARKET_SUBMIT_ENDPOINT,
            status_endpoint=MARKET_STATUS_ENDPOINT,
        )

    if model in VEO_MODELS:
        return ModelRoute(
            model=model,
            route="veo",
            submit_endpoint=VEO_SUBMIT_ENDPOINT,
            status_endpoint=VEO_STATUS_ENDPOINT,
        )

    if model in SUNO_MUSIC_MODELS:
        return ModelRoute(
            model=model,
            route="suno_music",
            submit_endpoint=(
                SUNO_SOUNDS_SUBMIT_ENDPOINT if model == SUNO_SOUNDS_MODEL else SUNO_MUSIC_SUBMIT_ENDPOINT
            ),
            status_endpoint=SUNO_MUSIC_STATUS_ENDPOINT,
        )

    if model in SUNO_LYRICS_MODELS:
        return ModelRoute(
            model=model,
            route="suno_lyrics",
            submit_endpoint=SUNO_LYRICS_SUBMIT_ENDPOINT,
            status_endpoint=SUNO_LYRICS_STATUS_ENDPOINT,
        )

    supported = ", ".join(sorted(MARKET_MODELS | VEO_MODELS | SUNO_MUSIC_MODELS | SUNO_LYRICS_MODELS))
    raise ValueError(
        f"Cannot determine status endpoint for model {model!r}. "
        f"Supported async models: {supported}"
    )


def is_terminal_status(status: str) -> bool:
    return status in {"succeeded", "failed", "timeout"}