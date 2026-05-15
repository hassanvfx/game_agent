from __future__ import annotations

import json
import random
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_ROOT = REPO_ROOT / "games" / "raw"
OBF_ROOT = REPO_ROOT / "tools" / "game_obfuscator"
RUNS_ROOT = OBF_ROOT / "runs"
VENV_PYTHON = OBF_ROOT / ".venv" / "bin" / "python"
PYTHON = VENV_PYTHON if VENV_PYTHON.exists() else Path(sys.executable)

SAMPLE_SIZE = 4
SEED = 20260514
RUN_ID = "run_game_obfuscator_raw_random4_baseline"
MANIFEST_PATH = REPO_ROOT / "tmp" / "raw_random4_obfuscator_manifest.json"


def select_games() -> list[Path]:
    candidates = [
        path
        for path in sorted(RAW_ROOT.iterdir())
        if path.is_dir() and path.name.startswith("gamezone-") and (path / "index.html").exists()
    ]
    if len(candidates) < SAMPLE_SIZE:
        raise SystemExit(f"Expected at least {SAMPLE_SIZE} raw games with index.html under {RAW_ROOT}")
    rng = random.Random(SEED)
    return sorted(rng.sample(candidates, SAMPLE_SIZE), key=lambda path: path.name)


def build_manifest(games: list[Path]) -> dict:
    return {
        "run_label": "raw_random4_baseline",
        "description": "Four random games sampled from games/raw for baseline obfuscator default-behavior inspection.",
        "selection": {
            "source_root": str(RAW_ROOT.resolve()),
            "sample_size": SAMPLE_SIZE,
            "seed": SEED,
        },
        "games": [
            {
                "game_id": game_dir.name,
                "display_name": game_dir.name,
                "source_path": str(game_dir.resolve()),
            }
            for game_dir in games
        ],
    }


def main() -> None:
    selected_games = select_games()
    manifest = build_manifest(selected_games)
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    run_dir = RUNS_ROOT / RUN_ID
    if run_dir.exists():
        raise SystemExit(
            f"Run directory already exists: {run_dir}\n"
            "Remove it first if you want to re-run with the same run id."
        )

    command = [
        str(PYTHON),
        str(OBF_ROOT / "scripts" / "game_obfuscator_cli.py"),
        "start",
        "--manifest",
        str(MANIFEST_PATH),
        "--run-id",
        RUN_ID,
    ]
    result = subprocess.run(command, capture_output=True, text=True)

    output = {
        "seed": SEED,
        "manifest_path": str(MANIFEST_PATH.resolve()),
        "selected_games": [game_dir.name for game_dir in selected_games],
        "command": command,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }
    print(json.dumps(output, indent=2))

    raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()