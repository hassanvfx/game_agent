#!/usr/bin/env python3

import argparse
import json
from collections import Counter
from pathlib import Path


def load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize replay build outcomes for a mirror run.")
    parser.add_argument("--run-dir", required=True, help="Path to the mirror run directory.")
    parser.add_argument("--attempt-name", default="attempt_0001", help="Replay attempt name to summarize.")
    parser.add_argument("--limit", type=int, default=25, help="Limit summary to the first N processed game directories.")
    args = parser.parse_args()

    run_dir = Path(args.run_dir)
    game_dirs = sorted(path for path in (run_dir / "games").iterdir() if path.is_dir())[: args.limit]

    items: list[dict] = []
    for game_dir in game_dirs:
        summary_path = game_dir / "replay" / args.attempt_name / "mirror_build_summary.json"
        if not summary_path.exists():
            continue
        data = load_json(summary_path)
        items.append(
            {
                "game_key": game_dir.name,
                "offline_readiness": data.get("offline_readiness"),
                "remaining_remote_ref_count": int(data.get("remaining_remote_ref_count") or 0),
                "unresolved_url_count": int(data.get("unresolved_url_count") or 0),
                "failed_asset_count": int(data.get("failed_asset_count") or 0),
                "blockers": list(data.get("blockers") or []),
            }
        )

    readiness = Counter(item["offline_readiness"] for item in items)
    remote_refs = Counter(item["remaining_remote_ref_count"] for item in items)
    unresolved = Counter(item["unresolved_url_count"] for item in items)
    failed_assets = Counter(item["failed_asset_count"] for item in items)
    blockers = Counter()
    for item in items:
        for blocker in item["blockers"]:
            blockers[blocker] += 1

    summary = {
        "run_dir": str(run_dir),
        "attempt_name": args.attempt_name,
        "requested_limit": args.limit,
        "summarized_count": len(items),
        "readiness_counts": dict(readiness),
        "remaining_remote_ref_count_distribution": dict(remote_refs),
        "unresolved_url_count_distribution": dict(unresolved),
        "failed_asset_count_distribution": dict(failed_assets),
        "top_blockers": [{"count": count, "blocker": blocker} for blocker, count in blockers.most_common(10)],
        "items": items,
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
