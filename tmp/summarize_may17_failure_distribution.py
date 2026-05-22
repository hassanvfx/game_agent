#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path("/Users/hassan/repos/game_agent")
DEFAULT_AUDIT_PATH = ROOT / "tmp/may17_regression_after_audit.json"
DEFAULT_JSON_REPORT_PATH = ROOT / "tmp/may17_failure_distribution.json"
DEFAULT_MARKDOWN_REPORT_PATH = ROOT / "tmp/may17_failure_distribution.md"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def pct(count: int, total: int) -> float:
    if total <= 0:
        return 0.0
    return round((count / total) * 100, 2)


def sample(values: set[str], limit: int = 5) -> list[str]:
    return sorted(values)[: max(limit, 0)]


def build_bucket_sets(
    zero_screenshots: set[str],
    generic_titles: set[str],
    no_tags: set[str],
) -> dict[str, set[str]]:
    union = zero_screenshots | generic_titles | no_tags
    buckets: dict[str, set[str]] = {
        "zero_only": set(),
        "generic_only": set(),
        "no_tags_only": set(),
        "zero_generic_only": set(),
        "zero_no_tags_only": set(),
        "generic_no_tags_only": set(),
        "all_three": set(),
    }

    for key in union:
        in_zero = key in zero_screenshots
        in_generic = key in generic_titles
        in_no_tags = key in no_tags
        membership = (in_zero, in_generic, in_no_tags)

        if membership == (True, False, False):
            buckets["zero_only"].add(key)
        elif membership == (False, True, False):
            buckets["generic_only"].add(key)
        elif membership == (False, False, True):
            buckets["no_tags_only"].add(key)
        elif membership == (True, True, False):
            buckets["zero_generic_only"].add(key)
        elif membership == (True, False, True):
            buckets["zero_no_tags_only"].add(key)
        elif membership == (False, True, True):
            buckets["generic_no_tags_only"].add(key)
        elif membership == (True, True, True):
            buckets["all_three"].add(key)
        else:
            raise ValueError(f"Unexpected membership state for {key}: {membership}")

    return buckets


def summarize_catalog(catalog: dict[str, Any]) -> dict[str, Any]:
    total_entries = int(catalog["total_entries"])
    zero_screenshots = set(catalog["zero_screenshots_keys"])
    generic_titles = set(catalog["generic_titles_keys"])
    no_tags = set(catalog["no_tags_keys"])
    candidate_for_removal = set(catalog["candidate_for_removal_keys"])

    buckets = build_bucket_sets(zero_screenshots, generic_titles, no_tags)

    bucket_counts = {name: len(values) for name, values in buckets.items()}
    bucket_percentages = {
        name: {
            "of_candidate_pool": pct(len(values), len(candidate_for_removal)),
            "of_total_catalog": pct(len(values), total_entries),
        }
        for name, values in buckets.items()
    }

    return {
        "total_entries": total_entries,
        "zero_screenshots_count": len(zero_screenshots),
        "generic_titles_count": len(generic_titles),
        "no_tags_count": len(no_tags),
        "candidate_for_removal_count": len(candidate_for_removal),
        "pairwise_overlaps": {
            "zero_and_generic": len(zero_screenshots & generic_titles),
            "zero_and_no_tags": len(zero_screenshots & no_tags),
            "generic_and_no_tags": len(generic_titles & no_tags),
            "all_three": len(zero_screenshots & generic_titles & no_tags),
        },
        "bucket_counts": bucket_counts,
        "bucket_percentages": bucket_percentages,
        "bucket_samples": {name: sample(values) for name, values in buckets.items()},
        "set_matches_candidate_union": sorted(candidate_for_removal) == sorted(
            zero_screenshots | generic_titles | no_tags
        ),
    }


