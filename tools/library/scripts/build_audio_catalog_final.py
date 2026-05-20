#!/usr/bin/env python3
"""Build a disk-reconciled final audio catalog in catalog.json-compatible shape."""

from __future__ import annotations

import argparse
import copy
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
DEFAULT_OUTPUT_PATH = LIBRARY_ROOT / "catalog_final.json"
DEFAULT_REMOTE_BASE_URL = "https://gamezone-virid.vercel.app/assets/audios/"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a disk-reconciled final audio catalog.")
    parser.add_argument("--catalog", default=str(CATALOG_PATH))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH))
    parser.add_argument("--audio-root", default=str(LIBRARY_ROOT))
    parser.add_argument("--remote-base-url", default=DEFAULT_REMOTE_BASE_URL)
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


def missing_variant_numbers(existing_numbers: list[int], desired_total_variants: int) -> list[int]:
    existing_set = set(existing_numbers)
    return [number for number in range(1, desired_total_variants + 1) if number not in existing_set]


def resolve_audio_type(record: dict[str, Any]) -> str:
    return record.get("audio_type") or ("one_shot" if record.get("category") == "sfx" else "loop")


def semantic_item_type(record: dict[str, Any]) -> str:
    return "sfx" if record.get("category") == "sfx" else "bgm"


def url_join(base_url: str, location: str) -> str:
    normalized_location = location.lstrip("/")
    normalized_base = base_url.rstrip("/")
    assets_prefix = "/assets/audios"
    if normalized_location.startswith("assets/audios/") and normalized_base.endswith(assets_prefix):
        normalized_base = normalized_base[: -len(assets_prefix)]
    return normalized_base.rstrip("/") + "/" + normalized_location


def build_semantic_target(record: dict[str, Any]) -> tuple[str, str]:
    reference_items = record.get("reference_items") or []
    for item in reference_items:
        if not isinstance(item, dict):
            continue
        url = item.get("url")
        if not isinstance(url, str) or not url:
            continue
        relative_path = urlparse(url).path.lstrip("/")
        filename = Path(relative_path).name
        match = re.match(r"^(?P<prefix>.+)_(?P<number>\d+)\.mp3$", filename)
        if match:
            return str(Path(relative_path).parent), match.group("prefix")

    world = record.get("world", "unknown")
    intent = record.get("intent", "generic")
    return f"assets/audios/{semantic_item_type(record)}", f"{world}_{intent}"


def scan_variant_entries(
    *,
    audio_root: Path,
    destination_dir: str,
    filename_prefix: str,
    usage: str,
    audio_type: str,
    remote_base_url: str,
) -> list[dict[str, Any]]:
    local_dir = local_path_from_location(audio_root, destination_dir)
    if not local_dir.exists():
        return []

    found: list[tuple[int, dict[str, Any]]] = []
    for path in sorted(local_dir.glob(f"{filename_prefix}_*.mp3")):
        number = parse_variant_number(path.name, filename_prefix)
        if number is None:
            continue
        relative_location = f"{destination_dir.rstrip('/')}/{path.name}"
        found.append(
            (
                number,
                {
                    "name": path.stem,
                    "url": url_join(remote_base_url, relative_location),
                    "location": relative_location,
                    "usage": usage,
                    "audio_type": audio_type,
                },
            )
        )
    return [entry for _, entry in sorted(found, key=lambda item: item[0])]


def status_fields(
    *,
    destination_dir: str,
    filename_prefix: str,
    existing_names: list[str],
    existing_numbers: list[int],
    desired_total_variants: int,
    variants_per_request: int,
) -> dict[str, Any]:
    next_numbers = missing_variant_numbers(existing_numbers, desired_total_variants)
    missing_variants = len(next_numbers)
    requests_needed = (missing_variants + variants_per_request - 1) // variants_per_request if missing_variants else 0
    return {
        "destination_dir": destination_dir,
        "filename_prefix": filename_prefix,
        "destination_pattern": f"{destination_dir}/{filename_prefix}_{{nn:02d}}.mp3",
        "existing_count": len(existing_numbers),
        "existing_variants": existing_names,
        "desired_total_variants": desired_total_variants,
        "missing_variants": missing_variants,
        "variants_per_request": variants_per_request,
        "requests_needed": requests_needed,
        "next_variant_numbers": next_numbers,
        "next_destinations": [f"{destination_dir}/{filename_prefix}_{number:02d}.mp3" for number in next_numbers],
        "status": "complete" if missing_variants == 0 else "pending",
        "status_source": "disk_reconciled",
    }


