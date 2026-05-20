#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from batch_pipeline_state import resolve_manifest


MANIFEST_PATH = Path(__file__).resolve().parent / "vatsal_top_mechanics.json"
ANNOTATIONS_PATH = Path(__file__).resolve().parent / "vatsal_top_mechanics.annotations.json"


def main() -> int:
    manifest_payload = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    annotations_payload = json.loads(ANNOTATIONS_PATH.read_text(encoding="utf-8"))

    resolved = resolve_manifest(manifest_payload)
    runs = resolved["runs"]
    prompts = [str(item.get("prompt") or "") for item in runs]
    unique_prompts = sorted({prompt for prompt in prompts if prompt})

    summary = {
        "manifest_path": str(MANIFEST_PATH),
        "annotations_path": str(ANNOTATIONS_PATH),
        "resolved_run_count": len(runs),
        "unique_prompt_count": len(unique_prompts),
        "annotations_item_count": len(annotations_payload.get("items", [])),
        "defaults": resolved.get("defaults", {}),
        "sample_prompts": prompts[:10],
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())