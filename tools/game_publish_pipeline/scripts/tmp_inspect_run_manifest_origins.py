#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path


RUNS_ROOT = Path("../../games/published/runs").resolve()


def main() -> int:
    if not RUNS_ROOT.is_dir():
        print(f"Missing runs root: {RUNS_ROOT}")
        return 1

    run_dirs = sorted(path for path in RUNS_ROOT.glob("run_*") if path.is_dir())
    manifest_runs = []
    source_field_runs = 0
    source_value_total = 0
    run_token_counts = Counter()
    cluster_counts = Counter()

    for run_dir in run_dirs:
        manifest_path = run_dir / "artifacts_manifest.json"
        if not manifest_path.is_file():
            continue

        manifest_runs.append(run_dir.name)
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        entries = payload.get("entries", []) if isinstance(payload, dict) else []
        has_source = False

        for entry in entries:
            if not isinstance(entry, dict):
                continue
            source = str(entry.get("source") or "")
            if not source:
                continue

            has_source = True
            source_value_total += 1

            match = re.search(r"run_[0-9TZ]+", source)
            if match:
                run_token_counts[match.group(0)] += 1

            parts = Path(source).parts
            cluster = "unknown"
            for idx, part in enumerate(parts):
                if part in {"runs", "imports", "outputs", "tmp"} and idx + 1 < len(parts):
                    cluster = f"{part}/{parts[idx + 1]}"
                    break
            cluster_counts[cluster] += 1

        if has_source:
            source_field_runs += 1

    print("== Inspect Run Manifest Origins ==")
    print(f"runs_root: {RUNS_ROOT}")
    print(f"run_dirs: {len(run_dirs)}")
    print(f"runs_with_artifacts_manifest: {len(manifest_runs)}")
    print(f"runs_with_nonempty_source_entries: {source_field_runs}")
    print(f"total_source_values_found: {source_value_total}")

    print("\nManifest runs:")
    for name in manifest_runs[:30]:
        print(f"  - {name}")
    if len(manifest_runs) > 30:
        print(f"  ... {len(manifest_runs) - 30} more")

    print("\nTop source run tokens:")
    for run_id, count in run_token_counts.most_common(15):
        print(f"  {run_id}: {count}")

    print("\nTop source clusters:")
    for cluster, count in cluster_counts.most_common(15):
        print(f"  {cluster}: {count}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
