#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = ROOT.parent.parent
TARGET_COMPOSITE_KEY = "gamezone-29e7c3b5-974b-47c7-b7bf-585b6d5cc301__remix-2d9ceef4234dc323cd850ecec55d170a"
TARGET_GAME_ID = "gamezone-29e7c3b5-974b-47c7-b7bf-585b6d5cc301"
MATCHER_ROOT = ROOT.parent / "game_matcher_v2"
PUBLIC_APP_JSON = REPO_ROOT / "games" / "published" / "public" / "app.json"
NORMALIZED_GAMES_JSON = MATCHER_ROOT / "fixtures" / "derived" / "normalized_games.json"


def run_matcher_probe() -> list[dict[str, object]]:
    command = [
        sys.executable,
        str((MATCHER_ROOT / "cli" / "match_prompt.py").resolve()),
        "3d gta game",
        "--limit",
        "5",
        "--force-rebuild",
    ]
    result = subprocess.run(command, capture_output=True, text=True, cwd=str(MATCHER_ROOT))
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    if result.returncode != 0:
        raise SystemExit(result.returncode)
    payload = json.loads(result.stdout)
    if not isinstance(payload, list):
        raise SystemExit("Expected list matcher output")
    return payload


def main() -> int:
    public_payload = json.loads(PUBLIC_APP_JSON.read_text())
    matches = run_matcher_probe()
    normalized_payload = json.loads(NORMALIZED_GAMES_JSON.read_text())
    games = normalized_payload.get("games") if isinstance(normalized_payload, dict) else []
    games = games if isinstance(games, list) else []
    report = {
        "target_key_present_in_public_app": TARGET_COMPOSITE_KEY in public_payload,
        "target_key_present_in_normalized_games": any(
            isinstance(item, dict) and item.get("doc_id") == TARGET_COMPOSITE_KEY for item in games
        ),
        "target_game_id_present_in_top_matches": any(
            isinstance(item, dict) and item.get("game_id") == TARGET_GAME_ID for item in matches
        ),
        "top_match_game_ids": [item.get("game_id") for item in matches if isinstance(item, dict)],
    }
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())