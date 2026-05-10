#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from orchestration_state import load_json, recompute_run_state, update_game_state, write_json


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Apply a simple deterministic minification/obfuscation pass to mirrored game outputs."
    )
    parser.add_argument("--run-dir", required=True, help="Path to a Game Obfuscator run directory.")
    return parser.parse_args()


def mirror_directory(source: Path, destination: Path) -> None:
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(source, destination)


def run_transformer(target_dir: Path) -> dict:
    command = ["node", str(SCRIPTS_DIR / "transform_web_assets.js"), str(target_dir)]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "Web asset transformer failed.")
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Transformer did not return valid JSON: {exc}") from exc


def prune_retained_surface(target_dir: Path) -> dict:
    kept_files: list[str] = []
    removed_files: list[str] = []
    removed_dirs: list[str] = []

    for child in sorted(target_dir.iterdir(), key=lambda item: item.name):
        if child.name == "index.html":
            kept_files.append(child.name)
            continue
        if child.name == "assets" and child.is_dir():
            continue
        if child.is_dir():
            shutil.rmtree(child)
            removed_dirs.append(child.name)
        else:
            child.unlink()
            removed_files.append(child.name)

    assets_dir = target_dir / "assets"
    if assets_dir.exists():
        for file_path in sorted(assets_dir.rglob("*")):
            if not file_path.is_file():
                continue
            relative_path = file_path.relative_to(target_dir).as_posix()
            if file_path.suffix.lower() in {".js", ".css"}:
                kept_files.append(relative_path)
            else:
                file_path.unlink()
                removed_files.append(relative_path)

        for dir_path in sorted((path for path in assets_dir.rglob("*") if path.is_dir()), reverse=True):
            if any(dir_path.iterdir()):
                continue
            dir_path.rmdir()
            removed_dirs.append(dir_path.relative_to(target_dir).as_posix())

    return {
        "kept_files": kept_files,
        "removed_files": removed_files,
        "removed_dirs": removed_dirs,
    }


def obfuscate_game_output(run_dir: Path, game_id: str) -> dict:
    game_state_path = run_dir / "games" / game_id / "game_state.json"
    game_state = load_json(game_state_path)

    mirror_dir = Path(game_state["input_mirror_path"])
    output_dir = Path(game_state["output_path"])
    artifacts_dir = Path(game_state["artifacts_path"])
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    if not mirror_dir.exists():
        raise FileNotFoundError(f"Missing mirrored input directory: {mirror_dir}")
    if not (mirror_dir / "index.html").exists():
        raise FileNotFoundError(f"Missing mirrored index.html: {mirror_dir / 'index.html'}")

    mirror_directory(mirror_dir, output_dir)
    prune_report = prune_retained_surface(output_dir)
    transform_report = run_transformer(output_dir)

    report = {
        "generated_at": utc_now(),
        "game_id": game_id,
        "source_mirror_path": str(mirror_dir),
        "output_path": str(output_dir),
        "prune_report": prune_report,
        "transformer_report": transform_report,
    }
    write_json(artifacts_dir / "simple_obfuscation_report.json", report)
    return report


def main() -> None:
    args = parse_args()
    run_dir = Path(args.run_dir).resolve()
    manifest = load_json(run_dir / "input_manifest.json")
    run_state = load_json(run_dir / "run_state.json")

    recompute_run_state(
        run_dir,
        current_phase="simple_obfuscation_started",
        note="Simple deterministic minification/obfuscation started.",
    )

    obfuscated_games = 0
    obfuscation_failed = 0

    for game in manifest.get("games", []):
        game_id = game["game_id"]
        update_game_state(
            run_dir,
            game_id,
            status="running",
            phase="simple_obfuscation_started",
            last_error=None,
            heartbeat=True,
            progress=True,
            mark_started=True,
            increment_attempt=True,
        )

        try:
            report = obfuscate_game_output(run_dir, game_id)
        except Exception as exc:
            artifacts_dir = Path(load_json(run_dir / "games" / game_id / "game_state.json")["artifacts_path"])
            update_game_state(
                run_dir,
                game_id,
                status="failed",
                phase="simple_obfuscation_failed",
                last_error=str(exc),
                heartbeat=True,
                progress=True,
                mark_completed=True,
                artifacts={
                    "simple_obfuscation_report": str(artifacts_dir / "simple_obfuscation_report.json"),
                },
            )
            obfuscation_failed += 1
            continue

        obfuscated_games += 1
        artifacts_dir = Path(load_json(run_dir / "games" / game_id / "game_state.json")["artifacts_path"])
        update_game_state(
            run_dir,
            game_id,
            status="succeeded",
            phase="simple_obfuscation_complete",
            last_error=None,
            heartbeat=True,
            progress=True,
            mark_completed=True,
            artifacts={
                "simple_obfuscation_report": str(artifacts_dir / "simple_obfuscation_report.json"),
            },
            extra_fields={
                "simple_transform_summary": {
                    "html_files": len(report["transformer_report"].get("html_files", [])),
                    "css_files": len(report["transformer_report"].get("css_files", [])),
                    "js_files": len(report["transformer_report"].get("js_files", [])),
                    "pruned_removed_files": len(report["prune_report"].get("removed_files", [])),
                    "pruned_removed_dirs": len(report["prune_report"].get("removed_dirs", [])),
                }
            },
        )

    run_state["games_obfuscated"] = obfuscated_games
    run_state["games_obfuscation_failed"] = obfuscation_failed
    run_state["current_phase"] = "simple_obfuscation_complete"
    run_state["status"] = "completed" if obfuscation_failed == 0 else "completed_with_failures"
    run_state["updated_at"] = utc_now()
    run_state.setdefault("notes", []).append("Simple deterministic minification/obfuscation completed.")
    write_json(run_dir / "run_state.json", run_state)
    recompute_run_state(run_dir, current_phase="simple_obfuscation_complete")

    print(run_dir)


if __name__ == "__main__":
    main()