#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNS_ROOT = Path("/Volumes/HDD2026/output")
LEDGER_PATH = ROOT / "tmp/retry_manifests/known_runs.json"
STATE_PATH = ROOT / "tmp/retry_manifests/watcher_state.json"
EVENTS_PATH = ROOT / "tmp/retry_manifests/watcher_events.log"
CONSOLIDATOR = ROOT / "tmp/consolidate_retry_manifests.py"
WORKFLOW_SCRIPT = ROOT / "tools/game_refactoring/scripts/game_workflow.py"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--stale-minutes", type=int, default=60)
    parser.add_argument("--cooldown-minutes", type=int, default=60)
    parser.add_argument("--once", action="store_true")
    return parser.parse_args()


def load_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    tmp_path.replace(path)


def append_event(event: dict) -> None:
    EVENTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with EVENTS_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event) + "\n")


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def isoformat(dt: datetime) -> str:
    return dt.isoformat()


def parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value)


def consider_path(path: Path, latest_mtime, latest_path):
    if not path.exists():
        return latest_mtime, latest_path
    stat = path.stat()
    mtime = stat.st_mtime
    if latest_mtime is None or mtime > latest_mtime:
        return mtime, str(path)
    return latest_mtime, latest_path


def get_latest_activity(run_dir: Path) -> dict:
    latest_mtime = None
    latest_path = None

    direct_files = [
        run_dir / "run_state.json",
        run_dir / "run_parallel_batch_debug_trace.log",
        run_dir / "dashboard" / "dashboard_data.json",
        run_dir / "batch_launcher_stdout.txt",
        run_dir / "batch_launcher_stderr.txt",
    ]
    for path in direct_files:
        latest_mtime, latest_path = consider_path(path, latest_mtime, latest_path)

    for section_name in ["output", "games"]:
        section_dir = run_dir / section_name
        latest_mtime, latest_path = consider_path(section_dir, latest_mtime, latest_path)
        if not section_dir.exists() or not section_dir.is_dir():
            continue
        for child in section_dir.iterdir():
            if child.name.startswith("._"):
                continue
            latest_mtime, latest_path = consider_path(child, latest_mtime, latest_path)

    return {
        "latest_mtime_epoch": latest_mtime,
        "latest_path": latest_path,
    }


def run_consolidator(prompt_key: str) -> dict:
    command = [
        "python3",
        str(CONSOLIDATOR),
        "--prompt-key",
        prompt_key,
        "--json-output",
    ]
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=True)
    return json.loads(completed.stdout)


def find_active_run_name(family: dict) -> str:
    runs = family.get("runs", [])
    for run_name in reversed(runs):
        if (RUNS_ROOT / run_name).exists():
            return run_name
    raise FileNotFoundError(f"No existing run dir found for family {family.get('prompt_key')}")


def build_next_run_id(prompt_key: str) -> str:
    return f"run_v4_{prompt_key}_retry_watch_{now_utc().strftime('%Y%m%dT%H%M%SZ')}"


def update_ledger_with_run(prompt_key: str, run_id: str) -> None:
    ledger = load_json(LEDGER_PATH, {"run_families": []})
    for family in ledger.get("run_families", []):
        if family.get("prompt_key") == prompt_key:
            runs = family.setdefault("runs", [])
            if run_id not in runs:
                runs.append(run_id)
            break
    save_json(LEDGER_PATH, ledger)


def launch_run(result: dict, run_id: str, dry_run: bool) -> dict:
    manifest_path = result["manifest_path"]
    remix_prompt = result["remix_prompt"]

    command = [
        "python3",
        str(WORKFLOW_SCRIPT),
        "--json",
        "--id",
        "creative_remix_v4",
        "--games-manifest-source",
        manifest_path,
        "--run-id",
        run_id,
        "--runs-root",
        str(RUNS_ROOT),
        "--source-mode",
        "copy",
        "--pipeline",
        "v2",
        "--model",
        "gpt-5.5",
        "--agent-timeout",
        "3600",
        "--max-concurrency",
        "1",
        "--poll-seconds",
        "5",
        "--stale-heartbeat-seconds",
        "900",
        "--remix-prompt",
        remix_prompt,
    ]

    if dry_run:
        return {
            "launched": False,
            "command": command,
            "returncode": None,
        }

    completed = subprocess.run(command, cwd=ROOT, text=True)
    return {
        "launched": True,
        "command": command,
        "returncode": completed.returncode,
    }


