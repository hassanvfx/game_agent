#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STYLE_ID = "neutral_prototype"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def append_run_note(run_dir: Path, message: str) -> None:
    run_state_path = run_dir / "run_state.json"
    if not run_state_path.exists():
        return
    run_state = load_json(run_state_path)
    run_state.setdefault("notes", []).append(message)
    run_state["updated_at"] = utc_now()
    write_json(run_state_path, run_state)


def append_batch_debug_event(run_dir: Path, event: dict) -> None:
    path = run_dir / "batch_debug_events.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a tiny sequential Game Remixer batch using the extracted single-game runner.")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--run-id")
    parser.add_argument("--model", default="gpt-5.4")
    parser.add_argument("--agent-timeout", type=int, default=3600)
    parser.add_argument("--style", default=DEFAULT_STYLE_ID)
    parser.add_argument("--remix-prompt")
    parser.add_argument("--remix-prompt-file")
    return parser.parse_args()


def run_python(*args: str) -> str:
    completed = subprocess.run(["python3", *args], check=True, capture_output=True, text=True)
    return completed.stdout.strip()


def run_python_logged(run_dir: Path, step_name: str, *args: str) -> str:
    append_batch_debug_event(
        run_dir,
        {
            "timestamp": utc_now(),
            "step": step_name,
            "status": "starting",
            "args": list(args),
        },
    )
    try:
        output = run_python(*args)
    except subprocess.CalledProcessError as exc:
        append_batch_debug_event(
            run_dir,
            {
                "timestamp": utc_now(),
                "step": step_name,
                "status": "failed",
                "args": list(args),
                "returncode": exc.returncode,
                "stdout": exc.stdout,
                "stderr": exc.stderr,
            },
        )
        append_run_note(run_dir, f"{step_name} failed with return code {exc.returncode}.")
        raise

    append_batch_debug_event(
        run_dir,
        {
            "timestamp": utc_now(),
            "step": step_name,
            "status": "completed",
            "args": list(args),
            "output": output,
        },
    )
    append_run_note(run_dir, f"{step_name} completed.")
    return output


def resolve_remix_prompt(args: argparse.Namespace) -> str | None:
    if args.remix_prompt and args.remix_prompt_file:
        raise ValueError("Pass only one of --remix-prompt or --remix-prompt-file.")
    if args.remix_prompt_file:
        return Path(args.remix_prompt_file).read_text(encoding="utf-8").strip()
    if args.remix_prompt:
        return args.remix_prompt.strip()
    return None


def run_spec_adaptor(run_dir: Path, style: str, remix_prompt: str) -> None:
    run_python_logged(
        run_dir,
        "spec_adaptor",
        str(ROOT / "scripts" / "spec_adaptor.py"),
        "--run-dir",
        str(run_dir),
        "--style",
        style,
        "--remix-prompt",
        remix_prompt,
    )


def main() -> None:
    args = parse_args()
    remix_prompt = resolve_remix_prompt(args)

    create_cmd = [str(ROOT / "scripts" / "create_run.py"), "--manifest", args.manifest]
    if args.run_id:
        create_cmd.extend(["--run-id", args.run_id])
    run_dir = Path(run_python(*create_cmd))

    append_batch_debug_event(
        run_dir,
        {
            "timestamp": utc_now(),
            "step": "batch_start",
            "status": "starting",
            "manifest": args.manifest,
            "run_id": run_dir.name,
            "style": args.style,
            "remix_prompt": remix_prompt,
        },
    )

    run_python_logged(run_dir, "prepare_inputs", str(ROOT / "scripts" / "prepare_inputs.py"), "--run-dir", str(run_dir))
    if remix_prompt:
        run_spec_adaptor(run_dir, args.style, remix_prompt)
    run_python_logged(run_dir, "build_dashboard_initial", str(ROOT / "scripts" / "build_dashboard.py"), "--run-dir", str(run_dir))
    run_python_logged(run_dir, "write_dashboard_launcher", str(ROOT / "scripts" / "write_dashboard_launcher.py"), "--run-dir", str(run_dir))

    manifest = load_json(run_dir / "input_manifest.json")
    for game in manifest.get("games", []):
        append_batch_debug_event(
            run_dir,
            {
                "timestamp": utc_now(),
                "step": "game_start",
                "status": "starting",
                "game_id": game["game_id"],
                "source_path": game.get("source_path"),
            },
        )
        append_run_note(run_dir, f"About to run single-game transform for {game['game_id']}.")
        run_python_logged(
            run_dir,
            f"run_single_game:{game['game_id']}",
            str(ROOT / "scripts" / "run_single_game.py"),
            "--run-dir",
            str(run_dir),
            "--game-id",
            game["game_id"],
            "--model",
            args.model,
            "--agent-timeout",
            str(args.agent_timeout),
            "--style",
            args.style,
            *(
                ["--remix-prompt", remix_prompt]
                if remix_prompt
                else []
            ),
        )
        append_batch_debug_event(
            run_dir,
            {
                "timestamp": utc_now(),
                "step": "game_finished",
                "status": "completed",
                "game_id": game["game_id"],
            },
        )
        run_python_logged(run_dir, f"build_dashboard_after:{game['game_id']}", str(ROOT / "scripts" / "build_dashboard.py"), "--run-dir", str(run_dir))

    run_state_path = run_dir / "run_state.json"
    run_state = load_json(run_state_path)
    if run_state["games_transform_failed"] == 0 and run_state["games_transform_completed"] == run_state["games_total"]:
        run_state["status"] = "transform_completed"
    elif run_state["games_transform_completed"] + run_state["games_transform_failed"] == run_state["games_total"]:
        run_state["status"] = "transform_failed"
    else:
        run_state["status"] = "transform_incomplete"
    run_state["current_phase"] = "sample_batch_finished"
    run_state["selected_style_id"] = args.style
    run_state["remix_prompt"] = remix_prompt
    run_state["notes"].append(f"Sequential extracted sample batch finished using style {args.style}.")
    run_state_path.write_text(json.dumps(run_state, indent=2) + "\n", encoding="utf-8")
    run_python_logged(run_dir, "build_dashboard_final", str(ROOT / "scripts" / "build_dashboard.py"), "--run-dir", str(run_dir))

    append_batch_debug_event(
        run_dir,
        {
            "timestamp": utc_now(),
            "step": "batch_finished",
            "status": "completed",
            "run_id": run_dir.name,
        },
    )

    print(run_dir)


if __name__ == "__main__":
    main()