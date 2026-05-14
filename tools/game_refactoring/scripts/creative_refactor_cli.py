#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.creative_refactor_runtime import (
    WorkerExecutionResult,
    execute_worker_command,
    load_json,
    utc_now,
    write_json,
)
from scripts.process_kill_utils import build_kill_all_payload, render_kill_all_human


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STYLE_ID = "neutral_prototype"


def discover_style_ids() -> list[str]:
    styles_root = ROOT / "styles"
    if not styles_root.exists():
        return [DEFAULT_STYLE_ID]

    style_ids: list[str] = []
    seen: set[str] = set()
    for manifest_path in sorted(styles_root.glob("*/style_manifest.json")):
        try:
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        style_id = payload.get("style_id")
        if isinstance(style_id, str) and style_id and style_id not in seen:
            seen.add(style_id)
            style_ids.append(style_id)

    return style_ids or [DEFAULT_STYLE_ID]


def add_runtime_override_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--timeout", type=int, default=None, help="Optional override timeout in seconds.")
    parser.add_argument("--model", default=None, help="Optional override model.")
    parser.add_argument("--verbose", action="store_true", help="Pass --verbose to cline for richer terminal output.")
    parser.add_argument("--json-output", action="store_true", help="Pass --json to cline for structured streaming output.")
    parser.add_argument("--thinking", default=None, help="Optional token budget for --thinking.")
    parser.add_argument(
        "--reasoning-effort",
        choices=["none", "low", "medium", "high", "xhigh"],
        default=None,
        help="Optional override for cline reasoning effort.",
    )


