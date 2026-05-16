import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def normalize_game(game: dict[str, Any]) -> dict[str, Any]:
    return {
        "game_id": game.get("game_id"),
        "game_version": game.get("game_version"),
        "name": game.get("name", ""),
        "url": game.get("url", ""),
    }


def dedupe_games(games: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[Any, Any]] = set()
    deduped: list[dict[str, Any]] = []

    for game in games:
        key = (game.get("game_id"), game.get("game_version"))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(game)

    return deduped


def classify_url(url: str) -> dict[str, str]:
    parsed = urlparse(url or "")
    host = parsed.netloc or "(missing-host)"
    path = parsed.path or "/"
    query = parse_qs(parsed.query)

    path_parts = [part for part in path.split("/") if part]
    bridge_target = ""
    if host == "web.rezona.ai" and path_parts and path_parts[0] == "bridge":
        raw_url = query.get("url", [""])[0]
        if raw_url:
            nested = urlparse(raw_url)
            nested_parts = [part for part in nested.path.split("/") if part]
            if len(nested_parts) >= 2:
                bridge_target = f"{nested.netloc} -> {nested_parts[0]}/{nested_parts[1]}"
            elif nested_parts:
                bridge_target = f"{nested.netloc} -> {nested_parts[0]}"
            else:
                bridge_target = f"{nested.netloc} -> (root)"

    first_part = path_parts[0] if path_parts else "(root)"
    second_part = path_parts[1] if len(path_parts) >= 2 else ""
    third_part = path_parts[2] if len(path_parts) >= 3 else ""

    exact_prefix = f"{host} -> {first_part}"
    if second_part:
        exact_prefix = f"{exact_prefix}/{second_part}"
    if host == "storage.googleapis.com" and first_part == "rezona-ai-prod" and third_part:
        exact_prefix = f"{host} -> {first_part}/{second_part}/{third_part}"

    broad_bucket = "other"
    if host == "storage.googleapis.com" and first_part == "rezona-ai-prod":
        if second_part == "minigame":
            broad_bucket = "minigame"
        elif second_part in {"agent-jobs", "ai-agent", "agents"}:
            broad_bucket = "ai-agent"
        else:
            broad_bucket = f"storage-other:{second_part or '(root)'}"
    elif host == "web.rezona.ai" and first_part == "bridge":
        broad_bucket = "bridge"
    elif host == "web.rezona.ai":
        broad_bucket = f"web:{first_part}"
    elif host:
        broad_bucket = f"other-host:{host}"

    return {
        "url": url,
        "host": host,
        "path": path,
        "broad_bucket": broad_bucket,
        "exact_prefix": exact_prefix,
        "bridge_target": bridge_target,
    }


def distribution_for_games(games: list[dict[str, Any]]) -> dict[str, Any]:
    normalized = [normalize_game(game) for game in games]
    deduped = dedupe_games(normalized)

    broad_counter = Counter()
    exact_counter = Counter()
    bridge_counter = Counter()

    for game in deduped:
        classification = classify_url(game.get("url", ""))
        broad_counter[classification["broad_bucket"]] += 1
        exact_counter[classification["exact_prefix"]] += 1
        if classification["bridge_target"]:
            bridge_counter[classification["bridge_target"]] += 1

    total = len(deduped)

    def to_rows(counter: Counter[str]) -> list[dict[str, Any]]:
        rows = []
        for key, count in counter.most_common():
            rows.append(
                {
                    "key": key,
                    "count": count,
                    "pct": round((count / total * 100), 4) if total else 0.0,
                }
            )
        return rows

    return {
        "game_count": total,
        "broad_bucket_distribution": to_rows(broad_counter),
        "exact_prefix_distribution": to_rows(exact_counter),
        "bridge_target_distribution": to_rows(bridge_counter),
    }


