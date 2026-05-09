#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROMPTS = ROOT / "tools/game_refactoring/prompts/operators_v2"
JOURNAL = ROOT / "docs/journals/creative-remix-v4-merged-prompts.md"

WORLD = PROMPTS / "01_creative_remix_v4_world_design_superprompt.md"
VISUAL = PROMPTS / "03_creative_remix_v4_visuals_unified.md"

WORLD_POLICY = """## Boring static background replacement mandate

If the input game uses a boring, generic, static, stock, or semantically weak background image as the dominant playfield scene, do not protect that image as the world identity.

The world-design pass must explicitly plan to replace or strongly demote that background with a prompt-specific authored procedural background system.

Requirements:
- identify whether a static image currently owns the playfield
- decide whether it is semantically strong enough to keep
- if it is boring/generic/static/stock-like, mark it as non-protected
- define a procedural replacement background inspired by the remix prompt and mechanic semantics
- specify motion-graphic layers, ambient animation, level/progress reactivity, and visual motifs
- preserve gameplay readability, hitboxes, controls, and HUD clarity
- ensure later visual stages know the intended authored background must become the real scene foundation

Do not merely decorate around the old background with overlays, tint, particles, wrapper polish, or themed text. If the old image remains the dominant scene, the remix has not achieved the intended v4 visual standard.
"""

VISUAL_POLICY = """## Mandatory procedural animated background replacement

If the actual rendered playfield is still dominated by a boring/generic/static/stock-like image background, this visual pass must replace, remove, strongly demote, or transform it until a prompt-specific procedural animated background is the true scene foundation.

This is mandatory visual work, not optional polish.

The replacement should favor:
- CSS/SVG/Canvas/DOM procedural drawing
- motion-graphic animated layers
- level/progress/state-reactive visual changes where safe
- semantic motifs derived from the remix prompt
- recognizable environment/world identity
- readable foreground gameplay and HUD contrast
- mobile-safe performance and non-blocking pointer behavior

Do not accept:
- a static background image as the main visual identity
- an unchanged stock scene with decorative particles on top
- wrapper polish while the original image still owns the playfield
- a background that is cool but hides controls, hazards, rewards, or the player

A static image may remain only if it is clearly non-dominant, semantically intentional, and subordinate to a stronger procedural authored world system.
"""

JOURNAL_ENTRY = """### Remix v4 Animated Background Replacement Mandate
- Restored and strengthened the original animated-background invariant for Remix v4.
- If an input game has a boring/generic/static/stock-like background image dominating the playfield, v4 should not preserve it as the world identity.
- `world_design_superprompt` must plan a prompt-specific procedural animated replacement, including motion-graphic layers, semantic motifs, and level/progress reactivity.
- `visuals_unified` must execute the replacement/demotion so the procedural authored world becomes the true scene foundation.
- Decorative overlays, tinting, particles, wrapper styling, or themed copy around an unchanged stock/static image are explicitly insufficient.
- Mechanics, controls, HUD readability, hitboxes, and mobile actionability remain protected.
"""


def insert_after_heading(path: Path, heading: str, policy: str, marker: str) -> None:
    text = path.read_text(encoding="utf-8")
    if marker in text:
        return
    index = text.find(heading)
    if index == -1:
        raise RuntimeError(f"heading not found in {path}: {heading}")
    insert_at = text.find("\n## ", index + len(heading))
    if insert_at == -1:
        insert_at = text.find("\n---", index + len(heading))
    if insert_at == -1:
        raise RuntimeError(f"insert point not found in {path}")
    text = text[:insert_at].rstrip() + "\n\n" + policy.strip() + "\n" + text[insert_at:]
    path.write_text(text, encoding="utf-8")


def update_journal() -> None:
    text = JOURNAL.read_text(encoding="utf-8")
    marker = "### Remix v4 Animated Background Replacement Mandate"
    if marker not in text:
        JOURNAL.write_text(text.rstrip() + "\n\n" + JOURNAL_ENTRY.strip() + "\n", encoding="utf-8")


def validate() -> None:
    world = WORLD.read_text(encoding="utf-8")
    visual = VISUAL.read_text(encoding="utf-8")
    journal = JOURNAL.read_text(encoding="utf-8")

    checks = [
        (world, "Boring static background replacement mandate"),
        (world, "define a procedural replacement background inspired by the remix prompt"),
        (world, "Do not merely decorate around the old background"),
        (visual, "Mandatory procedural animated background replacement"),
        (visual, "prompt-specific procedural animated background is the true scene foundation"),
        (visual, "an unchanged stock scene with decorative particles on top"),
        (journal, "Remix v4 Animated Background Replacement Mandate"),
        (journal, "Decorative overlays, tinting, particles, wrapper styling"),
    ]
    missing = [needle for haystack, needle in checks if needle not in haystack]
    if missing:
        raise AssertionError(f"missing required policy text: {missing}")


def main() -> None:
    insert_after_heading(
        WORLD,
        "## Stage mission",
        WORLD_POLICY,
        "Boring static background replacement mandate",
    )
    insert_after_heading(
        VISUAL,
        "## Non-negotiable invariants",
        VISUAL_POLICY,
        "Mandatory procedural animated background replacement",
    )
    update_journal()
    validate()
    print("v4_animated_background_policy_reinforced")


if __name__ == "__main__":
    main()