#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_COLLECTION_MANIFEST = REPO_ROOT / "docs" / "publish_manifests" / "vatsal_app_alpha_231_manifest.json"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "tmp" / "safe_231_publish"
DEFAULT_RUNTIME_MANIFEST = DEFAULT_OUTPUT_DIR / "runtime_publish_manifest.json"
DEFAULT_PREFLIGHT_REPORT = DEFAULT_OUTPUT_DIR / "preflight_report.json"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def run_command(command: list[str]) -> dict[str, Any]:
    completed = subprocess.run(command, capture_output=True, text=True)
    return {
        "command": command,
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def parse_collection_sources(collection_manifest: Path) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, str]]]:
    payload = load_json(collection_manifest)
    entries = payload.get("entries") if isinstance(payload, dict) else None
    if not isinstance(entries, list):
        raise SystemExit(f"Collection manifest must contain an entries array: {collection_manifest}")

    normalized_entries: list[dict[str, Any]] = []
    runtime_manifest_entries: list[dict[str, str]] = []

    for index, entry in enumerate(entries, start=1):
        if not isinstance(entry, dict):
            raise SystemExit(f"Collection entry #{index} is not an object")
        source = entry.get("source")
        if not source:
            raise SystemExit(f"Collection entry #{index} is missing source")
        source_path = Path(str(source)).resolve()
        normalized_entries.append(
            {
                "index": index,
                "game_id": entry.get("game_id"),
                "remix_id": entry.get("remix_id"),
                "composite_key": entry.get("composite_key"),
                "source": str(source_path),
            }
        )
        runtime_manifest_entries.append({"source": str(source_path)})

    return payload, normalized_entries, runtime_manifest_entries


def validate_sources(entries: list[dict[str, Any]]) -> dict[str, Any]:
    missing: list[dict[str, Any]] = []
    present_count = 0

    for entry in entries:
        source_path = Path(entry["source"])
        if source_path.is_dir():
            present_count += 1
            continue
        missing.append(
            {
                "index": entry["index"],
                "game_id": entry.get("game_id"),
                "remix_id": entry.get("remix_id"),
                "composite_key": entry.get("composite_key"),
                "source": entry["source"],
            }
        )

    return {
        "checked_count": len(entries),
        "present_count": present_count,
        "missing_count": len(missing),
        "missing": missing,
        "status": "passed" if not missing else "failed",
    }


def check_google_auth() -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    checks.append(
        {
            "name": "gcloud_version",
            **run_command(["gcloud", "--version"]),
        }
    )
    if checks[-1]["returncode"] != 0:
        return summarize_auth_checks(checks)

    checks.append(
        {
            "name": "gcloud_account",
            **run_command(["gcloud", "auth", "list", "--filter=status:ACTIVE", "--format=value(account)"]),
        }
    )
    if checks[-1]["returncode"] != 0 or not checks[-1]["stdout"]:
        return summarize_auth_checks(checks)

    checks.append(
        {
            "name": "application_default_account",
            **run_command(["gcloud", "auth", "application-default", "print-access-token"]),
        }
    )
    return summarize_auth_checks(checks)


def summarize_auth_checks(checks: list[dict[str, Any]]) -> dict[str, Any]:
    failures: list[dict[str, Any]] = []

    for check in checks:
        if check["returncode"] != 0:
            failures.append(
                {
                    "name": check["name"],
                    "reason": check["stderr"] or check["stdout"] or "command failed",
                }
            )
            continue
        if check["name"] == "gcloud_account" and not check["stdout"]:
            failures.append(
                {
                    "name": check["name"],
                    "reason": "no active gcloud account configured",
                }
            )
        if check["name"] == "application_default_account" and not check["stdout"]:
            failures.append(
                {
                    "name": check["name"],
                    "reason": "application-default auth did not return an access token",
                }
            )

    return {
        "status": "passed" if not failures else "failed",
        "checks": checks,
        "failure_count": len(failures),
        "failures": failures,
        "manual_login_required": bool(failures),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Assemble and preflight a fresh safe publish manifest for the canonical 231-item batch."
    )
    parser.add_argument(
        "--collection-manifest",
        default=str(DEFAULT_COLLECTION_MANIFEST),
        help="Canonical collection manifest with entries[].source.",
    )
    parser.add_argument(
        "--runtime-manifest",
        default=str(DEFAULT_RUNTIME_MANIFEST),
        help="Output path for the fresh runtime publish manifest.",
    )
    parser.add_argument(
        "--preflight-report",
        default=str(DEFAULT_PREFLIGHT_REPORT),
        help="Output path for the preflight report JSON.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()

    collection_manifest = Path(args.collection_manifest).resolve()
    runtime_manifest = Path(args.runtime_manifest).resolve()
    preflight_report = Path(args.preflight_report).resolve()

    collection_payload, normalized_entries, runtime_entries = parse_collection_sources(collection_manifest)
    source_validation = validate_sources(normalized_entries)
    auth_validation = check_google_auth()

    runtime_manifest_payload = runtime_entries
    preflight_payload = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "collection_manifest": str(collection_manifest),
        "batch_name": collection_payload.get("batch_name"),
        "entry_count": len(normalized_entries),
        "runtime_manifest_path": str(runtime_manifest),
        "source_validation": source_validation,
        "google_auth_validation": auth_validation,
        "ready_to_publish": source_validation["status"] == "passed" and auth_validation["status"] == "passed",
    }

    write_json(preflight_report, preflight_payload)

    if source_validation["status"] != "passed":
        print(json.dumps(preflight_payload, indent=2))
        print(
            "Preflight failed: one or more source paths are missing. See source_validation.missing in the preflight report.",
            file=sys.stderr,
        )
        return 2

    if auth_validation["status"] != "passed":
        print(json.dumps(preflight_payload, indent=2))
        print(
            "Preflight failed: Google auth is not ready. Run manual gcloud login / application-default login first.",
            file=sys.stderr,
        )
        return 3

    write_json(runtime_manifest, runtime_manifest_payload)
    print(json.dumps(preflight_payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())