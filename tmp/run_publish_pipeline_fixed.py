from __future__ import annotations

import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PYTHON = "python3"

SOURCE = REPO_ROOT / "games" / "raw" / "gamezone-2c5abec2-ad99-4268-96e0-10fda01cfc5a"


def main() -> None:
    command = [
        PYTHON,
        str(REPO_ROOT / "tools" / "game_publish_pipeline" / "scripts" / "publish_games.py"),
        "--inputs",
        str(SOURCE.resolve()),
        "--overwrite",
        "--report-path",
        str(REPO_ROOT / "tmp" / "game_publish_pipeline_fixed_report.json"),
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()