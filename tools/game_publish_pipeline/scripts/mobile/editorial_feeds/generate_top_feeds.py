#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

DEFAULT_APP_PATH = Path("app.json")
DEFAULT_OUTPUT_DIR = Path("editorial_feeds/output")
DEFAULT_TOP_FEEDS = 100
DEFAULT_RESULTS_PER_FEED = 200
DEFAULT_TOP_VARIATIONS = 12
DEFAULT_REMIX_LIMIT = 1000
DEFAULT_ALL_TAG_MATCH_COUNTS_PATH = Path("editorial_feeds/output/all_tag_match_counts.json")

FAMILY_CONFIG: dict[str, dict[str, Any]] = {
    "mechanics": {
        "source_fields": ["mechanic_tags"],
        "weight": 5.0,
    },
    "semantics": {
        "source_fields": ["semantic_tags"],
        "weight": 3.0,
    },
    "moods": {
        "source_fields": ["mood_tags"],
        "weight": 1.5,
    },
    "settings": {
        "source_fields": ["setting_tags"],
        "weight": 1.25,
    },
    "characters": {
        "source_fields": ["character_tags"],
        "weight": 1.0,
    },
    "references": {
        "source_fields": ["games_tags", "franchise_tags"],
        "weight": 2.0,
    },
}

TOKEN_SPLIT_RE = re.compile(r"[^a-z0-9]+")
MULTISPACE_RE = re.compile(r"\s+")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate isolated top tag feeds and a remix feed from app.json."
    )
    parser.add_argument(
        "--app",
        type=Path,
        default=DEFAULT_APP_PATH,
        help="Path to app.json catalog.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory where feed artifacts will be written.",
    )
    parser.add_argument(
        "--top-feeds",
        type=int,
        default=DEFAULT_TOP_FEEDS,
        help="Number of top feed seeds to generate.",
    )
    parser.add_argument(
        "--results-per-feed",
        type=int,
        default=DEFAULT_RESULTS_PER_FEED,
        help="Maximum number of sorted matches to store per feed. Use 0 or negative for all.",
    )
    parser.add_argument(
        "--top-variations",
        type=int,
        default=DEFAULT_TOP_VARIATIONS,
        help="Maximum number of related tag variations to keep per family in feed metadata.",
    )
    parser.add_argument(
        "--remix-limit",
        type=int,
        default=DEFAULT_REMIX_LIMIT,
        help="Maximum number of remix feed entries. Use 0 or negative for all.",
    )
    parser.add_argument(
        "--all-tag-match-counts-out",
        type=Path,
        default=DEFAULT_ALL_TAG_MATCH_COUNTS_PATH,
        help="Output path for the full all-tags match count artifact.",
    )
    return parser.parse_args()


def normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    normalized = normalized.encode("ascii", "ignore").decode("ascii")
    normalized = normalized.lower().strip()
    normalized = MULTISPACE_RE.sub(" ", normalized)
    return normalized


def tokenize_phrase(value: str) -> list[str]:
    normalized = normalize_text(value)
    return [token for token in TOKEN_SPLIT_RE.split(normalized) if token]


def slugify(value: str) -> str:
    return TOKEN_SPLIT_RE.sub("-", normalize_text(value)).strip("-")


def iter_list(values: Any) -> list[str]:
    if not isinstance(values, list):
        return []
    return [item.strip() for item in values if isinstance(item, str) and item.strip()]


