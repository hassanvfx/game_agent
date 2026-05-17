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

from pipeline_dashboard_presenter import build_dashboard_contract_extensions, generate_dashboard_html

ROOT = Path(__file__).resolve().parent.parent
PIPELINE_RUNS_DIR = ROOT / "pipeline_runs"
PIPELINE_OUTPUTS_DIR = ROOT / "output"

GAME_MATCHER_ROOT = ROOT.parent / "game_matcher"
GAME_MATCHER_V2_ROOT = ROOT.parent / "game_matcher_v2"
GAME_REFACTORING_ROOT = ROOT.parent / "game_refactoring"
GAME_PUBLISH_PIPELINE_ROOT = ROOT.parent / "game_publish_pipeline"
GAME_REMIX_EDITOR_ROOT = ROOT.parent / "game_remix_editor"
GAME_OBFUSCATOR_ROOT = ROOT.parent / "game_obfuscator"

PUBLIC_CDN_ROOT = "https://friendjam-game-assets.jabali.ai/games-prod/public"
PLAY_CDN_ROOT = "https://friendjam-game-assets.jabali.ai/games-prod/play"

DEFAULT_MATCHER_LIMIT = 2
DEFAULT_MATCHER_MODE = "v2"
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
    def __init__(self, step: str, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.step = step
        self.message = message
        self.details = details or {}


def is_gcloud_auth_error(stderr: str) -> bool:
    lowered = stderr.lower()
    return (
        "gcloud.storage.rsync" in lowered
        and "auth" in lowered
        and (
            "reauthentication failed" in lowered
            or "cannot prompt during non-interactive execution" in lowered
            or "gcloud auth login" in lowered
        )
    )

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

    def __init__(
        self,
        run_id: str,
        prompt: str,
        remix_prompt: str,
        publish_enabled: bool,
        poll_seconds: float,
        matcher_mode: str,
        upload_enabled: bool,
    ) -> None:
        self.run_id = run_id
        self.run_dir = PIPELINE_RUNS_DIR / run_id
        self.prompt = prompt
        self.remix_prompt = remix_prompt
        self.publish_enabled = publish_enabled
        self.poll_seconds = poll_seconds
        self.matcher_mode = matcher_mode
        self.upload_enabled = upload_enabled
        self.input_dir = self.run_dir / "input"
        self.matcher_dir = self.run_dir / "matcher"
        self.remixer_dir = self.run_dir / "remixer"
        self.refactoring_dir = self.run_dir / "refactoring"
        self.publish_dir = self.run_dir / "publish"
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
            self.refactoring_dir,
            self.publish_dir,
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
            "publish_enabled": publish_enabled,
            "poll_seconds": poll_seconds,
            "matcher_mode": matcher_mode,
            "remix_prompt": remix_prompt,
            "upload_enabled": upload_enabled,
            "global_watchdog_seconds": INITIAL_GLOBAL_WATCHDOG_SECONDS,
            "global_watchdog_deadline": iso_after_seconds(INITIAL_GLOBAL_WATCHDOG_SECONDS),
            "steps": {
                "matcher": {"status": "pending"},
                "refactoring": {"status": "pending"},
                "publish": {"status": "pending"},
                "finalize": {"status": "pending"},
            },
            "artifacts": {
                "run_dir": str(self.run_dir),
                "run_state_path": str(self.run_state_path),
                "events_path": str(self.events_path),
                "dashboard_path": str(self.dashboard_dir / "index.html"),
                "dashboard_data_path": str(self.dashboard_data_path),
            },
            "final_output_dir": None,
            "final_output_dirs": [],
            "error": None,
        }

        self.write_text(self.input_dir / "prompt.txt", prompt)
        self.write_text(self.input_dir / "remix_prompt.txt", remix_prompt)
        self._write_log(f"[{now}] run initialized: {run_id}")
        self.append_event(
            "system",
            "run_initialized",
            {"prompt": prompt, "remix_prompt": remix_prompt, "publish_enabled": publish_enabled, "upload_enabled": upload_enabled},
        )
        self.save_state()

    # --- NEW: Game Refactoring and Publish Integration ---
    def run_refactoring(self, selected_matches, matcher_context, remix_prompt):
        """
        Launch creative_remix_v5 via the workflow CLI, then poll until the final
        output directories are available.
        """
        games_manifest = {
            "run_label": self.run_id,
            "games": [],
        }
        for index, match in enumerate(selected_matches, start=1):
            source_path = resolve_refactoring_source_path(match)
            game_entry = {
                "game_id": match["game_id"],
                "display_name": match.get("name") or match["game_id"],
                "source_path": str(source_path),
                "source_url": match["url"],
                "match_rank": match.get("match_rank", index),
                "matcher_context": match.get("matcher_context", {}),
            }
            games_manifest["games"].append(game_entry)

        games_manifest_path = self.refactoring_dir / "games_manifest.json"
        write_json(games_manifest_path, games_manifest)

        launch_args = [
            "python3",
            "scripts/game_workflow.py",
            "--json",
            "--id",
            "creative_remix_v5",
            "--games-manifest-source",
            str(games_manifest_path),
            "--remix-prompt",
            remix_prompt,
        ]
        launch_command = execute_command(launch_args, GAME_REFACTORING_ROOT)
        self.write_command_artifacts(self.refactoring_dir, "launch", launch_command)
        if launch_command.exit_code != 0:
            raise StepError(
                "refactoring",
                "game_refactoring workflow launch failed",
                {"exit_code": launch_command.exit_code},
            )

        launch_payload = parse_json_command_output(launch_command, "refactoring")
        write_json(self.refactoring_dir / "launch_response.json", launch_payload)

        run_id = launch_payload.get("run_id")
        run_dir_value = launch_payload.get("run_dir")
        if not isinstance(run_id, str) or not isinstance(run_dir_value, str):
            raise StepError(
                "refactoring",
                "game_refactoring workflow response missing run_id/run_dir",
                launch_payload,
            )

        run_dir = Path(run_dir_value)
        self.state["steps"]["refactoring"] = {
            **self.state["steps"].get("refactoring", {}),
            "run_id": run_id,
            "run_dir": str(run_dir),
            "workflow_id": launch_payload.get("workflow_id"),
            "workflow_manifest_path": launch_payload.get("workflow_manifest_path"),
            "status_path": launch_payload.get("status_path"),
            "dashboard_path": launch_payload.get("dashboard_path"),
            "output_root": launch_payload.get("output_root"),
            "launcher_pid": launch_payload.get("pid"),
            "launcher_stdout_path": launch_payload.get("launcher_stdout_path"),
            "launcher_stderr_path": launch_payload.get("launcher_stderr_path"),
            "games_manifest_path": str(games_manifest_path),
            "status": "running",
            "last_known_status": launch_payload.get("status"),
            "current_phase": launch_payload.get("current_phase"),
            "completed": False,
        }
        self.save_state()

        deadline = time.time() + FINAL_GLOBAL_WATCHDOG_SECONDS
        status_payload: dict[str, Any] | None = None
        while time.time() < deadline:
            status_args = ["python3", "scripts/creative_refactor_cli.py", "--json", "status", "--run-dir", str(run_dir)]
            status_command = execute_command(status_args, GAME_REFACTORING_ROOT)
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            self.write_command_artifacts(self.refactoring_dir, f"status_{timestamp}", status_command)
            if status_command.exit_code != 0:
                raise StepError(
                    "refactoring",
                    "game_refactoring status polling failed",
                    {"exit_code": status_command.exit_code},
                )

            status_payload = parse_json_command_output(status_command, "refactoring")
            append_jsonl(
                self.refactoring_dir / "status_polls.jsonl",
                {
                    "polled_at": utc_now(),
                    "payload": status_payload,
                },
            )
            self.state["steps"]["refactoring"] = {
                **self.state["steps"].get("refactoring", {}),
                "last_known_status": status_payload.get("status"),
                "current_phase": status_payload.get("current_phase"),
                "updated_at": status_payload.get("updated_at"),
                "completed": status_payload.get("completed", False),
                "failed": status_payload.get("failed", False),
                "games_total": status_payload.get("games_total"),
                "games_transform_completed": status_payload.get("games_transform_completed"),
                "games_transform_failed": status_payload.get("games_transform_failed"),
            }
            self.save_state()

            if status_payload.get("completed") is True:
                break

            time.sleep(self.poll_seconds)
        else:
            raise StepError(
                "refactoring",
                "game_refactoring workflow did not complete before watchdog deadline",
                {"run_id": run_id, "run_dir": str(run_dir)},
            )

        result_args = ["python3", "scripts/creative_refactor_cli.py", "--json", "result", "--run-dir", str(run_dir)]
        result_command = execute_command(result_args, GAME_REFACTORING_ROOT)
        self.write_command_artifacts(self.refactoring_dir, "result", result_command)
        if result_command.exit_code != 0:
            raise StepError(
                "refactoring",
                "game_refactoring result lookup failed",
                {"exit_code": result_command.exit_code},
            )

        result_payload = parse_json_command_output(result_command, "refactoring")
        write_json(self.refactoring_dir / "result_response.json", result_payload)

        final_output_dirs = result_payload.get("final_output_dirs")
        if not isinstance(final_output_dirs, list) or not final_output_dirs:
            raise StepError(
                "refactoring",
                "game_refactoring result missing final_output_dirs",
                result_payload,
            )

        resolved_output_dirs = [str(Path(path).resolve()) for path in final_output_dirs]
        self.state["steps"]["refactoring"] = {
            **self.state["steps"].get("refactoring", {}),
            "status": "completed",
            "completed": True,
            "failed": result_payload.get("status") in {"transform_failed", "transform_incomplete"},
            "final_output_dirs": resolved_output_dirs,
        }
        self.save_state()
        return resolved_output_dirs

    def run_publish_pipeline(self, refactored_game_dirs):
        """
        Run the publish pipeline CLI against the refactoring outputs and optionally
        sync the published results to GCS.
        """
        report_path = self.publish_dir / "publish_report.json"
        args = [
            "python3",
            "scripts/publish_games.py",
            "--report-path",
            str(report_path),
            "--inputs",
            *refactored_game_dirs,
        ]
        command = execute_command(args, GAME_PUBLISH_PIPELINE_ROOT)
        self.write_command_artifacts(self.publish_dir, "publish", command)
        if command.exit_code != 0:
            raise StepError(
                "publish",
                "publish pipeline failed",
                {"exit_code": command.exit_code},
            )

        if not report_path.exists():
            raise StepError(
                "publish",
                "publish pipeline did not produce report_path",
                {"report_path": str(report_path)},
            )

        report_payload = read_json(report_path)
        report_payload["projected_cdn_urls"] = build_projected_cdn_urls(report_payload)
        scoped_upload_game_ids = extract_publish_game_ids(report_payload)

        if self.upload_enabled:
            if not scoped_upload_game_ids:
                raise StepError(
                    "publish",
                    "publish report missing game_ids required for scoped upload",
                    {"report_path": str(report_path)},
                )

            sync_args = [
                "python3",
                "scripts/sync_to_gcs.py",
                "--target",
                "both",
                "--mode",
                "per-item",
            ]
            for game_id in scoped_upload_game_ids:
                sync_args.extend(["--only-item", game_id])
            sync_command = execute_command(sync_args, GAME_PUBLISH_PIPELINE_ROOT)
            self.write_command_artifacts(self.publish_dir, "sync_to_gcs", sync_command)
            if sync_command.exit_code != 0:
                stderr_text = sync_command.stderr.strip()
                stdout_text = sync_command.stdout.strip()
                upload_payload: dict[str, Any] = {
                    "enabled": True,
                    "status": "failed",
                    "exit_code": sync_command.exit_code,
                    "stdout_path": str(self.publish_dir / "sync_to_gcs.stdout.txt"),
                    "stderr_path": str(self.publish_dir / "sync_to_gcs.stderr.txt"),
                    "command_path": str(self.publish_dir / "sync_to_gcs.command.json"),
                    "only_items": scoped_upload_game_ids,
                }
                if stdout_text:
                    upload_payload["stdout_excerpt"] = stdout_text[-2000:]
                if stderr_text:
                    upload_payload["stderr_excerpt"] = stderr_text[-2000:]
                if is_gcloud_auth_error(sync_command.stderr):
                    upload_payload["status"] = "auth_required"
                    upload_payload["next_action"] = (
                        "Run `gcloud auth login` in an interactive terminal, then rerun the short "
                        "publish resume command once available, or rerun this same command."
                    )
                report_payload["upload"] = upload_payload
            else:
                sync_payload = parse_jsonish_output(sync_command.stdout)
                report_payload["upload"] = {
                    "enabled": True,
                    "status": "completed",
                    "only_items": scoped_upload_game_ids,
                    "sync_result": sync_payload,
                }
        else:
            report_payload["upload"] = {"enabled": False, "status": "disabled"}

        write_json(self.publish_dir / "publish_response.json", report_payload)
        return report_payload

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
            if step_id == "remixer_lookup":
                continue
            steps.append(
                {
                    "id": step_id,
                    "label": step_id.replace("_", " ").title(),
                    "status": step_state.get("status", "unknown"),
                    "details": step_state,
                }
            )
        base_payload = {
            "run_id": self.run_id,
            "prompt": self.prompt,
            "status": self.state["status"],
            "current_step": self.state["current_step"],
            "updated_at": self.state["updated_at"],
            "started_at": self.state["started_at"],
            "completed_at": self.state.get("completed_at"),
            "publish_enabled": self.publish_enabled,
            "remix_prompt": self.remix_prompt,
            "upload_enabled": self.upload_enabled,
            "upload": self.state.get("upload"),
            "projected_cdn_urls": self.state.get("projected_cdn_urls", []),
            "artifacts": build_artifacts_map(self),
            "steps": steps,
            "recent_events": recent_events,
            "links": self.state["artifacts"]
            | {
                "final_output_dir": self.state["final_output_dir"],
                "final_output_dirs": self.state.get("final_output_dirs", []),
            },
            "error": self.state["error"],
        }
        return {
            **base_payload,
            **build_dashboard_contract_extensions(self.run_dir, base_payload),
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


def append_jsonl(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True) + "\n")


