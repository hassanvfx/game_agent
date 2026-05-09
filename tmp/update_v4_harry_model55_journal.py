#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JOURNAL = ROOT / "docs/journals/creative-remix-v4-merged-prompts.md"

RUN_ID = "run_v4_harry_potter_raw_one_game_model55_20260509T071151Z"
GAME_ID = "gamezone-0f3dc736-8159-48cf-93d0-bd78a54b8cd0"
SOURCE_PATH = ROOT / "games/raw/gamezone-0f3dc736-8159-48cf-93d0-bd78a54b8cd0"
RUN_DIR = Path("/Volumes/HDD2026/output") / RUN_ID
SINGLE_MANIFEST = ROOT / "tmp/game_refactoring_experiments/fixtures/v4_harry_potter_raw_one_game_manifest.json"


def main() -> None:
    marker = "### Model 5.5 HDD Output v4 Harry Potter Raw One-Game Launch"
    text = JOURNAL.read_text(encoding="utf-8")
    if marker in text:
        print("v4_harry_model55_journal_already_updated")
        return

    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    entry = f"""

{marker}
- Recorded at: `{now}`
- Workflow: `creative_remix_v4`
- Prompt: `Harry Potter`
- Model: `gpt-5.5`
- Source mode: `copy`
- Pipeline: `v2`
- Max concurrency: `1`
- Runs root: `/Volumes/HDD2026/output`
- Selected raw-backed game: `{GAME_ID}`
- Source path: `{SOURCE_PATH}`
- Single-game manifest: `{SINGLE_MANIFEST}`
- Run id: `{RUN_ID}`
- Run dir: `{RUN_DIR}`
- Dashboard: `{RUN_DIR / "dashboard/index.html"}`
- Status: `{RUN_DIR / "run_state.json"}`
- Output root: `{RUN_DIR / "output"}`
- Launcher stdout: `{RUN_DIR / "batch_launcher_stdout.txt"}`
- Launcher stderr: `{RUN_DIR / "batch_launcher_stderr.txt"}`
- Workflow manifest: `tools/game_refactoring/runs/_workflow_manifests/creative_remix_v4__v4_harry_potter_raw_one_game_manifest.json`

This is the model 5.5 comparison run matching the previous v4 Harry Potter raw-backed one-game setup.
"""
    JOURNAL.write_text(text.rstrip() + entry, encoding="utf-8")
    print("v4_harry_model55_journal_updated")


if __name__ == "__main__":
    main()