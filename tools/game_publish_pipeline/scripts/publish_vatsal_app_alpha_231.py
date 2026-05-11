#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

SCRIPT_PATH = Path(__file__).resolve()
TOOL_ROOT = SCRIPT_PATH.parents[1]
REPO_ROOT = TOOL_ROOT.parents[1]

PUBLISH_GAMES_SCRIPT = TOOL_ROOT / "scripts" / "publish_games.py"
REFRESH_APP_ARTIFACTS_SCRIPT = TOOL_ROOT / "scripts" / "refresh_app_artifacts.py"
VALIDATE_PUBLISHED_OUTPUTS_SCRIPT = TOOL_ROOT / "scripts" / "validate_published_outputs.py"
SYNC_TO_GCS_SCRIPT = TOOL_ROOT / "scripts" / "sync_to_gcs.py"
DEFAULT_COLLECTION_MANIFEST = REPO_ROOT / "docs" / "publish_manifests" / "vatsal_app_alpha_231_manifest.json"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Canonical 231-entry publish entrypoint for Vatsal App Alpha using the same path as the passing 10-item pilot."
    )
    parser.add_argument(
        "--collection-manifest",
        default=str(DEFAULT_COLLECTION_MANIFEST),
        help="Manifest selecting the 231 published entries for full publish + obfuscation + refresh + validation.",
    )
    parser.add_argument(
        "--collection-slug",
        default="vatsal_app_alpha",
        help="Collection slug for public/obfuscated app artifacts.",
    )
    parser.add_argument(
        "--strict-validation",
        action="store_true",
        help="Fail the wrapper if the post-publish validation step reports required failures.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing published destinations during canonical full-batch publish.",
    )
    parser.add_argument(
        "--report-path",
        help="Optional explicit report path for the underlying canonical publish pipeline run.",
    )
    parser.add_argument(
        "--sync-to-gcs",
        action="store_true",
        help="After publish + refresh + validation, sync public and obfuscated outputs to GCS one item at a time.",
    )
    parser.add_argument(
        "--sync-gcs-project",
        default="jabali-prod",
        help="Google Cloud project forwarded to the isolated GCS sync step.",
    )
    parser.add_argument(
        "--sync-gcs-dry-run",
        action="store_true",
        help="Forward --dry-run to the isolated GCS sync step.",
    )
    return parser


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def build_publish_manifest(collection_manifest: Path) -> Path:
    payload = load_json(collection_manifest)
    entries = payload.get("entries") if isinstance(payload, dict) else None
    if not isinstance(entries, list):
        raise SystemExit("Collection manifest must be a JSON object with an 'entries' array.")
    publish_entries = []
    for entry in entries:
        if not isinstance(entry, dict):
            raise SystemExit("Collection manifest entries must be JSON objects.")
        source = entry.get("source")
        if not source:
            raise SystemExit("Each collection entry must include 'source' for canonical publish.")
        publish_entries.append({"source": str(source)})
    handle = tempfile.NamedTemporaryFile(prefix="publish-vatsal-app-alpha-231-", suffix=".json", delete=False)
    manifest_path = Path(handle.name)
    handle.close()
    write_json(manifest_path, publish_entries)
    return manifest_path


def build_runtime_collection_manifest(
    *,
    original_collection_manifest: Path,
    publish_report_path: Path,
) -> Path:
    original_payload = load_json(original_collection_manifest)
    original_entries = original_payload.get("entries") if isinstance(original_payload, dict) else None
    if not isinstance(original_entries, list):
        raise SystemExit("Original collection manifest must include an 'entries' array.")

    publish_report = load_json(publish_report_path)
    deployment_results = ((publish_report.get("deployment") or {}).get("results") or [])
    if not isinstance(deployment_results, list):
        raise SystemExit("Publish report must include deployment.results.")

    source_to_original: dict[str, dict[str, Any]] = {}
    for entry in original_entries:
        if not isinstance(entry, dict):
            continue
        source = entry.get("source")
        if isinstance(source, str):
            source_to_original[str(Path(source).resolve())] = entry

    runtime_entries: list[dict[str, Any]] = []
    for item in deployment_results:
        if not isinstance(item, dict):
            continue
        source = str(Path(str(item["source"])).resolve())
        original_entry = source_to_original.get(source)
        if original_entry is None:
            raise SystemExit(f"Could not map publish result source back to original collection entry: {source}")

        game_id = str(item["game_id"])
        remix_id = f"remix-{item['remix_uuid']}"
        published_path = f"{game_id}/{remix_id}"

        runtime_entries.append(
            {
                **original_entry,
                "game_id": game_id,
                "remix_id": remix_id,
                "composite_key": f"{game_id}__{remix_id}",
                "published_path": published_path,
                "source": source,
            }
        )

    runtime_payload = {
        "batch_name": f"{original_payload.get('batch_name', 'vatsal_app_alpha')}_runtime",
        "collection_slug": original_payload.get("collection_slug", "vatsal_app_alpha"),
        "generated_from": str(original_collection_manifest),
        "publish_report": str(publish_report_path),
        "entry_count": len(runtime_entries),
        "entries": runtime_entries,
    }
    handle = tempfile.NamedTemporaryFile(prefix="runtime-vatsal-app-alpha-231-", suffix=".json", delete=False)
    runtime_manifest_path = Path(handle.name)
    handle.close()
    write_json(runtime_manifest_path, runtime_payload)
    return runtime_manifest_path


