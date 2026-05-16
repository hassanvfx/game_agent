import argparse
import json
import os
import posixpath
import re
import shutil
import socket
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib import error, parse, request
import subprocess


QUEUE_STATES = [
    "pending",
    "leased",
    "capturing",
    "replay_pending",
    "completed",
    "failed_retryable",
    "failed_terminal",
]

RUN_SUBDIRECTORIES = [
    "manifest",
    "games",
    "workers",
    "events",
    "reports",
    "config",
    *[f"queue/{state}" for state in QUEUE_STATES],
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def pretty_json(data: Any) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(pretty_json(payload), encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_bytes(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def read_text_if_exists(path: Path) -> str | None:
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8").strip()


def append_jsonl(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def slugify(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return normalized or "run"


def safe_name(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9._-]+", "_", value.strip())
    return normalized or "unknown"


def infer_url_type(url: str) -> str:
    if "/minigame/" in url and url.endswith("/index.html"):
        return "minigame_index"
    if "/user_upload/game/version/" in url and url.endswith(".html"):
        return "version_html"
    return "unknown"


def infer_game_key(item: dict[str, Any], source_url: str) -> str:
    game_id = item.get("game_id")
    if game_id is not None:
        return safe_name(f"game-{game_id}")

    minigame_match = re.search(r"/minigame/([^/]+)/index\.html$", source_url)
    if minigame_match:
        return safe_name(minigame_match.group(1))

    version_match = re.search(r"/(latest-[^.]+)\.html$", source_url)
    if version_match:
        return safe_name(version_match.group(1))

    return safe_name(slugify(source_url))


def count_json_files(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for child in path.iterdir() if child.is_file() and child.suffix == ".json")


def parse_utc_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    normalized = value.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(normalized)
    except ValueError:
        return None


def fetch_url(url: str, timeout_seconds: int = 30) -> tuple[int, dict[str, str], bytes, str]:
    req = request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) GameDownloader/0.1",
            "Accept": "*/*",
            "Connection": "close",
        },
    )

    try:
        with request.urlopen(req, timeout=timeout_seconds) as response:
            body = response.read()
            status_code = response.getcode()
            headers = dict(response.info().items())
            final_url = response.geturl()
    except error.HTTPError as exc:
        body = exc.read()
        status_code = exc.code
        headers = dict(exc.headers.items())
        final_url = exc.geturl()
    except error.URLError as exc:
        raise RuntimeError(f"Network error for {url}: {exc}") from exc

    return status_code, headers, body, final_url


def fetch_url_with_diagnostics(
    url: str,
    timeout_seconds: int = 30,
) -> tuple[int, dict[str, str], bytes, str, dict[str, Any]]:
    started_dt = datetime.now(timezone.utc)
    diagnostics: dict[str, Any] = {
        "started_at": started_dt.isoformat().replace("+00:00", "Z"),
        "timeout_seconds": timeout_seconds,
        "fetcher": "curl",
    }

    header_path = Path("/tmp") / f"rezonalyzer_curl_headers_{safe_name(str(started_dt.timestamp()))}_{safe_name(url)}.txt"
    body_path = Path("/tmp") / f"rezonalyzer_curl_body_{safe_name(str(started_dt.timestamp()))}_{safe_name(url)}.bin"
    write_out = r"%{http_code}\n%{time_namelookup}\n%{time_connect}\n%{time_appconnect}\n%{time_starttransfer}\n%{time_total}\n%{size_download}\n%{content_type}\n%{url_effective}"

    command = [
        "curl",
        "--silent",
        "--show-error",
        "--location",
        "--globoff",
        "--max-time",
        str(timeout_seconds),
        "--connect-timeout",
        str(timeout_seconds),
        "--header",
        "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) GameDownloader/0.1",
        "--header",
        "Accept: */*",
        "--header",
        "Connection: close",
        "--dump-header",
        str(header_path),
        "--output",
        str(body_path),
        "--write-out",
        write_out,
        "--",
        url,
    ]

    try:
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
        )
    except Exception as exc:
        failed_dt = datetime.now(timezone.utc)
        diagnostics.update(
            {
                "failed_at": failed_dt.isoformat().replace("+00:00", "Z"),
                "total_elapsed_seconds": round((failed_dt - started_dt).total_seconds(), 3),
                "error_type": type(exc).__name__,
                "error": str(exc),
            }
        )
        raise RuntimeError(f"curl execution failed for {url}: {exc}") from exc

    finished_dt = datetime.now(timezone.utc)
    stdout_lines = [line for line in completed.stdout.splitlines()]
    stderr_text = completed.stderr.strip()

    if completed.returncode != 0:
        diagnostics.update(
            {
                "failed_at": finished_dt.isoformat().replace("+00:00", "Z"),
                "total_elapsed_seconds": round((finished_dt - started_dt).total_seconds(), 3),
                "error_type": "curl_nonzero_exit",
                "error": stderr_text or f"curl exited with code {completed.returncode}",
                "curl_exit_code": completed.returncode,
            }
        )
        raise RuntimeError(f"curl failed for {url}: {stderr_text or f'exit code {completed.returncode}'}")

    if len(stdout_lines) < 9:
        raise RuntimeError(f"curl diagnostics were incomplete for {url}")

    status_code = int(stdout_lines[0] or "0")
    time_namelookup = float(stdout_lines[1] or "0")
    time_connect = float(stdout_lines[2] or "0")
    time_appconnect = float(stdout_lines[3] or "0")
    time_starttransfer = float(stdout_lines[4] or "0")
    time_total = float(stdout_lines[5] or "0")
    size_download = int(float(stdout_lines[6] or "0"))
    content_type = stdout_lines[7].strip()
    final_url = stdout_lines[8].strip() or url

    raw_headers = header_path.read_text(encoding="utf-8", errors="replace") if header_path.exists() else ""
    header_blocks = [block for block in raw_headers.split("\r\n\r\n") if block.strip()] or [raw_headers]
    final_header_block = header_blocks[-1]
    headers: dict[str, str] = {}
    for line in final_header_block.splitlines():
        if ":" not in line or line.startswith("HTTP/"):
            continue
        key, value = line.split(":", 1)
        headers[key.strip()] = value.strip()

    if content_type and "content-type" not in {str(key).lower() for key in headers.keys()}:
        headers["content-type"] = content_type

    body = body_path.read_bytes() if body_path.exists() else b""

    diagnostics.update(
        {
            "completed_at": finished_dt.isoformat().replace("+00:00", "Z"),
            "total_elapsed_seconds": round((finished_dt - started_dt).total_seconds(), 3),
            "time_namelookup_seconds": time_namelookup,
            "time_connect_seconds": time_connect,
            "time_appconnect_seconds": time_appconnect,
            "time_starttransfer_seconds": time_starttransfer,
            "open_elapsed_seconds": time_starttransfer,
            "read_elapsed_seconds": max(time_total - time_starttransfer, 0.0),
            "curl_time_total_seconds": time_total,
            "bytes": len(body) or size_download,
            "status_code": status_code,
            "final_url": final_url,
            "curl_exit_code": completed.returncode,
        }
    )

    try:
        if header_path.exists():
            header_path.unlink()
        if body_path.exists():
            body_path.unlink()
    except OSError:
        pass

    return status_code, headers, body, final_url, diagnostics


def canonicalize_asset_url(url: str) -> str:
    candidate = (url or "").strip()
    if not candidate.startswith(("http://", "https://")):
        return candidate
    parsed = parse.urlparse(candidate)
    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()
    path = parsed.path or ""

    if netloc == "cdn.tailwindcss.com":
        return f"{scheme}://{netloc}/3.4.17"

    if path != "/" and path.endswith("/"):
        path = path.rstrip("/")

    rebuilt = parse.urlunparse((scheme, netloc, path, parsed.params, parsed.query, ""))
    return rebuilt


def normalize_url_candidate(url: str, base_url: str | None = None) -> str | None:
    candidate = (url or "").strip()
    if not candidate or candidate.startswith(("data:", "javascript:", "#", "mailto:", "tel:")):
        return None
    if base_url:
        candidate = parse.urljoin(base_url, candidate)
    elif not candidate.startswith(("http://", "https://")):
        return candidate
    return canonicalize_asset_url(candidate)


def build_url_aliases(*urls: str) -> list[str]:
    aliases: list[str] = []
    seen: set[str] = set()

    for raw_url in urls:
        candidate = (raw_url or "").strip()
        if not candidate:
            continue

        variants: list[str] = [candidate]
        canonical = canonicalize_asset_url(candidate)
        if canonical and canonical not in variants:
            variants.append(canonical)

        if candidate.startswith(("http://", "https://")):
            parsed = parse.urlparse(candidate)
            path = parsed.path or ""
            if parsed.netloc.lower() == "cdn.tailwindcss.com":
                variants.extend(
                    [
                        parse.urlunparse((parsed.scheme, parsed.netloc, "", parsed.params, parsed.query, "")),
                        parse.urlunparse((parsed.scheme, parsed.netloc, "/", parsed.params, parsed.query, "")),
                        parse.urlunparse((parsed.scheme, parsed.netloc, "/3.4.17", parsed.params, parsed.query, "")),
                        parse.urlunparse((parsed.scheme, parsed.netloc, "/3.4.17/", parsed.params, parsed.query, "")),
                    ]
                )

            if path in {"", "/"}:
                slash_variant = parse.urlunparse((parsed.scheme, parsed.netloc, "/", parsed.params, parsed.query, ""))
                noslash_variant = parse.urlunparse((parsed.scheme, parsed.netloc, "", parsed.params, parsed.query, ""))
                variants.extend([slash_variant, noslash_variant])
            elif path.endswith("/"):
                variants.append(parse.urlunparse((parsed.scheme, parsed.netloc, path.rstrip("/"), parsed.params, parsed.query, "")))
            else:
                variants.append(parse.urlunparse((parsed.scheme, parsed.netloc, path + "/", parsed.params, parsed.query, "")))

        for variant in variants:
            normalized = (variant or "").strip()
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            aliases.append(normalized)

            canonical_variant = canonicalize_asset_url(normalized)
            if canonical_variant and canonical_variant not in seen:
                seen.add(canonical_variant)
                aliases.append(canonical_variant)

    return aliases


def build_entry_relative_aliases(entry_url: str, asset_url: str) -> list[str]:
    entry_candidate = (entry_url or "").strip()
    asset_candidate = canonicalize_asset_url((asset_url or "").strip())
    if not entry_candidate or not asset_candidate:
        return []
    if not entry_candidate.startswith(("http://", "https://")):
        return []
    if not asset_candidate.startswith(("http://", "https://")):
        return []

    entry_parsed = parse.urlparse(entry_candidate)
    asset_parsed = parse.urlparse(asset_candidate)
    if (
        entry_parsed.scheme.lower() != asset_parsed.scheme.lower()
        or entry_parsed.netloc.lower() != asset_parsed.netloc.lower()
    ):
        return []

    aliases: list[str] = []
    seen: set[str] = set()

    def add(candidate: str) -> None:
        normalized = (candidate or "").strip()
        if not normalized or normalized in seen:
            return
        seen.add(normalized)
        aliases.append(normalized)

    entry_path = entry_parsed.path or "/"
    entry_dir_path = entry_path if entry_path.endswith("/") else posixpath.dirname(entry_path) + "/"

    asset_path = asset_parsed.path or "/"
    relpath = posixpath.relpath(asset_path, start=entry_dir_path.rstrip("/") or "/")
    if relpath in {".", ""}:
        relpath = posixpath.basename(asset_path) or "asset"
    if asset_parsed.query:
        relpath = f"{relpath}?{asset_parsed.query}"

    add(relpath)
    if not relpath.startswith(("./", "../", "/")):
        add(f"./{relpath}")
    add(asset_path)
    if asset_parsed.query:
        add(f"{asset_path}?{asset_parsed.query}")

    return aliases


def detect_asset_file_extension(asset_url: str, final_url: str, headers: dict[str, str]) -> str:
    header_map = {str(key).lower(): str(value) for key, value in headers.items()}
    content_type = header_map.get("content-type", "").split(";", 1)[0].strip().lower()

    content_type_suffixes = {
        "text/html": ".html",
        "text/css": ".css",
        "application/javascript": ".js",
        "text/javascript": ".js",
        "application/x-javascript": ".js",
        "application/json": ".json",
        "image/png": ".png",
        "image/jpeg": ".jpg",
        "image/jpg": ".jpg",
        "image/gif": ".gif",
        "image/webp": ".webp",
        "image/svg+xml": ".svg",
        "audio/mpeg": ".mp3",
        "audio/mp3": ".mp3",
        "audio/wav": ".wav",
        "audio/ogg": ".ogg",
        "video/mp4": ".mp4",
        "font/woff": ".woff",
        "font/woff2": ".woff2",
    }

    known_suffixes = set(content_type_suffixes.values()) | {
        ".txt",
        ".xml",
        ".map",
        ".mjs",
        ".cjs",
        ".aac",
        ".flac",
        ".webm",
        ".mov",
        ".ttf",
        ".otf",
        ".eot",
    }

    url_candidates = [final_url, asset_url]
    for candidate in url_candidates:
        suffix = Path(candidate.split("?", 1)[0]).suffix.lower()
        if suffix in known_suffixes:
            return suffix

    if content_type in content_type_suffixes:
        return content_type_suffixes[content_type]

    for candidate in url_candidates:
        suffix = Path(candidate.split("?", 1)[0]).suffix.lower()
        if suffix and re.fullmatch(r"\.[a-z0-9]{1,8}", suffix):
            return suffix

    return ".bin"


def extract_asset_urls_from_html(html: str, base_url: str | None = None) -> list[str]:
    patterns = [
        r"""<script[^>]+src=["']([^"']+)["']""",
        r"""<img[^>]+src=["']([^"']+)["']""",
        r"""<source[^>]+src=["']([^"']+)["']""",
        r"""<audio[^>]+src=["']([^"']+)["']""",
        r"""<video[^>]+src=["']([^"']+)["']""",
        r"""<link[^>]+href=["']([^"']+)["']""",
        r"""url\(["']?([^)"']+)["']?\)""",
        r"""fetch\(["']([^"']+)["']""",
        r"""import\(["']([^"']+)["']""",
        r"""["'](https?://[^"'\\]+)["']""",
    ]
    discovered: list[str] = []
    seen: set[str] = set()

    for pattern in patterns:
        for match in re.finditer(pattern, html, flags=re.IGNORECASE):
            normalized = normalize_url_candidate(match.group(1), base_url=base_url)
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            discovered.append(normalized)

    return discovered


def is_probable_static_asset_url(url: str) -> bool:
    parsed = parse.urlparse(url)
    suffix = Path(parsed.path).suffix.lower()
    allowed_suffixes = {
        ".css",
        ".js",
        ".mjs",
        ".cjs",
        ".json",
        ".map",
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".webp",
        ".svg",
        ".mp3",
        ".wav",
        ".ogg",
        ".mp4",
        ".webm",
        ".woff",
        ".woff2",
        ".ttf",
        ".otf",
        ".eot",
        ".html",
        ".htm",
        ".xml",
        ".txt",
    }
    if suffix in allowed_suffixes:
        return True

    netloc = parsed.netloc.lower()
    if netloc == "fonts.gstatic.com" and parsed.path.startswith("/l/font"):
        return True

    return False


def extract_asset_urls_from_text_asset(text: str, base_url: str | None = None) -> list[str]:
    patterns = [
        r"""url\(["']?([^)"']+)["']?\)""",
        r"""fetch\(["']([^"']+)["']""",
        r"""import\(["']([^"']+)["']""",
        r"""["'](/[^"'\\]+\.(?:css|js|mjs|cjs|json|map|png|jpg|jpeg|gif|webp|svg|mp3|wav|ogg|mp4|webm|woff2?|ttf|otf|eot|html?|xml|txt)(?:\?[^"'\\]*)?)["']""",
    ]
    discovered: list[str] = []
    seen: set[str] = set()

    for pattern in patterns:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            normalized = normalize_url_candidate(match.group(1), base_url=base_url)
            if not normalized or normalized in seen or not is_probable_static_asset_url(normalized):
                continue
            seen.add(normalized)
            discovered.append(normalized)

    return discovered


def derive_replay_asset_relative_path(
    url: str,
    content_type: str | None = None,
    *,
    origin_netloc: str | None = None,
) -> str:
    parsed = parse.urlparse(url)
    raw_path = parsed.path or "/asset"
    path_obj = Path(raw_path)
    suffix = path_obj.suffix.lower()

    def has_valid_suffix(value: str) -> bool:
        candidate = Path(value).suffix.lower()
        return bool(candidate and re.fullmatch(r"\.[a-z][a-z0-9]{0,7}", candidate))

    if suffix and not re.fullmatch(r"\.[a-z][a-z0-9]{0,7}", suffix):
        suffix = ""

    if not suffix and content_type:
        detected_suffix = detect_asset_file_extension(url, url, {"content-type": content_type})
        if detected_suffix and detected_suffix != ".bin":
            suffix = detected_suffix

    if origin_netloc and parsed.netloc.lower() == origin_netloc.lower():
        relative_parts = [safe_name(part) for part in path_obj.parts if part not in {"", "/"}]
        if not relative_parts:
            relative_parts = ["asset" + (suffix or ".bin")]
        elif suffix and not has_valid_suffix(relative_parts[-1]):
            relative_parts[-1] = relative_parts[-1] + suffix

        if "assets" in relative_parts:
            asset_index = relative_parts.index("assets")
            relative_parts = relative_parts[asset_index + 1 :] or relative_parts[-1:]
            return str(Path("assets") / Path(*relative_parts))

        return str(Path("assets") / Path(*relative_parts))

    domain = safe_name(parsed.netloc or "unknown-host")
    parent_parts = [safe_name(part) for part in path_obj.parent.parts if part not in {"", "/"}]
    filename = safe_name(path_obj.name or "asset")
    if parsed.query:
        filename = safe_name(f"{filename}-{parsed.query}")
    if suffix and not has_valid_suffix(filename):
        filename = filename + suffix
    elif not suffix and not has_valid_suffix(filename):
        filename = filename + (suffix or ".bin")
    pieces = ["assets", domain, *parent_parts]
    return str(Path(*pieces) / filename)


def rewrite_text_with_mapping(
    text: str,
    replacements: dict[str, str],
    *,
    current_file_path: Path | None = None,
    rewrite_relative_to_file: bool = False,
) -> tuple[str, list[dict[str, Any]]]:
    rewritten = text
    applied: list[dict[str, Any]] = []
    placeholder_values: dict[str, str] = {}
    placeholder_index = 0

    for original, local_path in sorted(replacements.items(), key=lambda item: len(item[0]), reverse=True):
        effective_local_path = local_path
        if rewrite_relative_to_file and current_file_path is not None:
            effective_local_path = Path(
                os.path.relpath(local_path, start=current_file_path.parent.as_posix())
            ).as_posix()
        occurrences = rewritten.count(original)
        if occurrences <= 0:
            continue
        placeholder = f"__GAME_DOWNLOADER_REWRITE_{placeholder_index:06d}__"
        placeholder_index += 1
        rewritten = rewritten.replace(original, placeholder)
        placeholder_values[placeholder] = effective_local_path
        applied.append(
            {
                "original_url": original,
                "local_path": effective_local_path,
                "replacement_count": occurrences,
            }
        )

    for placeholder, effective_local_path in placeholder_values.items():
        rewritten = rewritten.replace(placeholder, effective_local_path)

    return rewritten, applied


def looks_like_text_asset(path: Path, content_type: str | None = None) -> bool:
    suffix = path.suffix.lower()
    text_suffixes = {
        ".html",
        ".htm",
        ".css",
        ".js",
        ".mjs",
        ".cjs",
        ".json",
        ".webmanifest",
        ".txt",
        ".map",
        ".xml",
    }
    if suffix in text_suffixes:
        return True

    normalized_content_type = (content_type or "").split(";", 1)[0].strip().lower()
    return normalized_content_type.startswith("text/") or normalized_content_type in {
        "application/javascript",
        "text/javascript",
        "application/x-javascript",
        "application/json",
        "application/manifest+json",
        "application/xml",
    }


def detect_remote_references(text: str, kind: str = "text") -> list[str]:
    ignored_exact_refs = {
        "https://tailwindcss.com",
    }
    ignored_prefixes = (
        "https://fonts.googleapis.com/",
        "https://fonts.gstatic.com/l/font",
    )

    def clean_refs(refs: set[str]) -> list[str]:
        cleaned: set[str] = set()
        for ref in refs:
            candidate = str(ref).strip().rstrip("`;,")
            if (
                not candidate
                or "${" in candidate
                or candidate in ignored_exact_refs
                or candidate.startswith(ignored_prefixes)
            ):
                continue
            cleaned.add(candidate)
        return sorted(cleaned)

    if kind == "js":
        patterns = [
            r"""import\(["'](https?://[^"'\\]+)["']""",
            r"""fetch\(["'](https?://[^"'\\]+)["']""",
            r"""from\s+["'](https?://[^"'\\]+)["']""",
            r"""url\(["']?(https?://[^)"']+)["']?\)""",
            r"""new\s+Worker\(["'](https?://[^"'\\]+)["']""",
            r"""new\s+URL\(["'](https?://[^"'\\]+)["']""",
        ]
        refs: set[str] = set()
        for pattern in patterns:
            refs.update(re.findall(pattern, text, flags=re.IGNORECASE))
        return clean_refs(refs)

    refs = set(re.findall(r"""https?://[^\s"'()<>]+""", text))
    return clean_refs(refs)


def classify_text_asset_kind(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".html", ".htm"}:
        return "html"
    if suffix == ".css":
        return "css"
    if suffix in {".js", ".mjs", ".cjs", ".map"}:
        return "js"
    if suffix in {".json", ".webmanifest", ".xml", ".txt"}:
        return "json_config"
    return "text"


@dataclass
class NormalizedEntry:
    game_key: str
    source_url: str
    url_type: str
    game_id: Any
    game_version: Any
    name: str
    creator_name: str | None
    creator_id: Any
    topic_id: Any
    topic_name: str | None
    source_record_index: int
    source_input_file: str
    raw_item: dict[str, Any]

    def to_manifest_record(self) -> dict[str, Any]:
        return {
            "game_key": self.game_key,
            "source_url": self.source_url,
            "url_type": self.url_type,
            "game_id": self.game_id,
            "game_version": self.game_version,
            "name": self.name,
            "creator_name": self.creator_name,
            "creator_id": self.creator_id,
            "topic_id": self.topic_id,
            "topic_name": self.topic_name,
            "source_record_index": self.source_record_index,
            "source_input_file": self.source_input_file,
        }

    def to_queue_record(self, run_id: str) -> dict[str, Any]:
        timestamp = utc_now()
        return {
            "run_id": run_id,
            "game_key": self.game_key,
            "status": "pending",
            "attempt_count": 0,
            "source_url": self.source_url,
            "url_type": self.url_type,
            "game_id": self.game_id,
            "game_version": self.game_version,
            "name": self.name,
            "topic_name": self.topic_name,
            "source_record_index": self.source_record_index,
            "source_input_file": self.source_input_file,
            "created_at": timestamp,
            "updated_at": timestamp,
        }


class MirrorRun:
    def __init__(self, run_dir: Path) -> None:
        self.run_dir = run_dir
        self.queue_dir = self.run_dir / "queue"
        self.games_dir = self.run_dir / "games"
        self.workers_dir = self.run_dir / "workers"
        self.events_path = self.run_dir / "events" / "events.jsonl"
        self.progress_json_path = self.run_dir / "reports" / "progress.json"
        self.progress_md_path = self.run_dir / "reports" / "progress.md"
        self.summary_path = self.run_dir / "manifest" / "summary.json"

        if not self.run_dir.exists():
            raise FileNotFoundError(f"Run directory not found: {self.run_dir}")
        if not self.summary_path.exists():
            raise FileNotFoundError(
                f"Run metadata not found at expected path: {self.summary_path}"
            )

    def summary(self) -> dict[str, Any]:
        return read_json(self.summary_path)

    def emit_verbose(self, verbose: bool, message: str) -> None:
        if verbose:
            print(message, flush=True)

    def queue_state_path(self, state: str) -> Path:
        return self.queue_dir / state

    def find_game_queue_file(self, game_key: str) -> tuple[str, Path]:
        for state in QUEUE_STATES:
            candidate = self.queue_state_path(state) / f"{game_key}.json"
            if candidate.exists():
                return state, candidate
        raise FileNotFoundError(f"Queue file not found for game_key={game_key}")

    def worker_status_path(self, worker_id: str) -> Path:
        return self.workers_dir / f"{worker_id}.json"

    def worker_heartbeat_path(self, worker_id: str) -> Path:
        return self.workers_dir / f"{worker_id}.heartbeat.txt"

    def worker_current_game_path(self, worker_id: str) -> Path:
        return self.workers_dir / f"{worker_id}.current_game.txt"

    def write_worker_status(
        self,
        worker_id: str,
        current_game: str | None,
        status: str,
    ) -> None:
        timestamp = utc_now()
        payload = {
            "worker_id": worker_id,
            "status": status,
            "current_game": current_game,
            "run_id": self.summary().get("run_id"),
            "hostname": socket.gethostname(),
            "updated_at": timestamp,
        }
        write_json(self.worker_status_path(worker_id), payload)
        write_text(self.worker_heartbeat_path(worker_id), timestamp + "\n")
        write_text(self.worker_current_game_path(worker_id), (current_game or "") + "\n")

    def append_event(self, event: str, **details: Any) -> None:
        payload = {
            "timestamp": utc_now(),
            "event": event,
            "run_id": self.summary().get("run_id"),
            **details,
        }
        append_jsonl(self.events_path, payload)

    def update_game_history(
        self,
        game_key: str,
        event: str,
        status: str,
        **details: Any,
    ) -> None:
        append_jsonl(
            self.games_dir / game_key / "history.jsonl",
            {
                "timestamp": utc_now(),
                "event": event,
                "status": status,
                **details,
            },
        )

    def update_game_status(self, game_key: str, status: str) -> None:
        write_text(self.games_dir / game_key / "status.txt", status + "\n")

    def load_queue_record(self, path: Path) -> dict[str, Any]:
        return read_json(path)

    def save_queue_record(self, path: Path, record: dict[str, Any]) -> None:
        write_json(path, record)

    def initialize_attempt(self, game_key: str, worker_id: str | None = None) -> dict[str, Any]:
        current_state, current_path = self.find_game_queue_file(game_key)
        record = self.load_queue_record(current_path)
        attempt_count = int(record.get("attempt_count", 0))
        if attempt_count <= 0:
            attempt_count = 1
            record["attempt_count"] = attempt_count
            record["updated_at"] = utc_now()
            self.save_queue_record(current_path, record)

        attempt_name = f"attempt_{attempt_count:04d}"
        attempt_dir = self.games_dir / game_key / "attempts" / attempt_name
        attempt_dir.mkdir(parents=True, exist_ok=True)

        metadata = {
            "run_id": self.summary().get("run_id"),
            "game_key": game_key,
            "attempt_name": attempt_name,
            "attempt_count": attempt_count,
            "worker_id": worker_id,
            "initialized_at": utc_now(),
            "source_url": record.get("source_url"),
            "url_type": record.get("url_type"),
            "current_queue_state": current_state,
            "capture_status": "initialized",
        }

        write_json(attempt_dir / "metadata.json", metadata)
        write_text(attempt_dir / "started_at.txt", metadata["initialized_at"] + "\n")
        write_text(attempt_dir / "result.txt", "initialized\n")
        write_text(attempt_dir / "worker_id.txt", (worker_id or "") + "\n")
        write_json(attempt_dir / "request_summary.json", {"requests_total": 0, "responses_total": 0})
        write_text(attempt_dir / "notes.txt", "")
        (attempt_dir / "responses").mkdir(parents=True, exist_ok=True)
        (attempt_dir / "network").mkdir(parents=True, exist_ok=True)
        (attempt_dir / "screenshots").mkdir(parents=True, exist_ok=True)
        (attempt_dir / "artifacts").mkdir(parents=True, exist_ok=True)

        self.update_game_history(
            game_key,
            event="attempt_initialized",
            status=current_state,
            worker_id=worker_id,
            attempt_name=attempt_name,
            attempt_count=attempt_count,
        )
        self.append_event(
            "attempt_initialized",
            game_key=game_key,
            worker_id=worker_id,
            attempt_name=attempt_name,
            attempt_count=attempt_count,
        )

        return {
            "run_id": self.summary().get("run_id"),
            "game_key": game_key,
            "attempt_name": attempt_name,
            "attempt_dir": str(attempt_dir),
            "attempt_count": attempt_count,
        }

    def recover_stale_workers(self, max_age_minutes: int, requeue_state: str) -> dict[str, Any]:
        if requeue_state not in {"pending", "failed_retryable"}:
            raise ValueError("requeue_state must be 'pending' or 'failed_retryable'")

        now = datetime.now(timezone.utc)
        recovered: list[dict[str, Any]] = []

        for worker_file in sorted(self.workers_dir.glob("*.json")):
            worker_status = read_json(worker_file)
            worker_id = worker_status.get("worker_id") or worker_file.stem
            status = str(worker_status.get("status") or "").strip()
            current_game = str(worker_status.get("current_game") or "").strip() or None

            if status not in {"leased", "capturing"} or not current_game:
                continue

            heartbeat_path = self.worker_heartbeat_path(worker_id)
            heartbeat_value = heartbeat_path.read_text(encoding="utf-8").strip() if heartbeat_path.exists() else ""
            heartbeat_at = parse_utc_timestamp(heartbeat_value) or parse_utc_timestamp(
                str(worker_status.get("updated_at") or "")
            )
            if heartbeat_at is None:
                continue

            age_minutes = (now - heartbeat_at).total_seconds() / 60.0
            if age_minutes < max_age_minutes:
                continue

            current_state, current_path = self.find_game_queue_file(current_game)
            if current_state not in {"leased", "capturing"}:
                continue

            record = self.load_queue_record(current_path)
            record["status"] = requeue_state
            record["updated_at"] = utc_now()
            record["recovered_from_worker_id"] = worker_id
            record["recovered_from_state"] = current_state
            record["recovered_at"] = utc_now()
            record["stale_heartbeat_at"] = heartbeat_value

            target_path = self.queue_state_path(requeue_state) / current_path.name
            self.save_queue_record(current_path, record)
            current_path.replace(target_path)

            self.update_game_status(current_game, requeue_state)
            self.update_game_history(
                current_game,
                event="stale_worker_recovered",
                status=requeue_state,
                previous_state=current_state,
                worker_id=worker_id,
                stale_heartbeat_at=heartbeat_value,
                requeue_state=requeue_state,
            )
            self.append_event(
                "stale_worker_recovered",
                game_key=current_game,
                worker_id=worker_id,
                previous_state=current_state,
                requeue_state=requeue_state,
                stale_heartbeat_at=heartbeat_value,
            )

            self.write_worker_status(worker_id=worker_id, current_game=None, status="recovered")
            recovered.append(
                {
                    "worker_id": worker_id,
                    "game_key": current_game,
                    "previous_state": current_state,
                    "requeue_state": requeue_state,
                    "stale_heartbeat_at": heartbeat_value,
                    "age_minutes": round(age_minutes, 2),
                    "queue_file": str(target_path),
                }
            )

        return {
            "run_id": self.summary().get("run_id"),
            "max_age_minutes": max_age_minutes,
            "requeue_state": requeue_state,
            "recovered_count": len(recovered),
            "recovered": recovered,
        }

    def find_latest_attempt_dir(self, game_key: str) -> Path:
        attempts_dir = self.games_dir / game_key / "attempts"
        if not attempts_dir.exists():
            raise FileNotFoundError(f"No attempts directory exists for game_key={game_key}")

        candidates = sorted(path for path in attempts_dir.iterdir() if path.is_dir())
        if not candidates:
            raise FileNotFoundError(f"No attempt directories exist for game_key={game_key}")
        return candidates[-1]

    def capture_entry_url(
        self,
        game_key: str,
        worker_id: str | None = None,
        timeout_seconds: int = 30,
    ) -> dict[str, Any]:
        current_state, current_path = self.find_game_queue_file(game_key)
        record = self.load_queue_record(current_path)
        attempt_dir = self.find_latest_attempt_dir(game_key)

        source_url = str(record.get("source_url") or "")
        if not source_url:
            raise ValueError(f"Queue record for {game_key} is missing source_url")

        started_at = utc_now()
        metadata_path = attempt_dir / "metadata.json"
        metadata = read_json(metadata_path)
        metadata["capture_status"] = "fetching_entry_url"
        metadata["fetch_started_at"] = started_at
        metadata["worker_id"] = worker_id or metadata.get("worker_id")
        write_json(metadata_path, metadata)

        requests_log = attempt_dir / "requests.jsonl"
        console_log = attempt_dir / "console.jsonl"
        errors_log = attempt_dir / "errors.jsonl"
        entry_dir = attempt_dir / "artifacts" / "entry"
        entry_dir.mkdir(parents=True, exist_ok=True)

        append_jsonl(
            requests_log,
            {
                "timestamp": started_at,
                "event": "entry_fetch_started",
                "url": source_url,
                "worker_id": worker_id,
                "queue_state": current_state,
            },
        )

        append_jsonl(
            console_log,
            {
                "timestamp": started_at,
                "event": "capture_scaffold_note",
                "message": (
                    f"Starting entry fetch via curl-backed diagnostics "
                    f"(timeout_seconds={timeout_seconds})."
                ),
            },
        )

        entry_fetch_url = source_url
        entry_fetch_mode = "source_url"
        try:
            status_code, headers, body, final_url, fetch_diagnostics = fetch_url_with_diagnostics(
                entry_fetch_url, timeout_seconds=timeout_seconds
            )
        except Exception as exc:
            parsed_source = parse.urlparse(source_url)
            src_values = parse.parse_qs(parsed_source.query).get("src") or []
            fallback_src_url = src_values[0] if parsed_source.netloc.lower() == "web.rezona.ai" and parsed_source.path == "/bridge" and src_values else None
            if fallback_src_url and "curl failed for" in str(exc) and "Failed writing received data to disk/application" in str(exc):
                append_jsonl(
                    console_log,
                    {
                        "timestamp": utc_now(),
                        "event": "capture_scaffold_note",
                        "message": (
                            "Bridge entry fetch hit curl write/output failure; "
                            f"retrying with decoded src URL fallback: {fallback_src_url}"
                        ),
                    },
                )
                entry_fetch_url = fallback_src_url
                entry_fetch_mode = "bridge_src_fallback"
                try:
                    status_code, headers, body, final_url, fetch_diagnostics = fetch_url_with_diagnostics(
                        entry_fetch_url, timeout_seconds=timeout_seconds
                    )
                except Exception as fallback_exc:
                    exc = fallback_exc
                else:
                    exc = None

            if exc is not None:
                finished_at = utc_now()
                write_text(attempt_dir / "finished_at.txt", finished_at + "\n")
                write_text(attempt_dir / "result.txt", "entry_fetch_failed\n")
                metadata["capture_status"] = "entry_fetch_failed"
                metadata["fetch_finished_at"] = finished_at
                metadata["fetch_error"] = str(exc)
                write_json(metadata_path, metadata)
                append_jsonl(
                    errors_log,
                    {
                        "timestamp": finished_at,
                        "event": "entry_fetch_failed",
                        "url": source_url,
                        "worker_id": worker_id,
                        "error": str(exc),
                    },
                )
                self.update_game_history(
                    game_key,
                    event="entry_fetch_failed",
                    status=current_state,
                    worker_id=worker_id,
                    error=str(exc),
                )
                self.append_event(
                    "entry_fetch_failed",
                    game_key=game_key,
                    worker_id=worker_id,
                    error=str(exc),
                )
                raise exc

        finished_at = utc_now()
        write_text(entry_dir / "body.html", body.decode("utf-8", errors="replace"))
        write_json(
            entry_dir / "headers.json",
            {
                "status_code": status_code,
                "final_url": final_url,
                "headers": headers,
            },
        )
        write_json(
            entry_dir / "summary.json",
            {
                "source_url": source_url,
                "requested_fetch_url": entry_fetch_url,
                "entry_fetch_mode": entry_fetch_mode,
                "final_url": final_url,
                "status_code": status_code,
                "bytes": len(body),
                "fetched_at": finished_at,
                "fetcher": "curl",
                "timing": fetch_diagnostics,
            },
        )
        write_text(attempt_dir / "finished_at.txt", finished_at + "\n")
        write_text(attempt_dir / "result.txt", "entry_fetched\n")
        write_json(
            attempt_dir / "request_summary.json",
            {
                "requests_total": 1,
                "responses_total": 1,
                "entry_fetch_status_code": status_code,
                "entry_fetch_bytes": len(body),
            },
        )
        metadata["capture_status"] = "entry_fetched"
        metadata["fetch_finished_at"] = finished_at
        metadata["entry_status_code"] = status_code
        metadata["entry_final_url"] = final_url
        metadata["entry_requested_fetch_url"] = entry_fetch_url
        metadata["entry_fetch_mode"] = entry_fetch_mode
        metadata["entry_body_path"] = str(entry_dir / "body.html")
        metadata["entry_fetcher"] = "curl"
        metadata["entry_fetch_diagnostics"] = fetch_diagnostics
        write_json(metadata_path, metadata)

        append_jsonl(
            requests_log,
            {
                "timestamp": finished_at,
                "event": "entry_fetch_completed",
                "url": source_url,
                "final_url": final_url,
                "status_code": status_code,
                "bytes": len(body),
                "worker_id": worker_id,
            },
        )
        append_jsonl(
            console_log,
            {
                "timestamp": finished_at,
                "event": "capture_scaffold_note",
                "message": (
                    f"Entry URL fetched via curl-backed diagnostics. "
                    f"status_code={status_code} bytes={len(body)} final_url={final_url}"
                ),
            },
        )
        self.update_game_history(
            game_key,
            event="entry_fetched",
            status=current_state,
            worker_id=worker_id,
            status_code=status_code,
            bytes=len(body),
        )
        self.append_event(
            "entry_fetched",
            game_key=game_key,
            worker_id=worker_id,
            status_code=status_code,
            bytes=len(body),
        )

        return {
            "run_id": self.summary().get("run_id"),
            "game_key": game_key,
            "attempt_dir": str(attempt_dir),
            "status_code": status_code,
            "bytes": len(body),
            "final_url": final_url,
        }

    def analyze_latest_attempt_assets(self, game_key: str) -> dict[str, Any]:
        attempt_dir = self.find_latest_attempt_dir(game_key)
        entry_body_path = attempt_dir / "artifacts" / "entry" / "body.html"
        if not entry_body_path.exists():
            raise FileNotFoundError(
                f"Entry HTML not found for latest attempt of game_key={game_key}: {entry_body_path}"
            )

        html = entry_body_path.read_text(encoding="utf-8", errors="replace")
        entry_summary_path = attempt_dir / "artifacts" / "entry" / "summary.json"
        entry_summary = read_json(entry_summary_path) if entry_summary_path.exists() else {}
        base_url = str(entry_summary.get("final_url") or entry_summary.get("source_url") or "")
        asset_urls = extract_asset_urls_from_html(html, base_url=base_url or None)

        asset_report = {
            "run_id": self.summary().get("run_id"),
            "game_key": game_key,
            "attempt_dir": str(attempt_dir),
            "asset_url_count": len(asset_urls),
            "asset_urls": asset_urls,
            "generated_at": utc_now(),
        }

        write_json(attempt_dir / "artifacts" / "entry" / "asset_urls.json", asset_report)
        append_jsonl(
            attempt_dir / "console.jsonl",
            {
                "timestamp": utc_now(),
                "event": "asset_urls_extracted",
                "asset_url_count": len(asset_urls),
            },
        )
        self.update_game_history(
            game_key,
            event="asset_urls_extracted",
            status=self.find_game_queue_file(game_key)[0],
            asset_url_count=len(asset_urls),
        )
        self.append_event(
            "asset_urls_extracted",
            game_key=game_key,
            asset_url_count=len(asset_urls),
        )

        return asset_report

    def download_latest_attempt_assets(
        self,
        game_key: str,
        worker_id: str | None = None,
        timeout_seconds: int = 30,
        limit: int | None = None,
        verbose: bool = False,
        only_asset_urls: list[str] | None = None,
    ) -> dict[str, Any]:
        attempt_dir = self.find_latest_attempt_dir(game_key)
        asset_report_path = attempt_dir / "artifacts" / "entry" / "asset_urls.json"
        if not asset_report_path.exists():
            raise FileNotFoundError(
                f"Asset URL report not found for latest attempt of game_key={game_key}: {asset_report_path}"
            )

        asset_report = read_json(asset_report_path)
        asset_urls = list(asset_report.get("asset_urls") or [])
        if only_asset_urls is not None:
            requested_urls = [str(url) for url in only_asset_urls if str(url).strip()]
            asset_urls = [url for url in asset_urls if url in requested_urls]
        if limit is not None:
            asset_urls = asset_urls[:limit]

        downloads_dir = attempt_dir / "artifacts" / "downloaded_assets"
        downloads_dir.mkdir(parents=True, exist_ok=True)
        requests_log = attempt_dir / "requests.jsonl"
        errors_log = attempt_dir / "errors.jsonl"
        download_events_path = downloads_dir / "download_events.jsonl"

        downloaded: list[dict[str, Any]] = []
        failed: list[dict[str, Any]] = []
        existing_downloaded_map: dict[str, dict[str, Any]] = {}
        total_assets = len(asset_urls)

        existing_download_summary_path = downloads_dir / "download_summary.json"
        if existing_download_summary_path.exists():
            existing_download_summary = read_json(existing_download_summary_path)
            for item in existing_download_summary.get("downloaded") or []:
                original_url = str(item.get("asset_url") or "").strip()
                final_url = str(item.get("final_url") or "").strip()
                if original_url:
                    existing_downloaded_map[original_url] = item
                if final_url:
                    existing_downloaded_map[final_url] = item

        self.emit_verbose(
            verbose,
            f"[download] starting asset download batch for {game_key}: {total_assets} asset(s), timeout={timeout_seconds}s",
        )

        for index, asset_url in enumerate(asset_urls, start=1):
            timestamp = utc_now()
            start_dt = datetime.now(timezone.utc)
            normalized_asset_url = asset_url.rstrip("/") if asset_url.startswith(("http://", "https://")) else asset_url
            if normalized_asset_url in existing_downloaded_map:
                reused_item = dict(existing_downloaded_map[normalized_asset_url])
                reused_item["asset_url"] = asset_url
                reused_item["reused_existing"] = True
                downloaded.append(reused_item)
                append_jsonl(
                    download_events_path,
                    {
                        "timestamp": timestamp,
                        "event": "asset_download_reused",
                        "game_key": game_key,
                        "worker_id": worker_id,
                        "index": index,
                        "total_assets": total_assets,
                        "asset_url": asset_url,
                        "matched_existing_url": normalized_asset_url,
                    },
                )
                self.emit_verbose(
                    verbose,
                    f"[download] reused {index}/{total_assets} url={asset_url} matched_existing={normalized_asset_url}",
                )
                continue

            self.emit_verbose(
                verbose,
                f"[download] start {index}/{total_assets} url={asset_url}",
            )
            append_jsonl(
                download_events_path,
                {
                    "timestamp": timestamp,
                    "event": "asset_download_started",
                    "game_key": game_key,
                    "worker_id": worker_id,
                    "index": index,
                    "total_assets": total_assets,
                    "asset_url": asset_url,
                    "timeout_seconds": timeout_seconds,
                },
            )
            append_jsonl(
                requests_log,
                {
                    "timestamp": timestamp,
                    "event": "asset_download_started",
                    "asset_url": asset_url,
                    "worker_id": worker_id,
                    "index": index,
                },
            )
            try:
                status_code, headers, body, final_url, fetch_diagnostics = fetch_url_with_diagnostics(
                    asset_url, timeout_seconds=timeout_seconds
                )
                asset_dir = downloads_dir / f"asset_{index:04d}"
                asset_dir.mkdir(parents=True, exist_ok=True)

                header_map = {str(key).lower(): str(value) for key, value in headers.items()}
                content_type = header_map.get("content-type", "").split(";", 1)[0].strip().lower()
                file_extension = detect_asset_file_extension(asset_url, final_url, headers)
                body_file_name = f"body{file_extension}"
                body_path = asset_dir / body_file_name

                write_bytes(body_path, body)
                write_json(
                    asset_dir / "headers.json",
                    {
                        "status_code": status_code,
                        "final_url": final_url,
                        "headers": headers,
                    },
                )
                completed_at = utc_now()
                elapsed_seconds = round((datetime.now(timezone.utc) - start_dt).total_seconds(), 3)
                open_elapsed_seconds = fetch_diagnostics.get("open_elapsed_seconds")
                read_elapsed_seconds = fetch_diagnostics.get("read_elapsed_seconds")
                write_json(
                    asset_dir / "summary.json",
                    {
                        "asset_url": asset_url,
                        "final_url": final_url,
                        "status_code": status_code,
                        "bytes": len(body),
                        "downloaded_at": completed_at,
                        "content_type": content_type or None,
                        "body_path": str(body_path),
                        "body_file_name": body_file_name,
                        "storage_mode": "raw_bytes",
                        "elapsed_seconds": elapsed_seconds,
                        "open_elapsed_seconds": open_elapsed_seconds,
                        "read_elapsed_seconds": read_elapsed_seconds,
                    },
                )
                downloaded_item = {
                    "asset_url": asset_url,
                    "status_code": status_code,
                    "bytes": len(body),
                    "final_url": final_url,
                    "asset_dir": str(asset_dir),
                    "content_type": content_type or None,
                    "body_path": str(body_path),
                    "body_file_name": body_file_name,
                    "storage_mode": "raw_bytes",
                    "elapsed_seconds": elapsed_seconds,
                    "open_elapsed_seconds": open_elapsed_seconds,
                    "read_elapsed_seconds": read_elapsed_seconds,
                }
                downloaded.append(downloaded_item)
                append_jsonl(
                    download_events_path,
                    {
                        "timestamp": completed_at,
                        "event": "asset_download_completed",
                        "game_key": game_key,
                        "worker_id": worker_id,
                        "index": index,
                        "total_assets": total_assets,
                        "asset_url": asset_url,
                        "final_url": final_url,
                        "status_code": status_code,
                        "bytes": len(body),
                        "content_type": content_type or None,
                        "elapsed_seconds": elapsed_seconds,
                        "open_elapsed_seconds": open_elapsed_seconds,
                        "read_elapsed_seconds": read_elapsed_seconds,
                        "time_namelookup_seconds": fetch_diagnostics.get("time_namelookup_seconds"),
                        "time_connect_seconds": fetch_diagnostics.get("time_connect_seconds"),
                        "time_appconnect_seconds": fetch_diagnostics.get("time_appconnect_seconds"),
                        "time_starttransfer_seconds": fetch_diagnostics.get("time_starttransfer_seconds"),
                        "curl_time_total_seconds": fetch_diagnostics.get("curl_time_total_seconds"),
                        "fetcher": fetch_diagnostics.get("fetcher"),
                    },
                )
                self.emit_verbose(
                    verbose,
                    f"[download] done {index}/{total_assets} status={status_code} bytes={len(body)} total={elapsed_seconds}s dns={fetch_diagnostics.get('time_namelookup_seconds')}s connect={fetch_diagnostics.get('time_connect_seconds')}s tls={fetch_diagnostics.get('time_appconnect_seconds')}s ttfb={fetch_diagnostics.get('time_starttransfer_seconds')}s read={read_elapsed_seconds}s url={asset_url}",
                )
            except KeyboardInterrupt:
                interrupted_at = utc_now()
                elapsed_seconds = round((datetime.now(timezone.utc) - start_dt).total_seconds(), 3)
                append_jsonl(
                    download_events_path,
                    {
                        "timestamp": interrupted_at,
                        "event": "asset_download_interrupted",
                        "game_key": game_key,
                        "worker_id": worker_id,
                        "index": index,
                        "total_assets": total_assets,
                        "asset_url": asset_url,
                        "elapsed_seconds": elapsed_seconds,
                    },
                )
                self.emit_verbose(
                    verbose,
                    f"[download] interrupted {index}/{total_assets} elapsed={elapsed_seconds}s url={asset_url}",
                )
                raise
            except Exception as exc:
                failed_at = utc_now()
                elapsed_seconds = round((datetime.now(timezone.utc) - start_dt).total_seconds(), 3)
                error_type = type(exc).__name__
                failed.append(
                    {
                        "asset_url": asset_url,
                        "error": str(exc),
                        "error_type": error_type,
                        "elapsed_seconds": elapsed_seconds,
                    }
                )
                append_jsonl(
                    download_events_path,
                    {
                        "timestamp": failed_at,
                        "event": "asset_download_failed",
                        "game_key": game_key,
                        "worker_id": worker_id,
                        "index": index,
                        "total_assets": total_assets,
                        "asset_url": asset_url,
                        "error": str(exc),
                        "error_type": error_type,
                        "elapsed_seconds": elapsed_seconds,
                    },
                )
                append_jsonl(
                    errors_log,
                    {
                        "timestamp": failed_at,
                        "event": "asset_download_failed",
                        "asset_url": asset_url,
                        "worker_id": worker_id,
                        "error": str(exc),
                        "error_type": error_type,
                        "elapsed_seconds": elapsed_seconds,
                    },
                )
                self.emit_verbose(
                    verbose,
                    f"[download] failed {index}/{total_assets} error_type={error_type} elapsed={elapsed_seconds}s url={asset_url} error={exc}",
                )

        merged_downloaded = downloaded
        if existing_download_summary_path.exists():
            existing_download_summary = read_json(existing_download_summary_path)
            existing_items = existing_download_summary.get("downloaded") or []
            seen_existing_keys = {str(item.get("asset_url") or "") for item in downloaded}
            for item in existing_items:
                original_url = str(item.get("asset_url") or "")
                final_url = str(item.get("final_url") or "")
                if original_url in seen_existing_keys or final_url in seen_existing_keys:
                    continue
                merged_downloaded.append(item)

        summary = {
            "run_id": self.summary().get("run_id"),
            "game_key": game_key,
            "attempt_dir": str(attempt_dir),
            "requested_asset_count": len(asset_urls),
            "downloaded_count": len(merged_downloaded),
            "failed_count": len(failed),
            "download_events_path": str(download_events_path),
            "downloaded": merged_downloaded,
            "failed": failed,
            "generated_at": utc_now(),
        }
        write_json(downloads_dir / "download_summary.json", summary)
        append_jsonl(
            attempt_dir / "console.jsonl",
            {
                "timestamp": utc_now(),
                "event": "asset_download_completed",
                "requested_asset_count": len(asset_urls),
                "downloaded_count": len(merged_downloaded),
                "failed_count": len(failed),
            },
        )
        self.update_game_history(
            game_key,
            event="asset_download_completed",
            status=self.find_game_queue_file(game_key)[0],
            requested_asset_count=len(asset_urls),
            downloaded_count=len(merged_downloaded),
            failed_count=len(failed),
        )
        self.append_event(
            "asset_download_completed",
            game_key=game_key,
            requested_asset_count=len(asset_urls),
            downloaded_count=len(merged_downloaded),
            failed_count=len(failed),
        )
        self.emit_verbose(
            verbose,
            f"[download] batch complete for {game_key}: downloaded={len(merged_downloaded)} failed={len(failed)} events={download_events_path}",
        )
        return summary

    def ensure_attempt_for_build(
        self,
        game_key: str,
        worker_id: str | None = None,
    ) -> tuple[Path, bool]:
        attempts_dir = self.games_dir / game_key / "attempts"
        existing_attempts = sorted(path for path in attempts_dir.iterdir() if path.is_dir()) if attempts_dir.exists() else []
        if existing_attempts:
            return existing_attempts[-1], False

        self.initialize_attempt(game_key=game_key, worker_id=worker_id)
        return self.find_latest_attempt_dir(game_key), True

    def ensure_build_capture_state(self, game_key: str, worker_id: str | None = None) -> tuple[Path, bool]:
        current_state, _ = self.find_game_queue_file(game_key)
        attempt_dir, created_attempt = self.ensure_attempt_for_build(game_key=game_key, worker_id=worker_id)

        if current_state in {"pending", "failed_retryable"}:
            self.transition_game(
                game_key=game_key,
                target_state="capturing",
                worker_id=worker_id,
                note="Autonomous local mirror build started",
            )
            current_state = "capturing"

        if current_state not in {"capturing", "replay_pending", "completed"}:
            raise ValueError(
                f"Game {game_key} must be in pending, failed_retryable, capturing, replay_pending, or completed before build; current state is '{current_state}'"
            )

        return attempt_dir, created_attempt

    def ensure_entry_capture_for_build(
        self,
        game_key: str,
        attempt_dir: Path,
        worker_id: str | None = None,
        timeout_seconds: int = 30,
    ) -> tuple[dict[str, Any], str]:
        entry_body_path = attempt_dir / "artifacts" / "entry" / "body.html"
        if not entry_body_path.exists():
            self.capture_entry_url(
                game_key=game_key,
                worker_id=worker_id,
                timeout_seconds=timeout_seconds,
            )

        entry_summary = read_json(attempt_dir / "artifacts" / "entry" / "summary.json")
        entry_html = entry_body_path.read_text(encoding="utf-8", errors="replace")
        return entry_summary, entry_html

    def recursive_discover_and_download_assets(
        self,
        game_key: str,
        attempt_dir: Path,
        worker_id: str | None = None,
        timeout_seconds: int = 30,
        max_iterations: int = 3,
        verbose: bool = False,
    ) -> dict[str, Any]:
        discovered_urls: set[str] = set()
        runtime_capture_urls_path = attempt_dir / "artifacts" / "runtime_capture" / "runtime_discovered_urls.json"
        if runtime_capture_urls_path.exists():
            runtime_capture_urls = read_json(runtime_capture_urls_path).get("urls") or []
            discovered_urls.update(str(url) for url in runtime_capture_urls if str(url).strip())
        iteration_summaries: list[dict[str, Any]] = []

        for iteration in range(1, max_iterations + 1):
            self.emit_verbose(verbose, f"[discovery] iteration {iteration} start for {game_key}")
            self.analyze_latest_attempt_assets(game_key=game_key)
            asset_report_path = attempt_dir / "artifacts" / "entry" / "asset_urls.json"
            asset_report = read_json(asset_report_path)
            entry_urls = set(str(url) for url in asset_report.get("asset_urls") or [])
            discovered_urls.update(entry_urls)

            existing_download_summary_path = attempt_dir / "artifacts" / "downloaded_assets" / "download_summary.json"
            existing_downloaded_urls: set[str] = set()
            if existing_download_summary_path.exists():
                existing_download_summary = read_json(existing_download_summary_path)
                for item in existing_download_summary.get("downloaded") or []:
                    existing_downloaded_urls.add(str(item.get("asset_url") or ""))
                    final_url = str(item.get("final_url") or "")
                    if final_url:
                        existing_downloaded_urls.add(final_url)

            missing_urls = sorted(url for url in discovered_urls if url not in existing_downloaded_urls)
            self.emit_verbose(
                verbose,
                f"[discovery] iteration {iteration} known={len(discovered_urls)} existing_downloaded={len(existing_downloaded_urls)} missing={len(missing_urls)}",
            )
            if missing_urls:
                write_json(
                    asset_report_path,
                    {
                        "run_id": self.summary().get("run_id"),
                        "game_key": game_key,
                        "attempt_dir": str(attempt_dir),
                        "asset_url_count": len(discovered_urls),
                        "asset_urls": sorted(discovered_urls),
                        "generated_at": utc_now(),
                        "source": "entry_html_plus_recursive_text_assets",
                    },
                )
                self.download_latest_attempt_assets(
                    game_key=game_key,
                    worker_id=worker_id,
                    timeout_seconds=timeout_seconds,
                    verbose=verbose,
                    only_asset_urls=missing_urls,
                )

            download_summary_path = attempt_dir / "artifacts" / "downloaded_assets" / "download_summary.json"
            download_summary = read_json(download_summary_path) if download_summary_path.exists() else {
                "downloaded": [],
                "failed": [],
                "downloaded_count": 0,
                "failed_count": 0,
            }

            recursive_urls: set[str] = set()
            for item in download_summary.get("downloaded") or []:
                body_path_value = str(item.get("body_path") or "")
                if not body_path_value:
                    continue
                body_path = Path(body_path_value)
                content_type = str(item.get("content_type") or "")
                if not body_path.exists() or not looks_like_text_asset(body_path, content_type):
                    continue
                asset_kind = classify_text_asset_kind(body_path)
                if asset_kind not in {"css", "json_config"}:
                    continue

                base_url = str(item.get("final_url") or item.get("asset_url") or "")
                text = body_path.read_text(encoding="utf-8", errors="replace")
                recursive_urls.update(extract_asset_urls_from_text_asset(text, base_url=base_url))

            new_recursive_urls = sorted(url for url in recursive_urls if url not in discovered_urls)
            iteration_summaries.append(
                {
                    "iteration": iteration,
                    "known_url_count": len(discovered_urls),
                    "missing_url_count": len(missing_urls),
                    "recursive_discovered_count": len(recursive_urls),
                    "new_recursive_url_count": len(new_recursive_urls),
                }
            )

            self.emit_verbose(
                verbose,
                f"[discovery] iteration {iteration} recursive_found={len(recursive_urls)} new_recursive={len(new_recursive_urls)}",
            )
            if not new_recursive_urls:
                break

            discovered_urls.update(new_recursive_urls)

        final_download_summary_path = attempt_dir / "artifacts" / "downloaded_assets" / "download_summary.json"
        final_download_summary = read_json(final_download_summary_path) if final_download_summary_path.exists() else {
            "downloaded": [],
            "failed": [],
            "downloaded_count": 0,
            "failed_count": 0,
        }
        asset_report_path = attempt_dir / "artifacts" / "entry" / "asset_urls.json"
        canonical_discovered_urls = sorted({canonicalize_asset_url(url) for url in discovered_urls if str(url).strip()})
        final_asset_report = {
            "run_id": self.summary().get("run_id"),
            "game_key": game_key,
            "attempt_dir": str(attempt_dir),
            "asset_url_count": len(canonical_discovered_urls),
            "asset_urls": canonical_discovered_urls,
            "generated_at": utc_now(),
            "source": "entry_html_recursive_text_assets_and_runtime_capture",
            "iterations": iteration_summaries,
            "runtime_capture_urls_included": runtime_capture_urls_path.exists(),
        }
        write_json(asset_report_path, final_asset_report)
        return {
            "asset_report": final_asset_report,
            "discovered_urls": list(final_asset_report["asset_urls"]),
            "download_summary": final_download_summary,
            "iterations": iteration_summaries,
        }

    def assemble_replay_package(
        self,
        game_key: str,
        attempt_dir: Path,
        entry_html: str,
        discovered_urls: list[str],
        download_summary: dict[str, Any],
        entry_summary: dict[str, Any],
    ) -> dict[str, Any]:
        replay_dir = self.games_dir / game_key / "replay" / attempt_dir.name
        if replay_dir.exists():
            shutil.rmtree(replay_dir)
        replay_dir.mkdir(parents=True, exist_ok=True)

        replacements: dict[str, str] = {}
        html_replacements: dict[str, str] = {}
        url_map_entries: list[dict[str, Any]] = []
        entry_url_for_aliases = str(entry_summary.get("final_url") or entry_summary.get("source_url") or "")
        entry_origin_netloc = parse.urlparse(
            entry_url_for_aliases
        ).netloc.lower() or None

        for item in download_summary.get("downloaded") or []:
            original_url = str(item.get("asset_url") or "")
            final_url = str(item.get("final_url") or "")
            body_path_value = str(item.get("body_path") or "")
            content_type = item.get("content_type")
            if not original_url or not body_path_value:
                continue

            body_path = Path(body_path_value)
            canonical_url = canonicalize_asset_url(final_url or original_url)
            relative_asset_path = derive_replay_asset_relative_path(
                canonical_url,
                content_type,
                origin_netloc=entry_origin_netloc,
            )
            replay_asset_path = replay_dir / relative_asset_path
            replay_asset_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(body_path, replay_asset_path)

            replay_relative = replay_asset_path.relative_to(replay_dir).as_posix()
            alias_urls = build_url_aliases(original_url, final_url)
            for alias_url in alias_urls:
                replacements[alias_url] = replay_relative
                html_replacements[alias_url] = replay_relative

            entry_relative_aliases = build_entry_relative_aliases(
                entry_url_for_aliases,
                final_url or original_url,
            )
            for alias_url in entry_relative_aliases:
                html_replacements[alias_url] = replay_relative

            url_map_entries.append(
                {
                    "original_url": original_url,
                    "final_url": final_url or None,
                    "canonical_url": canonical_url,
                    "alias_urls": alias_urls,
                    "local_path": replay_relative,
                    "content_type": content_type,
                    "status_code": item.get("status_code"),
                    "bytes": item.get("bytes"),
                    "storage_mode": item.get("storage_mode"),
                    "source_body_path": body_path_value,
                    "status": "resolved",
                }
            )

        rewritten_html, applied_replacements = rewrite_text_with_mapping(
            entry_html,
            html_replacements,
            current_file_path=replay_dir / "index.html",
            rewrite_relative_to_file=False,
        )
        write_text(replay_dir / "index.html", rewritten_html)

        rewritten_asset_files: list[dict[str, Any]] = []
        all_text_asset_paths = [
            path
            for path in sorted(replay_dir.rglob("*"))
            if path.is_file() and looks_like_text_asset(path)
        ]
        for _pass_index in range(3):
            for path in all_text_asset_paths:
                original_text = path.read_text(encoding="utf-8", errors="replace")
                rewritten_text, file_replacements = rewrite_text_with_mapping(
                    original_text,
                    replacements,
                    current_file_path=path,
                    rewrite_relative_to_file=True,
                )
                path.write_text(rewritten_text, encoding="utf-8")
                if _pass_index == 0 and path.name != "index.html":
                    rewritten_asset_files.append(
                        {
                            "path": path.relative_to(replay_dir).as_posix(),
                            "kind": classify_text_asset_kind(path),
                            "replacement_count": sum(
                                int(entry.get("replacement_count") or 0) for entry in file_replacements
                            ),
                            "applied_replacements": file_replacements,
                        }
                    )

        unresolved_urls: list[dict[str, Any]] = []
        for asset_url in discovered_urls:
            asset_aliases = build_url_aliases(asset_url)
            resolved_local_path = next((replacements.get(alias_url) for alias_url in asset_aliases if alias_url in replacements), None)
            if resolved_local_path:
                continue
            unresolved_urls.append({"url": asset_url, "aliases_checked": asset_aliases, "reason": "no_downloaded_artifact"})
            url_map_entries.append(
                {
                    "original_url": asset_url,
                    "final_url": None,
                    "canonical_url": canonicalize_asset_url(asset_url),
                    "alias_urls": asset_aliases,
                    "local_path": None,
                    "content_type": None,
                    "status": "unresolved",
                    "reason": "no_downloaded_artifact",
                }
            )

        write_json(replay_dir / "url_map.json", {"entries": url_map_entries, "generated_at": utc_now()})
        write_json(replay_dir / "unresolved_urls.json", {"items": unresolved_urls, "generated_at": utc_now()})
        return {
            "replay_dir": replay_dir,
            "url_map_entries": url_map_entries,
            "unresolved_urls": unresolved_urls,
            "applied_replacements": applied_replacements,
            "rewritten_asset_files": rewritten_asset_files,
            "replacements": replacements,
        }

    def audit_remaining_remote_refs(self, replay_dir: Path) -> dict[str, Any]:
        items: list[dict[str, Any]] = []
        counts_by_kind = {"html": 0, "css": 0, "js": 0, "json_config": 0, "text": 0}
        ignored_metadata_files = {
            "url_map.json",
            "unresolved_urls.json",
            "remaining_remote_refs.json",
            "remaining_remote_refs.pre_branding.json",
            "mirror_build_summary.json",
            "branding_normalization_summary.json",
            "README.md",
        }

        for path in sorted(replay_dir.rglob("*")):
            if not path.is_file() or path.name in ignored_metadata_files or not looks_like_text_asset(path):
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            kind = classify_text_asset_kind(path)
            refs = detect_remote_references(text, kind=kind)
            if path.relative_to(replay_dir).as_posix().startswith("assets/www.w3.org/"):
                refs = []
            if not refs:
                continue
            counts_by_kind[kind] = counts_by_kind.get(kind, 0) + len(refs)
            items.append(
                {
                    "path": path.relative_to(replay_dir).as_posix(),
                    "kind": kind,
                    "remote_refs": refs,
                    "remote_ref_count": len(refs),
                }
            )

        audit = {
            "generated_at": utc_now(),
            "total_files_with_remote_refs": len(items),
            "total_remote_ref_count": sum(item["remote_ref_count"] for item in items),
            "counts_by_kind": counts_by_kind,
            "items": items,
        }
        write_json(replay_dir / "remaining_remote_refs.pre_branding.json", audit)
        write_json(replay_dir / "remaining_remote_refs.json", audit)
        return audit

    def classify_offline_readiness(
        self,
        game_key: str,
        unresolved_urls: list[dict[str, Any]],
        download_summary: dict[str, Any],
        remote_ref_audit: dict[str, Any],
    ) -> tuple[str, list[str]]:
        readiness = "fully_offline_ready"
        blockers: list[str] = []

        if unresolved_urls:
            readiness = "partially_offline_ready"
            blockers.append("One or more discovered remote URLs did not have local downloaded artifacts.")

        failed_asset_count = int(download_summary.get("failed_count") or 0)
        if failed_asset_count > 0:
            readiness = "partially_offline_ready"
            blockers.append(f"{failed_asset_count} discovered asset download(s) failed.")

        total_remote_ref_count = int(remote_ref_audit.get("total_remote_ref_count") or 0)
        if total_remote_ref_count > 0:
            readiness = "partially_offline_ready"
            blockers.append(
                f"Replay package still contains {total_remote_ref_count} remote HTTP(S) reference(s) after rewriting."
            )

        if "live" in json.dumps(read_json(self.games_dir / game_key / "source.json"), ensure_ascii=False).lower():
            blockers.append("Game metadata suggests live/interactivity behavior that may require runtime network capture.")
            if readiness == "fully_offline_ready":
                readiness = "partially_offline_ready"

        return readiness, blockers

    def apply_branding_normalization(self, replay_dir: Path) -> dict[str, Any]:
        protected_file_names = {
            "url_map.json",
            "unresolved_urls.json",
            "remaining_remote_refs.json",
            "mirror_build_summary.json",
            "branding_normalization_summary.json",
        }
        replacements_summary: list[dict[str, Any]] = []
        renamed_paths: list[dict[str, Any]] = []
        skipped_paths: list[dict[str, Any]] = []

        for path in sorted(
            replay_dir.rglob("*"),
            key=lambda candidate: len(candidate.relative_to(replay_dir).parts),
            reverse=True,
        ):
            if path.is_file():
                if path.name in protected_file_names:
                    skipped_paths.append({"path": path.relative_to(replay_dir).as_posix(), "reason": "protected_metadata"})
                    continue
                if not looks_like_text_asset(path):
                    skipped_paths.append({"path": path.relative_to(replay_dir).as_posix(), "reason": "non_text_file"})
                    continue

                original_text = path.read_text(encoding="utf-8", errors="replace")
                normalized_text = re.sub(r"(?<![A-Za-z0-9._/-])Rezona(?![A-Za-z0-9._/-])", "Gamezone", original_text)
                normalized_text = re.sub(r"(?<![A-Za-z0-9._/-])rezona(?![A-Za-z0-9._/-])", "gamezone", normalized_text)
                replacement_count = 0
                if normalized_text != original_text:
                    replacement_count = (
                        len(re.findall(r"(?<![A-Za-z0-9._/-])Rezona(?![A-Za-z0-9._/-])", original_text))
                        + len(re.findall(r"(?<![A-Za-z0-9._/-])rezona(?![A-Za-z0-9._/-])", original_text))
                    )
                    path.write_text(normalized_text, encoding="utf-8")
                    replacements_summary.append(
                        {
                            "path": path.relative_to(replay_dir).as_posix(),
                            "replacement_count": replacement_count,
                        }
                    )

            target_name = re.sub(r"(?<![A-Za-z0-9._/-])Rezona(?![A-Za-z0-9._/-])", "Gamezone", path.name)
            target_name = re.sub(r"(?<![A-Za-z0-9._/-])rezona(?![A-Za-z0-9._/-])", "gamezone", target_name)
            if target_name != path.name:
                target_path = path.with_name(target_name)
                path.rename(target_path)
                renamed_paths.append(
                    {
                        "from": path.relative_to(replay_dir).as_posix(),
                        "to": target_path.relative_to(replay_dir).as_posix(),
                    }
                )

        summary = {
            "generated_at": utc_now(),
            "text_files_changed": len(replacements_summary),
            "paths_renamed": len(renamed_paths),
            "files_changed": replacements_summary,
            "renamed_paths": renamed_paths,
            "skipped_paths": skipped_paths,
            "safeguards": [
                "Runs only after replay assembly.",
                "Skips protected build metadata files.",
                "Skips non-text assets.",
                "Does not modify queue/run-control folders outside the replay package.",
            ],
        }
        write_json(replay_dir / "branding_normalization_summary.json", summary)
        return summary

    def write_replay_summary_outputs(
        self,
        game_key: str,
        attempt_dir: Path,
        replay_dir: Path,
        created_attempt: bool,
        discovered_urls: list[str],
        url_map_entries: list[dict[str, Any]],
        unresolved_urls: list[dict[str, Any]],
        download_summary: dict[str, Any],
        readiness: str,
        blockers: list[str],
        applied_replacements: list[dict[str, Any]],
        recursive_iterations: list[dict[str, Any]],
        rewritten_asset_files: list[dict[str, Any]],
        remote_ref_audit: dict[str, Any],
        branding_summary: dict[str, Any],
    ) -> dict[str, Any]:
        summary = {
            "run_id": self.summary().get("run_id"),
            "game_key": game_key,
            "attempt_name": attempt_dir.name,
            "attempt_dir": str(attempt_dir),
            "replay_dir": str(replay_dir),
            "index_file": str(replay_dir / "index.html"),
            "open_file": str(replay_dir / "index.html"),
            "created_attempt": created_attempt,
            "discovered_url_count": len(discovered_urls),
            "resolved_url_count": sum(1 for entry in url_map_entries if entry.get("status") == "resolved"),
            "unresolved_url_count": len(unresolved_urls),
            "downloaded_asset_count": int(download_summary.get("downloaded_count") or 0),
            "failed_asset_count": int(download_summary.get("failed_count") or 0),
            "recursive_discovery_iterations": recursive_iterations,
            "rewritten_file_count": len([item for item in rewritten_asset_files if item.get("replacement_count")]),
            "rewritten_asset_files": rewritten_asset_files,
            "remaining_remote_ref_count": int(remote_ref_audit.get("total_remote_ref_count") or 0),
            "remaining_remote_ref_counts_by_kind": remote_ref_audit.get("counts_by_kind") or {},
            "branding_normalization": {
                "text_files_changed": branding_summary.get("text_files_changed"),
                "paths_renamed": branding_summary.get("paths_renamed"),
            },
            "offline_readiness": readiness,
            "blockers": blockers,
            "applied_replacements": applied_replacements,
            "generated_at": utc_now(),
        }
        write_json(replay_dir / "mirror_build_summary.json", summary)
        write_text(
            replay_dir / "README.md",
            "\n".join(
                [
                    f"# Local Mirror — {game_key}",
                    "",
                    f"- Attempt: `{attempt_dir.name}`",
                    f"- Offline readiness: `{readiness}`",
                    f"- Open this file: `{replay_dir / 'index.html'}`",
                    "",
                    "See `mirror_build_summary.json`, `unresolved_urls.json`, `remaining_remote_refs.json`, and `branding_normalization_summary.json` for details.",
                    "",
                ]
            ),
        )
        return summary

    def finalize_build_outputs(
        self,
        game_key: str,
        attempt_dir: Path,
        replay_dir: Path,
        summary: dict[str, Any],
        worker_id: str | None = None,
        unresolved_urls: list[dict[str, Any]] | None = None,
    ) -> None:
        metadata_path = attempt_dir / "metadata.json"
        metadata = read_json(metadata_path)
        metadata["latest_replay_build_at"] = summary["generated_at"]
        metadata["latest_replay_dir"] = str(replay_dir)
        metadata["offline_readiness"] = summary["offline_readiness"]
        write_json(metadata_path, metadata)

        post_state, _ = self.find_game_queue_file(game_key)
        if post_state == "capturing":
            self.finalize_attempt(
                game_key=game_key,
                target_state="replay_pending",
                worker_id=worker_id,
                note=f"Autonomous local mirror built with readiness={summary['offline_readiness']}",
            )

        unresolved_urls = unresolved_urls or []
        self.update_game_history(
            game_key,
            event="local_mirror_built",
            status=self.find_game_queue_file(game_key)[0],
            worker_id=worker_id,
            attempt_name=attempt_dir.name,
            replay_dir=str(replay_dir),
            offline_readiness=summary["offline_readiness"],
            unresolved_url_count=len(unresolved_urls),
        )
        self.append_event(
            "local_mirror_built",
            game_key=game_key,
            worker_id=worker_id,
            attempt_name=attempt_dir.name,
            replay_dir=str(replay_dir),
            offline_readiness=summary["offline_readiness"],
            unresolved_url_count=len(unresolved_urls),
        )

    def capture_runtime_requests(
        self,
        game_key: str,
        worker_id: str | None = None,
        timeout_seconds: int = 30,
        wait_after_load_seconds: int = 5,
        wait_until: str = "domcontentloaded",
        skip_networkidle: bool = False,
        post_wait_seconds: int | None = None,
    ) -> dict[str, Any]:
        try:
            from playwright.sync_api import sync_playwright
        except ImportError as exc:
            raise RuntimeError(
                "Playwright is not available in the current Python environment. Use ./.venv/bin/python."
            ) from exc

        attempt_dir, created_attempt = self.ensure_build_capture_state(game_key=game_key, worker_id=worker_id)
        runtime_dir = attempt_dir / "artifacts" / "runtime_capture"
        if runtime_dir.exists():
            shutil.rmtree(runtime_dir)
        runtime_dir.mkdir(parents=True, exist_ok=True)
        responses_dir = runtime_dir / "responses"
        responses_dir.mkdir(parents=True, exist_ok=True)
        screenshots_dir = runtime_dir / "screenshots"
        screenshots_dir.mkdir(parents=True, exist_ok=True)
        runtime_events_path = runtime_dir / "runtime_events.jsonl"

        current_state, current_path = self.find_game_queue_file(game_key)
        record = self.load_queue_record(current_path)
        source_url = str(record.get("source_url") or "")
        if not source_url:
            raise ValueError(f"Queue record for {game_key} is missing source_url")

        requests_log = attempt_dir / "requests.jsonl"
        console_log = attempt_dir / "console.jsonl"
        errors_log = attempt_dir / "errors.jsonl"
        metadata_path = attempt_dir / "metadata.json"
        metadata = read_json(metadata_path)
        effective_post_wait_seconds = post_wait_seconds if post_wait_seconds is not None else wait_after_load_seconds
        effective_wait_until = wait_until.strip().lower()
        if effective_wait_until not in {"domcontentloaded", "networkidle"}:
            raise ValueError("wait_until must be either 'domcontentloaded' or 'networkidle'")
        networkidle_requested = effective_wait_until == "networkidle" and not skip_networkidle
        started_at = utc_now()
        metadata["capture_status"] = "runtime_capture_started"
        metadata["runtime_capture_started_at"] = started_at
        metadata["worker_id"] = worker_id or metadata.get("worker_id")
        metadata["runtime_capture_wait_until"] = effective_wait_until
        metadata["runtime_capture_skip_networkidle"] = skip_networkidle
        metadata["runtime_capture_post_wait_seconds"] = effective_post_wait_seconds
        metadata["runtime_capture_timeout_seconds"] = timeout_seconds
        write_json(metadata_path, metadata)
        append_jsonl(
            runtime_events_path,
            {
                "timestamp": started_at,
                "event": "runtime_capture_started",
                "source_url": source_url,
                "timeout_seconds": timeout_seconds,
                "wait_after_load_seconds": wait_after_load_seconds,
                "post_wait_seconds": effective_post_wait_seconds,
                "wait_until": effective_wait_until,
                "skip_networkidle": skip_networkidle,
            },
        )

        runtime_items: list[dict[str, Any]] = []
        console_messages: list[dict[str, Any]] = []
        page_errors: list[dict[str, Any]] = []
        final_url = source_url
        title = ""
        networkidle_status = "not_requested"
        networkidle_error: str | None = None

        with sync_playwright() as playwright:
            append_jsonl(runtime_events_path, {"timestamp": utc_now(), "event": "browser_launch_started"})
            browser = playwright.chromium.launch(headless=True)
            append_jsonl(runtime_events_path, {"timestamp": utc_now(), "event": "browser_launched"})
            context = browser.new_context()
            append_jsonl(runtime_events_path, {"timestamp": utc_now(), "event": "browser_context_created"})
            page = context.new_page()
            append_jsonl(runtime_events_path, {"timestamp": utc_now(), "event": "page_created"})

            def handle_console(message: Any) -> None:
                entry = {
                    "timestamp": utc_now(),
                    "event": "runtime_console",
                    "type": message.type,
                    "text": message.text,
                }
                console_messages.append(entry)
                append_jsonl(console_log, entry)

            def handle_page_error(error_obj: Any) -> None:
                entry = {
                    "timestamp": utc_now(),
                    "event": "runtime_page_error",
                    "error": str(error_obj),
                }
                page_errors.append(entry)
                append_jsonl(errors_log, entry)

            def handle_response(response: Any) -> None:
                request_obj = response.request
                response_url = response.url
                request_url = request_obj.url
                method = request_obj.method
                resource_type = request_obj.resource_type
                status_code = response.status
                headers = response.headers
                content_type = headers.get("content-type", "").split(";", 1)[0].strip().lower()
                body_path_value: str | None = None
                body_error: str | None = None

                try:
                    body = response.body()
                    file_extension = detect_asset_file_extension(request_url, response_url, headers)
                    response_index = len(runtime_items) + 1
                    response_dir = responses_dir / f"response_{response_index:04d}"
                    response_dir.mkdir(parents=True, exist_ok=True)
                    body_file_name = f"body{file_extension}"
                    body_path = response_dir / body_file_name
                    write_bytes(body_path, body)
                    write_json(
                        response_dir / "metadata.json",
                        {
                            "request_url": request_url,
                            "response_url": response_url,
                            "method": method,
                            "resource_type": resource_type,
                            "status_code": status_code,
                            "content_type": content_type or None,
                            "body_path": str(body_path),
                            "body_file_name": body_file_name,
                            "bytes": len(body),
                            "captured_at": utc_now(),
                        },
                    )
                    body_path_value = str(body_path)
                except Exception as exc:
                    body_error = str(exc)

                entry = {
                    "timestamp": utc_now(),
                    "request_url": request_url,
                    "response_url": response_url,
                    "method": method,
                    "resource_type": resource_type,
                    "status_code": status_code,
                    "content_type": content_type or None,
                    "response_headers": headers,
                    "body_path": body_path_value,
                    "body_capture_error": body_error,
                }
                runtime_items.append(entry)
                append_jsonl(
                    requests_log,
                    {
                        "timestamp": entry["timestamp"],
                        "event": "runtime_response_captured",
                        "request_url": request_url,
                        "response_url": response_url,
                        "method": method,
                        "resource_type": resource_type,
                        "status_code": status_code,
                    },
                )

            page.on("console", handle_console)
            page.on("pageerror", handle_page_error)
            page.on("response", handle_response)
            append_jsonl(runtime_events_path, {"timestamp": utc_now(), "event": "page_event_handlers_registered"})

            append_jsonl(
                runtime_events_path,
                {
                    "timestamp": utc_now(),
                    "event": "goto_started",
                    "source_url": source_url,
                    "wait_until": effective_wait_until,
                },
            )
            page.goto(source_url, wait_until="domcontentloaded", timeout=timeout_seconds * 1000)
            append_jsonl(runtime_events_path, {"timestamp": utc_now(), "event": "goto_completed", "page_url": page.url})
            append_jsonl(runtime_events_path, {"timestamp": utc_now(), "event": "domcontentloaded", "page_url": page.url})

            append_jsonl(runtime_events_path, {"timestamp": utc_now(), "event": "screenshot_started", "name": "after_domcontentloaded.png"})
            try:
                page.screenshot(path=str(screenshots_dir / "after_domcontentloaded.png"), full_page=True)
                append_jsonl(runtime_events_path, {"timestamp": utc_now(), "event": "screenshot_completed", "name": "after_domcontentloaded.png"})
            except Exception as exc:
                append_jsonl(runtime_events_path, {"timestamp": utc_now(), "event": "screenshot_failed", "name": "after_domcontentloaded.png", "error": str(exc)})

            if networkidle_requested:
                append_jsonl(runtime_events_path, {"timestamp": utc_now(), "event": "networkidle_wait_started", "page_url": page.url})
                try:
                    page.wait_for_load_state("networkidle", timeout=timeout_seconds * 1000)
                    networkidle_status = "reached"
                    append_jsonl(runtime_events_path, {"timestamp": utc_now(), "event": "networkidle_reached", "page_url": page.url})
                    append_jsonl(runtime_events_path, {"timestamp": utc_now(), "event": "screenshot_started", "name": "after_networkidle.png"})
                    try:
                        page.screenshot(path=str(screenshots_dir / "after_networkidle.png"), full_page=True)
                        append_jsonl(runtime_events_path, {"timestamp": utc_now(), "event": "screenshot_completed", "name": "after_networkidle.png"})
                    except Exception as exc:
                        append_jsonl(runtime_events_path, {"timestamp": utc_now(), "event": "screenshot_failed", "name": "after_networkidle.png", "error": str(exc)})
                except Exception as exc:
                    networkidle_status = "timeout"
                    networkidle_error = str(exc)
                    append_jsonl(
                        runtime_events_path,
                        {
                            "timestamp": utc_now(),
                            "event": "networkidle_wait_failed",
                            "page_url": page.url,
                            "error": networkidle_error,
                        },
                    )
            else:
                networkidle_status = "skipped" if skip_networkidle else "not_requested"
                append_jsonl(
                    runtime_events_path,
                    {
                        "timestamp": utc_now(),
                        "event": "networkidle_wait_skipped",
                        "page_url": page.url,
                        "reason": "skip_networkidle" if skip_networkidle else "wait_until_domcontentloaded",
                    },
                )

            append_jsonl(runtime_events_path, {"timestamp": utc_now(), "event": "post_wait_started", "seconds": effective_post_wait_seconds, "page_url": page.url})
            page.wait_for_timeout(effective_post_wait_seconds * 1000)
            append_jsonl(runtime_events_path, {"timestamp": utc_now(), "event": "post_wait_completed", "page_url": page.url})
            append_jsonl(runtime_events_path, {"timestamp": utc_now(), "event": "screenshot_started", "name": "after_post_wait.png"})
            try:
                page.screenshot(path=str(screenshots_dir / "after_post_wait.png"), full_page=True)
                append_jsonl(runtime_events_path, {"timestamp": utc_now(), "event": "screenshot_completed", "name": "after_post_wait.png"})
            except Exception as exc:
                append_jsonl(runtime_events_path, {"timestamp": utc_now(), "event": "screenshot_failed", "name": "after_post_wait.png", "error": str(exc)})

            final_url = page.url
            title = page.title()
            append_jsonl(runtime_events_path, {"timestamp": utc_now(), "event": "browser_close_started", "final_url": final_url, "title": title})
            browser.close()
            append_jsonl(runtime_events_path, {"timestamp": utc_now(), "event": "browser_close_completed", "final_url": final_url, "title": title})

        runtime_manifest = {
            "run_id": self.summary().get("run_id"),
            "game_key": game_key,
            "attempt_dir": str(attempt_dir),
            "created_attempt": created_attempt,
            "source_url": source_url,
            "final_url": final_url,
            "page_title": title,
            "wait_until": effective_wait_until,
            "skip_networkidle": skip_networkidle,
            "post_wait_seconds": effective_post_wait_seconds,
            "networkidle_status": networkidle_status,
            "networkidle_error": networkidle_error,
            "runtime_request_count": len(runtime_items),
            "console_message_count": len(console_messages),
            "page_error_count": len(page_errors),
            "items": runtime_items,
            "generated_at": utc_now(),
        }
        write_json(runtime_dir / "runtime_request_manifest.json", runtime_manifest)

        runtime_urls = sorted(
            {
                str(item.get("request_url") or "")
                for item in runtime_items
                if normalize_url_candidate(str(item.get("request_url") or ""))
            }
        )
        write_json(
            runtime_dir / "runtime_discovered_urls.json",
            {
                "run_id": self.summary().get("run_id"),
                "game_key": game_key,
                "attempt_dir": str(attempt_dir),
                "url_count": len(runtime_urls),
                "urls": runtime_urls,
                "generated_at": utc_now(),
            },
        )

        completed_at = utc_now()
        metadata["capture_status"] = "runtime_capture_completed"
        metadata["runtime_capture_completed_at"] = completed_at
        metadata["runtime_capture_manifest_path"] = str(runtime_dir / "runtime_request_manifest.json")
        metadata["runtime_discovered_urls_path"] = str(runtime_dir / "runtime_discovered_urls.json")
        metadata["runtime_events_path"] = str(runtime_events_path)
        metadata["runtime_screenshots_dir"] = str(screenshots_dir)
        metadata["runtime_capture_wait_until"] = effective_wait_until
        metadata["runtime_capture_skip_networkidle"] = skip_networkidle
        metadata["runtime_capture_post_wait_seconds"] = effective_post_wait_seconds
        metadata["runtime_capture_networkidle_status"] = networkidle_status
        metadata["runtime_capture_networkidle_error"] = networkidle_error
        write_json(metadata_path, metadata)
        append_jsonl(
            runtime_events_path,
            {
                "timestamp": completed_at,
                "event": "runtime_capture_completed",
                "runtime_request_count": len(runtime_items),
                "runtime_url_count": len(runtime_urls),
                "console_message_count": len(console_messages),
                "page_error_count": len(page_errors),
                "wait_until": effective_wait_until,
                "skip_networkidle": skip_networkidle,
                "post_wait_seconds": effective_post_wait_seconds,
                "networkidle_status": networkidle_status,
                "networkidle_error": networkidle_error,
            },
        )

        self.update_game_history(
            game_key,
            event="runtime_capture_completed",
            status=self.find_game_queue_file(game_key)[0],
            worker_id=worker_id,
            runtime_request_count=len(runtime_items),
            page_error_count=len(page_errors),
            runtime_url_count=len(runtime_urls),
        )
        self.append_event(
            "runtime_capture_completed",
            game_key=game_key,
            worker_id=worker_id,
            runtime_request_count=len(runtime_items),
            page_error_count=len(page_errors),
            runtime_url_count=len(runtime_urls),
        )

        return {
            "run_id": self.summary().get("run_id"),
            "game_key": game_key,
            "attempt_dir": str(attempt_dir),
            "runtime_request_count": len(runtime_items),
            "runtime_url_count": len(runtime_urls),
            "final_url": final_url,
            "wait_until": effective_wait_until,
            "skip_networkidle": skip_networkidle,
            "post_wait_seconds": effective_post_wait_seconds,
            "networkidle_status": networkidle_status,
            "networkidle_error": networkidle_error,
            "runtime_manifest": str(runtime_dir / "runtime_request_manifest.json"),
        }

    def build_local_mirror(
        self,
        game_key: str,
        worker_id: str | None = None,
        timeout_seconds: int = 30,
        verbose: bool = False,
    ) -> dict[str, Any]:
        self.emit_verbose(verbose, f"[build] start game={game_key} timeout={timeout_seconds}s")
        self.emit_verbose(verbose, f"[build] ensure build/capture state for {game_key}")
        attempt_dir, created_attempt = self.ensure_build_capture_state(game_key=game_key, worker_id=worker_id)
        self.emit_verbose(verbose, f"[build] using attempt_dir={attempt_dir} created_attempt={created_attempt}")
        downloaded_assets_dir = attempt_dir / "artifacts" / "downloaded_assets"
        self.emit_verbose(verbose, f"[build] ensure entry capture for {game_key}")
        entry_summary, entry_html = self.ensure_entry_capture_for_build(
            game_key=game_key,
            attempt_dir=attempt_dir,
            worker_id=worker_id,
            timeout_seconds=timeout_seconds,
        )
        self.emit_verbose(verbose, f"[build] recursive discovery and download for {game_key}")
        discovery_result = self.recursive_discover_and_download_assets(
            game_key=game_key,
            attempt_dir=attempt_dir,
            worker_id=worker_id,
            timeout_seconds=timeout_seconds,
            verbose=verbose,
        )
        self.emit_verbose(
            verbose,
            f"[build] discovery complete discovered={len(discovery_result['discovered_urls'])} downloaded={int(discovery_result['download_summary'].get('downloaded_count') or 0)} failed={int(discovery_result['download_summary'].get('failed_count') or 0)}",
        )
        self.emit_verbose(verbose, f"[build] assemble replay package for {game_key}")
        replay_result = self.assemble_replay_package(
            game_key=game_key,
            attempt_dir=attempt_dir,
            entry_html=entry_html,
            discovered_urls=discovery_result["discovered_urls"],
            download_summary=discovery_result["download_summary"],
            entry_summary=entry_summary,
        )
        self.emit_verbose(verbose, f"[build] audit remaining remote refs for {replay_result['replay_dir']}")
        remote_ref_audit = self.audit_remaining_remote_refs(replay_result["replay_dir"])
        self.emit_verbose(verbose, f"[build] apply branding normalization for {game_key}")
        branding_summary = self.apply_branding_normalization(replay_result["replay_dir"])
        self.emit_verbose(verbose, f"[build] re-audit remaining remote refs after branding normalization for {replay_result['replay_dir']}")
        remote_ref_audit = self.audit_remaining_remote_refs(replay_result["replay_dir"])
        self.emit_verbose(verbose, f"[build] classify offline readiness for {game_key}")
        readiness, blockers = self.classify_offline_readiness(
            game_key=game_key,
            unresolved_urls=replay_result["unresolved_urls"],
            download_summary=discovery_result["download_summary"],
            remote_ref_audit=remote_ref_audit,
        )
        self.emit_verbose(verbose, f"[build] write replay summary outputs for {game_key}")
        summary = self.write_replay_summary_outputs(
            game_key=game_key,
            attempt_dir=attempt_dir,
            replay_dir=replay_result["replay_dir"],
            created_attempt=created_attempt,
            discovered_urls=discovery_result["discovered_urls"],
            url_map_entries=replay_result["url_map_entries"],
            unresolved_urls=replay_result["unresolved_urls"],
            download_summary=discovery_result["download_summary"],
            readiness=readiness,
            blockers=blockers,
            applied_replacements=replay_result["applied_replacements"],
            recursive_iterations=discovery_result["iterations"],
            rewritten_asset_files=replay_result["rewritten_asset_files"],
            remote_ref_audit=remote_ref_audit,
            branding_summary=branding_summary,
        )
        self.emit_verbose(verbose, f"[build] finalize build outputs for {game_key}")
        self.finalize_build_outputs(
            game_key=game_key,
            attempt_dir=attempt_dir,
            replay_dir=replay_result["replay_dir"],
            summary=summary,
            worker_id=worker_id,
            unresolved_urls=replay_result["unresolved_urls"],
        )
        self.emit_verbose(
            verbose,
            f"[build] complete game={game_key} readiness={summary['offline_readiness']} unresolved={summary['unresolved_url_count']} remaining_remote_refs={summary['remaining_remote_ref_count']}",
        )
        return summary

    def rebuild_progress(self) -> dict[str, Any]:
        queue_counts = {state: count_json_files(self.queue_state_path(state)) for state in QUEUE_STATES}
        attempts_total = sum(
            1
            for game_dir in self.games_dir.iterdir()
            if game_dir.is_dir()
            for attempt_dir in (game_dir / "attempts").iterdir()
            if attempt_dir.is_dir()
        ) if self.games_dir.exists() else 0

        summary = self.summary()
        progress = {
            "run_id": summary.get("run_id"),
            "updated_at": utc_now(),
            "input_file": summary.get("input_file"),
            "total_games": summary.get("total_games"),
            "queue_counts": queue_counts,
            "attempts_total": attempts_total,
            "notes": [
                "Progress rebuilt from filesystem state.",
                "Queue counts are derived from queue/*.json files.",
            ],
        }
        write_json(self.progress_json_path, progress)

        progress_md = "\n".join(
            [
                f"# Mirror Run Progress — {summary.get('run_id')}",
                "",
                f"- Updated at: {progress['updated_at']}",
                f"- Input file: `{summary.get('input_file')}`",
                f"- Total games: {summary.get('total_games')}",
                f"- Attempts discovered: {attempts_total}",
                "",
                "## Queue Counts",
                "",
                *(f"- {state}: {queue_counts[state]}" for state in QUEUE_STATES),
                "",
                "## Notes",
                "",
                *(f"- {note}" for note in progress["notes"]),
                "",
            ]
        )
        write_text(self.progress_md_path, progress_md)
        self.append_event("progress_rebuilt", queue_counts=queue_counts, attempts_total=attempts_total)
        return progress

    def lease_next(self, worker_id: str, from_state: str = "pending") -> dict[str, Any]:
        if from_state not in {"pending", "failed_retryable"}:
            raise ValueError("from_state must be 'pending' or 'failed_retryable'")

        candidates = sorted(self.queue_state_path(from_state).glob("*.json"))
        if not candidates:
            raise RuntimeError(f"No queue items available in state '{from_state}'")

        source_path = candidates[0]
        record = self.load_queue_record(source_path)
        game_key = record["game_key"]
        target_path = self.queue_state_path("leased") / source_path.name

        if target_path.exists():
            raise FileExistsError(f"Lease target already exists: {target_path}")

        attempt_count = int(record.get("attempt_count", 0)) + 1
        timestamp = utc_now()
        record.update(
            {
                "status": "leased",
                "attempt_count": attempt_count,
                "leased_at": timestamp,
                "updated_at": timestamp,
                "worker_id": worker_id,
                "previous_state": from_state,
            }
        )

        self.save_queue_record(source_path, record)
        source_path.replace(target_path)
        self.update_game_status(game_key, "leased")
        self.update_game_history(
            game_key,
            event="game_leased",
            status="leased",
            worker_id=worker_id,
            attempt_count=attempt_count,
            previous_state=from_state,
        )
        self.write_worker_status(worker_id=worker_id, current_game=game_key, status="leased")
        self.append_event(
            "game_leased",
            worker_id=worker_id,
            game_key=game_key,
            previous_state=from_state,
            attempt_count=attempt_count,
        )

        return {
            "run_id": self.summary().get("run_id"),
            "worker_id": worker_id,
            "leased_from": from_state,
            "queue_file": str(target_path),
            "game_key": game_key,
            "attempt_count": attempt_count,
            "source_url": record.get("source_url"),
        }

    def transition_game(
        self,
        game_key: str,
        target_state: str,
        worker_id: str | None = None,
        note: str | None = None,
    ) -> dict[str, Any]:
        if target_state not in QUEUE_STATES:
            raise ValueError(f"Unknown target state: {target_state}")

        current_state, current_path = self.find_game_queue_file(game_key)
        if current_state == target_state:
            raise ValueError(f"Game {game_key} is already in state '{target_state}'")

        record = self.load_queue_record(current_path)
        record["status"] = target_state
        record["updated_at"] = utc_now()
        if worker_id:
            record["worker_id"] = worker_id
        if note:
            record["note"] = note

        target_path = self.queue_state_path(target_state) / current_path.name
        self.save_queue_record(current_path, record)
        current_path.replace(target_path)

        self.update_game_status(game_key, target_state)
        self.update_game_history(
            game_key,
            event="state_transition",
            status=target_state,
            previous_state=current_state,
            worker_id=worker_id,
            note=note,
        )
        if worker_id:
            self.write_worker_status(worker_id=worker_id, current_game=game_key, status=target_state)

        self.append_event(
            "state_transition",
            game_key=game_key,
            previous_state=current_state,
            target_state=target_state,
            worker_id=worker_id,
            note=note,
        )

        return {
            "run_id": self.summary().get("run_id"),
            "game_key": game_key,
            "previous_state": current_state,
            "target_state": target_state,
            "queue_file": str(target_path),
        }

    def finalize_attempt(
        self,
        game_key: str,
        target_state: str = "replay_pending",
        worker_id: str | None = None,
        note: str | None = None,
    ) -> dict[str, Any]:
        if target_state not in {"replay_pending", "completed", "failed_retryable", "failed_terminal"}:
            raise ValueError(
                "target_state must be one of: replay_pending, completed, failed_retryable, failed_terminal"
            )

        current_state, current_path = self.find_game_queue_file(game_key)
        if current_state != "capturing":
            raise ValueError(
                f"Game {game_key} must be in 'capturing' before finalization; current state is '{current_state}'"
            )

        record = self.load_queue_record(current_path)
        attempt_dir = self.find_latest_attempt_dir(game_key)
        metadata_path = attempt_dir / "metadata.json"
        metadata = read_json(metadata_path)

        finished_at = utc_now()
        request_summary = read_json(attempt_dir / "request_summary.json")
        download_summary_path = attempt_dir / "artifacts" / "downloaded_assets" / "download_summary.json"
        download_summary = read_json(download_summary_path) if download_summary_path.exists() else None

        capture_status = str(metadata.get("capture_status") or "").strip()
        if not capture_status:
            capture_status = "finalized"

        metadata["capture_status"] = capture_status
        metadata["finalized_at"] = finished_at
        metadata["final_queue_state"] = target_state
        metadata["current_queue_state"] = target_state
        if note:
            metadata["finalization_note"] = note
        write_json(metadata_path, metadata)

        write_text(attempt_dir / "finished_at.txt", finished_at + "\n")
        write_text(attempt_dir / "result.txt", target_state + "\n")
        write_json(
            attempt_dir / "finalization_summary.json",
            {
                "run_id": self.summary().get("run_id"),
                "game_key": game_key,
                "attempt_dir": str(attempt_dir),
                "previous_state": current_state,
                "target_state": target_state,
                "capture_status": capture_status,
                "worker_id": worker_id,
                "note": note,
                "finalized_at": finished_at,
                "request_summary": request_summary,
                "download_summary_present": download_summary is not None,
                "downloaded_count": (download_summary or {}).get("downloaded_count"),
                "failed_count": (download_summary or {}).get("failed_count"),
            },
        )

        transition_result = self.transition_game(
            game_key=game_key,
            target_state=target_state,
            worker_id=worker_id,
            note=note or f"Attempt finalized from capture status '{capture_status}'",
        )

        history_status = target_state
        self.update_game_history(
            game_key,
            event="attempt_finalized",
            status=history_status,
            worker_id=worker_id,
            attempt_name=attempt_dir.name,
            capture_status=capture_status,
            note=note,
            request_summary=request_summary,
            download_summary=download_summary,
            previous_attempt_result=read_text_if_exists(attempt_dir / "result.txt"),
        )
        self.append_event(
            "attempt_finalized",
            game_key=game_key,
            worker_id=worker_id,
            attempt_name=attempt_dir.name,
            capture_status=capture_status,
            target_state=target_state,
            note=note,
        )

        return {
            "run_id": self.summary().get("run_id"),
            "game_key": game_key,
            "attempt_dir": str(attempt_dir),
            "attempt_name": attempt_dir.name,
            "previous_state": current_state,
            "target_state": target_state,
            "capture_status": capture_status,
            "finalized_at": finished_at,
            "queue_file": transition_result["queue_file"],
        }


class MirrorRunInitializer:
    def __init__(
        self,
        input_path: Path,
        runs_root: Path,
        run_id: str | None,
        force: bool,
    ) -> None:
        self.input_path = input_path
        self.runs_root = runs_root
        self.run_id = run_id or self.default_run_id()
        self.force = force
        self.run_dir = self.runs_root / self.run_id

    def default_run_id(self) -> str:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        return f"run_{timestamp}"

    def validate_input(self) -> list[dict[str, Any]]:
        if not self.input_path.exists():
            raise FileNotFoundError(f"Input file not found: {self.input_path}")

        payload = read_json(self.input_path)
        items = payload.get("items")
        if not isinstance(items, list):
            raise ValueError(
                f"Expected {self.input_path} to contain a top-level object with an 'items' list."
            )

        invalid_indexes: list[int] = []
        for index, item in enumerate(items):
            if not isinstance(item, dict):
                invalid_indexes.append(index)
                continue
            if item.get("game_id") is None or not item.get("url"):
                invalid_indexes.append(index)

        if invalid_indexes:
            preview = ", ".join(str(index) for index in invalid_indexes[:10])
            raise ValueError(
                f"Input contains malformed items missing required fields at indexes: {preview}"
            )

        return items

    def normalize_items(self, items: list[dict[str, Any]]) -> list[NormalizedEntry]:
        normalized: list[NormalizedEntry] = []
        source_input_file = str(self.input_path)

        for index, item in enumerate(items):
            creator = item.get("creator") or {}
            topic = item.get("topic") or {}
            source_url = str(item["url"])
            normalized.append(
                NormalizedEntry(
                    game_key=infer_game_key(item, source_url),
                    source_url=source_url,
                    url_type=infer_url_type(source_url),
                    game_id=item.get("game_id"),
                    game_version=item.get("game_version"),
                    name=str(item.get("name") or ""),
                    creator_name=creator.get("name"),
                    creator_id=creator.get("id"),
                    topic_id=topic.get("id"),
                    topic_name=topic.get("name"),
                    source_record_index=index,
                    source_input_file=source_input_file,
                    raw_item=item,
                )
            )

        return normalized

    def ensure_run_dir(self) -> None:
        if self.run_dir.exists() and not self.force:
            raise FileExistsError(
                f"Run directory already exists: {self.run_dir}. Pass --force to overwrite."
            )

        self.run_dir.mkdir(parents=True, exist_ok=True)
        for relative_path in RUN_SUBDIRECTORIES:
            (self.run_dir / relative_path).mkdir(parents=True, exist_ok=True)

    def write_run_metadata(self, normalized_items: list[NormalizedEntry]) -> None:
        queue_files = {state: 0 for state in QUEUE_STATES}
        queue_files["pending"] = len(normalized_items)

        run_metadata = {
            "run_id": self.run_id,
            "created_at": utc_now(),
            "input_file": str(self.input_path),
            "runs_root": str(self.runs_root),
            "total_games": len(normalized_items),
            "queue_states": QUEUE_STATES,
            "notes": [
                "Filesystem-as-database scaffold only; browser capture/replay phases are not implemented yet.",
                "Input path is dynamic and expected to match the deduped catalog schema with a top-level 'items' array.",
            ],
        }
        write_json(self.run_dir / "manifest" / "summary.json", run_metadata)

        config = {
            "network": {
                "proxy_mode": "system_default",
                "proxy_enabled": False,
                "notes": "Use the laptop's normal network path by default. Explicit proxy config can be added later.",
            },
            "capture": {
                "engine": "playwright_planned",
                "status": "scaffold_only",
            },
        }
        write_json(self.run_dir / "config" / "runtime_config.json", config)

        progress = {
            "run_id": self.run_id,
            "updated_at": utc_now(),
            "total_games": len(normalized_items),
            "queue_counts": queue_files,
            "attempts_total": 0,
            "notes": [
                "Run scaffold initialized successfully.",
                "No capture attempts have been executed yet.",
            ],
        }
        write_json(self.run_dir / "reports" / "progress.json", progress)

        progress_md = "\n".join(
            [
                f"# Mirror Run Progress — {self.run_id}",
                "",
                f"- Updated at: {progress['updated_at']}",
                f"- Input file: `{self.input_path}`",
                f"- Total games: {len(normalized_items)}",
                "",
                "## Queue Counts",
                "",
                *(f"- {state}: {queue_files[state]}" for state in QUEUE_STATES),
                "",
                "## Notes",
                "",
                *(f"- {note}" for note in progress["notes"]),
                "",
            ]
        )
        write_text(self.run_dir / "reports" / "progress.md", progress_md)

        append_jsonl(
            self.run_dir / "events" / "events.jsonl",
            {
                "timestamp": utc_now(),
                "event": "run_initialized",
                "run_id": self.run_id,
                "input_file": str(self.input_path),
                "total_games": len(normalized_items),
            },
        )

    def write_manifest(self, normalized_items: list[NormalizedEntry]) -> None:
        manifest_path = self.run_dir / "manifest" / "all_games.jsonl"
        for entry in normalized_items:
            append_jsonl(manifest_path, entry.to_manifest_record())

    def write_game_seed_files(self, normalized_items: list[NormalizedEntry]) -> None:
        for entry in normalized_items:
            game_dir = self.run_dir / "games" / entry.game_key
            attempts_dir = game_dir / "attempts"
            artifacts_dir = game_dir / "artifacts"
            logs_dir = game_dir / "logs"
            replay_dir = game_dir / "replay"

            attempts_dir.mkdir(parents=True, exist_ok=True)
            artifacts_dir.mkdir(parents=True, exist_ok=True)
            logs_dir.mkdir(parents=True, exist_ok=True)
            replay_dir.mkdir(parents=True, exist_ok=True)

            write_json(game_dir / "source.json", entry.raw_item)
            write_text(game_dir / "status.txt", "pending\n")
            append_jsonl(
                game_dir / "history.jsonl",
                {
                    "timestamp": utc_now(),
                    "event": "game_seeded",
                    "status": "pending",
                    "run_id": self.run_id,
                    "game_key": entry.game_key,
                },
            )

            queue_record = entry.to_queue_record(self.run_id)
            write_json(
                self.run_dir / "queue" / "pending" / f"{entry.game_key}.json",
                queue_record,
            )

    def initialize(self) -> dict[str, Any]:
        items = self.validate_input()
        normalized_items = self.normalize_items(items)
        self.ensure_run_dir()
        self.write_manifest(normalized_items)
        self.write_game_seed_files(normalized_items)
        self.write_run_metadata(normalized_items)

        return {
            "run_id": self.run_id,
            "run_dir": str(self.run_dir),
            "input_file": str(self.input_path),
            "total_games": len(normalized_items),
            "manifest_path": str(self.run_dir / "manifest" / "all_games.jsonl"),
            "progress_report": str(self.run_dir / "reports" / "progress.json"),
        }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Initialize and operate a filesystem-based mirror run."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    create_run_parser = subparsers.add_parser(
        "create-run", help="Create a new mirror run scaffold from an input JSON file."
    )
    create_run_parser.add_argument(
        "--input",
        required=True,
        help="Path to a deduped catalog JSON file with a top-level 'items' array.",
    )
    create_run_parser.add_argument(
        "--runs-root",
        default="mirror_runs",
        help="Root directory where mirror run folders should be created.",
    )
    create_run_parser.add_argument(
        "--run-id",
        help="Optional explicit run id. Defaults to run_<UTC timestamp>.",
    )
    create_run_parser.add_argument(
        "--force",
        action="store_true",
        help="Allow reusing an existing run directory path.",
    )

    lease_parser = subparsers.add_parser(
        "lease-next",
        help="Lease the next queue item from pending or failed_retryable into leased.",
    )
    lease_parser.add_argument("--run-dir", required=True, help="Path to an existing downloader run.")
    lease_parser.add_argument(
        "--worker-id",
        required=True,
        help="Stable worker id used for filesystem heartbeat/status files.",
    )
    lease_parser.add_argument(
        "--from-state",
        choices=["pending", "failed_retryable"],
        default="pending",
        help="Queue state to lease from.",
    )

    transition_parser = subparsers.add_parser(
        "transition-game",
        help="Move a game queue record to a new state and update status/history.",
    )
    transition_parser.add_argument("--run-dir", required=True, help="Path to an existing downloader run.")
    transition_parser.add_argument("--game-key", required=True, help="Game key to transition.")
    transition_parser.add_argument(
        "--target-state",
        required=True,
        choices=QUEUE_STATES,
        help="Target queue state.",
    )
    transition_parser.add_argument("--worker-id", help="Optional worker id performing the transition.")
    transition_parser.add_argument("--note", help="Optional note stored in history and events.")

    attempt_parser = subparsers.add_parser(
        "init-attempt",
        help="Create the per-attempt filesystem scaffold for a specific game.",
    )
    attempt_parser.add_argument("--run-dir", required=True, help="Path to an existing downloader run.")
    attempt_parser.add_argument("--game-key", required=True, help="Game key to initialize an attempt for.")
    attempt_parser.add_argument("--worker-id", help="Optional worker id attached to the attempt.")

    recover_parser = subparsers.add_parser(
        "recover-stale",
        help="Recover stale leased/capturing work back into a requeue state.",
    )
    recover_parser.add_argument("--run-dir", required=True, help="Path to an existing downloader run.")
    recover_parser.add_argument(
        "--max-age-minutes",
        type=int,
        default=30,
        help="Minimum worker heartbeat age, in minutes, required before recovery.",
    )
    recover_parser.add_argument(
        "--requeue-state",
        choices=["pending", "failed_retryable"],
        default="pending",
        help="Queue state to move recovered work into.",
    )

    capture_parser = subparsers.add_parser(
        "capture-entry",
        help="Fetch the entry URL into the latest attempt folder using a simple urllib fallback.",
    )
    capture_parser.add_argument("--run-dir", required=True, help="Path to an existing downloader run.")
    capture_parser.add_argument("--game-key", required=True, help="Game key to capture.")
    capture_parser.add_argument("--worker-id", help="Optional worker id attached to the capture.")
    capture_parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=30,
        help="Timeout for the entry URL fetch.",
    )

    analyze_assets_parser = subparsers.add_parser(
        "analyze-entry-assets",
        help="Extract static asset-like URLs from the latest captured entry HTML.",
    )
    analyze_assets_parser.add_argument("--run-dir", required=True, help="Path to an existing downloader run.")
    analyze_assets_parser.add_argument("--game-key", required=True, help="Game key to analyze.")

    download_assets_parser = subparsers.add_parser(
        "download-entry-assets",
        help="Download asset URLs listed in the latest attempt's asset_urls.json file.",
    )
    download_assets_parser.add_argument("--run-dir", required=True, help="Path to an existing downloader run.")
    download_assets_parser.add_argument("--game-key", required=True, help="Game key to download assets for.")
    download_assets_parser.add_argument("--worker-id", help="Optional worker id attached to the download.")
    download_assets_parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=30,
        help="Timeout for each asset download.",
    )
    download_assets_parser.add_argument(
        "--limit",
        type=int,
        help="Optional maximum number of assets to download from the manifest.",
    )

    finalize_parser = subparsers.add_parser(
        "finalize-attempt",
        help="Finalize the latest attempt and move a capturing game into a terminal or next-phase queue state.",
    )
    finalize_parser.add_argument("--run-dir", required=True, help="Path to an existing downloader run.")
    finalize_parser.add_argument("--game-key", required=True, help="Game key to finalize.")
    finalize_parser.add_argument("--worker-id", help="Optional worker id performing the finalization.")
    finalize_parser.add_argument(
        "--target-state",
        choices=["replay_pending", "completed", "failed_retryable", "failed_terminal"],
        default="replay_pending",
        help="Queue state to move the game into after finalizing the attempt.",
    )
    finalize_parser.add_argument("--note", help="Optional note stored in history and events.")

    build_local_parser = subparsers.add_parser(
        "build-local-mirror",
        help="Autonomously capture, download, rewrite, and package a local mirror for one game.",
    )
    build_local_parser.add_argument("--run-dir", required=True, help="Path to an existing downloader run.")
    build_local_parser.add_argument("--game-key", required=True, help="Game key to build a local mirror for.")
    build_local_parser.add_argument("--worker-id", help="Optional worker id attached to the build.")
    build_local_parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=30,
        help="Timeout used for entry capture and asset downloads.",
    )
    build_local_parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print super-verbose phase and per-asset progress to stdout during the build.",
    )

    runtime_capture_parser = subparsers.add_parser(
        "capture-runtime",
        help="Use Playwright to capture runtime requests and responses into the latest attempt folder.",
    )
    runtime_capture_parser.add_argument("--run-dir", required=True, help="Path to an existing downloader run.")
    runtime_capture_parser.add_argument("--game-key", required=True, help="Game key to capture runtime activity for.")
    runtime_capture_parser.add_argument("--worker-id", help="Optional worker id attached to the runtime capture.")
    runtime_capture_parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=30,
        help="Navigation timeout for the Playwright page load.",
    )
    runtime_capture_parser.add_argument(
        "--wait-after-load-seconds",
        type=int,
        default=5,
        help="Compatibility alias for the post-load fixed wait in seconds.",
    )
    runtime_capture_parser.add_argument(
        "--wait-until",
        choices=["domcontentloaded", "networkidle"],
        default="domcontentloaded",
        help="Requested page readiness mode before the fixed post-load wait begins.",
    )
    runtime_capture_parser.add_argument(
        "--post-wait-seconds",
        type=int,
        help="Fixed additional wait in seconds after initial page readiness is reached.",
    )
    runtime_capture_parser.add_argument(
        "--skip-networkidle",
        action="store_true",
        help="Skip the explicit networkidle wait even if a networkidle-oriented capture mode is requested.",
    )

    report_parser = subparsers.add_parser(
        "rebuild-report",
        help="Rebuild progress reports from the current filesystem state.",
    )
    report_parser.add_argument("--run-dir", required=True, help="Path to an existing downloader run.")

    return parser


