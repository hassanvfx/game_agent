#!/usr/bin/env python3
"""Print a concise summary from the published game audio reference audit."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUDIT_PATH = ROOT / "tmp" / "library-consolitaion" / "published_game_audio_ref_audit.json"


def main() -> int:
    payload = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
    summary = payload["summary"]
    runtime_summary = payload.get("runtime_summary", {})
    mismatches = payload.get("mismatches", [])
    runtime_mismatches = payload.get("runtime_mismatches", [])

    print("Overall summary:")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print("\nRuntime-only summary:")
    print(json.dumps(runtime_summary, ensure_ascii=False, indent=2))

    by_classification: dict[str, list[dict]] = defaultdict(list)
    for item in runtime_mismatches:
        by_classification[item.get("classification", "unknown")].append(item)

    print("\nTop runtime mismatch examples by classification:")
    for classification in sorted(by_classification):
        print(f"\n## {classification} ({len(by_classification[classification])})")
        seen = 0
        for item in by_classification[classification]:
            print(
                json.dumps(
                    {
                        "reference": item.get("reference"),
                        "normalized_location": item.get("normalized_location"),
                        "normalized_full_path": item.get("normalized_full_path"),
                        "basename": item.get("basename"),
                        "gamezone_folder": item.get("gamezone_folder"),
                        "source_file": item.get("source_file"),
                    },
                    ensure_ascii=False,
                )
            )
            seen += 1
            if seen >= 5:
                break

    artifact_report_mismatches = [
        item for item in mismatches if item.get("source_role") == "artifact_report"
    ]
    print(f"\nArtifact-report mismatch count: {len(artifact_report_mismatches)}")

    print("\nTop audio usage entries:")
    for item in payload.get("top_audio_usage", [])[:20]:
        print(json.dumps(item, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())