def run_command(command: list[str]) -> dict[str, Any]:
    result = subprocess.run(command, capture_output=True, text=True)
    payload: dict[str, Any] = {
        "command": command,
        "returncode": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }
    if result.stdout.strip():
        try:
            payload["parsed"] = json.loads(result.stdout)
        except json.JSONDecodeError:
            payload["parsed"] = None
    else:
        payload["parsed"] = None
    if result.returncode != 0:
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        raise SystemExit(result.returncode)
    return payload


def main() -> None:
    args = build_parser().parse_args()
    collection_manifest = Path(args.collection_manifest).resolve()
    publish_manifest = build_publish_manifest(collection_manifest)

    if args.report_path:
        report_path = Path(args.report_path).resolve()
    else:
        report_path = REPO_ROOT / "tmp" / "game_publish_pipeline_canonical_report.json"

    print(f"[wrapper] collection manifest: {collection_manifest}", flush=True)
    print(f"[wrapper] generated publish manifest: {publish_manifest}", flush=True)
    print(f"[wrapper] pipeline report: {report_path}", flush=True)

    publish_command = [
        sys.executable,
        str(PUBLISH_GAMES_SCRIPT),
        "--manifest",
        str(publish_manifest),
        "--overwrite",
        "--report-path",
        str(report_path),
    ]
    if args.overwrite:
        publish_command.append("--overwrite")

    print("[wrapper] launching canonical publish pipeline...", flush=True)
    print(f"[wrapper] command: {' '.join(publish_command)}", flush=True)
    publish_result = run_command(publish_command)

    print("[wrapper] building runtime collection manifest from actual deployment results...", flush=True)
    runtime_collection_manifest = build_runtime_collection_manifest(
        original_collection_manifest=collection_manifest,
        publish_report_path=report_path,
    )
    print(f"[wrapper] runtime collection manifest: {runtime_collection_manifest}", flush=True)

    refresh_command = [
        sys.executable,
        str(REFRESH_APP_ARTIFACTS_SCRIPT),
        "--manifest",
        str(runtime_collection_manifest),
        "--collection-slug",
        str(args.collection_slug),
    ]
    print("[wrapper] refreshing app artifacts from runtime manifest...", flush=True)
    print(f"[wrapper] command: {' '.join(refresh_command)}", flush=True)
    refresh_result = run_command(refresh_command)

    validate_command = [
        sys.executable,
        str(VALIDATE_PUBLISHED_OUTPUTS_SCRIPT),
        "--manifest",
        str(runtime_collection_manifest),
        "--collection-slug",
        str(args.collection_slug),
    ]
    if args.strict_validation:
        validate_command.append("--strict")
    print("[wrapper] validating published outputs from runtime manifest...", flush=True)
    print(f"[wrapper] command: {' '.join(validate_command)}", flush=True)
    validation_result = run_command(validate_command)

    sync_result: dict[str, Any] | None = None
    if args.sync_to_gcs:
        sync_command = [
            sys.executable,
            str(SYNC_TO_GCS_SCRIPT),
            "--target",
            "both",
            "--mode",
            "per-item",
            "--project",
            str(args.sync_gcs_project),
        ]
        if args.sync_gcs_dry_run:
            sync_command.append("--dry-run")
        print("[wrapper] syncing public items to GCS and then obfuscated items to GCS...", flush=True)
        print(f"[wrapper] command: {' '.join(sync_command)}", flush=True)
        sync_result = run_command(sync_command)

    print(
        json.dumps(
            {
                "collection_manifest": str(collection_manifest),
                "collection_slug": str(args.collection_slug),
                "publish_manifest": str(publish_manifest),
                "pipeline_report": str(report_path),
                "runtime_collection_manifest": str(runtime_collection_manifest),
                "canonical_publish": publish_result.get("parsed"),
                "app_artifacts_refresh": refresh_result.get("parsed"),
                "validation": validation_result.get("parsed"),
                "gcs_sync": sync_result.get("parsed") if sync_result else None,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()