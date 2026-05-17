#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path


APP_JSON_PATH = Path("../../games/published/public/app.json").resolve()


def infer_cluster(source: str) -> str:
    parts = Path(source).parts
    for idx, part in enumerate(parts):
        if part in {"runs", "imports", "outputs", "tmp"} and idx + 1 < len(parts):
            return f"{part}/{parts[idx + 1]}"
    return "unknown"


def main() -> int:
    if not APP_JSON_PATH.is_file():
        print(f"Missing app.json: {APP_JSON_PATH}")
        return 1

    payload = json.loads(APP_JSON_PATH.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        print(f"Expected dict app.json, found {type(payload).__name__}")
        return 1

    source_count = Counter()
    run_token_count = Counter()
    cluster_count = Counter()
    missing_source = 0

    for record in payload.values():
        if not isinstance(record, dict):
            continue

        source = str(record.get("source") or "")
        if not source:
            missing_source += 1
            continue

        source_count[source] += 1

        match = re.search(r"run_[0-9TZ]+", source)
        if match:
            run_token_count[match.group(0)] += 1

        cluster_count[infer_cluster(source)] += 1

    sample_keys = []
    if payload:
        first = next(iter(payload.values()))
        if isinstance(first, dict):
            sample_keys = sorted(first.keys())

    print("== Group Games By Origin Run ==")
    print(f"app_json: {APP_JSON_PATH}")
    print(f"entries: {len(payload)}")
    print(f"missing_source: {missing_source}")
    print(f"unique_source_values: {len(source_count)}")
    print(f"sample_keys: {sample_keys[:30]}")

    print("\nTop run tokens found in source paths:")
    for run_id, count in run_token_count.most_common(15):
        print(f"  {run_id}: {count}")

    print("\nTop coarse clusters from source paths:")
    for cluster, count in cluster_count.most_common(15):
        print(f"  {cluster}: {count}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
