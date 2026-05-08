#!/usr/bin/env python3
"""Build consolidated gameplay reverse indexes from Rezona query crawl outputs."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from typing import Any


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Aggregate Rezona gameplay query results into consolidated reverse indexes."
    )
    parser.add_argument(
        "--input-root",
        default="fixtures/source_outputs",
        help="Root directory containing run_<timestamp> folders.",
    )
    parser.add_argument(
        "--output-dir",
        default="fixtures/consolidated",
        help="Directory where consolidated output files will be written.",
    )
    return parser.parse_args()


def iter_query_files(input_root: Path) -> list[Path]:
    query_files: list[Path] = []
    for run_dir in sorted(input_root.glob("run_*")):
        query_dir = run_dir / "queries"
        if not query_dir.exists():
            continue
        query_files.extend(sorted(query_dir.glob("query_*.json")))
    return query_files


def get_game_payload(item: dict[str, Any]) -> dict[str, Any] | None:
    if not isinstance(item, dict):
        return None
    game = item.get("game")
    if isinstance(game, dict):
        return game
    if "game_id" in item:
        return item
    return None


def main() -> int:
    args = parse_args()
    input_root = Path(args.input_root)
    output_dir = Path(args.output_dir)

    query_files = iter_query_files(input_root)
    if not query_files:
        raise SystemExit(f"No query files found under {input_root}")

    games: dict[str, dict[str, Any]] = {}
    query_to_games: dict[str, dict[str, Any]] = {}
    processed_files = 0

    for query_file in query_files:
        run_id = query_file.parent.parent.name
        payload = json.loads(query_file.read_text(encoding="utf-8"))
        metadata = payload.get("query_metadata") or {}
        response = payload.get("response") or {}
        data = response.get("data") or {}
        items = data.get("items") or []

        query = metadata.get("query")
        if not query:
            continue

        category = metadata.get("category")
        subcategory = metadata.get("subcategory")
        mechanic_family = metadata.get("mechanic_family")
        query_type = metadata.get("query_type")
        priority = metadata.get("priority")

        query_record = query_to_games.setdefault(
            query,
            {
                "query": query,
                "category": category,
                "subcategory": subcategory,
                "mechanic_family": mechanic_family,
                "query_type": query_type,
                "priority": priority,
                "source_runs": set(),
                "games": [],
                "_seen_game_positions": set(),
            },
        )
        query_record["source_runs"].add(run_id)

        for idx, item in enumerate(items, start=1):
            game_payload = get_game_payload(item)
            if not game_payload:
                continue

            game_id = game_payload.get("game_id")
            if game_id is None:
                continue

            game_key = str(game_id)
            game_record = games.setdefault(
                game_key,
                {
                    "game_id": game_payload.get("game_id"),
                    "game_version": game_payload.get("game_version"),
                    "name": game_payload.get("name"),
                    "description": game_payload.get("description"),
                    "url": game_payload.get("url"),
                    "cover_url": game_payload.get("cover_url"),
                    "dynamic_cover_url": game_payload.get("dynamic_cover_url"),
                    "screen_orientation": game_payload.get("screen_orientation"),
                    "is_public": game_payload.get("is_public"),
                    "created_at": game_payload.get("created_at"),
                    "updated_at": game_payload.get("updated_at"),
                    "stats": game_payload.get("stats"),
                    "creator": game_payload.get("creator"),
                    "topic": game_payload.get("topic"),
                    "queries": set(),
                    "feed_positions": set(),
                    "query_categories": set(),
                    "source_runs": set(),
                    "exact_match_queries": set(),
                    "query_matches": [],
                    "_seen_match_keys": set(),
                },
            )

            feed_position = idx
            exact_match = bool(game_payload.get("exact_match", False))
            match_key = (query, feed_position)

            game_record["queries"].add(query)
            game_record["feed_positions"].add(feed_position)
            if category:
                game_record["query_categories"].add(category)
            game_record["source_runs"].add(run_id)
            if exact_match:
                game_record["exact_match_queries"].add(query)

            if match_key not in game_record["_seen_match_keys"]:
                game_record["_seen_match_keys"].add(match_key)
                game_record["query_matches"].append(
                    {
                        "query": query,
                        "feed_position": feed_position,
                        "category": category,
                        "subcategory": subcategory,
                        "mechanic_family": mechanic_family,
                        "query_type": query_type,
                        "priority": priority,
                        "run_id": run_id,
                        "exact_match": exact_match,
                    }
                )

            q_seen_key = (game_key, feed_position)
            if q_seen_key not in query_record["_seen_game_positions"]:
                query_record["_seen_game_positions"].add(q_seen_key)
                query_record["games"].append(
                    {
                        "game_id": game_payload.get("game_id"),
                        "name": game_payload.get("name"),
                        "feed_position": feed_position,
                        "exact_match": exact_match,
                        "run_id": run_id,
                        "url": game_payload.get("url"),
                    }
                )

        processed_files += 1

    consolidated_games = []
    for game_record in games.values():
        feed_positions = sorted(game_record["feed_positions"])
        queries = sorted(game_record["queries"])
        query_categories = sorted(game_record["query_categories"])
        source_runs = sorted(game_record["source_runs"])
        exact_match_queries = sorted(game_record["exact_match_queries"])
        query_matches = sorted(
            game_record["query_matches"],
            key=lambda item: (item["query"], item["feed_position"], item["run_id"]),
        )

        summary_record = {
            key: value
            for key, value in game_record.items()
            if not key.startswith("_")
            and key
            not in {
                "queries",
                "feed_positions",
                "query_categories",
                "source_runs",
                "exact_match_queries",
                "query_matches",
            }
        }
        summary_record["queries"] = queries
        summary_record["feed_positions"] = feed_positions
        summary_record["query_count"] = len(queries)
        summary_record["best_feed_position"] = min(feed_positions) if feed_positions else None
        summary_record["avg_feed_position"] = round(mean(feed_positions), 4) if feed_positions else None
        summary_record["query_categories"] = query_categories
        summary_record["unique_category_count"] = len(query_categories)
        summary_record["source_runs"] = source_runs
        summary_record["exact_match_queries"] = exact_match_queries
        summary_record["exact_match_count"] = len(exact_match_queries)
        summary_record["query_matches"] = query_matches

        consolidated_games.append(summary_record)

    consolidated_games.sort(
        key=lambda item: (
            -(item.get("query_count") or 0),
            item.get("best_feed_position") if item.get("best_feed_position") is not None else 999999,
            -((item.get("stats") or {}).get("played_count", 0)),
            str(item.get("name") or "").lower(),
        )
    )

    summary_games = [
        {
            "game_id": item.get("game_id"),
            "name": item.get("name"),
            "query_count": item.get("query_count"),
            "best_feed_position": item.get("best_feed_position"),
            "avg_feed_position": item.get("avg_feed_position"),
            "query_categories": item.get("query_categories"),
            "source_runs": item.get("source_runs"),
            "queries": item.get("queries"),
            "url": item.get("url"),
            "played_count": (item.get("stats") or {}).get("played_count"),
        }
        for item in consolidated_games
    ]

    consolidated_queries = []
    for query, query_record in sorted(query_to_games.items()):
        category_counts = Counter()
        for game in query_record["games"]:
            if game.get("exact_match"):
                category_counts["exact_match_results"] += 1
        consolidated_queries.append(
            {
                "query": query,
                "category": query_record.get("category"),
                "subcategory": query_record.get("subcategory"),
                "mechanic_family": query_record.get("mechanic_family"),
                "query_type": query_record.get("query_type"),
                "priority": query_record.get("priority"),
                "source_runs": sorted(query_record["source_runs"]),
                "game_count": len({game["game_id"] for game in query_record["games"]}),
                "result_count": len(query_record["games"]),
                "exact_match_result_count": category_counts["exact_match_results"],
                "games": sorted(
                    query_record["games"],
                    key=lambda item: (item["feed_position"], str(item.get("name") or "").lower()),
                ),
            }
        )

    master_payload = {
        "meta": {
            "input_root": str(input_root),
            "query_file_count": processed_files,
            "game_count": len(consolidated_games),
            "query_count": len(consolidated_queries),
        },
        "games": consolidated_games,
    }

    summary_payload = {
        "meta": master_payload["meta"],
        "games": summary_games,
    }

    query_index_payload = {
        "meta": master_payload["meta"],
        "queries": consolidated_queries,
    }

    write_json(output_dir / "master_game_reverse_index.json", master_payload)
    write_json(output_dir / "master_game_reverse_index_summary.json", summary_payload)
    write_json(output_dir / "master_query_to_games_index.json", query_index_payload)

    print(
        json.dumps(
            {
                "output_dir": str(output_dir),
                "query_file_count": processed_files,
                "game_count": len(consolidated_games),
                "query_count": len(consolidated_queries),
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())