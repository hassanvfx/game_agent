from __future__ import annotations

import json
import shutil
import sys
import tempfile
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_ROOT = REPO_ROOT / "tools" / "game_obfuscator" / "scripts"
sys.path.insert(0, str(SCRIPTS_ROOT))

from obfuscate_separate_outputs import process_game
from orchestration_state import load_json


RUN_DIR = Path("tools/game_obfuscator/runs/run_game_obfuscator_20260510T135235Z")
GAME_ID = "gamezone-0a01fa77-8b8b-4c02-93db-07cf4e05ee06"


def main() -> None:
    source_run = RUN_DIR
    game_state = load_json(source_run / "games" / GAME_ID / "game_state.json")

    with tempfile.TemporaryDirectory(prefix="obfuscator-profile-") as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        temp_run = tmp_dir / source_run.name
        shutil.copytree(source_run, temp_run)

        temp_game_state = load_json(temp_run / "games" / GAME_ID / "game_state.json")
        start = time.perf_counter()
        result = process_game(temp_game_state, temp_run, timeout_ms=8000)
        elapsed = time.perf_counter() - start

        payload = {
            "elapsed_seconds": elapsed,
            "result_keys": sorted(result.keys()),
            "published_verification_status": result.get("published_verification_status"),
            "runtime_index": result.get("runtime_index"),
            "report_exists": (temp_run / "output" / GAME_ID / "artifacts" / "separate_obfuscation_report.json").exists(),
            "verification_exists": (temp_run / "output" / GAME_ID / "artifacts" / "verification.json").exists(),
            "separate_verification_exists": (
                temp_run / "output" / GAME_ID / "artifacts" / "separate_obfuscation" / "verification.json"
            ).exists(),
        }
        print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()