def handle_create_run(args: argparse.Namespace) -> int:
    initializer = MirrorRunInitializer(
        input_path=Path(args.input),
        runs_root=Path(args.runs_root),
        run_id=args.run_id,
        force=args.force,
    )
    result = initializer.initialize()
    print(pretty_json(result))
    return 0


def handle_lease_next(args: argparse.Namespace) -> int:
    run = MirrorRun(Path(args.run_dir))
    result = run.lease_next(worker_id=args.worker_id, from_state=args.from_state)
    run.rebuild_progress()
    print(pretty_json(result))
    return 0


def handle_transition_game(args: argparse.Namespace) -> int:
    run = MirrorRun(Path(args.run_dir))
    result = run.transition_game(
        game_key=args.game_key,
        target_state=args.target_state,
        worker_id=args.worker_id,
        note=args.note,
    )
    run.rebuild_progress()
    print(pretty_json(result))
    return 0


def handle_init_attempt(args: argparse.Namespace) -> int:
    run = MirrorRun(Path(args.run_dir))
    result = run.initialize_attempt(game_key=args.game_key, worker_id=args.worker_id)
    run.rebuild_progress()
    print(pretty_json(result))
    return 0


def handle_recover_stale(args: argparse.Namespace) -> int:
    run = MirrorRun(Path(args.run_dir))
    result = run.recover_stale_workers(
        max_age_minutes=args.max_age_minutes,
        requeue_state=args.requeue_state,
    )
    run.rebuild_progress()
    print(pretty_json(result))
    return 0