def build_markdown_report(payload: dict[str, Any]) -> str:
    public = payload["public"]
    matches = payload["public_obfuscated_sets_match"]
    bucket_counts = public["bucket_counts"]
    bucket_percentages = public["bucket_percentages"]
    pairwise = public["pairwise_overlaps"]

    def bucket_line(name: str, label: str) -> str:
        count = bucket_counts[name]
        pool_pct = bucket_percentages[name]["of_candidate_pool"]
        total_pct = bucket_percentages[name]["of_total_catalog"]
        return f"- `{label} = {count}` ({pool_pct}% of candidates, {total_pct}% of total catalog)"

    lines = [
        "### 2026-05-21 21:10 - Computed the general failure distribution across the full candidate pool",
        "",
        "**Goal:**",
        "Break down the full published-catalog failure pool into overlap buckets so we can tell whether the dominant issue is screenshots, generic titles, missing tags, or combinations of those signals.",
        "",
        "**High-Level Counts (public catalog):**",
        f"- `total_entries = {public['total_entries']}`",
        f"- `candidate_for_removal_count = {public['candidate_for_removal_count']}`",
        f"- `zero_screenshots_count = {public['zero_screenshots_count']}`",
        f"- `generic_titles_count = {public['generic_titles_count']}`",
        f"- `no_tags_count = {public['no_tags_count']}`",
        "",
        "**Set Consistency:**",
        f"- Public and obfuscated tracked-failure sets match exactly: `{matches}`",
        f"- Candidate pool exactly equals the union of the three tracked failure sets: `{public['set_matches_candidate_union']}`",
        "",
        "**Exact Failure Distribution (public/obfuscated are identical):**",
        bucket_line("zero_only", "zero_only"),
        bucket_line("generic_only", "generic_only"),
        bucket_line("no_tags_only", "no_tags_only"),
        bucket_line("zero_generic_only", "zero_generic_only"),
        bucket_line("zero_no_tags_only", "zero_no_tags_only"),
        bucket_line("generic_no_tags_only", "generic_no_tags_only"),
        bucket_line("all_three", "all_three"),
        "",
        "**Pairwise Overlap Totals:**",
        f"- `zero_and_generic = {pairwise['zero_and_generic']}`",
        f"- `zero_and_no_tags = {pairwise['zero_and_no_tags']}`",
        f"- `generic_and_no_tags = {pairwise['generic_and_no_tags']}`",
        f"- `all_three = {pairwise['all_three']}`",
        "",
        "**Interpretation:**",
        "- This distribution shows whether the broken pool is dominated by screenshot/title coupling, tag-only gaps, or mixed failures.",
        "- Because public and obfuscated sets match exactly, we only need one remediation plan per failure bucket rather than separate catalog fixes.",
        "",
        "**Artifacts Created:**",
        "- `tmp/summarize_may17_failure_distribution.py`",
        "- `tmp/may17_failure_distribution.json`",
        "- `tmp/may17_failure_distribution.md`",
        "",
        "**Status:** In Progress",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    audit = load_json(DEFAULT_AUDIT_PATH)
    public = summarize_catalog(audit["public"])
    obfuscated = summarize_catalog(audit["obfuscated"])
    public_obfuscated_sets_match = all(
        set(audit["public"][field]) == set(audit["obfuscated"][field])
        for field in (
            "zero_screenshots_keys",
            "generic_titles_keys",
            "no_tags_keys",
            "candidate_for_removal_keys",
        )
    )

    payload = {
        "source_audit_path": str(DEFAULT_AUDIT_PATH),
        "public": public,
        "obfuscated": obfuscated,
        "public_obfuscated_sets_match": public_obfuscated_sets_match,
        "public_obfuscated_bucket_counts_match": public["bucket_counts"] == obfuscated["bucket_counts"],
    }
    markdown = build_markdown_report(payload)

    write_json(DEFAULT_JSON_REPORT_PATH, payload)
    write_text(DEFAULT_MARKDOWN_REPORT_PATH, markdown)

    print(
        json.dumps(
            {
                "json_report_path": str(DEFAULT_JSON_REPORT_PATH),
                "markdown_report_path": str(DEFAULT_MARKDOWN_REPORT_PATH),
                "public_bucket_counts": public["bucket_counts"],
                "public_pairwise_overlaps": public["pairwise_overlaps"],
                "candidate_for_removal_count": public["candidate_for_removal_count"],
                "public_obfuscated_sets_match": payload["public_obfuscated_sets_match"],
                "public_obfuscated_bucket_counts_match": payload["public_obfuscated_bucket_counts_match"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()