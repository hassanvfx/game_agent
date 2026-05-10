from __future__ import annotations

import json
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
OBF_ROOT = REPO_ROOT / "tools" / "game_obfuscator"
VENV_PYTHON = OBF_ROOT / ".venv" / "bin" / "python"

MANIFEST = REPO_ROOT / "tmp" / "baseline_obfuscator_manifest.json"


def main() -> None:
    payload = {
        "run_label": "baseline_public_single_game",
        "description": "Single known public deploy for baseline obfuscator check.",
        "games": [
            {
                "game_id": "gamezone-0a01fa77-8b8b-4c02-93db-07cf4e05ee06",
                "display_name": "baseline_public_single_game",
                "source_path": str(
                    (
                        REPO_ROOT
                        / "games"
                        / "published"
                        / "public"
                        / "gamezone-0a01fa77-8b8b-4c02-93db-07cf4e05ee06"
                        / "remix-321f864173014c43aa4d4afad5e07111"
                    ).resolve()
                ),
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
        "run_game_obfuscator_baseline_single_public",
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