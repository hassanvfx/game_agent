#!/usr/bin/env python3

import csv
import json
import math
import random
from collections import Counter
from itertools import combinations
from pathlib import Path
from statistics import mean, median


RUN_DIR = Path("outputs/rezona_crawl/run_20260415T064109Z")
SEARCH_DIR = RUN_DIR / "search"
SUMMARY_DIR = RUN_DIR / "summaries"
REPORT_MD = RUN_DIR / "SEARCH_OVERLAP_ANALYSIS.md"
PAIRWISE_CSV = SUMMARY_DIR / "search_pairwise_overlap.csv"
PER_QUERY_CSV = SUMMARY_DIR / "search_query_overlap_summary.csv"
MULTIPLICITY_CSV = SUMMARY_DIR / "search_game_multiplicity_distribution.csv"
DISCOVERY_CSV = SUMMARY_DIR / "search_discovery_curve.csv"
JSON_OUT = SUMMARY_DIR / "search_overlap_analysis.json"


def load_query_sets(search_dir: Path) -> dict[str, set[int]]:
    query_sets: dict[str, set[int]] = {}
    for path in sorted(search_dir.glob("query_*.json")):
        with path.open() as f:
            payload = json.load(f)
        slug = payload["slug"]
        game_ids = {
            item["game"]["game_id"]
            for item in payload.get("items", [])
            if item.get("type") == "game" and item.get("game", {}).get("game_id") is not None
        }
        query_sets[slug] = game_ids
    return query_sets


def compute_pairwise(query_sets: dict[str, set[int]]) -> list[dict]:
    rows = []
    for left, right in combinations(sorted(query_sets), 2):
        a = query_sets[left]
        b = query_sets[right]
        intersection = len(a & b)
        union = len(a | b)
        jaccard = intersection / union if union else 0.0
        overlap_vs_smaller = intersection / min(len(a), len(b)) if a and b else 0.0
        overlap_vs_left = intersection / len(a) if a else 0.0
        overlap_vs_right = intersection / len(b) if b else 0.0
        rows.append(
            {
                "query_a": left,
                "query_b": right,
                "count_a": len(a),
                "count_b": len(b),
                "intersection": intersection,
                "union": union,
                "jaccard": jaccard,
                "overlap_vs_smaller": overlap_vs_smaller,
                "overlap_vs_a": overlap_vs_left,
                "overlap_vs_b": overlap_vs_right,
            }
        )
    return rows


def compute_query_summary(query_sets: dict[str, set[int]], multiplicity: Counter) -> list[dict]:
    all_queries = set(query_sets)
    rows = []
    for slug in sorted(query_sets):
        games = query_sets[slug]
        unique_only = sum(1 for gid in games if multiplicity[gid] == 1)
        shared = len(games) - unique_only
        avg_other_queries = mean(multiplicity[gid] - 1 for gid in games) if games else 0.0
        total_memberships = sum(multiplicity[gid] for gid in games)
        rows.append(
            {
                "query": slug,
                "raw_count": len(games),
                "unique_only_count": unique_only,
                "shared_count": shared,
                "unique_only_pct": unique_only / len(games) if games else 0.0,
                "shared_pct": shared / len(games) if games else 0.0,
                "avg_other_queries_per_game": avg_other_queries,
                "avg_total_query_membership": total_memberships / len(games) if games else 0.0,
            }
        )
    return rows


def compute_multiplicity(query_sets: dict[str, set[int]]) -> Counter:
    counts: Counter = Counter()
    for games in query_sets.values():
        for gid in games:
            counts[gid] += 1
    return counts


