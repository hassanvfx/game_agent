import json
import random
from pathlib import Path

SOURCE_MANIFEST = Path("tools/game_refactoring/fixtures/rick_and_morty_raw_catalog_107_manifest.json")
TARGET_MANIFEST = Path("tmp/game_refactoring_two_random_kawaii_manifest.json")


def main() -> None:
    payload = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    games = payload["games"][:]
    random.seed(42)
    selected = random.sample(games, 2)

    manifest = {
        "manifest_version": payload.get("manifest_version", "1.0.0"),
        "run_label": "two-random-kawaii-style-test",
        "created_at": payload.get("created_at", "2026-05-13T22:00:00Z"),
        "games": [
            {
                "game_id": game["game_id"],
                "source_path": game["source_path"],
                "display_name": game.get("display_name", game["game_id"]),
            }
            for game in selected
        ],
    }

    TARGET_MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    TARGET_MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print(f"Created: {TARGET_MANIFEST}")
    for game in manifest["games"]:
        print(f"{game['game_id']} -> {game['source_path']}")


if __name__ == "__main__":
    main()