def read_recent_events(path: Path, limit: int = 25) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in lines[-limit:]][::-1]


def parse_jsonish_output(stdout: str) -> dict[str, Any]:
    text = stdout.strip()
    if not text:
        return {}
    decoder = json.JSONDecoder()
    last_error: Exception | None = None
    for start in range(len(text)):
        if text[start] not in "[{":
            continue
        try:
            candidate, _ = decoder.raw_decode(text[start:])
            if isinstance(candidate, dict):
                return candidate
            return {"value": candidate}
        except json.JSONDecodeError as exc:
            last_error = exc
    raise ValueError(f"unable to decode JSON payload from stdout: {last_error}")


def build_cdn_url(base_url: str, local_root: str, local_path: str) -> str | None:
    try:
        relative = Path(local_path).resolve().relative_to(Path(local_root).resolve())
    except ValueError:
        return None
    return f"{base_url.rstrip('/')}/{relative.as_posix().lstrip('/')}/index.html"


def build_projected_cdn_urls(report_payload: dict[str, Any]) -> list[dict[str, Any]]:
    deployment = report_payload.get("deployment", {})
    obfuscation = report_payload.get("obfuscation", {})

    public_root = deployment.get("published_public_root")
    obfuscated_root = obfuscation.get("published_obfuscated_root")
    deployment_results = deployment.get("results", [])
    obfuscated_outputs = obfuscation.get("game_outputs", [])

    obfuscated_by_game_id: dict[str, str] = {}
    if isinstance(obfuscated_outputs, list):
        for item in obfuscated_outputs:
            if isinstance(item, dict):
                game_id = item.get("game_id")
                output_path = item.get("output_path")
                if isinstance(game_id, str) and isinstance(output_path, str):
                    obfuscated_by_game_id[game_id] = output_path

    projected: list[dict[str, Any]] = []
    if not isinstance(deployment_results, list):
        return projected

    for item in deployment_results:
        if not isinstance(item, dict):
            continue
        game_id = item.get("game_id")
        deploy_dir = item.get("deploy_dir")
        if not isinstance(game_id, str) or not isinstance(deploy_dir, str):
            continue

        public_url = None
        if isinstance(public_root, str):
            public_url = build_cdn_url(PUBLIC_CDN_ROOT, public_root, deploy_dir)

        obfuscated_path = obfuscated_by_game_id.get(game_id)
        play_url = None
        if isinstance(obfuscated_root, str) and isinstance(obfuscated_path, str):
            play_url = build_cdn_url(PLAY_CDN_ROOT, obfuscated_root, obfuscated_path)

        projected.append(
            {
                "game_id": game_id,
                "public_local_dir": deploy_dir,
                "public_cdn_url": public_url,
                "play_local_dir": obfuscated_path,
                "play_cdn_url": play_url,
            }
        )
    return projected