def handle_capture_entry(args: argparse.Namespace) -> int:
    run = MirrorRun(Path(args.run_dir))
    result = run.capture_entry_url(
        game_key=args.game_key,
        worker_id=args.worker_id,
        timeout_seconds=args.timeout_seconds,
    )
    run.rebuild_progress()
    print(pretty_json(result))
    return 0


def handle_analyze_entry_assets(args: argparse.Namespace) -> int:
    run = MirrorRun(Path(args.run_dir))
    result = run.analyze_latest_attempt_assets(game_key=args.game_key)
    run.rebuild_progress()
    print(pretty_json(result))
    return 0


def handle_download_entry_assets(args: argparse.Namespace) -> int:
    run = MirrorRun(Path(args.run_dir))
    result = run.download_latest_attempt_assets(
        game_key=args.game_key,
        worker_id=args.worker_id,
        timeout_seconds=args.timeout_seconds,
        limit=args.limit,
    )
    run.rebuild_progress()
    print(pretty_json(result))
    return 0


def handle_finalize_attempt(args: argparse.Namespace) -> int:
    run = MirrorRun(Path(args.run_dir))
    result = run.finalize_attempt(
        game_key=args.game_key,
        target_state=args.target_state,
        worker_id=args.worker_id,
        note=args.note,
    )
    run.rebuild_progress()
    print(pretty_json(result))
    return 0


