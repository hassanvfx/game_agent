import json
import random
from pathlib import Path

RAW_ROOT = Path("games/raw")
TARGET_MANIFEST = Path("tmp/game_refactoring_two_random_kawaii_local_raw_manifest.json")


def main() -> None:
    game_dirs = sorted(path for path in RAW_ROOT.iterdir() if path.is_dir() and path.name.startswith("gamezone-"))
    random.seed(42)
    selected = random.sample(game_dirs, 2)

    manifest = {
        "manifest_version": "1.0.0",
        "run_label": "two-random-kawaii-style-local-raw-test",
        "created_at": "2026-05-13T22:12:00Z",
        "games": [
            {
                "game_id": game_dir.name.removeprefix("gamezone-"),
                "source_path": str(game_dir.resolve()),
                "display_name": game_dir.name,
            }
            for game_dir in selected
        ],
    }

    TARGET_MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    TARGET_MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print(f"Created: {TARGET_MANIFEST}")
    for game in manifest["games"]:
        print(f"{game['game_id']} -> {game['source_path']}")


if __name__ == "__main__":
    main()