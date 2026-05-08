#!/usr/bin/env python3
"""Observable game generation pipeline orchestrator."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import signal
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parent.parent
PIPELINE_RUNS_DIR = ROOT / "pipeline_runs"
PIPELINE_OUTPUTS_DIR = ROOT / "output"

GAME_MATCHER_ROOT = ROOT.parent / "game_matcher"
GAME_REMIXER_ROOT = ROOT.parent / "game_remixer"
GAME_REMIX_EDITOR_ROOT = ROOT.parent / "game_remix_editor"
GAME_OBFUSCATOR_ROOT = ROOT.parent / "game_obfuscator"

DEFAULT_MATCHER_LIMIT = 2
DEFAULT_POLL_SECONDS = 60.0
LAUNCH_TIMEOUT_SECONDS = 120
REMIX_EDITOR_LAUNCH_TIMEOUT_SECONDS = 900
INITIAL_GLOBAL_WATCHDOG_SECONDS = 3600
FINAL_GLOBAL_WATCHDOG_SECONDS = 7200
ASYNC_STAGE_ATTEMPT_TIMEOUTS = (900, 1800, 3600)
FINAL_TERMINAL_STATES = {"completed", "failed"}
REMIX_EDITOR_TERMINAL_STATUSES = {
    "transform_completed",
    "transform_failed",
    "transform_incomplete",
}
OBFUSCATOR_TERMINAL_STATUSES = {
    "completed",
    "completed_with_failures",
    "failed",
    "stalled",
}


@dataclass
class StepError(RuntimeError):
    step: str
    message: str
    details: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        super().__init__(self.message)


@dataclass
class CompletedCommand:
    args: list[str]
    cwd: Path
    exit_code: int
    stdout: str
    stderr: str
    started_at: str
    completed_at: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "args": self.args,
            "cwd": str(self.cwd),
            "exit_code": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
        }


class PipelineRun:
    """Persists run state, events, and artifact files for observability."""

    def __init__(self, run_id: str, prompt: str, obfuscate: bool, poll_seconds: float) -> None:
        self.run_id = run_id
        self.run_dir = PIPELINE_RUNS_DIR / run_id
        self.prompt = prompt
        self.obfuscate = obfuscate
        self.poll_seconds = poll_seconds
        self.input_dir = self.run_dir / "input"
        self.matcher_dir = self.run_dir / "matcher"
        self.remixer_dir = self.run_dir / "remixer"
        self.remix_editor_dir = self.run_dir / "remix_editor"
        self.obfuscator_dir = self.run_dir / "obfuscator"
        self.final_dir = self.run_dir / "final"
        self.logs_dir = self.run_dir / "logs"
        self.dashboard_dir = self.run_dir / "dashboard"
        self.events_path = self.run_dir / "events.jsonl"
        self.run_state_path = self.run_dir / "run_state.json"
        self.dashboard_data_path = self.dashboard_dir / "dashboard_data.json"
        self.log_path = self.logs_dir / "orchestrator.log"

        self.run_dir.mkdir(parents=True, exist_ok=False)
        for path in (
            self.input_dir,
            self.matcher_dir,
            self.remixer_dir,
            self.remix_editor_dir,
            self.obfuscator_dir,
            self.final_dir,
            self.logs_dir,
            self.dashboard_dir,
        ):
            path.mkdir(parents=True, exist_ok=True)

        now = utc_now()
        self.state: dict[str, Any] = {
            "run_id": run_id,
            "prompt": prompt,
            "status": "running",
            "current_step": "initializing",
            "started_at": now,
            "updated_at": now,
            "obfuscation_enabled": obfuscate,
            "poll_seconds": poll_seconds,
            "global_watchdog_seconds": INITIAL_GLOBAL_WATCHDOG_SECONDS,
            "global_watchdog_deadline": iso_after_seconds(INITIAL_GLOBAL_WATCHDOG_SECONDS),
            "steps": {
                "matcher": {"status": "pending"},
                "remixer_lookup": {"status": "pending"},
                "remix_editor": {"status": "pending"},
                "obfuscator": {"status": "pending" if obfuscate else "skipped"},
                "finalize": {"status": "pending"},
            },
            "artifacts": {
                "run_dir": str(self.run_dir),
                "events_path": str(self.events_path),
                "dashboard_path": str(self.dashboard_dir / "index.html"),
            },
            "final_output_dir": None,
            "final_output_dirs": [],
            "error": None,
        }

        self.write_text(self.input_dir / "prompt.txt", prompt)
        self._write_log(f"[{now}] run initialized: {run_id}")
        self.append_event("system", "run_initialized", {"prompt": prompt, "obfuscate": obfuscate})
        self.save_state()

    def set_current_step(self, step: str) -> None:
        self.state["current_step"] = step
        self.state["updated_at"] = utc_now()
        self.save_state()

    def start_step(self, step: str, extra: dict[str, Any] | None = None) -> None:
        now = utc_now()
        payload = {"status": "running", "started_at": now}
        if extra:
            payload.update(extra)
        self.state["steps"][step] = {**self.state["steps"].get(step, {}), **payload}
        self.state["current_step"] = step
        self.state["updated_at"] = now
        self.append_event(step, "started", extra or {})
        self.save_state()

    def complete_step(self, step: str, extra: dict[str, Any] | None = None) -> None:
        now = utc_now()
        payload = {"status": "completed", "completed_at": now}
        if extra:
            payload.update(extra)
        self.state["steps"][step] = {**self.state["steps"].get(step, {}), **payload}
        self.state["updated_at"] = now
        self.append_event(step, "completed", extra or {})
        self.save_state()

    def fail_step(self, step: str, message: str, details: dict[str, Any] | None = None) -> None:
        now = utc_now()
        payload = {
            "status": "failed",
            "completed_at": now,
            "error": {
                "message": message,
                "details": details or {},
            },
        }
        self.state["steps"][step] = {**self.state["steps"].get(step, {}), **payload}
        self.state["status"] = "failed"
        self.state["current_step"] = step
        self.state["updated_at"] = now
        self.state["error"] = {"step": step, "message": message, "details": details or {}}
        self.append_event(step, "failed", {"message": message, "details": details or {}}, level="error")
        self.save_state()

    def skip_step(self, step: str, reason: str) -> None:
        now = utc_now()
        self.state["steps"][step] = {
            **self.state["steps"].get(step, {}),
            "status": "skipped",
            "completed_at": now,
            "reason": reason,
        }
        self.state["updated_at"] = now
        self.append_event(step, "skipped", {"reason": reason})
        self.save_state()

    def mark_completed(self, final_output_dir: Path, final_output_dirs: list[str] | None = None) -> None:
        now = utc_now()
        self.state["status"] = "completed"
        self.state["current_step"] = "done"
        self.state["updated_at"] = now
        self.state["completed_at"] = now
        self.state["final_output_dir"] = str(final_output_dir)
        if final_output_dirs is not None:
            self.state["final_output_dirs"] = final_output_dirs
        self.append_event(
            "system",
            "run_completed",
            {
                "final_output_dir": str(final_output_dir),
                "final_output_dirs": final_output_dirs or [str(final_output_dir)],
            },
        )
        self.save_state()

    def append_event(
        self,
        step: str,
        event: str,
        details: dict[str, Any] | None = None,
        *,
        level: str = "info",
    ) -> None:
        payload = {
            "ts": utc_now(),
            "level": level,
            "step": step,
            "event": event,
            "details": details or {},
        }
        with self.events_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload) + "\n")
        self._write_log(json.dumps(payload))

    def save_state(self) -> None:
        self.state["updated_at"] = utc_now()
        write_json(self.run_state_path, self.state)
        dashboard_data = self.build_dashboard_data()
        write_json(self.dashboard_data_path, dashboard_data)
        ensure_dashboard_html(self.dashboard_dir / "index.html")

    def build_dashboard_data(self) -> dict[str, Any]:
        recent_events = read_recent_events(self.events_path, limit=25)
        steps = []
        for step_id, step_state in self.state["steps"].items():
            steps.append(
                {
                    "id": step_id,
                    "label": step_id.replace("_", " ").title(),
                    "status": step_state.get("status", "unknown"),
                    "details": step_state,
                }
            )
        return {
            "run_id": self.run_id,
            "prompt": self.prompt,
            "status": self.state["status"],
            "current_step": self.state["current_step"],
            "updated_at": self.state["updated_at"],
            "started_at": self.state["started_at"],
            "obfuscation_enabled": self.obfuscate,
            "steps": steps,
            "recent_events": recent_events,
            "links": self.state["artifacts"]
            | {
                "final_output_dir": self.state["final_output_dir"],
                "final_output_dirs": self.state.get("final_output_dirs", []),
            },
            "error": self.state["error"],
        }

    def write_text(self, path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def write_command_artifacts(self, step_dir: Path, name: str, command: CompletedCommand) -> None:
        write_json(step_dir / f"{name}.command.json", command.to_dict())
        self.write_text(step_dir / f"{name}.stdout.txt", command.stdout)
        self.write_text(step_dir / f"{name}.stderr.txt", command.stderr)

    def _write_log(self, line: str) -> None:
        with self.log_path.open("a", encoding="utf-8") as handle:
            handle.write(line.rstrip() + "\n")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def iso_after_seconds(seconds: int) -> str:
    return (datetime.now(timezone.utc).replace(microsecond=0) + timedelta(seconds=seconds)).isoformat()


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_recent_events(path: Path, limit: int = 25) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in lines[-limit:]][::-1]


def generate_run_id() -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"run_pipeline_{timestamp}"


def execute_command(args: list[str], cwd: Path) -> CompletedCommand:
    started_at = utc_now()
    completed = subprocess.run(args, cwd=str(cwd), capture_output=True, text=True)
    completed_at = utc_now()
    return CompletedCommand(
        args=args,
        cwd=cwd,
        exit_code=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
        started_at=started_at,
        completed_at=completed_at,
    )


def execute_command_with_timeout(args: list[str], cwd: Path, timeout_seconds: int) -> CompletedCommand:
    started_at = utc_now()
    try:
        completed = subprocess.run(
            args,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
        exit_code = completed.returncode
        stdout = completed.stdout
        stderr = completed.stderr
    except subprocess.TimeoutExpired as exc:
        completed_at = utc_now()
        raise StepError(
            "system",
            "launch command timed out",
            {
                "args": args,
                "cwd": str(cwd),
                "timeout_seconds": timeout_seconds,
                "stdout": exc.stdout or "",
                "stderr": exc.stderr or "",
                "started_at": started_at,
                "completed_at": completed_at,
            },
        ) from exc

    completed_at = utc_now()
    return CompletedCommand(
        args=args,
        cwd=cwd,
        exit_code=exit_code,
        stdout=stdout,
        stderr=stderr,
        started_at=started_at,
        completed_at=completed_at,
    )


def parse_matcher_output(stdout: str) -> list[dict[str, Any]]:
    decoder = json.JSONDecoder()
    text = stdout.strip()
    if not text:
        raise ValueError("matcher stdout was empty")
    payload = None
    last_error: Exception | None = None
    for start in range(len(text)):
        if text[start] not in "[{":
            continue
        try:
            candidate, _ = decoder.raw_decode(text[start:])
            payload = candidate
            break
        except json.JSONDecodeError as exc:
            last_error = exc
    if payload is None:
        raise ValueError(f"unable to decode matcher JSON from stdout: {last_error}") from last_error

    if isinstance(payload, dict):
        for key in ("results", "matches", "items"):
            value = payload.get(key)
            if isinstance(value, list):
                return value
        raise ValueError("matcher JSON object did not contain results/matches/items list")
    if isinstance(payload, list):
        return payload
    raise ValueError("matcher JSON payload was neither a list nor an object with results")


def extract_game_id(item: dict[str, Any]) -> str:
    for key in ("game_id", "id", "gameId"):
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
        if isinstance(value, int):
            return str(value)
    raise ValueError(f"match item missing usable game id: {item}")


def extract_game_url(item: dict[str, Any]) -> str:
    for key in ("url", "game_url", "gameUrl", "source_url", "sourceUrl"):
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    raise ValueError(f"match item missing usable url: {item}")


def normalize_selected_match(item: dict[str, Any]) -> dict[str, str]:
    return {
        "game_id": extract_game_id(item),
        "url": extract_game_url(item),
        "name": str(item.get("name") or item.get("title") or extract_game_id(item)),
    }


def run_matcher(pipeline: PipelineRun, prompt: str, limit: int) -> list[dict[str, str]]:
    pipeline.start_step("matcher", {"prompt": prompt, "limit": limit})
    command = execute_command(
        ["python3", "cli/game_matcher_cli.py", prompt, "--limit", str(limit)],
        GAME_MATCHER_ROOT,
    )
    pipeline.write_command_artifacts(pipeline.matcher_dir, "matcher", command)

    if command.exit_code != 0:
        raise StepError(
            "matcher",
            "matcher command failed",
            {"exit_code": command.exit_code, "stderr_path": str(pipeline.matcher_dir / "matcher.stderr.txt")},
        )

    matches = parse_matcher_output(command.stdout)
    if len(matches) < 2:
        raise StepError("matcher", "matcher returned fewer than two matches", {"match_count": len(matches)})

    try:
        selected_matches = [normalize_selected_match(match) for match in matches[:2]]
    except ValueError as exc:
        raise StepError("matcher", "matcher results missing usable game fields", {"message": str(exc)}) from exc

    write_json(
        pipeline.matcher_dir / "parsed_matches.json",
        {"matches": matches, "selected_matches": selected_matches},
    )
    pipeline.complete_step(
        "matcher",
        {"selected_game_ids": [item["game_id"] for item in selected_matches], "match_count": len(matches)},
    )
    return selected_matches


def resolve_game_with_remixer(pipeline: PipelineRun, match: dict[str, str], slot: int) -> dict[str, str]:
    game_id = match["game_id"]
    url = match["url"]
    command = execute_command(["./get_game", "--url", url, "--game-id", game_id], GAME_REMIXER_ROOT)
    base_name = f"game_{slot}_get_game"
    pipeline.write_command_artifacts(pipeline.remixer_dir, base_name, command)

    if command.exit_code != 0:
        raise StepError(
            "remixer_lookup",
            f"get_game failed for {game_id}",
            {"game_id": game_id, "url": url, "exit_code": command.exit_code},
        )

    index_path_text = command.stdout.strip()
    if not index_path_text:
        raise StepError(
            "remixer_lookup",
            f"get_game returned empty stdout for {game_id}",
            {"game_id": game_id, "url": url},
        )

    index_path = Path(index_path_text)
    if not index_path.exists() or index_path.name != "index.html":
        raise StepError(
            "remixer_lookup",
            f"resolved index path invalid for {game_id}",
            {"game_id": game_id, "url": url, "index_path": index_path_text},
        )

    source_dir = index_path.parent
    pipeline.write_text(pipeline.remixer_dir / f"game_{slot}_index_path.txt", str(index_path) + "\n")
    return {
        "game_id": game_id,
        "url": url,
        "name": match["name"],
        "index_path": str(index_path),
        "source_path": str(source_dir),
    }


def run_remixer_lookup(pipeline: PipelineRun, selected_matches: list[dict[str, str]]) -> list[dict[str, str]]:
    pipeline.start_step(
        "remixer_lookup",
        {"game_ids": [item["game_id"] for item in selected_matches], "urls": [item["url"] for item in selected_matches]},
    )
    resolved = [resolve_game_with_remixer(pipeline, match, slot + 1) for slot, match in enumerate(selected_matches)]
    write_json(pipeline.remixer_dir / "resolved_sources.json", {"games": resolved})
    pipeline.complete_step(
        "remixer_lookup",
        {
            "resolved_index_paths": [item["index_path"] for item in resolved],
            "resolved_source_dirs": [item["source_path"] for item in resolved],
        },
    )
    return resolved


def build_remix_editor_manifest(pipeline: PipelineRun, resolved_games: list[dict[str, str]]) -> Path:
    manifest = {
        "run_label": pipeline.run_id,
        "description": f"Pipeline manifest for prompt: {pipeline.prompt}",
        "games": [
            {
                "game_id": item["game_id"],
                "display_name": item["game_id"],
                "source_path": item["source_path"],
            }
            for item in resolved_games
        ],
    }
    manifest_path = pipeline.remix_editor_dir / "manifest.json"
    write_json(manifest_path, manifest)
    return manifest_path


def build_obfuscator_manifest(pipeline: PipelineRun, source_dir: Path) -> Path:
    manifest = {
        "run_label": f"{pipeline.run_id}_obfuscator",
        "description": f"Obfuscation manifest for {pipeline.run_id}",
        "games": [
            {
                "game_id": pipeline.run_id,
                "display_name": pipeline.run_id,
                "source_path": str(source_dir),
            }
        ],
    }
    manifest_path = pipeline.obfuscator_dir / "manifest.json"
    write_json(manifest_path, manifest)
    return manifest_path


def parse_json_command_output(command: CompletedCommand, step: str) -> dict[str, Any]:
    stdout = command.stdout.strip()
    if not stdout:
        raise StepError(step, f"{step} command returned empty stdout")
    try:
        return json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise StepError(step, f"{step} command returned invalid JSON", {"stdout": stdout}) from exc


def reset_global_watchdog(pipeline: PipelineRun, seconds: int, reason: str) -> None:
    pipeline.state["global_watchdog_seconds"] = seconds
    pipeline.state["global_watchdog_deadline"] = iso_after_seconds(seconds)
    pipeline.append_event(
        "system",
        "global_watchdog_reset",
        {
            "global_watchdog_seconds": seconds,
            "global_watchdog_deadline": pipeline.state["global_watchdog_deadline"],
            "reason": reason,
        },
    )
    pipeline.save_state()


def enforce_overall_watchdog(pipeline: PipelineRun, step: str) -> None:
    deadline_raw = pipeline.state.get("global_watchdog_deadline")
    if not isinstance(deadline_raw, str):
        return
    deadline = datetime.fromisoformat(deadline_raw).astimezone(timezone.utc)
    now = datetime.now(timezone.utc)
    if now > deadline:
        raise StepError(
            step,
            "overall pipeline watchdog exceeded",
            {
                "global_watchdog_seconds": pipeline.state.get("global_watchdog_seconds"),
                "global_watchdog_deadline": deadline_raw,
                "now": now.replace(microsecond=0).isoformat(),
            },
        )


def build_attempt_policy(attempt_number: int) -> dict[str, int]:
    timeout_seconds = ASYNC_STAGE_ATTEMPT_TIMEOUTS[min(attempt_number - 1, len(ASYNC_STAGE_ATTEMPT_TIMEOUTS) - 1)]
    global_watchdog_seconds = INITIAL_GLOBAL_WATCHDOG_SECONDS if attempt_number < 3 else FINAL_GLOBAL_WATCHDOG_SECONDS
    return {
        "attempt_timeout_seconds": timeout_seconds,
        "global_watchdog_seconds": global_watchdog_seconds,
    }


def start_async_attempt(
    pipeline: PipelineRun,
    step: str,
    attempt_number: int,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    policy = build_attempt_policy(attempt_number)
    attempt_started_at = utc_now()
    base = pipeline.state["steps"].get(step, {})
    attempt_history = list(base.get("attempt_history", []))
    attempt_state = {
        **base,
        "status": "running",
        "attempt_number": attempt_number,
        "max_attempts": len(ASYNC_STAGE_ATTEMPT_TIMEOUTS),
        "attempt_started_at": attempt_started_at,
        "attempt_timeout_seconds": policy["attempt_timeout_seconds"],
        "global_watchdog_seconds": policy["global_watchdog_seconds"],
        "attempt_history": attempt_history,
    }
    if extra:
        attempt_state.update(extra)
    pipeline.state["steps"][step] = attempt_state
    pipeline.state["current_step"] = step
    pipeline.save_state()
    reset_global_watchdog(pipeline, policy["global_watchdog_seconds"], f"{step}_attempt_{attempt_number}")
    pipeline.append_event(
        step,
        "attempt_started",
        {
            "attempt_number": attempt_number,
            "attempt_timeout_seconds": policy["attempt_timeout_seconds"],
            "global_watchdog_seconds": policy["global_watchdog_seconds"],
        },
    )
    return policy


def record_async_attempt_end(
    pipeline: PipelineRun,
    step: str,
    *,
    attempt_number: int,
    outcome: str,
    details: dict[str, Any] | None = None,
) -> None:
    step_state = pipeline.state["steps"].get(step, {})
    history = list(step_state.get("attempt_history", []))
    history.append(
        {
            "attempt_number": attempt_number,
            "started_at": step_state.get("attempt_started_at"),
            "ended_at": utc_now(),
            "attempt_timeout_seconds": step_state.get("attempt_timeout_seconds"),
            "outcome": outcome,
            "details": details or {},
            "run_id": step_state.get("run_id"),
            "run_dir": step_state.get("run_dir"),
            "launcher_pid": step_state.get("launcher_pid"),
        }
    )
    pipeline.state["steps"][step] = {
        **step_state,
        "attempt_history": history,
        "last_attempt_outcome": outcome,
    }
    pipeline.save_state()


def enforce_stage_attempt_watchdog(pipeline: PipelineRun, step: str) -> None:
    step_state = pipeline.state["steps"].get(step, {})
    started_at_raw = step_state.get("attempt_started_at")
    timeout_seconds = step_state.get("attempt_timeout_seconds")
    if not isinstance(started_at_raw, str) or not isinstance(timeout_seconds, int):
        return
    started_at = datetime.fromisoformat(started_at_raw).astimezone(timezone.utc)
    elapsed_seconds = int((datetime.now(timezone.utc) - started_at).total_seconds())
    if elapsed_seconds > timeout_seconds:
        raise StepError(
            step,
            f"{step} attempt watchdog exceeded",
            {
                "attempt_number": step_state.get("attempt_number"),
                "attempt_timeout_seconds": timeout_seconds,
                "elapsed_seconds": elapsed_seconds,
                "attempt_started_at": started_at_raw,
                "run_id": step_state.get("run_id"),
                "run_dir": step_state.get("run_dir"),
                "launcher_pid": step_state.get("launcher_pid"),
            },
        )


def terminate_pid(pid: int) -> bool:
    try:
        os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        return False
    time.sleep(1.0)
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return True
    try:
        os.kill(pid, signal.SIGKILL)
    except ProcessLookupError:
        return True
    return True


def terminate_upstream_run(
    pipeline: PipelineRun,
    step: str,
    root: Path,
    run_id: str | None,
    run_dir: str | None,
    launcher_pid: int | None,
) -> dict[str, Any]:
    termination: dict[str, Any] = {
        "launcher_pid": launcher_pid,
        "run_id": run_id,
        "run_dir": run_dir,
        "terminated": False,
    }

    if isinstance(launcher_pid, int):
        termination["terminated"] = terminate_pid(launcher_pid)
        pipeline.append_event(step, "upstream_termination", termination)
        return termination

    if run_id:
        probe = execute_command(["pgrep", "-f", run_id], root)
        pids = [int(line.strip()) for line in probe.stdout.splitlines() if line.strip().isdigit()]
        terminated: list[int] = []
        for pid in pids:
            if terminate_pid(pid):
                terminated.append(pid)
        termination["matched_pids"] = terminated
        termination["terminated"] = bool(terminated)

    pipeline.append_event(step, "upstream_termination", termination)
    return termination


def poll_until_complete(
    pipeline: PipelineRun,
    *,
    step: str,
    status_command_factory: Callable[[], list[str]],
    status_parser: Callable[[dict[str, Any]], dict[str, Any]],
    terminal_statuses: set[str],
    poll_log_path: Path,
) -> dict[str, Any]:
    while True:
        enforce_overall_watchdog(pipeline, step)
        enforce_stage_attempt_watchdog(pipeline, step)
        command = execute_command(status_command_factory(), cwd=status_command_factory.__self__)  # type: ignore[attr-defined]
        payload = parse_json_command_output(command, step)
        entry = {
            "polled_at": utc_now(),
            "command": command.to_dict(),
            "payload": payload,
        }
        with poll_log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry) + "\n")

        parsed = status_parser(payload)
        pipeline.append_event(step, "status_poll", parsed)
        pipeline.state["steps"][step] = {**pipeline.state["steps"].get(step, {}), **parsed}
        pipeline.save_state()

        status = parsed.get("last_known_status") or parsed.get("status")
        if isinstance(status, str) and status in terminal_statuses:
            return payload

        time.sleep(pipeline.poll_seconds)


def reconcile_remix_editor_terminal_state(run_id: str) -> dict[str, Any] | None:
    status_command = execute_command(
        ["python3", "scripts/creative_refactor_cli.py", "--json", "status", "--run-id", run_id],
        GAME_REMIX_EDITOR_ROOT,
    )
    if status_command.exit_code == 0:
        status_payload = parse_json_command_output(status_command, "remix_editor")
        if status_payload.get("completed") is True and status_payload.get("status") == "transform_completed":
            return status_payload

    result_command = execute_command(
        ["python3", "scripts/creative_refactor_cli.py", "--json", "result", "--run-id", run_id],
        GAME_REMIX_EDITOR_ROOT,
    )
    if result_command.exit_code != 0:
        return None

    result_payload = parse_json_command_output(result_command, "remix_editor")
    final_output_dirs = result_payload.get("final_output_dirs")
    if (
        result_payload.get("status") == "transform_completed"
        and isinstance(final_output_dirs, list)
        and bool(final_output_dirs)
    ):
        return {
            "run_id": result_payload.get("run_id"),
            "run_dir": result_payload.get("run_dir"),
            "status": result_payload.get("status"),
            "current_phase": "parallel_batch_finished",
            "updated_at": result_payload.get("updated_at"),
            "dashboard_path": result_payload.get("dashboard_path"),
            "output_root": result_payload.get("output_root"),
            "completed": True,
            "final_output_dirs": final_output_dirs,
        }

    return None


def run_remix_editor_attempt(pipeline: PipelineRun, manifest_path: Path, attempt_number: int) -> list[Path]:
    policy = start_async_attempt(
        pipeline,
        "remix_editor",
        attempt_number,
        {
            "manifest_path": str(manifest_path),
            "launch_timeout_seconds": REMIX_EDITOR_LAUNCH_TIMEOUT_SECONDS,
            "launch_phase": "starting",
        },
    )

    launch_args = [
        "python3",
        "scripts/creative_refactor_cli.py",
        "--json",
        "start-batch",
        "--manifest",
        str(manifest_path),
        "--remix-prompt",
        pipeline.prompt,
        "--poll-seconds",
        str(pipeline.poll_seconds),
        "--agent-timeout",
        str(policy["attempt_timeout_seconds"]),
        "--stale-heartbeat-seconds",
        str(policy["attempt_timeout_seconds"]),
    ]
    pipeline.state["steps"]["remix_editor"]["launch_args"] = launch_args
    pipeline.save_state()

    write_json(
        pipeline.remix_editor_dir / f"attempt_{attempt_number}_start_invocation.json",
        {
            "attempt_number": attempt_number,
            "args": launch_args,
            "cwd": str(GAME_REMIX_EDITOR_ROOT),
            "launch_timeout_seconds": REMIX_EDITOR_LAUNCH_TIMEOUT_SECONDS,
            "started_at": utc_now(),
        },
    )

    start_command = execute_command_with_timeout(
        launch_args,
        GAME_REMIX_EDITOR_ROOT,
        REMIX_EDITOR_LAUNCH_TIMEOUT_SECONDS,
    )
    pipeline.write_command_artifacts(pipeline.remix_editor_dir, f"attempt_{attempt_number}_start", start_command)
    if start_command.exit_code != 0:
        raise StepError("remix_editor", "remix editor start-batch failed", {"exit_code": start_command.exit_code})

    start_payload = parse_json_command_output(start_command, "remix_editor")
    write_json(pipeline.remix_editor_dir / f"attempt_{attempt_number}_start_response.json", start_payload)

    run_id = start_payload.get("run_id")
    run_dir = start_payload.get("run_dir")
    if not isinstance(run_id, str) or not isinstance(run_dir, str):
        raise StepError("remix_editor", "remix editor start response missing run_id/run_dir", start_payload)

    pipeline.state["steps"]["remix_editor"] = {
        **pipeline.state["steps"].get("remix_editor", {}),
        "run_id": run_id,
        "run_dir": run_dir,
        "status_path": start_payload.get("status_path"),
        "dashboard_path": start_payload.get("dashboard_path"),
        "output_root": start_payload.get("output_root"),
        "launcher_pid": start_payload.get("launcher_pid"),
        "launcher_stdout_path": start_payload.get("launcher_stdout_path"),
        "launcher_stderr_path": start_payload.get("launcher_stderr_path"),
        "accepted_at": start_payload.get("accepted_at"),
        "updated_at": start_payload.get("updated_at"),
        "spec_adaptor": start_payload.get("spec_adaptor"),
        "last_known_status": start_payload.get("status"),
        "current_phase": start_payload.get("current_phase"),
        "completed": start_payload.get("completed", False),
        "status": "running",
        "launch_phase": "polling",
    }
    pipeline.save_state()

    if start_payload.get("completed") is True or start_payload.get("status") in REMIX_EDITOR_TERMINAL_STATUSES:
        final_status_payload = start_payload
    else:
        def status_command() -> list[str]:
            return ["python3", "scripts/creative_refactor_cli.py", "--json", "status", "--run-id", run_id]

        setattr(status_command, "__self__", GAME_REMIX_EDITOR_ROOT)
        poll_log_path = pipeline.remix_editor_dir / f"attempt_{attempt_number}_status_polls.jsonl"

        final_status_payload = poll_until_complete(
        pipeline,
        step="remix_editor",
            status_command_factory=status_command,
            status_parser=lambda payload: {
                "status": "running",
                "last_known_status": payload.get("status"),
                "current_phase": payload.get("current_phase"),
                "last_polled_at": utc_now(),
                "completed": payload.get("completed", False),
                "dashboard_path": payload.get("dashboard_path"),
                "output_root": payload.get("output_root"),
                "updated_at": payload.get("updated_at"),
                "games_total": payload.get("games_total"),
                "games_transform_completed": payload.get("games_transform_completed"),
                "games_transform_failed": payload.get("games_transform_failed"),
            },
            terminal_statuses=REMIX_EDITOR_TERMINAL_STATUSES,
            poll_log_path=poll_log_path,
        )

    final_status = final_status_payload.get("status")
    if final_status_payload.get("completed") is not True or final_status != "transform_completed":
        reconciled_payload = reconcile_remix_editor_terminal_state(run_id)
        if reconciled_payload is not None:
            pipeline.append_event(
                "remix_editor",
                "terminal_reconciliation_succeeded",
                {
                    "run_id": run_id,
                    "status": reconciled_payload.get("status"),
                    "current_phase": reconciled_payload.get("current_phase"),
                },
            )
            final_status_payload = reconciled_payload
            final_status = final_status_payload.get("status")
        else:
            raise StepError("remix_editor", "remix editor run did not complete successfully", final_status_payload)

    result_command = execute_command(
        ["python3", "scripts/creative_refactor_cli.py", "--json", "result", "--run-id", run_id],
        GAME_REMIX_EDITOR_ROOT,
    )
    pipeline.write_command_artifacts(pipeline.remix_editor_dir, f"attempt_{attempt_number}_result", result_command)
    if result_command.exit_code != 0:
        raise StepError("remix_editor", "remix editor result command failed", {"exit_code": result_command.exit_code})

    result_payload = parse_json_command_output(result_command, "remix_editor")
    write_json(pipeline.remix_editor_dir / f"attempt_{attempt_number}_final_result.json", result_payload)

    final_output_dirs = result_payload.get("final_output_dirs")
    if not isinstance(final_output_dirs, list) or not final_output_dirs:
        raise StepError("remix_editor", "remix editor result missing final output dirs", result_payload)

    resolved_output_dirs = [Path(path) for path in final_output_dirs]
    missing_output_dirs = [str(path) for path in resolved_output_dirs if not path.exists()]
    if missing_output_dirs:
        raise StepError(
            "remix_editor",
            "remix editor final output dirs do not exist",
            {"paths": missing_output_dirs},
        )

    record_async_attempt_end(
        pipeline,
        "remix_editor",
        attempt_number=attempt_number,
        outcome="completed",
        details={"final_output_dirs": [str(path) for path in resolved_output_dirs]},
    )
    pipeline.complete_step(
        "remix_editor",
        {
            "run_id": run_id,
            "run_dir": run_dir,
            "dashboard_path": result_payload.get("dashboard_path"),
            "output_root": result_payload.get("output_root"),
            "accepted_at": start_payload.get("accepted_at"),
            "updated_at": result_payload.get("updated_at"),
            "completed": result_payload.get("completed"),
            "spec_adaptor": result_payload.get("spec_adaptor", start_payload.get("spec_adaptor")),
            "result_path": str(pipeline.remix_editor_dir / f"attempt_{attempt_number}_final_result.json"),
            "final_output_dir": str(resolved_output_dirs[0]),
            "final_output_dirs": [str(path) for path in resolved_output_dirs],
        },
    )
    return resolved_output_dirs


def run_remix_editor(pipeline: PipelineRun, manifest_path: Path) -> list[Path]:
    last_error: StepError | None = None
    for attempt_number in range(1, len(ASYNC_STAGE_ATTEMPT_TIMEOUTS) + 1):
        try:
            return run_remix_editor_attempt(pipeline, manifest_path, attempt_number)
        except StepError as exc:
            last_error = exc
            if exc.step == "remix_editor" and "attempt watchdog exceeded" in exc.message and attempt_number < len(ASYNC_STAGE_ATTEMPT_TIMEOUTS):
                step_state = pipeline.state["steps"].get("remix_editor", {})
                termination = terminate_upstream_run(
                    pipeline,
                    "remix_editor",
                    GAME_REMIX_EDITOR_ROOT,
                    step_state.get("run_id"),
                    step_state.get("run_dir"),
                    step_state.get("launcher_pid"),
                )
                record_async_attempt_end(
                    pipeline,
                    "remix_editor",
                    attempt_number=attempt_number,
                    outcome="timed_out_retrying",
                    details={**(exc.details or {}), "termination": termination},
                )
                pipeline.append_event(
                    "remix_editor",
                    "attempt_retry_scheduled",
                    {"attempt_number": attempt_number + 1, "previous_attempt": attempt_number},
                )
                continue
            raise
    assert last_error is not None
    raise last_error


def run_obfuscator_attempt(pipeline: PipelineRun, source_dir: Path, attempt_number: int) -> Path:
    manifest_path = build_obfuscator_manifest(pipeline, source_dir)
    start_async_attempt(
        pipeline,
        "obfuscator",
        attempt_number,
        {
            "source_dir": str(source_dir),
            "manifest_path": str(manifest_path),
            "launch_timeout_seconds": LAUNCH_TIMEOUT_SECONDS,
            "launch_phase": "starting",
        },
    )

    launch_args = ["python3", "scripts/game_obfuscator_cli.py", "start", "--manifest", str(manifest_path)]
    pipeline.state["steps"]["obfuscator"]["launch_args"] = launch_args
    pipeline.save_state()

    write_json(
        pipeline.obfuscator_dir / f"attempt_{attempt_number}_start_invocation.json",
        {
            "attempt_number": attempt_number,
            "args": launch_args,
            "cwd": str(GAME_OBFUSCATOR_ROOT),
            "launch_timeout_seconds": LAUNCH_TIMEOUT_SECONDS,
            "started_at": utc_now(),
        },
    )

    start_command = execute_command_with_timeout(
        launch_args,
        GAME_OBFUSCATOR_ROOT,
        LAUNCH_TIMEOUT_SECONDS,
    )
    pipeline.write_command_artifacts(pipeline.obfuscator_dir, f"attempt_{attempt_number}_start", start_command)
    if start_command.exit_code != 0:
        raise StepError("obfuscator", "obfuscator start failed", {"exit_code": start_command.exit_code})

    start_payload = parse_json_command_output(start_command, "obfuscator")
    write_json(pipeline.obfuscator_dir / f"attempt_{attempt_number}_start_response.json", start_payload)

    run_id = start_payload.get("run_id")
    if not isinstance(run_id, str):
        raise StepError("obfuscator", "obfuscator start response missing run_id", start_payload)

    pipeline.state["steps"]["obfuscator"] = {
        **pipeline.state["steps"].get("obfuscator", {}),
        "run_id": run_id,
        "run_dir": start_payload.get("run_dir"),
        "status_path": start_payload.get("status_path"),
        "dashboard_path": start_payload.get("dashboard_path"),
        "output_root": start_payload.get("output_root"),
        "launcher_pid": start_payload.get("launcher_pid"),
        "launcher_stdout_path": start_payload.get("launcher_stdout_path"),
        "launcher_stderr_path": start_payload.get("launcher_stderr_path"),
        "last_known_status": start_payload.get("status"),
        "current_phase": start_payload.get("current_phase"),
        "completed": start_payload.get("completed", False),
        "status": "running",
        "launch_phase": "polling",
        "manifest_path": str(manifest_path),
    }
    pipeline.save_state()

    def status_command() -> list[str]:
        return ["python3", "scripts/game_obfuscator_cli.py", "status", "--run-id", run_id]

    setattr(status_command, "__self__", GAME_OBFUSCATOR_ROOT)
    poll_log_path = pipeline.obfuscator_dir / f"attempt_{attempt_number}_status_polls.jsonl"

    final_status_payload = poll_until_complete(
        pipeline,
        step="obfuscator",
        status_command_factory=status_command,
        status_parser=lambda payload: {
            "status": "running",
            "last_known_status": payload.get("status"),
            "current_phase": payload.get("current_phase"),
            "last_polled_at": utc_now(),
            "completed": payload.get("completed", False),
            "dashboard_path": payload.get("dashboard_path"),
            "output_root": payload.get("output_root"),
            "games_stalled": payload.get("games_stalled"),
        },
        terminal_statuses=OBFUSCATOR_TERMINAL_STATUSES,
        poll_log_path=poll_log_path,
    )

    final_status = final_status_payload.get("status")
    if final_status_payload.get("completed") is not True or final_status != "completed":
        raise StepError("obfuscator", "obfuscator run did not complete successfully", final_status_payload)

    output_command = execute_command(
        ["python3", "scripts/game_obfuscator_cli.py", "output-path", "--run-id", run_id, "--include-games"],
        GAME_OBFUSCATOR_ROOT,
    )
    pipeline.write_command_artifacts(pipeline.obfuscator_dir, f"attempt_{attempt_number}_output_path", output_command)
    if output_command.exit_code != 0:
        raise StepError("obfuscator", "obfuscator output-path failed", {"exit_code": output_command.exit_code})

    output_payload = parse_json_command_output(output_command, "obfuscator")
    write_json(pipeline.obfuscator_dir / f"attempt_{attempt_number}_output_path.json", output_payload)

    output_path_value = output_payload.get("output_path")
    if not isinstance(output_path_value, str):
        raise StepError("obfuscator", "obfuscator output-path missing output_path", output_payload)

    output_path = Path(output_path_value)
    if not output_path.exists():
        raise StepError("obfuscator", "obfuscator output path does not exist", {"path": str(output_path)})

    record_async_attempt_end(
        pipeline,
        "obfuscator",
        attempt_number=attempt_number,
        outcome="completed",
        details={"output_path": str(output_path)},
    )
    pipeline.complete_step(
        "obfuscator",
        {
            "run_id": run_id,
            "run_dir": output_payload.get("run_dir"),
            "dashboard_path": output_payload.get("dashboard_path"),
            "output_path": str(output_path),
            "completed": output_payload.get("completed"),
            "manifest_path": str(manifest_path),
        },
    )
    return output_path


def run_obfuscator(pipeline: PipelineRun, source_dir: Path) -> Path:
    last_error: StepError | None = None
    for attempt_number in range(1, len(ASYNC_STAGE_ATTEMPT_TIMEOUTS) + 1):
        try:
            return run_obfuscator_attempt(pipeline, source_dir, attempt_number)
        except StepError as exc:
            last_error = exc
            if exc.step == "obfuscator" and "attempt watchdog exceeded" in exc.message and attempt_number < len(ASYNC_STAGE_ATTEMPT_TIMEOUTS):
                step_state = pipeline.state["steps"].get("obfuscator", {})
                termination = terminate_upstream_run(
                    pipeline,
                    "obfuscator",
                    GAME_OBFUSCATOR_ROOT,
                    step_state.get("run_id"),
                    step_state.get("run_dir"),
                    step_state.get("launcher_pid"),
                )
                record_async_attempt_end(
                    pipeline,
                    "obfuscator",
                    attempt_number=attempt_number,
                    outcome="timed_out_retrying",
                    details={**(exc.details or {}), "termination": termination},
                )
                pipeline.append_event(
                    "obfuscator",
                    "attempt_retry_scheduled",
                    {"attempt_number": attempt_number + 1, "previous_attempt": attempt_number},
                )
                continue
            raise
    assert last_error is not None
    raise last_error


def finalize_output(pipeline: PipelineRun, source_dirs: list[Path]) -> Path:
    pipeline.start_step("finalize", {"source_dirs": [str(path) for path in source_dirs]})
    PIPELINE_OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    destination = PIPELINE_OUTPUTS_DIR / pipeline.run_id
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True, exist_ok=True)

    copied_output_dirs: list[str] = []
    for source_dir in source_dirs:
        target_dir = destination / source_dir.name
        shutil.copytree(source_dir, target_dir)
        copied_output_dirs.append(str(target_dir))

    pipeline.complete_step(
        "finalize",
        {
            "destination": str(destination),
            "copied_output_dirs": copied_output_dirs,
        },
    )
    pipeline.mark_completed(destination, copied_output_dirs)
    return destination


def ensure_dashboard_html(path: Path) -> None:
    if path.exists():
        return
    path.write_text(
        """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Pipeline Run Dashboard</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body { font-family: Arial, sans-serif; margin: 24px; background: #111827; color: #f3f4f6; }
    h1, h2 { margin-bottom: 0.5rem; }
    .meta, .card { background: #1f2937; border-radius: 8px; padding: 16px; margin-bottom: 16px; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 16px; }
    .status-running { color: #fbbf24; }
    .status-completed { color: #34d399; }
    .status-failed { color: #f87171; }
    .status-pending, .status-skipped { color: #9ca3af; }
    code, pre { background: #0f172a; padding: 2px 4px; border-radius: 4px; }
    pre { padding: 12px; overflow: auto; }
    ul { padding-left: 20px; }
    a { color: #93c5fd; }
    .small { font-size: 0.9rem; color: #d1d5db; }
  </style>
</head>
<body>
  <h1>Pipeline Dashboard</h1>
  <div id="app">Loading…</div>
  <script>
    async function loadData() {
      const response = await fetch("./dashboard_data.json?ts=" + Date.now(), { cache: "no-store" });
      if (!response.ok) {
        throw new Error("Failed to load dashboard data");
      }
      return response.json();
    }

    function esc(value) {
      return String(value ?? "")
        .replaceAll("&", "&")
        .replaceAll("<", "<")
        .replaceAll(">", ">");
    }

    function renderStep(step) {
      const status = step.status || "unknown";
      return `
        <div class="card">
          <h2>${esc(step.label)}</h2>
          <div class="small">Status: <span class="status-${esc(status)}">${esc(status)}</span></div>
          <pre>${esc(JSON.stringify(step.details, null, 2))}</pre>
        </div>
      `;
    }

    function renderEvent(event) {
      return `<li><code>${esc(event.ts)}</code> [${esc(event.level)}] <strong>${esc(event.step)}</strong> ${esc(event.event)}</li>`;
    }

    async function render() {
      const app = document.getElementById("app");
      try {
        const data = await loadData();
        app.innerHTML = `
          <div class="meta">
            <div><strong>Run ID:</strong> ${esc(data.run_id)}</div>
            <div><strong>Prompt:</strong> ${esc(data.prompt)}</div>
            <div><strong>Status:</strong> <span class="status-${esc(data.status)}">${esc(data.status)}</span></div>
            <div><strong>Current Step:</strong> ${esc(data.current_step)}</div>
            <div><strong>Updated At:</strong> ${esc(data.updated_at)}</div>
            <div><strong>Final Output:</strong> ${esc(data.links?.final_output_dir || "N/A")}</div>
          </div>
          <div class="grid">${(data.steps || []).map(renderStep).join("")}</div>
          <div class="card">
            <h2>Recent Events</h2>
            <ul>${(data.recent_events || []).map(renderEvent).join("")}</ul>
          </div>
          <div class="card">
            <h2>Error</h2>
            <pre>${esc(JSON.stringify(data.error, null, 2))}</pre>
          </div>
        `;
      } catch (error) {
        app.innerHTML = `<div class="card">Dashboard load failed: ${esc(error.message)}</div>`;
      }
    }

    render();
    setInterval(render, 60000);
  </script>
</body>
</html>
""",
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the observable game generation pipeline.")
    parser.add_argument("prompt", help="Creative prompt, e.g. 'a harry potter flappy bird game'")
    parser.add_argument("--obfuscate", action="store_true", help="Run obfuscator on the remix output.")
    parser.add_argument("--poll-seconds", type=float, default=DEFAULT_POLL_SECONDS, help="Polling interval for async stages.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    PIPELINE_RUNS_DIR.mkdir(parents=True, exist_ok=True)
    run = PipelineRun(generate_run_id(), args.prompt, args.obfuscate, args.poll_seconds)

    try:
        game_ids = run_matcher(run, args.prompt, DEFAULT_MATCHER_LIMIT)
        resolved_games = run_remixer_lookup(run, game_ids)
        manifest_path = build_remix_editor_manifest(run, resolved_games)
        remix_output_dirs = run_remix_editor(run, manifest_path)

        if args.obfuscate:
            final_source_dirs = [run_obfuscator(run, source_dir) for source_dir in remix_output_dirs]
        else:
            run.skip_step("obfuscator", "disabled by CLI flag")
            final_source_dirs = remix_output_dirs

        final_output_dir = finalize_output(run, final_source_dirs)
        print(
            json.dumps(
                {
                    "run_id": run.run_id,
                    "run_dir": str(run.run_dir),
                    "status": "completed",
                    "final_output_dir": str(final_output_dir),
                    "dashboard_path": str(run.dashboard_dir / "index.html"),
                },
                indent=2,
            )
        )
        return 0
    except StepError as exc:
        run.fail_step(exc.step, exc.message, exc.details)
        print(
            json.dumps(
                {
                    "run_id": run.run_id,
                    "run_dir": str(run.run_dir),
                    "status": "failed",
                    "error": {"step": exc.step, "message": exc.message, "details": exc.details or {}},
                    "dashboard_path": str(run.dashboard_dir / "index.html"),
                },
                indent=2,
            ),
            file=sys.stderr,
        )
        return 1
    except Exception as exc:  # pragma: no cover - defensive catch for orchestration visibility
        run.fail_step("system", "unexpected pipeline exception", {"type": type(exc).__name__, "message": str(exc)})
        print(
            json.dumps(
                {
                    "run_id": run.run_id,
                    "run_dir": str(run.run_dir),
                    "status": "failed",
                    "error": {"step": "system", "message": "unexpected pipeline exception", "details": {"message": str(exc)}},
                    "dashboard_path": str(run.dashboard_dir / "index.html"),
                },
                indent=2,
            ),
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())