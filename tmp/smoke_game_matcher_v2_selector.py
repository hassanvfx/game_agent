from pathlib import Path
import json
import sys

repo_root = Path(__file__).resolve().parents[1]
tool_root = repo_root / "tools" / "game_matcher_v2"
sys.path.insert(0, str(tool_root))

from game_matcher_v2.builder import build_artifacts, load_json
from game_matcher_v2.selector import prepare_selector_workspace, validate_selected_tags
from game_matcher_v2.scorer import score_games

result = build_artifacts()
paths = prepare_selector_workspace(
    prompt="flappy bird",
    artifacts_dir=result.artifacts_dir,
    runs_dir=repo_root / "tmp" / "gmv2_smoke_runs",
)

selected_tags = {
    "mechanic_tags": [{"tag": "Endless runner", "score": 1.0}],
    "games_tags": [{"tag": "Flappy Bird", "score": 1.0}],
}
validated = validate_selected_tags(selected_tags, artifacts_dir=result.artifacts_dir)
normalized_games = load_json(result.artifacts_dir / "normalized_games.json")
ranked = score_games(normalized_games, validated, limit=3)

payload = {
    "workspace": str(paths.workspace),
    "validated_selected_tags": validated,
    "top_results": ranked,
}
print(json.dumps(payload, indent=2, ensure_ascii=False))