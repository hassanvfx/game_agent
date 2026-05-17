#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


MANIFEST_PATH = Path("tmp/curated_limit2_prompt_only_manifest.json")
OLD_SUFFIX = (
    "with mobile-first controls, touch-friendly interactions, responsive readability, "
    "and the best-adapted mobile UX version"
)
NEW_SUFFIX = (
    "with mobile-first controls, touch-friendly interactions, responsive readability, "
    "optimized on game start for portrait UI format, and the best-adapted mobile UX version "
    "targeting portrait aspect ratios in the 4:7 to 9:16 range"
)


def main() -> None:
    payload = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    payload.setdefault("defaults", {})["limit"] = 6

    updated = 0
    for item in payload.get("runs", []):
        prompt = item.get("prompt")
        if not isinstance(prompt, str):
            continue
        if OLD_SUFFIX in prompt:
            prompt = prompt.replace(OLD_SUFFIX, NEW_SUFFIX)
        elif NEW_SUFFIX not in prompt:
            prompt = prompt.rstrip().rstrip(".") + " " + NEW_SUFFIX
        item["prompt"] = prompt
        updated += 1

    MANIFEST_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    sample_prompts = [run["prompt"] for run in payload.get("runs", [])[:2] if isinstance(run.get("prompt"), str)]
    print(
        json.dumps(
            {
                "path": str(MANIFEST_PATH),
                "limit": payload.get("defaults", {}).get("limit"),
                "updated_prompts": updated,
                "sample_prompts": sample_prompts,
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()