from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = REPO_ROOT / "tmp" / "raw_random4_obfuscator_manifest.json"
REPORT_PATH = REPO_ROOT / "tmp" / "game_publish_pipeline_raw_random4_report.json"


def main() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    sources = [str(Path(game["source_path"]).resolve()) for game in manifest["games"]]

    command = [
        sys.executable,
        str(REPO_ROOT / "tools" / "game_publish_pipeline" / "scripts" / "publish_games.py"),
        "--report-path",
        str(REPORT_PATH),
        "--overwrite",
        "--inputs",
        *sources,
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()