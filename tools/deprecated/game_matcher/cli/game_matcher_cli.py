#!/usr/bin/env python3
import argparse
import json
import os
import sys
from pathlib import Path

CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from matcher.cli_support import (
    DEFAULT_QUERIES_PATH,
    DEFAULT_REVERSE_INDEX_PATH,
    ROOT_DIR,
    TOP800_REVERSE_INDEX_PATH,
    build_output_games,
    build_single_game_output,
    find_game_by_url,
    load_env_file,
    load_json,
    rank_games,
    translate_prompt_to_queries,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Match a free-text game idea to ranked games using OpenAI query selection and local indexes."
    )
    parser.add_argument(
        "prompt",
        nargs="?",
        help="Free-text game idea to match against the local game index.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Maximum number of ranked games to return. Defaults to 20.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        help="Optional path to write the JSON array output.",
    )
    parser.add_argument(
        "--env-file",
        type=Path,
        default=ROOT_DIR / ".env",
        help="Optional .env file path. Defaults to ./.env",
    )
    parser.add_argument(
        "--index",
        choices=("top800", "all"),
        default="top800",
        help="Which reverse index to use. Defaults to top800. Use --index all for the legacy full index.",
    )
    parser.add_argument(
        "--url",
        help="Look up a game directly by source URL instead of using prompt-based matching.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if not args.prompt and not args.url:
        print("Either a prompt or --url must be provided.", file=sys.stderr)
        return 2

    if args.prompt and args.url:
        print("Provide either a prompt or --url, not both.", file=sys.stderr)
        return 2

    if args.limit <= 0:
        print("--limit must be greater than 0.", file=sys.stderr)
        return 2

    load_env_file(args.env_file)
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Missing OPENAI_API_KEY environment variable.", file=sys.stderr)
        return 2

    try:
        all_queries = load_json(DEFAULT_QUERIES_PATH)
        reverse_index_path = (
            TOP800_REVERSE_INDEX_PATH if args.index == "top800" else DEFAULT_REVERSE_INDEX_PATH
        )
        reverse_index = load_json(reverse_index_path)
        if args.url:
            matched_game = find_game_by_url(args.url, reverse_index)
            if not matched_game:
                print("No game found for the provided URL.", file=sys.stderr)
                return 1
            output_games = build_single_game_output(matched_game)
        else:
            translated_queries = translate_prompt_to_queries(args.prompt, all_queries, api_key)
            ranked_games = rank_games(args.prompt, translated_queries, reverse_index)
            output_games = build_output_games(ranked_games, args.limit)
    except FileNotFoundError as error:
        print(f"Required file not found: {error.filename}", file=sys.stderr)
        return 1
    except RuntimeError as error:
        print(str(error), file=sys.stderr)
        return 1

    output_text = json.dumps(output_games, indent=2, ensure_ascii=False)

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(output_text + "\n", encoding="utf-8")
        print(f"Wrote results to {args.out}", file=sys.stderr)
    else:
        print(output_text)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())