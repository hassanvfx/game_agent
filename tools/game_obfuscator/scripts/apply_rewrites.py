#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
from datetime import datetime, timezone
from pathlib import Path

from orchestration_state import load_json, recompute_run_state, update_game_state, write_json

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".bmp", ".ico"}
AUDIO_EXTENSIONS = {".mp3", ".wav", ".ogg", ".m4a", ".aac", ".flac"}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Apply conservative rewrite plans to a Game Obfuscator run.")
    parser.add_argument("--run-dir", required=True, help="Path to a Game Obfuscator run directory.")
    return parser.parse_args()


def reset_directory(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def copy_tree_without_audio(source: Path, destination: Path) -> list[str]:
    removed_audio_files: list[str] = []

    for file_path in sorted(path for path in source.rglob("*") if path.is_file()):
        relative_path = file_path.relative_to(source)
        target_path = destination / relative_path
        target_path.parent.mkdir(parents=True, exist_ok=True)

        if file_path.suffix.lower() in AUDIO_EXTENSIONS:
            removed_audio_files.append(str(relative_path))
            continue

        shutil.copy2(file_path, target_path)

    return removed_audio_files


def copy_selected_emoji_assets(emoji_assets: list[str], destination_root: Path) -> list[str]:
    copied_assets: list[str] = []
    emoji_source_root = Path("emoji-images-1.2.1/imgs")
    emoji_destination_root = destination_root / "assets" / "emoji"

    for asset_path in sorted(set(emoji_assets)):
        filename = Path(asset_path).name
        source_path = emoji_source_root / filename
        destination_path = emoji_destination_root / filename
        destination_path.parent.mkdir(parents=True, exist_ok=True)

        if source_path.exists():
            shutil.copy2(source_path, destination_path)
            copied_assets.append(str(destination_path.relative_to(destination_root)))

    return copied_assets


def apply_text_replacements(
    output_root: Path,
    emoji_plan: dict,
    audio_plan: dict,
) -> tuple[list[dict], list[dict]]:
    replacement_log: list[dict] = []
    audio_stub_log: list[dict] = []

    for file_path in sorted(path for path in output_root.rglob("*") if path.is_file()):
        if file_path.suffix.lower() not in {".html", ".css", ".js"}:
            continue

        original_text = file_path.read_text(encoding="utf-8", errors="ignore")
        updated_text = original_text
        relative_path = str(file_path.relative_to(output_root))

        for item in emoji_plan.get("runtime_image_refs", []):
            if item["source_file"] != relative_path:
                continue
            source_ref = item["source_ref"]
            replacement_ref = item["replacement_emoji_asset"]
            if source_ref == "image_api_marker":
                continue
            if source_ref in updated_text:
                updated_text = updated_text.replace(source_ref, replacement_ref)
                replacement_log.append(
                    {
                        "file": relative_path,
                        "kind": "emoji_ref_rewrite",
                        "source_ref": source_ref,
                        "replacement_ref": replacement_ref,
                    }
                )

        if relative_path.endswith((".html", ".js")):
            lowered = updated_text.lower()
            audio_marker_detected = False
            for item in audio_plan.get("runtime_audio_refs", []):
                if item["source_file"] != relative_path:
                    continue

                source_ref = item["source_ref"]
                if source_ref != "audio_api_marker" and source_ref in updated_text:
                    updated_text = updated_text.replace(source_ref, "")
                    audio_stub_log.append(
                        {
                            "file": relative_path,
                            "kind": "audio_ref_removed",
                            "source_ref": source_ref,
                        }
                    )

                if source_ref == "audio_api_marker":
                    audio_marker_detected = True

            if audio_marker_detected and "<!-- game_obfuscator_audio_stub -->" not in updated_text:
                stub = (
                    "\n<script>\n"
                    "window.Audio=function(){return {play(){},pause(){},load(){},addEventListener(){},removeEventListener(){}}};\n"
                    "window.AudioContext=window.AudioContext||function(){return {close(){},resume(){},suspend(){}}};\n"
                    "window.webkitAudioContext=window.webkitAudioContext||window.AudioContext;\n"
                    "</script>\n<!-- game_obfuscator_audio_stub -->\n"
                )
                if "</body>" in updated_text:
                    updated_text = updated_text.replace("</body>", f"{stub}</body>")
                else:
                    updated_text += stub
                audio_stub_log.append(
                    {
                        "file": relative_path,
                        "kind": "audio_api_stub_inserted",
                        "source_ref": "audio_api_marker",
                    }
                )

        if updated_text != original_text:
            file_path.write_text(updated_text, encoding="utf-8")

    return replacement_log, audio_stub_log


def apply_game_rewrite(game_state: dict) -> dict:
    input_dir = Path(game_state["input_mirror_path"])
    output_dir = Path(game_state["output_path"])
    artifacts_dir = Path(game_state["artifacts_path"])

    emoji_plan = load_json(artifacts_dir / "emoji_mapping_plan.json")
    audio_plan = load_json(artifacts_dir / "audio_removal_plan.json")
    external_plan = load_json(artifacts_dir / "external_runtime_refs.json")

    reset_directory(output_dir)
    removed_audio_files = copy_tree_without_audio(input_dir, output_dir)
    copied_emoji_assets = copy_selected_emoji_assets(emoji_plan.get("emoji_asset_candidates", []), output_dir)
    replacement_log, audio_stub_log = apply_text_replacements(output_dir, emoji_plan, audio_plan)

    copied_assets_report = {
        "generated_at": utc_now(),
        "game_id": game_state["game_id"],
        "copied_emoji_assets": copied_emoji_assets,
    }

    audio_stub_report = {
        "generated_at": utc_now(),
        "game_id": game_state["game_id"],
        "removed_audio_files": removed_audio_files,
        "audio_stub_actions": audio_stub_log,
    }

    rewrite_report = {
        "generated_at": utc_now(),
        "game_id": game_state["game_id"],
        "replacement_log": replacement_log,
        "removed_audio_file_count": len(removed_audio_files),
        "copied_emoji_asset_count": len(copied_emoji_assets),
        "possible_runtime_external_ref_count": len(external_plan.get("possible_runtime_external_refs", [])),
    }

    write_json(artifacts_dir / "copied_emoji_assets.json", copied_assets_report)
    write_json(artifacts_dir / "audio_stub_report.json", audio_stub_report)
    write_json(artifacts_dir / "rewrite_report.json", rewrite_report)

    return {
        "copied_emoji_assets": copied_assets_report,
        "audio_stub_report": audio_stub_report,
        "rewrite_report": rewrite_report,
    }


def main() -> None:
    args = parse_args()
    run_dir = Path(args.run_dir).resolve()
    manifest = load_json(run_dir / "input_manifest.json")
    run_state = load_json(run_dir / "run_state.json")
    recompute_run_state(run_dir, current_phase="rewrite_started", note="Rewrite application started.")

    rewritten_games = 0
    rewrite_failed = 0
    total_removed_audio_files = 0
    total_copied_emoji_assets = 0

    for game in manifest.get("games", []):
        game_id = game["game_id"]
        game_state_path = run_dir / "games" / game_id / "game_state.json"
        game_state = load_json(game_state_path)

        artifacts_dir = Path(game_state["artifacts_path"])
        update_game_state(
            run_dir,
            game_id,
            status="running",
            phase="rewrite_started",
            last_error=None,
            mark_started=True,
            heartbeat=True,
            progress=True,
        )
        required_artifacts = [
            artifacts_dir / "emoji_mapping_plan.json",
            artifacts_dir / "audio_removal_plan.json",
            artifacts_dir / "external_runtime_refs.json",
        ]
        missing = [str(path) for path in required_artifacts if not path.exists()]
        if missing:
            update_game_state(
                run_dir,
                game_id,
                status="failed",
                phase="rewrite_failed",
                last_error=f"Missing rewrite-planning artifacts: {', '.join(missing)}",
                heartbeat=True,
                progress=True,
            )
            rewrite_failed += 1
            continue

        reports = apply_game_rewrite(game_state)
        rewritten_games += 1
        total_removed_audio_files += len(reports["audio_stub_report"]["removed_audio_files"])
        total_copied_emoji_assets += len(reports["copied_emoji_assets"]["copied_emoji_assets"])

        update_game_state(
            run_dir,
            game_id,
            status="ready",
            phase="rewrite_complete",
            last_error=None,
            heartbeat=True,
            progress=True,
            artifacts={
                "rewrite_report": str(artifacts_dir / "rewrite_report.json"),
                "copied_emoji_assets": str(artifacts_dir / "copied_emoji_assets.json"),
                "audio_stub_report": str(artifacts_dir / "audio_stub_report.json"),
            },
        )

    run_state["games_rewritten"] = rewritten_games
    run_state["games_rewrite_failed"] = rewrite_failed
    run_state["current_phase"] = "rewrite_complete"
    run_state["status"] = "ready_for_bundling" if rewrite_failed == 0 else "failed"
    run_state["rewrite_totals"] = {
        "removed_audio_file_count": total_removed_audio_files,
        "copied_emoji_asset_count": total_copied_emoji_assets,
    }
    run_state["updated_at"] = utc_now()
    run_state.setdefault("notes", []).append("Conservative rewrite pass completed.")
    write_json(run_dir / "run_state.json", run_state)
    recompute_run_state(run_dir, current_phase="rewrite_complete")

    print(run_dir)


if __name__ == "__main__":
    main()