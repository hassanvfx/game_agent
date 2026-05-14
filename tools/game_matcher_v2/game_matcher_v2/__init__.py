"""Deterministic tag-family matcher built from app.json."""

from .builder import (
    DEFAULT_APP_JSON_PATH,
    DEFAULT_ARTIFACTS_DIR,
    DEFAULT_METADATA_PATH,
    build_artifacts,
    ensure_artifacts,
)
from .scorer import score_games

__all__ = [
    "DEFAULT_APP_JSON_PATH",
    "DEFAULT_ARTIFACTS_DIR",
    "DEFAULT_METADATA_PATH",
    "build_artifacts",
    "ensure_artifacts",
    "score_games",
]