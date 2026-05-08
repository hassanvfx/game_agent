#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlparse

TEXT_SCAN_SUFFIXES = {
    ".html",
    ".htm",
    ".css",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".json",
    ".md",
    ".txt",
}

MEDIA_SCAN_SUFFIXES = {
    ".html",
    ".htm",
    ".css",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
}

EXTERNAL_URL_RE = re.compile(r"https?://[^\s\"'()<>]+", re.IGNORECASE)
CSS_URL_RE = re.compile(r"url\((?P<quote>['\"]?)(?P<value>[^)'\"]+)(?P=quote)\)", re.IGNORECASE)
HTML_ATTR_RE = re.compile(
    r"""(?P<attr>\b(?:src|href|poster|data-src|data-href)\b)\s*=\s*(?P<quote>['"])(?P<value>.*?)(?P=quote)""",
    re.IGNORECASE,
)
QUOTED_PATH_RE = re.compile(
    r"""(?P<quote>['"])(?P<value>(?:\.{0,2}/)?assets/[^"'()\s<>]+\.(?:mp3|wav|ogg|m4a|aac|flac|png|jpg|jpeg|gif|webp|svg|mp4|webm|mov|m4v|woff|woff2|ttf|otf|eot|css))(?P=quote)""",
    re.IGNORECASE,
)
ASSET_EXTENSION_HIT_RE = re.compile(
    r"""(?i)(?:^|(?<=[\s"'(=:,;\[]))(?:/assets|(?:\.{0,2}/)?assets)/[^\s"'()<>]+\.(?:mp3|wav|ogg|m4a|aac|flac|png|jpg|jpeg|gif|webp|svg|mp4|webm|mov|m4v|woff|woff2|ttf|otf|eot|css)"""
)
FONT_FAMILY_RE = re.compile(r"""font-family\s*:\s*([^;}{]+)""", re.IGNORECASE)
IMPORT_FONT_URL_RE = re.compile(r"""@import\s+url\((?P<quote>['"]?)(?P<value>[^)'" ]+)(?P=quote)\)""", re.IGNORECASE)
MATERIAL_SYMBOLS_RE = re.compile(r"""material-symbols(?:-outlined|-rounded|-sharp)?""", re.IGNORECASE)

MEDIA_EXTENSIONS = {
    ".mp3": "audio",
    ".wav": "audio",
    ".ogg": "audio",
    ".m4a": "audio",
    ".aac": "audio",
    ".flac": "audio",
    ".png": "image",
    ".jpg": "image",
    ".jpeg": "image",
    ".gif": "gif",
    ".webp": "image",
    ".svg": "image",
    ".mp4": "video",
    ".webm": "video",
    ".mov": "video",
    ".m4v": "video",
}

FONT_EXTENSIONS = {
    ".woff": "font_file",
    ".woff2": "font_file",
    ".ttf": "font_file",
    ".otf": "font_file",
    ".eot": "font_file",
    ".css": "font_stylesheet",
}

