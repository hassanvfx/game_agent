"""Domain exceptions for kie-cli."""

from __future__ import annotations


class KieCliError(Exception):
    """Base CLI error."""


class ConfigurationError(KieCliError):
    """Raised when required local configuration is missing."""


class ApiError(KieCliError):
    """Raised when KIE returns an unsuccessful API response."""

    def __init__(self, message: str, *, code: int | str | None = None, raw: object = None):
        super().__init__(message)
        self.code = code
        self.raw = raw
