#!/usr/bin/env python3
"""Run a resumable unattended batch over normalized library audio jobs."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from audio_paths import resolve_library_root  # type: ignore  # noqa: E402

LIBRARY_ROOT = resolve_library_root()
CATALOG_PATH = LIBRARY_ROOT / "catalog.json"
JOBS_LIST_PATH = LIBRARY_ROOT / "jobs_list.json"
DEFAULT_STATE_PATH = LIBRARY_ROOT / "jobs" / "batch" / "latest_batch_state.json"
GENERATOR_SCRIPT = ROOT / "tools" / "library" / "scripts" / "generate_audio_variants.py"

from build_audio_jobs_list import build_jobs_list_payload, write_json, load_json  # type: ignore  # noqa: E402


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run unattended resumable generation batch for library audio jobs.")
    parser.add_argument("--catalog", default=str(CATALOG_PATH))
    parser.add_argument("--jobs-list", default=str(JOBS_LIST_PATH))
    parser.add_argument("--state-path", default=str(DEFAULT_STATE_PATH))
    parser.add_argument("--desired-total-variants", type=int, default=4)
    parser.add_argument("--variants-per-request", type=int, default=2)
    parser.add_argument("--record-id", action="append", default=[])
    parser.add_argument("--max-records", type=int)
    parser.add_argument("--poll-interval", type=float, default=5.0)
    parser.add_argument("--timeout", type=float, default=900.0)
    parser.add_argument("--sounds-model", default="V5")
    parser.add_argument("--music-model")
    parser.add_argument("--include-semantic-query", action="store_true")
    parser.add_argument("--callback-url")
    parser.add_argument("--verbose-stages", action="store_true")
    parser.add_argument("--overwrite-all", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def print_stage_lines(job_id: str, payload: dict[str, Any] | None) -> None:
    if not payload:
        return
    stage_events = payload.get("stage_events") or []
    if not isinstance(stage_events, list):
        return
    for event in stage_events:
        if not isinstance(event, dict):
            continue
        stage = event.get("stage", "unknown")
        status = event.get("status", "unknown")
        target = event.get("target")
        request_label = event.get("requestLabel")
        parts = [f"[{job_id}]", f"stage={stage}", f"status={status}"]
        if request_label:
            parts.append(f"request={request_label}")
        if target:
            parts.append(f"target={target}")
        print(" ".join(parts))


def refresh_jobs_list(*, catalog_path: Path, jobs_list_path: Path, desired_total_variants: int, variants_per_request: int) -> dict[str, Any]:
    catalog = load_json(catalog_path)
    payload = build_jobs_list_payload(
        catalog,
        desired_total_variants=desired_total_variants,
        variants_per_request=variants_per_request,
    )
    write_json(jobs_list_path, payload)
    return payload


def extract_json(stdout: str) -> Any:
    text = stdout.strip()
    if not text:
        return None
    return json.loads(text)


def run_streaming(command: list[str]) -> tuple[int, str, str]:
    process = subprocess.Popen(
        command,
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )

    stdout_chunks: list[str] = []
    stderr_chunks: list[str] = []

    def consume_stdout() -> None:
        assert process.stdout is not None
        for line in process.stdout:
            stdout_chunks.append(line)

    def consume_stderr() -> None:
        assert process.stderr is not None
        for line in process.stderr:
            stderr_chunks.append(line)
            print(line, end="")

    stdout_thread = threading.Thread(target=consume_stdout, daemon=True)
    stderr_thread = threading.Thread(target=consume_stderr, daemon=True)
    stdout_thread.start()
    stderr_thread.start()
    returncode = process.wait()
    stdout_thread.join()
    stderr_thread.join()
    return returncode, "".join(stdout_chunks), "".join(stderr_chunks)


def main() -> int:
    args = parse_args()
    catalog_path = Path(args.catalog)
    jobs_list_path = Path(args.jobs_list)
    state_path = Path(args.state_path)

    jobs_payload = refresh_jobs_list(
        catalog_path=catalog_path,
        jobs_list_path=jobs_list_path,
        desired_total_variants=args.desired_total_variants,
        variants_per_request=args.variants_per_request,
    )

    jobs = list(jobs_payload["jobs"])
    if not args.include_semantic_query:
        jobs = [job for job in jobs if job.get("record_type") == "asset_family"]
    if args.record_id:
        allowed = set(args.record_id)
        jobs = [job for job in jobs if job["id"] in allowed]
    jobs = [job for job in jobs if args.overwrite_all or job["missing_variants"] > 0]
    if args.max_records is not None:
        jobs = jobs[: args.max_records]

    state: dict[str, Any] = {
        "schema_version": 1,
        "started_at": utc_now(),
        "catalog": str(catalog_path.relative_to(ROOT)),
        "jobs_list": str(jobs_list_path.relative_to(ROOT)),
        "desired_total_variants": args.desired_total_variants,
        "variants_per_request": args.variants_per_request,
        "include_semantic_query": args.include_semantic_query,
        "verbose_stages": args.verbose_stages,
        "jobs_total": len(jobs),
        "results": [],
    }
    write_json(state_path, state)

    for job in jobs:
        if args.verbose_stages:
            print(f"==> starting job {job['id']} ({job.get('record_type')})")
        command = [
            sys.executable,
            str(GENERATOR_SCRIPT),
            "--record-id",
            job["id"],
            "--desired-count",
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
        if args.callback_url:
            command.extend(["--callback-url", args.callback_url])
        if args.verbose_stages:
            command.append("--verbose-stages")
        if args.overwrite_all:
            command.append("--overwrite-all")
        if args.dry_run:
            command.append("--dry-run")

        returncode, stdout_text_raw, stderr_text_raw = run_streaming(command)
        parsed_stdout = None
        stdout_text = stdout_text_raw.strip()
        if stdout_text:
            try:
                parsed_stdout = extract_json(stdout_text)
            except json.JSONDecodeError:
                parsed_stdout = {"raw": stdout_text}

        state["results"].append(
            {
                "job_id": job["id"],
                "returncode": returncode,
                "stdout": parsed_stdout,
                "stderr": stderr_text_raw.strip(),
                "finished_at": utc_now(),
            }
        )
        write_json(state_path, state)

        if args.verbose_stages:
            print(f"<== finished job {job['id']} returncode={returncode}")

        refresh_jobs_list(
            catalog_path=catalog_path,
            jobs_list_path=jobs_list_path,
            desired_total_variants=args.desired_total_variants,
            variants_per_request=args.variants_per_request,
        )

    state["finished_at"] = utc_now()
    state["completed_jobs"] = len(state["results"])
    write_json(state_path, state)

    final_jobs_payload = load_json(jobs_list_path)
    summary = {
        "jobs_total": len(jobs),
        "completed_jobs": len(state["results"]),
        "pending_job_count": final_jobs_payload["summary"]["pending_job_count"],
        "complete_job_count": final_jobs_payload["summary"]["complete_job_count"],
        "state_path": str(state_path.relative_to(ROOT)),
        "jobs_list": str(jobs_list_path.relative_to(ROOT)),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())