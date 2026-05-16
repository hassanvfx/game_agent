#!/usr/bin/env python3
import json
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
FIXTURES_DIR = ROOT_DIR / "fixtures" / "consolidated"

GAME_IDS_PATH = FIXTURES_DIR / "top800_game_ids.txt"
FULL_MAP_PATH = FIXTURES_DIR / "game_url_key_map.json"
FULL_REVERSE_INDEX_PATH = FIXTURES_DIR / "master_game_reverse_index.json"

FILTERED_MAP_PATH = FIXTURES_DIR / "top800_game_url_key_map.json"
FILTERED_REVERSE_INDEX_PATH = FIXTURES_DIR / "top800_master_game_reverse_index.json"
FILTERED_SUMMARY_PATH = FIXTURES_DIR / "top800_master_game_reverse_index_summary.json"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> int:
    allowlist = {
        line.strip()
        for line in GAME_IDS_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    }

    full_map = load_json(FULL_MAP_PATH)
    reverse_index = load_json(FULL_REVERSE_INDEX_PATH)
    reverse_games = reverse_index.get("games", [])

    filtered_map = [item for item in full_map if item.get("game_key") in allowlist]
    allowed_game_keys = {item.get("game_key") for item in filtered_map}

    filtered_games = [game for game in reverse_games if game.get("url") and any(
        mapping.get("url") == game.get("url") for mapping in filtered_map
    )]

    unmatched_allowlist = sorted(allowlist - allowed_game_keys)
    duplicate_keys_in_filtered_map = sorted(
        {
            key
            for key in allowed_game_keys
            if sum(1 for item in filtered_map if item.get("game_key") == key) > 1
        }
    )

    filtered_reverse_index = {
        **reverse_index,
        "meta": {
            **(reverse_index.get("meta") or {}),
            "source": "master_game_reverse_index.json",
            "filter_prefix": "top800",
            "source_game_count": len(reverse_games),
            "allowlist_count": len(allowlist),
            "filtered_game_count": len(filtered_games),
            "matched_game_key_count": len(allowed_game_keys),
            "unmatched_allowlist_count": len(unmatched_allowlist),
        },
        "games": filtered_games,
    }

    summary = {
        "meta": {
            "filter_prefix": "top800",
            "source_reverse_index": str(FULL_REVERSE_INDEX_PATH.relative_to(ROOT_DIR)),
            "source_map": str(FULL_MAP_PATH.relative_to(ROOT_DIR)),
            "allowlist_path": str(GAME_IDS_PATH.relative_to(ROOT_DIR)),
        },
        "counts": {
            "source_game_count": len(reverse_games),
            "allowlist_count": len(allowlist),
            "filtered_map_count": len(filtered_map),
            "filtered_game_count": len(filtered_games),
            "matched_game_key_count": len(allowed_game_keys),
            "unmatched_allowlist_count": len(unmatched_allowlist),
            "duplicate_key_count": len(duplicate_keys_in_filtered_map),
        },
        "unmatched_allowlist": unmatched_allowlist,
        "duplicate_game_keys": duplicate_keys_in_filtered_map,
    }

    with FILTERED_MAP_PATH.open("w", encoding="utf-8") as handle:
        json.dump(filtered_map, handle, indent=2, ensure_ascii=False)
        handle.write("\n")

    with FILTERED_REVERSE_INDEX_PATH.open("w", encoding="utf-8") as handle:
        json.dump(filtered_reverse_index, handle, indent=2, ensure_ascii=False)
        handle.write("\n")

    with FILTERED_SUMMARY_PATH.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, ensure_ascii=False)
        handle.write("\n")

    print(
        json.dumps(
            {
                "allowlist_count": len(allowlist),
                "filtered_map_count": len(filtered_map),
                "filtered_game_count": len(filtered_games),
                "unmatched_allowlist_count": len(unmatched_allowlist),
                "duplicate_key_count": len(duplicate_keys_in_filtered_map),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())