ALLOWED_EXACT_HOSTS = {
    "gamezone-virid.vercel.app",
    "giphy.com",
    "media.giphy.com",
    "i.giphy.com",
    "fonts.googleapis.com",
    "fonts.gstatic.com",
    "cdn.tailwindcss.com",
    "apis.google.com",
    "brm.io",
    "cdn.jsdelivr.net",
    "computergraphics.stackexchange.com",
    "discourse.threejs.org",
    "en.wikipedia.org",
    "evanw.github.com",
    "evilmartians.com",
    "gamedev.stackexchange.com",
    "geomalgorithms.com",
    "github.com",
    "graphics.stanford.edu",
    "ideone.com",
    "jacksondunstan.com",
    "jsperf.com",
    "mathworld.wolfram.com",
    "mths.be",
    "opencollective.com",
    "paulbourke.net",
    "peerjs.com",
    "planning.cs.uiuc.edu",
    "prideout.net",
    "react.dev",
    "reactjs.org",
    "regex101.com",
    "seblagarde.files.wordpress.com",
    "serverfault.com",
    "stackoverflow.com",
    "storage.googleapis.com",
    "tailwindcss.com",
    "twitter.com",
    "www.blackpawn.com",
    "www.bobatkins.com",
    "www.cemyuksel.com",
    "www.chiark.greenend.org.uk",
    "www.cs.indiana.edu",
    "www.desmos.com",
    "www.euclideanspace.com",
    "www.fox-toolkit.org",
    "www.gamedev.net",
    "www.geometrictools.com",
    "www.gstatic.com",
    "www.khronos.org",
    "www.mathworks.com",
    "www.oodesign.com",
    "www.opensource.org",
    "www.pixijs.com",
    "www.ppsloan.org",
    "www.rorydriscoll.com",
    "www.russellcottrell.com",
    "www.scirra.com",
    "www.terathon.com",
    "www.w3.org",
    "www.w3ctech.com",
    "www.youtube.com",
}

ALLOWED_HOST_SUBSTRINGS = (
    "unpkg.com",
    "cdnjs.cloudflare.com",
    "cdn.jsdelivr.net",
    "cdn.jsdelivr.com",
    "skypack.dev",
    "esm.sh",
    "react.dev",
    "www.w3.org",
    "aistudiocdn.com",
)

HARDBLOCK_HOST_SUBSTRINGS = (
    "rezona",
    "resona",
)

METADATA_EXCLUDED_FILENAMES = {
    "branding_normalization_summary.json",
    "candidate_probe.json",
    "candidate_probe_dedup.json",
    "media_cleanup_plan.json",
    "mirror_build_summary.json",
    "url_map.json",
}

ACTIONABLE_SOURCE_SUFFIXES = {
    ".html",
    ".htm",
    ".css",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
}


def _normalize_host(host: str) -> str:
    return host.lower().strip().strip(".")


def _is_external_reference(value: str) -> bool:
    lowered = value.lower().strip()
    return lowered.startswith(("http://", "https://"))


def _looks_like_local_asset_reference(value: str) -> bool:
    lowered = value.lower().strip()
    return "assets/" in lowered and not _is_external_reference(lowered)


def _guess_extension(value: str) -> str:
    cleaned = value.split("?", 1)[0].split("#", 1)[0]
    return Path(cleaned).suffix.lower()


def _guess_media_kind(value: str) -> str | None:
    return MEDIA_EXTENSIONS.get(_guess_extension(value))


def _guess_font_kind(value: str) -> str | None:
    return FONT_EXTENSIONS.get(_guess_extension(value))


def _is_allowed_media_replacement_ref(value: str, candidate_type: str) -> bool:
    if not isinstance(value, str) or not isinstance(candidate_type, str):
        return False
    if candidate_type not in {"audio", "image", "gif", "video"}:
        return False
    if not _is_external_reference(value):
        return False
    return _is_allowed_external_url(value)


def _is_allowed_font_ref(value: str) -> bool:
    if not isinstance(value, str):
        return False
    if not _is_external_reference(value):
        return False
    return _is_allowed_external_url(value)


def _candidate_location_kind(value: str) -> str:
    return "external" if _is_external_reference(value) else "local_relative"


def _is_under_assets(value: str) -> bool:
    return "assets/" in value.lower()


def _is_allowed_external_url(url: str) -> bool:
    parsed = urlparse(url)
    host = _normalize_host(parsed.netloc)
    if not host:
        return False
    if host in ALLOWED_EXACT_HOSTS:
        return True
    return any(token in host for token in ALLOWED_HOST_SUBSTRINGS)


def _is_hardblocked_url(url: str) -> bool:
    lowered = url.lower()
    return any(token in lowered for token in HARDBLOCK_HOST_SUBSTRINGS)


