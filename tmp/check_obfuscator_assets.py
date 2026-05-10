from __future__ import annotations

import json
from pathlib import Path


RUN_DIR = Path("tools/game_obfuscator/runs/run_game_obfuscator_20260510T135235Z")
GAME_ID = "gamezone-0a01fa77-8b8b-4c02-93db-07cf4e05ee06"


def main() -> None:
    game_root = RUN_DIR / "output" / GAME_ID
    source_root = game_root / "artifacts" / "pre_bundle_site"
    payload = {}

    interesting = [
        "index.html",
        "game-obfuscated-321f864173014c43aa4d4afad5e07111.json",
        "assets/cdn.tailwindcss.com/3.4.17.js",
        "assets/fonts.googleapis.com/css2-family_Teko_wght_400_600_display_swap.css",
        "assets/obfuscated/inline-script-001.js",
        "assets/obfuscated/inline-script-002.js",
        "assets/obfuscated/inline-style-001.css",
    ]

    for rel in interesting:
        payload[rel] = {
            "in_output": (game_root / rel).exists(),
            "in_source_snapshot": (source_root / rel).exists(),
        }

    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()