def load_catalog(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SystemExit(f"Expected top-level object in {path}")
    return payload


def build_tag_registry(
    catalog: dict[str, Any],
) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]], list[dict[str, Any]]]:
    registry: dict[str, dict[str, Any]] = {}
    games: list[dict[str, Any]] = []

    for entry_key, raw_game in catalog.items():
        if not isinstance(raw_game, dict):
            continue

        game = {
            "entry_key": entry_key,
            "game_id": raw_game.get("game_id") or entry_key,
            "title": raw_game.get("title") or "",
            "description": raw_game.get("description") or "",
            "published_path": raw_game.get("published_path"),
            "screenshots": raw_game.get("screenshots") or [],
            "families": {},
            "searchable_terms": set(),
        }

        for family_name, family_config in FAMILY_CONFIG.items():
            family_terms: dict[str, dict[str, Any]] = {}
            for source_field in family_config["source_fields"]:
                for raw_value in iter_list(raw_game.get(source_field)):
                    normalized_label = normalize_text(raw_value)
                    if not normalized_label:
                        continue
                    token = slugify(normalized_label)
                    if not token:
                        continue

                    game["searchable_terms"].add(token)
                    game["searchable_terms"].add(normalized_label)

                    term_entry = family_terms.setdefault(
                        token,
                        {
                            "token": token,
                            "label": raw_value.strip(),
                            "normalized_label": normalized_label,
                            "phrase_tokens": tokenize_phrase(normalized_label),
                        },
                    )

                    registry_entry = registry.setdefault(
                        token,
                        {
                            "token": token,
                            "label": term_entry["label"],
                            "normalized_label": normalized_label,
                            "families": defaultdict(int),
                            "source_fields": defaultdict(int),
                            "game_ids": set(),
                            "entry_keys": set(),
                            "weighted_count": 0.0,
                            "raw_count": 0,
                        },
                    )
                    registry_entry["families"][family_name] += 1
                    registry_entry["source_fields"][source_field] += 1
                    registry_entry["game_ids"].add(game["game_id"])
                    registry_entry["entry_keys"].add(entry_key)
                    registry_entry["weighted_count"] += float(family_config["weight"])
                    registry_entry["raw_count"] += 1

            if family_terms:
                game["families"][family_name] = {
                    "weight": float(family_config["weight"]),
                    "terms": list(family_terms.values()),
                }

        game["searchable_terms"] = sorted(game["searchable_terms"])
        games.append(game)

    family_variations: dict[str, dict[str, Any]] = {
        family_name: {} for family_name in FAMILY_CONFIG
    }

    for token, registry_entry in registry.items():
        for family_name, count in registry_entry["families"].items():
            if count <= 0:
                continue
            family_variations[family_name][token] = {
                "token": token,
                "label": registry_entry["label"],
                "normalized_label": registry_entry["normalized_label"],
                "family": family_name,
                "count": count,
                "game_count": len(registry_entry["game_ids"]),
                "weighted_count": round(count * float(FAMILY_CONFIG[family_name]["weight"]), 6),
            }

    return registry, family_variations, games


def rank_feed_tokens(
    registry: dict[str, dict[str, Any]],
    limit: int,
) -> list[dict[str, Any]]:
    ranked = []
    for token, entry in registry.items():
        family_counts = dict(sorted(entry["families"].items()))
        ranked.append(
            {
                "token": token,
                "label": entry["label"],
                "normalized_label": entry["normalized_label"],
                "raw_count": entry["raw_count"],
                "game_count": len(entry["game_ids"]),
                "weighted_count": round(float(entry["weighted_count"]), 6),
                "family_counts": family_counts,
                "family_count": len(family_counts),
                "dominant_family": max(
                    family_counts.items(),
                    key=lambda item: (item[1], FAMILY_CONFIG[item[0]]["weight"], item[0]),
                )[0]
                if family_counts
                else None,
            }
        )

    ranked.sort(
        key=lambda item: (
            -item["weighted_count"],
            -item["game_count"],
            -item["raw_count"],
            -item["family_count"],
            item["label"].lower(),
            item["token"],
        )
    )
    return ranked[:limit] if limit > 0 else ranked


