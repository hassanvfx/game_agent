#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path("/Users/hassan/repos/game_agent")
RUNS_ROOT = Path("/Volumes/HDD2026/output")
GAME_ID = "gamezone-3fefc41a-1c39-4dcb-808f-183207e990e7"
RUNS = [
    "run_v4_brainrot_momsday_retry_20260509T160832Z",
    "run_v4_brainrot_momsday_retry2_20260509T174740Z",
    "run_v4_brainrot_momsday_vatsal107_model55_c1_20260509T084144Z",
    "run_v4_flappy_bird_pending_manual_20260510T113810Z",
    "run_v4_flappy_bird_pending_manual_20260510T121747Z",
    "run_v4_flappy_bird_retry_20260509T160602Z",
    "run_v4_flappy_bird_retry2_20260509T174740Z",
    "run_v4_flappy_bird_vatsal107_model55_c1_20260509T085122Z",
    "run_v4_harry_potter_retry_20260509T160354Z",
    "run_v4_harry_potter_retry2_20260509T174740Z",
    "run_v4_harry_potter_vatsal107_model55_c1_20260509T083751Z",
    "run_v4_rick_morty_retry_20260509T161119Z",
    "run_v4_rick_morty_retry2_20260509T174740Z",
    "run_v4_rick_morty_retry2_20260510T054341Z",
    "run_v4_rick_morty_retry2_20260510T080658Z",
    "run_v4_rick_morty_retry2_20260510T082742Z",
    "run_v4_rick_morty_vatsal107_model55_c1_20260509T083929Z",
]


def summarize_json(path: Path) -> dict:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as error:  # noqa: BLE001
        return {"path": str(path), "error": str(error)}

    if not isinstance(payload, dict):
        return {"path": str(path), "type": type(payload).__name__}

    return {
        "path": str(path),
        "keys": sorted(payload.keys()),
        "has_game_id": bool(payload.get("game_id")),
        "has_semantic_tags": bool(payload.get("semantic_tags")),
        "has_identity": bool(payload.get("identity")),
        "has_mechanics_classification": bool(payload.get("mechanics_classification")),
        "has_recreation_prompt_markdown": bool(payload.get("recreation_prompt_markdown")),
        "has_blueprint_markdown": bool(payload.get("blueprint_markdown")),
        "has_screenshots_png": bool(payload.get("screenshots_png")),
        "has_screenshots_jpg": bool(payload.get("screenshots_jpg")),
    }


def main() -> None:
    matches = []

    for run in RUNS:
        game_dir = RUNS_ROOT / run / "output" / GAME_ID
        if not game_dir.exists():
            continue

        json_summaries = [summarize_json(path) for path in sorted(game_dir.glob("*.json"))]
        markdown_files = sorted(path.name for path in game_dir.glob("*.md"))
        screenshot_files = sorted(path.relative_to(game_dir).as_posix() for path in game_dir.rglob("*") if path.is_file() and path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"} and "screenshot" in path.name.lower())

        matches.append(
            {
                "run": run,
                "game_dir": str(game_dir),
                "json_files": json_summaries,
                "markdown_files": markdown_files,
                "screenshot_files_sample": screenshot_files[:10],
            }
        )

    print(json.dumps({"game_id": GAME_ID, "matches": matches}, indent=2))


if __name__ == "__main__":
    main()