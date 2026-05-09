#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JOURNAL = ROOT / "docs/journals/creative-remix-v4-merged-prompts.md"


def main() -> None:
    text = JOURNAL.read_text(encoding="utf-8")
    if "### Validation Results" in text:
        print("journal_already_updated")
        return
    text += """

### Validation Results
- `python3 tmp/validate_creative_remix_v4.py` passed:
  - `creative_remix_v4_validation_ok`
  - `v4_prompt_count 5`
  - `source_prompts_modified 0`
- `python3 tmp/check_creative_remix_v4_readiness.py` passed:
  - `creative_remix_v4_readiness_ok`
  - `workflow_nodes 5`
  - `dry_manifest_game_count 1`
- The readiness check confirmed:
  - workflow resolution for `creative_remix_v4`
  - expected five-node v4 stage order
  - required v4 production markers
  - provenance/source markers
  - raw concat bundle presence
  - dry manifest construction for one game

### Temp Tooling Decision
The temporary scripts remain in `tmp/` for reproducibility and quick follow-up validation:
- `tmp/create_creative_remix_v4.py`
- `tmp/fix_v4_mechanics_invariant.py`
- `tmp/validate_creative_remix_v4.py`
- `tmp/check_creative_remix_v4_readiness.py`

### Recommended Next Step
Run a one-game `creative_remix_v4` smoke test with low concurrency before using the 107-game manifests.
"""
    JOURNAL.write_text(text, encoding="utf-8")
    print("v4_journal_validation_updated")


if __name__ == "__main__":
    main()