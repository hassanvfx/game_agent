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
from game_matcher_v2.selector import (  # noqa: E402
    DEFAULT_MODEL,
    DEFAULT_RUNS_DIR,
    DEFAULT_TIMEOUT_SECONDS,
    SelectorError,
    run_selector,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the full game_matcher_v2 flow: build artifacts, select ranked tags with Cline, and score games."
    )
    parser.add_argument("prompt", help="User prompt to match against the published game corpus.")
    parser.add_argument(
        "--app-json",
        type=Path,
        default=DEFAULT_APP_JSON_PATH,
        help="Optional override path to the source app.json. Defaults to games/published/public/app.json.",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Cline model identifier. Defaults to {DEFAULT_MODEL}.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Maximum number of ranked games to return. Defaults to 20.",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=DEFAULT_TIMEOUT_SECONDS,
        help=f"Selector timeout in seconds. Defaults to {DEFAULT_TIMEOUT_SECONDS}.",
    )
    parser.add_argument(
        "--runs-dir",
        type=Path,
        default=DEFAULT_RUNS_DIR,
        help="Directory where selector run artifacts should be written.",
    )
    parser.add_argument(
        "--force-rebuild",
        action="store_true",
        help="Force rebuild of derived artifacts before selecting and scoring.",
    )
    parser.add_argument(
        "--selected-tags-out",
        type=Path,
        help="Optional path to write the validated selected-tags JSON payload.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        help="Optional path to write the final ranked matcher-style JSON array.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.limit <= 0:
        print("--limit must be greater than 0.", file=sys.stderr)
        return 2
    if args.timeout_seconds <= 0:
        print("--timeout-seconds must be greater than 0.", file=sys.stderr)
        return 2

    try:
        result = build_artifacts(app_json=args.app_json, force=args.force_rebuild)
        normalized_games = load_json(result.artifacts_dir / "normalized_games.json")
        selector_result = run_selector(
            prompt=args.prompt,
            artifacts_dir=result.artifacts_dir,
            model=args.model,
            timeout_seconds=args.timeout_seconds,
            runs_dir=args.runs_dir,
        )
        ranked_games = score_games(normalized_games, selector_result.validated_selected_tags, limit=args.limit)
    except FileNotFoundError as error:
        print(str(error), file=sys.stderr)
        return 1
    except (SelectorError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 2

    if args.selected_tags_out:
        args.selected_tags_out.parent.mkdir(parents=True, exist_ok=True)
        args.selected_tags_out.write_text(
            json.dumps(selector_result.validated_selected_tags, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"Wrote validated selected tags to {args.selected_tags_out}", file=sys.stderr)

    output_text = json.dumps(ranked_games, indent=2, ensure_ascii=False)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(output_text + "\n", encoding="utf-8")
        print(f"Wrote ranked results to {args.out}", file=sys.stderr)
    else:
        print(output_text)

    print(f"Selector run artifacts: {selector_result.run_root}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())