def extract_publish_game_ids(report_payload: dict[str, Any]) -> list[str]:
    ordered_game_ids: list[str] = []
    seen: set[str] = set()

    sources = [
        report_payload.get("deployment", {}).get("results", []),
        report_payload.get("obfuscation", {}).get("game_outputs", []),
    ]

    for source in sources:
        if not isinstance(source, list):
            continue
        for item in source:
            if not isinstance(item, dict):
                continue
            game_id = item.get("game_id")
            if isinstance(game_id, str) and game_id and game_id not in seen:
                seen.add(game_id)
                ordered_game_ids.append(game_id)

    return ordered_game_ids


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


def build_matcher_context(
    *,
    prompt: str,
    matcher_mode: str,
    match_item: dict[str, Any],
    match_rank: int,
    match_count: int,
    validated_selected_tags: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "prompt": prompt,
        "matcher_mode": matcher_mode,
        "match_rank": match_rank,
        "match_count": match_count,
        "matched_queries": match_item.get("matched_queries"),
        "coverage": match_item.get("coverage"),
        "distance": match_item.get("distance"),
        "best_feed_position": match_item.get("best_feed_position"),
        "played_count": match_item.get("played_count"),
        "validated_selected_tags": validated_selected_tags,
    }


def normalize_selected_match(
    item: dict[str, Any],
    *,
    prompt: str,
    matcher_mode: str,
    match_rank: int,
    match_count: int,
    validated_selected_tags: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "game_id": extract_game_id(item),
        "url": extract_game_url(item),
        "name": str(item.get("name") or item.get("title") or extract_game_id(item)),
        "match_rank": match_rank,
        "matcher_context": build_matcher_context(
            prompt=prompt,
            matcher_mode=matcher_mode,
            match_item=item,
            match_rank=match_rank,
            match_count=match_count,
            validated_selected_tags=validated_selected_tags,
        ),
    }


