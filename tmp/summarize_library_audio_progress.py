#!/usr/bin/env python3
"""Summarize library audio progress from the mirrored jobs list."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JOBS_LIST_PATH = ROOT / "tools" / "library" / "assets" / "audios" / "jobs_list.json"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def percent(done: int, total: int) -> float:
    if total <= 0:
        return 0.0
    return round((done / total) * 100, 1)


def bucket_for_job(job: dict) -> str:
    if job.get("record_type") == "asset_family":
        return job.get("destination_dir", "unknown")
    destination_dir = job.get("destination_dir", "")
    if destination_dir.startswith("assets/audios/"):
        remainder = destination_dir[len("assets/audios/") :]
        return remainder.split("/", 1)[0] if remainder else "assets_audios"
    return destination_dir or "unknown"


def main() -> int:
    payload = load_json(JOBS_LIST_PATH)
    jobs = payload.get("jobs", [])

    overall = {
        "total_jobs": len(jobs),
        "complete_jobs": sum(1 for job in jobs if job.get("status") == "complete"),
        "pending_jobs": sum(1 for job in jobs if job.get("status") == "pending"),
    }
    overall["progress_percent"] = percent(overall["complete_jobs"], overall["total_jobs"])

    by_record_type: dict[str, dict[str, int | float]] = {}
    for record_type in sorted({job.get("record_type", "unknown") for job in jobs}):
        subset = [job for job in jobs if job.get("record_type") == record_type]
        total = len(subset)
        complete = sum(1 for job in subset if job.get("status") == "complete")
        pending = total - complete
        by_record_type[record_type] = {
            "total": total,
            "complete": complete,
            "pending": pending,
            "progress_percent": percent(complete, total),
        }

    grouped: dict[str, list[dict]] = defaultdict(list)
    for job in jobs:
        grouped[bucket_for_job(job)].append(job)

    by_bucket: dict[str, dict[str, int | float]] = {}
    for bucket, subset in sorted(grouped.items()):
        total = len(subset)
        complete = sum(1 for job in subset if job.get("status") == "complete")
        pending = total - complete
        by_bucket[bucket] = {
            "total": total,
            "complete": complete,
            "pending": pending,
            "progress_percent": percent(complete, total),
        }

    result = {
        "jobs_list": str(JOBS_LIST_PATH.relative_to(ROOT)),
        "overall": overall,
        "by_record_type": by_record_type,
        "by_bucket": by_bucket,
    }
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())