def add_batch_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--manifest", required=True, help="Manifest file containing the list of games.")
    parser.add_argument("--run-id", help="Optional explicit run id. Defaults to create_run.py timestamp behavior.")
    parser.add_argument(
        "--runs-root",
        help="Optional custom runs root directory. Defaults to the repo-local runs/ directory.",
    )
    parser.add_argument(
        "--source-mode",
        choices=["copy", "inplace"],
        default="copy",
        help="How source game directories should be prepared before execution.",
    )
    parser.add_argument(
        "--pipeline",
        choices=["v2", "legacy"],
        default="v2",
        help="Batch pipeline to use. Default: v2 operator pipeline. Use legacy for the previous run_parallel_batch.py path.",
    )
    parser.add_argument("--model", default="gpt-5.5", help="Model to use for downstream workers.")
    parser.add_argument("--agent-timeout", type=int, default=3600, help="Per-game worker timeout in seconds.")
    parser.add_argument("--max-concurrency", type=int, default=2, help="Maximum number of active workers.")
    parser.add_argument("--poll-seconds", type=float, default=5.0, help="Scheduler poll interval in seconds.")
    parser.add_argument(
        "--stale-heartbeat-seconds",
        type=int,
        default=900,
        help="Heartbeat age threshold after which a worker is considered stale.",
    )
    parser.add_argument("--remix-prompt", help="Optional remix prompt.")
    parser.add_argument("--remix-prompt-file", help="Optional file containing remix prompt text.")
    parser.add_argument("--playwright-port-base", type=int, help="Optional leased-port pool base for browser-grounded workers.")
    parser.add_argument(
        "--playwright-port-pool-size",
        type=int,
        help="Optional leased-port pool size for browser-grounded workers.",
    )
    parser.add_argument(
        "--playwright-port-lease-ttl-seconds",
        type=int,
        help="Optional leased-port TTL in seconds for browser-grounded workers.",
    )
    parser.add_argument(
        "--dry-run-operators",
        action="store_true",
        help="Run the operator pipeline shell without invoking cline workers; stage results are simulated.",
    )
    parser.add_argument(
        "--dry-run-spec-adaptor",
        action="store_true",
        help="Run the spec-adaptor shell without invoking cline; shared adapted bundle artifacts are simulated.",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Formal creative refactor CLI for replaying prepared attempts or orchestrating manifest-driven runs."
    )
    parser.add_argument("--json", action="store_true", help="Emit structured JSON responses for CLI orchestration commands.")
    subparsers = parser.add_subparsers(dest="mode")

    replay_parser = subparsers.add_parser(
        "replay",
        help="Replay a prepared creative refactor attempt directly against the cline worker.",
    )
    replay_parser.add_argument(
        "--attempt-dir",
        required=True,
        help="Attempt directory containing prompt, packet, and invocation files.",
    )
    add_runtime_override_args(replay_parser)

    pipeline_parser = subparsers.add_parser(
        "pipeline",
        help="Resolve the latest creative refactor attempt from a run/game pair and replay it.",
    )
    pipeline_parser.add_argument("--run-dir", required=True, help="Run directory containing games/<game_id>/attempts.")
    pipeline_parser.add_argument("--game-id", required=True, help="Game identifier within the run.")
    pipeline_parser.add_argument(
        "--attempt-number",
        type=int,
        default=None,
        help="Optional explicit attempt number. Defaults to the latest attempt directory.",
    )
    add_runtime_override_args(pipeline_parser)

    start_batch_parser = subparsers.add_parser(
        "start-batch",
        help="Start a manifest-driven bounded parallel creative refactor run.",
    )
    add_batch_args(start_batch_parser)

    status_parser = subparsers.add_parser(
        "status",
        help="Return pollable status for a previously started manifest-driven run.",
    )
    status_group = status_parser.add_mutually_exclusive_group(required=True)
    status_group.add_argument("--run-id", help="Run identifier under runs/.")
    status_group.add_argument("--run-dir", help="Explicit run directory path.")

    result_parser = subparsers.add_parser(
        "result",
        help="Return the current final destination contract for a previously started manifest-driven run.",
    )
    result_group = result_parser.add_mutually_exclusive_group(required=True)
    result_group.add_argument("--run-id", help="Run identifier under runs/.")
    result_group.add_argument("--run-dir", help="Explicit run directory path.")

    finish_parser = subparsers.add_parser(
        "finish",
        help="Alias for 'result'; resolve the current final destination contract for a run.",
    )
    finish_group = finish_parser.add_mutually_exclusive_group(required=True)
    finish_group.add_argument("--run-id", help="Run identifier under runs/.")
    finish_group.add_argument("--run-dir", help="Explicit run directory path.")

    kill_all_parser = subparsers.add_parser(
        "kill-all",
        help="List and terminate active remix-related CLI and worker processes.",
    )
    kill_all_parser.add_argument("--dry-run", action="store_true", help="Preview matching processes without signaling.")
    kill_all_parser.add_argument("--force", action="store_true", help="Use SIGKILL instead of SIGTERM.")
    kill_all_parser.add_argument(
        "--include-cline",
        action="store_true",
        help="Also target generic 'cline' processes in addition to known remixer scripts.",
    )

    legacy_attempt_dir = None
    if "--attempt-dir" in __import__("sys").argv[1:]:
        legacy_attempt_dir = True

    args = parser.parse_args()
    if args.mode is None:
        if legacy_attempt_dir:
            replay_parser.parse_args()
        parser.error("A mode is required. Use 'replay', 'pipeline', 'start-batch', 'status', 'result', or 'finish'.")
    return args


def run_python(*args: str) -> str:
    completed = subprocess.run(["python3", *args], check=True, capture_output=True, text=True)
    return completed.stdout.strip()


def write_launcher_invocation(path: Path, payload: dict[str, Any]) -> None:
    write_json(path, payload)


def resolve_run_dir(run_id: str | None, run_dir: str | None) -> Path:
    if run_dir:
        path = Path(run_dir).resolve()
    else:
        if not run_id:
            raise ValueError("Either run_id or run_dir is required.")
        path = (ROOT / "runs" / run_id).resolve()
    if not path.exists():
        raise FileNotFoundError(f"Run directory not found: {path}")
    return path


