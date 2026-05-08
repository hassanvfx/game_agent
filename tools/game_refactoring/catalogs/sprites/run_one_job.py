#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
KIE_API_DIR = (ROOT.parent.parent.parent / "kie-api").resolve()
LIVE_DIR = ROOT / "live"
DEFAULT_RUN_ID = "initial-sample"
DEFAULT_JOB_KEY = "assets/images/sprites/runner/player_runner"


def run_cli(command: list[str]) -> dict[str, Any]:
    result = subprocess.run(
        command,
        cwd=KIE_API_DIR,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Command failed ({result.returncode}): {' '.join(command)}\n{result.stdout}\n{result.stderr}"
        )
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"CLI did not return JSON:\n{result.stdout}") from exc


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n")


def load_manifest_item(run_dir: Path, job_key: str) -> dict[str, Any]:
    manifest_path = run_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    for item in manifest:
        if item["job_key"] == job_key:
            return item
    raise KeyError(f"Job key not found in manifest: {job_key}")


def build_state_paths(run_dir: Path, item: dict[str, Any]) -> tuple[Path, Path, Path]:
    job_file = Path(item["job_file_path"])
    state_file = Path(item["state_path"])
    output_file = Path(item["output_abspath"])
    if not str(job_file).startswith(str(run_dir)):
        raise RuntimeError("Job file path is outside run directory")
    if not str(state_file).startswith(str(run_dir)):
        raise RuntimeError("State file path is outside run directory")
    if not str(output_file).startswith(str(run_dir)):
        raise RuntimeError("Output file path is outside run directory")
    return job_file, state_file, output_file


def submit_job(item: dict[str, Any], job_file: Path) -> dict[str, Any]:
    command = [
        str(KIE_API_DIR / ".venv/bin/kie-cli"),
        "image",
        "gpt-image-2",
        "--prompt",
        item["composed_prompt"],
        "--aspect-ratio",
        "1:1" if item["asset_kind"] == "sprite_transparent" else "16:9",
        "--resolution",
        "1K",
        "--save-job",
        str(job_file),
        "--json",
    ]
    return run_cli(command)


def wait_for_job(job_file: Path) -> dict[str, Any]:
    command = [
        str(KIE_API_DIR / ".venv/bin/kie-cli"),
        "wait",
        "--job-file",
        str(job_file),
        "--poll-interval",
        "5",
        "--timeout",
        "240",
        "--json",
    ]
    return run_cli(command)


def download_output(url: str, output_file: Path) -> None:
    output_file.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        [
            "curl",
            "-L",
            "--fail",
            "-A",
            "Mozilla/5.0",
            "-o",
            str(output_file),
            url,
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Download failed ({result.returncode}) for {url}\n{result.stdout}\n{result.stderr}"
        )


def publish_to_live(item: dict[str, Any], output_file: Path) -> Path:
    live_path = LIVE_DIR / item["output_relpath"]
    live_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(output_file, live_path)
    return live_path


def build_state(item: dict[str, Any], status: str, **extra: Any) -> dict[str, Any]:
    state = {
        "job_key": item["job_key"],
        "name": item["name"],
        "asset_kind": item["asset_kind"],
        "status": status,
        "updated_at": datetime.now().astimezone().isoformat(),
        "source_url": item["source_url"],
        "output_abspath": item["output_abspath"],
        "job_file_path": item["job_file_path"],
        "state_path": item["state_path"],
    }
    state.update(extra)
    return state


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Submit, wait, and download one sprite job end-to-end.")
    parser.add_argument("--run-id", default=DEFAULT_RUN_ID)
    parser.add_argument("--job-key", default=DEFAULT_JOB_KEY)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_dir = ROOT / "runs" / args.run_id
    item = load_manifest_item(run_dir, args.job_key)
    job_file, state_file, output_file = build_state_paths(run_dir, item)

    write_json(state_file, build_state(item, "submitting"))
    submitted = submit_job(item, job_file)
    write_json(state_file, build_state(item, "submitted", submit_result=submitted))

    write_json(state_file, build_state(item, "waiting", submit_result=submitted))
    waited = wait_for_job(job_file)
    write_json(state_file, build_state(item, waited["status"], submit_result=submitted, wait_result=waited))

    output_url = waited.get("outputUrl")
    if waited.get("status") != "succeeded" or not output_url:
        raise RuntimeError(f"Job did not succeed cleanly: {json.dumps(waited, indent=2)}")

    write_json(state_file, build_state(item, "downloading", submit_result=submitted, wait_result=waited))
    download_output(output_url, output_file)
    write_json(state_file, build_state(item, "publishing", submit_result=submitted, wait_result=waited, downloaded_from=output_url, final_output=str(output_file)))
    live_path = publish_to_live(item, output_file)
    write_json(
        state_file,
        build_state(
            item,
            "completed",
            submit_result=submitted,
            wait_result=waited,
            downloaded_from=output_url,
            final_output=str(output_file),
            published_path=str(live_path),
            published_from_run=args.run_id,
        ),
    )

    print(
        json.dumps(
            {
                "ok": True,
                "run_id": args.run_id,
                "job_key": args.job_key,
                "job_id": waited["jobId"],
                "status": "completed",
                "output_file": str(output_file),
                "live_path": str(live_path),
                "output_url": output_url,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)