def handle_build_local_mirror(args: argparse.Namespace) -> int:
    run = MirrorRun(Path(args.run_dir))
    result = run.build_local_mirror(
        game_key=args.game_key,
        worker_id=args.worker_id,
        timeout_seconds=args.timeout_seconds,
        verbose=args.verbose,
    )
    run.rebuild_progress()
    print(pretty_json(result))
    return 0


def handle_capture_runtime(args: argparse.Namespace) -> int:
    run = MirrorRun(Path(args.run_dir))
    result = run.capture_runtime_requests(
        game_key=args.game_key,
        worker_id=args.worker_id,
        timeout_seconds=args.timeout_seconds,
        wait_after_load_seconds=args.wait_after_load_seconds,
        wait_until=args.wait_until,
        skip_networkidle=args.skip_networkidle,
        post_wait_seconds=args.post_wait_seconds,
    )
    run.rebuild_progress()
    print(pretty_json(result))
    return 0


def handle_rebuild_report(args: argparse.Namespace) -> int:
    run = MirrorRun(Path(args.run_dir))
    result = run.rebuild_progress()
    print(pretty_json(result))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "create-run":
            return handle_create_run(args)
        if args.command == "lease-next":
            return handle_lease_next(args)
        if args.command == "transition-game":
            return handle_transition_game(args)
        if args.command == "init-attempt":
            return handle_init_attempt(args)
        if args.command == "recover-stale":
            return handle_recover_stale(args)
        if args.command == "capture-entry":
            return handle_capture_entry(args)
        if args.command == "analyze-entry-assets":
            return handle_analyze_entry_assets(args)
        if args.command == "download-entry-assets":
            return handle_download_entry_assets(args)
        if args.command == "finalize-attempt":
            return handle_finalize_attempt(args)
        if args.command == "build-local-mirror":
            return handle_build_local_mirror(args)
        if args.command == "capture-runtime":
            return handle_capture_runtime(args)
        if args.command == "rebuild-report":
            return handle_rebuild_report(args)
    except Exception as exc:  # pragma: no cover - CLI safety path
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())