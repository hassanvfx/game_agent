#!/usr/bin/env python3

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path


def load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def find_latest_attempt_name(path: Path) -> str | None:
    if not path.exists():
        return None
    candidates = sorted(child.name for child in path.iterdir() if child.is_dir() and child.name.startswith("attempt_"))
    return candidates[-1] if candidates else None


def classify_item(summary: dict, source_text: str) -> str:
    rr = int(summary.get("remaining_remote_ref_count") or 0)
    uu = int(summary.get("unresolved_url_count") or 0)
    fa = int(summary.get("failed_asset_count") or 0)
    blockers = summary.get("blockers") or []

    if uu == 0 and fa == 0 and rr > 0:
        return f"remote_refs_only_rr_{rr}"
    if (uu > 0 or fa > 0) and rr <= 5:
        return "unresolved_or_failed_assets_small"
    if uu > 0 or fa > 0:
        return "unresolved_or_failed_assets_large"
    if rr == 0 and any("live/interactivity" in blocker for blocker in blockers):
        return "live_metadata_only"
    if "live" in source_text.lower():
        return "live_metadata_only"
    return "other_partial"


def main() -> int:
    parser = argparse.ArgumentParser(description="Classify partially offline-ready games into remediation buckets.")
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--limit", type=int, default=7069)
    args = parser.parse_args()

    run_dir = Path(args.run_dir)
    items = []
    bucket_counts = Counter()
    samples = defaultdict(list)

    for game_dir in sorted(path for path in (run_dir / "games").iterdir() if path.is_dir())[: args.limit]:
        replay_root = game_dir / "replay"
        latest_replay_attempt = find_latest_attempt_name(replay_root)
        if latest_replay_attempt is None:
            continue

        summary_path = replay_root / latest_replay_attempt / "mirror_build_summary.json"
        if not summary_path.exists():
            continue

        summary = load_json(summary_path)
        if summary.get("offline_readiness") != "partially_offline_ready":
            continue

        source_path = game_dir / "source.json"
        source_text = source_path.read_text(encoding="utf-8", errors="replace") if source_path.exists() else ""

        bucket = classify_item(summary, source_text)
        bucket_counts[bucket] += 1

        item = {
            "game_key": game_dir.name,
            "bucket": bucket,
            "attempt_name": latest_replay_attempt,
            "remaining_remote_ref_count": int(summary.get("remaining_remote_ref_count") or 0),
            "unresolved_url_count": int(summary.get("unresolved_url_count") or 0),
            "failed_asset_count": int(summary.get("failed_asset_count") or 0),
            "blockers": summary.get("blockers") or [],
            "summary_path": str(summary_path),
        }
        items.append(item)

        if len(samples[bucket]) < 10:
            samples[bucket].append(item)

    print(
        json.dumps(
            {
                "run_dir": str(run_dir),
                "partial_total": len(items),
                "bucket_counts": dict(bucket_counts.most_common()),
                "samples": dict(samples),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())