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

from scripts.report_pending_counts import PROMPT_RUNS, compute_prompt_summary

DEFAULT_POLL_SECONDS = 60.0
DEFAULT_TIMEOUT_SECONDS = 24 * 3600
DEFAULT_MAX_CONCURRENCY = 2
DEFAULT_WORKFLOW_SCRIPT = "tools/game_refactoring/scripts/game_workflow.py"
DEFAULT_LEDGER_PATH = "tmp/game_refactoring_cli_queue_ledger.json"
DEFAULT_RUNS_ROOT = "/Volumes/HDD2026/output"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Sequential direct-CLI launcher for prompt/manifest game_refactoring jobs."
    )
    parser.add_argument("config", help="Path to JSON config containing queued launch jobs")
    parser.add_argument("--ledger-path", default=DEFAULT_LEDGER_PATH, help="Path to durable ledger/state file")
    parser.add_argument(
        "--workflow-script",
        default=DEFAULT_WORKFLOW_SCRIPT,
        help="Path to the direct CLI workflow launcher script",
    )
    parser.add_argument(
        "--runs-root",
        default=DEFAULT_RUNS_ROOT,
        help="Runs root used both for scripted reconciliation and new execution unless overridden per job",
    )
    parser.add_argument("--poll-seconds", type=float, default=DEFAULT_POLL_SECONDS)
    parser.add_argument("--timeout-seconds", type=int, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument("--max-concurrency", type=int, default=DEFAULT_MAX_CONCURRENCY)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--resume-running", action="store_true")
    parser.add_argument(
        "--max-attempts-per-job",
        type=int,
        default=3,
        help="Maximum total attempts per queue job, including the first run.",
    )
    return parser


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    tmp_path.replace(path)


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def log(message: str) -> None:
    print(f"[queue] {message}", flush=True)


def slugify(value: str) -> str:
    cleaned = []
    for char in value.lower():
        if char.isalnum():
            cleaned.append(char)
        else:
            cleaned.append("-")
    slug = "".join(cleaned)
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug.strip("-") or "job"


def ensure_list_of_dicts(value: Any, field_name: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{field_name} must be a non-empty list")
    normalized: list[dict[str, Any]] = []
    for item in value:
        if not isinstance(item, dict):
            raise ValueError(f"{field_name} entries must be objects")
        normalized.append(item)
    return normalized


def ensure_games_manifest(path: Path) -> dict[str, Any]:
    manifest = load_json(path, None)
    if not isinstance(manifest, dict):
        raise ValueError(f"Manifest at {path} must be a JSON object")
    ensure_list_of_dicts(manifest.get("games"), "games")
    return manifest


def normalize_game_id(entry: Any) -> str | None:
    if isinstance(entry, str):
        return entry
    if isinstance(entry, dict):
        value = entry.get("game_id") or entry.get("id") or entry.get("name")
        if value is not None:
            return str(value)
    return None


def build_manifest_from_raw_game_ids(job: dict[str, Any], job_name: str) -> Path:
    raw_game_ids = job.get("raw_game_ids")
    if not isinstance(raw_game_ids, list) or not raw_game_ids:
        raise ValueError("Each job must include manifest/games_manifest_source or non-empty raw_game_ids")
    games = []
    for raw_game_id in raw_game_ids:
        if not raw_game_id:
            raise ValueError(f"Job {job_name} includes an empty raw_game_id")
        games.append(
            {
                "game_id": str(raw_game_id),
                "source_path": str((Path("games/raw") / str(raw_game_id)).resolve()),
            }
        )
    manifest_path = Path("tmp/game_refactoring_cli_queue_manifests") / f"{slugify(job_name)}.json"
    save_json(
        manifest_path,
        {
            "manifest_version": "2.0.0",
            "run_label": slugify(job_name),
            "games": games,
            "generated_by": "scripts/run_game_refactoring_queue.py",
            "generated_at": utc_now(),
        },
    )
    return manifest_path


def compute_pending_games_for_prompt(
    prompt_key: str,
    base_manifest_path: Path,
    runs_root: Path,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    base_manifest = ensure_games_manifest(base_manifest_path)
    base_games = ensure_list_of_dicts(base_manifest.get("games"), "games")
    base_by_id = {}
    for game in base_games:
        game_id = normalize_game_id(game)
        if game_id:
            base_by_id[game_id] = game

    family = PROMPT_RUNS.get(prompt_key)
    if not family:
        pending_games = list(base_by_id.values())
        return pending_games, {
            "prompt_key": prompt_key,
            "used_scripted_runs": False,
            "source_runs": [],
            "resolved_count": 0,
            "pending_count": len(pending_games),
        }

    summary = compute_prompt_summary(prompt_key, family, set(base_by_id.keys()), runs_root)
    pending_games = [base_by_id[game_id] for game_id in summary["pending_game_ids"] if game_id in base_by_id]
    return pending_games, {
        "prompt_key": prompt_key,
        "used_scripted_runs": True,
        "source_runs": summary["source_runs"],
        "resolved_count": summary["resolved_count"],
        "pending_count": summary["pending_count"],
    }


def write_pending_manifest(job_name: str, prompt_key: str, base_manifest_path: Path, pending_games: list[dict[str, Any]]) -> Path:
    base_manifest = ensure_games_manifest(base_manifest_path)
    payload = dict(base_manifest)
    payload["games"] = pending_games
    payload["pending_context"] = {
        "prompt_key": prompt_key,
        "generated_at": utc_now(),
        "source_manifest": str(base_manifest_path),
        "games_count": len(pending_games),
    }
    manifest_path = Path("tmp/game_refactoring_cli_queue_pending_manifests") / f"{slugify(job_name)}.json"
    save_json(manifest_path, payload)
    return manifest_path


def ensure_ledger(jobs: list[dict[str, Any]], ledger_path: Path, config_path: str, dry_run: bool) -> dict[str, Any]:
    ledger = load_json(
        ledger_path,
        {
            "config_path": config_path,
            "mode": "direct_cli_queue",
            "current_index": 0,
            "jobs": [],
            "orchestrator": {"restarts": 0, "last_started_at": None, "last_finished_at": None},
        },
    )
    if not ledger.get("jobs"):
        ledger["jobs"] = []
        for index, job in enumerate(jobs):
            name = job.get("name") or job.get("prompt_key") or job.get("prompt") or f"job_{index}"
            ledger["jobs"].append(
                {
                    "index": index,
                    "name": name,
                    "status": "pending",
                    "started_at": None,
                    "finished_at": None,
                    "attempts": 0,
                    "attempt_history": [],
                    "active_attempt_number": None,
                    "last_attempt_dir": None,
                    "last_run_dir": None,
                    "last_status_payload": None,
                    "last_result_payload": None,
                    "failure_summary": None,
                    "pending_manifest_path": None,
                    "pending_manifest_game_count": None,
                    "prompt_key": job.get("prompt_key") or job.get("prompt"),
                }
            )
        if not dry_run:
            save_json(ledger_path, ledger)
    return ledger


def build_job_runtime(
    job: dict[str, Any],
    job_state: dict[str, Any],
    default_max_concurrency: int,
    workflow_script: str,
    default_runs_root: Path,
) -> dict[str, Any]:
    prompt_key = str(job.get("prompt_key") or job.get("prompt") or "").strip()
    if not prompt_key:
        raise ValueError("Each job must include prompt or prompt_key")

    remix_prompt = job.get("remix_prompt") or prompt_key
    workflow_id = job.get("workflow_id") or job.get("id") or "creative_remix_v4"

    base_manifest_value = job.get("manifest") or job.get("games_manifest_source")
    if base_manifest_value:
        base_manifest_path = Path(str(base_manifest_value))
    else:
        base_manifest_path = build_manifest_from_raw_game_ids(job, job_state.get("name", prompt_key))

    runs_root = Path(str(job.get("runs_root") or default_runs_root))
    pending_games, pending_summary = compute_pending_games_for_prompt(
        prompt_key=prompt_key,
        base_manifest_path=base_manifest_path,
        runs_root=runs_root,
    )
    pending_manifest_path = write_pending_manifest(
        job_name=job_state.get("name", prompt_key),
        prompt_key=prompt_key,
        base_manifest_path=base_manifest_path,
        pending_games=pending_games,
    )
    job_state["pending_manifest_path"] = str(pending_manifest_path)
    job_state["pending_manifest_game_count"] = len(pending_games)
    job_state["pending_summary"] = pending_summary

    runtime: dict[str, Any] = {
        "prompt_key": prompt_key,
        "remix_prompt": str(remix_prompt),
        "workflow_id": workflow_id,
        "base_manifest_path": str(base_manifest_path),
        "games_manifest_source": str(pending_manifest_path),
        "source_mode": job.get("source_mode", "copy"),
        "pipeline": job.get("pipeline", "v2"),
        "model": job.get("model", "gpt-5.5"),
        "agent_timeout": int(job.get("agent_timeout", 3600)),
        "max_concurrency": int(job.get("max_concurrency", default_max_concurrency)),
        "poll_seconds": float(job.get("poll_seconds", 5.0)),
        "stale_heartbeat_seconds": int(job.get("stale_heartbeat_seconds", 900)),
        "workflow_script": workflow_script,
        "runs_root": str(runs_root),
    }

    optional_fields = [
        "remix_prompt_file",
        "playwright_port_base",
        "playwright_port_pool_size",
        "playwright_port_lease_ttl_seconds",
    ]
    for key in optional_fields:
        if key in job and job[key] is not None:
            runtime[key] = job[key]

    if "dry_run_operators" in job:
        runtime["dry_run_operators"] = bool(job["dry_run_operators"])
    if "dry_run_spec_adaptor" in job:
        runtime["dry_run_spec_adaptor"] = bool(job["dry_run_spec_adaptor"])

    return runtime


def choose_attempt_manifest(job_runtime: dict[str, Any], job_state: dict[str, Any]) -> str:
    if job_state.get("attempts", 0) <= 0:
        return job_runtime["games_manifest_source"]
    attempt_history = job_state.get("attempt_history", [])
    if attempt_history:
        previous = attempt_history[-1]
        retry_manifest = previous.get("retry_manifest_path")
        if retry_manifest:
            return retry_manifest
    raise RuntimeError(f"Job {job_state.get('name')} has no retry manifest for the next attempt")


def make_attempt_dir(job_runtime: dict[str, Any], job_state: dict[str, Any], attempt_number: int) -> Path:
    runs_root = Path("tmp/game_refactoring_cli_queue_runs")
    return runs_root / slugify(job_state.get("name", "job")) / "attempts" / f"attempt_{attempt_number:02d}"


def build_run_id(job_state: dict[str, Any], attempt_number: int) -> str:
    return f"{slugify(job_state.get('name', 'job'))}_attempt_{attempt_number:02d}"


def build_attempt_command(job_runtime: dict[str, Any], manifest_path: str, run_id: str) -> list[str]:
    command = [
        "python3",
        job_runtime["workflow_script"],
        "--json",
        "--id",
        str(job_runtime["workflow_id"]),
        "--games-manifest-source",
        str(manifest_path),
        "--run-id",
        run_id,
        "--runs-root",
        str(job_runtime["runs_root"]),
        "--source-mode",
        str(job_runtime["source_mode"]),
        "--pipeline",
        str(job_runtime["pipeline"]),
        "--model",
        str(job_runtime["model"]),
        "--agent-timeout",
        str(job_runtime["agent_timeout"]),
        "--max-concurrency",
        str(job_runtime["max_concurrency"]),
        "--poll-seconds",
        str(job_runtime["poll_seconds"]),
        "--stale-heartbeat-seconds",
        str(job_runtime["stale_heartbeat_seconds"]),
    ]
    if job_runtime.get("remix_prompt"):
        command.extend(["--remix-prompt", str(job_runtime["remix_prompt"])])
    if job_runtime.get("remix_prompt_file"):
        command.extend(["--remix-prompt-file", str(job_runtime["remix_prompt_file"])])
    if job_runtime.get("playwright_port_base") is not None:
        command.extend(["--playwright-port-base", str(job_runtime["playwright_port_base"])])
    if job_runtime.get("playwright_port_pool_size") is not None:
        command.extend(["--playwright-port-pool-size", str(job_runtime["playwright_port_pool_size"])])
    if job_runtime.get("playwright_port_lease_ttl_seconds") is not None:
        command.extend(["--playwright-port-lease-ttl-seconds", str(job_runtime["playwright_port_lease_ttl_seconds"])])
    if job_runtime.get("dry_run_operators"):
        command.append("--dry-run-operators")
    if job_runtime.get("dry_run_spec_adaptor"):
        command.append("--dry-run-spec-adaptor")
    return command


def wait_for_terminal_run(run_dir: Path, poll_seconds: float, timeout_seconds: int) -> dict[str, Any]:
    run_state_path = run_dir / "run_state.json"
    started = time.time()
    last_payload: dict[str, Any] | None = None
    while True:
        if run_state_path.exists():
            run_state = load_json(run_state_path, {})
            if isinstance(run_state, dict) and run_state:
                status = run_state.get("status")
                last_payload = {
                    "run_id": run_state.get("run_id"),
                    "run_dir": str(run_dir),
                    "status": status,
                    "current_phase": run_state.get("current_phase"),
                    "updated_at": run_state.get("updated_at"),
                    "games_total": run_state.get("games_total", 0),
                    "games_transform_completed": run_state.get("games_transform_completed", 0),
                    "games_transform_failed": run_state.get("games_transform_failed", 0),
                    "completed": status in {"transform_completed", "transform_failed", "transform_incomplete"},
                    "failed": status in {"transform_failed", "transform_incomplete"},
                    "running": status not in {"transform_completed", "transform_failed", "transform_incomplete"},
                }
                if last_payload["completed"]:
                    return last_payload
        if time.time() - started > timeout_seconds:
            return {
                "run_dir": str(run_dir),
                "status": "timeout",
                "current_phase": "queue_timeout",
                "updated_at": utc_now(),
                "completed": True,
                "failed": True,
                "running": False,
                "timed_out": True,
                "last_seen": last_payload,
            }
        time.sleep(poll_seconds)


def game_failed(game_state: dict[str, Any]) -> bool:
    status = str(game_state.get("status") or "").lower()
    current_phase = str(game_state.get("current_phase") or "").lower()
    integrity_status = str(game_state.get("integrity_status") or "").lower()
    if status in {"failed", "error", "timeout"}:
        return True
    if integrity_status == "failed":
        return True
    if "failed" in current_phase or "error" in current_phase or "timeout" in current_phase:
        return True
    return False


def collect_failed_games_from_run(run_dir: Path, source_manifest_path: Path) -> list[dict[str, Any]]:
    run_state = load_json(run_dir / "run_state.json", {})
    source_manifest = ensure_games_manifest(source_manifest_path)
    source_games = ensure_list_of_dicts(source_manifest.get("games"), "games")
    source_by_id = {}
    for game in source_games:
        game_id = normalize_game_id(game)
        if game_id:
            source_by_id[game_id] = game

    failed_ids: list[str] = []
    seen: set[str] = set()
    run_games = run_state.get("games", [])
    if isinstance(run_games, list):
        for game_state in run_games:
            if not isinstance(game_state, dict):
                continue
            game_id = normalize_game_id(game_state)
            if not game_id or game_id in seen:
                continue
            if game_failed(game_state):
                failed_ids.append(game_id)
                seen.add(game_id)

    if not failed_ids:
        games_root = run_dir / "games"
        if games_root.exists():
            for game_dir in sorted(path for path in games_root.iterdir() if path.is_dir()):
                game_state_path = game_dir / "game_state.json"
                if not game_state_path.exists():
                    failed_ids.append(game_dir.name)
                    continue
                game_state = load_json(game_state_path, {})
                if isinstance(game_state, dict) and game_failed(game_state):
                    failed_ids.append(game_dir.name)

    return [source_by_id[game_id] for game_id in failed_ids if game_id in source_by_id]


def write_retry_manifest(source_manifest_path: Path, retry_games: list[dict[str, Any]], attempt_dir: Path, attempt_number: int) -> Path | None:
    if not retry_games:
        return None
    source_manifest = ensure_games_manifest(source_manifest_path)
    payload = dict(source_manifest)
    payload["games"] = retry_games
    payload["retry_context"] = {
        "source_manifest": str(source_manifest_path),
        "generated_at": utc_now(),
        "attempt_number": attempt_number,
        "games_count": len(retry_games),
    }
    retry_manifest_path = attempt_dir / f"retry_manifest_attempt_{attempt_number + 1:02d}.json"
    save_json(retry_manifest_path, payload)
    return retry_manifest_path


def finalize_attempt(
    job: dict[str, Any],
    job_state: dict[str, Any],
    attempt_state: dict[str, Any],
    poll_seconds: float,
    timeout_seconds: int,
) -> dict[str, Any]:
    run_dir = Path(attempt_state["launch_payload"]["run_dir"])
    status_payload = wait_for_terminal_run(run_dir, poll_seconds, timeout_seconds)
    result_payload = {
        "run_id": status_payload.get("run_id"),
        "status": status_payload.get("status"),
        "run_dir": str(run_dir),
        "dashboard_path": str(run_dir / "dashboard" / "index.html"),
        "output_root": str(run_dir / "output"),
        "completed": bool(status_payload.get("completed")),
    }
    if result_payload["completed"] and (run_dir / "output").exists():
        result_payload["final_output_dirs"] = sorted(str(path) for path in (run_dir / "output").iterdir() if path.is_dir())

    attempt_state["status_payload"] = status_payload
    attempt_state["result_payload"] = result_payload
    attempt_state["finished_at"] = utc_now()
    attempt_state["run_dir"] = str(run_dir)
    attempt_state["status"] = status_payload.get("status", "unknown")
    attempt_state["completed"] = bool(status_payload.get("completed"))
    attempt_state["failed"] = bool(status_payload.get("failed"))
    attempt_state["timed_out"] = bool(status_payload.get("timed_out", False))

    manifest_path = Path(attempt_state["manifest_path"])
    retry_games = collect_failed_games_from_run(run_dir, manifest_path)
    attempt_state["failed_game_ids"] = [normalize_game_id(game) for game in retry_games if normalize_game_id(game)]
    retry_manifest_path = write_retry_manifest(manifest_path, retry_games, Path(attempt_state["attempt_dir"]), int(attempt_state["attempt_number"]))
    attempt_state["retry_manifest_path"] = str(retry_manifest_path) if retry_manifest_path else None
    attempt_state["retry_games_count"] = len(retry_games)

    job_state["last_run_dir"] = str(run_dir)
    job_state["last_status_payload"] = status_payload
    job_state["last_result_payload"] = result_payload

    if not attempt_state["failed"]:
        job_state["status"] = "completed"
        job_state["finished_at"] = utc_now()
        job_state["failure_summary"] = None
        return job_state

    job_state["failure_summary"] = {
        "attempt_number": attempt_state["attempt_number"],
        "failed_game_ids": attempt_state["failed_game_ids"],
        "retry_games_count": attempt_state["retry_games_count"],
        "timed_out": attempt_state["timed_out"],
        "run_status": attempt_state["status"],
    }

    if int(job_state.get("attempts", 0)) >= int(job.get("max_attempts_per_job", 0) or 0):
        job_state["status"] = "failed"
        job_state["finished_at"] = utc_now()
        return job_state

    if attempt_state["retry_games_count"] <= 0:
        job_state["status"] = "failed"
        job_state["finished_at"] = utc_now()
        return job_state

    job_state["status"] = "pending"
    return job_state


def process_job(
    job: dict[str, Any],
    job_state: dict[str, Any],
    poll_seconds: float,
    timeout_seconds: int,
    default_max_concurrency: int,
    workflow_script: str,
    default_runs_root: Path,
    dry_run: bool,
    resume_running: bool,
    max_attempts_per_job: int,
) -> tuple[dict[str, Any], bool]:
    job_name = job_state.get("name", "unknown-job")
    log(f"processing job={job_name} status={job_state.get('status')} attempts={job_state.get('attempts', 0)}")

    if job_state["status"] == "completed":
        return job_state, True

    job["max_attempts_per_job"] = int(job.get("max_attempts_per_job", max_attempts_per_job))
    job_runtime = build_job_runtime(
        job=job,
        job_state=job_state,
        default_max_concurrency=default_max_concurrency,
        workflow_script=workflow_script,
        default_runs_root=default_runs_root,
    )

    if int(job_state.get("pending_manifest_game_count") or 0) == 0:
        job_state["status"] = "completed"
        job_state["started_at"] = job_state.get("started_at") or utc_now()
        job_state["finished_at"] = utc_now()
        job_state["failure_summary"] = None
        log(f"job={job_name} has no pending games after reconciliation; marking completed")
        return job_state, True

    if job_state["status"] == "failed":
        attempts = int(job_state.get("attempts", 0))
        if attempts >= job["max_attempts_per_job"]:
            return job_state, False
        job_state["status"] = "pending"

    if job_state["status"] == "running":
        if not resume_running:
            raise RuntimeError(f"Job {job_name} is marked running. Re-run with --resume-running.")
        attempt_history = job_state.get("attempt_history", [])
        if not attempt_history:
            raise RuntimeError(f"Job {job_name} is marked running but has no attempt history")
        active_attempt = attempt_history[-1]
        job_state = finalize_attempt(job, job_state, active_attempt, poll_seconds, timeout_seconds)
        return job_state, job_state["status"] == "completed"

    if job_state["status"] != "pending":
        raise RuntimeError(f"Unsupported job status for {job_name}: {job_state['status']}")

    attempts = int(job_state.get("attempts", 0))
    if attempts >= job["max_attempts_per_job"]:
        job_state["status"] = "failed"
        job_state["finished_at"] = utc_now()
        return job_state, False

    attempt_number = attempts + 1
    manifest_path = choose_attempt_manifest(job_runtime, job_state)
    manifest = ensure_games_manifest(Path(manifest_path))
    attempt_dir = make_attempt_dir(job_runtime, job_state, attempt_number)
    run_id = build_run_id(job_state, attempt_number)
    command = build_attempt_command(job_runtime, manifest_path, run_id)

    attempt_state: dict[str, Any] = {
        "attempt_number": attempt_number,
        "attempt_dir": str(attempt_dir),
        "manifest_path": str(manifest_path),
        "run_id": run_id,
        "games_count": len(manifest.get("games", [])),
        "command": command,
        "started_at": utc_now(),
        "finished_at": None,
        "launch_payload": None,
        "status_payload": None,
        "result_payload": None,
        "status": "launch_pending",
        "failed": False,
        "timed_out": False,
        "retry_manifest_path": None,
        "retry_games_count": 0,
        "failed_game_ids": [],
    }

    if dry_run:
        job_state["status"] = "dry_run_pending_submit"
        job_state["active_attempt_number"] = attempt_number
        job_state["last_attempt_dir"] = str(attempt_dir)
        job_state.setdefault("attempt_history", []).append(attempt_state)
        return job_state, False

    attempt_dir.mkdir(parents=True, exist_ok=True)
    save_json(
        attempt_dir / "launch_request.json",
        {
            "generated_at": utc_now(),
            "job_name": job_name,
            "prompt_key": job_runtime["prompt_key"],
            "pending_manifest_path": job_state.get("pending_manifest_path"),
            "manifest_path": manifest_path,
            "command": command,
            "attempt_number": attempt_number,
            "games_count": attempt_state["games_count"],
        },
    )

    completed = subprocess.run(command, text=True, capture_output=True)
    (attempt_dir / "launcher_stdout.json").write_text(completed.stdout or "", encoding="utf-8")
    (attempt_dir / "launcher_stderr.txt").write_text(completed.stderr or "", encoding="utf-8")

    if completed.returncode != 0:
        attempt_state["status"] = "launch_failed"
        attempt_state["failed"] = True
        attempt_state["finished_at"] = utc_now()
        attempt_state["launcher_returncode"] = completed.returncode
        save_json(attempt_dir / "attempt_state.json", attempt_state)
        job_state.setdefault("attempt_history", []).append(attempt_state)
        job_state["attempts"] = attempt_number
        job_state["active_attempt_number"] = attempt_number
        job_state["last_attempt_dir"] = str(attempt_dir)
        job_state["status"] = "failed" if attempt_number >= job["max_attempts_per_job"] else "pending"
        job_state["failure_summary"] = {
            "attempt_number": attempt_number,
            "launch_failed": True,
            "launcher_returncode": completed.returncode,
            "retry_games_count": 0,
        }
        if job_state["status"] == "failed":
            job_state["finished_at"] = utc_now()
        return job_state, False

    try:
        launch_payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Job {job_name} produced non-JSON workflow output: {exc}") from exc

    attempt_state["launch_payload"] = launch_payload
    attempt_state["launcher_returncode"] = completed.returncode
    attempt_state["status"] = "running"
    job_state.setdefault("attempt_history", []).append(attempt_state)
    job_state["attempts"] = attempt_number
    job_state["active_attempt_number"] = attempt_number
    job_state["last_attempt_dir"] = str(attempt_dir)
    job_state["status"] = "running"
    if not job_state.get("started_at"):
        job_state["started_at"] = utc_now()

    save_json(attempt_dir / "launch_payload.json", launch_payload)
    job_state = finalize_attempt(job, job_state, attempt_state, poll_seconds, timeout_seconds)
    save_json(attempt_dir / "attempt_state.json", attempt_state)

    if job_state["status"] == "completed":
        return job_state, True
    return job_state, False


def run_queue_once(args: argparse.Namespace) -> int:
    config_path = Path(args.config)
    ledger_path = Path(args.ledger_path)
    default_runs_root = Path(args.runs_root)

    config = load_json(config_path, None)
    if isinstance(config, list):
        config = {"jobs": config}
    if not isinstance(config, dict):
        raise SystemExit("Config must be a JSON object or a top-level JSON array of jobs")

    jobs = config.get("jobs")
    if not isinstance(jobs, list) or not jobs:
        raise SystemExit("Config must contain non-empty jobs")

    ledger = ensure_ledger(jobs, ledger_path, str(config_path), args.dry_run)
    ledger.setdefault("orchestrator", {})
    ledger["orchestrator"]["last_started_at"] = utc_now()
    current_index = int(ledger.get("current_index", 0))

    for index in range(current_index, len(jobs)):
        job = jobs[index]
        job_state = ledger["jobs"][index]
        updated_state, success = process_job(
            job=job,
            job_state=job_state,
            poll_seconds=args.poll_seconds,
            timeout_seconds=args.timeout_seconds,
            default_max_concurrency=args.max_concurrency,
            workflow_script=args.workflow_script,
            default_runs_root=default_runs_root,
            dry_run=args.dry_run,
            resume_running=args.resume_running,
            max_attempts_per_job=args.max_attempts_per_job,
        )
        ledger["jobs"][index] = updated_state

        if success:
            ledger["current_index"] = index + 1
        elif args.dry_run:
            pass
        else:
            ledger["orchestrator"]["last_finished_at"] = utc_now()
            save_json(ledger_path, ledger)
            print(json.dumps({"ledger": ledger}, indent=2))
            return 1

        if not args.dry_run:
            save_json(ledger_path, ledger)

        if args.dry_run:
            print(json.dumps({"ledger": ledger}, indent=2))
            return 0

    ledger["orchestrator"]["last_finished_at"] = utc_now()
    print(json.dumps({"ledger": ledger}, indent=2))
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return run_queue_once(args)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))