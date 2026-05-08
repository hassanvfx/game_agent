#!/usr/bin/env python3
"""Download the KIE documentation corpus referenced by docs.kie.ai/llms.txt.

The script intentionally shells out to curl for network fetches so it mirrors the
manual workflow and avoids adding Python HTTP dependencies.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse


LLMS_URL = "https://docs.kie.ai/llms.txt"
DOCS_HOST = "docs.kie.ai"
DEFAULT_RAW_DIR = Path("docs/kie-ai/raw")
DEFAULT_MANIFEST_PATH = Path("docs/kie-ai/manifest.json")
URL_PATTERN = re.compile(r"https://docs\.kie\.ai/[^\s)\]]+")


@dataclass
class DownloadRecord:
    url: str
    local_path: str
    status: str
    http_code: int | None
    sha256: str | None
    byte_size: int | None
    downloaded_at: str
    error: str | None


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def run_curl(url: str, timeout_seconds: int) -> tuple[int, str, bytes, str]:
    command = [
        "curl",
        "-L",
        "--silent",
        "--show-error",
        "--max-time",
        str(timeout_seconds),
        "--write-out",
        "\n%{http_code}",
        url,
    ]
    result = subprocess.run(command, capture_output=True, check=False)

    stdout = result.stdout
    stderr = result.stderr.decode("utf-8", errors="replace").strip()

    if b"\n" not in stdout:
        return result.returncode, "000", stdout, stderr

    body, http_code_bytes = stdout.rsplit(b"\n", 1)
    http_code = http_code_bytes.decode("ascii", errors="replace").strip()
    return result.returncode, http_code, body, stderr


def extract_doc_urls(llms_text: str) -> list[str]:
    seen: set[str] = set()
    urls: list[str] = []

    for match in URL_PATTERN.finditer(llms_text):
        url = match.group(0).rstrip(".,:")
        if url in seen:
            continue
        seen.add(url)
        urls.append(url)

    return urls


def local_path_for_url(url: str, raw_dir: Path) -> Path:
    parsed = urlparse(url)
    if parsed.netloc != DOCS_HOST:
        raise ValueError(f"Unsupported host for docs mirror: {url}")

    path = parsed.path.lstrip("/")
    if not path:
        path = "index.md"

    if not path.endswith(".md") and not path.endswith(".txt"):
        path = f"{path.rstrip('/')}/index.md"

    return raw_dir / path


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_bytes(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def is_success_status(status: str) -> bool:
    return status in {"downloaded", "cached"}


def download_one(url: str, raw_dir: Path, timeout_seconds: int) -> DownloadRecord:
    local_path = local_path_for_url(url, raw_dir)
    downloaded_at = utc_now()

    if local_path.exists():
        body = local_path.read_bytes()
        return DownloadRecord(
            url=url,
            local_path=str(local_path),
            status="cached",
            http_code=None,
            sha256=sha256_bytes(body),
            byte_size=len(body),
            downloaded_at=downloaded_at,
            error=None,
        )

    try:
        return_code, http_code_text, body, stderr = run_curl(url, timeout_seconds)
        http_code = int(http_code_text) if http_code_text.isdigit() else None
        ok = return_code == 0 and http_code is not None and 200 <= http_code < 300

        if ok:
            write_bytes(local_path, body)
            return DownloadRecord(
                url=url,
                local_path=str(local_path),
                status="downloaded",
                http_code=http_code,
                sha256=sha256_bytes(body),
                byte_size=len(body),
                downloaded_at=downloaded_at,
                error=None,
            )

        error_parts = []
        if return_code != 0:
            error_parts.append(f"curl exited {return_code}")
        if http_code is not None:
            error_parts.append(f"HTTP {http_code}")
        if stderr:
            error_parts.append(stderr)

        return DownloadRecord(
            url=url,
            local_path=str(local_path),
            status="failed",
            http_code=http_code,
            sha256=None,
            byte_size=None,
            downloaded_at=downloaded_at,
            error="; ".join(error_parts) or "unknown download failure",
        )
    except Exception as exc:  # noqa: BLE001 - keep manifest complete.
        return DownloadRecord(
            url=url,
            local_path=str(local_path),
            status="failed",
            http_code=None,
            sha256=None,
            byte_size=None,
            downloaded_at=downloaded_at,
            error=str(exc),
        )


def write_manifest(
    manifest_path: Path,
    llms_record: DownloadRecord,
    records: Iterable[DownloadRecord],
) -> None:
    record_list = list(records)
    manifest = {
        "source": LLMS_URL,
        "generated_at": utc_now(),
        "counts": {
            "total_docs": len(record_list),
            "available": sum(1 for item in record_list if is_success_status(item.status)),
            "downloaded": sum(1 for item in record_list if item.status == "downloaded"),
            "cached": sum(1 for item in record_list if item.status == "cached"),
            "failed": sum(1 for item in record_list if item.status == "failed"),
        },
        "llms": asdict(llms_record),
        "documents": [asdict(item) for item in record_list],
    }

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download all KIE docs linked from https://docs.kie.ai/llms.txt."
    )
    parser.add_argument("--raw-dir", type=Path, default=DEFAULT_RAW_DIR)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST_PATH)
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--limit", type=int, default=0, help="Optional test limit.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)

    llms_local_path = args.raw_dir / "llms.txt"
    llms_download = download_one(LLMS_URL, args.raw_dir, args.timeout)

    if not is_success_status(llms_download.status):
        write_manifest(args.manifest, llms_download, [])
        print(f"Failed to download {LLMS_URL}: {llms_download.error}", file=sys.stderr)
        return 1

    # Keep llms.txt at the root of the mirror, not nested by URL path.
    generated_llms_path = local_path_for_url(LLMS_URL, args.raw_dir)
    if generated_llms_path != llms_local_path and generated_llms_path.exists():
        llms_local_path.parent.mkdir(parents=True, exist_ok=True)
        llms_local_path.write_bytes(generated_llms_path.read_bytes())
    llms_download.local_path = str(llms_local_path)

    llms_text = llms_local_path.read_text(encoding="utf-8")
    urls = [url for url in extract_doc_urls(llms_text) if url != LLMS_URL]
    if args.limit > 0:
        urls = urls[: args.limit]

    records: list[DownloadRecord] = []
    for index, url in enumerate(urls, start=1):
        record = download_one(url, args.raw_dir, args.timeout)
        records.append(record)
        print(
            f"[{index:03d}/{len(urls):03d}] {record.status.upper():10s} "
            f"{record.http_code or '-'} {url} -> {record.local_path}"
        )

    write_manifest(args.manifest, llms_download, records)

    available = sum(1 for item in records if is_success_status(item.status))
    downloaded = sum(1 for item in records if item.status == "downloaded")
    cached = sum(1 for item in records if item.status == "cached")
    failed = sum(1 for item in records if item.status == "failed")
    print(
        f"Completed KIE docs mirror: {available} available "
        f"({downloaded} downloaded, {cached} cached), {failed} failed, "
        f"manifest={args.manifest}"
    )

    return 0 if failed == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))