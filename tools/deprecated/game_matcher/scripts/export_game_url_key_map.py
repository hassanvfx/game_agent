#!/usr/bin/env python3
import json
import re
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parent.parent
INPUT_PATH = ROOT_DIR / "fixtures" / "consolidated" / "master_game_reverse_index.json"
OUTPUT_PATH = ROOT_DIR / "fixtures" / "consolidated" / "game_url_key_map.json"


def safe_name(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9._-]+", "_", value.strip())
    return normalized or "unknown"


def slugify(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return normalized or "run"


def infer_game_key(item: dict[str, Any], source_url: str) -> str:
    minigame_match = re.search(r"/minigame/([^/]+)/index\.html$", source_url)
    if minigame_match:
        return safe_name(minigame_match.group(1))

    version_match = re.search(r"/(latest-[^.]+)\.html$", source_url)
    if version_match:
        return safe_name(version_match.group(1))

    game_id = item.get("game_id")
    if game_id is not None:
        return safe_name(f"game-{game_id}")

    return safe_name(slugify(source_url))


def main() -> int:
    with INPUT_PATH.open("r", encoding="utf-8") as handle:
        reverse_index = json.load(handle)

    games = reverse_index.get("games", [])
    output: list[dict[str, Any]] = []

    for item in games:
        source_url = str(item.get("url") or "")
        output.append(
            {
                "game_id": item.get("game_id"),
                "name": item.get("name"),
                "url": source_url,
                "game_key": infer_game_key(item, source_url),
            }
        )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2, ensure_ascii=False)
        handle.write("\n")

    print(f"Wrote {len(output)} mappings to {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())