def resolve_attempt_dir(run_dir: Path, game_id: str, attempt_number: int | None) -> Path:
    attempts_dir = run_dir / "games" / game_id / "attempts"
    if not attempts_dir.exists():
        raise FileNotFoundError(f"Attempts directory not found: {attempts_dir}")
    if attempt_number is not None:
        attempt_dir = attempts_dir / f"attempt_{attempt_number:04d}"
        if not attempt_dir.exists():
            raise FileNotFoundError(f"Attempt directory not found: {attempt_dir}")
        return attempt_dir

    candidates = sorted(path for path in attempts_dir.iterdir() if path.is_dir() and path.name.startswith("attempt_"))
    if not candidates:
        raise FileNotFoundError(f"No attempt directories found in: {attempts_dir}")
    return candidates[-1]


def resolve_paths(attempt_dir: Path) -> tuple[Path, Path, Path]:
    prompt_path = attempt_dir / "creative_refactor_prompt.txt"
    packet_path = attempt_dir / "creative_refactor_task_packet.json"
    invocation_path = attempt_dir / "creative_refactor_invocation.json"

    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
    if not packet_path.exists():
        raise FileNotFoundError(f"Task packet not found: {packet_path}")
    if not invocation_path.exists():
        raise FileNotFoundError(f"Invocation file not found: {invocation_path}")

    return prompt_path, packet_path, invocation_path


def build_command(
    invocation: dict,
    work_dir: Path,
    model: str | None,
    timeout: int | None,
    prompt: str,
    verbose: bool,
    json_output: bool,
    thinking: str | None,
    reasoning_effort: str | None,
) -> list[str]:
    command = invocation["command"][:]
    if command[-1] == "<prompt omitted; see creative_refactor_prompt.txt>":
        command[-1] = prompt

    if model is not None and "--model" in command:
        model_index = command.index("--model")
        if model_index + 1 < len(command):
            command[model_index + 1] = model

    if timeout is not None and "-t" in command:
        timeout_index = command.index("-t")
        if timeout_index + 1 < len(command):
            command[timeout_index + 1] = str(timeout)

    if "-c" in command:
        cwd_index = command.index("-c")
        if cwd_index + 1 < len(command):
            command[cwd_index + 1] = str(work_dir)

    if reasoning_effort is not None and "--reasoning-effort" in command:
        effort_index = command.index("--reasoning-effort")
        if effort_index + 1 < len(command):
            command[effort_index + 1] = reasoning_effort

    if verbose and "--verbose" not in command and "-v" not in command:
        command.insert(-1, "--verbose")

    if json_output and "--json" not in command:
        command.insert(-1, "--json")

    if thinking is not None:
        if "--thinking" in command:
            thinking_index = command.index("--thinking")
            if thinking_index + 1 < len(command):
                command[thinking_index + 1] = str(thinking)
        else:
            command.insert(-1, str(thinking))
            command.insert(-1, "--thinking")

    return command


def write_replay_invocation(
    replay_invocation_path: Path,
    attempt_dir: Path,
    packet_path: Path,
    prompt_path: Path,
    work_dir: Path,
    command: list[str],
    args: argparse.Namespace,
    packet: dict,
) -> None:
    timeout_seconds = args.timeout if args.timeout is not None else None
    write_json(
        replay_invocation_path,
        {
            "generated_at": utc_now(),
            "mode": args.mode,
            "attempt_dir": str(attempt_dir),
            "packet_path": str(packet_path),
            "prompt_path": str(prompt_path),
            "work_dir": str(work_dir),
            "command": command[:-1] + ["<prompt omitted; see creative_refactor_prompt.txt>"],
            "effective_model": args.model or packet.get("model"),
            "timeout_override_seconds": timeout_seconds,
            "verbose": args.verbose,
            "json_output": args.json_output,
            "thinking": args.thinking,
            "reasoning_effort": args.reasoning_effort,
            "resolved_from_run_dir": str(Path(args.run_dir).resolve()) if getattr(args, "run_dir", None) else None,
            "resolved_game_id": getattr(args, "game_id", None),
            "resolved_attempt_number": getattr(args, "attempt_number", None),
        },
    )