def load_topic_sets(run_dir: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    topic_sets = []
    grouped_games = []

    for path in sorted((run_dir / "topics").glob("topic_*.json")):
        payload = read_json(path)
        topic = payload.get("topic", {})
        games = payload.get("games", [])
        topic_sets.append(
            {
                "set_type": "topic",
                "set_id": topic.get("id"),
                "set_name": topic.get("name"),
                "file": str(path.relative_to(run_dir)),
                "analysis": distribution_for_games(games),
            }
        )
        grouped_games.extend(games)

    return topic_sets, grouped_games


def load_query_sets(run_dir: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    query_sets = []
    grouped_games = []

    for path in sorted((run_dir / "search").glob("query_*.json")):
        payload = read_json(path)
        games = payload.get("games", [])
        query_sets.append(
            {
                "set_type": "query",
                "set_id": payload.get("slug"),
                "set_name": payload.get("query"),
                "file": str(path.relative_to(run_dir)),
                "analysis": distribution_for_games(games),
            }
        )
        grouped_games.extend(games)

    return query_sets, grouped_games


def build_report(run_dir: Path) -> dict[str, Any]:
    topic_sets, topic_games = load_topic_sets(run_dir)
    query_sets, query_games = load_query_sets(run_dir)
    global_games = dedupe_games(
        [normalize_game(game) for game in topic_games + query_games]
    )

    return {
        "run_dir": str(run_dir),
        "per_result_set": {
            "topics": topic_sets,
            "queries": query_sets,
        },
        "grouped": {
            "topics_combined": distribution_for_games(topic_games),
            "search_combined": distribution_for_games(query_games),
        },
        "global": distribution_for_games(global_games),
    }


def markdown_distribution(title: str, analysis: dict[str, Any]) -> list[str]:
    lines = [f"## {title}", ""]
    lines.append(f"- Total games: **{analysis['game_count']}**")
    lines.append("")

    lines.append("### Broad bucket distribution")
    for row in analysis["broad_bucket_distribution"]:
        lines.append(f"- `{row['key']}`: {row['count']} ({row['pct']}%)")
    lines.append("")

    lines.append("### Top exact prefixes")
    for row in analysis["exact_prefix_distribution"][:10]:
        lines.append(f"- `{row['key']}`: {row['count']} ({row['pct']}%)")
    lines.append("")

    if analysis["bridge_target_distribution"]:
        lines.append("### Bridge target distribution")
        for row in analysis["bridge_target_distribution"][:10]:
            lines.append(f"- `{row['key']}`: {row['count']} ({row['pct']}%)")
        lines.append("")

    return lines


def build_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Rezona Prefix Distribution Analysis",
        "",
        f"Run directory: `{report['run_dir']}`",
        "",
        "This report summarizes prefix-path distributions for:",
        "- each topic result set",
        "- each query result set",
        "- grouped topic results",
        "- grouped search results",
        "- global deduped results",
        "",
    ]

    lines.extend(markdown_distribution("Grouped: Topics Combined", report["grouped"]["topics_combined"]))
    lines.extend(markdown_distribution("Grouped: Search Combined", report["grouped"]["search_combined"]))
    lines.extend(markdown_distribution("Global Deduped", report["global"]))

    lines.append("## Per-topic result sets")
    lines.append("")
    for item in report["per_result_set"]["topics"]:
        lines.append(
            f"### Topic {item['set_id']}: {item['set_name']} "
            f"(`{item['analysis']['game_count']}` games)"
        )
        top = item["analysis"]["broad_bucket_distribution"][:5]
        for row in top:
            lines.append(f"- `{row['key']}`: {row['count']} ({row['pct']}%)")
        lines.append("")

    lines.append("## Per-query result sets")
    lines.append("")
    for item in report["per_result_set"]["queries"]:
        lines.append(
            f"### Query {item['set_name']} "
            f"(`{item['analysis']['game_count']}` games)"
        )
        top = item["analysis"]["broad_bucket_distribution"][:5]
        for row in top:
            lines.append(f"- `{row['key']}`: {row['count']} ({row['pct']}%)")
        lines.append("")

    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze captured Rezona game URL prefix distributions from a run folder."
    )
    parser.add_argument(
        "--run-dir",
        required=True,
        help="Path to a Rezona crawler run directory.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_dir = Path(args.run_dir)

    report = build_report(run_dir)

    json_path = run_dir / "summaries" / "prefix_distribution_analysis.json"
    markdown_path = run_dir / "PREFIX_DISTRIBUTION_ANALYSIS.md"

    write_json(json_path, report)
    write_text(markdown_path, build_markdown(report))

    print(f"Wrote {json_path}")
    print(f"Wrote {markdown_path}")


if __name__ == "__main__":
    main()