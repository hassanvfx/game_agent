#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path

REPO_ROOT = Path("/Users/hassan/repos/game_agent")
JOURNAL = REPO_ROOT / "docs/journals/vatsaltop100-app-alpha-batch.md"

ENTRY = """### 2026-05-10 15:47 - Commit note for next stage

**What Changed:**
- Prepared the repository for commit after establishing the 124-entry raw `run_id/game_id` extraction workflow.
- Recorded the explicit next-stage handoff note for follow-up implementation.

**Next Stage Comment:**
- Build a normalizer for the shape of the Vatsal top100 raw folders so their structure can be mapped deterministically into the same full games-info JSON schema.

"""


def run(command: list[str]) -> None:
    completed = subprocess.run(command, cwd=REPO_ROOT, text=True, capture_output=True)
    if completed.stdout:
        print(completed.stdout.rstrip())
    if completed.stderr:
        print(completed.stderr.rstrip())
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def main() -> None:
    text = JOURNAL.read_text(encoding="utf-8")
    marker = "## 📚 Quick Reference"
    if ENTRY not in text:
        text = text.replace(marker, ENTRY + marker)
        JOURNAL.write_text(text, encoding="utf-8")

    run(["git", "add", "-A"])
    run(
        [
            "git",
            "commit",
            "-m",
            "Add shared game metadata extractor and 124-entry raw run-game workflow",
            "-m",
            "Next stage: normalize the Vatsal top100 raw folder shape into the full games-info JSON schema.",
        ]
    )


if __name__ == "__main__":
    main()