def _should_scan_file(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in TEXT_SCAN_SUFFIXES and path.name not in METADATA_EXCLUDED_FILENAMES


def _iter_scan_files(workspace: Path) -> list[Path]:
    return sorted(path for path in workspace.rglob("*") if _should_scan_file(path))


def _should_scan_media_file(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in MEDIA_SCAN_SUFFIXES and path.name not in METADATA_EXCLUDED_FILENAMES


def _iter_media_scan_files(workspace: Path) -> list[Path]:
    return sorted(path for path in workspace.rglob("*") if _should_scan_media_file(path))


def _normalize_relative_path(relative_path: str) -> str:
    return relative_path.replace("\\", "/").lower()


def _is_catalog_file(relative_path: str) -> bool:
    return _normalize_relative_path(relative_path).startswith("catalogs/")


def _filter_raw_media_candidates(
    relative_path: str,
    raw_candidates: list[tuple[str, str]],
) -> list[tuple[str, str]]:
    if _is_catalog_file(relative_path):
        return []

    filtered: list[tuple[str, str]] = []
    for reference, source_hint in raw_candidates:
        cleaned = reference.strip()

        if source_hint == "extension_scan":
            if not (
                cleaned.startswith("/assets/")
                or cleaned.startswith("assets/")
                or cleaned.startswith("./assets/")
                or cleaned.startswith("../assets/")
            ):
                continue

        filtered.append((cleaned, source_hint))

    return filtered


def _is_actionable_source_file(relative_path: str) -> bool:
    normalized = _normalize_relative_path(relative_path)
    if _is_catalog_file(relative_path):
        return False
    return Path(normalized).suffix.lower() in ACTIONABLE_SOURCE_SUFFIXES


SOURCE_HINT_PRIORITY = {
    "html_attr:src": 1,
    "html_attr:href": 1,
    "html_attr:poster": 1,
    "html_attr:data-src": 1,
    "html_attr:data-href": 1,
    "css_url": 2,
    "css_import": 2,
    "quoted_path": 3,
    "extension_scan": 4,
}


def _build_candidate_record(
    *,
    source_file: str,
    reference: str,
    candidate_type: str,
    extension: str,
    location_kind: str,
    under_assets: bool,
    source_hint: str,
) -> dict[str, object]:
    return {
        "source_file": source_file,
        "reference": reference,
        "candidate_type": candidate_type,
        "extension": extension,
        "location_kind": location_kind,
        "under_assets": under_assets,
        "source_hint": source_hint,
    }


def collect_potential_urls_to_remove(workspace: Path) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()

    for file_path in _iter_media_scan_files(workspace):
        relative_path = str(file_path.relative_to(workspace))
        text = file_path.read_text(encoding="utf-8", errors="ignore")

        candidate_urls = set(EXTERNAL_URL_RE.findall(text))
        candidate_urls.update(
            value for value in (match.group("value") for match in CSS_URL_RE.finditer(text)) if _is_external_reference(value)
        )
        candidate_urls.update(
            value for value in (match.group("value") for match in HTML_ATTR_RE.finditer(text)) if _is_external_reference(value)
        )
        candidate_urls.update(
            value for value in (match.group("value") for match in IMPORT_FONT_URL_RE.finditer(text)) if _is_external_reference(value)
        )

        for url in sorted(candidate_urls):
            normalized_url = url.rstrip("/")
            key = (relative_path, normalized_url)
            if key in seen:
                continue
            seen.add(key)

            if _is_hardblocked_url(normalized_url):
                findings.append(
                    {
                        "source_file": relative_path,
                        "url": normalized_url,
                        "reason": "hard_blacklist_rezona_resona",
                    }
                )
                continue

            if _is_allowed_external_url(normalized_url):
                continue

            findings.append(
                {
                    "source_file": relative_path,
                    "url": normalized_url,
                    "reason": "not_in_allowlist",
                }
            )

    return findings


def collect_media_replacement_candidates(workspace: Path) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    seen: set[tuple[str, str, str]] = set()

    for file_path in _iter_scan_files(workspace):
        relative_path = str(file_path.relative_to(workspace))
        text = file_path.read_text(encoding="utf-8", errors="ignore")

        raw_candidates: list[tuple[str, str]] = []

        for match in HTML_ATTR_RE.finditer(text):
            raw_candidates.append((match.group("value").strip(), f"html_attr:{match.group('attr').lower()}"))

        for match in CSS_URL_RE.finditer(text):
            raw_candidates.append((match.group("value").strip(), "css_url"))

        for match in QUOTED_PATH_RE.finditer(text):
            raw_candidates.append((match.group("value").strip(), "quoted_path"))

        for match in ASSET_EXTENSION_HIT_RE.finditer(text):
            candidate = match.group(0).strip()
            if candidate and candidate[0] in {'"', "'", "(", "=", ":", ",", ";", "["}:
                candidate = candidate[1:].strip()
            raw_candidates.append((candidate, "extension_scan"))

        raw_candidates = _filter_raw_media_candidates(relative_path, raw_candidates)

        for reference, source_hint in raw_candidates:
            candidate_type = _guess_media_kind(reference)
            if not candidate_type:
                continue

            if _is_allowed_media_replacement_ref(reference, candidate_type):
                continue

            location_kind = _candidate_location_kind(reference)
            under_assets = _is_under_assets(reference)

            if location_kind == "local_relative" and not under_assets:
                continue

            extension = _guess_extension(reference)
            key = (relative_path, reference)
            existing_key = next((item for item in seen if item[0] == relative_path and item[1] == reference), None)
            if existing_key is not None:
                existing_priority = SOURCE_HINT_PRIORITY.get(existing_key[2], 999)
                incoming_priority = SOURCE_HINT_PRIORITY.get(source_hint, 999)
                if incoming_priority >= existing_priority:
                    continue
                seen.remove(existing_key)
            seen.add((relative_path, reference, source_hint))

            findings.append(
                _build_candidate_record(
                    source_file=relative_path,
                    reference=reference,
                    candidate_type=candidate_type,
                    extension=extension,
                    location_kind=location_kind,
                    under_assets=under_assets,
                    source_hint=source_hint,
                )
            )

    return findings


def collect_font_replacement_candidates(workspace: Path) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    seen: set[tuple[str, str, str]] = set()

    for file_path in _iter_scan_files(workspace):
        relative_path = str(file_path.relative_to(workspace))
        if _is_catalog_file(relative_path):
            continue
        text = file_path.read_text(encoding="utf-8", errors="ignore")

        for match in FONT_FAMILY_RE.finditer(text):
            raw_value = match.group(1).strip()
            if not raw_value:
                continue
            key = (relative_path, raw_value)
            existing_key = next((item for item in seen if item[0] == relative_path and item[1] == raw_value), None)
            if existing_key is not None:
                continue
            seen.add((relative_path, raw_value, "font_family"))
            findings.append(
                {
                    "source_file": relative_path,
                    "font_family": raw_value,
                    "candidate_type": "font_family",
                    "source_hint": "css_font_family",
                }
            )

        for match in HTML_ATTR_RE.finditer(text):
            reference = match.group("value").strip()
            font_kind = _guess_font_kind(reference)
            if not font_kind:
                continue
            if not (_is_external_reference(reference) or _looks_like_local_asset_reference(reference)):
                continue
            if _is_allowed_font_ref(reference):
                continue
            source_hint = f"html_attr:{match.group('attr').lower()}"
            existing_key = next((item for item in seen if item[0] == relative_path and item[1] == reference), None)
            if existing_key is not None:
                existing_priority = SOURCE_HINT_PRIORITY.get(existing_key[2], 999)
                incoming_priority = SOURCE_HINT_PRIORITY.get(source_hint, 999)
                if incoming_priority >= existing_priority:
                    continue
                seen.remove(existing_key)
            seen.add((relative_path, reference, source_hint))
            findings.append(
                _build_candidate_record(
                    source_file=relative_path,
                    reference=reference,
                    candidate_type=font_kind,
                    extension=_guess_extension(reference),
                    location_kind=_candidate_location_kind(reference),
                    under_assets=_is_under_assets(reference),
                    source_hint=source_hint,
                )
            )

        for match in CSS_URL_RE.finditer(text):
            reference = match.group("value").strip()
            font_kind = _guess_font_kind(reference)
            if not font_kind:
                continue
            if not (_is_external_reference(reference) or _looks_like_local_asset_reference(reference)):
                continue
            if _is_allowed_font_ref(reference):
                continue
            existing_key = next((item for item in seen if item[0] == relative_path and item[1] == reference), None)
            if existing_key is not None:
                existing_priority = SOURCE_HINT_PRIORITY.get(existing_key[2], 999)
                incoming_priority = SOURCE_HINT_PRIORITY.get("css_url", 999)
                if incoming_priority >= existing_priority:
                    continue
                seen.remove(existing_key)
            seen.add((relative_path, reference, "css_url"))
            findings.append(
                _build_candidate_record(
                    source_file=relative_path,
                    reference=reference,
                    candidate_type=font_kind,
                    extension=_guess_extension(reference),
                    location_kind=_candidate_location_kind(reference),
                    under_assets=_is_under_assets(reference),
                    source_hint="css_url",
                )
            )

        for match in IMPORT_FONT_URL_RE.finditer(text):
            reference = match.group("value").strip()
            if _is_allowed_font_ref(reference):
                continue
            existing_key = next((item for item in seen if item[0] == relative_path and item[1] == reference), None)
            if existing_key is not None:
                existing_priority = SOURCE_HINT_PRIORITY.get(existing_key[2], 999)
                incoming_priority = SOURCE_HINT_PRIORITY.get("css_import", 999)
                if incoming_priority >= existing_priority:
                    continue
                seen.remove(existing_key)
            seen.add((relative_path, reference, "css_import"))
            findings.append(
                _build_candidate_record(
                    source_file=relative_path,
                    reference=reference,
                    candidate_type="font_stylesheet",
                    extension=_guess_extension(reference),
                    location_kind=_candidate_location_kind(reference),
                    under_assets=_is_under_assets(reference),
                    source_hint="css_import",
                )
            )

    return findings


def collect_icon_font_candidates(workspace: Path) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    seen: set[tuple[str, str]] = set()

    for file_path in _iter_scan_files(workspace):
        relative_path = str(file_path.relative_to(workspace))
        if _is_catalog_file(relative_path):
            continue
        text = file_path.read_text(encoding="utf-8", errors="ignore")

        for match in MATERIAL_SYMBOLS_RE.finditer(text):
            token = match.group(0)
            key = (relative_path, token)
            if key in seen:
                continue
            seen.add(key)
            findings.append(
                {
                    "source_file": relative_path,
                    "token": token,
                    "candidate_type": "icon_font_class",
                    "source_hint": "material_symbols_token",
                }
            )

    return findings


def _filter_actionable_candidates(candidates: list[dict[str, object]]) -> list[dict[str, object]]:
    actionable: list[dict[str, object]] = []
    for candidate in candidates:
        source_file = candidate.get("source_file")
        if not isinstance(source_file, str):
            continue
        if _is_actionable_source_file(source_file):
            actionable.append(candidate)
    return actionable


def _stringify_media_candidates(candidates: list[dict[str, object]]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for candidate in candidates:
        reference = candidate.get("reference")
        if not isinstance(reference, str):
            continue
        if reference in seen:
            continue
        seen.add(reference)
        ordered.append(reference)
    return ordered


def _stringify_font_candidates(candidates: list[dict[str, object]]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for candidate in candidates:
        value = candidate.get("reference") or candidate.get("font_family")
        if not isinstance(value, str):
            continue
        if value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered


NORMALIZED_MEDIA_PLACEHOLDER_BASENAMES = {
    "audio": "infer-audio",
    "image": "infer-image",
    "gif": "infer-gif",
    "video": "infer-video",
}


def _build_normalized_media_replacement_plan(candidates: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for candidate in candidates:
        reference = candidate.get("reference")
        candidate_type = candidate.get("candidate_type")
        extension = candidate.get("extension")
        source_file = candidate.get("source_file")
        if not isinstance(reference, str) or not isinstance(candidate_type, str) or not isinstance(extension, str):
            continue
        if not isinstance(source_file, str):
            continue
        if candidate_type not in NORMALIZED_MEDIA_PLACEHOLDER_BASENAMES:
            continue
        grouped[candidate_type].append(candidate)

    plans: list[dict[str, object]] = []
    for candidate_type in ("audio", "image", "gif", "video"):
        items = grouped.get(candidate_type, [])
        items.sort(
            key=lambda item: (
                str(item.get("reference", "")),
                str(item.get("source_file", "")),
                str(item.get("source_hint", "")),
            )
        )
        basename = NORMALIZED_MEDIA_PLACEHOLDER_BASENAMES[candidate_type]
        for index, candidate in enumerate(items, start=1):
            extension = str(candidate.get("extension") or "")
            normalized_filename = f"{basename}-{index:02d}{extension}"
            normalized_relative_path = f"assets/inferred/{normalized_filename}"
            plans.append(
                {
                    "source_file": candidate["source_file"],
                    "original_reference": candidate["reference"],
                    "candidate_type": candidate_type,
                    "extension": extension,
                    "normalized_placeholder_filename": normalized_filename,
                    "normalized_placeholder_path": normalized_relative_path,
                    "source_hint": candidate.get("source_hint"),
                }
            )
    return plans


def _stringify_normalized_media_plan(plans: list[dict[str, object]]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for plan in plans:
        original_reference = plan.get("original_reference")
        normalized_placeholder_path = plan.get("normalized_placeholder_path")
        if not isinstance(original_reference, str) or not isinstance(normalized_placeholder_path, str):
            continue
        value = f"{original_reference} -> {normalized_placeholder_path}"
        if value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered


def _build_media_cleanup_plan(
    actionable_candidates: list[dict[str, object]],
    normalized_plan: list[dict[str, object]],
) -> list[dict[str, object]]:
    normalized_by_original: dict[str, dict[str, object]] = {}
    for plan in normalized_plan:
        original_reference = plan.get("original_reference")
        if isinstance(original_reference, str) and original_reference not in normalized_by_original:
            normalized_by_original[original_reference] = plan

    cleanup_plan: list[dict[str, object]] = []
    seen: set[tuple[str, str]] = set()
    for candidate in actionable_candidates:
        source_file = candidate.get("source_file")
        original_reference = candidate.get("reference")
        if not isinstance(source_file, str) or not isinstance(original_reference, str):
            continue
        normalized = normalized_by_original.get(original_reference)
        if not normalized:
            continue
        key = (source_file, original_reference)
        if key in seen:
            continue
        seen.add(key)
        cleanup_plan.append(
            {
                "source_file": source_file,
                "obsolete_reference": original_reference,
                "required_normalized_placeholder_path": normalized.get("normalized_placeholder_path"),
                "candidate_type": candidate.get("candidate_type"),
                "cleanup_rule": "remove_obsolete_reference_after_verified_replacement",
            }
        )
    return cleanup_plan


APPROVED_ICON_VOCABULARY = [
    "home", "menu", "close", "search", "settings", "account_circle", "person", "group",
    "favorite", "favorite_border", "star", "star_border", "check", "check_circle", "cancel",
    "add", "remove", "edit", "delete", "arrow_back", "arrow_forward", "arrow_upward", "arrow_downward",
    "expand_more", "expand_less", "chevron_left", "chevron_right", "refresh", "sync", "download",
    "upload", "cloud", "cloud_download", "cloud_upload", "notifications", "notifications_none",
    "email", "mail", "chat", "chat_bubble", "phone", "call", "videocam", "camera_alt", "image",
    "photo", "play_arrow", "pause", "stop", "skip_next", "skip_previous", "volume_up", "volume_off",
    "mic", "mic_off", "lock", "lock_open", "visibility", "visibility_off", "shopping_cart", "payment",
    "attach_money", "credit_card", "store", "location_on", "map", "gps_fixed", "directions",
    "calendar_today", "event", "schedule", "access_time", "alarm", "help", "info", "warning",
    "error", "build", "code", "terminal", "bug_report", "api", "language", "public", "link",
    "attach_file", "folder", "folder_open", "description", "article", "dashboard", "analytics",
    "bar_chart", "pie_chart", "trending_up", "trending_down", "wifi", "bluetooth", "battery_full",
    "battery_charging_full", "power",
]


def build_media_policy_report(workspace: Path) -> dict[str, object]:
    potential_urls = collect_potential_urls_to_remove(workspace)
    media_candidates = collect_media_replacement_candidates(workspace)
    font_candidates = collect_font_replacement_candidates(workspace)
    icon_candidates = collect_icon_font_candidates(workspace)
    actionable_media_candidates = _filter_actionable_candidates(media_candidates)
    actionable_font_candidates = _filter_actionable_candidates(font_candidates)
    actionable_icon_candidates = _filter_actionable_candidates(icon_candidates)
    normalized_media_replacement_plan = _build_normalized_media_replacement_plan(actionable_media_candidates)
    normalized_media_replacement_refs = _stringify_normalized_media_plan(normalized_media_replacement_plan)
    media_cleanup_plan = _build_media_cleanup_plan(actionable_media_candidates, normalized_media_replacement_plan)
    actionable_media_candidate_refs = _stringify_media_candidates(actionable_media_candidates)
    actionable_font_candidate_refs = _stringify_font_candidates(actionable_font_candidates)
    return {
        "workspace_path": str(workspace),
        "allowed_exact_hosts": sorted(ALLOWED_EXACT_HOSTS),
        "allowed_host_substrings": sorted(ALLOWED_HOST_SUBSTRINGS),
        "hardblock_host_substrings": list(HARDBLOCK_HOST_SUBSTRINGS),
        "metadata_excluded_filenames": sorted(METADATA_EXCLUDED_FILENAMES),
        "potential_urls_to_remove": potential_urls,
        "media_replacement_candidates": media_candidates,
        "font_replacement_candidates": font_candidates,
        "icon_font_candidates": icon_candidates,
        "actionable_media_replacement_candidates": actionable_media_candidates,
        "actionable_font_replacement_candidates": actionable_font_candidates,
        "actionable_icon_font_candidates": actionable_icon_candidates,
        "actionable_media_replacement_candidate_refs": actionable_media_candidate_refs,
        "actionable_font_replacement_candidate_refs": actionable_font_candidate_refs,
        "normalized_media_replacement_plan": normalized_media_replacement_plan,
        "normalized_media_replacement_refs": normalized_media_replacement_refs,
        "media_cleanup_plan": media_cleanup_plan,
        "approved_icon_vocabulary": APPROVED_ICON_VOCABULARY,
        "actionable_media_replacement_candidate_count": len(actionable_media_candidate_refs),
        "actionable_font_replacement_candidate_count": len(actionable_font_candidate_refs),
        "actionable_icon_font_candidate_count": len(actionable_icon_candidates),
    }


def write_media_policy_report(workspace: Path, output_path: Path) -> dict[str, object]:
    report = build_media_policy_report(workspace)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspect media/font replacement candidates in a workspace.")
    parser.add_argument("workspace", help="Workspace directory to inspect.")
    parser.add_argument("--output", help="Optional path to write the full JSON report.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    workspace = Path(args.workspace).resolve()
    report = build_media_policy_report(workspace)
    if args.output:
        output_path = Path(args.output).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()