def build_related_variations(
    feed_token: str,
    family_variations: dict[str, dict[str, Any]],
    top_variations: int,
) -> dict[str, list[dict[str, Any]]]:
    feed_parts = set(feed_token.split("-"))
    related: dict[str, list[dict[str, Any]]] = {}

    for family_name, variations in family_variations.items():
        items = []
        for token, entry in variations.items():
            if token == feed_token:
                continue
            token_parts = set(token.split("-"))
            overlap = len(feed_parts.intersection(token_parts))
            if overlap <= 0:
                continue
            items.append(
                {
                    "token": token,
                    "label": entry["label"],
                    "count": entry["count"],
                    "game_count": entry["game_count"],
                    "weighted_count": entry["weighted_count"],
                    "overlap": overlap,
                }
            )

        items.sort(
            key=lambda item: (
                -item["overlap"],
                -item["weighted_count"],
                -item["game_count"],
                item["label"].lower(),
            )
        )

        if top_variations > 0:
            items = items[:top_variations]
        related[family_name] = items

    return related


def score_game_for_token(game: dict[str, Any], query_token: str) -> dict[str, Any] | None:
    matched_terms: set[str] = set()
    matched_families: set[str] = set()
    score = 0.0
    max_possible_score = 0.0

    for family_name, family_payload in game.get("families", {}).items():
        family_weight = float(family_payload.get("weight") or 0.0)
        terms = family_payload.get("terms") or []
        family_matched = False

        for term in terms:
            token = term.get("token")
            if not isinstance(token, str) or not token:
                continue

            max_possible_score += family_weight
            normalized_label = str(term.get("normalized_label") or "")
            phrase_tokens = set(term.get("phrase_tokens") or [])

            has_exact_token = token == query_token
            query_parts = set(query_token.split("-"))
            has_phrase_overlap = bool(query_parts.intersection(phrase_tokens))
            has_loose_match = query_token in set(game.get("searchable_terms") or []) or (
                normalized_label and normalize_text(query_token.replace("-", " ")) in normalized_label
            )

            if not (has_exact_token or has_phrase_overlap or has_loose_match):
                continue

            if has_exact_token:
                phrase_boost = 1.0
            elif has_phrase_overlap:
                overlap_ratio = len(query_parts.intersection(phrase_tokens)) / max(len(phrase_tokens), 1)
                phrase_boost = max(0.4, overlap_ratio)
            else:
                phrase_boost = 0.3

            score += family_weight * phrase_boost
            family_matched = True
            label = term.get("label")
            if isinstance(label, str) and label:
                matched_terms.add(label)

        if family_matched:
            matched_families.add(family_name)

    if score <= 0:
        return None

    normalized_score = min(score / max_possible_score, 1.0) if max_possible_score > 0 else min(score / 10.0, 1.0)
    return {
        "game_id": game.get("game_id"),
        "entry_key": game.get("entry_key"),
        "title": game.get("title") or "",
        "description": game.get("description") or "",
        "published_path": game.get("published_path"),
        "screenshots": game.get("screenshots") or [],
        "similarity_score": round(normalized_score, 6),
        "distance": round(max(0.0, 1.0 - normalized_score), 6),
        "matched_terms": sorted(matched_terms),
        "matched_families": sorted(matched_families),
    }


def build_feed_results(
    games: list[dict[str, Any]],
    feed_token: str,
    results_per_feed: int,
) -> list[dict[str, Any]]:
    results = []
    for game in games:
        scored = score_game_for_token(game, feed_token)
        if scored is not None:
            results.append(scored)

    results.sort(
        key=lambda item: (
            -item["similarity_score"],
            str(item.get("title") or "").lower(),
            str(item.get("game_id") or ""),
        )
    )
    return results[:results_per_feed] if results_per_feed > 0 else results


def build_remix_entry(
    rank: int,
    source_feed_token: str,
    source_feed_label: str,
    result: dict[str, Any],
) -> dict[str, Any]:
    return {
        "rank": rank,
        "source_feed_token": source_feed_token,
        "source_feed_label": source_feed_label,
        "game_id": result.get("game_id"),
        "entry_key": result.get("entry_key"),
        "title": result.get("title"),
        "published_path": result.get("published_path"),
        "similarity_score": result.get("similarity_score"),
        "matched_terms": result.get("matched_terms") or [],
        "matched_families": result.get("matched_families") or [],
    }


