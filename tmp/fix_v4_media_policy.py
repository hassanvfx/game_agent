#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROMPT = ROOT / "tools/game_refactoring/prompts/operators_v2/04_creative_remix_v4_final_mobile_repair_aggressive.md"
JOURNAL = ROOT / "docs/journals/creative-remix-v4-merged-prompts.md"

POLICY = """## Media/network error triage policy

Do not burn the final repair loop chasing expected or transient external/generated media fetch noise.

Treat these as non-blocking media fetch noise unless they cause a code-level exception, block play, hide required controls, or make required gameplay entities invisible:

- catalog media returning 404/400
- Giphy or generated-media URLs returning 404/400 while assets may still be processing
- optional decorative GIF/image/audio fetch failures
- third-party media fetch failures that do not break code or playability
- missing optional ambience/audio that has a safe fallback or is not required for game operation

Valid media/network fixes are limited to deterministic corrections where the correct route is known, for example:

- incorrect CDN hostname with a known correct hostname
- outdated CDN/library route with a known updated route
- typo in a local required asset path
- broken local required media reference that prevents gameplay or required UI from rendering
- media load failure that triggers JavaScript exceptions because code lacks a safe fallback

When a media failure is non-blocking, document it as `non-blocking external/generated media fetch noise` and continue prioritizing code-level runtime errors, gameplay blockers, mobile actionability, and screenshot-visible UI/layout defects.
"""

JOURNAL_ENTRY = """
### Remix v4 Final Repair Media Error Policy
- Final mobile repair should focus on code-level runtime errors, gameplay blockers, mobile actionability, and screenshot-visible UI/layout defects.
- Do not chase expected/transient catalog or generated-media 404/400 responses, including Giphy/generated assets that may still be processing.
- Treat optional decorative GIF/image/audio fetch failures as `non-blocking external/generated media fetch noise` unless they crash code, hide required controls, block play, or make required gameplay entities invisible.
- Valid media fixes are deterministic corrections where the correct replacement is known: wrong CDN hostname, outdated library route, typo in a required local asset path, or missing required media that breaks code/playability.
- Remix 3 prompts remain untouched; this policy applies to the new Remix v4 final mobile repair prompt.
"""


def dedupe_prompt_policy() -> None:
    text = PROMPT.read_text(encoding="utf-8")
    count = text.count(POLICY)
    if count > 1:
        first = text.find(POLICY)
        before = text[: first + len(POLICY)]
        after = text[first + len(POLICY) :].replace(POLICY, "")
        text = before + after
        PROMPT.write_text(text, encoding="utf-8")


def update_journal() -> None:
    text = JOURNAL.read_text(encoding="utf-8")
    marker = "### Remix v4 Final Repair Media Error Policy"
    if marker not in text:
        JOURNAL.write_text(text.rstrip() + "\n\n" + JOURNAL_ENTRY.strip() + "\n", encoding="utf-8")


def validate() -> None:
    text = PROMPT.read_text(encoding="utf-8")
    required = [
        "Code-level console errors are defects.",
        "non-blocking external/generated media fetch noise",
        "catalog media returning 404/400",
        "Giphy or generated-media URLs returning 404/400 while assets may still be processing",
        "incorrect CDN hostname with a known correct hostname",
        "ReferenceError",
        "TypeError",
        "unhandled promise rejections",
    ]
    missing = [item for item in required if item not in text]
    if missing:
        raise AssertionError(f"missing prompt requirements: {missing}")
    if text.count(POLICY) != 1:
        raise AssertionError("media triage policy should appear exactly once")
    journal = JOURNAL.read_text(encoding="utf-8")
    if "### Remix v4 Final Repair Media Error Policy" not in journal:
        raise AssertionError("journal missing media policy entry")


def main() -> None:
    dedupe_prompt_policy()
    update_journal()
    validate()
    print("v4_media_policy_fixed_and_validated")


if __name__ == "__main__":
    main()