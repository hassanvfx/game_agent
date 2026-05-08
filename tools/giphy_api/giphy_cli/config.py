from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


class ConfigError(RuntimeError):
    """Raised when required configuration is missing."""


@dataclass(frozen=True)
class Settings:
    api_key: str


def load_settings() -> Settings:
    """Load configuration from environment variables and .env."""
    load_dotenv()

    api_key = os.getenv("GIPHY_API_KEY", "").strip()
    if not api_key:
        raise ConfigError(
            "Missing GIPHY_API_KEY. Add it to your environment or .env file."
        )

    return Settings(api_key=api_key)