def build_catalog_fallback_results(games: list[dict[str, Any]]) -> list[dict[str, Any]]:
    fallback = []
    for game in games:
        fallback.append(
            {
                "game_id": game.get("game_id"),
                "entry_key": game.get("entry_key"),
                "title": game.get("title") or "",
                "published_path": game.get("published_path"),
                "similarity_score": 0.0,
                "matched_terms": [],
                "matched_families": [],
            }
        )

    fallback.sort(
        key=lambda item: (
            str(item.get("title") or "").lower(),
            str(item.get("game_id") or ""),
        )
    )
    return fallback


def build_remix_feed(
    feeds: list[dict[str, Any]],
    games: list[dict[str, Any]],
    remix_limit: int,
) -> list[dict[str, Any]]:
    seen_game_ids: set[str] = set()
    remix: list[dict[str, Any]] = []
    cursor = 0

    while True:
        emitted_any = False
        for feed in feeds:
            results = feed.get("results") or []
            while cursor < len(results):
                result = results[cursor]
                game_id = result.get("game_id")
                if not isinstance(game_id, str) or not game_id or game_id in seen_game_ids:
                    cursor += 1
                    continue

                remix.append(
                    build_remix_entry(
                        rank=len(remix) + 1,
                        source_feed_token=str(feed.get("token") or ""),
                        source_feed_label=str(feed.get("label") or ""),
                        result=result,
                    )
                )
                seen_game_ids.add(game_id)
                emitted_any = True
                break

            if remix_limit > 0 and len(remix) >= remix_limit:
                return remix

        if not emitted_any:
            break
        cursor += 1

    if remix_limit <= 0:
        return remix

    fallback_results = build_catalog_fallback_results(games)
    for result in fallback_results:
        game_id = result.get("game_id")
        if not isinstance(game_id, str) or not game_id or game_id in seen_game_ids:
            continue

        remix.append(
            build_remix_entry(
                rank=len(remix) + 1,
                source_feed_token="catalog-fallback",
                source_feed_label="Catalog Fallback",
                result=result,
            )
        )
        seen_game_ids.add(game_id)

        if len(remix) >= remix_limit:
            break

    return remix


def sanitize_registry_entry(entry: dict[str, Any]) -> dict[str, Any]:
    return {
        "token": entry["token"],
        "label": entry["label"],
        "normalized_label": entry["normalized_label"],
        "families": dict(sorted(entry["families"].items())),
        "source_fields": dict(sorted(entry["source_fields"].items())),
        "game_count": len(entry["game_ids"]),
        "entry_count": len(entry["entry_keys"]),
        "weighted_count": round(float(entry["weighted_count"]), 6),
        "raw_count": entry["raw_count"],
    }


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def progress(message: str) -> None:
    print(f"[mobile-editorial-feeds] {message}", flush=True, file=sys.stderr)


