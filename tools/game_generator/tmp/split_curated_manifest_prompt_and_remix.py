#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


MANIFEST_PATH = Path("tmp/curated_limit2_prompt_only_manifest.json")
MOBILE_PORTRAIT_SUFFIX = (
    "with mobile-first controls, touch-friendly interactions, responsive readability, "
    "optimized on game start for portrait UI format, and the best-adapted mobile UX version "
    "targeting portrait aspect ratios in the 4:7 to 9:16 range"
)


def strip_article(text: str) -> str:
    lowered = text.lower()
    for prefix in ("a ", "an ", "the "):
        if lowered.startswith(prefix):
            return text[len(prefix):]
    return text


def sentence_case(text: str) -> str:
    if not text:
        return text
    return text[0].upper() + text[1:]


def build_search_prompt(full_prompt: str) -> str:
    base = full_prompt
    if MOBILE_PORTRAIT_SUFFIX in base:
        base = base.replace(" " + MOBILE_PORTRAIT_SUFFIX, "")
    head = base.split(" with ", 1)[0].strip()
    head = strip_article(head)
    if head.lower().endswith(" game"):
        head = head[:-5].strip()
    return head


def build_remix_prompt(search_prompt: str, full_prompt: str) -> str:
    descriptive = full_prompt.strip().rstrip(".")
    descriptive = sentence_case(descriptive)
    return f"{search_prompt}. {descriptive}."


def main() -> None:
    payload = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    payload.setdefault("defaults", {})["limit"] = 6

    converted = 0
    for item in payload.get("runs", []):
        full_prompt = item.get("prompt")
        if not isinstance(full_prompt, str) or not full_prompt.strip():
            continue
        search_prompt = build_search_prompt(full_prompt.strip())
        item["prompt"] = search_prompt
        item["remix_prompt"] = build_remix_prompt(search_prompt, full_prompt)
        converted += 1

    MANIFEST_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(
        json.dumps(
            {
                "path": str(MANIFEST_PATH),
                "limit": payload.get("defaults", {}).get("limit"),
                "converted_runs": converted,
                "samples": payload.get("runs", [])[:3],
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()