def resolve_refactoring_source_path(match: dict[str, Any]) -> Path:
    url = str(match["url"]).strip().lstrip("/")
    if not url:
        raise StepError("refactoring", "selected match is missing url for source resolution", {"match": match})

    url_path = Path(url)
    candidate = (ROOT.parent.parent / "games" / "published" / "public" / url_path.parent).resolve()
    if not candidate.exists():
        raise StepError(
            "refactoring",
            "resolved source_path does not exist for selected match",
            {"game_id": match.get("game_id"), "candidate": str(candidate), "url": url},
        )
    if not candidate.is_dir():
        raise StepError(
            "refactoring",
            "resolved source_path is not a directory for selected match",
            {"game_id": match.get("game_id"), "candidate": str(candidate), "url": url},
        )
    if not (candidate / "index.html").exists():
        raise StepError(
            "refactoring",
            "resolved source_path is missing index.html for selected match",
            {"game_id": match.get("game_id"), "candidate": str(candidate), "url": url},
        )
    return candidate


def run_matcher(pipeline: PipelineRun, prompt: str, limit: int) -> list[dict[str, Any]]:
    pipeline.start_step("matcher", {"prompt": prompt, "limit": limit, "matcher_mode": pipeline.matcher_mode})

    validated_selected_tags: dict[str, Any] | None = None
    if pipeline.matcher_mode == "v2":
        ranked_matches_path = pipeline.matcher_dir / "ranked_matches.json"
        validated_selected_tags_path = pipeline.matcher_dir / "validated_selected_tags.json"
        command = execute_command(
            [
                "python3",
                "cli/match_prompt.py",
                prompt,
                "--limit",
                str(limit),
                "--selected-tags-out",
                str(validated_selected_tags_path),
                "--out",
                str(ranked_matches_path),
            ],
            GAME_MATCHER_V2_ROOT,
        )
    else:
        ranked_matches_path = None
        validated_selected_tags_path = None
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

    if pipeline.matcher_mode == "v2":
        if ranked_matches_path is None or not ranked_matches_path.exists():
            raise StepError(
                "matcher",
                "matcher v2 did not write ranked matches output",
                {"ranked_matches_path": str(ranked_matches_path) if ranked_matches_path else None},
            )
        matches = read_json(ranked_matches_path)
        if not isinstance(matches, list):
            raise StepError("matcher", "matcher v2 ranked output was not a list")
        if validated_selected_tags_path is not None and validated_selected_tags_path.exists():
            loaded_tags = read_json(validated_selected_tags_path)
            if isinstance(loaded_tags, dict):
                validated_selected_tags = loaded_tags
    else:
        matches = parse_matcher_output(command.stdout)

    if len(matches) == 0 and pipeline.matcher_mode == "v2":
        raise StepError(
            "matcher",
            "matcher v2 had no controlled-vocabulary coverage for prompt",
            {
                "prompt": prompt,
                "match_count": 0,
                "validated_selected_tags_path": (
                    str(validated_selected_tags_path)
                    if validated_selected_tags_path is not None
                    else None
                ),
            },
        )

    if len(matches) < 2:
        raise StepError("matcher", "matcher returned fewer than two matches", {"match_count": len(matches)})

    try:
        selected_matches = [
            normalize_selected_match(
                match,
                prompt=prompt,
                matcher_mode=pipeline.matcher_mode,
                match_rank=index + 1,
                match_count=len(matches),
                validated_selected_tags=validated_selected_tags,
            )
            for index, match in enumerate(matches[:2])
        ]
    except ValueError as exc:
        raise StepError("matcher", "matcher results missing usable game fields", {"message": str(exc)}) from exc

    write_json(
        pipeline.matcher_dir / "parsed_matches.json",
        {
            "matcher_mode": pipeline.matcher_mode,
            "matches": matches,
            "selected_matches": selected_matches,
            "validated_selected_tags": validated_selected_tags,
        },
    )
    pipeline.complete_step(
        "matcher",
        {
            "selected_game_ids": [item["game_id"] for item in selected_matches],
            "match_count": len(matches),
            "matcher_mode": pipeline.matcher_mode,
            "validated_selected_tags_path": (
                str(validated_selected_tags_path) if validated_selected_tags_path and validated_selected_tags_path.exists() else None
            ),
        },
    )
    return selected_matches


