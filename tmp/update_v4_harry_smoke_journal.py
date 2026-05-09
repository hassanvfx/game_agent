#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JOURNAL = ROOT / "docs/journals/creative-remix-v4-merged-prompts.md"

RUN_IDS = [
    "run_v4_harry_potter_one_game_20260509T070547Z",
    "run_v4_harry_potter_one_game_20260509T070548Z",
    "run_v4_harry_potter_one_game_20260509T070549Z",
]
PRIMARY_RUN_ID = RUN_IDS[-1]
RUNS_ROOT = ROOT / "tmp/game_refactoring_experiments/runs"


def main() -> None:
    text = JOURNAL.read_text(encoding="utf-8")
    marker = "### One-Game v4 Harry Potter Smoke Launch"
    if marker in text:
        print("v4_harry_smoke_journal_already_updated")
        return

    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    lines = [
        "",
        marker,
        f"- Recorded at: `{now}`",
        "- Requested smoke prompt: `Harry Potter`",
        "- Workflow: `creative_remix_v4`",
        "- Manifest: `tmp/game_refactoring_experiments/fixtures/top100_vatsal_first_game_manifest.json`",
        "- Source mode: `copy`",
        "- Pipeline: `v2`",
        "- Max concurrency: `1`",
        "- Note: three launch invocations were accidentally triggered by duplicate tool calls; no relaunch was performed after detection.",
        "- `scripts/kill_all_tool_runtimes.py` was run afterward and reported zero matched/surviving tool runtimes.",
        "- Existing run states still showed `parallel_batch_running`; treat the latest run as the primary monitor target.",
        f"- Primary monitor run: `{PRIMARY_RUN_ID}`",
        "",
        "Launched run IDs:",
    ]
    for run_id in RUN_IDS:
        run_dir = RUNS_ROOT / run_id
        lines.extend(
            [
                f"- `{run_id}`",
                f"  - run dir: `{run_dir}`",
                f"  - dashboard: `{run_dir / 'dashboard/index.html'}`",
                f"  - status: `{run_dir / 'run_state.json'}`",
            ]
        )

    JOURNAL.write_text(text.rstrip() + "\n" + "\n".join(lines) + "\n", encoding="utf-8")
    print("v4_harry_smoke_journal_updated")


if __name__ == "__main__":
    main()