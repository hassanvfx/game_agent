from __future__ import annotations

import json
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
OBF_ROOT = REPO_ROOT / "tools" / "game_obfuscator"
VENV_PYTHON = OBF_ROOT / ".venv" / "bin" / "python"

GAME_ID = "gamezone-2c5abec2-ad99-4268-96e0-10fda01cfc5a"
SOURCE_PATH = REPO_ROOT / "games" / "raw" / GAME_ID
MANIFEST = REPO_ROOT / "tmp" / "raw_obfuscator_fixed_manifest.json"


def main() -> None:
    payload = {
        "run_label": "raw_single_game_fixed",
        "description": "Single raw game baseline obfuscator check after CLI-resolution fix.",
        "games": [
            {
                "game_id": GAME_ID,
                "display_name": "raw_single_game_fixed",
                "source_path": str(SOURCE_PATH.resolve()),
            }
        ],
    }
    MANIFEST.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    command = [
        str(VENV_PYTHON),
        str(OBF_ROOT / "scripts" / "game_obfuscator_cli.py"),
        "start",
        "--manifest",
        str(MANIFEST),
        "--run-id",
        "run_game_obfuscator_raw_single_game_fixed",
        "--timeout-ms",
        "8000",
        "--max-game-seconds",
        "300",
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()