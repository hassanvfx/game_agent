#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys


def main() -> None:
    command = [
        sys.executable,
        "tools/game_publish_pipeline/scripts/publish_games.py",
        "--manifest",
        "tmp/retry_manifests/vatsal_app_alpha_10_pilot_manifest.json",
        "--published-public-root",
        "tmp/publisher_probe_10_retry/public",
        "--published-obfuscated-root",
        "tmp/publisher_probe_10_retry/obfuscated",
        "--report-path",
        "tmp/publisher_probe_10_retry/report.json",
        "--overwrite",
    ]
    raise SystemExit(subprocess.run(command).returncode)


if __name__ == "__main__":
    main()