def write_replay_result(
    result_path: Path,
    attempt_dir: Path,
    packet_path: Path,
    prompt_path: Path,
    work_dir: Path,
    stdout_path: Path,
    stderr_path: Path,
    execution: WorkerExecutionResult,
) -> None:
    write_json(
        result_path,
        {
            "status": execution.status,
            "attempt_dir": str(attempt_dir),
            "packet_path": str(packet_path),
            "prompt_path": str(prompt_path),
            "work_dir": str(work_dir),
            "pid": execution.pid,
            "started_at": execution.started_at,
            "finished_at": execution.finished_at,
            "duration_seconds": execution.duration_seconds,
            "returncode": execution.returncode,
            "timed_out": execution.timed_out,
            "stdout_path": str(stdout_path),
            "stderr_path": str(stderr_path),
            "stdout_bytes": execution.stdout_bytes,
            "stderr_bytes": execution.stderr_bytes,
        },
    )


def run_replay(args: argparse.Namespace) -> Path:
    attempt_dir = (
        Path(args.attempt_dir).resolve()
        if args.mode == "replay"
        else resolve_attempt_dir(Path(args.run_dir).resolve(), args.game_id, args.attempt_number)
    )
    prompt_path, packet_path, invocation_path = resolve_paths(attempt_dir)

    prompt = prompt_path.read_text(encoding="utf-8")
    packet = load_json(packet_path)
    invocation = load_json(invocation_path)
    work_dir = Path(packet["target_path"]).resolve()

    stdout_path = attempt_dir / "direct_worker_stdout.txt"
    stderr_path = attempt_dir / "direct_worker_stderr.txt"
    result_path = attempt_dir / "direct_worker_result.json"
    replay_invocation_path = attempt_dir / "direct_worker_invocation.json"

    command = build_command(
        invocation,
        work_dir,
        args.model,
        args.timeout,
        prompt,
        args.verbose,
        args.json_output,
        args.thinking,
        args.reasoning_effort,
    )

    write_replay_invocation(
        replay_invocation_path=replay_invocation_path,
        attempt_dir=attempt_dir,
        packet_path=packet_path,
        prompt_path=prompt_path,
        work_dir=work_dir,
        command=command,
        args=args,
        packet=packet,
    )

    execution = execute_worker_command(
        command=command,
        cwd=work_dir,
        stdout_path=stdout_path,
        stderr_path=stderr_path,
        timeout_seconds=args.timeout,
    )

    write_replay_result(
        result_path=result_path,
        attempt_dir=attempt_dir,
        packet_path=packet_path,
        prompt_path=prompt_path,
        work_dir=work_dir,
        stdout_path=stdout_path,
        stderr_path=stderr_path,
        execution=execution,
    )
    return result_path


def build_start_batch_payload(run_dir: Path) -> dict:
    run_state_path = run_dir / "run_state.json"
    dashboard_path = run_dir / "dashboard" / "index.html"
    output_root = run_dir / "output"
    run_state = load_json(run_state_path)
    return {
        "run_id": run_state["run_id"],
        "run_dir": str(run_dir),
        "status_path": str(run_state_path),
        "dashboard_path": str(dashboard_path),
        "output_root": str(output_root),
        "status": run_state["status"],
        "current_phase": run_state["current_phase"],
        "updated_at": run_state["updated_at"],
    }


def resolve_remix_prompt_from_args(args: argparse.Namespace) -> str | None:
    if getattr(args, "remix_prompt", None) and getattr(args, "remix_prompt_file", None):
        raise ValueError("Pass only one of --remix-prompt or --remix-prompt-file.")
    if getattr(args, "remix_prompt_file", None):
        return Path(args.remix_prompt_file).read_text(encoding="utf-8").strip()
    if getattr(args, "remix_prompt", None):
        return args.remix_prompt.strip()
    return None


