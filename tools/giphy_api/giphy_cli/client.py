from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import giphy_client
from giphy_client.rest import ApiException

from giphy_cli.config import Settings


class GiphyCliError(RuntimeError):
    """Raised for Giphy API failures surfaced to the CLI."""


@dataclass(frozen=True)
class GifResult:
    id: str
    title: str
    gif_url: str
    webp_url: str
    username: str
    rating: str
    source: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


class GiphyService:
    """Thin wrapper around the official Giphy Python client."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._api = giphy_client.DefaultApi()

    def search(
        self,
        query: str,
        *,
        limit: int = 10,
        offset: int = 0,
        rating: str | None = None,
        lang: str | None = None,
    ) -> list[GifResult]:
        try:
            response = self._api.gifs_search_get(
                self._settings.api_key,
                query,
                limit=limit,
                offset=offset,
                rating=rating,
                lang=lang,
            )
        except ApiException as exc:
            raise GiphyCliError(f"Giphy API request failed: {exc}") from exc

        return [self._normalize_gif(item) for item in getattr(response, "data", [])]

    def trending(
        self,
        *,
        limit: int = 10,
        rating: str | None = None,
    ) -> list[GifResult]:
        kwargs: dict[str, Any] = {"limit": limit}
        if rating:
            kwargs["rating"] = rating

        try:
            response = self._api.gifs_trending_get(
                self._settings.api_key,
                **kwargs,
            )
        except ApiException as exc:
            raise GiphyCliError(f"Giphy API request failed: {exc}") from exc

        return [self._normalize_gif(item) for item in getattr(response, "data", [])]

    def translate(self, phrase: str) -> GifResult:
        try:
            response = self._api.gifs_translate_get(
                self._settings.api_key,
                phrase,
            )
        except ApiException as exc:
            raise GiphyCliError(f"Giphy API request failed: {exc}") from exc

        return self._normalize_gif(getattr(response, "data", response))

    def random(self, *, tag: str | None = None, rating: str | None = None) -> GifResult:
        try:
            response = self._api.gifs_random_get(
                self._settings.api_key,
                tag=tag,
                rating=rating,
            )
        except ApiException as exc:
            raise GiphyCliError(f"Giphy API request failed: {exc}") from exc

        return self._normalize_gif(getattr(response, "data", response))

    def _normalize_gif(self, gif: Any) -> GifResult:
        gif_id = str(getattr(gif, "id", "") or "")
        gif_url = f"https://i.giphy.com/{gif_id}.gif" if gif_id else ""
        webp_url = f"https://i.giphy.com/{gif_id}.webp" if gif_id else ""

        return GifResult(
            id=gif_id,
            title=str(getattr(gif, "title", "") or ""),
            gif_url=str(gif_url),
            webp_url=str(webp_url),
            username=str(getattr(gif, "username", "") or ""),
            rating=str(getattr(gif, "rating", "") or ""),
            source=str(getattr(gif, "source", "") or ""),
        )
