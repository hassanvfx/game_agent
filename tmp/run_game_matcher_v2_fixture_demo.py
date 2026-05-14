import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.game_matcher_v2.game_matcher_v2.builder import build_artifacts, load_json
from tools.game_matcher_v2.game_matcher_v2.scorer import score_games


def run_fixture(path_str: str) -> None:
    path = Path(path_str)
    print(f"=== {path.name} ===")
    selected_tags = load_json(path)
    result = build_artifacts()
    normalized_games = load_json(result.artifacts_dir / "normalized_games.json")
    ranked = score_games(normalized_games, selected_tags, limit=5)
    for idx, item in enumerate(ranked, start=1):
        print(
            f"{idx}. {item['name']} | game_id={item['game_id']} | "
            f"coverage={item['coverage']} | distance={item['distance']}"
        )
        if item["matched_queries"]:
            print(f"   matched: {', '.join(item['matched_queries'])}")
    print()


def main() -> None:
    run_fixture("tools/game_matcher_v2/fixtures/expectations/flappy_bird_selected_tags.json")
    run_fixture("tools/game_matcher_v2/fixtures/expectations/mario_bros_selected_tags.json")


if __name__ == "__main__":
    main()