def build_all_tag_match_counts(
    ranked_tokens: list[dict[str, Any]],
    games: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    items = []
    total = len(ranked_tokens)

    for index, tag in enumerate(ranked_tokens, start=1):
        results = build_feed_results(games, tag["token"], 0)
        items.append(
            {
                "rank": index,
                "of": total,
                "token": tag["token"],
                "label": tag["label"],
                "normalized_label": tag["normalized_label"],
                "dominant_family": tag["dominant_family"],
                "raw_count": tag["raw_count"],
                "game_count": tag["game_count"],
                "weighted_count": tag["weighted_count"],
                "family_counts": tag["family_counts"],
                "results_count": len(results),
            }
        )

    return items


def main() -> int:
    args = parse_args()
    if not args.app.exists():
        raise SystemExit(f"App catalog not found: {args.app}")

    progress(f"start app={args.app}")
    catalog = load_catalog(args.app)
    progress(f"loaded catalog entries={len(catalog)}")
    registry, family_variations, games = build_tag_registry(catalog)
    progress(f"built registry unique_tags={len(registry)} games={len(games)}")
    all_ranked_tokens = rank_feed_tokens(registry, 0)
    ranked_tokens = all_ranked_tokens[: args.top_feeds] if args.top_feeds > 0 else all_ranked_tokens
    progress(f"ranked tokens total={len(all_ranked_tokens)} selected_top_feeds={len(ranked_tokens)}")

    feeds = []
    for rank, feed_entry in enumerate(ranked_tokens, start=1):
        if rank == 1 or rank % 10 == 0 or rank == len(ranked_tokens):
            progress(f"building feed results rank={rank}/{len(ranked_tokens)} token={feed_entry['token']}")
        feed_token = feed_entry["token"]
        results = build_feed_results(games, feed_token, args.results_per_feed)
        feeds.append(
            {
                "rank": rank,
                "token": feed_token,
                "label": feed_entry["label"],
                "normalized_label": feed_entry["normalized_label"],
                "dominant_family": feed_entry["dominant_family"],
                "raw_count": feed_entry["raw_count"],
                "game_count": feed_entry["game_count"],
                "weighted_count": feed_entry["weighted_count"],
                "family_counts": feed_entry["family_counts"],
                "related_variations": build_related_variations(
                    feed_token=feed_token,
                    family_variations=family_variations,
                    top_variations=args.top_variations,
                ),
                "query": feed_entry["label"],
                "results_count": len(results),
                "results": results,
            }
        )

    progress(f"built feeds count={len(feeds)}")
    remix_feed = build_remix_feed(feeds, games, args.remix_limit)
    progress(f"built remix feed count={len(remix_feed)}")
    progress("building all_tag_match_counts...")
    all_tag_match_counts = build_all_tag_match_counts(all_ranked_tokens, games)
    progress(f"built all_tag_match_counts count={len(all_tag_match_counts)}")

    summary_payload = {
        "version": 1,
        "source_app": str(args.app),
        "family_weights": {family: config["weight"] for family, config in FAMILY_CONFIG.items()},
        "catalog_game_count": len(games),
        "unique_tag_count": len(registry),
        "top_feed_count": len(feeds),
        "remix_count": len(remix_feed),
        "feeds": feeds,
    }

    registry_payload = {
        "version": 1,
        "source_app": str(args.app),
        "catalog_game_count": len(games),
        "unique_tag_count": len(registry),
        "tags": [sanitize_registry_entry(registry[token]) for token in sorted(registry)],
    }

    remix_payload = {
        "version": 1,
        "source_app": str(args.app),
        "top_feed_count": len(feeds),
        "remix_count": len(remix_feed),
        "requested_remix_limit": args.remix_limit,
        "items": remix_feed,
    }

    all_tag_match_counts_payload = {
        "version": 1,
        "source_app": str(args.app),
        "unique_tag_count": len(all_tag_match_counts),
        "items": all_tag_match_counts,
    }

    out_dir = args.out_dir
    progress(f"writing outputs to {out_dir}")
    write_json(out_dir / "top_tag_feeds.json", summary_payload)
    write_json(out_dir / "tag_registry.json", registry_payload)
    write_json(out_dir / "remix_feed.json", remix_payload)
    write_json(args.all_tag_match_counts_out, all_tag_match_counts_payload)

    print(f"Wrote {out_dir / 'top_tag_feeds.json'}")
    print(f"Wrote {out_dir / 'tag_registry.json'}")
    print(f"Wrote {out_dir / 'remix_feed.json'}")
    print(f"Wrote {args.all_tag_match_counts_out}")
    print(f"Catalog games: {len(games)}")
    print(f"Unique tags: {len(registry)}")
    print(f"Top feeds: {len(feeds)}")
    print(f"Remix items: {len(remix_feed)}")
    print(f"All tag match counts: {len(all_tag_match_counts)}")
    for feed in feeds[:10]:
        print(
            f"{feed['rank']:>3}. {feed['label']} [{feed['token']}] "
            f"games={feed['game_count']} weighted={feed['weighted_count']} results={feed['results_count']}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())