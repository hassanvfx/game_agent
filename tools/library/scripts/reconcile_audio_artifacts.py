#!/usr/bin/env python3
"""Reconcile, run missing audio jobs, and refresh local library artifacts."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from audio_paths import resolve_library_root  # type: ignore  # noqa: E402

LIBRARY_ROOT = resolve_library_root()
CATALOG_PATH = LIBRARY_ROOT / "catalog.json"
CATALOG_FINAL_PATH = LIBRARY_ROOT / "catalog_final.json"
JOBS_LIST_PATH = LIBRARY_ROOT / "jobs_list.json"
BUILD_JOBS_LIST_SCRIPT = ROOT / "tools" / "library" / "scripts" / "build_audio_jobs_list.py"
BUILD_CATALOG_FINAL_SCRIPT = ROOT / "tools" / "library" / "scripts" / "build_audio_catalog_final.py"
RUN_BATCH_SCRIPT = ROOT / "tools" / "library" / "scripts" / "run_audio_jobs_batch.py"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Reconcile, run missing audio jobs, and refresh local library artifacts.")
    parser.add_argument("--catalog", default=str(CATALOG_PATH))
    parser.add_argument("--jobs-list", default=str(JOBS_LIST_PATH))
    parser.add_argument("--catalog-final", default=str(CATALOG_FINAL_PATH))
    parser.add_argument("--desired-total-variants", type=int, default=4)
    parser.add_argument("--variants-per-request", type=int, default=2)
    parser.add_argument("--record-id", action="append", default=[])
    parser.add_argument("--max-records", type=int)
    parser.add_argument("--poll-interval", type=float, default=5.0)
    parser.add_argument("--timeout", type=float, default=900.0)
    parser.add_argument("--sounds-model", default="V5")
    parser.add_argument("--music-model")
    parser.add_argument("--include-semantic-query", action="store_true")
    parser.add_argument("--concrete-only", action="store_true")
    parser.add_argument("--callback-url")
    parser.add_argument("--verbose-stages", action="store_true")
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument("--overwrite-all", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--reconcile-only", action="store_true")
    return parser.parse_args()


def run(args: list[str]) -> None:
    subprocess.run(args, cwd=ROOT, check=True)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def refresh_artifacts(
    *,
    python: str,
    catalog_path: Path,
    jobs_list_path: Path,
    catalog_final_path: Path,
    desired_total_variants: int,
    variants_per_request: int,
) -> None:
    run(
        [
            python,
            str(BUILD_JOBS_LIST_SCRIPT),
            "--catalog",
            str(catalog_path),
            "--output",
            str(jobs_list_path),
            "--desired-total-variants",
            str(desired_total_variants),
            "--variants-per-request",
            str(variants_per_request),
        ]
    )
    run(
        [
            python,
            str(BUILD_CATALOG_FINAL_SCRIPT),
            "--catalog",
            str(catalog_path),
            "--output",
            str(catalog_final_path),
            "--desired-total-variants",
            str(desired_total_variants),
            "--variants-per-request",
            str(variants_per_request),
        ]
    )


def run_missing_jobs(
    *,
    python: str,
    args: argparse.Namespace,
    catalog_path: Path,
    jobs_list_path: Path,
) -> None:
    include_semantic_query = args.include_semantic_query or not args.concrete_only
    verbose_stages = args.verbose_stages or not args.quiet

    command = [
        python,
        str(RUN_BATCH_SCRIPT),
        "--catalog",
        str(catalog_path),
        "--jobs-list",
        str(jobs_list_path),
        "--desired-total-variants",
        str(args.desired_total_variants),
        "--variants-per-request",
        str(args.variants_per_request),
        "--poll-interval",
        str(args.poll_interval),
        "--timeout",
        str(args.timeout),
        "--sounds-model",
        args.sounds_model,
    ]
    if args.music_model:
        command.extend(["--music-model", args.music_model])
    if include_semantic_query:
        command.append("--include-semantic-query")
    if args.callback_url:
        command.extend(["--callback-url", args.callback_url])
    if verbose_stages:
        command.append("--verbose-stages")
    if args.overwrite_all:
        command.append("--overwrite-all")
    if args.dry_run:
        command.append("--dry-run")
    if args.max_records is not None:
        command.extend(["--max-records", str(args.max_records)])
    for record_id in args.record_id:
        command.extend(["--record-id", record_id])
    run(command)


def build_report(*, args: argparse.Namespace, jobs_list_path: Path, catalog_final_path: Path) -> dict[str, Any]:
    include_semantic_query = args.include_semantic_query or not args.concrete_only
    verbose_stages = args.verbose_stages or not args.quiet
    jobs_payload = load_json(jobs_list_path)
    catalog_final_payload = load_json(catalog_final_path)
    jobs = jobs_payload.get("jobs", [])
    concrete = [job for job in jobs if job.get("record_type") == "asset_family"]
    semantic = [job for job in jobs if job.get("record_type") == "semantic_query"]
    concrete_complete = sum(1 for job in concrete if job.get("status") == "complete")
    semantic_complete = sum(1 for job in semantic if job.get("status") == "complete")
    return {
        "jobs_list": str(jobs_list_path.relative_to(ROOT)),
        "catalog_final": str(catalog_final_path.relative_to(ROOT)),
        "run_mode": "reconcile_only" if args.reconcile_only else ("dry_run" if args.dry_run else "reconcile_run_refresh"),
        "launcher_defaults": {
            "include_semantic_query": include_semantic_query,
            "verbose_stages": verbose_stages,
        },
        "summary": jobs_payload.get("summary", {}),
        "catalog_final_summary": catalog_final_payload.get("summary", {}),
        "concrete_asset_family": {
            "total": len(concrete),
            "complete": concrete_complete,
            "pending": len(concrete) - concrete_complete,
        },
        "semantic_query": {
            "total": len(semantic),
            "complete": semantic_complete,
            "pending": len(semantic) - semantic_complete,
        },
    }


def main() -> int:
    args = parse_args()
    python = sys.executable
    catalog_path = Path(args.catalog)
    jobs_list_path = Path(args.jobs_list)
    catalog_final_path = Path(args.catalog_final)

    refresh_artifacts(
        python=python,
        catalog_path=catalog_path,
        jobs_list_path=jobs_list_path,
        catalog_final_path=catalog_final_path,
        desired_total_variants=args.desired_total_variants,
        variants_per_request=args.variants_per_request,
    )

    if not args.reconcile_only:
        run_missing_jobs(
            python=python,
            args=args,
            catalog_path=catalog_path,
            jobs_list_path=jobs_list_path,
        )
        refresh_artifacts(
            python=python,
            catalog_path=catalog_path,
            jobs_list_path=jobs_list_path,
            catalog_final_path=catalog_final_path,
            desired_total_variants=args.desired_total_variants,
            variants_per_request=args.variants_per_request,
        )

    print(json.dumps(build_report(args=args, jobs_list_path=jobs_list_path, catalog_final_path=catalog_final_path), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())