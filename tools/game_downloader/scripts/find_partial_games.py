#!/usr/bin/env python3

import argparse
import json
from pathlib import Path


def load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def main() -> int:
    parser = argparse.ArgumentParser(description="List partial replay builds for a mirror run.")
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--limit", type=int, default=125)
    args = parser.parse_args()

    run_dir = Path(args.run_dir)
    results = []

    for game_dir in sorted(path for path in (run_dir / "games").iterdir() if path.is_dir())[: args.limit]:
        summary_path = game_dir / "replay" / "attempt_0001" / "mirror_build_summary.json"
        if not summary_path.exists():
            continue
        summary = load_json(summary_path)
        if summary.get("offline_readiness") == "fully_offline_ready":
            continue
        results.append(
            {
                "game_key": game_dir.name,
                "offline_readiness": summary.get("offline_readiness"),
                "remaining_remote_ref_count": int(summary.get("remaining_remote_ref_count") or 0),
                "unresolved_url_count": int(summary.get("unresolved_url_count") or 0),
                "failed_asset_count": int(summary.get("failed_asset_count") or 0),
                "blockers": summary.get("blockers") or [],
                "summary_path": str(summary_path),
                "remote_refs_path": str(game_dir / "replay" / "attempt_0001" / "remaining_remote_refs.json"),
                "unresolved_path": str(game_dir / "replay" / "attempt_0001" / "unresolved_urls.json"),
            }
        )

    print(json.dumps({"partial_count": len(results), "items": results}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())