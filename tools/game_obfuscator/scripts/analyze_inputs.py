#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from orchestration_state import load_json, recompute_run_state, update_game_state, write_json


EXTERNAL_URL_RE = re.compile(r"https?://[^\s\"'()<>]+", re.IGNORECASE)
CSS_URL_RE = re.compile(r"url\((?P<quote>['\"]?)(?P<value>[^)'\"]+)(?P=quote)\)", re.IGNORECASE)
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".bmp", ".ico"}
AUDIO_EXTENSIONS = {".mp3", ".wav", ".ogg", ".m4a", ".aac", ".flac"}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze prepared Game Obfuscator run inputs.")
    parser.add_argument("--run-dir", required=True, help="Path to a prepared Game Obfuscator run directory.")
    return parser.parse_args()


def classify_file(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".html":
        return "html"
    if suffix == ".css":
        return "css"
    if suffix == ".js":
        return "js"
    if suffix in IMAGE_EXTENSIONS:
        return "image"
    if suffix in AUDIO_EXTENSIONS:
        return "audio"
    return "other"


def collect_text_references(file_type: str, text: str) -> dict[str, list[str]]:
    references: dict[str, list[str]] = {
        "external_urls": EXTERNAL_URL_RE.findall(text),
        "css_url_values": [match.group("value") for match in CSS_URL_RE.finditer(text)],
        "image_like_refs": [],
        "audio_like_refs": [],
    }

    for value in references["css_url_values"]:
        lower_value = value.lower()
        suffix = Path(lower_value).suffix
        if suffix in IMAGE_EXTENSIONS:
            references["image_like_refs"].append(value)
        elif suffix in AUDIO_EXTENSIONS:
            references["audio_like_refs"].append(value)

    lowered_text = text.lower()
    if file_type in {"html", "js"}:
        image_refs = re.findall(r"""['"]([^'"]+\.(?:png|jpg|jpeg|gif|webp|svg|bmp|ico))['"]""", text, re.IGNORECASE)
        audio_refs = re.findall(r"""['"]([^'"]+\.(?:mp3|wav|ogg|m4a|aac|flac))['"]""", text, re.IGNORECASE)
        references["image_like_refs"].extend(image_refs)
        references["audio_like_refs"].extend(audio_refs)

        if "<audio" in lowered_text or "new audio(" in lowered_text or "audiocontext" in lowered_text:
            references.setdefault("audio_api_markers", []).append("audio_api_detected")
        if "<img" in lowered_text or "new image(" in lowered_text:
            references.setdefault("image_api_markers", []).append("image_api_detected")

    return references


def analyze_game_input(game_id: str, input_dir: Path, artifacts_dir: Path) -> dict:
    files = sorted(path for path in input_dir.rglob("*") if path.is_file())
    file_counts: Counter[str] = Counter()
    inventory_files: list[dict] = []
    aggregate_external_urls: set[str] = set()
    aggregate_image_refs: list[str] = []
    aggregate_audio_refs: list[str] = []
    aggregate_markers: Counter[str] = Counter()

    for file_path in files:
        relative_path = file_path.relative_to(input_dir)
        file_type = classify_file(file_path)
        file_counts[file_type] += 1

        file_record = {
            "path": str(relative_path),
            "type": file_type,
            "size_bytes": file_path.stat().st_size,
        }

        if file_type in {"html", "css", "js"}:
            text = file_path.read_text(encoding="utf-8", errors="ignore")
            refs = collect_text_references(file_type, text)
            file_record["external_url_count"] = len(refs["external_urls"])
            file_record["image_reference_count"] = len(refs["image_like_refs"])
            file_record["audio_reference_count"] = len(refs["audio_like_refs"])

            aggregate_external_urls.update(refs["external_urls"])
            aggregate_image_refs.extend(refs["image_like_refs"])
            aggregate_audio_refs.extend(refs["audio_like_refs"])

            for marker in refs.get("audio_api_markers", []):
                aggregate_markers[marker] += 1
            for marker in refs.get("image_api_markers", []):
                aggregate_markers[marker] += 1

        inventory_files.append(file_record)

    input_inventory = {
        "generated_at": utc_now(),
        "game_id": game_id,
        "input_dir": str(input_dir),
        "files": inventory_files,
    }

    analysis_summary = {
        "generated_at": utc_now(),
        "game_id": game_id,
        "input_dir": str(input_dir),
        "file_counts": dict(file_counts),
        "text_reference_counts": {
            "external_url_count": len(aggregate_external_urls),
            "image_reference_count": len(aggregate_image_refs),
            "audio_reference_count": len(aggregate_audio_refs),
        },
        "detected_markers": dict(aggregate_markers),
        "sample_external_urls": sorted(aggregate_external_urls)[:20],
        "sample_image_references": aggregate_image_refs[:20],
        "sample_audio_references": aggregate_audio_refs[:20],
    }

    write_json(artifacts_dir / "input_inventory.json", input_inventory)
    write_json(artifacts_dir / "analysis_summary.json", analysis_summary)

    return analysis_summary


def main() -> None:
    args = parse_args()
    run_dir = Path(args.run_dir).resolve()

    manifest = load_json(run_dir / "input_manifest.json")
    run_state = load_json(run_dir / "run_state.json")
    recompute_run_state(run_dir, current_phase="analyze_inputs_started", note="Input analysis started.")

    analyzed_games = 0
    analysis_failed = 0
    total_external_refs = 0
    total_image_refs = 0
    total_audio_refs = 0

    for game in manifest.get("games", []):
        game_id = game["game_id"]
        game_state_path = run_dir / "games" / game_id / "game_state.json"
        game_state = load_json(game_state_path)
        input_dir = Path(game_state["input_mirror_path"])
        artifacts_dir = Path(game_state["artifacts_path"])

        update_game_state(
            run_dir,
            game_id,
            status="running",
            phase="analysis_started",
            last_error=None,
            mark_started=True,
            heartbeat=True,
            progress=True,
        )

        if not input_dir.exists():
            update_game_state(
                run_dir,
                game_id,
                status="failed",
                phase="analysis_failed",
                last_error=f"Input mirror path does not exist: {input_dir}",
                heartbeat=True,
                progress=True,
            )
            analysis_failed += 1
            continue

        analysis_summary = analyze_game_input(game_id, input_dir, artifacts_dir)
        analyzed_games += 1
        total_external_refs += analysis_summary["text_reference_counts"]["external_url_count"]
        total_image_refs += analysis_summary["text_reference_counts"]["image_reference_count"]
        total_audio_refs += analysis_summary["text_reference_counts"]["audio_reference_count"]

        update_game_state(
            run_dir,
            game_id,
            status="ready",
            phase="inventory_scanned",
            last_error=None,
            heartbeat=True,
            progress=True,
            artifacts={
                "input_inventory": str(artifacts_dir / "input_inventory.json"),
                "analysis_summary": str(artifacts_dir / "analysis_summary.json"),
            },
        )

    run_state["games_analyzed"] = analyzed_games
    run_state["games_analysis_failed"] = analysis_failed
    run_state["current_phase"] = "inputs_analyzed"
    run_state["status"] = "ready_for_rewrite_planning" if analysis_failed == 0 else "failed"
    run_state["analysis_totals"] = {
        "external_url_count": total_external_refs,
        "image_reference_count": total_image_refs,
        "audio_reference_count": total_audio_refs,
    }
    run_state["updated_at"] = utc_now()
    run_state.setdefault("notes", []).append("Input inventory analysis completed.")
    write_json(run_dir / "run_state.json", run_state)
    recompute_run_state(run_dir, current_phase="analyze_inputs_complete")

    print(run_dir)


if __name__ == "__main__":
    main()