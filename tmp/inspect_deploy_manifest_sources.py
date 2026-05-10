#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

MANIFEST_PATH = Path("tmp/retry_manifests/latest_selected_remix_deploy_manifest.json")


def main() -> int:
    payload = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    for entry in payload:
        source = Path(entry["source"])
        print(source)
        for candidate in sorted(source.glob("*.json")):
            try:
                candidate.read_text(encoding="utf-8")
                print(f"  ok  {candidate.name}")
            except UnicodeDecodeError as exc:
                print(f"  bad {candidate.name}: {exc}")
                return 1
    print("all top-level json files are utf-8 readable")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())