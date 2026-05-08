#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.media_policy import build_media_policy_report


FIXTURE_WORKSPACE = Path(
    "runs/run_game_remixer_20260501T093715Z/games/9c1ce83a-9ed6-45e9-aed0-0241d23d6f16/"
    "operator_pipeline/stage_03_media_mapper/attempt_01/workspace"
)


def main() -> int:
    workspace = FIXTURE_WORKSPACE.resolve()
    report = build_media_policy_report(workspace)

    media_refs = report.get("actionable_media_replacement_candidate_refs", [])
    font_refs = report.get("actionable_font_replacement_candidate_refs", [])

    expected_font_ref = "assets/fonts.googleapis.com/css2-family_Press_Start_2P_display_swap.css"
    expected_font_binary_ref = "../../../../../../../../assets/fonts.gstatic.com/s/pressstart2p/v16/e3t4euO8T-267oIAQAu6jDQyK0nS.ttf"
    expected_audio_refs = {
        "assets/inferred/infer-audio-01.mp3",
        "assets/inferred/infer-audio-02.mp3",
    }
    allowed_vercel_audio_ref = "https://gamezone-virid.vercel.app/assets/audios/music/action_loop_01.mp3"
    allowed_google_font_css = "https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap"
    allowed_google_font_ttf = "https://fonts.gstatic.com/s/pressstart2p/v16/e3t4euO8T-267oIAQAu6jDQyK0nS.ttf"

    failures: list[str] = []

    if not isinstance(media_refs, list):
        failures.append("actionable_media_replacement_candidate_refs is not a list")
        media_refs = []
    if not isinstance(font_refs, list):
        failures.append("actionable_font_replacement_candidate_refs is not a list")
        font_refs = []

    missing_audio_refs = sorted(expected_audio_refs.difference(set(media_refs)))
    if missing_audio_refs:
        failures.append(f"missing expected media refs: {missing_audio_refs}")

    if expected_font_ref not in font_refs:
        failures.append(f"missing expected font ref: {expected_font_ref}")

    if expected_font_binary_ref not in font_refs:
        failures.append(f"missing expected font binary ref: {expected_font_binary_ref}")

    if allowed_vercel_audio_ref in media_refs:
        failures.append(f"allowed Vercel audio ref should not remain actionable: {allowed_vercel_audio_ref}")

    if allowed_google_font_css in font_refs:
        failures.append(f"allowed Google font css should not remain actionable: {allowed_google_font_css}")

    if allowed_google_font_ttf in font_refs:
        failures.append(f"allowed Google font ttf should not remain actionable: {allowed_google_font_ttf}")

    summary = {
        "workspace": str(workspace),
        "media_refs": media_refs,
        "font_refs": font_refs,
        "allowed_vercel_audio_ref": allowed_vercel_audio_ref,
        "allowed_google_font_css": allowed_google_font_css,
        "allowed_google_font_ttf": allowed_google_font_ttf,
        "failures": failures,
    }
    print(json.dumps(summary, indent=2))

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())