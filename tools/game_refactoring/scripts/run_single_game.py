#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.creative_refactor_runtime import execute_worker_command, load_json, utc_now, update_json_file, write_json


ROOT = Path(__file__).resolve().parents[1]
PROMPTS_ROOT = ROOT / "prompts"
SPECS_ROOT = ROOT / "specs"
DEFAULT_STYLE_ID = "neutral_prototype"
REUSABLE_SPEC_ADAPTOR_FILES = (
    "creative_refactor_agent_template.md",
    "creative_remix_contract.md",
    "visual_identity_contract.md",
    "theme_policy.md",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a single extracted creative transform in Game Remixer.")
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--game-id", required=True)
    parser.add_argument("--model", default="gpt-5.5")
    parser.add_argument("--agent-timeout", type=int, default=3600)
    parser.add_argument("--skip-run-state-update", action="store_true")
    parser.add_argument("--style", default=DEFAULT_STYLE_ID)
    parser.add_argument("--remix-prompt")
    parser.add_argument("--remix-prompt-file")
    parser.add_argument("--playwright-port", type=int)
    return parser.parse_args()


def clone_directory(source: Path, destination: Path) -> None:
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(source, destination)


def base_job_state(game_id: str, attempt_dir: Path, attempt_number: int, job_type: str, timeout_seconds: int) -> dict:
    return {
        "job_id": f"{game_id}_{job_type}_attempt_{attempt_number:04d}",
        "job_type": job_type,
        "status": "queued",
        "owner_game_id": game_id,
        "attempt_number": attempt_number,
        "heartbeat_at": None,
        "started_at": None,
        "finished_at": None,
        "result_path": None,
        "stdout_path": str(attempt_dir / f"{job_type}_stdout.txt"),
        "stderr_path": str(attempt_dir / f"{job_type}_stderr.txt"),
        "artifacts_manifest_path": str(attempt_dir / "artifacts_manifest.json"),
        "failure_reason": None,
        "timeout_seconds": timeout_seconds,
        "forced_mode": None,
    }


def build_refactor_prompt(packet: dict, playwright_port: int | None = None) -> str:
    prompt_template = Path(packet["prompt_template_path"]).read_text(encoding="utf-8").strip()
    primary_contract_path = packet["spec_paths"][0]
    supporting_policy_paths = packet.get("policy_paths", [])
    audio_catalog_path = packet.get("audio_catalog_path")
    lines = [
        prompt_template,
        "",
        "You are operating on a seeded working clone that already contains a mirrored copy of the original source.",
        "Validation Runtime Contract:",
        f"- validation_host: {'127.0.0.1' if playwright_port is not None else 'NONE_ASSIGNED'}",
        f"- validation_port: {playwright_port if playwright_port is not None else 'NONE_ASSIGNED'}",
        f"- validation_root_url: {f'http://127.0.0.1:{playwright_port}/' if playwright_port is not None else 'NONE_ASSIGNED'}",
        "- If runtime/browser verification is required, use only the assigned validation localhost URL/port.",
        "- Do not choose another localhost port or attach to another local server.",
        "- Write screenshots or browser-grounded evidence only inside the current working clone.",
        "",
        f"Run ID: {packet['run_id']}",
        f"Game ID: {packet['game_id']}",
        f"Attempt Number: {packet['attempt_number']}",
        f"Style ID: {packet.get('style_id', 'unknown')}",
        f"Source Path: {packet['source_path']}",
        f"Working Clone Path: {packet['working_clone_path']}",
        f"Prompt Template Path: {packet['prompt_template_path']}",
        f"Primary Contract Path: {primary_contract_path}",
        f"Audio Catalog Path: {audio_catalog_path or 'NONE'}",
        "Supporting Policy Paths:",
    ]
    lines.extend(f"- {path}" for path in supporting_policy_paths)
    lines.extend(
        [
            "Read and follow the primary contract file completely.",
            "Also read and follow every supporting policy file before editing.",
            "If Audio Catalog Path is not NONE, read the audio catalog JSON before editing and use only its listed URLs when adding audio.",
            "Priority order:",
            "1. The primary contract is the leading remix authority.",
            "2. Supporting policy files refine identity, audio, network, theme, system, and compliance behavior.",
            "3. If there is tension, preserve gameplay, controls, runtime stability, readability, and coherent remix intent over cosmetic ambition.",
            "Edit the existing files in the working clone in place.",
            "Do not replace the project from zero unless strictly necessary.",
            "Preserve structure, assets, DOM, scripts, and behavior as much as possible while making targeted, coherent remix edits.",
            "",
            "Return exactly six lines and nothing else:",
            "CHANGED FILES: file1, file2 or NONE",
            "SUMMARY: one short sentence describing the in-place refactor",
            "REMIX CONCEPT: one short sentence naming the thematic framing and presentation direction",
            "MEANINGFUL CHANGES: dim1, dim2, dim3, dim4",
            "DESIGN SYSTEM: panels|bars|buttons|type|glow = short note",
            "PLAYABILITY CHECK: controls unobstructed|issues, HUD readable|issues, mechanics preserved|issues",
        ]
    )
    return "\n".join(lines)


def extract_changed_files(stdout: str, working_dir: Path) -> list[str]:
    marker = "CHANGED FILES:"
    for line in stdout.splitlines():
        if line.startswith(marker):
            raw = line[len(marker):].strip()
            if not raw or raw.upper() == "NONE":
                return []
            return [item.strip() for item in raw.split(",") if item.strip()]
    return sorted(str(path.relative_to(working_dir)) for path in working_dir.rglob("*") if path.is_file())


def extract_summary(stdout: str, fallback: str) -> str:
    marker = "SUMMARY:"
    for line in stdout.splitlines():
        if line.startswith(marker):
            value = line[len(marker):].strip()
            if value:
                return value
    stripped = stdout.strip()
    if stripped:
        return stripped.splitlines()[0][:300]
    return fallback


def resolve_remix_prompt(args: argparse.Namespace) -> str | None:
    if args.remix_prompt and args.remix_prompt_file:
        raise ValueError("Pass only one of --remix-prompt or --remix-prompt-file.")
    if args.remix_prompt_file:
        return Path(args.remix_prompt_file).read_text(encoding="utf-8").strip()
    if args.remix_prompt:
        return args.remix_prompt.strip()
    return None


def run_spec_adaptor(run_dir: Path, style: str, remix_prompt: str) -> None:
    subprocess.run(
        [
            "python3",
            str(ROOT / "scripts" / "spec_adaptor.py"),
            "--run-dir",
            str(run_dir),
            "--style",
            style,
            "--remix-prompt",
            remix_prompt,
        ],
        check=True,
        capture_output=True,
        text=True,
    )


def has_matching_ready_spec_adaptor(run_state: dict, style: str, remix_prompt: str) -> bool:
    spec_adaptor = run_state.get("spec_adaptor")
    if not spec_adaptor or spec_adaptor.get("status") != "ready":
        return False
    if run_state.get("selected_style_id") != style:
        return False
    if (run_state.get("remix_prompt") or "") != remix_prompt:
        return False

    adapted_dir_raw = spec_adaptor.get("adapted_dir")
    summary_path_raw = spec_adaptor.get("recomposition_summary_path")
    if not adapted_dir_raw or not summary_path_raw:
        return False

    adapted_dir = Path(adapted_dir_raw)
    summary_path = Path(summary_path_raw)
    if not adapted_dir.exists() or not summary_path.exists():
        return False

    for filename in REUSABLE_SPEC_ADAPTOR_FILES:
        if not (adapted_dir / filename).exists():
            return False

    return True


def ensure_spec_adaptor_ready(run_dir: Path, run_state_path: Path, style: str, remix_prompt: str) -> dict:
    run_state = load_json(run_state_path)
    if has_matching_ready_spec_adaptor(run_state, style, remix_prompt):
        return run_state

    run_spec_adaptor(run_dir, style, remix_prompt)
    refreshed_run_state = load_json(run_state_path)
    if not has_matching_ready_spec_adaptor(refreshed_run_state, style, remix_prompt):
        raise RuntimeError("Spec adaptor did not produce a reusable ready state for the requested style/remix prompt.")
    return refreshed_run_state


def main() -> None:
    args = parse_args()
    remix_prompt = resolve_remix_prompt(args)
    run_dir = Path(args.run_dir).resolve()
    run_state_path = run_dir / "run_state.json"
    run_state = load_json(run_state_path)
    if remix_prompt:
        run_state = ensure_spec_adaptor_ready(run_dir, run_state_path, args.style, remix_prompt)

    game_dir = run_dir / "games" / args.game_id
    game_state_path = game_dir / "game_state.json"
    game_state = load_json(game_state_path)

    if game_state.get("integrity_status") != "passed":
        raise RuntimeError(f"Game {args.game_id} is not integrity-passed and cannot be transformed.")

    input_dir = Path(game_state["input_mirror_path"])
    working_dir = Path(game_state["working_clone_path"])
    output_dir = Path(game_state["output_path"])

    clone_directory(input_dir, working_dir)
    clone_directory(working_dir, output_dir)

    game_state["status"] = "running"
    game_state["current_phase"] = "creative_clone_prepared"
    game_state["creative_output_path"] = str(output_dir)
    game_state["selected_style_id"] = args.style
    game_state["remix_prompt"] = remix_prompt
    game_state["assigned_playwright_port"] = args.playwright_port
    game_state["validation_root_url"] = f"http://127.0.0.1:{args.playwright_port}/" if args.playwright_port is not None else None
    game_state["updated_at"] = utc_now()
    write_json(game_state_path, game_state)

    attempt_number = 1
    attempt_dir = game_dir / "attempts" / f"attempt_{attempt_number:04d}"
    attempt_dir.mkdir(parents=True, exist_ok=True)

    packet_cmd = [
        "python3",
        str(ROOT / "scripts" / "generate_task_packet.py"),
        "--run-dir",
        str(run_dir),
        "--game-id",
        args.game_id,
        "--job-type",
        "creative_refactor",
        "--attempt-number",
        str(attempt_number),
        "--target-path",
        str(output_dir),
        "--input-reference-path",
        str(working_dir),
        "--style",
        args.style,
    ]
    packet_path = Path(subprocess.run(packet_cmd, check=True, capture_output=True, text=True).stdout.strip())
    packet = load_json(packet_path)

    job_state = base_job_state(args.game_id, attempt_dir, attempt_number, "creative_refactor", args.agent_timeout)
    job_state["status"] = "running"
    job_state["started_at"] = utc_now()
    job_state["heartbeat_at"] = job_state["started_at"]
    job_state["style_id"] = args.style
    job_state["remix_prompt"] = remix_prompt
    job_state["playwright_port"] = args.playwright_port
    job_state["validation_root_url"] = f"http://127.0.0.1:{args.playwright_port}/" if args.playwright_port is not None else None
    write_json(attempt_dir / "job_state.json", job_state)

    prompt = build_refactor_prompt(packet, playwright_port=args.playwright_port)
    prompt_path = attempt_dir / "creative_refactor_prompt.txt"
    prompt_path.write_text(prompt, encoding="utf-8")

    invocation_path = attempt_dir / "creative_refactor_invocation.json"
    write_json(
        invocation_path,
        {
            "command": [
                "cline",
                "-a",
                "-y",
                "-t",
                str(args.agent_timeout),
                "--reasoning-effort",
                "high",
                "-c",
                str(output_dir),
                "--model",
                args.model,
                "<prompt omitted; see creative_refactor_prompt.txt>",
            ],
            "generated_at": utc_now(),
            "style_id": args.style,
            "remix_prompt": remix_prompt,
            "playwright_port": args.playwright_port,
            "validation_root_url": f"http://127.0.0.1:{args.playwright_port}/" if args.playwright_port is not None else None,
        },
    )

    command = [
        "cline",
        "-a",
        "-y",
        "-t",
        str(args.agent_timeout),
        "--reasoning-effort",
        "high",
        "-c",
        str(output_dir),
        "--model",
        args.model,
        prompt,
    ]

    def update_job_heartbeat() -> None:
        def mutate(job_state_payload: dict) -> None:
            if job_state_payload.get("status") == "running":
                job_state_payload["heartbeat_at"] = utc_now()

        update_json_file(attempt_dir / "job_state.json", mutate)

    execution = execute_worker_command(
        command=command,
        cwd=output_dir,
        stdout_path=Path(job_state["stdout_path"]),
        stderr_path=Path(job_state["stderr_path"]),
        timeout_seconds=args.agent_timeout,
        heartbeat_callback=update_job_heartbeat,
    )

    result_text = execution.stdout_text if execution.stdout_text.strip() else execution.stderr_text
    result_path = attempt_dir / "creative_refactor_result.json"
    result = {
        "status": execution.status,
        "run_id": run_state["run_id"],
        "game_id": args.game_id,
        "attempt_number": attempt_number,
        "job_type": "creative_refactor",
        "style_id": args.style,
        "remix_prompt": remix_prompt,
        "playwright_port": args.playwright_port,
        "validation_root_url": f"http://127.0.0.1:{args.playwright_port}/" if args.playwright_port is not None else None,
        "target_path": str(output_dir),
        "summary": extract_summary(
            result_text,
            (
                "Creative refactor completed."
                if execution.returncode == 0
                else ("Creative refactor timed out." if execution.timed_out else "Creative refactor failed.")
            ),
        ),
        "changed_files": extract_changed_files(result_text, output_dir),
        "artifacts": [
            str(packet_path),
            str(prompt_path),
            str(invocation_path),
            job_state["stdout_path"],
            job_state["stderr_path"],
        ],
        "generated_at": utc_now(),
    }
    write_json(result_path, result)

    job_state["status"] = execution.status
    job_state["finished_at"] = utc_now()
    job_state["heartbeat_at"] = job_state["finished_at"]
    job_state["result_path"] = str(result_path)
    job_state["failure_reason"] = (
        None
        if execution.returncode == 0
        else ("creative_refactor_command_timed_out" if execution.timed_out else "creative_refactor_command_failed")
    )
    write_json(attempt_dir / "job_state.json", job_state)

    write_json(
        attempt_dir / "artifacts_manifest.json",
        {
            "generated_at": utc_now(),
            "style_id": args.style,
            "remix_prompt": remix_prompt,
            "playwright_port": args.playwright_port,
            "validation_root_url": f"http://127.0.0.1:{args.playwright_port}/" if args.playwright_port is not None else None,
            "artifacts": [
                str(packet_path),
                str(prompt_path),
                str(invocation_path),
                str(attempt_dir / "job_state.json"),
                str(result_path),
                job_state["stdout_path"],
                job_state["stderr_path"],
            ],
        },
    )

    game_state = load_json(game_state_path)
    game_state["attempt_count"] = attempt_number
    game_state["creative_status"] = execution.status
    game_state["creative_phase"] = (
        "creative_refactor_completed"
        if execution.returncode == 0
        else ("creative_refactor_timed_out" if execution.timed_out else "creative_refactor_failed")
    )
    game_state["current_phase"] = game_state["creative_phase"]
    game_state["status"] = execution.status
    game_state["last_error"] = (
        None
        if execution.returncode == 0
        else (
            "Creative-only refactor CLI execution timed out."
            if execution.timed_out
            else "Creative-only refactor CLI execution failed."
        )
    )
    game_state["selected_style_id"] = args.style
    game_state["remix_prompt"] = remix_prompt
    game_state["assigned_playwright_port"] = args.playwright_port
    game_state["validation_root_url"] = f"http://127.0.0.1:{args.playwright_port}/" if args.playwright_port is not None else None
    game_state["updated_at"] = utc_now()
    write_json(game_state_path, game_state)

    if not args.skip_run_state_update:
        run_state = load_json(run_state_path)
        run_state["games_transform_completed"] += 1 if execution.returncode == 0 else 0
        run_state["games_transform_failed"] += 0 if execution.returncode == 0 else 1
        run_state["status"] = (
            "transform_completed" if execution.returncode == 0 else ("transform_timeout" if execution.timed_out else "transform_failed")
        )
        run_state["current_phase"] = "single_game_transform_finished"
        run_state["selected_style_id"] = args.style
        run_state["remix_prompt"] = remix_prompt
        run_state["assigned_playwright_port"] = args.playwright_port
        run_state["validation_root_url"] = f"http://127.0.0.1:{args.playwright_port}/" if args.playwright_port is not None else None
        run_state["updated_at"] = utc_now()
        run_state.setdefault("notes", []).append(
            f"{args.game_id} creative transform {'completed' if execution.returncode == 0 else ('timed out' if execution.timed_out else 'failed')} in extracted remixer using style {args.style}."
        )
        write_json(run_state_path, run_state)

    print(run_dir)


if __name__ == "__main__":
    main()