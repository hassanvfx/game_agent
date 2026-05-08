#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from datetime import datetime, timezone
from pathlib import Path

from orchestration_state import load_json, recompute_run_state, update_game_state, write_json


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".bmp", ".ico"}
AUDIO_EXTENSIONS = {".mp3", ".wav", ".ogg", ".m4a", ".aac", ".flac"}

RUNTIME_IMAGE_RE = re.compile(r"""['"]([^'"]+\.(?:png|jpg|jpeg|gif|webp|svg|bmp|ico))['"]""", re.IGNORECASE)
RUNTIME_AUDIO_RE = re.compile(r"""['"]([^'"]+\.(?:mp3|wav|ogg|m4a|aac|flac))['"]""", re.IGNORECASE)
EXTERNAL_URL_RE = re.compile(r"https?://[^\s\"'()<>]+", re.IGNORECASE)
AUDIO_API_MARKERS = ("<audio", "new audio(", "audiocontext", "webkitAudioContext".lower())
IMAGE_API_MARKERS = ("<img", "new image(", "drawimage(", "background-image", "url(")

EMOJI_CATEGORY_MAP = {
    "food": "1f355.png",
    "drink": "1f964.png",
    "dessert": "1f369.png",
    "fruit": "1f34e.png",
    "vegetable": "1f955.png",
    "face": "1f600.png",
    "person": "1f642.png",
    "hand": "1f44b.png",
    "clothing": "1f455.png",
    "animal": "1f431.png",
    "pet": "1f436.png",
    "monster": "1f47e.png",
    "money": "1f4b0.png",
    "gem": "1f48e.png",
    "heart": "1f49b.png",
    "star": "2b50.png",
    "sparkle": "2728.png",
    "danger": "26a0-fe0f.png",
    "fire": "1f525.png",
    "nature": "1f33f.png",
    "tree": "1f333.png",
    "flower": "1f33b.png",
    "weather": "2601-fe0f.png",
    "sport": "26bd.png",
    "game": "1f3ae.png",
    "vehicle": "1f697.png",
    "travel": "2708-fe0f.png",
    "building": "1f3e0.png",
    "tech": "1f4bb.png",
    "tool": "1f6e0-fe0f.png",
    "music": "1f3b5.png",
    "book": "1f4d6.png",
    "symbol": "1f4a0.png",
    "warning": "26a0-fe0f.png",
    "generic": "2753.png",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create rewrite-planning artifacts for a prepared/analyzed run.")
    parser.add_argument("--run-dir", required=True, help="Path to a Game Obfuscator run directory.")
    return parser.parse_args()


def classify_emoji_category(text: str) -> tuple[str, str]:
    lowered = text.lower()

    keyword_groups = [
        ("food", ("food", "snack", "pizza", "burger", "sandwich", "meal")),
        ("drink", ("drink", "juice", "soda", "coffee", "tea", "boba")),
        ("dessert", ("dessert", "cake", "cookie", "candy", "donut", "icecream")),
        ("fruit", ("fruit", "apple", "banana", "orange", "berry", "grape")),
        ("vegetable", ("vegetable", "veggie", "carrot", "corn", "pepper")),
        ("face", ("avatar", "face", "smile", "happy", "sad", "emoji")),
        ("person", ("player", "character", "person", "human", "hero", "runner")),
        ("hand", ("hand", "tap", "click", "point", "touch", "swipe")),
        ("clothing", ("shirt", "hat", "shoe", "clothing", "dress", "armor")),
        ("animal", ("animal", "cat", "lion", "tiger", "bear", "fox")),
        ("pet", ("dog", "pet", "puppy", "kitten")),
        ("monster", ("monster", "alien", "ghost", "skull", "enemy", "creature")),
        ("money", ("coin", "gold", "money", "cash", "reward", "bank")),
        ("gem", ("gem", "diamond", "crystal", "jewel")),
        ("heart", ("heart", "life", "health", "hp", "heal")),
        ("star", ("star", "bonus", "collect", "pickup", "badge")),
        ("sparkle", ("spark", "sparkle", "magic", "glow", "shine")),
        ("danger", ("danger", "hazard", "bomb", "toxic", "warning", "trap")),
        ("fire", ("fire", "flame", "burn", "lava", "hot")),
        ("nature", ("nature", "leaf", "grass", "plant", "garden")),
        ("tree", ("tree", "forest", "wood", "branch")),
        ("flower", ("flower", "rose", "petal", "bloom", "sunflower")),
        ("weather", ("sun", "cloud", "rain", "storm", "snow", "weather")),
        ("sport", ("ball", "sport", "soccer", "basketball", "tennis")),
        ("game", ("game", "controller", "joystick", "arcade")),
        ("vehicle", ("car", "vehicle", "truck", "bike", "race", "kart")),
        ("travel", ("plane", "travel", "rocket", "ship", "train")),
        ("building", ("house", "home", "building", "city", "castle")),
        ("tech", ("computer", "laptop", "phone", "tech", "robot")),
        ("tool", ("tool", "hammer", "wrench", "gear", "build")),
        ("music", ("music", "song", "note", "guitar", "piano")),
        ("book", ("book", "card", "scroll", "paper", "letter")),
        ("symbol", ("icon", "symbol", "mark", "sign", "ui")),
        ("warning", ("warn", "alert", "caution")),
    ]

    for category, keywords in keyword_groups:
        if any(keyword in lowered for keyword in keywords):
            return category, "keyword_match"

    return "generic", "fallback"


def should_keep_external_url(url: str) -> bool:
    lowered = url.lower()
    documentation_hosts = (
        "github.com/",
        "tailwindcss.com/",
        "twitter.com/",
        "w3ctech.com/",
        "evilmartians.com/",
        "mths.be/",
    )
    return not any(host in lowered for host in documentation_hosts)


def plan_for_game(game_state: dict) -> dict[str, dict]:
    input_dir = Path(game_state["input_mirror_path"])
    artifacts_dir = Path(game_state["artifacts_path"])

    runtime_image_refs: list[dict] = []
    runtime_audio_refs: list[dict] = []
    external_runtime_refs: list[dict] = []
    seen_image_refs: set[tuple[str, str]] = set()
    seen_audio_refs: set[tuple[str, str]] = set()
    seen_external_refs: set[tuple[str, str]] = set()

    local_image_files = sorted(
        str(path.relative_to(input_dir)) for path in input_dir.rglob("*") if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    )
    local_audio_files = sorted(
        str(path.relative_to(input_dir)) for path in input_dir.rglob("*") if path.is_file() and path.suffix.lower() in AUDIO_EXTENSIONS
    )

    for file_path in sorted(path for path in input_dir.rglob("*") if path.is_file()):
        if file_path.suffix.lower() not in {".html", ".css", ".js"}:
            continue

        relative_path = str(file_path.relative_to(input_dir))
        text = file_path.read_text(encoding="utf-8", errors="ignore")
        lowered = text.lower()

        for match in RUNTIME_IMAGE_RE.findall(text):
            key = (relative_path, match)
            if key in seen_image_refs:
                continue
            seen_image_refs.add(key)
            category, reason = classify_emoji_category(match)
            runtime_image_refs.append(
                {
                    "source_file": relative_path,
                    "source_ref": match,
                    "category": category,
                    "replacement_emoji_asset": f"assets/emoji/{EMOJI_CATEGORY_MAP[category]}",
                    "mapping_reason": reason,
                }
            )

        for match in RUNTIME_AUDIO_RE.findall(text):
            key = (relative_path, match)
            if key in seen_audio_refs:
                continue
            seen_audio_refs.add(key)
            runtime_audio_refs.append(
                {
                    "source_file": relative_path,
                    "source_ref": match,
                    "usage_type": "audio_file_reference",
                    "planned_action": "remove_or_stub",
                }
            )

        for url in EXTERNAL_URL_RE.findall(text):
            if not should_keep_external_url(url):
                continue
            key = (relative_path, url)
            if key in seen_external_refs:
                continue
            seen_external_refs.add(key)
            external_runtime_refs.append(
                {
                    "source_file": relative_path,
                    "url": url,
                    "classification": "possible_runtime_dependency",
                }
            )

        if any(marker in lowered for marker in AUDIO_API_MARKERS):
            key = (relative_path, "audio_api_marker")
            if key not in seen_audio_refs:
                seen_audio_refs.add(key)
                runtime_audio_refs.append(
                    {
                        "source_file": relative_path,
                        "source_ref": "audio_api_marker",
                        "usage_type": "audio_api_usage",
                        "planned_action": "stub_runtime_calls",
                    }
                )

        if any(marker in lowered for marker in IMAGE_API_MARKERS) and not runtime_image_refs:
            category, reason = classify_emoji_category(relative_path)
            runtime_image_refs.append(
                {
                    "source_file": relative_path,
                    "source_ref": "image_api_marker",
                    "category": category,
                    "replacement_emoji_asset": f"assets/emoji/{EMOJI_CATEGORY_MAP[category]}",
                    "mapping_reason": reason,
                }
            )

    emoji_mapping_plan = {
        "generated_at": utc_now(),
        "game_id": game_state["game_id"],
        "local_image_files": local_image_files,
        "runtime_image_refs": runtime_image_refs,
        "emoji_asset_candidates": sorted({item["replacement_emoji_asset"] for item in runtime_image_refs}),
    }

    audio_removal_plan = {
        "generated_at": utc_now(),
        "game_id": game_state["game_id"],
        "local_audio_files": local_audio_files,
        "runtime_audio_refs": runtime_audio_refs,
        "default_stub_strategy": {
            "audio_element": "remove_dom_nodes_if_present",
            "audio_constructor": "replace_with_noop_audio_stub",
            "audio_context": "replace_with_noop_audio_context_stub",
        },
    }

    external_runtime_refs_plan = {
        "generated_at": utc_now(),
        "game_id": game_state["game_id"],
        "possible_runtime_external_refs": external_runtime_refs,
    }

    write_json(artifacts_dir / "emoji_mapping_plan.json", emoji_mapping_plan)
    write_json(artifacts_dir / "audio_removal_plan.json", audio_removal_plan)
    write_json(artifacts_dir / "external_runtime_refs.json", external_runtime_refs_plan)

    return {
        "emoji_mapping_plan": emoji_mapping_plan,
        "audio_removal_plan": audio_removal_plan,
        "external_runtime_refs": external_runtime_refs_plan,
    }


def main() -> None:
    args = parse_args()
    run_dir = Path(args.run_dir).resolve()
    manifest = load_json(run_dir / "input_manifest.json")
    run_state = load_json(run_dir / "run_state.json")
    recompute_run_state(run_dir, current_phase="rewrite_planning_started", note="Rewrite planning started.")

    games_planned = 0
    planning_failed = 0
    totals = {
        "runtime_image_ref_count": 0,
        "runtime_audio_ref_count": 0,
        "possible_runtime_external_ref_count": 0,
    }

    for game in manifest.get("games", []):
        game_id = game["game_id"]
        game_state_path = run_dir / "games" / game_id / "game_state.json"
        game_state = load_json(game_state_path)

        input_dir = Path(game_state["input_mirror_path"])
        update_game_state(
            run_dir,
            game_id,
            status="running",
            phase="rewrite_planning_started",
            last_error=None,
            mark_started=True,
            heartbeat=True,
            progress=True,
        )
        if not input_dir.exists():
            update_game_state(
                run_dir,
                game_id,
                status="failed",
                phase="rewrite_planning_failed",
                last_error=f"Input mirror path does not exist: {input_dir}",
                heartbeat=True,
                progress=True,
            )
            planning_failed += 1
            continue

        plans = plan_for_game(game_state)
        games_planned += 1

        totals["runtime_image_ref_count"] += len(plans["emoji_mapping_plan"]["runtime_image_refs"])
        totals["runtime_audio_ref_count"] += len(plans["audio_removal_plan"]["runtime_audio_refs"])
        totals["possible_runtime_external_ref_count"] += len(
            plans["external_runtime_refs"]["possible_runtime_external_refs"]
        )

        artifacts_dir = Path(game_state["artifacts_path"])
        update_game_state(
            run_dir,
            game_id,
            status="ready",
            phase="emoji_mapping_planned",
            last_error=None,
            heartbeat=True,
            progress=True,
            artifacts={
                "emoji_mapping_plan": str(artifacts_dir / "emoji_mapping_plan.json"),
                "audio_removal_plan": str(artifacts_dir / "audio_removal_plan.json"),
                "external_runtime_refs": str(artifacts_dir / "external_runtime_refs.json"),
            },
        )

    run_state["games_rewrite_planned"] = games_planned
    run_state["games_rewrite_planning_failed"] = planning_failed
    run_state["current_phase"] = "rewrite_planning_complete"
    run_state["status"] = "ready_for_rewrite" if planning_failed == 0 else "failed"
    run_state["rewrite_planning_totals"] = totals
    run_state["updated_at"] = utc_now()
    run_state.setdefault("notes", []).append("Rewrite-planning artifacts completed.")
    write_json(run_dir / "run_state.json", run_state)
    recompute_run_state(run_dir, current_phase="rewrite_planning_complete")

    print(run_dir)


if __name__ == "__main__":
    main()