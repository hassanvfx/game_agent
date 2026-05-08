#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
DEFAULT_RUN_ID = "full-pack-10"
DEFAULT_ITEM_TIMEOUT_SECONDS = 300


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a sequential batch of sprite jobs.")
    parser.add_argument("--run-id", default=DEFAULT_RUN_ID)
    parser.add_argument("--limit", type=int, help="Optional limit for selected jobs.")
    parser.add_argument("--all", action="store_true", help="Run all jobs in the manifest sequentially.")
    parser.add_argument("--start-index", type=int, default=0)
    parser.add_argument("--only-pending", action="store_true")
    parser.add_argument("--item-timeout", type=int, default=DEFAULT_ITEM_TIMEOUT_SECONDS)
    return parser.parse_args()


def load_manifest(run_dir: Path) -> list[dict[str, Any]]:
    return json.loads((run_dir / "manifest.json").read_text())


def is_pending(item: dict[str, Any]) -> bool:
    state_path = Path(item["state_path"])
    if not state_path.exists():
        return True
    state = json.loads(state_path.read_text())
    return state.get("status") != "completed"


def build_summary_base(run_id: str, selected: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "run_id": run_id,
        "total_selected": len(selected),
        "completed": 0,
        "failed": 0,
        "timed_out": 0,
        "pending_estimate": len(selected),
        "current_index": 0,
        "current_job_key": None,
        "last_finished_job_key": None,
        "updated_at": datetime.now().astimezone().isoformat(),
        "results": [],
    }


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n")


def main() -> None:
    args = parse_args()
    run_dir = ROOT / "runs" / args.run_id
    manifest = load_manifest(run_dir)

    selected = manifest
    if args.only_pending:
        selected = [item for item in selected if is_pending(item)]

    if args.all or args.limit is None:
        selected = selected[args.start_index :]
    else:
        selected = selected[args.start_index : args.start_index + args.limit]

    logs_dir = run_dir / "logs"
    progress_path = logs_dir / "progress.json"
    failures_path = logs_dir / "failures.json"
    summary_path = logs_dir / "batch-summary.json"

    summary = build_summary_base(args.run_id, selected)
    failures: list[dict[str, Any]] = []
    write_json(progress_path, summary)
    write_json(failures_path, failures)

    for index, item in enumerate(selected, start=1):
        summary["current_index"] = index
        summary["current_job_key"] = item["job_key"]
        summary["updated_at"] = datetime.now().astimezone().isoformat()
        write_json(progress_path, summary)

        command = [
            sys.executable,
            str(ROOT / "run_one_job.py"),
            "--run-id",
            args.run_id,
            "--job-key",
            item["job_key"],
        ]

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False,
                timeout=args.item_timeout,
            )
            returncode = result.returncode
            status = "completed" if returncode == 0 else "failed"
            stdout = result.stdout
            stderr = result.stderr
        except subprocess.TimeoutExpired as exc:
            returncode = 124
            status = "timed_out"
            stdout = exc.stdout or ""
            stderr = exc.stderr or ""
            failures.append(
                {
                    "job_key": item["job_key"],
                    "status": status,
                    "error": "Item exceeded watchdog timeout",
                    "timestamp": datetime.now().astimezone().isoformat(),
                }
            )
            write_json(failures_path, failures)

        entry = {
            "index": index,
            "job_key": item["job_key"],
            "returncode": returncode,
            "status": status,
            "stdout": stdout,
            "stderr": stderr,
        }
        summary["results"].append(entry)

        if status == "completed":
            summary["completed"] += 1
        elif status == "timed_out":
            summary["timed_out"] += 1
        else:
            summary["failed"] += 1
            failures.append(
                {
                    "job_key": item["job_key"],
                    "status": status,
                    "error": stderr.strip() or "Unknown batch failure",
                    "timestamp": datetime.now().astimezone().isoformat(),
                }
            )
            write_json(failures_path, failures)

        summary["pending_estimate"] = max(summary["total_selected"] - index, 0)
        summary["last_finished_job_key"] = item["job_key"]
        summary["current_job_key"] = None
        summary["updated_at"] = datetime.now().astimezone().isoformat()
        write_json(progress_path, summary)

    final_summary = {
        "ok": summary["failed"] == 0 and summary["timed_out"] == 0,
        "run_id": args.run_id,
        "selected": summary["total_selected"],
        "succeeded": summary["completed"],
        "failed": summary["failed"],
        "timed_out": summary["timed_out"],
        "progress_path": str(progress_path),
        "failures_path": str(failures_path),
        "results": summary["results"],
    }
    write_json(summary_path, final_summary)
    print(
        json.dumps(
            {
                "ok": final_summary["ok"],
                "run_id": args.run_id,
                "selected": final_summary["selected"],
                "succeeded": final_summary["succeeded"],
                "failed": final_summary["failed"],
                "timed_out": final_summary["timed_out"],
                "summary_path": str(summary_path),
                "progress_path": str(progress_path),
                "failures_path": str(failures_path),
            },
            indent=2,
        )
    )

    if not final_summary["ok"]:
        sys.exit(1)


if __name__ == "__main__":
    main()