def start_batch(args: argparse.Namespace) -> dict:
    create_cmd = [
        str(ROOT / "scripts" / "create_run.py"),
        "--manifest",
        args.manifest,
        "--source-mode",
        args.source_mode,
    ]
    if args.run_id:
        create_cmd.extend(["--run-id", args.run_id])
    if args.runs_root:
        create_cmd.extend(["--runs-root", args.runs_root])

    run_dir = Path(run_python(*create_cmd))
    remix_prompt = resolve_remix_prompt_from_args(args)

    batch_runner = "run_operator_pipeline_batch.py" if args.pipeline == "v2" else "run_parallel_batch.py"
    run_parallel_command = [
        sys.executable,
        str(ROOT / "scripts" / batch_runner),
        "--manifest",
        args.manifest,
        "--run-dir",
        str(run_dir),
        "--model",
        args.model,
        "--agent-timeout",
        str(args.agent_timeout),
        "--max-concurrency",
        str(args.max_concurrency),
        "--poll-seconds",
        str(args.poll_seconds),
        "--stale-heartbeat-seconds",
        str(args.stale_heartbeat_seconds),
        "--source-mode",
        args.source_mode,
    ]
    if remix_prompt:
        run_parallel_command.extend(["--remix-prompt", remix_prompt])
    if getattr(args, "playwright_port_base", None) is not None:
        run_parallel_command.extend(["--playwright-port-base", str(args.playwright_port_base)])
    if getattr(args, "playwright_port_pool_size", None) is not None:
        run_parallel_command.extend(["--playwright-port-pool-size", str(args.playwright_port_pool_size)])
    if getattr(args, "playwright_port_lease_ttl_seconds", None) is not None:
        run_parallel_command.extend(
            ["--playwright-port-lease-ttl-seconds", str(args.playwright_port_lease_ttl_seconds)]
        )
    if args.dry_run_operators:
        run_parallel_command.append("--dry-run-operators")
    if args.dry_run_spec_adaptor:
        run_parallel_command.append("--dry-run-spec-adaptor")

    launcher_stdout_path = run_dir / "batch_launcher_stdout.txt"
    launcher_stderr_path = run_dir / "batch_launcher_stderr.txt"
    launcher_invocation_path = run_dir / "batch_launcher_invocation.json"

    with launcher_stdout_path.open("w", encoding="utf-8") as stdout_handle, launcher_stderr_path.open(
        "w", encoding="utf-8"
    ) as stderr_handle:
        process = subprocess.Popen(
            run_parallel_command,
            cwd=str(ROOT),
            stdin=subprocess.DEVNULL,
            stdout=stdout_handle,
            stderr=stderr_handle,
            text=True,
            start_new_session=True,
        )

    write_launcher_invocation(
        launcher_invocation_path,
        {
            "generated_at": utc_now(),
            "mode": "start-batch",
            "pipeline": args.pipeline,
            "batch_runner": batch_runner,
            "run_dir": str(run_dir),
            "command": run_parallel_command,
            "pid": process.pid,
            "manifest": str(Path(args.manifest).resolve()),
            "model": args.model,
            "agent_timeout": args.agent_timeout,
            "max_concurrency": args.max_concurrency,
            "poll_seconds": args.poll_seconds,
            "stale_heartbeat_seconds": args.stale_heartbeat_seconds,
            "source_mode": args.source_mode,
            "runs_root": str(Path(args.runs_root).resolve()) if args.runs_root else None,
            "remix_prompt_present": bool(remix_prompt),
            "playwright_port_base": getattr(args, "playwright_port_base", None),
            "playwright_port_pool_size": getattr(args, "playwright_port_pool_size", None),
            "playwright_port_lease_ttl_seconds": getattr(args, "playwright_port_lease_ttl_seconds", None),
            "dry_run_operators": args.dry_run_operators,
            "dry_run_spec_adaptor": args.dry_run_spec_adaptor,
            "stdout_path": str(launcher_stdout_path),
            "stderr_path": str(launcher_stderr_path),
        },
    )

    payload = build_start_batch_payload(run_dir)
    payload["pid"] = process.pid
    payload["launcher_stdout_path"] = str(launcher_stdout_path)
    payload["launcher_stderr_path"] = str(launcher_stderr_path)
    payload["launcher_invocation_path"] = str(launcher_invocation_path)
    return payload


