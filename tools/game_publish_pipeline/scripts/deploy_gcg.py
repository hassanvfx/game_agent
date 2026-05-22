#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from game_publish_pipeline.cleanup import (  # noqa: E402
    build_candidate_directory_map,
    build_candidate_key_set,
    build_regression_audit,
    build_runtime_manifest_from_public_root,
    delete_published_targets,
    detect_identical_public_obfuscated,
    sanitize_published_media_refs,
    write_json,
)


SCRIPT_PATH = Path(__file__).resolve()
TOOL_ROOT = SCRIPT_PATH.parents[1]
REPO_ROOT = TOOL_ROOT.parents[1]

DEFAULT_PUBLIC_ROOT = REPO_ROOT / "games" / "published" / "public"
DEFAULT_OBFUSCATED_ROOT = REPO_ROOT / "games" / "published" / "obfuscated"
DEFAULT_RUNS_ROOT = REPO_ROOT / "games" / "published" / "runs"
REFRESH_APP_ARTIFACTS_SCRIPT = TOOL_ROOT / "scripts" / "refresh_app_artifacts.py"
VALIDATE_PUBLISHED_OUTPUTS_SCRIPT = TOOL_ROOT / "scripts" / "validate_published_outputs.py"
SYNC_TO_GCS_SCRIPT = TOOL_ROOT / "scripts" / "sync_to_gcs.py"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Published-only cleanup/deploy wrapper for GCG-facing public and obfuscated outputs."
    )
    parser.add_argument("--public-root", default=str(DEFAULT_PUBLIC_ROOT), help="Published public root.")
    parser.add_argument("--obfuscated-root", default=str(DEFAULT_OBFUSCATED_ROOT), help="Published obfuscated root.")
    parser.add_argument("--runs-root", default=str(DEFAULT_RUNS_ROOT), help="Published runs root for refresh artifacts.")
    parser.add_argument("--collection-slug", default="vatsal_app_alpha", help="Collection slug for regenerated app artifacts.")
    parser.add_argument("--sample-limit", type=int, default=20, help="Sample limit for audit output slices.")
    parser.add_argument("--approved", choices=("true", "false"), help="Optional approved value forwarded to refresh_app_artifacts.py.")
    parser.add_argument(
        "--reconcile-mode",
        choices=("replace", "merge"),
        default="replace",
        help="How refreshed root artifacts should reconcile with existing root artifacts.",
    )
    parser.add_argument("--run-id", help="Optional explicit run id forwarded to refresh_app_artifacts.py and validation.")
    parser.add_argument("--report-path", help="Optional JSON report path for the wrapper result.")
    parser.add_argument("--runtime-manifest-path", help="Optional path for the generated runtime manifest.")
    parser.add_argument(
        "--confirm-delete",
        action="store_true",
        help="Allow deletion of mapped published candidates. Without this flag, the wrapper stops after audit/report when candidates are found.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview deletion/sanitization/runtime-manifest effects without mutating files or running refresh/validate.",
    )
    parser.add_argument(
        "--sync-to-gcs",
        action="store_true",
        help="After refresh + validation, sync public and obfuscated outputs to GCS one item at a time.",
    )
    parser.add_argument("--sync-gcs-project", default="jabali-prod", help="Google Cloud project forwarded to sync_to_gcs.py.")
    parser.add_argument(
        "--sync-gcs-dry-run",
        action="store_true",
        help="Forward --dry-run to sync_to_gcs.py when --sync-to-gcs is enabled.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print stage-by-stage and per-item progress, and stream child command output live.",
    )
    return parser


def default_report_path() -> Path:
    timestamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    return (REPO_ROOT / "tmp" / f"deploy_gcg_report_{timestamp}.json").resolve()


def default_runtime_manifest_path() -> Path:
    timestamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    return (REPO_ROOT / "tmp" / f"deploy_gcg_runtime_manifest_{timestamp}.json").resolve()


def parse_json_payload_from_stdout(stdout: str) -> dict[str, Any] | None:
    text = stdout.strip()
    if not text:
        return None

    try:
        payload = json.loads(text)
        if isinstance(payload, dict):
            return payload
    except json.JSONDecodeError:
        pass

    open_brace_positions = [index for index, char in enumerate(text) if char == "{"]
    for index in reversed(open_brace_positions):
        candidate = text[index:]
        try:
            payload = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            return payload
    return None


def print_stage_banner(title: str) -> None:
    print(f"[deploy_gcg] {title}", flush=True)


