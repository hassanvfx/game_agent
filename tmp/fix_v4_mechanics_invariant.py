#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROMPTS = ROOT / "tools/game_refactoring/prompts/operators_v2"

FILES = [
    "01_creative_remix_v4_world_design_superprompt.md",
    "02_creative_remix_v4_visuals_base.md",
    "03_creative_remix_v4_visual_ui_refine.md",
    "04_creative_remix_v4_final_mobile_repair_aggressive.md",
]

INSERTIONS = {
    "01_creative_remix_v4_world_design_superprompt.md": (
        "## Global mechanics invariant\n\n"
        "The static harness remains: do not break game mechanics."
    ),
    "02_creative_remix_v4_visuals_base.md": (
        "## Global mechanics invariant\n\n"
        "Do not break mechanics. Do not rewrite core game logic."
    ),
    "03_creative_remix_v4_visual_ui_refine.md": (
        "## Global mechanics invariant\n\n"
        "Do not break mechanics. Do not rewrite gameplay."
    ),
    "04_creative_remix_v4_final_mobile_repair_aggressive.md": (
        "## Global mechanics invariant\n\n"
        "Do not redesign the mechanics."
    ),
}


def main() -> None:
    for filename in FILES:
        path = PROMPTS / filename
        text = path.read_text(encoding="utf-8")
        if "Do not break mechanics." in text:
            continue
        needle = INSERTIONS[filename]
        replacement = needle + "\n\nDo not break mechanics."
        if needle not in text:
            raise RuntimeError(f"needle not found in {filename}")
        path.write_text(text.replace(needle, replacement, 1), encoding="utf-8")
    print("v4_mechanics_invariant_fixed")


if __name__ == "__main__":
    main()