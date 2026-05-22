#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path("/Users/hassan/repos/game_agent")
DEFAULT_PUBLIC_APP = ROOT / "games/published/public/app.json"
DEFAULT_OBFUSCATED_APP = ROOT / "games/published/obfuscated/app.json"
DEFAULT_REPORT_PATH = ROOT / "tmp/may17_regression_baseline_audit.json"
TAG_FAMILIES = [
    "mechanic_tags",
    "semantic_tags",
    "mood_tags",
    "setting_tags",
    "character_tags",
    "games_tags",
    "franchise_tags",
]


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def normalize_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def normalize_text(value: Any) -> str:
    return " ".join(str(value or "").strip().lower().split())


def sample(items: list[str], limit: int) -> list[str]:
    return items[: max(limit, 0)]


def is_generic_title(record: dict[str, Any], composite_key: str) -> bool:
    title = str(record.get("title") or "").strip()
    if not title:
        return True

    normalized_title = normalize_text(title)
    game_id = str(record.get("game_id") or "").strip()
    remix_id = str(record.get("remix_id") or "").strip()
    published_path = str(record.get("published_path") or "").strip()
    candidate_values = {
        normalize_text(title),
    }

    if title.startswith("gamezone-"):
        return True

    raw_candidates = {
        normalize_text(game_id),
        normalize_text(composite_key),
        normalize_text(f"{game_id}__{remix_id}" if game_id and remix_id else ""),
        normalize_text(published_path),
        normalize_text(Path(published_path).name if published_path else ""),
    }
    raw_candidates.discard("")
    return normalized_title in raw_candidates


def tag_family_lengths(record: dict[str, Any]) -> dict[str, int]:
    return {family: len(normalize_string_list(record.get(family))) for family in TAG_FAMILIES}


def has_no_tags(record: dict[str, Any]) -> bool:
    return all(length == 0 for length in tag_family_lengths(record).values())


def summarize_catalog(path: Path, sample_limit: int) -> dict[str, Any]:
    payload = load_json(path)
    if not isinstance(payload, dict):
        raise ValueError(f"Catalog at {path} must be a JSON object")

    zero_screenshot_keys: list[str] = []
    generic_title_keys: list[str] = []
    no_tag_keys: list[str] = []
    candidate_keys: list[str] = []
    invalid_record_keys: list[str] = []

    for key, record in payload.items():
        if not isinstance(record, dict):
            invalid_record_keys.append(str(key))
            continue

        screenshots = normalize_string_list(record.get("screenshots"))
        generic_title = is_generic_title(record, str(key))
        no_tags = has_no_tags(record)

        if not screenshots:
            zero_screenshot_keys.append(str(key))
        if generic_title:
            generic_title_keys.append(str(key))
        if no_tags:
            no_tag_keys.append(str(key))
        if (not screenshots) or generic_title or no_tags:
            candidate_keys.append(str(key))

    zero_screenshot_keys.sort()
    generic_title_keys.sort()
    no_tag_keys.sort()
    candidate_keys = sorted(set(candidate_keys))
    invalid_record_keys.sort()

    return {
        "catalog_path": str(path),
        "total_entries": len(payload),
        "invalid_record_count": len(invalid_record_keys),
        "invalid_record_sample": sample(invalid_record_keys, sample_limit),
        "zero_screenshots_count": len(zero_screenshot_keys),
        "zero_screenshots_sample": sample(zero_screenshot_keys, sample_limit),
        "zero_screenshots_keys": zero_screenshot_keys,
        "generic_titles_count": len(generic_title_keys),
        "generic_titles_sample": sample(generic_title_keys, sample_limit),
        "generic_titles_keys": generic_title_keys,
        "no_tags_count": len(no_tag_keys),
        "no_tags_sample": sample(no_tag_keys, sample_limit),
        "no_tags_keys": no_tag_keys,
        "candidate_for_removal_count": len(candidate_keys),
        "candidate_for_removal_sample": sample(candidate_keys, sample_limit),
        "candidate_for_removal_keys": candidate_keys,
    }


def compare_key_sets(public: dict[str, Any], obfuscated: dict[str, Any], field: str) -> dict[str, Any]:
    public_keys = set(public[field])
    obfuscated_keys = set(obfuscated[field])
    public_only = sorted(public_keys - obfuscated_keys)
    obfuscated_only = sorted(obfuscated_keys - public_keys)
    return {
        "public_only_count": len(public_only),
        "public_only_sample": public_only[:10],
        "obfuscated_only_count": len(obfuscated_only),
        "obfuscated_only_sample": obfuscated_only[:10],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Audit published catalog regressions for screenshots, generic titles, and missing tags.")
    parser.add_argument("--public-app", default=str(DEFAULT_PUBLIC_APP))
    parser.add_argument("--obfuscated-app", default=str(DEFAULT_OBFUSCATED_APP))
    parser.add_argument("--report-path", default=str(DEFAULT_REPORT_PATH))
    parser.add_argument("--sample-limit", type=int, default=20)
    parser.add_argument(
        "--label",
        default="baseline",
        help="Human-readable label for this audit run, e.g. baseline or after_overwrite.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    public_summary = summarize_catalog(Path(args.public_app), args.sample_limit)
    obfuscated_summary = summarize_catalog(Path(args.obfuscated_app), args.sample_limit)

    payload = {
        "timestamp": utc_timestamp(),
        "label": args.label,
        "tag_families": TAG_FAMILIES,
        "public": public_summary,
        "obfuscated": obfuscated_summary,
        "cross_catalog_diffs": {
            "zero_screenshots": compare_key_sets(public_summary, obfuscated_summary, "zero_screenshots_keys"),
            "generic_titles": compare_key_sets(public_summary, obfuscated_summary, "generic_titles_keys"),
            "no_tags": compare_key_sets(public_summary, obfuscated_summary, "no_tags_keys"),
            "candidate_for_removal": compare_key_sets(public_summary, obfuscated_summary, "candidate_for_removal_keys"),
        },
        "summary": {
            "public_total_entries": public_summary["total_entries"],
            "obfuscated_total_entries": obfuscated_summary["total_entries"],
            "public_candidate_for_removal_count": public_summary["candidate_for_removal_count"],
            "obfuscated_candidate_for_removal_count": obfuscated_summary["candidate_for_removal_count"],
        },
    }

    write_json(Path(args.report_path), payload)
    print(json.dumps({"report_path": args.report_path, **payload["summary"]}, indent=2))


if __name__ == "__main__":
    main()