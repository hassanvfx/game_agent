from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence

from giphy_cli.client import GiphyCliError, GiphyService, GifResult
from giphy_cli.config import ConfigError, load_settings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="giphy",
        description="Thin CLI wrapper around the Giphy API.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    search_parser = subparsers.add_parser("search", help="Search GIFs by query.")
    search_parser.add_argument("query", help="Search query text.")
    search_parser.add_argument("--limit", type=int, default=10, help="Number of GIFs.")
    search_parser.add_argument("--offset", type=int, default=0, help="Result offset.")
    search_parser.add_argument("--rating", help="Content rating filter.")
    search_parser.add_argument("--lang", help="Language for regional content.")
    search_parser.add_argument(
        "--json",
        action="store_true",
        help="Emit raw JSON-friendly output.",
    )

    trending_parser = subparsers.add_parser("trending", help="Get trending GIFs.")
    trending_parser.add_argument("--limit", type=int, default=10, help="Number of GIFs.")
    trending_parser.add_argument("--rating", help="Content rating filter.")
    trending_parser.add_argument(
        "--json",
        action="store_true",
        help="Emit raw JSON-friendly output.",
    )

    translate_parser = subparsers.add_parser(
        "translate", help="Get a single GIF matching a phrase."
    )
    translate_parser.add_argument("phrase", help="Phrase to translate into a GIF.")
    translate_parser.add_argument(
        "--json",
        action="store_true",
        help="Emit raw JSON-friendly output.",
    )

    random_parser = subparsers.add_parser("random", help="Get a random GIF.")
    random_parser.add_argument("--tag", help="Optional random tag.")
    random_parser.add_argument("--rating", help="Content rating filter.")
    random_parser.add_argument(
        "--json",
        action="store_true",
        help="Emit raw JSON-friendly output.",
    )

    return parser


def format_gif(result: GifResult) -> str:
    lines = [
        f"id: {result.id}",
        f"title: {result.title or '(untitled)'}",
        f"gif_url: {result.gif_url}",
        f"webp_url: {result.webp_url}",
    ]
    if result.username:
        lines.append(f"username: {result.username}")
    if result.rating:
        lines.append(f"rating: {result.rating}")
    if result.source:
        lines.append(f"source: {result.source}")
    return "\n".join(lines)


def print_results(results: Sequence[GifResult], as_json: bool) -> None:
    if as_json:
        print(json.dumps([item.to_dict() for item in results], indent=2))
        return

    if not results:
        print("No GIFs found.")
        return

    for index, result in enumerate(results, start=1):
        if index > 1:
            print()
        print(f"[{index}] {format_gif(result)}")


def print_result(result: GifResult, as_json: bool) -> None:
    if as_json:
        print(json.dumps(result.to_dict(), indent=2))
        return

    print(format_gif(result))


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        settings = load_settings()
        service = GiphyService(settings)

        if args.command == "search":
            results = service.search(
                args.query,
                limit=args.limit,
                offset=args.offset,
                rating=args.rating,
                lang=args.lang,
            )
            print_results(results, args.json)
            return 0

        if args.command == "trending":
            results = service.trending(
                limit=args.limit,
                rating=args.rating,
            )
            print_results(results, args.json)
            return 0

        if args.command == "translate":
            result = service.translate(args.phrase)
            print_result(result, args.json)
            return 0

        if args.command == "random":
            result = service.random(tag=args.tag, rating=args.rating)
            print_result(result, args.json)
            return 0

        parser.error(f"Unsupported command: {args.command}")
    except (ConfigError, GiphyCliError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())