# Legacy remixer lookup functions removed (no longer used in pipeline)


def build_remix_editor_manifest(pipeline: PipelineRun, resolved_games: list[dict[str, Any]]) -> Path:
    manifest = {
        "run_label": pipeline.run_id,
        "description": f"Pipeline manifest for prompt: {pipeline.prompt}",
        "games": [
            {
                "game_id": item["game_id"],
                "display_name": item.get("name") or item["game_id"],
                "source_path": item["source_path"],
                "source_url": item.get("url"),
                "match_rank": item.get("match_rank"),
                "matcher_context": item.get("matcher_context"),
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
    path.write_text(generate_dashboard_html(), encoding="utf-8")
    return
    path.write_text(
        """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Pipeline Run Dashboard</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    :root {
      color-scheme: dark;
      --bg: #111827;
      --panel: #1f2937;
      --panel-alt: #0f172a;
      --border: #374151;
      --text: #f3f4f6;
      --muted: #d1d5db;
      --pending: #9ca3af;
      --running: #fbbf24;
      --completed: #34d399;
      --failed: #f87171;
      --link: #93c5fd;
    }

    * { box-sizing: border-box; }
    body {
      font-family: Arial, sans-serif;
      margin: 0;
      padding: 24px;
      background: var(--bg);
      color: var(--text);
      line-height: 1.45;
    }

    h1, h2, h3 { margin: 0 0 0.5rem; }
    a { color: var(--link); }
    code, pre {
      background: var(--panel-alt);
      border-radius: 6px;
    }
    code {
      padding: 2px 4px;
    }
    pre {
      padding: 12px;
      overflow: auto;
      white-space: pre-wrap;
      word-break: break-word;
      border: 1px solid var(--border);
    }

    .page-title {
      margin-bottom: 20px;
    }

    .card {
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 16px;
      margin-bottom: 16px;
    }

    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 16px;
    }

    .meta-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 12px;
    }

    .meta-item {
      background: rgba(255, 255, 255, 0.03);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 12px;
    }

    .meta-label {
      display: block;
      font-size: 0.85rem;
      color: var(--muted);
      margin-bottom: 4px;
    }

    .stage-flow {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
      gap: 12px;
      margin-top: 12px;
    }

    .stage-tile {
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 12px;
      background: rgba(255, 255, 255, 0.02);
    }

    .stage-name {
      font-weight: 700;
      margin-bottom: 6px;
    }

    .status-pill {
      display: inline-block;
      padding: 2px 8px;
      border-radius: 999px;
      font-size: 0.82rem;
      font-weight: 700;
      background: rgba(255,255,255,0.08);
    }

    .status-running, .status-in_progress { color: var(--running); }
    .status-completed, .status-done, .status-success { color: var(--completed); }
    .status-failed, .status-error { color: var(--failed); }
    .status-pending, .status-skipped, .status-unknown { color: var(--pending); }

    .small {
      font-size: 0.9rem;
      color: var(--muted);
    }

    .list {
      margin: 0;
      padding-left: 20px;
    }

    .list li {
      margin-bottom: 6px;
    }

    .empty {
      color: var(--pending);
      font-style: italic;
    }
  </style>
</head>
<body>
  <h1 class="page-title">Pipeline Dashboard</h1>
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

    function prettyJson(value) {
      return esc(JSON.stringify(value ?? null, null, 2));
    }

    function humanStatus(value) {
      return value || "unknown";
    }

    function renderPathList(paths) {
      if (!Array.isArray(paths) || paths.length === 0) {
        return '<div class="empty">None</div>';
      }
      return `<ul class="list">${paths.map((path) => `<li><code>${esc(path)}</code></li>`).join("")}</ul>`;
    }

    function renderProjectedCdnUrls(entries) {
      if (!Array.isArray(entries) || entries.length === 0) {
        return '<div class="empty">No projected CDN URLs yet.</div>';
      }
      return `
        <ul class="list">
          ${entries.map((entry) => {
            const publicUrl = entry?.public_url ? `<div>Public: <a href="${esc(entry.public_url)}" target="_blank" rel="noreferrer">${esc(entry.public_url)}</a></div>` : "";
            const playUrl = entry?.play_url ? `<div>Play: <a href="${esc(entry.play_url)}" target="_blank" rel="noreferrer">${esc(entry.play_url)}</a></div>` : "";
            const label = entry?.game_id || entry?.remix_uuid || "artifact";
            return `<li><strong>${esc(label)}</strong>${publicUrl}${playUrl}</li>`;
          }).join("")}
        </ul>
      `;
    }

    function stageStatusFor(data, key) {
      const steps = Array.isArray(data.steps) ? data.steps : [];
      const found = steps.find((step) => step && step.key === key);
      if (!found) return "pending";
      return found.status || "unknown";
    }

    function renderStageFlow(data) {
      const stageOrder = [
        { key: "matcher", label: "Match" },
        { key: "refactoring", label: "Refactor" },
        { key: "publish", label: "Publish" },
        { key: "finalize", label: "Finalize" },
      ];
      return `
        <div class="card">
          <h2>Pipeline Stages</h2>
          <div class="small">Current flow: match → refactor → publish → finalize</div>
          <div class="stage-flow">
            ${stageOrder.map((stage) => {
              const status = stageStatusFor(data, stage.key);
              return `
                <div class="stage-tile">
                  <div class="stage-name">${esc(stage.label)}</div>
                  <div class="status-pill status-${esc(status)}">${esc(humanStatus(status))}</div>
                </div>
              `;
            }).join("")}
          </div>
        </div>
      `;
    }

    function renderStep(step) {
      const status = step.status || "unknown";
      return `
        <div class="card">
          <h3>${esc(step.label || step.key || "Step")}</h3>
          <div class="small">Key: <code>${esc(step.key || "unknown")}</code></div>
          <div class="small">Status: <span class="status-pill status-${esc(status)}">${esc(humanStatus(status))}</span></div>
          <pre>${prettyJson(step.details)}</pre>
        </div>
      `;
    }

    function renderEvent(event) {
      return `
        <li>
          <code>${esc(event.ts)}</code>
          [${esc(event.level)}]
          <strong>${esc(event.step)}</strong>
          ${esc(event.event)}
        </li>
      `;
    }

    async function render() {
      const app = document.getElementById("app");
      try {
        const data = await loadData();
        app.innerHTML = `
          <div class="card">
            <h2>Run Summary</h2>
            <div class="meta-grid">
              <div class="meta-item">
                <span class="meta-label">Run ID</span>
                <code>${esc(data.run_id)}</code>
              </div>
              <div class="meta-item">
                <span class="meta-label">Status</span>
                <span class="status-pill status-${esc(data.status)}">${esc(humanStatus(data.status))}</span>
              </div>
              <div class="meta-item">
                <span class="meta-label">Current Step</span>
                <strong>${esc(data.current_step || "unknown")}</strong>
              </div>
              <div class="meta-item">
                <span class="meta-label">Updated At</span>
                <strong>${esc(data.updated_at || "unknown")}</strong>
              </div>
              <div class="meta-item">
                <span class="meta-label">Prompt</span>
                <div>${esc(data.prompt || "")}</div>
              </div>
              <div class="meta-item">
                <span class="meta-label">Remix Prompt</span>
                <div>${esc(data.remix_prompt || data.prompt || "")}</div>
              </div>
              <div class="meta-item">
                <span class="meta-label">Publish Enabled</span>
                <strong>${esc(data.publish_enabled ? "true" : "false")}</strong>
              </div>
              <div class="meta-item">
                <span class="meta-label">Upload Enabled</span>
                <strong>${esc(data.upload_enabled ? "true" : "false")}</strong>
              </div>
              <div class="meta-item">
                <span class="meta-label">Upload Status</span>
                <strong>${esc(data.upload?.status || (data.upload_enabled ? "pending" : "disabled"))}</strong>
              </div>
            </div>
          </div>

          ${renderStageFlow(data)}

          <div class="grid">
            <div class="card">
              <h2>Links</h2>
              <div><strong>Run Dir:</strong> <code>${esc(data.links?.run_dir || "N/A")}</code></div>
              <div><strong>Dashboard Path:</strong> <code>${esc(data.links?.dashboard_path || "N/A")}</code></div>
              <div><strong>Events Path:</strong> <code>${esc(data.links?.events_path || "N/A")}</code></div>
              <div><strong>Final Output Dir:</strong> <code>${esc(data.links?.final_output_dir || "N/A")}</code></div>
            </div>

            <div class="card">
              <h2>Final Output Dirs</h2>
              ${renderPathList(data.links?.final_output_dirs)}
            </div>
          </div>

          <div class="card">
            <h2>Projected CDN URLs</h2>
            ${renderProjectedCdnUrls(data.projected_cdn_urls)}
          </div>

          <div class="card">
            <h2>Artifacts</h2>
            <pre>${prettyJson(data.artifacts)}</pre>
          </div>

          <div class="card">
            <h2>Upload</h2>
            <pre>${prettyJson(data.upload)}</pre>
          </div>

          <div class="card">
            <h2>Step Details</h2>
            <div class="grid">${(data.steps || []).map(renderStep).join("")}</div>
          </div>

          <div class="card">
            <h2>Recent Events</h2>
            ${(data.recent_events || []).length
              ? `<ul class="list">${(data.recent_events || []).map(renderEvent).join("")}</ul>`
              : '<div class="empty">No recent events.</div>'}
          </div>

          <div class="card">
            <h2>Error</h2>
            <pre>${prettyJson(data.error)}</pre>
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


def build_artifacts_map(run: PipelineRun) -> dict[str, Any]:
    matcher_state = run.state.get("steps", {}).get("matcher", {})
    refactoring_state = run.state.get("steps", {}).get("refactoring", {})
    publish_state = run.state.get("steps", {}).get("publish", {})
    artifacts: dict[str, Any] = {
        "run_dir": str(run.run_dir),
        "run_state_path": str(run.run_state_path),
        "events_path": str(run.events_path),
        "dashboard_path": str(run.dashboard_dir / "index.html"),
        "dashboard_data_path": str(run.dashboard_data_path),
        "matcher": {
            "command_path": str(run.matcher_dir / "matcher.command.json"),
            "stdout_path": str(run.matcher_dir / "matcher.stdout.txt"),
            "stderr_path": str(run.matcher_dir / "matcher.stderr.txt"),
            "parsed_matches_path": str(run.matcher_dir / "parsed_matches.json"),
            "ranked_matches_path": str(run.matcher_dir / "ranked_matches.json"),
            "validated_selected_tags_path": matcher_state.get("validated_selected_tags_path"),
        },
        "refactoring": {
            "games_manifest_path": refactoring_state.get("games_manifest_path"),
            "launch_response_path": str(run.refactoring_dir / "launch_response.json"),
            "result_response_path": str(run.refactoring_dir / "result_response.json"),
            "launch_command_path": str(run.refactoring_dir / "launch.command.json"),
            "launch_stdout_path": str(run.refactoring_dir / "launch.stdout.txt"),
            "launch_stderr_path": str(run.refactoring_dir / "launch.stderr.txt"),
            "result_command_path": str(run.refactoring_dir / "result.command.json"),
            "result_stdout_path": str(run.refactoring_dir / "result.stdout.txt"),
            "result_stderr_path": str(run.refactoring_dir / "result.stderr.txt"),
            "run_dir": refactoring_state.get("run_dir"),
            "dashboard_path": refactoring_state.get("dashboard_path"),
            "workflow_manifest_path": refactoring_state.get("workflow_manifest_path"),
        },
        "publish": {
            "publish_report_path": str(run.publish_dir / "publish_report.json"),
            "publish_response_path": str(run.publish_dir / "publish_response.json"),
            "publish_command_path": str(run.publish_dir / "publish.command.json"),
            "publish_stdout_path": str(run.publish_dir / "publish.stdout.txt"),
            "publish_stderr_path": str(run.publish_dir / "publish.stderr.txt"),
            "sync_command_path": str(run.publish_dir / "sync_to_gcs.command.json"),
            "sync_stdout_path": str(run.publish_dir / "sync_to_gcs.stdout.txt"),
            "sync_stderr_path": str(run.publish_dir / "sync_to_gcs.stderr.txt"),
        },
        "cost": {
            "report_path": str(run.refactoring_dir / "result_response.json"),
        },
    }
    if publish_state:
        artifacts["publish"]["status"] = publish_state.get("status")
    return artifacts


def build_final_response(
    run: PipelineRun,
    *,
    upload_payload: dict[str, Any] | None,
    projected_cdn_urls: list[dict[str, Any]],
    resumed_from_run: str | None,
) -> dict[str, Any]:
    return {
        "run_id": run.run_id,
        "run_dir": str(run.run_dir),
        "status": run.state["status"],
        "prompt": run.prompt,
        "remix_prompt": run.remix_prompt,
        "publish_enabled": run.publish_enabled,
        "upload_enabled": run.upload_enabled,
        "upload": upload_payload,
        "final_output_dir": run.state["final_output_dir"],
        "final_output_dirs": run.state.get("final_output_dirs", []),
        "dashboard_path": str(run.dashboard_dir / "index.html"),
        "projected_cdn_urls": projected_cdn_urls,
        "artifacts": build_artifacts_map(run),
        "resumed_from_run": resumed_from_run,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the observable game generation pipeline.")
    parser.add_argument("prompt", help="Matcher prompt, e.g. 'a harry potter flappy bird game'")
    parser.add_argument("--remix-prompt", help="Optional creative remix prompt override. Defaults to the matcher prompt.")
    parser.add_argument("--upload", action="store_true", help="Sync published public/obfuscated roots to GCS after local publish.")
    parser.add_argument("--resume-from-run", help="Resume from an existing pipeline run id under pipeline_runs/ and continue from publish/finalize.")
    parser.add_argument("--publish", action="store_true", help="Run the publish pipeline after refactoring.")
    parser.add_argument("--poll-seconds", type=float, default=DEFAULT_POLL_SECONDS, help="Polling interval for async stages.")
    parser.add_argument(
        "--matcher-mode",
        choices=["legacy", "v2"],
        default=DEFAULT_MATCHER_MODE,
        help="Matcher backend to use. Defaults to v2.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    PIPELINE_RUNS_DIR.mkdir(parents=True, exist_ok=True)

    resumed = bool(args.resume_from_run)
    if resumed:
        resumed_run_dir = PIPELINE_RUNS_DIR / args.resume_from_run
        resumed_state_path = resumed_run_dir / "run_state.json"
        if not resumed_state_path.exists():
            print(
                json.dumps(
                    {
                        "status": "failed",
                        "error": {
                            "step": "resume",
                            "message": "resume run_state.json not found",
                            "details": {"run_id": args.resume_from_run, "run_state_path": str(resumed_state_path)},
                        },
                    },
                    indent=2,
                ),
                file=sys.stderr,
            )
            return 1
        resumed_state = read_json(resumed_state_path)
        prompt = resumed_state.get("prompt")
        remix_prompt = resumed_state.get("remix_prompt") or prompt
        if not prompt:
            print(
                json.dumps(
                    {
                        "status": "failed",
                        "error": {
                            "step": "resume",
                            "message": "resume run missing prompt",
                            "details": {"run_id": args.resume_from_run},
                        },
                    },
                    indent=2,
                ),
                file=sys.stderr,
            )
            return 1
        run = PipelineRun(generate_run_id(), prompt, remix_prompt, args.publish, args.poll_seconds, args.matcher_mode, args.upload)
        run.append_event(
            "system",
            "resume_initialized",
            {"resumed_from_run": args.resume_from_run, "resumed_from_run_dir": str(resumed_run_dir)},
        )
        refactored_game_dirs = resumed_state.get("steps", {}).get("refactoring", {}).get("final_output_dirs", [])
        if not isinstance(refactored_game_dirs, list) or not refactored_game_dirs:
            run.fail_step(
                "resume",
                "resume run missing refactoring final_output_dirs",
                {"source_run_id": args.resume_from_run, "source_run_dir": str(resumed_run_dir)},
            )
            print(
                json.dumps(
                    {
                        "run_id": run.run_id,
                        "run_dir": str(run.run_dir),
                        "status": "failed",
                        "error": run.state["error"],
                        "dashboard_path": str(run.dashboard_dir / "index.html"),
                    },
                    indent=2,
                ),
                file=sys.stderr,
            )
            return 1
        run.skip_step("matcher", f"resumed from prior run {args.resume_from_run}")
        run.skip_step("refactoring", f"reusing refactoring outputs from prior run {args.resume_from_run}")
    else:
        prompt = args.prompt
        remix_prompt = args.remix_prompt or args.prompt
        run = PipelineRun(generate_run_id(), prompt, remix_prompt, args.publish, args.poll_seconds, args.matcher_mode, args.upload)

    try:
        if not resumed:
            # 1. Run matcher
            selected_matches = run_matcher(run, prompt, DEFAULT_MATCHER_LIMIT)
            # 2. Prepare matcher handoff metadata for refactoring
            matcher_context = [
                {
                    "matcher_context": m.get("matcher_context"),
                    "selected_tags": m.get("matcher_context", {}).get("validated_selected_tags"),
                    "rank": m.get("match_rank"),
                    "prompt": prompt,
                }
                for m in selected_matches
            ]
            # 3. Run creative_remix_v5 refactoring workflow
            run.start_step("refactoring", {"prompt": prompt, "remix_prompt": remix_prompt, "matcher_context": matcher_context})
            refactored_game_dirs = run.run_refactoring(selected_matches, matcher_context, remix_prompt)
            run.complete_step("refactoring", {"refactored_game_dirs": refactored_game_dirs})

        # 4. Run publish pipeline (optional)
        if args.publish:
            run.start_step("publish", {"refactored_game_dirs": refactored_game_dirs, "resumed": resumed})
            publish_output = run.run_publish_pipeline(refactored_game_dirs)
            projected_cdn_urls = publish_output.get("projected_cdn_urls", [])
            run.state["projected_cdn_urls"] = projected_cdn_urls
            run.state["upload"] = publish_output.get("upload")
            run.complete_step("publish", {"publish_output": publish_output})
        else:
            publish_output = {"upload": {"enabled": False, "status": "disabled"}, "projected_cdn_urls": []}
            projected_cdn_urls = []
            run.state["projected_cdn_urls"] = projected_cdn_urls
            run.state["upload"] = publish_output.get("upload")
            run.skip_step("publish", "publish flag not provided")

        # 5. Finalize output (optional, could copy or link published outputs)
        final_output_dir = finalize_output(run, [Path(d) for d in refactored_game_dirs])
        print(
            json.dumps(
                build_final_response(
                    run,
                    upload_payload=publish_output.get("upload"),
                    projected_cdn_urls=projected_cdn_urls,
                    resumed_from_run=args.resume_from_run,
                ),
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