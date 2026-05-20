#!/usr/bin/env python3
"""Build a normalized flat jobs list for library audio generation."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[3]
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in __import__("sys").path:
    __import__("sys").path.insert(0, str(SCRIPT_DIR))

from audio_paths import local_path_from_location, resolve_library_root  # type: ignore  # noqa: E402

LIBRARY_ROOT = resolve_library_root()
CATALOG_PATH = LIBRARY_ROOT / "catalog.json"
DEFAULT_OUTPUT_PATH = LIBRARY_ROOT / "jobs_list.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build normalized jobs list for all concrete library audio families.")
    parser.add_argument("--catalog", default=str(CATALOG_PATH))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH))
    parser.add_argument("--desired-total-variants", type=int, default=4)
    parser.add_argument("--variants-per-request", type=int, default=2)
    return parser.parse_args()


def parse_variant_number(name: str, prefix: str) -> int | None:
    stem = Path(name).stem
    expected_prefix = f"{prefix}_"
    if not stem.startswith(expected_prefix):
        return None
    suffix = stem[len(expected_prefix) :]
    return int(suffix) if suffix.isdigit() else None


def existing_variants_from_disk(
    *,
    audio_root: Path,
    destination_dir: str,
    filename_prefix: str,
) -> tuple[list[int], list[str]]:
    local_dir = local_path_from_location(audio_root, destination_dir)
    if not local_dir.exists():
        return [], []

    found: list[tuple[int, str]] = []
    for path in sorted(local_dir.glob(f"{filename_prefix}_*.mp3")):
        number = parse_variant_number(path.name, filename_prefix)
        if number is None:
            continue
        found.append((number, path.stem))

    numbers = [number for number, _ in found]
    names = [name for _, name in found]
    return numbers, names


def missing_variant_numbers(existing_numbers: list[int], desired_total_variants: int) -> list[int]:
    existing_set = set(existing_numbers)
    return [number for number in range(1, desired_total_variants + 1) if number not in existing_set]


def semantic_reference_names(entry: dict[str, Any]) -> list[str]:
    items = entry.get("reference_items") or []
    names: list[str] = []
    for index, item in enumerate(items, 1):
        if not isinstance(item, dict):
            continue
        url = item.get("url")
        if isinstance(url, str) and url:
            names.append(Path(url).name)
        else:
            names.append(f"item_{index:02d}.mp3")
    return names


def semantic_reference_urls(entry: dict[str, Any]) -> list[str]:
    items = entry.get("reference_items") or []
    urls: list[str] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        url = item.get("url")
        if isinstance(url, str) and url:
            urls.append(url)
    return urls


def build_destination_pattern_from_reference_url(url: str) -> str | None:
    parsed = urlparse(url)
    relative_path = parsed.path.lstrip("/")
    if not relative_path:
        return None

    filename = Path(relative_path).name
    match = re.match(r"^(?P<prefix>.+)_(?P<number>\d+)\.mp3$", filename)
    if not match:
        return None

    prefix = match.group("prefix")
    parent = str(Path(relative_path).parent)
    return f"{parent}/{prefix}_{{nn:02d}}.mp3"


def build_destination_pattern_for_semantic(entry: dict[str, Any]) -> str:
    reference_urls = semantic_reference_urls(entry)
    for url in reference_urls:
        destination_pattern = build_destination_pattern_from_reference_url(url)
        if destination_pattern:
            return destination_pattern

    world = entry.get("world", "unknown")
    intent = entry.get("intent", "generic")
    category = entry.get("category", "music")
    bucket = "sfx" if category == "sfx" else "bgm"
    return f"assets/audios/{bucket}/{world}_{intent}_{{nn:02d}}.mp3"


def build_jobs_list_payload(
    catalog: dict[str, Any],
    *,
    desired_total_variants: int,
    variants_per_request: int,
    audio_root: Path | None = None,
) -> dict[str, Any]:
    if variants_per_request <= 0:
        raise ValueError("variants_per_request must be greater than zero")

    resolved_audio_root = audio_root or resolve_library_root()

    jobs: list[dict[str, Any]] = []
    asset_records = [record for record in catalog["records"] if record.get("record_type") == "asset_family"]
    semantic_records = [record for record in catalog["records"] if record.get("record_type") == "semantic_query"]
    for record in asset_records:
        destination_dir = record["target"]["directory"]
        filename_prefix = record["target"]["filename_prefix"]
        existing_numbers, existing_variant_names = existing_variants_from_disk(
            audio_root=resolved_audio_root,
            destination_dir=destination_dir,
            filename_prefix=filename_prefix,
        )
        existing_count = len(existing_numbers)
        next_numbers = missing_variant_numbers(existing_numbers, desired_total_variants)
        missing_variants = len(next_numbers)
        requests_needed = (missing_variants + variants_per_request - 1) // variants_per_request

        jobs.append(
            {
                "record_type": "asset_family",
                "id": record["id"],
                "group": record["group"],
                "category": record["category"],
                "audio_type": record.get("audio_type") or ("one_shot" if record["category"] == "sfx" else "loop"),
                "generation_route": record["generation_route"],
                "prompt": record["prompt_template"],
                "usage": record.get("usage", ""),
                "destination_dir": destination_dir,
                "filename_prefix": filename_prefix,
                "destination_pattern": f"{destination_dir}/{filename_prefix}_{{nn:02d}}.mp3",
                "existing_count": existing_count,
                "existing_variants": existing_variant_names,
                "desired_total_variants": desired_total_variants,
                "missing_variants": missing_variants,
                "variants_per_request": variants_per_request,
                "requests_needed": requests_needed,
                "next_variant_numbers": next_numbers,
                "next_destinations": [f"{destination_dir}/{filename_prefix}_{number:02d}.mp3" for number in next_numbers],
                "status": "complete" if missing_variants == 0 else "pending",
            }
        )

    for record in semantic_records:
        reference_urls = semantic_reference_urls(record)
        reference_names = semantic_reference_names(record)
        destination_pattern = build_destination_pattern_for_semantic(record)
        destination_dir = str(Path(destination_pattern).parent)
        filename_prefix = Path(destination_pattern).stem.replace("_{nn:02d}", "")
        existing_numbers, existing_variant_names = existing_variants_from_disk(
            audio_root=resolved_audio_root,
            destination_dir=destination_dir,
            filename_prefix=filename_prefix,
        )
        existing_count = len(existing_numbers)
        next_numbers = missing_variant_numbers(existing_numbers, desired_total_variants)
        missing_variants = len(next_numbers)
        requests_needed = (missing_variants + variants_per_request - 1) // variants_per_request

        jobs.append(
            {
                "record_type": "semantic_query",
                "id": record["id"],
                "group": record.get("semantic_role"),
                "category": record["category"],
                "audio_type": "one_shot" if record["category"] == "sfx" else "loop",
                "generation_route": record["generation_route"],
                "prompt": record["prompt_template"],
                "usage": record.get("usage", ""),
                "destination_dir": destination_dir,
                "filename_prefix": filename_prefix,
                "destination_pattern": destination_pattern,
                "existing_count": existing_count,
                "existing_variants": existing_variant_names or reference_names,
                "reference_urls": reference_urls,
                "desired_total_variants": desired_total_variants,
                "missing_variants": missing_variants,
                "variants_per_request": variants_per_request,
                "requests_needed": requests_needed,
                "next_variant_numbers": next_numbers,
                "next_destinations": [destination_pattern.replace("{nn:02d}", f"{number:02d}") for number in next_numbers],
                "status": "complete" if missing_variants == 0 else "pending",
                "query": record.get("query"),
                "world": record.get("world"),
                "intent": record.get("intent"),
                "tags": record.get("tags", []),
            }
        )

    pending_jobs = sum(1 for job in jobs if job["status"] == "pending")
    asset_family_job_count = sum(1 for job in jobs if job["record_type"] == "asset_family")
    semantic_query_job_count = sum(1 for job in jobs if job["record_type"] == "semantic_query")
    return {
        "schema_version": 1,
        "generated_at": utc_now(),
        "source_catalog": str(CATALOG_PATH.relative_to(ROOT)),
        "summary": {
            "job_count": len(jobs),
            "asset_family_job_count": asset_family_job_count,
            "semantic_query_job_count": semantic_query_job_count,
            "pending_job_count": pending_jobs,
            "complete_job_count": len(jobs) - pending_jobs,
            "desired_total_variants": desired_total_variants,
            "variants_per_request": variants_per_request,
        },
        "jobs": jobs,
    }


def main() -> int:
    args = parse_args()
    catalog_path = Path(args.catalog)
    output_path = Path(args.output)

    catalog = load_json(catalog_path)
    payload = build_jobs_list_payload(
        catalog,
        desired_total_variants=args.desired_total_variants,
        variants_per_request=args.variants_per_request,
        audio_root=catalog_path.parent,
    )
    write_json(output_path, payload)

    print(json.dumps(payload["summary"], ensure_ascii=False, indent=2))
    print(f"wrote {output_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())