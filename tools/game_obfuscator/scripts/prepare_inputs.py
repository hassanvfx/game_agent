#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
from datetime import datetime, timezone
from pathlib import Path

from orchestration_state import load_json, recompute_run_state, update_game_state, write_json


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Mirror source games locally and record integrity status for a Game Obfuscator run."
    )
    parser.add_argument("--run-dir", required=True, help="Path to a Game Obfuscator run directory.")
    return parser.parse_args()


def mirror_directory(source: Path, destination: Path) -> None:
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(source, destination)


def verify_integrity(mirror_dir: Path) -> tuple[str, list[str]]:
    issues: list[str] = []
    index_path = mirror_dir / "index.html"
    if not index_path.exists():
        issues.append("Missing index.html in mirrored input.")

    status = "passed" if not issues else "failed"
    return status, issues


def main() -> None:
    args = parse_args()
    run_dir = Path(args.run_dir).resolve()

    manifest = load_json(run_dir / "input_manifest.json")
    run_state = load_json(run_dir / "run_state.json")
    recompute_run_state(run_dir, current_phase="prepare_inputs_started", note="Input preparation started.")

    prepared = 0
    integrity_passed = 0
    integrity_failed = 0

    integrity_report = {
        "generated_at": utc_now(),
        "run_id": run_state["run_id"],
        "games": [],
    }

    for game in manifest.get("games", []):
        game_id = game["game_id"]
        entry_key = game["entry_key"]
        source_path = Path(game["source_path"]).resolve()
        game_state_path = run_dir / "games" / entry_key / "game_state.json"
        game_state = load_json(game_state_path)
        mirror_dir = Path(game_state["input_mirror_path"])

        update_game_state(
            run_dir,
            entry_key,
            status="running",
            phase="input_prepare_started",
            last_error=None,
            mark_started=True,
            heartbeat=True,
            progress=True,
        )

        issues: list[str] = []
        if not source_path.exists():
            issues.append(f"Source path does not exist: {source_path}")
        elif not source_path.is_dir():
            issues.append(f"Source path is not a directory: {source_path}")

        if not issues:
            mirror_directory(source_path, mirror_dir)
            prepared += 1
            integrity_status, integrity_issues = verify_integrity(mirror_dir)
            issues.extend(integrity_issues)
        else:
            integrity_status = "failed"

        if integrity_status == "passed":
            integrity_passed += 1
            next_phase = "input_prepared"
            status = "ready"
            last_error = None
        else:
            integrity_failed += 1
            next_phase = "input_prepare_failed"
            status = "failed"
            last_error = "; ".join(issues) if issues else "Unknown integrity failure."

        update_game_state(
            run_dir,
            entry_key,
            status=status,
            phase=next_phase,
            last_error=last_error,
            heartbeat=True,
            progress=True,
            artifacts={
                "integrity_report": str(run_dir / "integrity_report.json"),
            },
            extra_fields={
                "integrity_status": integrity_status,
            },
        )

        integrity_report["games"].append(
            {
                "entry_key": entry_key,
                "game_id": game_id,
                "display_name": game.get("display_name"),
                "source_path": str(source_path),
                "input_mirror_path": str(mirror_dir),
                "integrity_status": integrity_status,
                "issues": issues,
            }
        )

    run_state["games_prepared"] = prepared
    run_state["games_integrity_passed"] = integrity_passed
    run_state["games_integrity_failed"] = integrity_failed
    run_state["status"] = "ready" if integrity_failed == 0 else "failed"
    run_state["current_phase"] = "inputs_prepared"
    run_state["updated_at"] = utc_now()
    run_state.setdefault("notes", []).append("Local input mirroring and integrity verification completed.")
    write_json(run_dir / "run_state.json", run_state)
    write_json(run_dir / "integrity_report.json", integrity_report)
    recompute_run_state(run_dir, current_phase="prepare_inputs_complete")

    print(run_dir)


if __name__ == "__main__":
    main()