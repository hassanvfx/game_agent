"""Media input resolution helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

from .client import KieUploadClient


@dataclass(frozen=True)
class ResolvedMedia:
    kind: str
    source_type: str
    original_value: str
    resolved_url: str
    uploaded: bool
    upload: dict | None = None


def is_http_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def resolve_media_inputs(
    values: list[str],
    *,
    kind: str,
    uploader: KieUploadClient | None = None,
    upload_path: str = "kie-cli/uploads",
    dry_run: bool = False,
) -> list[ResolvedMedia]:
    resolved: list[ResolvedMedia] = []
    for value in values:
        if is_http_url(value):
            resolved.append(
                ResolvedMedia(
                    kind=kind,
                    source_type="remote_url",
                    original_value=value,
                    resolved_url=value,
                    uploaded=False,
                )
            )
            continue

        parsed = urlparse(value)
        if parsed.scheme and parsed.scheme != "file":
            raise ValueError(
                f"Unsupported {kind} input URI scheme: {parsed.scheme}. "
                "Use a local path or http(s) URL."
            )

        path = Path(parsed.path if parsed.scheme == "file" else value)
        if dry_run:
            resolved.append(
                ResolvedMedia(
                    kind=kind,
                    source_type="local_path",
                    original_value=value,
                    resolved_url=f"dry-run://uploaded/{path.name}",
                    uploaded=True,
                    upload={"dryRun": True, "uploadPath": upload_path},
                )
            )
            continue

        if uploader is None:
            raise ValueError("A KieUploadClient is required to upload local files.")

        upload = uploader.upload_file(path, upload_path=upload_path)
        resolved.append(
            ResolvedMedia(
                kind=kind,
                source_type="local_path",
                original_value=value,
                resolved_url=upload["downloadUrl"],
                uploaded=True,
                upload=upload,
            )
        )

    return resolved
