from __future__ import annotations

import hashlib
import json
import re
import shutil
from pathlib import Path
from typing import Any, Collection, Mapping, Sequence
from urllib.parse import urlparse

TAG_FAMILIES = [
    "mechanic_tags",
    "semantic_tags",
    "mood_tags",
    "setting_tags",
    "character_tags",
    "games_tags",
    "franchise_tags",
]

DEFAULT_IDENTICAL_EXTENSIONS = {".html", ".js", ".css"}
DEFAULT_VENDOR_ASSET_DOMAINS = {
    "fonts.googleapis.com",
    "cdn.tailwindcss.com",
    "unpkg.com",
    "cdnjs.cloudflare.com",
}
DEFAULT_SANITIZE_SUFFIXES = {".html", ".js", ".mjs", ".cjs", ".css", ".json"}
ROOT_ARTIFACT_NAMES = {"app.json", "app_tags.json", "index.json"}
MAX_TEXT_BYTES = 2_000_000
MP3_REF_RE = re.compile(r"[^\"'\s<>()]+\.mp3(?:\?[^\"'\s<>()]*)?")
METADATA_JSON_RE = re.compile(r"^game-obfuscated-.*\.json$")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def normalize_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def normalize_text(value: Any) -> str:
    return " ".join(str(value or "").strip().lower().split())


def sample(items: Sequence[str], limit: int) -> list[str]:
    return list(items[: max(limit, 0)])


def _relative_str(path: Path | None, root: Path) -> str | None:
    if path is None:
        return None
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def _sorted_unique(items: Collection[str]) -> list[str]:
    return sorted({item for item in items if item})


def is_generic_title(record: Mapping[str, Any], composite_key: str) -> bool:
    title = str(record.get("title") or "").strip()
    if not title:
        return True

    normalized_title = normalize_text(title)
    game_id = str(record.get("game_id") or "").strip()
    remix_id = str(record.get("remix_id") or "").strip()
    published_path = str(record.get("published_path") or "").strip()

    if title.startswith("gamezone-"):
        return True

    raw_candidates = {
        normalize_text(game_id),
        normalize_text(composite_key),
        normalize_text(f"{game_id}__{remix_id}" if game_id and remix_id else ""),
        normalize_text(published_path),
        normalize_text(Path(published_path).name if published_path else ""),
    }
    raw_candidates.discard("")
    return normalized_title in raw_candidates


def tag_family_lengths(record: Mapping[str, Any]) -> dict[str, int]:
    return {family: len(normalize_string_list(record.get(family))) for family in TAG_FAMILIES}


def has_no_tags(record: Mapping[str, Any]) -> bool:
    return all(length == 0 for length in tag_family_lengths(record).values())


def summarize_catalog(path: Path, sample_limit: int) -> dict[str, Any]:
    payload = load_json(path)
    if not isinstance(payload, dict):
        raise ValueError(f"Catalog at {path} must be a JSON object")

    zero_screenshot_keys: list[str] = []
    generic_title_keys: list[str] = []
    no_tag_keys: list[str] = []
    candidate_keys: list[str] = []
    invalid_record_keys: list[str] = []

    for key, record in payload.items():
        if not isinstance(record, dict):
            invalid_record_keys.append(str(key))
            continue

        screenshots = normalize_string_list(record.get("screenshots"))
        generic_title = is_generic_title(record, str(key))
        no_tags = has_no_tags(record)

        if not screenshots:
            zero_screenshot_keys.append(str(key))
        if generic_title:
            generic_title_keys.append(str(key))
        if no_tags:
            no_tag_keys.append(str(key))
        if (not screenshots) or generic_title or no_tags:
            candidate_keys.append(str(key))

    zero_screenshot_keys.sort()
    generic_title_keys.sort()
    no_tag_keys.sort()
    candidate_keys = sorted(set(candidate_keys))
    invalid_record_keys.sort()

    return {
        "catalog_path": str(path),
        "total_entries": len(payload),
        "invalid_record_count": len(invalid_record_keys),
        "invalid_record_sample": sample(invalid_record_keys, sample_limit),
        "zero_screenshots_count": len(zero_screenshot_keys),
        "zero_screenshots_sample": sample(zero_screenshot_keys, sample_limit),
        "zero_screenshots_keys": zero_screenshot_keys,
        "generic_titles_count": len(generic_title_keys),
        "generic_titles_sample": sample(generic_title_keys, sample_limit),
        "generic_titles_keys": generic_title_keys,
        "no_tags_count": len(no_tag_keys),
        "no_tags_sample": sample(no_tag_keys, sample_limit),
        "no_tags_keys": no_tag_keys,
        "candidate_for_removal_count": len(candidate_keys),
        "candidate_for_removal_sample": sample(candidate_keys, sample_limit),
        "candidate_for_removal_keys": candidate_keys,
    }


