#!/usr/bin/env python3
"""Shared path helpers for the mirrored library audio root."""

from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[3]
MIRRORED_LIBRARY_ROOT = ROOT / "tools" / "library" / "assets" / "audios"
LEGACY_LIBRARY_ROOT = ROOT / "tools" / "library" / "audio_library"
ASSETS_AUDIOS_PREFIX = "assets/audios/"


def resolve_library_root(preferred: Path | None = None) -> Path:
    if preferred is not None:
        return preferred
    if MIRRORED_LIBRARY_ROOT.exists():
        return MIRRORED_LIBRARY_ROOT
    return LEGACY_LIBRARY_ROOT


def strip_assets_audios_prefix(location: str) -> str:
    normalized = location.lstrip("/")
    if normalized.startswith(ASSETS_AUDIOS_PREFIX):
        return normalized[len(ASSETS_AUDIOS_PREFIX) :]
    return normalized


def location_from_url(url: str) -> str:
    return urlparse(url).path.lstrip("/")


def local_path_from_location(audio_root: Path, location: str) -> Path:
    return audio_root / Path(strip_assets_audios_prefix(location))