def simulate_discovery_curve(
    query_sets: dict[str, set[int]], iterations: int = 1000, seed: int = 42
) -> list[dict]:
    rng = random.Random(seed)
    slugs = sorted(query_sets)
    accum = [0] * len(slugs)
    marginals = [[] for _ in slugs]

    for _ in range(iterations):
        order = slugs[:]
        rng.shuffle(order)
        seen: set[int] = set()
        for i, slug in enumerate(order):
            before = len(seen)
            seen |= query_sets[slug]
            after = len(seen)
            gain = after - before
            accum[i] += after
            marginals[i].append(gain)

    rows = []
    for i in range(len(slugs)):
        rows.append(
            {
                "queries_used": i + 1,
                "avg_unique_games_seen": accum[i] / iterations,
                "avg_marginal_new_games": mean(marginals[i]),
                "median_marginal_new_games": median(marginals[i]),
                "min_marginal_new_games": min(marginals[i]),
                "max_marginal_new_games": max(marginals[i]),
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def fmt_pct(value: float) -> str:
    return f"{value * 100:.2f}%"


def main() -> None:
    query_sets = load_query_sets(SEARCH_DIR)
    pairwise = compute_pairwise(query_sets)
    multiplicity = compute_multiplicity(query_sets)
    query_summary = compute_query_summary(query_sets, multiplicity)
    discovery = simulate_discovery_curve(query_sets)

    raw_total = sum(len(games) for games in query_sets.values())
    unique_union = len(multiplicity)
    query_count = len(query_sets)
    pair_count = len(pairwise)

    avg_pairwise_intersection = mean(row["intersection"] for row in pairwise)
    median_pairwise_intersection = median(row["intersection"] for row in pairwise)
    avg_jaccard = mean(row["jaccard"] for row in pairwise)
    median_jaccard = median(row["jaccard"] for row in pairwise)
    avg_overlap_vs_smaller = mean(row["overlap_vs_smaller"] for row in pairwise)
    avg_queries_per_game = mean(multiplicity.values())
    median_queries_per_game = median(multiplicity.values())
    single_query_games = sum(1 for count in multiplicity.values() if count == 1)
    multi_query_games = sum(1 for count in multiplicity.values() if count >= 2)
    redundancy_factor = raw_total / unique_union if unique_union else math.nan

    multiplicity_rows = [
        {
            "query_membership_count": membership_count,
            "games": games_count,
            "pct_of_unique_union": games_count / unique_union if unique_union else 0.0,
        }
        for membership_count, games_count in sorted(Counter(multiplicity.values()).items())
    ]

    top_pairs = sorted(pairwise, key=lambda row: row["intersection"], reverse=True)[:20]
    top_jaccard_pairs = sorted(pairwise, key=lambda row: row["jaccard"], reverse=True)[:20]
    top_unique_queries = sorted(query_summary, key=lambda row: row["unique_only_count"], reverse=True)
    most_redundant_queries = sorted(query_summary, key=lambda row: row["shared_pct"], reverse=True)

    write_csv(
        PAIRWISE_CSV,
        pairwise,
        [
            "query_a",
            "query_b",
            "count_a",
            "count_b",
            "intersection",
            "union",
            "jaccard",
            "overlap_vs_smaller",
            "overlap_vs_a",
            "overlap_vs_b",
        ],
    )
    write_csv(
        PER_QUERY_CSV,
        query_summary,
        [
            "query",
            "raw_count",
            "unique_only_count",
            "shared_count",
            "unique_only_pct",
            "shared_pct",
            "avg_other_queries_per_game",
            "avg_total_query_membership",
        ],
    )
    write_csv(
        MULTIPLICITY_CSV,
        multiplicity_rows,
        ["query_membership_count", "games", "pct_of_unique_union"],
    )
    write_csv(
        DISCOVERY_CSV,
        discovery,
        [
            "queries_used",
            "avg_unique_games_seen",
            "avg_marginal_new_games",
            "median_marginal_new_games",
            "min_marginal_new_games",
            "max_marginal_new_games",
        ],
    )

    json_payload = {
        "run_dir": str(RUN_DIR),
        "query_count": query_count,
        "pair_count": pair_count,
        "raw_total_search_memberships": raw_total,
        "unique_search_union": unique_union,
        "redundancy_factor": redundancy_factor,
        "avg_pairwise_intersection": avg_pairwise_intersection,
        "median_pairwise_intersection": median_pairwise_intersection,
        "avg_pairwise_jaccard": avg_jaccard,
        "median_pairwise_jaccard": median_jaccard,
        "avg_pairwise_overlap_vs_smaller": avg_overlap_vs_smaller,
        "avg_queries_per_game": avg_queries_per_game,
        "median_queries_per_game": median_queries_per_game,
        "single_query_games": single_query_games,
        "single_query_games_pct": single_query_games / unique_union if unique_union else 0.0,
        "multi_query_games": multi_query_games,
        "multi_query_games_pct": multi_query_games / unique_union if unique_union else 0.0,
        "top_pairs_by_intersection": top_pairs,
        "top_pairs_by_jaccard": top_jaccard_pairs,
        "top_queries_by_unique_only_count": top_unique_queries[:20],
        "most_redundant_queries": most_redundant_queries[:20],
        "discovery_curve": discovery,
    }
    JSON_OUT.write_text(json.dumps(json_payload, indent=2))

    report = f"""# Rezona Search Overlap Analysis

Run folder: `{RUN_DIR}`

## Headline metrics

- Search query files analyzed: **{query_count}**
- Query pairs analyzed: **{pair_count}**
- Raw summed search memberships: **{raw_total}**
- Deduped unique search union: **{unique_union}**
- Redundancy factor (`raw_total / unique_union`): **{redundancy_factor:.3f}x**
- Average queries per game: **{avg_queries_per_game:.3f}**
- Median queries per game: **{median_queries_per_game:.1f}**

## Average overlap across all words

- Average pairwise intersection: **{avg_pairwise_intersection:.2f} games**
- Median pairwise intersection: **{median_pairwise_intersection:.1f} games**
- Average pairwise Jaccard similarity: **{fmt_pct(avg_jaccard)}**
- Median pairwise Jaccard similarity: **{fmt_pct(median_jaccard)}**
- Average pairwise overlap vs smaller set: **{fmt_pct(avg_overlap_vs_smaller)}**

## Multiplicity / redundancy view

- Games seen in exactly 1 query: **{single_query_games}** ({fmt_pct(single_query_games / unique_union)})
- Games seen in 2+ queries: **{multi_query_games}** ({fmt_pct(multi_query_games / unique_union)})

## Discovery-curve / searchable lake interpretation

Using random query order simulations:
- After 1 average query: **{discovery[0]['avg_unique_games_seen']:.2f}** unique games observed
- After 5 average queries: **{discovery[4]['avg_unique_games_seen']:.2f}** unique games observed
- After 10 average queries: **{discovery[9]['avg_unique_games_seen']:.2f}** unique games observed
- After 20 average queries: **{discovery[19]['avg_unique_games_seen']:.2f}** unique games observed
- After all {query_count} queries: **{discovery[-1]['avg_unique_games_seen']:.2f}** unique games observed

Average marginal new games added by another query:
- Query #1: **{discovery[0]['avg_marginal_new_games']:.2f}**
- Query #5: **{discovery[4]['avg_marginal_new_games']:.2f}**
- Query #10: **{discovery[9]['avg_marginal_new_games']:.2f}**
- Query #20: **{discovery[19]['avg_marginal_new_games']:.2f}**
- Query #{query_count}: **{discovery[-1]['avg_marginal_new_games']:.2f}**

Interpretation:
- The search lake captured by these seed words contains **{unique_union} unique games** across search results alone.
- Because the redundancy factor is **{redundancy_factor:.3f}x**, the average captured game is returned by more than one query.
- Because the last query still adds an average of **{discovery[-1]['avg_marginal_new_games']:.2f}** new games in random-order simulations, the search-discoverable lake is likely not fully saturated by the current query list.
- This is an estimate of the **search-discoverable lake through the current endpoint/query behavior**, not necessarily the full total number of Rezona games in existence.

## Top query pairs by raw intersection

"""
    for row in top_pairs[:10]:
        report += (
            f"- `{row['query_a']}` × `{row['query_b']}`: "
            f"{row['intersection']} shared games "
            f"(Jaccard {fmt_pct(row['jaccard'])}, overlap-vs-smaller {fmt_pct(row['overlap_vs_smaller'])})\n"
        )

    report += "\n## Top query pairs by Jaccard similarity\n\n"
    for row in top_jaccard_pairs[:10]:
        report += (
            f"- `{row['query_a']}` × `{row['query_b']}`: "
            f"Jaccard {fmt_pct(row['jaccard'])}, {row['intersection']} shared games\n"
        )

    report += "\n## Queries contributing the most exclusive games\n\n"
    for row in top_unique_queries[:10]:
        report += (
            f"- `{row['query']}`: {row['unique_only_count']} exclusive games "
            f"({fmt_pct(row['unique_only_pct'])} of its results)\n"
        )

    report += "\n## Most redundant queries\n\n"
    for row in most_redundant_queries[:10]:
        report += (
            f"- `{row['query']}`: {fmt_pct(row['shared_pct'])} shared, "
            f"{row['unique_only_count']} exclusive games\n"
        )

    report += f"""
## Output files

- `{REPORT_MD}`
- `{JSON_OUT}`
- `{PAIRWISE_CSV}`
- `{PER_QUERY_CSV}`
- `{MULTIPLICITY_CSV}`
- `{DISCOVERY_CSV}`
"""
    REPORT_MD.write_text(report)


if __name__ == "__main__":
    main()