def compare_key_sets(public: Mapping[str, Any], obfuscated: Mapping[str, Any], field: str) -> dict[str, Any]:
    public_keys = set(public[field])
    obfuscated_keys = set(obfuscated[field])
    public_only = sorted(public_keys - obfuscated_keys)
    obfuscated_only = sorted(obfuscated_keys - public_keys)
    return {
        "public_only_count": len(public_only),
        "public_only_sample": public_only[:10],
        "obfuscated_only_count": len(obfuscated_only),
        "obfuscated_only_sample": obfuscated_only[:10],
    }


def build_regression_audit(
    public_app_path: Path,
    obfuscated_app_path: Path,
    *,
    sample_limit: int = 20,
    label: str = "baseline",
) -> dict[str, Any]:
    public_summary = summarize_catalog(public_app_path, sample_limit)
    obfuscated_summary = summarize_catalog(obfuscated_app_path, sample_limit)
    return {
        "label": label,
        "tag_families": list(TAG_FAMILIES),
        "public": public_summary,
        "obfuscated": obfuscated_summary,
        "cross_catalog_diffs": {
            "zero_screenshots": compare_key_sets(public_summary, obfuscated_summary, "zero_screenshots_keys"),
            "generic_titles": compare_key_sets(public_summary, obfuscated_summary, "generic_titles_keys"),
            "no_tags": compare_key_sets(public_summary, obfuscated_summary, "no_tags_keys"),
            "candidate_for_removal": compare_key_sets(public_summary, obfuscated_summary, "candidate_for_removal_keys"),
        },
        "summary": {
            "public_total_entries": public_summary["total_entries"],
            "obfuscated_total_entries": obfuscated_summary["total_entries"],
            "public_candidate_for_removal_count": public_summary["candidate_for_removal_count"],
            "obfuscated_candidate_for_removal_count": obfuscated_summary["candidate_for_removal_count"],
        },
    }


def build_candidate_key_set(audit_report: Mapping[str, Any]) -> list[str]:
    public_keys = set(((audit_report.get("public") or {}).get("candidate_for_removal_keys") or []))
    obfuscated_keys = set(((audit_report.get("obfuscated") or {}).get("candidate_for_removal_keys") or []))
    return sorted(public_keys | obfuscated_keys)


def build_candidate_reason_index(audit_report: Mapping[str, Any]) -> dict[str, list[str]]:
    reasons: dict[str, set[str]] = {}
    for scope in ("public", "obfuscated"):
        summary = audit_report.get(scope) or {}
        for category, field in (
            ("zero_screenshots", "zero_screenshots_keys"),
            ("generic_titles", "generic_titles_keys"),
            ("no_tags", "no_tags_keys"),
        ):
            for key in summary.get(field) or []:
                reasons.setdefault(str(key), set()).add(category)
    return {key: sorted(values) for key, values in reasons.items()}


def load_catalog_records(path: Path) -> dict[str, dict[str, Any]]:
    payload = load_json(path)
    if not isinstance(payload, dict):
        raise ValueError(f"Catalog at {path} must be a JSON object")
    return {str(key): value for key, value in payload.items() if isinstance(key, str) and isinstance(value, dict)}


def is_appledouble(rel_path: Path) -> bool:
    return any(part.startswith("._") for part in rel_path.parts)


def is_vendor_asset(rel_path: Path, vendor_domains: Collection[str]) -> bool:
    parts = rel_path.parts
    for index, part in enumerate(parts):
        if part == "assets" and index + 1 < len(parts):
            return parts[index + 1] in vendor_domains
    return False


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def extract_affected_gamezones(identical_rel_paths: Sequence[str]) -> list[str]:
    affected: set[str] = set()
    for rel in identical_rel_paths:
        parts = Path(rel).parts
        if parts and parts[0].startswith("gamezone-"):
            affected.add(parts[0])
    return sorted(affected)