def print_detail(message: str) -> None:
    print(f"[deploy_gcg] {message}", flush=True)


def build_delete_markers(public_delete_targets: list[str], obfuscated_delete_targets: list[str]) -> list[str]:
    markers: list[str] = []
    for rel_path in public_delete_targets:
        markers.append(f"public:{rel_path}")
    for rel_path in obfuscated_delete_targets:
        markers.append(f"obfuscated:{rel_path}")
    markers.sort(key=lambda item: (-len(Path(item.split(":", 1)[1]).parts), item))
    return markers


def print_delete_markers(markers: list[str]) -> None:
    total = len(markers)
    for index, marker in enumerate(markers, start=1):
        print_detail(f"[{index}/{total}] delete target :: {marker}")


def print_sanitize_result(sanitize_result: dict[str, Any]) -> None:
    root_summaries = sanitize_result.get("root_summaries") or []
    for summary in root_summaries:
        print_detail(
            "sanitize root :: "
            f"root={summary.get('root')} scanned={summary.get('scanned_file_count')} "
            f"changed={summary.get('changed_file_count')}"
        )

    changed_entries = sanitize_result.get("changed_entries") or []
    total = len(changed_entries)
    for index, entry in enumerate(changed_entries, start=1):
        print_detail(
            "sanitize change :: "
            f"[{index}/{total}] {entry.get('root')}::{entry.get('path')} "
            f"removed_refs={entry.get('removed_reference_count')}"
        )


def run_command(command: list[str], *, verbose: bool = False, label: str | None = None) -> dict[str, Any]:
    if verbose:
        if label:
            print_stage_banner(f"running child command :: {label}")
        print_detail(f"command :: {' '.join(command)}")
        completed = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        stdout_lines: list[str] = []
        assert completed.stdout is not None
        for line in completed.stdout:
            print(line.rstrip("\n"), flush=True)
            stdout_lines.append(line)
        returncode = completed.wait()
        stdout = "".join(stdout_lines).strip()
        if returncode != 0:
            raise SystemExit(returncode)
        return {
            "command": command,
            "stdout": stdout,
            "stderr": "",
            "parsed": parse_json_payload_from_stdout(stdout),
        }

    completed = subprocess.run(command, capture_output=True, text=True)
    stdout = completed.stdout.strip()
    stderr = completed.stderr.strip()
    if stdout:
        print(stdout)
    if stderr:
        print(stderr, file=sys.stderr)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)
    return {
        "command": command,
        "stdout": stdout,
        "stderr": stderr,
        "parsed": parse_json_payload_from_stdout(stdout),
    }


def build_report_skeleton(
    *,
    audit_report: dict[str, Any],
    identical_report: dict[str, Any],
    candidate_directory_map: dict[str, Any],
) -> dict[str, Any]:
    candidate_game_ids = sorted(
        {
            str(entry.get("game_id"))
            for entry in candidate_directory_map.get("candidate_entries", [])
            if entry.get("game_id")
        }
        | {
            str(entry.get("game_id"))
            for entry in candidate_directory_map.get("affected_gamezone_entries", [])
            if entry.get("game_id")
        }
    )
    return {
        "audit": audit_report,
        "identical": identical_report,
        "candidate_directory_map": candidate_directory_map,
        "candidate_summary": {
            "candidate_composite_key_count": int(candidate_directory_map.get("candidate_count") or 0),
            "identical_affected_gamezone_count": int(candidate_directory_map.get("affected_gamezone_count") or 0),
            "public_delete_target_count": len(candidate_directory_map.get("public_delete_targets", [])),
            "obfuscated_delete_target_count": len(candidate_directory_map.get("obfuscated_delete_targets", [])),
            "candidate_game_ids": candidate_game_ids,
            "requires_confirmation": bool(candidate_directory_map.get("public_delete_targets") or candidate_directory_map.get("obfuscated_delete_targets")),
        },
    }


