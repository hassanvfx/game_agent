#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path


PREPARE_INPUTS = Path("tools/game_refactoring/scripts/prepare_inputs.py")
RAW_ROOT = Path("games/raw")
TMP_ROOT = Path("tmp/prepare_inputs_metadata_fix")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate the centralized prepare_inputs metadata ignore fix with a synthetic copy-mode run scaffold."
    )
    parser.add_argument("--keep-temp", action="store_true", help="Keep the synthetic tmp run directory after validation.")
    return parser.parse_args()


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def pick_sample_games() -> list[Path]:
    contaminated = RAW_ROOT / "gamezone-00949d28-6fa6-4cc3-8b31-ff3d5791265b"
    clean = RAW_ROOT / "gamezone-0022d901-ea58-4a11-b909-fff27f0ee38f"
    missing = [str(path) for path in [clean, contaminated] if not path.exists()]
    if missing:
        raise SystemExit(f"Missing expected sample raw games: {missing}")
    return [clean.resolve(), contaminated.resolve()]


def build_synthetic_run_dir() -> tuple[Path, list[str]]:
    if TMP_ROOT.exists():
        shutil.rmtree(TMP_ROOT)
    run_dir = TMP_ROOT / "run_game_remixer_metadata_fix_synthetic"
    run_dir.mkdir(parents=True, exist_ok=True)

    sample_games = pick_sample_games()
    games_payload: list[dict] = []
    game_ids: list[str] = []
    for sample_source in sample_games:
        game_id = sample_source.name
        game_ids.append(game_id)
        games_payload.append(
            {
                "game_id": game_id,
                "display_name": game_id,
                "source_path": str(sample_source),
            }
        )
        write_json(
            run_dir / "games" / game_id / "game_state.json",
            {
                "game_id": game_id,
                "input_mirror_path": str((run_dir / "input" / game_id).resolve()),
                "status": "created",
                "current_phase": "run_created",
            },
        )

    write_json(run_dir / "input_manifest.json", {"games": games_payload})
    write_json(
        run_dir / "run_state.json",
        {
            "run_id": run_dir.name,
            "run_dir": str(run_dir.resolve()),
            "runs_root": str(TMP_ROOT.resolve()),
            "status": "created",
            "current_phase": "run_created",
            "games_total": len(games_payload),
            "games_mirrored": 0,
            "games_integrity_passed": 0,
            "games_integrity_failed": 0,
            "games_transform_completed": 0,
            "games_transform_failed": 0,
            "source_mode": "copy",
            "notes": ["Synthetic run scaffold for metadata ignore validation."],
        },
    )
    return run_dir.resolve(), game_ids


def main() -> None:
    args = parse_args()
    run_dir, game_ids = build_synthetic_run_dir()
    completed = subprocess.run(
        ["python3", str(PREPARE_INPUTS), "--run-dir", str(run_dir), "--source-mode", "copy"],
        capture_output=True,
        text=True,
        check=False,
    )

    run_state = load_json(run_dir / "run_state.json")
    integrity_report = load_json(run_dir / "integrity_report.json")
    input_root = run_dir / "input"
    metadata_matches = sorted(
        str(path)
        for path in input_root.rglob("*")
        if path.name == ".DS_Store" or path.name.startswith("._")
    )

    payload = {
        "synthetic": True,
        "run_dir": str(run_dir),
        "game_ids": game_ids,
        "command": completed.args,
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "run_state": {
            "status": run_state.get("status"),
            "current_phase": run_state.get("current_phase"),
            "games_mirrored": run_state.get("games_mirrored"),
            "games_integrity_passed": run_state.get("games_integrity_passed"),
            "games_integrity_failed": run_state.get("games_integrity_failed"),
            "source_mode": run_state.get("source_mode"),
        },
        "integrity_report_summary": {
            "games": len(integrity_report.get("games", [])),
            "all_passed": all(item.get("integrity_status") == "passed" for item in integrity_report.get("games", [])),
            "sample_pre_prepare_purge": (integrity_report.get("games") or [{}])[0].get("pre_prepare_purge"),
        },
        "remaining_metadata_artifacts_in_input": metadata_matches[:50],
        "remaining_metadata_artifact_count": len(metadata_matches),
    }
    print(json.dumps(payload, indent=2))

    if not args.keep_temp:
        shutil.rmtree(TMP_ROOT, ignore_errors=True)


if __name__ == "__main__":
    main()