def detect_identical_public_obfuscated(
    public_root: Path,
    obfuscated_root: Path,
    *,
    extensions: Collection[str] | None = None,
    include_appledouble: bool = False,
    include_annotator: bool = False,
    include_vendor_assets: bool = False,
    vendor_asset_domains: Collection[str] | None = None,
) -> dict[str, Any]:
    if not public_root.is_dir():
        raise ValueError(f"Public root is not a directory: {public_root}")
    if not obfuscated_root.is_dir():
        raise ValueError(f"Obfuscated root is not a directory: {obfuscated_root}")

    target_extensions = {item.lower() for item in (extensions or DEFAULT_IDENTICAL_EXTENSIONS)}
    vendor_domains = set(vendor_asset_domains or DEFAULT_VENDOR_ASSET_DOMAINS)

    scanned_public_files = 0
    skipped_appledouble = 0
    skipped_annotator = 0
    skipped_vendor_assets = 0
    comparable_pairs = 0
    identical_pairs: list[str] = []
    missing_in_obfuscated: list[str] = []

    for public_path in sorted(public_root.rglob("*")):
        if not public_path.is_file() or public_path.suffix.lower() not in target_extensions:
            continue

        scanned_public_files += 1
        rel_path = public_path.relative_to(public_root)

        if not include_appledouble and is_appledouble(rel_path):
            skipped_appledouble += 1
            continue
        if not include_annotator and rel_path.name == "annotator.html":
            skipped_annotator += 1
            continue
        if not include_vendor_assets and is_vendor_asset(rel_path, vendor_domains):
            skipped_vendor_assets += 1
            continue

        obfuscated_path = obfuscated_root / rel_path
        if not obfuscated_path.is_file():
            missing_in_obfuscated.append(str(rel_path))
            continue

        comparable_pairs += 1
        if sha256_file(public_path) == sha256_file(obfuscated_path):
            identical_pairs.append(str(rel_path))

    affected_gamezones = extract_affected_gamezones(identical_pairs)
    return {
        "public_root": str(public_root),
        "obfuscated_root": str(obfuscated_root),
        "extensions": sorted(target_extensions),
        "scanned_public_files": scanned_public_files,
        "skipped_appledouble": skipped_appledouble,
        "skipped_annotator": skipped_annotator,
        "skipped_vendor_assets": skipped_vendor_assets,
        "comparable_pairs": comparable_pairs,
        "identical_pairs": len(identical_pairs),
        "identical_paths": identical_pairs,
        "missing_in_obfuscated": len(missing_in_obfuscated),
        "missing_paths": missing_in_obfuscated,
        "affected_gamezone_count": len(affected_gamezones),
        "affected_gamezone_ids": affected_gamezones,
    }


def resolve_public_publish_dir(public_root: Path, published_path: str) -> Path | None:
    if not published_path:
        return None
    candidate = public_root / published_path
    return candidate if candidate.is_dir() else None


def resolve_obfuscated_publish_dir(obfuscated_root: Path, game_id: str, published_path: str) -> Path | None:
    if published_path:
        nested = obfuscated_root / published_path
        if nested.is_dir():
            return nested
    if game_id:
        flat = obfuscated_root / game_id
        if flat.is_dir():
            return flat
    return None


def list_public_dirs_for_gamezone(public_root: Path, game_id: str) -> list[Path]:
    game_root = public_root / game_id
    if not game_root.is_dir():
        return []
    remix_dirs = [path for path in sorted(game_root.iterdir()) if path.is_dir()]
    if remix_dirs:
        return remix_dirs
    return [game_root] if (game_root / "index.html").is_file() else []


def list_obfuscated_dirs_for_gamezone(obfuscated_root: Path, game_id: str) -> list[Path]:
    game_root = obfuscated_root / game_id
    if not game_root.exists():
        return []
    if (game_root / "index.html").is_file():
        return [game_root]
    remix_dirs = [path for path in sorted(game_root.iterdir()) if path.is_dir() and (path / "index.html").is_file()]
    return remix_dirs


