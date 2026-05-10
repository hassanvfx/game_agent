#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

DEPLOY_MANIFEST = Path("tmp/retry_manifests/latest_selected_remix_deploy_manifest.json")
OUTPUT_PATH = Path("tmp/retry_manifests/latest_selected_remix_obfuscator_manifest.json")
PUBLIC_ROOT = Path("games/published/public")
OBFUSCATED_ROOT = Path("games/published/obfuscated")


def compute_remix_uuid(source: Path) -> str:
    import hashlib

    digest = hashlib.sha256()
    files = sorted(path for path in source.rglob("*") if path.is_file())
    for path in files:
        digest.update(path.relative_to(source).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(hashlib.sha256(path.read_bytes()).hexdigest().encode("utf-8"))
        digest.update(b"\0")
    return digest.hexdigest()[:32]


def main() -> int:
    deploy_manifest = json.loads(DEPLOY_MANIFEST.read_text(encoding="utf-8"))
    games = []
    for entry in deploy_manifest:
        source = Path(entry["source"]).resolve()
        game_id = source.name
        remix_uuid = compute_remix_uuid(source)
        public_dir = (PUBLIC_ROOT / game_id / f"remix-{remix_uuid}").resolve()
        obfuscated_dir = (OBFUSCATED_ROOT / game_id / f"remix-{remix_uuid}").resolve()
        games.append(
            {
                "game_id": game_id,
                "source_path": str(public_dir),
                "output_path": str(obfuscated_dir),
            }
        )

    payload = {"games": games}
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(games)} games to {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())