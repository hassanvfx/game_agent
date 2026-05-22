#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str((REPO_ROOT / "tools" / "game_publish_pipeline" / "scripts").resolve()))

import sync_to_gcs as sync_module  # noqa: E402


def main() -> int:
    remote_listing = "\n".join(
        [
            "gs://friendjam-ios/games-prod/public/gamezone-alpha/index.html",
            "gs://friendjam-ios/games-prod/public/gamezone-alpha/screenshots/001.png",
            "gs://friendjam-ios/games-prod/public/gamezone-beta/index.html",
            "gs://friendjam-ios/games-prod/public/index.json",
        ]
    )
    remote_names = sync_module.parse_remote_item_names(remote_listing, "gs://friendjam-ios/games-prod/public")
    prune_ops = sync_module.build_prune_operations_from_item_names(
        target="public",
        destination_root="gs://friendjam-ios/games-prod/public",
        project="jabali-prod",
        local_names=["gamezone-alpha", "gamezone-gamma"],
        remote_names=remote_names,
    )

    payload = {
        "remote_names": remote_names,
        "prune_item_names": [operation["item_name"] for operation in prune_ops],
        "prune_commands": [operation["command"] for operation in prune_ops],
    }
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())