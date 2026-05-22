#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str((REPO_ROOT / "tools" / "game_publish_pipeline").resolve()))

from game_publish_pipeline.cleanup import (  # noqa: E402
    build_candidate_directory_map,
    build_candidate_key_set,
    build_regression_audit,
    detect_identical_public_obfuscated,
    sanitize_published_media_refs,
    write_json,
)


def main() -> int:
    public_root = REPO_ROOT / "games" / "published" / "public"
    obfuscated_root = REPO_ROOT / "games" / "published" / "obfuscated"
    public_app = public_root / "app.json"
    obfuscated_app = obfuscated_root / "app.json"

    audit = build_regression_audit(public_app, obfuscated_app, sample_limit=3, label="smoke")
    identical = detect_identical_public_obfuscated(public_root, obfuscated_root)
    mapping = build_candidate_directory_map(
        public_app_path=public_app,
        obfuscated_app_path=obfuscated_app,
        public_root=public_root,
        obfuscated_root=obfuscated_root,
        candidate_keys=build_candidate_key_set(audit),
        affected_gamezones=identical["affected_gamezone_ids"],
        audit_report=audit,
    )
    sanitize = sanitize_published_media_refs([public_root, obfuscated_root], apply_changes=False)

    payload = {
        "audit_summary": audit["summary"],
        "identical_summary": {
            "affected_gamezone_count": identical["affected_gamezone_count"],
            "identical_pairs": identical["identical_pairs"],
        },
        "mapping_summary": {
            "candidate_count": mapping["candidate_count"],
            "affected_gamezone_count": mapping["affected_gamezone_count"],
            "public_delete_targets": len(mapping["public_delete_targets"]),
            "obfuscated_delete_targets": len(mapping["obfuscated_delete_targets"]),
        },
        "sanitize_summary": {
            "scanned_file_count": sanitize["scanned_file_count"],
            "changed_file_count": sanitize["changed_file_count"],
            "removed_reference_count": sanitize["removed_reference_count"],
        },
    }

    output_path = REPO_ROOT / "tmp" / "deploy_gcg_cleanup_helper_smoke.json"
    write_json(output_path, payload)
    print(json.dumps({"report_path": str(output_path), **payload}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())