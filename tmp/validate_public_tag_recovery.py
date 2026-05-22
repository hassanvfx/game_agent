#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path("/Users/hassan/repos/game_agent")
PUBLISHED_ROOT = ROOT / "games/published/public"
OUTPUT_ROOT = ROOT / "tmp/generated_metadata_public_tag_recovery_latest"
AUDIT_PATH = OUTPUT_ROOT / "audit.json"
BASELINE_AUDIT_PATH = ROOT / "tmp/generated_metadata_repair_probe_20260521T2227Z/audit.json"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    subprocess.run(
        [
            "python3",
            str(ROOT / "scripts/generate_published_app_metadata.py"),
            "--published-root",
            str(PUBLISHED_ROOT),
            "--output-root",
            str(OUTPUT_ROOT),
            "--strict",
        ],
        check=True,
    )
    subprocess.run(
        [
            "python3",
            str(ROOT / "tmp/audit_published_catalog_regressions.py"),
            "--public-app",
            str(OUTPUT_ROOT / "app.json"),
            "--obfuscated-app",
            str(OUTPUT_ROOT / "app.json"),
            "--report-path",
            str(AUDIT_PATH),
            "--label",
            "public_tag_recovery",
        ],
        check=True,
    )

    baseline = load_json(BASELINE_AUDIT_PATH)["public"]
    current = load_json(AUDIT_PATH)["public"]
    no_tag_delta = baseline["no_tags_count"] - current["no_tags_count"]
    print(
        json.dumps(
            {
                "baseline": {
                    "generic_titles_count": baseline["generic_titles_count"],
                    "no_tags_count": baseline["no_tags_count"],
                    "candidate_for_removal_count": baseline["candidate_for_removal_count"],
                },
                "current": {
                    "generic_titles_count": current["generic_titles_count"],
                    "no_tags_count": current["no_tags_count"],
                    "candidate_for_removal_count": current["candidate_for_removal_count"],
                    "no_tags_sample": current["no_tags_sample"][:10],
                },
                "improvement": {
                    "no_tags_recovered": no_tag_delta,
                    "no_tags_recovered_pct": round((no_tag_delta / baseline["no_tags_count"]) * 100, 2) if baseline["no_tags_count"] else 0,
                },
                "output_root": str(OUTPUT_ROOT),
                "audit_path": str(AUDIT_PATH),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()