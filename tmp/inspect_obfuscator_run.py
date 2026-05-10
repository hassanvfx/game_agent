from __future__ import annotations

import hashlib
import json
from pathlib import Path


RUN_DIR = Path("tools/game_obfuscator/runs/run_game_obfuscator_20260510T135235Z")
GAME_ID = "gamezone-0a01fa77-8b8b-4c02-93db-07cf4e05ee06"


def digest_tree(root: Path) -> tuple[str, list[str]]:
    digest = hashlib.sha256()
    files: list[str] = []
    if not root.exists():
        return "", files
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        digest.update(rel.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
        files.append(rel)
    return digest.hexdigest(), files


def main() -> None:
    game_root = RUN_DIR / "output" / GAME_ID
    artifacts_root = game_root / "artifacts"
    source_root = artifacts_root / "pre_bundle_site"

    source_hash, source_files = digest_tree(source_root)
    output_hash, output_files = digest_tree(game_root)

    payload = {
        "run_dir_exists": RUN_DIR.exists(),
        "game_root_exists": game_root.exists(),
        "source_root_exists": source_root.exists(),
        "source_file_count": len(source_files),
        "output_file_count": len(output_files),
        "source_hash": source_hash,
        "output_hash": output_hash,
        "extra_in_output": sorted(set(output_files) - set(source_files)),
        "missing_in_output": sorted(set(source_files) - set(output_files)),
        "artifacts_files": sorted(
            str(path.relative_to(RUN_DIR))
            for path in artifacts_root.rglob("*")
            if path.is_file()
        ),
    }
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()