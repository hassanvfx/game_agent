"""HTTP client wrappers for KIE generation, status, and upload APIs."""

from __future__ import annotations

import mimetypes
from pathlib import Path
from typing import Any

import requests

from .config import KieConfig
from .errors import ApiError, ConfigurationError


class KieClient:
    def __init__(self, config: KieConfig, *, request_timeout: int | float = 60):
        self.config = config
        self.request_timeout = request_timeout

    def _headers(self) -> dict[str, str]:
        if not self.config.api_key:
            raise ConfigurationError("KIE_API_KEY is required. Add it to .env or the environment.")
        return {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }

    def create_market_task(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._post_json("/api/v1/jobs/createTask", payload)

    def get_market_task(self, task_id: str) -> dict[str, Any]:
        return self._get_json("/api/v1/jobs/recordInfo", {"taskId": task_id})

    def create_veo_task(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._post_json("/api/v1/veo/generate", payload)

    def get_veo_task(self, task_id: str) -> dict[str, Any]:
        return self._get_json("/api/v1/veo/record-info", {"taskId": task_id})

    def create_gpt_5_2_chat_completion(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._post_json("/gpt-5-2/v1/chat/completions", payload)

    def create_gemini_3_pro_chat_completion(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._post_json("/gemini-3-pro/v1/chat/completions", payload)

    def create_suno_music_task(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._post_json("/api/v1/generate", payload)

    def get_suno_music_task(self, task_id: str) -> dict[str, Any]:
        return self._get_json("/api/v1/generate/record-info", {"taskId": task_id})

    def create_suno_lyrics_task(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._post_json("/api/v1/lyrics", payload)

    def get_suno_lyrics_task(self, task_id: str) -> dict[str, Any]:
        return self._get_json("/api/v1/lyrics/record-info", {"taskId": task_id})

    def create_suno_sounds_task(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._post_json("/api/v1/generate/sounds", payload)

    def _post_json(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        response = requests.post(
            f"{self.config.base_url}{path}",
            headers=self._headers(),
            json=payload,
            timeout=self.request_timeout,
        )
        return self._decode_response(response)

    def _get_json(self, path: str, params: dict[str, Any]) -> dict[str, Any]:
        response = requests.get(
            f"{self.config.base_url}{path}",
            headers=self._headers(),
            params=params,
            timeout=self.request_timeout,
        )
        return self._decode_response(response)

    @staticmethod
    def _decode_response(response: requests.Response) -> dict[str, Any]:
        try:
            data = response.json()
        except ValueError as exc:
            raise ApiError(
                f"KIE returned non-JSON response with HTTP {response.status_code}",
                code=response.status_code,
                raw=response.text,
            ) from exc

        if response.status_code >= 400:
            raise ApiError(
                str(data.get("msg") or f"HTTP {response.status_code}"),
                code=data.get("code", response.status_code),
                raw=data,
            )
        return data


class KieUploadClient:
    def __init__(self, config: KieConfig):
        self.config = config

    def _headers(self) -> dict[str, str]:
        if not self.config.api_key:
            raise ConfigurationError("KIE_API_KEY is required. Add it to .env or the environment.")
        return {"Authorization": f"Bearer {self.config.api_key}"}

    def upload_file(
        self,
        file_path: str | Path,
        *,
        upload_path: str = "kie-cli/uploads",
        file_name: str | None = None,
    ) -> dict[str, Any]:
        path = Path(file_path)
        if not path.is_file():
            raise FileNotFoundError(f"Input file does not exist: {path}")

        guessed_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        with path.open("rb") as handle:
            files = {"file": (file_name or path.name, handle, guessed_type)}
            data = {"uploadPath": upload_path}
            if file_name:
                data["fileName"] = file_name

            response = requests.post(
                f"{self.config.upload_base_url}/api/file-stream-upload",
                headers=self._headers(),
                files=files,
                data=data,
                timeout=120,
            )

        decoded = KieClient._decode_response(response)
        if not decoded.get("success", decoded.get("code") == 200):
            raise ApiError(
                str(decoded.get("msg") or "Upload failed"),
                code=decoded.get("code"),
                raw=decoded,
            )

        payload = decoded.get("data") or {}
        if not payload.get("downloadUrl"):
            raise ApiError("Upload response did not include data.downloadUrl", raw=decoded)
        return payload
