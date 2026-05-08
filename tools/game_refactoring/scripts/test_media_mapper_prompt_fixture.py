#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.media_policy import build_media_policy_report
from scripts.operator_registry_v2 import load_registry
from scripts.run_operator_pipeline_game import build_operator_prompt_text


FIXTURE_WORKSPACE = Path(
    "runs/run_game_remixer_20260501T093715Z/games/9c1ce83a-9ed6-45e9-aed0-0241d23d6f16/"
    "operator_pipeline/stage_03_media_mapper/attempt_01/workspace"
)


def main() -> int:
    workspace = FIXTURE_WORKSPACE.resolve()
    report = build_media_policy_report(workspace)
    registry = load_registry()
    operator = next(op for op in registry.operators if op.id == "media_mapper")

    run_state = {
        "run_id": "fixture_run",
        "run_dir": "unknown",
        "selected_style_id": "neutral_prototype",
        "remix_prompt": "Harry Potter",
        "operator_pipeline_v2": {
            "max_retries_per_stage": 3,
        },
    }
    game_state = {
        "game_id": "fixture_game",
        "display_name": "Harry Potter",
    }

    prompt = build_operator_prompt_text(
        run_state=run_state,
        game_state=game_state,
        operator=operator,
        attempt_number=1,
        attempt_workspace=workspace,
        current_workspace=workspace,
        adapted_spec_dir=None,
        workspace_catalogs={},
        potential_urls_to_remove=report.get("potential_urls_to_remove", []),
        media_replacement_candidates=report.get("actionable_media_replacement_candidate_refs", []),
        normalized_media_replacement_refs=report.get("normalized_media_replacement_refs", []),
        media_cleanup_plan=report.get("media_cleanup_plan", []),
        font_replacement_candidates=report.get("actionable_font_replacement_candidate_refs", []),
        approved_icon_vocabulary=report.get("approved_icon_vocabulary", []),
    )

    required_snippets = [
        "REQUIRED URLs to remove for this attempt:",
        "REQUIRED media references to replace or remap for this attempt:",
        "assets/inferred/infer-audio-01.mp3",
        "assets/inferred/infer-audio-02.mp3",
        "assets/fonts.googleapis.com/css2-family_Press_Start_2P_display_swap.css",
        "## Generic Replacement Examples",
        "## Failure Criteria",
        "this section is fixed in the prompt",
    ]
    forbidden_snippets = [
        "Normalized placeholder-safe destination contract for those actionable media replacements:",
        "Post-replacement cleanup plan for obsolete risky refs:",
    ]

    failures = [snippet for snippet in required_snippets if snippet not in prompt]
    forbidden_present = [snippet for snippet in forbidden_snippets if snippet in prompt]
    if forbidden_present:
        failures.append(f"forbidden prompt sections still present: {forbidden_present}")

    summary = {
        "workspace": str(workspace),
        "required_snippets": required_snippets,
        "forbidden_snippets": forbidden_snippets,
        "missing_snippets": [snippet for snippet in required_snippets if snippet not in prompt],
        "forbidden_present": forbidden_present,
    }
    print(json.dumps(summary, indent=2))

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())