#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "tmp" / "curated_limit2_prompt_only_manifest.json"
MATCHER_ROOT = ROOT.parent / "game_matcher_v2"
RANKED_OUT = ROOT / "tmp" / "debug_first_prompt_ranked_matches.json"
TAGS_OUT = ROOT / "tmp" / "debug_first_prompt_selected_tags.json"


def main() -> int:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    runs = manifest.get("runs", [])
    if not runs:
        raise SystemExit("manifest has no runs")

    first = runs[0]
    prompt = first.get("prompt")
    if not isinstance(prompt, str) or not prompt.strip():
        raise SystemExit("first run has no usable prompt")

    command = [
        sys.executable,
        "cli/match_prompt.py",
        prompt,
        "--limit",
        "6",
        "--selected-tags-out",
        str(TAGS_OUT),
        "--out",
        str(RANKED_OUT),
    ]

    completed = subprocess.run(command, cwd=str(MATCHER_ROOT), capture_output=True, text=True)

    ranked = None
    if RANKED_OUT.exists():
        ranked = json.loads(RANKED_OUT.read_text(encoding="utf-8"))

    tags = None
    if TAGS_OUT.exists():
        tags = json.loads(TAGS_OUT.read_text(encoding="utf-8"))

    print(
        json.dumps(
            {
                "prompt": prompt,
                "command": command,
                "cwd": str(MATCHER_ROOT),
                "returncode": completed.returncode,
                "stdout": completed.stdout,
                "stderr": completed.stderr,
                "ranked_out": str(RANKED_OUT),
                "selected_tags_out": str(TAGS_OUT),
                "ranked_match_count": len(ranked) if isinstance(ranked, list) else None,
                "ranked_matches": ranked,
                "selected_tags": tags,
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())