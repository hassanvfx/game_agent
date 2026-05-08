"""Configuration loading for kie-cli."""

from __future__ import annotations

from dataclasses import dataclass
from os import environ, getenv
from pathlib import Path

try:
    from dotenv import load_dotenv as python_dotenv_load
except ImportError:  # pragma: no cover - exercised when dependency is absent locally.
    python_dotenv_load = None


DEFAULT_BASE_URL = "https://api.kie.ai"
DEFAULT_UPLOAD_BASE_URL = "https://kieai.redpandaai.co"


@dataclass(frozen=True)
class KieConfig:
    api_key: str | None
    base_url: str = DEFAULT_BASE_URL
    upload_base_url: str = DEFAULT_UPLOAD_BASE_URL

    @property
    def has_api_key(self) -> bool:
        return bool(self.api_key)


def load_config() -> KieConfig:
    load_dotenv()
    return KieConfig(
        api_key=getenv("KIE_API_KEY"),
        base_url=getenv("KIE_BASE_URL", DEFAULT_BASE_URL).rstrip("/"),
        upload_base_url=getenv("KIE_UPLOAD_BASE_URL", DEFAULT_UPLOAD_BASE_URL).rstrip("/"),
    )


def load_dotenv() -> None:
    """Load .env values.

    Prefer python-dotenv when installed. A tiny fallback keeps dry-run tests and
    local development usable before dependencies are installed.
    """

    if python_dotenv_load is not None:
        python_dotenv_load()
        return

    env_path = Path(".env")
    if not env_path.is_file():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue

        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        environ.setdefault(key, value)
