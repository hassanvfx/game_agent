#!/usr/bin/env python3
from __future__ import annotations

import contextlib
import io
import json
import shutil
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str((REPO_ROOT / "tools" / "game_publish_pipeline" / "scripts").resolve()))

import sync_to_gcs as sync_module  # noqa: E402


def main() -> int:
    original_argv = list(sys.argv)
    stdout_buffer = io.StringIO()
    original_list_remote_item_names = sync_module.list_remote_item_names
    smoke_root = REPO_ROOT / "tmp" / "smoke_sync_to_gcs_public_root"

    try:
        if smoke_root.exists():
            shutil.rmtree(smoke_root)
        (smoke_root / "gamezone-alpha").mkdir(parents=True, exist_ok=True)
        (smoke_root / "gamezone-gamma").mkdir(parents=True, exist_ok=True)

        sync_module.list_remote_item_names = lambda destination_root, project: [  # type: ignore[assignment]
            "gamezone-alpha",
            "gamezone-beta",
        ]
        sys.argv = [
            "sync_to_gcs.py",
            "--target",
            "public",
            "--mode",
            "per-item",
            "--dry-run",
            "--prune-remote",
            "--public-root",
            str(smoke_root),
        ]
        with contextlib.redirect_stdout(stdout_buffer):
            sync_module.main()
    finally:
        sync_module.list_remote_item_names = original_list_remote_item_names  # type: ignore[assignment]
        sys.argv = original_argv
        if smoke_root.exists():
            shutil.rmtree(smoke_root)

    stdout_text = stdout_buffer.getvalue()

    payload = None
    for index, char in enumerate(stdout_text):
        if char != "{":
            continue
        candidate = stdout_text[index:].strip()
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            payload = parsed
            break

    if payload is None:
        raise SystemExit("Could not parse JSON payload from sync_to_gcs main smoke output.")

    summary = payload.get("summary") or {}
    prune_plans = payload.get("prune_plans") or []
    compact = {
        "summary": summary,
        "stale_remote_item_names": [
            item
            for plan in prune_plans
            for item in (plan.get("stale_remote_item_names") or [])
        ],
    }
    print(json.dumps(compact, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())