def materialize_asset_family_record(
    record: dict[str, Any],
    *,
    audio_root: Path,
    remote_base_url: str,
    desired_total_variants: int,
    variants_per_request: int,
) -> tuple[dict[str, Any], int]:
    materialized = copy.deepcopy(record)
    target = materialized["target"]
    destination_dir = target["directory"]
    filename_prefix = target["filename_prefix"]
    audio_type = resolve_audio_type(materialized)
    variants = scan_variant_entries(
        audio_root=audio_root,
        destination_dir=destination_dir,
        filename_prefix=filename_prefix,
        usage=materialized.get("usage", ""),
        audio_type=audio_type,
        remote_base_url=remote_base_url,
    )
    materialized["variants"] = variants
    existing_names = [variant["name"] for variant in variants]
    existing_numbers = [number for number in (parse_variant_number(name, filename_prefix) for name in existing_names) if number is not None]
    materialized["materialized"] = status_fields(
        destination_dir=destination_dir,
        filename_prefix=filename_prefix,
        existing_names=existing_names,
        existing_numbers=existing_numbers,
        desired_total_variants=desired_total_variants,
        variants_per_request=variants_per_request,
    )
    return materialized, len(variants)


def materialize_semantic_record(
    record: dict[str, Any],
    *,
    audio_root: Path,
    remote_base_url: str,
    desired_total_variants: int,
    variants_per_request: int,
) -> tuple[dict[str, Any], int]:
    materialized = copy.deepcopy(record)
    destination_dir, filename_prefix = build_semantic_target(materialized)
    audio_type = resolve_audio_type(materialized)
    variants = scan_variant_entries(
        audio_root=audio_root,
        destination_dir=destination_dir,
        filename_prefix=filename_prefix,
        usage=materialized.get("usage", ""),
        audio_type=audio_type,
        remote_base_url=remote_base_url,
    )
    materialized["reference_items"] = [
        {
            "type": semantic_item_type(materialized),
            "url": variant["url"],
        }
        for variant in variants
    ]
    existing_names = [variant["name"] for variant in variants]
    existing_numbers = [number for number in (parse_variant_number(name, filename_prefix) for name in existing_names) if number is not None]
    materialized["materialized"] = status_fields(
        destination_dir=destination_dir,
        filename_prefix=filename_prefix,
        existing_names=existing_names,
        existing_numbers=existing_numbers,
        desired_total_variants=desired_total_variants,
        variants_per_request=variants_per_request,
    )
    return materialized, len(variants)


def build_catalog_final_payload(
    catalog: dict[str, Any],
    *,
    catalog_path: Path,
    audio_root: Path,
    remote_base_url: str,
    desired_total_variants: int,
    variants_per_request: int,
) -> dict[str, Any]:
    materialized_records: list[dict[str, Any]] = []
    asset_family_count = 0
    semantic_query_count = 0
    complete_record_count = 0
    asset_variant_total = 0
    semantic_reference_total = 0

    for record in catalog.get("records", []):
        if record.get("record_type") == "semantic_query":
            materialized_record, reference_count = materialize_semantic_record(
                record,
                audio_root=audio_root,
                remote_base_url=remote_base_url,
                desired_total_variants=desired_total_variants,
                variants_per_request=variants_per_request,
            )
            semantic_query_count += 1
            semantic_reference_total += reference_count
        else:
            materialized_record, variant_count = materialize_asset_family_record(
                record,
                audio_root=audio_root,
                remote_base_url=remote_base_url,
                desired_total_variants=desired_total_variants,
                variants_per_request=variants_per_request,
            )
            asset_family_count += 1
            asset_variant_total += variant_count

        if materialized_record["materialized"]["status"] == "complete":
            complete_record_count += 1
        materialized_records.append(materialized_record)

    payload = copy.deepcopy(catalog)
    payload["generated_at"] = utc_now()
    payload["summary"] = {
        "asset_family_count": asset_family_count,
        "semantic_query_count": semantic_query_count,
        "record_count": len(materialized_records),
        "complete_record_count": complete_record_count,
        "pending_record_count": len(materialized_records) - complete_record_count,
        "materialized_asset_variant_count": asset_variant_total,
        "materialized_semantic_reference_count": semantic_reference_total,
        "desired_total_variants": desired_total_variants,
        "variants_per_request": variants_per_request,
    }
    payload["materialization"] = {
        "planner_catalog": str(catalog_path.relative_to(ROOT)),
        "audio_root": str(audio_root.relative_to(ROOT)),
        "status_source": "disk_reconciled",
    }
    payload["records"] = materialized_records
    return payload


def main() -> int:
    args = parse_args()
    catalog_path = Path(args.catalog)
    output_path = Path(args.output)
    audio_root = Path(args.audio_root)

    catalog = load_json(catalog_path)
    payload = build_catalog_final_payload(
        catalog,
        catalog_path=catalog_path,
        audio_root=audio_root,
        remote_base_url=args.remote_base_url,
        desired_total_variants=args.desired_total_variants,
        variants_per_request=args.variants_per_request,
    )
    write_json(output_path, payload)

    print(json.dumps(payload["summary"], ensure_ascii=False, indent=2))
    print(f"wrote {output_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())