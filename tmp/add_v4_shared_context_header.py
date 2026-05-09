#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROMPTS = ROOT / "tools/game_refactoring/prompts/operators_v2"
JOURNAL = ROOT / "docs/journals/creative-remix-v4-merged-prompts.md"

TARGETS = [
    PROMPTS / "00_creative_remix_v4_remix_inference_plus.md",
    PROMPTS / "01_creative_remix_v4_world_design_superprompt.md",
    PROMPTS / "03_creative_remix_v4_visuals_unified.md",
    PROMPTS / "04_creative_remix_v4_final_mobile_repair_aggressive.md",
]

HEADER = """## Remix v4 Shared Context

As general context:

Remix v4 in brief:

## Stages
1. **`remix_inference_plus`**
2. **`world_design_superprompt`**
3. **`visuals_unified`**
4. **`final_mobile_repair_aggressive`**

## Stage tags

### 1) `remix_inference_plus`
- #mechanic-decomposition
- #complexity-profile
- #5-level-progression
- #1.5-level-core
- #visual-evolution-plan
- #procedural-art-system
- #preserve-mechanics
- #plan-authored-world

### 2) `world_design_superprompt`
- #authored-world
- #narrative-gameplay-media-merge
- #theme-mapping
- #mechanic-aware-framing
- #progression-support
- #procedural-background-plan
- #replace-boring-static-bg
- #remix-theme-json
- #preserve-mechanics

### 3) `visuals_unified`
- #procedural-visual-transformation
- #animated-background
- #motion-graphics
- #recognizable-characters-items-props
- #ui-hud-refinement
- #mobile-readable
- #replace-stock-static-bg
- #screenshot-guided-visual-check
- #playwright-discipline
- #preserve-mechanics

### 4) `final_mobile_repair_aggressive`
- #code-level-console-fixes
- #mobile-actionability
- #aggressive-runtime-exploration
- #monkey-tapping
- #3-to-4-screen-states
- #screenshot-guided-ui-repair
- #ignore-nonblocking-media-404s
- #fix-deterministic-cdn-path-bugs-only
- #preserve-mechanics

## Core policies
- #default-model-gpt55
- #do-not-break-mechanics
- #procedural-code-native-art
- #animated-authored-backgrounds
- #replace-boring-stock-scenes
- #5-level-progression
- #mobile-first
- #playwright-only-validation
- #final-stage-fixes-code-errors-not-random-media-noise
"""

JOURNAL_ENTRY = """### Remix v4 Shared Context Header
- Added one shared Remix v4 context header block to all active Remix v4 prompts.
- The shared header includes:
  - four-stage workflow summary
  - stage tag summary
  - global policy tag summary
- Purpose: every Remix v4 node sees the whole workflow shape, its role, and the shared invariants immediately at prompt start.
- Remix 3 prompts remain untouched.
"""


def add_header(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    marker = "## Remix v4 Shared Context"
    if marker in text:
        return

    lines = text.splitlines()
    insert_index = 0
    while insert_index < len(lines) and lines[insert_index].startswith("<!--"):
        insert_index += 1
    while insert_index < len(lines) and lines[insert_index].strip() == "":
        insert_index += 1

    new_lines = lines[:insert_index] + [""] + HEADER.strip().splitlines() + [""] + lines[insert_index:]
    path.write_text("\n".join(new_lines).rstrip() + "\n", encoding="utf-8")


def update_journal() -> None:
    text = JOURNAL.read_text(encoding="utf-8")
    marker = "### Remix v4 Shared Context Header"
    if marker not in text:
        JOURNAL.write_text(text.rstrip() + "\n\n" + JOURNAL_ENTRY.strip() + "\n", encoding="utf-8")


def validate() -> None:
    marker = "## Remix v4 Shared Context"
    for path in TARGETS:
        text = path.read_text(encoding="utf-8")
        if text.count(marker) != 1:
            raise AssertionError(f"{path.name} should contain shared header exactly once")
        required = [
            "Remix v4 in brief:",
            "### 3) `visuals_unified`",
            "#default-model-gpt55",
            "#replace-boring-static-bg",
            "#final-stage-fixes-code-errors-not-random-media-noise",
        ]
        missing = [item for item in required if item not in text]
        if missing:
            raise AssertionError(f"{path.name} missing shared header items: {missing}")

    journal = JOURNAL.read_text(encoding="utf-8")
    if "### Remix v4 Shared Context Header" not in journal:
        raise AssertionError("journal missing shared-context entry")


def main() -> None:
    for path in TARGETS:
        add_header(path)
    update_journal()
    validate()
    print("v4_shared_context_header_added")


if __name__ == "__main__":
    main()