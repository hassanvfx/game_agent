#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


APP_JSON_PATH = Path("../../games/published/public/app.json").resolve()
RUNS_ROOT = Path("../../games/published/runs").resolve()


def load_manifest_keys(path: Path) -> set[str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    entries = payload.get("entries", []) if isinstance(payload, dict) else []
    keys = set()
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        composite_key = str(entry.get("composite_key") or "")
        if composite_key:
            keys.add(composite_key)
    return keys


def main() -> int:
    if not APP_JSON_PATH.is_file():
        print(f"Missing app.json: {APP_JSON_PATH}")
        return 1
    if not RUNS_ROOT.is_dir():
        print(f"Missing runs root: {RUNS_ROOT}")
        return 1

    app_payload = json.loads(APP_JSON_PATH.read_text(encoding="utf-8"))
    if not isinstance(app_payload, dict):
        print(f"Expected dict app.json, found {type(app_payload).__name__}")
        return 1

    current_keys = {key for key in app_payload.keys() if isinstance(key, str) and key}

    run_membership = {}
    for run_dir in sorted(path for path in RUNS_ROOT.glob("run_*") if path.is_dir()):
        manifest_path = run_dir / "artifacts_manifest.json"
        if manifest_path.is_file():
            run_membership[run_dir.name] = load_manifest_keys(manifest_path)

    membership_count = Counter()
    for key in current_keys:
        matched = [run_id for run_id, keys in run_membership.items() if key in keys]
        if not matched:
            membership_count["not_in_any_run_manifest"] += 1
        elif len(matched) == 1:
            membership_count[f"only:{matched[0]}"] += 1
        else:
            membership_count[f"overlap:{'+'.join(matched)}"] += 1

    print("== Map Current Games To Run Manifests ==")
    print(f"app_json: {APP_JSON_PATH}")
    print(f"current_keys: {len(current_keys)}")
    print(f"manifest_runs: {len(run_membership)}")

    print("\nManifest sizes:")
    for run_id, keys in run_membership.items():
        print(f"  {run_id}: {len(keys)}")

    print("\nCurrent-key membership breakdown:")
    for label, count in membership_count.most_common():
        print(f"  {label}: {count}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
