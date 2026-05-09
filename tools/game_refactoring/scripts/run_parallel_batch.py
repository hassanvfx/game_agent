#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.port_lease_service import (
    DEFAULT_LEASE_TTL_SECONDS,
    DEFAULT_POOL_SIZE,
    DEFAULT_PORT_BASE,
    acquire_port_lease,
    release_port_lease,
    shared_port_state_path_for_run_dir,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POLL_SECONDS = 5.0
DEFAULT_STYLE_ID = "neutral_prototype"
DEBUG_TRACE_FILENAME = "run_parallel_batch_debug_trace.log"


@dataclass
class ActiveWorker:
    game_id: str
    process: subprocess.Popen[str]
    launched_at: str
    leased_port: int
    lease_state_path: Path
    lease_owner_pid: int


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_utc(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def append_debug_trace(trace_path: Path, message: str) -> None:
    trace_path.parent.mkdir(parents=True, exist_ok=True)
    with trace_path.open("a", encoding="utf-8") as handle:
        handle.write(f"[{utc_now()}] {message}\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a bounded parallel Game Remixer batch.")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--run-id")
    parser.add_argument("--run-dir")
    parser.add_argument("--runs-root")
    parser.add_argument("--model", default="gpt-5.4")
    parser.add_argument("--agent-timeout", type=int, default=3600)
    parser.add_argument("--max-concurrency", type=int, default=2)
    parser.add_argument("--poll-seconds", type=float, default=DEFAULT_POLL_SECONDS)
    parser.add_argument("--stale-heartbeat-seconds", type=int, default=900)
    parser.add_argument("--style", default=DEFAULT_STYLE_ID)
    parser.add_argument("--remix-prompt")
    parser.add_argument("--remix-prompt-file")
    parser.add_argument("--playwright-port-base", type=int, default=DEFAULT_PORT_BASE)
    parser.add_argument("--playwright-port-pool-size", type=int, default=DEFAULT_POOL_SIZE)
    parser.add_argument("--playwright-port-lease-ttl-seconds", type=int, default=DEFAULT_LEASE_TTL_SECONDS)
    return parser.parse_args()


def run_python(*args: str, trace_path: Path | None = None) -> str:
    command = ["python3", *args]
    if trace_path is not None:
        append_debug_trace(trace_path, f"Running helper command: {json.dumps(command)}")
    completed = subprocess.run(command, check=True, capture_output=True, text=True)
    if trace_path is not None:
        append_debug_trace(
            trace_path,
            f"Helper command completed: returncode={completed.returncode}, stdout_chars={len(completed.stdout)}, stderr_chars={len(completed.stderr)}",
        )
        if completed.stdout.strip():
            append_debug_trace(trace_path, f"Helper stdout: {completed.stdout.strip()[:1000]}")
        if completed.stderr.strip():
            append_debug_trace(trace_path, f"Helper stderr: {completed.stderr.strip()[:1000]}")
    return completed.stdout.strip()


def resolve_remix_prompt(args: argparse.Namespace) -> str | None:
    if args.remix_prompt and args.remix_prompt_file:
        raise ValueError("Pass only one of --remix-prompt or --remix-prompt-file.")
    if args.remix_prompt_file:
        return Path(args.remix_prompt_file).read_text(encoding="utf-8").strip()
    if args.remix_prompt:
        return args.remix_prompt.strip()
    return None


def run_spec_adaptor(run_dir: Path, style: str, remix_prompt: str, trace_path: Path | None = None) -> None:
    try:
        run_python(
            str(ROOT / "scripts" / "spec_adaptor.py"),
            "--run-dir",
            str(run_dir),
            "--style",
            style,
            "--remix-prompt",
            remix_prompt,
            trace_path=trace_path,
        )
    except subprocess.CalledProcessError as error:
        if trace_path is not None:
            append_debug_trace(trace_path, f"run_spec_adaptor() failed with returncode={error.returncode}")
            if error.stdout:
                append_debug_trace(trace_path, f"run_spec_adaptor stdout: {error.stdout.strip()[:1000]}")
            if error.stderr:
                append_debug_trace(trace_path, f"run_spec_adaptor stderr: {error.stderr.strip()[:1000]}")
        job_state_path = run_dir / "spec_adaptor" / "spec_adaptor_job_state.json"
        if job_state_path.exists() and trace_path is not None:
            append_debug_trace(trace_path, f"Spec adaptor job state available at {job_state_path}")
        raise


def release_worker_lease(worker: ActiveWorker, trace_path: Path | None = None) -> None:
    released = release_port_lease(worker.lease_state_path, port=worker.leased_port, owner_pid=worker.lease_owner_pid)
    if not released:
        released = release_port_lease(worker.lease_state_path, port=worker.leased_port)
    if trace_path is not None:
        append_debug_trace(
            trace_path,
            f"Lease release owner context for game_id={worker.game_id}: lease_owner_pid={worker.lease_owner_pid} worker_pid={worker.process.pid} lease_state_path={worker.lease_state_path}",
        )
        append_debug_trace(
            trace_path,
            f"Released leased playwright port for game_id={worker.game_id} pid={worker.process.pid} port={worker.leased_port} released={released}",
        )


def launch_worker(
    run_dir: Path,
    game_id: str,
    model: str,
    timeout: int,
    style: str,
    remix_prompt: str | None,
    lease_state_path: Path,
    playwright_port: int,
    lease_owner_pid: int,
    trace_path: Path | None = None,
) -> ActiveWorker:
    process = subprocess.Popen(
        [
            sys.executable,
            str(ROOT / "scripts" / "run_single_game.py"),
            "--run-dir",
            str(run_dir),
            "--game-id",
            game_id,
            "--model",
            model,
            "--agent-timeout",
            str(timeout),
            "--style",
            style,
            "--playwright-port",
            str(playwright_port),
            *(
                ["--remix-prompt", remix_prompt]
                if remix_prompt
                else []
            ),
            "--skip-run-state-update",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        text=True,
        start_new_session=True,
    )
    worker = ActiveWorker(
        game_id=game_id,
        process=process,
        launched_at=utc_now(),
        leased_port=playwright_port,
        lease_state_path=lease_state_path,
        lease_owner_pid=lease_owner_pid,
    )
    if trace_path is not None:
        append_debug_trace(
            trace_path,
            f"Launched worker for game_id={game_id} pid={process.pid} timeout={timeout} style={style} remix_prompt_present={bool(remix_prompt)} playwright_port={playwright_port}",
        )
    return worker


def current_job_state_path(run_dir: Path, game_id: str) -> Path:
    return run_dir / "games" / game_id / "attempts" / "attempt_0001" / "job_state.json"


def current_game_state_path(run_dir: Path, game_id: str) -> Path:
    return run_dir / "games" / game_id / "game_state.json"


def terminate_worker(process: subprocess.Popen[str], graceful_seconds: float = 10.0) -> None:
    if process.poll() is not None:
        return

    try:
        process.send_signal(signal.SIGTERM)
        deadline = time.monotonic() + graceful_seconds
        while time.monotonic() < deadline:
            if process.poll() is not None:
                return
            time.sleep(0.2)
    except ProcessLookupError:
        return

    if process.poll() is not None:
        return

    try:
        process.kill()
    except ProcessLookupError:
        return


def finalize_stale_worker(run_dir: Path, worker: ActiveWorker, stale_gap_seconds: int) -> None:
    ended_at = utc_now()
    game_state_path = current_game_state_path(run_dir, worker.game_id)
    game_state = load_json(game_state_path)
    game_state["attempt_count"] = 1
    game_state["status"] = "failed"
    game_state["current_phase"] = "creative_refactor_failed"
    game_state["creative_phase"] = "creative_refactor_failed"
    game_state["creative_status"] = "failed"
    game_state["last_error"] = f"Creative refactor worker became stale after {stale_gap_seconds} seconds without heartbeat."
    game_state["updated_at"] = ended_at
    write_json(game_state_path, game_state)

    job_state_path = current_job_state_path(run_dir, worker.game_id)
    if job_state_path.exists():
        job_state = load_json(job_state_path)
    else:
        attempt_dir = job_state_path.parent
        job_state = {
            "job_id": f"{worker.game_id}_creative_refactor_attempt_0001",
            "job_type": "creative_refactor",
            "status": "running",
            "owner_game_id": worker.game_id,
            "attempt_number": 1,
            "heartbeat_at": worker.launched_at,
            "started_at": worker.launched_at,
            "finished_at": None,
            "result_path": None,
            "stdout_path": str(attempt_dir / "creative_refactor_stdout.txt"),
            "stderr_path": str(attempt_dir / "creative_refactor_stderr.txt"),
            "artifacts_manifest_path": str(attempt_dir / "artifacts_manifest.json"),
            "failure_reason": None,
            "timeout_seconds": None,
            "forced_mode": None,
        }
    job_state["status"] = "failed"
    job_state["failure_reason"] = "stale_heartbeat"
    job_state["heartbeat_at"] = job_state.get("heartbeat_at") or job_state.get("started_at") or worker.launched_at
    job_state["finished_at"] = ended_at
    write_json(job_state_path, job_state)

    run_state_path = run_dir / "run_state.json"
    run_state = load_json(run_state_path)
    run_state["games_transform_failed"] += 1
    run_state["updated_at"] = ended_at
    run_state.setdefault("notes", []).append(
        f"{worker.game_id} marked failed due to stale heartbeat ({stale_gap_seconds}s); worker terminated."
    )
    write_json(run_state_path, run_state)


def initialize_run_status(run_dir: Path, max_concurrency: int, stale_heartbeat_seconds: int, style: str, remix_prompt: str | None) -> None:
    run_state_path = run_dir / "run_state.json"
    run_state = load_json(run_state_path)
    run_state["status"] = "running"
    run_state["current_phase"] = "parallel_batch_running"
    run_state["selected_style_id"] = style
    run_state["remix_prompt"] = remix_prompt
    run_state["updated_at"] = utc_now()
    notes = run_state.setdefault("notes", [])
    notes.append(f"Bounded parallel extracted batch started (max_concurrency={max_concurrency}, style={style}).")
    notes.append(f"Stale heartbeat cutoff enabled at {stale_heartbeat_seconds} seconds.")
    write_json(run_state_path, run_state)


def finalize_run_status(run_dir: Path, style: str, remix_prompt: str | None) -> None:
    run_state_path = run_dir / "run_state.json"
    run_state = load_json(run_state_path)
    if run_state["games_transform_failed"] == 0 and run_state["games_transform_completed"] == run_state["games_total"]:
        run_state["status"] = "transform_completed"
    elif run_state["games_transform_completed"] + run_state["games_transform_failed"] == run_state["games_total"]:
        run_state["status"] = "transform_failed"
    else:
        run_state["status"] = "transform_incomplete"
    run_state["current_phase"] = "parallel_batch_finished"
    run_state["selected_style_id"] = style
    run_state["remix_prompt"] = remix_prompt
    notes = run_state.setdefault("notes", [])
    final_note = f"Bounded parallel extracted batch finished using style {style}."
    if final_note not in notes:
        notes.append(final_note)
    run_state["updated_at"] = utc_now()
    write_json(run_state_path, run_state)


def main() -> None:
    args = parse_args()
    remix_prompt = resolve_remix_prompt(args)

    run_dir = Path(args.run_dir).resolve() if args.run_dir else (ROOT / "runs" / args.run_id if args.run_id else None)
    if run_dir is not None and run_dir.exists():
        trace_path = run_dir / DEBUG_TRACE_FILENAME
        source_label = "--run-dir" if args.run_dir else "--run-id"
        append_debug_trace(trace_path, f"Reusing existing run_dir={run_dir} supplied via {source_label}")
    else:
        create_cmd = [str(ROOT / "scripts" / "create_run.py"), "--manifest", args.manifest]
        if args.run_id:
            create_cmd.extend(["--run-id", args.run_id])
        if args.runs_root:
            create_cmd.extend(["--runs-root", args.runs_root])
        run_dir = Path(run_python(*create_cmd))
        trace_path = run_dir / DEBUG_TRACE_FILENAME
        append_debug_trace(trace_path, f"Created run_dir={run_dir} via create_run.py")
    append_debug_trace(trace_path, f"run_parallel_batch.py starting for run_dir={run_dir}")
    lease_state_path = shared_port_state_path_for_run_dir(run_dir)
    append_debug_trace(
        trace_path,
        f"Arguments: manifest={args.manifest}, run_id={args.run_id}, run_dir={args.run_dir}, runs_root={args.runs_root}, model={args.model}, agent_timeout={args.agent_timeout}, max_concurrency={args.max_concurrency}, poll_seconds={args.poll_seconds}, stale_heartbeat_seconds={args.stale_heartbeat_seconds}, style={args.style}, remix_prompt_present={bool(remix_prompt)} playwright_port_base={args.playwright_port_base} playwright_port_pool_size={args.playwright_port_pool_size} playwright_port_lease_ttl_seconds={args.playwright_port_lease_ttl_seconds} lease_state_path={lease_state_path}",
    )

    append_debug_trace(trace_path, "Starting prepare_inputs.py")
    run_python(str(ROOT / "scripts" / "prepare_inputs.py"), "--run-dir", str(run_dir), trace_path=trace_path)
    append_debug_trace(trace_path, "prepare_inputs.py completed successfully")
    if remix_prompt:
        append_debug_trace(trace_path, "Starting run_spec_adaptor()")
        try:
            run_spec_adaptor(run_dir, args.style, remix_prompt, trace_path=trace_path)
            append_debug_trace(trace_path, "run_spec_adaptor() completed successfully")
        except subprocess.CalledProcessError:
            append_debug_trace(trace_path, "Aborting batch because spec adaptation failed before worker launch")
            raise
    append_debug_trace(trace_path, "Initializing run status for parallel execution")
    initialize_run_status(run_dir, args.max_concurrency, args.stale_heartbeat_seconds, args.style, remix_prompt)
    append_debug_trace(trace_path, "Run status initialized")
    run_python(str(ROOT / "scripts" / "build_dashboard.py"), "--run-dir", str(run_dir), trace_path=trace_path)
    run_python(str(ROOT / "scripts" / "write_dashboard_launcher.py"), "--run-dir", str(run_dir), trace_path=trace_path)

    manifest = load_json(run_dir / "input_manifest.json")
    pending = [game["game_id"] for game in manifest.get("games", [])]
    active: dict[str, ActiveWorker] = {}
    append_debug_trace(trace_path, f"Loaded manifest with pending game_ids={pending}")

    while pending or active:
        while pending and len(active) < args.max_concurrency:
            game_id = pending.pop(0)
            append_debug_trace(trace_path, f"Scheduling next worker for game_id={game_id}; active={list(active)} pending_remaining={len(pending)}")
            port_lease = acquire_port_lease(
                lease_state_path,
                owner_pid=os.getpid(),
                owner_label=f"run_parallel_batch:{run_dir.name}:{game_id}",
                port_base=args.playwright_port_base,
                pool_size=args.playwright_port_pool_size,
                lease_ttl_seconds=args.playwright_port_lease_ttl_seconds,
            )
            append_debug_trace(
                trace_path,
                f"Acquired leased playwright port for game_id={game_id} port={port_lease.port} lease_id={port_lease.lease_id} lease_owner_pid={port_lease.owner_pid} lease_state_path={port_lease.state_path} localhost_url={port_lease.localhost_url}",
            )
            active[game_id] = launch_worker(
                run_dir,
                game_id,
                args.model,
                args.agent_timeout,
                args.style,
                remix_prompt,
                lease_state_path,
                port_lease.port,
                lease_owner_pid=port_lease.owner_pid,
                trace_path=trace_path,
            )

        finished: list[str] = []
        for game_id, worker in list(active.items()):
            return_code = worker.process.poll()
            if return_code is not None:
                append_debug_trace(trace_path, f"Worker process exited for game_id={game_id} with return_code={return_code}")
                finished.append(game_id)
                continue

            job_state_path = current_job_state_path(run_dir, game_id)
            if not job_state_path.exists():
                continue

            job_state = load_json(job_state_path)
            heartbeat = parse_utc(job_state.get("heartbeat_at"))
            if heartbeat is None:
                continue

            gap = (datetime.now(timezone.utc) - heartbeat).total_seconds()
            if gap > args.stale_heartbeat_seconds:
                append_debug_trace(trace_path, f"Worker stale heartbeat detected for game_id={game_id}; gap={gap:.1f}s")
                terminate_worker(worker.process)
                finalize_stale_worker(run_dir, worker, int(gap))
                finished.append(game_id)

        if finished:
            append_debug_trace(trace_path, f"Processing finished workers: {finished}")
            run_state_path = run_dir / "run_state.json"
            run_state = load_json(run_state_path)
            for game_id in finished:
                worker = active.pop(game_id, None)
                if worker is not None:
                    release_worker_lease(worker, trace_path=trace_path)
                game_state = load_json(current_game_state_path(run_dir, game_id))
                if game_state["status"] == "completed":
                    run_state["games_transform_completed"] += 1
                    run_state.setdefault("notes", []).append(
                        f"{game_id} creative transform completed in extracted remixer using style {args.style}."
                    )
                elif game_state["status"] == "failed":
                    if current_job_state_path(run_dir, game_id).exists():
                        job_state = load_json(current_job_state_path(run_dir, game_id))
                        if job_state.get("failure_reason") != "stale_heartbeat":
                            run_state["games_transform_failed"] += 1
                    else:
                        run_state["games_transform_failed"] += 1
                    run_state.setdefault("notes", []).append(
                        f"{game_id} creative transform failed in extracted remixer using style {args.style}."
                    )
            run_state["status"] = "running"
            run_state["current_phase"] = "parallel_batch_running"
            run_state["selected_style_id"] = args.style
            run_state["remix_prompt"] = remix_prompt
            run_state["updated_at"] = utc_now()
            write_json(run_state_path, run_state)
            append_debug_trace(
                trace_path,
                f"Run state updated after finished workers; completed={run_state['games_transform_completed']} failed={run_state['games_transform_failed']} active={list(active)} pending_remaining={len(pending)}",
            )
            run_python(str(ROOT / "scripts" / "build_dashboard.py"), "--run-dir", str(run_dir), trace_path=trace_path)
        if pending or active:
            append_debug_trace(trace_path, f"Polling sleep with active={list(active)} pending_remaining={len(pending)}")
            time.sleep(max(0.2, args.poll_seconds))

    append_debug_trace(trace_path, "No pending or active workers remain; finalizing run status")
    finalize_run_status(run_dir, args.style, remix_prompt)
    run_python(str(ROOT / "scripts" / "build_dashboard.py"), "--run-dir", str(run_dir), trace_path=trace_path)
    append_debug_trace(trace_path, f"run_parallel_batch.py completed successfully for run_dir={run_dir}")
    print(run_dir)


if __name__ == "__main__":
    main()