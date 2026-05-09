#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JOURNAL = ROOT / "docs/journals/creative-remix-v4-merged-prompts.md"


def main() -> None:
    marker = "### Remix v4 Model Decision"
    text = JOURNAL.read_text(encoding="utf-8")
    if marker in text:
        print("v4_model55_note_already_present")
        return

    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    entry = f"""

{marker}
- Recorded at: `{now}`
- Decision: use `gpt-5.5` as the preferred/default model for Remix v4 runs.
- Rationale: after launching the model 5.5 comparison run for the same raw-backed Harry Potter single-game setup, future `creative_remix_v4` experiments should be launched with `--model gpt-5.5` unless explicitly testing another model.
- Applies to:
  - one-game v4 smoke tests
  - raw-backed v4 prompt experiments
  - future v4 batch launches
- Existing model 5.4 runs remain useful as comparison artifacts, but v4 going forward should use model 5.5.
"""
    JOURNAL.write_text(text.rstrip() + entry, encoding="utf-8")
    print("v4_model55_note_added")


if __name__ == "__main__":
    main()