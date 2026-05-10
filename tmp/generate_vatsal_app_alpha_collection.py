#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path("/Users/hassan/repos/game_agent")
MANIFEST_PATH = ROOT / "tmp/retry_manifests/vatsal_app_alpha_231_manifest.json"
OUTPUT_ROOT = ROOT / "tmp/generated_collections/vatsal_app_alpha"
PUBLIC_ROOT = ROOT / "games/published/public"

PUBLIC_INDEX = PUBLIC_ROOT / "vatsal_app_alpha-index.json"
PUBLIC_APP_TAGS = PUBLIC_ROOT / "vatsal_app_alpha-app_tags.json"
PUBLIC_APP = PUBLIC_ROOT / "vatsal_app_alpha-app.json"


def main() -> None:
    if OUTPUT_ROOT.exists():
        shutil.rmtree(OUTPUT_ROOT)
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

    subprocess.run(
        [
            "python3",
            str(ROOT / "scripts/generate_published_app_metadata.py"),
            "--manifest",
            str(MANIFEST_PATH),
            "--published-root",
            str(PUBLIC_ROOT),
            "--output-root",
            str(OUTPUT_ROOT),
            "--strict",
        ],
        check=True,
    )

    shutil.copy2(OUTPUT_ROOT / "index.json", PUBLIC_INDEX)
    shutil.copy2(OUTPUT_ROOT / "app_tags.json", PUBLIC_APP_TAGS)
    shutil.copy2(OUTPUT_ROOT / "app.json", PUBLIC_APP)

    print(
        json.dumps(
            {
                "manifest": str(MANIFEST_PATH),
                "output_root": str(OUTPUT_ROOT),
                "public_index": str(PUBLIC_INDEX),
                "public_app_tags": str(PUBLIC_APP_TAGS),
                "public_app": str(PUBLIC_APP),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()