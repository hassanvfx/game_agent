#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from game_matcher_v2.builder import DEFAULT_APP_JSON_PATH, build_artifacts, load_json  # noqa: E402
from game_matcher_v2.scorer import score_games  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Score ranked selected tags against app.json-derived deterministic game_matcher_v2 artifacts."
    )
    parser.add_argument(
        "--selected-tags",
        type=Path,
        required=True,
        help="Path to ranked selected tags JSON.",
    )
    parser.add_argument(
        "--app-json",
        type=Path,
        default=DEFAULT_APP_JSON_PATH,
        help="Optional override path to the source app.json. Defaults to games/published/public/app.json.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Maximum number of ranked games to return. Defaults to 20.",
    )
    parser.add_argument(
        "--force-rebuild",
        action="store_true",
        help="Force rebuild of derived artifacts before scoring.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        help="Optional path to write the JSON array output.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.limit <= 0:
        print("--limit must be greater than 0.", file=sys.stderr)
        return 2

    if not args.selected_tags.exists():
        print(f"Selected tags file not found: {args.selected_tags}", file=sys.stderr)
        return 1

    try:
        result = build_artifacts(app_json=args.app_json, force=args.force_rebuild)
        normalized_games = load_json(result.artifacts_dir / "normalized_games.json")
        selected_tags = load_json(args.selected_tags)
        ranked_games = score_games(normalized_games, selected_tags, limit=args.limit)
    except FileNotFoundError as error:
        print(str(error), file=sys.stderr)
        return 1
    except ValueError as error:
        print(str(error), file=sys.stderr)
        return 2

    output_text = json.dumps(ranked_games, indent=2, ensure_ascii=False)

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(output_text + "\n", encoding="utf-8")
        print(f"Wrote results to {args.out}", file=sys.stderr)
    else:
        print(output_text)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())