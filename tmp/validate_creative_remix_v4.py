#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMPTS = ROOT / "tools/game_refactoring/prompts/operators_v2"
WORKFLOW = ROOT / "tools/game_refactoring/scripts/game_workflow.py"

V4_FILES = [
    "00_creative_remix_v4_remix_inference_plus.md",
    "01_creative_remix_v4_world_design_superprompt.md",
    "02_creative_remix_v4_visuals_base.md",
    "03_creative_remix_v4_visual_ui_refine.md",
    "04_creative_remix_v4_final_mobile_repair_aggressive.md",
]

SOURCE_PROMPTS_THAT_MUST_NOT_BE_MODIFIED = [
    "00_creative_remix_v3_remix_inference.md",
    "01_creative_remix_v1_narrative.md",
    "02_creative_remix_v1_gameplay.md",
    "03_media_mapper.md",
    "04_creative_remix_v1_media_mapper.md",
    "03_creative_remix_v1_visuals.md",
    "05_creative_remix_v1_visual_judge.md",
    "06_creative_remix_v3_visual_ui_redesign.md",
    "09_creative_remix_v3_final_mobile_repair.md",
    "10_creative_remix_v3_level_adapter.md",
    "11_creative_remix_v3_multilevel_qa.md",
    "03_capture_mobile_screenshot.md",
]


def git_changed_files() -> set[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def validate() -> None:
    missing = [name for name in V4_FILES if not (PROMPTS / name).exists()]
    if missing:
        raise AssertionError(f"missing v4 prompt files: {missing}")

    for name in V4_FILES:
        text = (PROMPTS / name).read_text(encoding="utf-8")
        if "CREATIVE REMIX V4 PRODUCTION PROMPT" not in text:
            raise AssertionError(f"{name} missing v4 production marker")
        if "Source-Derived Instruction Library" not in text:
            raise AssertionError(f"{name} missing source-derived instruction library")
        if "Do not break mechanics" not in text:
            raise AssertionError(f"{name} missing mechanics invariant")

    workflow_text = WORKFLOW.read_text(encoding="utf-8")
    required_workflow_tokens = [
        '"creative_remix_v4": WorkflowDefinition(',
        '"id": "remix_inference_plus"',
        '"id": "world_design_superprompt"',
        '"id": "visuals_base"',
        '"id": "visual_ui_refine"',
        '"id": "final_mobile_repair_aggressive"',
    ]
    for token in required_workflow_tokens:
        if token not in workflow_text:
            raise AssertionError(f"workflow missing token: {token}")

    changed = git_changed_files()
    forbidden_changed = [
        f"tools/game_refactoring/prompts/operators_v2/{name}"
        for name in SOURCE_PROMPTS_THAT_MUST_NOT_BE_MODIFIED
        if f"tools/game_refactoring/prompts/operators_v2/{name}" in changed
    ]
    if forbidden_changed:
        raise AssertionError(f"source prompts were modified: {forbidden_changed}")

    print("creative_remix_v4_validation_ok")
    print("v4_prompt_count", len(V4_FILES))
    print("source_prompts_modified", 0)


if __name__ == "__main__":
    try:
        validate()
    except Exception as exc:
        print(f"creative_remix_v4_validation_failed: {exc}", file=sys.stderr)
        sys.exit(1)