def build_candidate_directory_map(
    *,
    public_app_path: Path,
    obfuscated_app_path: Path,
    public_root: Path,
    obfuscated_root: Path,
    candidate_keys: Sequence[str],
    affected_gamezones: Sequence[str] | None = None,
    audit_report: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    public_records = load_catalog_records(public_app_path)
    obfuscated_records = load_catalog_records(obfuscated_app_path)
    reason_index = build_candidate_reason_index(audit_report or {})

    candidate_entries: list[dict[str, Any]] = []
    public_delete_targets: set[str] = set()
    obfuscated_delete_targets: set[str] = set()

    for composite_key in sorted(set(candidate_keys)):
        record = public_records.get(composite_key) or obfuscated_records.get(composite_key) or {}
        game_id = str(record.get("game_id") or composite_key.split("__", 1)[0] or "")
        remix_id = str(record.get("remix_id") or "")
        published_path = str(record.get("published_path") or "")
        public_dir = resolve_public_publish_dir(public_root, published_path)
        obfuscated_dir = resolve_obfuscated_publish_dir(obfuscated_root, game_id, published_path)

        public_rel = _relative_str(public_dir, public_root)
        obfuscated_rel = _relative_str(obfuscated_dir, obfuscated_root)
        if public_rel:
            public_delete_targets.add(public_rel)
        if obfuscated_rel:
            obfuscated_delete_targets.add(obfuscated_rel)

        candidate_entries.append(
            {
                "composite_key": composite_key,
                "reasons": reason_index.get(composite_key, []),
                "game_id": game_id,
                "remix_id": remix_id,
                "published_path": published_path,
                "public_record_present": composite_key in public_records,
                "obfuscated_record_present": composite_key in obfuscated_records,
                "public_dir": public_rel,
                "public_dir_exists": bool(public_dir),
                "obfuscated_dir": obfuscated_rel,
                "obfuscated_dir_exists": bool(obfuscated_dir),
            }
        )

    affected_entries: list[dict[str, Any]] = []
    for game_id in sorted(set(affected_gamezones or [])):
        public_dirs = list_public_dirs_for_gamezone(public_root, game_id)
        obfuscated_dirs = list_obfuscated_dirs_for_gamezone(obfuscated_root, game_id)
        public_rel_paths = [_relative_str(path, public_root) for path in public_dirs]
        obfuscated_rel_paths = [_relative_str(path, obfuscated_root) for path in obfuscated_dirs]
        public_delete_targets.update(path for path in public_rel_paths if path)
        obfuscated_delete_targets.update(path for path in obfuscated_rel_paths if path)
        affected_entries.append(
            {
                "game_id": game_id,
                "public_dirs": [path for path in public_rel_paths if path],
                "obfuscated_dirs": [path for path in obfuscated_rel_paths if path],
            }
        )

    return {
        "candidate_count": len(candidate_entries),
        "candidate_entries": candidate_entries,
        "affected_gamezone_count": len(affected_entries),
        "affected_gamezone_entries": affected_entries,
        "public_delete_targets": sorted(public_delete_targets),
        "obfuscated_delete_targets": sorted(obfuscated_delete_targets),
    }


def extract_gamezone_folder(rel_path: Path) -> str | None:
    for part in rel_path.parts:
        if part.startswith("gamezone-"):
            return part
    return None


def looks_textual(path: Path) -> bool:
    if path.suffix.lower() in DEFAULT_SANITIZE_SUFFIXES:
        return True
    try:
        sample_bytes = path.read_bytes()[:1024]
    except OSError:
        return False
    return b"\0" not in sample_bytes


def is_runtime_sanitizable_file(path: Path, root: Path, sanitize_suffixes: Collection[str]) -> bool:
    rel_path = path.relative_to(root)
    if extract_gamezone_folder(rel_path) is None:
        return False
    if is_appledouble(rel_path):
        return False
    if any(part == "artifacts" for part in rel_path.parts):
        return False
    if path.name in ROOT_ARTIFACT_NAMES:
        return False
    if path.suffix.lower() == ".json" and METADATA_JSON_RE.match(path.name):
        return False
    if path.suffix.lower() not in sanitize_suffixes:
        return False
    try:
        if path.stat().st_size > MAX_TEXT_BYTES:
            return False
    except OSError:
        return False
    return looks_textual(path)


def is_allowed_mp3_reference(reference: str) -> bool:
    raw = reference.strip("'\" ")
    parsed = urlparse(raw)
    hostname = (parsed.hostname or "").lower()
    path = parsed.path.lower()
    return parsed.scheme == "https" and hostname.endswith(".vercel.app") and path.endswith(".mp3")


def sanitize_mp3_text(text: str) -> tuple[str, list[str], list[str]]:
    allowed_refs: list[str] = []
    removed_refs: list[str] = []

    def replace_match(match: re.Match[str]) -> str:
        reference = match.group(0)
        if is_allowed_mp3_reference(reference):
            allowed_refs.append(reference)
            return reference
        removed_refs.append(reference)
        return ""

    sanitized = MP3_REF_RE.sub(replace_match, text)
    return sanitized, allowed_refs, removed_refs


def sanitize_published_media_refs(
    roots: Sequence[Path],
    *,
    apply_changes: bool = False,
    sanitize_suffixes: Collection[str] | None = None,
) -> dict[str, Any]:
    suffixes = {suffix.lower() for suffix in (sanitize_suffixes or DEFAULT_SANITIZE_SUFFIXES)}
    root_summaries: list[dict[str, Any]] = []
    changed_entries: list[dict[str, Any]] = []
    removed_reference_set: set[str] = set()
    allowed_reference_set: set[str] = set()
    scanned_files = 0
    changed_files = 0
    removed_references = 0

    for root in roots:
        changed_in_root = 0
        scanned_in_root = 0
        for path in sorted(root.rglob("*")):
            if not path.is_file() or not is_runtime_sanitizable_file(path, root, suffixes):
                continue

            scanned_files += 1
            scanned_in_root += 1
            try:
                original = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue

            if ".mp3" not in original:
                continue

            sanitized, allowed_refs, removed_refs = sanitize_mp3_text(original)
            if not removed_refs:
                allowed_reference_set.update(allowed_refs)
                continue

            rel_path = path.relative_to(root)
            if apply_changes:
                path.write_text(sanitized, encoding="utf-8")

            changed_files += 1
            changed_in_root += 1
            removed_references += len(removed_refs)
            removed_reference_set.update(removed_refs)
            allowed_reference_set.update(allowed_refs)
            changed_entries.append(
                {
                    "root": str(root),
                    "path": str(rel_path),
                    "game_id": extract_gamezone_folder(rel_path),
                    "removed_reference_count": len(removed_refs),
                    "removed_references": _sorted_unique(removed_refs),
                    "allowed_references": _sorted_unique(allowed_refs),
                    "applied": apply_changes,
                }
            )

        root_summaries.append(
            {
                "root": str(root),
                "scanned_file_count": scanned_in_root,
                "changed_file_count": changed_in_root,
            }
        )

    return {
        "applied": apply_changes,
        "roots": [str(root) for root in roots],
        "scanned_file_count": scanned_files,
        "changed_file_count": changed_files,
        "removed_reference_count": removed_references,
        "removed_reference_sample": sample(_sorted_unique(removed_reference_set), 20),
        "allowed_reference_sample": sample(_sorted_unique(allowed_reference_set), 20),
        "root_summaries": root_summaries,
        "changed_entries": changed_entries,
    }


def build_runtime_manifest_from_public_root(
    public_root: Path,
    *,
    collection_slug: str = "vatsal_app_alpha",
    batch_name: str | None = None,
    exclude_published_paths: Collection[str] | None = None,
) -> dict[str, Any]:
    excluded = {item for item in (exclude_published_paths or []) if item}
    entries: list[dict[str, Any]] = []

    for game_dir in sorted(path for path in public_root.iterdir() if path.is_dir() and path.name.startswith("gamezone-")):
        for remix_dir in sorted(path for path in game_dir.iterdir() if path.is_dir() and path.name.startswith("remix-")):
            published_path = f"{game_dir.name}/{remix_dir.name}"
            if published_path in excluded:
                continue
            entries.append(
                {
                    "game_id": game_dir.name,
                    "remix_id": remix_dir.name,
                    "composite_key": f"{game_dir.name}__{remix_dir.name}",
                    "published_path": published_path,
                }
            )

    return {
        "batch_name": batch_name or f"{collection_slug}_runtime",
        "collection_slug": collection_slug,
        "entry_count": len(entries),
        "entries": entries,
    }


def delete_published_targets(
    *,
    public_root: Path,
    obfuscated_root: Path,
    public_delete_targets: Sequence[str],
    obfuscated_delete_targets: Sequence[str],
    dry_run: bool = False,
) -> dict[str, Any]:
    deleted_targets: list[str] = []
    missing_targets: list[str] = []

    planned_targets: list[tuple[str, Path]] = []
    for rel_path in public_delete_targets:
        planned_targets.append((f"public:{rel_path}", public_root / rel_path))
    for rel_path in obfuscated_delete_targets:
        planned_targets.append((f"obfuscated:{rel_path}", obfuscated_root / rel_path))

    planned_targets.sort(key=lambda item: (-len(Path(item[0].split(':', 1)[1]).parts), item[0]))

    for marker, path in planned_targets:
        if path.exists():
            deleted_targets.append(marker)
            if not dry_run:
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()
        else:
            missing_targets.append(marker)

    return {
        "dry_run": dry_run,
        "deleted_count": len(deleted_targets),
        "deleted_targets": deleted_targets,
        "missing_count": len(missing_targets),
        "missing_targets": missing_targets,
    }