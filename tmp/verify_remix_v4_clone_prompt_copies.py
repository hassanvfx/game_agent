#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

PAIRS = [
    (
        ROOT / "tools/game_refactoring/prompts/operators_v2/00_creative_remix_v4_remix_inference_plus.md",
        ROOT / "tools/game_refactoring/prompts/operators_v2/00_remix_v4_clone_remix_inference_plus.md",
    ),
    (
        ROOT / "tools/game_refactoring/prompts/operators_v2/01_creative_remix_v4_world_design_superprompt.md",
        ROOT / "tools/game_refactoring/prompts/operators_v2/02_remix_v4_clone_world_design_superprompt.md",
    ),
    (
        ROOT / "tools/game_refactoring/prompts/operators_v2/03_creative_remix_v4_visuals_unified.md",
        ROOT / "tools/game_refactoring/prompts/operators_v2/03_remix_v4_clone_visuals_unified.md",
    ),
    (
        ROOT / "tools/game_refactoring/prompts/operators_v2/04_creative_remix_v4_final_mobile_repair_aggressive.md",
        ROOT / "tools/game_refactoring/prompts/operators_v2/04_remix_v4_clone_final_mobile_repair_aggressive.md",
    ),
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    results = []
    all_identical = True
    for source, clone in PAIRS:
        source_bytes = source.read_bytes()
        clone_bytes = clone.read_bytes()
        identical = source_bytes == clone_bytes
        all_identical = all_identical and identical
        results.append(
            {
                "source": str(source),
                "clone": str(clone),
                "identical": identical,
                "source_sha256": sha256(source),
                "clone_sha256": sha256(clone),
            }
        )
    print(json.dumps({"all_identical": all_identical, "results": results}, indent=2))


if __name__ == "__main__":
    main()