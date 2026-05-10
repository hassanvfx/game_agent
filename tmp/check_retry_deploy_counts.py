#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

MANIFEST_PATH = Path("tmp/retry_manifests/latest_selected_remix_deploy_manifest.json")
PUBLIC_ROOT = Path("games/published/public")
OBFUSCATED_ROOT = Path("games/published/obfuscated")


def load_manifest() -> list[dict]:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def compute_remix_uuid(source: Path) -> str:
    import hashlib

    digest = hashlib.sha256()
    files = sorted(path for path in source.rglob("*") if path.is_file())
    for path in files:
        digest.update(path.relative_to(source).as_posix().encode("utf-8"))
        digest.update(b"\0")
        file_digest = hashlib.sha256(path.read_bytes()).hexdigest().encode("utf-8")
        digest.update(file_digest)
        digest.update(b"\0")
    return digest.hexdigest()[:32]


def main() -> int:
    manifest = load_manifest()
    expected = len(manifest)
    public_found = 0
    obfuscated_found = 0
    missing_public: list[str] = []
    missing_obfuscated: list[str] = []

    for entry in manifest:
        source = Path(entry["source"])
        game_id = source.name
        remix_uuid = compute_remix_uuid(source)

        public_dir = PUBLIC_ROOT / game_id / f"remix-{remix_uuid}"
        obfuscated_dir = OBFUSCATED_ROOT / game_id / f"remix-{remix_uuid}"

        if public_dir.exists():
            public_found += 1
        else:
            missing_public.append(str(public_dir))

        if obfuscated_dir.exists():
            obfuscated_found += 1
        else:
            missing_obfuscated.append(str(obfuscated_dir))

    print(f"expected_manifest_entries: {expected}")
    print(f"public_deploy_dirs_found: {public_found}")
    print(f"obfuscated_game_dirs_found: {obfuscated_found}")

    if missing_public:
        print("\nMissing public deploy dirs:")
        for path in missing_public:
            print(f"  - {path}")

    if missing_obfuscated:
        print("\nMissing obfuscated game dirs:")
        for path in missing_obfuscated:
            print(f"  - {path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())