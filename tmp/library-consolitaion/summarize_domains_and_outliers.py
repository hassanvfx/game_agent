#!/usr/bin/env python3
"""Summarize mismatch domains and true outlier mp3 refs."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUDIT_PATH = ROOT / "tmp" / "library-consolitaion" / "published_game_audio_ref_audit.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def domain_of(location: str | None) -> str:
    if not location:
        return "unknown"
    parts = location.split("/")
    return parts[0] if parts else "unknown"


def main() -> int:
    audit = load_json(AUDIT_PATH)
    runtime_mismatches = audit.get("runtime_mismatches", [])

    domain_counter = Counter()
    domain_by_classification: dict[str, Counter] = defaultdict(Counter)
    outliers: list[dict] = []

    for item in runtime_mismatches:
        classification = item.get("classification", "unknown")
        location = item.get("normalized_location")
        domain = domain_of(location)
        domain_counter[domain] += 1
        domain_by_classification[classification][domain] += 1
        if classification in {"other_mp3_reference", "obfuscated_local_audio_asset"}:
            outliers.append(
                {
                    "classification": classification,
                    "reference": item.get("reference"),
                    "normalized_full_path": item.get("normalized_full_path"),
                    "gamezone_folder": item.get("gamezone_folder"),
                    "source_file": item.get("source_file"),
                }
            )

    payload = {
        "runtime_mismatch_domain_counts": dict(domain_counter),
        "classification_domain_counts": {
            key: dict(value) for key, value in domain_by_classification.items()
        },
        "outlier_mp3_refs": outliers,
    }

    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())