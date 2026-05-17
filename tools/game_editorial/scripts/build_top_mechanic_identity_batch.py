#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

CURRENT_FILE = Path(__file__).resolve()
TOOL_ROOT = CURRENT_FILE.parent.parent
REPO_ROOT = TOOL_ROOT.parent.parent
MATCHER_TOOL_ROOT = REPO_ROOT / "tools" / "game_matcher_v2"

for import_root in (TOOL_ROOT, MATCHER_TOOL_ROOT):
    if str(import_root) not in sys.path:
        sys.path.insert(0, str(import_root))

from game_editorial import DEFAULT_APP_JSON_PATH, generate_mechanic_identity_batch  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build a traceable editorial batch of top mechanic identities from "
            "games/published/public/app.json and fetch the top matcher results per tag."
        )
    )
    parser.add_argument(
        "--app-json",
        type=Path,
        default=DEFAULT_APP_JSON_PATH,
        help="Relative or absolute path to the published app.json corpus.",
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=100,
        help="How many mechanic identities to rank. Defaults to 100.",
    )
    parser.add_argument(
        "--matches-per-tag",
        type=int,
        default=10,
        help="How many top matcher results to keep per mechanic identity. Defaults to 10.",
    )
    parser.add_argument(
        "--min-support",
        type=int,
        default=2,
        help="Minimum number of published entries that must carry a mechanic tag.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        help="Optional explicit output directory. Defaults to a timestamped workspace run folder.",
    )
    parser.add_argument(
        "--force-rebuild",
        action="store_true",
        help="Force rebuild of the matcher derived artifacts before scoring.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.top_n <= 0:
        print("--top-n must be greater than 0.", file=sys.stderr)
        return 2
    if args.matches_per_tag <= 0:
        print("--matches-per-tag must be greater than 0.", file=sys.stderr)
        return 2
    if args.min_support <= 0:
        print("--min-support must be greater than 0.", file=sys.stderr)
        return 2

    try:
        result = generate_mechanic_identity_batch(
            app_json=args.app_json,
            top_n=args.top_n,
            matches_per_tag=args.matches_per_tag,
            min_support=args.min_support,
            out_dir=args.out_dir,
            force_rebuild=args.force_rebuild,
        )
    except (FileNotFoundError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 1

    payload = {
        "source_path": str(result.source_path),
        "output_dir": str(result.output_dir),
        "batch_summary_path": str(result.batch_summary_path),
        "top_tags_path": str(result.top_tags_path),
        "matches_path": str(result.matches_path),
        "game_refactoring_manifest_path": str(result.game_refactoring_manifest_path),
        "total_entries": result.total_entries,
        "unique_mechanic_tags": result.unique_mechanic_tags,
        "ranked_count": result.ranked_count,
        "matches_per_tag": result.matches_per_tag,
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())