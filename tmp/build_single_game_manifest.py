from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract a single game entry from a games manifest.")
    parser.add_argument("--source", required=True, help="Path to source manifest JSON")
    parser.add_argument("--output", required=True, help="Path to output single-game manifest JSON")
    parser.add_argument("--game-index", type=int, default=0, help="0-based game index to extract")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source = Path(args.source)
    output = Path(args.output)
    payload = json.loads(source.read_text(encoding="utf-8"))
    games = payload.get("games") or []
    if not games:
        raise SystemExit(f"Source manifest has no games: {source}")
    if args.game_index < 0 or args.game_index >= len(games):
        raise SystemExit(f"game-index {args.game_index} out of range for {len(games)} games")

    selected = games[args.game_index]
    new_payload = {
        "manifest_version": "1.0.0",
        "source_manifest": str(source),
        "selected_game_index": args.game_index,
        "games": [selected],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(new_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(
        json.dumps(
            {
                "source_manifest": str(source),
                "output_manifest": str(output),
                "selected_index": args.game_index,
                "selected_game_id": selected.get("game_id"),
                "selected_display_name": selected.get("display_name"),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()