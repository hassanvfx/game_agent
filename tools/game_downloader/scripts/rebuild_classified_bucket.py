#!/usr/bin/env python3

import argparse
import json
import subprocess
from collections import Counter
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


def classify_games(run_dir: Path) -> list[dict]:
    items = []
    for game_dir in sorted(path for path in (run_dir / "games").iterdir() if path.is_dir()):
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
        items.append(
            {
                "game_key": game_dir.name,
                "bucket": bucket,
                "attempt_name": latest_replay_attempt,
                "remaining_remote_ref_count": int(summary.get("remaining_remote_ref_count") or 0),
                "unresolved_url_count": int(summary.get("unresolved_url_count") or 0),
                "failed_asset_count": int(summary.get("failed_asset_count") or 0),
            }
        )
    return items


def run_build(run_dir: Path, game_key: str, worker_id: str, timeout_seconds: int) -> dict:
    completed = subprocess.run(
        [
            "python3",
            "mirror_system.py",
            "build-local-mirror",
            "--run-dir",
            str(run_dir),
            "--game-key",
            game_key,
            "--worker-id",
            worker_id,
            "--timeout-seconds",
            str(timeout_seconds),
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"build-local-mirror failed for {game_key}\nSTDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}"
        )
    return json.loads(completed.stdout)


def regenerate_qa(run_dir: Path) -> dict:
    completed = subprocess.run(
        [
            "python3",
            "generate_qa_index.py",
            "--run-dir",
            str(run_dir),
            "--limit",
            "7069",
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"generate_qa_index failed\nSTDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}"
        )
    return json.loads(completed.stdout)


def main() -> int:
    parser = argparse.ArgumentParser(description="Rebuild a classified partial bucket in controlled slices.")
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--bucket", required=True)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--count", type=int, default=50)
    parser.add_argument("--worker-id", default="batch-001")
    parser.add_argument("--timeout-seconds", type=int, default=30)
    parser.add_argument("--inventory-only", action="store_true")
    args = parser.parse_args()

    run_dir = Path(args.run_dir)
    classified = classify_games(run_dir)
    matching = [item for item in classified if item["bucket"] == args.bucket]
    selected = matching[args.offset : args.offset + args.count]

    if args.inventory_only:
        print(
            json.dumps(
                {
                    "run_dir": str(run_dir),
                    "bucket": args.bucket,
                    "bucket_total": len(matching),
                    "offset": args.offset,
                    "count": args.count,
                    "selected_count": len(selected),
                    "selected": selected,
                    "bucket_counts": dict(Counter(item["bucket"] for item in classified).most_common()),
                },
                indent=2,
            )
        )
        return 0

    results = []
    failures = []
    for item in selected:
        try:
            results.append(run_build(run_dir, item["game_key"], args.worker_id, args.timeout_seconds))
        except Exception as exc:
            failures.append({"game_key": item["game_key"], "error": str(exc)})

    qa = regenerate_qa(run_dir)
    post_classified = classify_games(run_dir)
    post_matching = [item for item in post_classified if item["bucket"] == args.bucket]

    print(
        json.dumps(
            {
                "run_dir": str(run_dir),
                "bucket": args.bucket,
                "bucket_total_before": len(matching),
                "offset": args.offset,
                "count": args.count,
                "selected_count": len(selected),
                "rebuilt_count": len(results),
                "failure_count": len(failures),
                "results": results,
                "failures": failures,
                "bucket_total_after": len(post_matching),
                "qa": qa,
                "post_bucket_counts": dict(Counter(item["bucket"] for item in post_classified).most_common()),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())