def build_status_payload(run_dir: Path) -> dict:
    run_state_path = run_dir / "run_state.json"
    run_state = load_json(run_state_path)
    dashboard_path = run_dir / "dashboard" / "index.html"
    output_root = run_dir / "output"

    final_output_dirs = sorted(str(path) for path in output_root.iterdir() if path.is_dir()) if output_root.exists() else []
    status = run_state["status"]
    completed = status in {"transform_completed", "transform_failed", "transform_incomplete"}
    failed = status in {"transform_failed", "transform_incomplete"}
    running = not completed
    payload = {
        "run_id": run_state["run_id"],
        "run_dir": str(run_dir),
        "status": status,
        "current_phase": run_state["current_phase"],
        "updated_at": run_state["updated_at"],
        "games_total": run_state.get("games_total", 0),
        "games_transform_completed": run_state.get("games_transform_completed", 0),
        "games_transform_failed": run_state.get("games_transform_failed", 0),
        "dashboard_path": str(dashboard_path),
        "output_root": str(output_root),
        "running": running,
        "completed": completed,
        "failed": failed,
    }
    if completed:
        payload["final_output_dirs"] = final_output_dirs
    return payload


def build_result_payload(run_dir: Path) -> dict:
    run_state = load_json(run_dir / "run_state.json")
    output_root = run_dir / "output"
    final_output_dirs = sorted(str(path) for path in output_root.iterdir() if path.is_dir()) if output_root.exists() else []
    completed = run_state["status"] in {"transform_completed", "transform_failed", "transform_incomplete"}
    payload = {
        "run_id": run_state["run_id"],
        "status": run_state["status"],
        "run_dir": str(run_dir),
        "dashboard_path": str(run_dir / "dashboard" / "index.html"),
        "output_root": str(output_root),
        "completed": completed,
    }
    if completed:
        payload["final_output_dirs"] = final_output_dirs
    return payload


def emit_output(args: argparse.Namespace, payload: dict | Path) -> None:
    if isinstance(payload, Path):
        print(payload)
        return
    if args.json:
        print(json.dumps(payload, indent=2))
        return
    if payload.get("mode") == "kill-all":
        print(render_kill_all_human(payload))
        return
    if "run_id" in payload:
        print(payload["run_id"])
        return
    print(json.dumps(payload, indent=2))


def main() -> None:
    args = parse_args()
    if args.mode in {"replay", "pipeline"}:
        emit_output(args, run_replay(args))
        return
    if args.mode == "start-batch":
        emit_output(args, start_batch(args))
        return
    if args.mode == "status":
        run_dir = resolve_run_dir(getattr(args, "run_id", None), getattr(args, "run_dir", None))
        emit_output(args, build_status_payload(run_dir))
        return
    if args.mode in {"result", "finish"}:
        run_dir = resolve_run_dir(getattr(args, "run_id", None), getattr(args, "run_dir", None))
        emit_output(args, build_result_payload(run_dir))
        return
    if args.mode == "kill-all":
        payload = build_kill_all_payload(
            include_cline=args.include_cline,
            dry_run=args.dry_run,
            force=args.force,
            exclude_pid=os.getpid(),
        )
        emit_output(args, payload)
        return
    raise RuntimeError(f"Unsupported mode: {args.mode}")


if __name__ == "__main__":
    main()