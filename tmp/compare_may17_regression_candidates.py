#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path("/Users/hassan/repos/game_agent")
BASELINE_PATH = ROOT / "tmp/may17_regression_baseline_audit.json"
AFTER_PATH = ROOT / "tmp/may17_regression_after_audit.json"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def diff_keys(before: dict[str, Any], after: dict[str, Any], field: str) -> list[str]:
    return sorted(set(after[field]) - set(before[field]))


def summarize_catalog(name: str, before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    return {
        "catalog": name,
        "total_entries_before": before["total_entries"],
        "total_entries_after": after["total_entries"],
        "delta_total_entries": after["total_entries"] - before["total_entries"],
        "new_zero_screenshot_keys": diff_keys(before, after, "zero_screenshots_keys"),
        "new_generic_title_keys": diff_keys(before, after, "generic_titles_keys"),
        "new_no_tag_keys": diff_keys(before, after, "no_tags_keys"),
        "new_candidate_keys": diff_keys(before, after, "candidate_for_removal_keys"),
    }


def main() -> None:
    baseline = load_json(BASELINE_PATH)
    after = load_json(AFTER_PATH)
    result = {
        "public": summarize_catalog("public", baseline["public"], after["public"]),
        "obfuscated": summarize_catalog("obfuscated", baseline["obfuscated"], after["obfuscated"]),
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()