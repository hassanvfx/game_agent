#!/usr/bin/env python3
"""Generate cache-aware audio variants from the merged canonical catalog."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[3]
KIE_SRC = ROOT / "tools" / "kie-api" / "src"
if str(KIE_SRC) not in sys.path:
    sys.path.insert(0, str(KIE_SRC))

from kie_cli.client import KieClient  # type: ignore  # noqa: E402
from kie_cli.config import load_config  # type: ignore  # noqa: E402
from kie_cli.jobs import build_job_record, write_job_record  # type: ignore  # noqa: E402
from kie_cli.payloads import build_suno_music_payload, build_suno_sounds_payload  # type: ignore  # noqa: E402
from kie_cli.polling import poll_until_complete  # type: ignore  # noqa: E402
from kie_cli.status import (  # type: ignore  # noqa: E402
    normalize_market_status,
    normalize_submit,
    normalize_suno_lyrics_status,
    normalize_suno_music_status,
    normalize_veo_status,
)
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from audio_paths import local_path_from_location, resolve_library_root  # type: ignore  # noqa: E402

LIBRARY_ROOT = resolve_library_root()
CATALOG_PATH = LIBRARY_ROOT / "catalog.json"
LIBRARY_AUDIOS_PATH = LIBRARY_ROOT / "audios.json"
DEFAULT_JOBS_ROOT = LIBRARY_ROOT / "jobs"
DEFAULT_DOWNLOAD_ROOT = LIBRARY_ROOT / "incoming" / "generated"
DEFAULT_REMOTE_BASE_URL = "https://gamezone-virid.vercel.app/assets/audios/"
DEFAULT_SUNO_MUSIC_MODEL = "V5"
DEFAULT_CALLBACK_URL = "https://example.com/kie-callback"
LIVE_STAGE_STREAM = False


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate audio variants into the library cache from the canonical catalog.")
    parser.add_argument("--catalog", default=str(CATALOG_PATH))
    parser.add_argument("--library-audios", default=str(LIBRARY_AUDIOS_PATH))
    parser.add_argument("--audio-root", default=str(LIBRARY_ROOT))
    parser.add_argument("--jobs-root", default=str(DEFAULT_JOBS_ROOT))
    parser.add_argument("--download-root", default=str(DEFAULT_DOWNLOAD_ROOT))
    parser.add_argument("--remote-base-url", default=DEFAULT_REMOTE_BASE_URL)
    parser.add_argument("--record-id", action="append", default=[])
    parser.add_argument("--desired-count", type=int, default=1)
    parser.add_argument("--variants-per-request", type=int, default=2)
    parser.add_argument("--poll-interval", type=float, default=5.0)
    parser.add_argument("--timeout", type=float, default=900.0)
    parser.add_argument("--overwrite-all", action="store_true")
    parser.add_argument("--sounds-model", default="V5")
    parser.add_argument("--music-model", default=DEFAULT_SUNO_MUSIC_MODEL)
    parser.add_argument("--callback-url")
    parser.add_argument("--verbose-stages", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def resolve_callback_url(explicit_value: str | None) -> str:
    return explicit_value or DEFAULT_CALLBACK_URL


def add_stage_event(
    events: list[dict[str, Any]],
    *,
    record_id: str,
    stage: str,
    status: str,
    request_label: str | None = None,
    target: str | None = None,
    detail: Any | None = None,
) -> None:
    event: dict[str, Any] = {
        "timestamp": utc_now(),
        "record_id": record_id,
        "stage": stage,
        "status": status,
    }
    if request_label:
        event["requestLabel"] = request_label
    if target:
        event["target"] = target
    if detail is not None:
        event["detail"] = detail
    events.append(event)
    if LIVE_STAGE_STREAM:
        parts = [f"[{record_id}]", f"stage={stage}", f"status={status}"]
        if request_label:
            parts.append(f"request={request_label}")
        if target:
            parts.append(f"target={target}")
        print(" ".join(parts), file=sys.stderr, flush=True)


def resolve_audio_type(record: dict[str, Any]) -> str:
    return record.get("audio_type") or ("one_shot" if record["category"] == "sfx" else "loop")


def semantic_item_type(record: dict[str, Any]) -> str:
    return "sfx" if record["category"] == "sfx" else "bgm"


def parse_variant_number(name: str, prefix: str) -> int | None:
    stem = Path(name).stem
    expected_prefix = f"{prefix}_"
    if not stem.startswith(expected_prefix):
        return None
    suffix = stem[len(expected_prefix) :]
    return int(suffix) if suffix.isdigit() else None


def build_payload(record: dict[str, Any], args: argparse.Namespace) -> tuple[str, dict[str, Any]]:
    route = record["generation_route"]
    prompt = record["prompt_template"]
    callback_url = resolve_callback_url(args.callback_url)
    if route == "suno-sounds":
        payload = build_suno_sounds_payload(
            prompt=prompt,
            model=args.sounds_model,
            sound_loop=False,
            callback_url=callback_url,
        )
        model = "suno-sounds"
    elif route == "suno-music":
        payload = build_suno_music_payload(
            prompt=prompt,
            model=args.music_model,
            instrumental=True,
            callback_url=callback_url,
        )
        model = "suno-music"
    else:
        raise ValueError(f"Unsupported generation route: {route}")
    return model, payload


def next_variant_numbers(existing_variants: list[dict[str, Any]], prefix: str, desired_count: int, overwrite_all: bool) -> list[int]:
    existing_numbers = sorted(
        number
        for number in (parse_variant_number(variant["name"], prefix) for variant in existing_variants)
        if number is not None
    )
    if overwrite_all:
        return list(range(1, desired_count + 1))
    existing_set = set(existing_numbers)
    return [number for number in range(1, desired_count + 1) if number not in existing_set]


def chunk_numbers(numbers: list[int], size: int) -> list[list[int]]:
    if size <= 0:
        raise ValueError("variants_per_request must be greater than zero")
    return [numbers[index : index + size] for index in range(0, len(numbers), size)]


def request_label(prefix: str, numbers: list[int]) -> str:
    if not numbers:
        raise ValueError("request_label requires at least one variant number")
    if len(numbers) == 1:
        return f"{prefix}_{numbers[0]:02d}"
    return f"{prefix}_{numbers[0]:02d}__{numbers[-1]:02d}"


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


def semantic_variants(record: dict[str, Any]) -> list[dict[str, Any]]:
    variants: list[dict[str, Any]] = []
    for item in record.get("reference_items") or []:
        if not isinstance(item, dict):
            continue
        url = item.get("url")
        if not isinstance(url, str) or not url:
            continue
        relative_path = urlparse(url).path.lstrip("/")
        variants.append(
            {
                "name": Path(relative_path).stem,
                "url": url,
                "location": relative_path,
                "usage": record.get("usage", ""),
                "audio_type": resolve_audio_type(record),
            }
        )
    return sorted(variants, key=lambda item: item["name"])


def existing_variants_for_record(record: dict[str, Any]) -> list[dict[str, Any]]:
    if record.get("record_type") == "semantic_query":
        return semantic_variants(record)
    return list(record.get("variants") or [])


def target_for_record(record: dict[str, Any]) -> tuple[str, str]:
    if record.get("record_type") == "semantic_query":
        return build_semantic_target(record)
    target = record["target"]
    return target["directory"], target["filename_prefix"]


def update_record_variant(record: dict[str, Any], variant_entry: dict[str, Any]) -> None:
    if record.get("record_type") == "semantic_query":
        item_type = semantic_item_type(record)
        items = []
        for item in record.get("reference_items") or []:
            if not isinstance(item, dict):
                continue
            existing_url = item.get("url")
            existing_stem = Path(urlparse(existing_url).path).stem if isinstance(existing_url, str) and existing_url else None
            if existing_stem == variant_entry["name"]:
                continue
            items.append(item)
        items.append({"type": item_type, "url": variant_entry["url"]})
        items.sort(key=lambda item: item.get("url", ""))
        record["reference_items"] = items
        return

    record["variants"] = [variant for variant in record["variants"] if variant.get("name") != variant_entry["name"]]
    record["variants"].append(
        {
            **variant_entry,
            "usage": record["usage"],
            "audio_type": resolve_audio_type(record),
        }
    )
    record["variants"].sort(key=lambda item: item["name"])


def iter_download_candidates(final_result: dict[str, Any]) -> list[str]:
    candidates: list[str] = []
    response = final_result.get("response") or {}
    suno_data = response.get("sunoData") or []
    if isinstance(suno_data, list):
        for item in suno_data:
            if not isinstance(item, dict):
                continue
            for key in ("streamAudioUrl", "audioUrl", "sourceStreamAudioUrl", "sourceAudioUrl"):
                value = item.get(key)
                if isinstance(value, str) and value:
                    candidates.append(value)

    for value in final_result.get("outputUrls") or []:
        if isinstance(value, str) and value and (value.endswith(".mp3") or "musicfile.kie.ai" in value):
            candidates.append(value)

    output_url = final_result.get("outputUrl")
    if isinstance(output_url, str) and output_url:
        candidates.append(output_url)

    deduped: list[str] = []
    seen: set[str] = set()
    for url in candidates:
        if url in seen:
            continue
        seen.add(url)
        deduped.append(url)
    return deduped


def iter_item_download_candidates(item: dict[str, Any]) -> list[str]:
    candidates: list[str] = []
    for key in ("streamAudioUrl", "audioUrl", "sourceStreamAudioUrl", "sourceAudioUrl"):
        value = item.get(key)
        if isinstance(value, str) and value:
            candidates.append(value)

    deduped: list[str] = []
    seen: set[str] = set()
    for url in candidates:
        if url in seen:
            continue
        seen.add(url)
        deduped.append(url)
    return deduped


def resolve_generation_outputs(final_result: dict[str, Any]) -> list[dict[str, Any]]:
    response = final_result.get("response") or {}
    suno_data = response.get("sunoData") or []
    outputs: list[dict[str, Any]] = []
    if isinstance(suno_data, list):
        for index, item in enumerate(suno_data):
            if not isinstance(item, dict):
                continue
            candidates = iter_item_download_candidates(item)
            if not candidates:
                continue
            outputs.append(
                {
                    "index": index,
                    "candidate_urls": candidates,
                    "raw_item": item,
                }
            )
    if outputs:
        return outputs

    fallback_candidates = iter_download_candidates(final_result)
    if not fallback_candidates:
        return []
    return [{"index": 0, "candidate_urls": fallback_candidates, "raw_item": {}}]


def download_file(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request) as response, destination.open("wb") as handle:
        shutil.copyfileobj(response, handle)


def download_first_available(candidates: list[str], destination: Path) -> str:
    last_error: Exception | None = None
    for candidate in candidates:
        try:
            download_file(candidate, destination)
            return candidate
        except (urllib.error.URLError, urllib.error.HTTPError, PermissionError, OSError) as exc:
            last_error = exc
            continue
    if last_error is None:
        raise RuntimeError("No downloadable output URLs were available")
    raise RuntimeError(f"All candidate output URLs failed; last error: {last_error}")


def sync_variant_into_library_index(
    library_index: dict[str, list[dict[str, Any]]],
    *,
    group: str,
    name: str,
    location: str,
    usage: str,
    audio_type: str,
    remote_base_url: str,
) -> None:
    bucket = library_index.setdefault(group, [])
    updated = {
        "name": name,
        "url": url_join(remote_base_url, location),
        "location": location,
        "usage": usage,
        "audio_type": audio_type,
    }
    for index, existing in enumerate(bucket):
        if existing.get("name") == name:
            bucket[index] = updated
            break
    else:
        bucket.append(updated)
        bucket.sort(key=lambda item: item["name"])


def build_local_target(audio_root: Path, relative_location: str) -> Path:
    return local_path_from_location(audio_root, relative_location)


def existing_variants_from_disk(
    *,
    record: dict[str, Any],
    audio_root: Path,
    target_directory: str,
    prefix: str,
) -> list[dict[str, Any]]:
    local_dir = build_local_target(audio_root, target_directory)
    if not local_dir.exists():
        return []

    variants: list[dict[str, Any]] = []
    for path in sorted(local_dir.glob(f"{prefix}_*.mp3")):
        number = parse_variant_number(path.name, prefix)
        if number is None:
            continue
        relative_location = f"{target_directory.rstrip('/')}/{path.name}"
        variants.append(
            {
                "name": path.stem,
                "location": relative_location,
                "usage": record.get("usage", ""),
                "audio_type": resolve_audio_type(record),
            }
        )
    return variants


def main() -> int:
    global LIVE_STAGE_STREAM
    args = parse_args()
    LIVE_STAGE_STREAM = args.verbose_stages
    catalog_path = Path(args.catalog)
    library_audios_path = Path(args.library_audios)
    audio_root = Path(args.audio_root)
    jobs_root = Path(args.jobs_root)
    download_root = Path(args.download_root)

    catalog = load_json(catalog_path)
    library_index = load_json(library_audios_path)
    records = list(catalog["records"])
    if args.record_id:
        allowed_ids = set(args.record_id)
        records = [record for record in records if record["id"] in allowed_ids]

    results: list[dict[str, Any]] = []
    stage_events: list[dict[str, Any]] = []

    config = None if args.dry_run else load_config()
    client = None if args.dry_run else KieClient(config)

    for record in records:
        add_stage_event(stage_events, record_id=record["id"], stage="record_start", status="started")
        target_directory, prefix = target_for_record(record)
        existing_variants = existing_variants_from_disk(
            record=record,
            audio_root=audio_root,
            target_directory=target_directory,
            prefix=prefix,
        )
        if not existing_variants:
            existing_variants = existing_variants_for_record(record)
        planned_numbers = next_variant_numbers(existing_variants, prefix, args.desired_count, args.overwrite_all)
        if not planned_numbers:
            add_stage_event(
                stage_events,
                record_id=record["id"],
                stage="record_skip",
                status="skipped_existing",
                detail={"existing": len(existing_variants)},
            )
            results.append({"id": record["id"], "status": "skipped_existing", "existing": len(existing_variants)})
            continue

        for numbers_chunk in chunk_numbers(planned_numbers, args.variants_per_request):
            chunk_targets: list[dict[str, Any]] = []
            for number in numbers_chunk:
                target_name = f"{prefix}_{number:02d}.mp3"
                relative_location = f"{target_directory}/{target_name}"
                target_path = build_local_target(audio_root, relative_location)
                if target_path.exists() and not args.overwrite_all:
                    results.append({"id": record["id"], "target": target_name, "status": "skipped_existing_file"})
                    continue
                chunk_targets.append(
                    {
                        "number": number,
                        "target_name": target_name,
                        "relative_location": relative_location,
                        "target_path": target_path,
                    }
                )

            if not chunk_targets:
                continue

            model, payload = build_payload(record, args)
            job_dir = jobs_root / record["id"]
            numbers_for_request = [entry["number"] for entry in chunk_targets]
            request_base = request_label(prefix, numbers_for_request)
            add_stage_event(
                stage_events,
                record_id=record["id"],
                stage="request_planned",
                status="ready",
                request_label=request_base,
                detail={
                    "model": model,
                    "targetCount": len(chunk_targets),
                    "targets": [entry["target_name"] for entry in chunk_targets],
                },
            )
            submit_job_path = job_dir / f"{request_base}.submit.json"
            final_job_path = job_dir / f"{request_base}.final.json"

            if args.dry_run:
                for entry in chunk_targets:
                    add_stage_event(
                        stage_events,
                        record_id=record["id"],
                        stage="request_dry_run",
                        status="dry_run",
                        request_label=request_base,
                        target=entry["target_name"],
                        detail={"model": model},
                    )
                    results.append(
                        {
                            "id": record["id"],
                            "target": entry["target_name"],
                            "status": "dry_run",
                            "model": model,
                            "payload": payload,
                            "requestLabel": request_base,
                        }
                    )
                continue

            try:
                add_stage_event(stage_events, record_id=record["id"], stage="submit", status="started", request_label=request_base)
                if model == "suno-sounds":
                    submit_response = client.create_suno_sounds_task(payload)
                else:
                    submit_response = client.create_suno_music_task(payload)
                submit_result = normalize_submit(submit_response, model=model)
                if not submit_result.get("ok"):
                    add_stage_event(
                        stage_events,
                        record_id=record["id"],
                        stage="submit",
                        status="failed",
                        request_label=request_base,
                        detail=submit_result,
                    )
                    write_json(final_job_path, submit_result)
                    for entry in chunk_targets:
                        results.append(
                            {
                                "id": record["id"],
                                "target": entry["target_name"],
                                "status": "submit_failed",
                                "detail": submit_result,
                                "requestLabel": request_base,
                            }
                        )
                    continue

                job_record = build_job_record(
                    job_id=submit_result["jobId"],
                    model=model,
                    status=submit_result.get("status", "queued"),
                    submitted_payload=payload,
                    resolved_media=[],
                    raw_submit_response=submit_response,
                )
                write_job_record(job_record, submit_job_path)
                add_stage_event(
                    stage_events,
                    record_id=record["id"],
                    stage="submit",
                    status="succeeded",
                    request_label=request_base,
                    detail={"jobId": submit_result["jobId"], "model": model},
                )

                add_stage_event(stage_events, record_id=record["id"], stage="poll", status="started", request_label=request_base)
                final_result = poll_until_complete(
                    client=client,
                    job_id=submit_result["jobId"],
                    model=model,
                    market_normalizer=normalize_market_status,
                    veo_normalizer=normalize_veo_status,
                    suno_music_normalizer=normalize_suno_music_status,
                    suno_lyrics_normalizer=normalize_suno_lyrics_status,
                    poll_interval=args.poll_interval,
                    timeout=args.timeout,
                )
                write_json(final_job_path, final_result)
                add_stage_event(
                    stage_events,
                    record_id=record["id"],
                    stage="poll",
                    status=final_result.get("status", "unknown"),
                    request_label=request_base,
                    detail={"jobId": submit_result["jobId"]},
                )
                if final_result.get("status") != "succeeded":
                    for entry in chunk_targets:
                        results.append(
                            {
                                "id": record["id"],
                                "target": entry["target_name"],
                                "status": "generation_failed",
                                "detail": final_result,
                                "requestLabel": request_base,
                            }
                        )
                    continue

                outputs = resolve_generation_outputs(final_result)
                if not outputs:
                    add_stage_event(
                        stage_events,
                        record_id=record["id"],
                        stage="outputs",
                        status="missing_output_url",
                        request_label=request_base,
                    )
                    for entry in chunk_targets:
                        results.append(
                            {
                                "id": record["id"],
                                "target": entry["target_name"],
                                "status": "missing_output_url",
                                "detail": final_result,
                                "requestLabel": request_base,
                            }
                        )
                    continue

                add_stage_event(
                    stage_events,
                    record_id=record["id"],
                    stage="outputs",
                    status="resolved",
                    request_label=request_base,
                    detail={"outputCount": len(outputs)},
                )

                for entry, output in zip(chunk_targets, outputs):
                    add_stage_event(
                        stage_events,
                        record_id=record["id"],
                        stage="download",
                        status="started",
                        request_label=request_base,
                        target=entry["target_name"],
                    )
                    download_root.mkdir(parents=True, exist_ok=True)
                    with NamedTemporaryFile(delete=False, suffix=".mp3", dir=download_root) as handle:
                        temp_path = Path(handle.name)
                    downloaded_from = download_first_available(output["candidate_urls"], temp_path)
                    target_path = entry["target_path"]
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    temp_path.replace(target_path)

                    variant_entry = {
                        "name": Path(entry["relative_location"]).stem,
                        "url": url_join(args.remote_base_url, entry["relative_location"]),
                        "location": entry["relative_location"],
                    }
                    update_record_variant(record, variant_entry)

                    if record.get("record_type") == "asset_family":
                        sync_variant_into_library_index(
                            library_index,
                            group=record["group"],
                            name=variant_entry["name"],
                            location=variant_entry["location"],
                            usage=record["usage"],
                            audio_type=resolve_audio_type(record),
                            remote_base_url=args.remote_base_url,
                        )

                    write_json(catalog_path, catalog)
                    write_json(library_audios_path, library_index)
                    add_stage_event(
                        stage_events,
                        record_id=record["id"],
                        stage="materialize",
                        status="generated",
                        request_label=request_base,
                        target=entry["target_name"],
                        detail={"outputUrl": downloaded_from},
                    )
                    results.append(
                        {
                            "id": record["id"],
                            "target": entry["target_name"],
                            "status": "generated",
                            "outputUrl": downloaded_from,
                            "candidateCount": len(output["candidate_urls"]),
                            "requestLabel": request_base,
                            "outputIndex": output["index"],
                        }
                    )

                if len(outputs) < len(chunk_targets):
                    for entry in chunk_targets[len(outputs) :]:
                        add_stage_event(
                            stage_events,
                            record_id=record["id"],
                            stage="outputs",
                            status="insufficient_outputs",
                            request_label=request_base,
                            target=entry["target_name"],
                            detail={"expectedOutputs": len(chunk_targets), "receivedOutputs": len(outputs)},
                        )
                        results.append(
                            {
                                "id": record["id"],
                                "target": entry["target_name"],
                                "status": "insufficient_outputs",
                                "requestLabel": request_base,
                                "expectedOutputs": len(chunk_targets),
                                "receivedOutputs": len(outputs),
                            }
                        )
            except Exception as exc:  # noqa: BLE001
                add_stage_event(
                    stage_events,
                    record_id=record["id"],
                    stage="request_error",
                    status="error",
                    request_label=request_base,
                    detail={"error": str(exc)},
                )
                for entry in chunk_targets:
                    results.append(
                        {
                            "id": record["id"],
                            "target": entry["target_name"],
                            "status": "error",
                            "error": str(exc),
                            "requestLabel": request_base,
                        }
                    )
                continue

    output_payload: dict[str, Any] = {"results": results}
    if args.verbose_stages:
        output_payload["stage_events"] = stage_events
    print(json.dumps(output_payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())