#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare source games locally and record integrity status for a Game Remixer run.")
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--source-mode", choices=["copy", "inplace"], default="copy")
    return parser.parse_args()


def mirror_directory(source: Path, destination: Path) -> None:
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(source, destination)


def purge_prepared_directory(prepared_dir: Path) -> dict[str, list[str]]:
    kept: list[str] = []
    removed: list[str] = []

    for child in sorted(prepared_dir.iterdir(), key=lambda path: path.name):
        if child.name == "index.html" and child.is_file():
            kept.append(child.name)
            continue
        if child.name == "assets" and child.is_dir():
            kept.append(child.name + "/")
            continue
        if child.is_dir():
            shutil.rmtree(child)
            removed.append(child.name + "/")
        else:
            child.unlink()
            removed.append(child.name)

    return {
        "kept": kept,
        "removed": removed,
    }


def validate_source_directory(source: Path, game_id: str) -> None:
    if not source.exists():
        raise SystemExit(f"Cannot start flow for game '{game_id}': source_path does not exist: {source}")
    if not source.is_dir():
        raise SystemExit(f"Cannot start flow for game '{game_id}': source_path is not a directory: {source}")


def verify_integrity(prepared_dir: Path) -> tuple[str, list[str]]:
    issues: list[str] = []
    index_path = prepared_dir / "index.html"
    if not index_path.exists():
        issues.append("Missing index.html in prepared input.")
    status = "passed" if not issues else "failed"
    return status, issues


def main() -> None:
    args = parse_args()
    run_dir = Path(args.run_dir).resolve()
    manifest = load_json(run_dir / "input_manifest.json")
    run_state = load_json(run_dir / "run_state.json")

    mirrored = 0
    integrity_passed = 0
    integrity_failed = 0
    integrity_report = {
        "generated_at": utc_now(),
        "run_id": run_state["run_id"],
        "games": [],
    }

    for game in manifest.get("games", []):
        game_id = game["game_id"]
        source_path = Path(game["source_path"]).resolve()
        validate_source_directory(source_path, game_id)
        game_state_path = run_dir / "games" / game_id / "game_state.json"
        game_state = load_json(game_state_path)
        prepared_dir = Path(game_state["input_mirror_path"])

        purge_report = None
        if args.source_mode == "copy":
            mirror_directory(source_path, prepared_dir)
            purge_report = purge_prepared_directory(prepared_dir)
            mirrored += 1
        else:
            prepared_dir = source_path
            game_state["input_mirror_path"] = str(prepared_dir)

        integrity_status, issues = verify_integrity(prepared_dir)
        if integrity_status == "passed":
            integrity_passed += 1
            next_phase = "input_integrity_passed"
            last_error = None
        else:
            integrity_failed += 1
            next_phase = "input_integrity_failed"
            last_error = "; ".join(issues)

        game_state["status"] = "ready" if integrity_status == "passed" else "failed"
        game_state["current_phase"] = next_phase
        game_state["integrity_status"] = integrity_status
        game_state["last_error"] = last_error
        game_state["updated_at"] = utc_now()
        write_json(game_state_path, game_state)

        integrity_report["games"].append(
            {
                "game_id": game_id,
                "source_path": str(source_path),
                "input_mirror_path": str(prepared_dir),
                "integrity_status": integrity_status,
                "issues": issues,
                "pre_prepare_purge": purge_report,
            }
        )

    run_state["games_mirrored"] = mirrored
    run_state["source_mode"] = args.source_mode
    run_state["games_integrity_passed"] = integrity_passed
    run_state["games_integrity_failed"] = integrity_failed
    run_state["status"] = "ready" if integrity_failed == 0 else "failed"
    run_state["current_phase"] = "inputs_prepared"
    run_state["updated_at"] = utc_now()
    run_state.setdefault("notes", []).append("Local input mirroring and integrity verification completed.")
    if args.source_mode == "copy":
        run_state.setdefault("notes", []).append(
            "Prepared copied inputs were purged before pipeline execution to keep only index.html and assets/."
        )
    else:
        run_state.setdefault("notes", []).append(
            "Prepared input purge was skipped because source_mode=inplace and the external source remains untouched."
        )
    write_json(run_dir / "run_state.json", run_state)
    write_json(run_dir / "integrity_report.json", integrity_report)

    print(run_dir)


if __name__ == "__main__":
    main()