def main() -> int:
    args = build_parser().parse_args()

    public_root = Path(args.public_root).resolve()
    obfuscated_root = Path(args.obfuscated_root).resolve()
    runs_root = Path(args.runs_root).resolve()
    public_app_path = public_root / "app.json"
    obfuscated_app_path = obfuscated_root / "app.json"
    report_path = Path(args.report_path).resolve() if args.report_path else default_report_path()
    runtime_manifest_path = Path(args.runtime_manifest_path).resolve() if args.runtime_manifest_path else default_runtime_manifest_path()

    if args.verbose:
        print_stage_banner("starting published cleanup/deploy wrapper")
        print_detail(f"public root :: {public_root}")
        print_detail(f"obfuscated root :: {obfuscated_root}")
        print_detail(f"runs root :: {runs_root}")

    if args.verbose:
        print_stage_banner("auditing published root catalogs")
    audit_report = build_regression_audit(
        public_app_path,
        obfuscated_app_path,
        sample_limit=int(args.sample_limit),
        label="deploy_gcg",
    )
    if args.verbose:
        print_detail(
            "audit summary :: "
            f"public_candidates={audit_report['public']['candidate_for_removal_count']} "
            f"obfuscated_candidates={audit_report['obfuscated']['candidate_for_removal_count']}"
        )

    if args.verbose:
        print_stage_banner("detecting identical public vs obfuscated outputs")
    identical_report = detect_identical_public_obfuscated(public_root, obfuscated_root)
    if args.verbose:
        print_detail(
            "identical summary :: "
            f"affected_gamezones={identical_report['affected_gamezone_count']} "
            f"identical_pairs={identical_report['identical_pairs']}"
        )

    if args.verbose:
        print_stage_banner("mapping cleanup candidates to concrete published directories")
    candidate_directory_map = build_candidate_directory_map(
        public_app_path=public_app_path,
        obfuscated_app_path=obfuscated_app_path,
        public_root=public_root,
        obfuscated_root=obfuscated_root,
        candidate_keys=build_candidate_key_set(audit_report),
        affected_gamezones=identical_report["affected_gamezone_ids"],
        audit_report=audit_report,
    )

    report = build_report_skeleton(
        audit_report=audit_report,
        identical_report=identical_report,
        candidate_directory_map=candidate_directory_map,
    )
    report["report_path"] = str(report_path)

    requires_confirmation = bool(report["candidate_summary"]["requires_confirmation"])
    public_delete_targets = candidate_directory_map.get("public_delete_targets", [])
    obfuscated_delete_targets = candidate_directory_map.get("obfuscated_delete_targets", [])
    delete_markers = build_delete_markers(public_delete_targets, obfuscated_delete_targets)

    if args.verbose:
        print_detail(
            "candidate mapping summary :: "
            f"public_delete_targets={len(public_delete_targets)} "
            f"obfuscated_delete_targets={len(obfuscated_delete_targets)}"
        )

    if requires_confirmation and not args.confirm_delete and not args.dry_run:
        report["status"] = "confirmation_required"
        write_json(report_path, report)
        print(
            json.dumps(
                {
                    "status": report["status"],
                    "report_path": str(report_path),
                    "public_delete_target_count": report["candidate_summary"]["public_delete_target_count"],
                    "obfuscated_delete_target_count": report["candidate_summary"]["obfuscated_delete_target_count"],
                    "identical_affected_gamezone_count": report["candidate_summary"]["identical_affected_gamezone_count"],
                },
                indent=2,
            )
        )
        return 0

    if args.dry_run:
        if args.verbose:
            print_stage_banner(f"dry-run delete preview ({len(delete_markers)} targets)")
            print_delete_markers(delete_markers)
        deletion_preview = delete_published_targets(
            public_root=public_root,
            obfuscated_root=obfuscated_root,
            public_delete_targets=public_delete_targets,
            obfuscated_delete_targets=obfuscated_delete_targets,
            dry_run=True,
        )
        if args.verbose:
            print_stage_banner("dry-run media sanitization analysis")
        sanitize_preview = sanitize_published_media_refs([public_root, obfuscated_root], apply_changes=False)
        if args.verbose:
            print_sanitize_result(sanitize_preview)
            print_stage_banner("dry-run runtime manifest build")
        runtime_manifest_preview = build_runtime_manifest_from_public_root(
            public_root,
            collection_slug=str(args.collection_slug),
            exclude_published_paths=public_delete_targets,
        )
        write_json(runtime_manifest_path, runtime_manifest_preview)
        if args.verbose:
            print_detail(f"runtime manifest entries :: {runtime_manifest_preview['entry_count']}")
            print_detail(f"report path :: {report_path}")
            print_detail(f"runtime manifest path :: {runtime_manifest_path}")

        report["status"] = "dry_run"
        report["dry_run_requires_confirmation_for_apply"] = requires_confirmation
        report["deletion"] = deletion_preview
        report["sanitize"] = sanitize_preview
        report["runtime_manifest"] = {
            "path": str(runtime_manifest_path),
            "entry_count": runtime_manifest_preview["entry_count"],
        }
        write_json(report_path, report)
        print(
            json.dumps(
                {
                    "status": report["status"],
                    "report_path": str(report_path),
                    "runtime_manifest_path": str(runtime_manifest_path),
                    "runtime_entry_count": runtime_manifest_preview["entry_count"],
                    "sanitize_changed_file_count": sanitize_preview["changed_file_count"],
                    "requires_confirmation_for_apply": requires_confirmation,
                },
                indent=2,
            )
        )
        return 0

    if args.verbose:
        print_stage_banner(f"deleting mapped published targets ({len(delete_markers)} total)")
        print_delete_markers(delete_markers)
    deletion_result = delete_published_targets(
        public_root=public_root,
        obfuscated_root=obfuscated_root,
        public_delete_targets=public_delete_targets,
        obfuscated_delete_targets=obfuscated_delete_targets,
        dry_run=False,
    )
    if args.verbose:
        print_detail(
            "delete summary :: "
            f"deleted={deletion_result['deleted_count']} missing={deletion_result['missing_count']}"
        )

    if args.verbose:
        print_stage_banner("sanitizing runtime mp3 references")
    sanitize_result = sanitize_published_media_refs([public_root, obfuscated_root], apply_changes=True)
    if args.verbose:
        print_sanitize_result(sanitize_result)

    if args.verbose:
        print_stage_banner("building runtime manifest from remaining public directories")
    runtime_manifest = build_runtime_manifest_from_public_root(public_root, collection_slug=str(args.collection_slug))
    write_json(runtime_manifest_path, runtime_manifest)
    if args.verbose:
        print_detail(f"runtime manifest entries :: {runtime_manifest['entry_count']}")

    refresh_command = [
        sys.executable,
        str(REFRESH_APP_ARTIFACTS_SCRIPT),
        "--manifest",
        str(runtime_manifest_path),
        "--collection-slug",
        str(args.collection_slug),
        "--public-root",
        str(public_root),
        "--obfuscated-root",
        str(obfuscated_root),
        "--runs-root",
        str(runs_root),
        "--reconcile-mode",
        str(args.reconcile_mode),
    ]
    if args.approved is not None:
        refresh_command.extend(["--approved", str(args.approved)])
    if args.run_id:
        refresh_command.extend(["--run-id", str(args.run_id)])
    if args.verbose:
        print_stage_banner("refreshing public and obfuscated root artifacts")
    refresh_result = run_command(refresh_command, verbose=bool(args.verbose), label="refresh_app_artifacts")
    refresh_payload = refresh_result.get("parsed") or {}
    effective_run_id = str(refresh_payload.get("run_id") or args.run_id or "")

    validate_command = [
        sys.executable,
        str(VALIDATE_PUBLISHED_OUTPUTS_SCRIPT),
        "--manifest",
        str(runtime_manifest_path),
        "--public-root",
        str(public_root),
        "--obfuscated-root",
        str(obfuscated_root),
        "--runs-root",
        str(runs_root),
        "--collection-slug",
        str(args.collection_slug),
        "--strict",
    ]
    if effective_run_id:
        validate_command.extend(["--run-id", effective_run_id])
    if args.verbose:
        print_stage_banner("validating published outputs")
    validation_result = run_command(validate_command, verbose=bool(args.verbose), label="validate_published_outputs")

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
        if args.verbose:
            print_stage_banner("syncing published outputs to GCS")
        sync_result = run_command(sync_command, verbose=bool(args.verbose), label="sync_to_gcs")

    report["status"] = "completed"
    report["deletion"] = deletion_result
    report["sanitize"] = sanitize_result
    report["runtime_manifest"] = {
        "path": str(runtime_manifest_path),
        "entry_count": runtime_manifest["entry_count"],
    }
    report["refresh"] = refresh_result.get("parsed")
    report["validation"] = validation_result.get("parsed")
    report["gcs_sync"] = sync_result.get("parsed") if sync_result else None
    write_json(report_path, report)

    if args.verbose:
        print_stage_banner("wrapper completed successfully")
        print_detail(f"report path :: {report_path}")
        print_detail(f"runtime manifest path :: {runtime_manifest_path}")

    print(
        json.dumps(
            {
                "status": report["status"],
                "report_path": str(report_path),
                "runtime_manifest_path": str(runtime_manifest_path),
                "runtime_entry_count": runtime_manifest["entry_count"],
                "deleted_target_count": deletion_result["deleted_count"],
                "sanitize_changed_file_count": sanitize_result["changed_file_count"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())