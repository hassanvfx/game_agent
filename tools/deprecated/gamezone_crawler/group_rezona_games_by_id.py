import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


DEFAULT_INPUT_PATH = Path(
    "outputs/rezona_crawl/run_20260415T064109Z/summaries/all_games_deduped.json"
)
DEFAULT_OUTPUT_PATH = Path(
    "outputs/rezona_crawl/run_20260415T064109Z/summaries/games_grouped_by_game_id.json"
)


def load_items(input_path: Path) -> list[dict[str, Any]]:
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Expected top-level JSON object.")
    items = payload.get("items")

    if not isinstance(items, list):
        raise ValueError("Expected top-level JSON object with an 'items' array.")

    normalized_items: list[dict[str, Any]] = []
    for item in items:
        if isinstance(item, dict):
            normalized_items.append(item)

    return normalized_items


def version_sort_key(item: dict[str, Any]) -> tuple[int, str]:
    raw_version = item.get("game_version")
    if isinstance(raw_version, int):
        return (0, str(raw_version))
    if isinstance(raw_version, str) and raw_version.isdigit():
        return (0, raw_version)
    return (1, str(raw_version))


def group_games_by_id(items: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)

    for item in items:
        game_id = item.get("game_id")
        if game_id is None:
            continue
        grouped[str(game_id)].append(item)

    return {
        game_id: sorted(versions, key=version_sort_key)
        for game_id, versions in sorted(grouped.items(), key=lambda entry: int(entry[0]))
    }


def write_output(output_path: Path, grouped: dict[str, list[dict[str, Any]]]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(grouped, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Group Rezona crawl games by game_id and sort each game's versions by "
            "ascending game_version."
        )
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT_PATH,
        help="Path to all_games_deduped.json.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help="Path to write the grouped JSON output.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    items = load_items(args.input)
    grouped = group_games_by_id(items)
    write_output(args.output, grouped)
    print(
        f"Wrote grouped games for {len(grouped)} game_ids to {args.output}",
    )


if __name__ == "__main__":
    main()