def evaluate_family(family: dict, state: dict, args: argparse.Namespace) -> dict:
    prompt_key = family["prompt_key"]
    remix_prompt = family["remix_prompt"]
    active_run = find_active_run_name(family)
    run_dir = RUNS_ROOT / active_run

    family_state = state.setdefault("families", {}).setdefault(
        prompt_key,
        {
            "last_seen_mtime_epoch": None,
            "last_seen_path": None,
            "last_progress_at": None,
            "last_checked_at": None,
            "last_active_run": None,
            "last_relaunch_at": None,
            "last_relaunch_run_id": None,
        },
    )

    activity = get_latest_activity(run_dir)
    current_mtime = activity["latest_mtime_epoch"]
    current_path = activity["latest_path"]
    now = now_utc()

    previous_mtime = family_state.get("last_seen_mtime_epoch")
    last_progress_at = parse_dt(family_state.get("last_progress_at"))
    if current_mtime is not None and (previous_mtime is None or current_mtime > previous_mtime):
        family_state["last_seen_mtime_epoch"] = current_mtime
        family_state["last_seen_path"] = current_path
        family_state["last_progress_at"] = isoformat(now)
        last_progress_at = now

    family_state["last_checked_at"] = isoformat(now)
    family_state["last_active_run"] = active_run

    stalled = False
    idle_minutes = None
    if last_progress_at is not None:
        idle_minutes = (now - last_progress_at).total_seconds() / 60.0
        stalled = idle_minutes >= args.stale_minutes

    result_payload = run_consolidator(prompt_key)
    result = result_payload["results"][0] if result_payload.get("results") else None

    relaunch = None
    reason = "healthy"
    if result and result["retry_count"] == 0:
        reason = "no_retry_needed"
    elif stalled:
        last_relaunch_at = parse_dt(family_state.get("last_relaunch_at"))
        cooldown_ok = (
            last_relaunch_at is None
            or (now - last_relaunch_at).total_seconds() / 60.0 >= args.cooldown_minutes
        )
        if cooldown_ok and result:
            next_run_id = build_next_run_id(prompt_key)
            launch = launch_run(result, next_run_id, args.dry_run)
            relaunch = {
                "next_run_id": next_run_id,
                "command": launch["command"],
                "returncode": launch["returncode"],
                "dry_run": args.dry_run,
            }
            reason = "stalled_relaunch"
            if not args.dry_run:
                family_state["last_relaunch_at"] = isoformat(now)
                family_state["last_relaunch_run_id"] = next_run_id
                update_ledger_with_run(prompt_key, next_run_id)
        else:
            reason = "stalled_cooldown"
    else:
        reason = "waiting_for_progress"

    event = {
        "timestamp": isoformat(now),
        "prompt_key": prompt_key,
        "active_run": active_run,
        "reason": reason,
        "idle_minutes": idle_minutes,
        "latest_path": current_path,
        "retry_count": result["retry_count"] if result else None,
        "dry_run": args.dry_run,
        "relaunch": relaunch,
    }
    append_event(event)

    return {
        "prompt_key": prompt_key,
        "remix_prompt": remix_prompt,
        "active_run": active_run,
        "latest_path": current_path,
        "last_seen_mtime_epoch": family_state.get("last_seen_mtime_epoch"),
        "last_progress_at": family_state.get("last_progress_at"),
        "idle_minutes": idle_minutes,
        "stalled": stalled,
        "reason": reason,
        "retry_manifest_path": result["manifest_path"] if result else None,
        "retry_count": result["retry_count"] if result else None,
        "launch_command": result["launch_command"] if result else None,
        "relaunch": relaunch,
    }


def main() -> int:
    args = parse_args()
    ledger = load_json(LEDGER_PATH, {"run_families": []})
    state = load_json(STATE_PATH, {"families": {}})

    results = []
    for family in ledger.get("run_families", []):
        results.append(evaluate_family(family, state, args))

    if not args.dry_run:
        save_json(STATE_PATH, state)

    print(json.dumps({"dry_run": args.dry_run, "results": results}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())