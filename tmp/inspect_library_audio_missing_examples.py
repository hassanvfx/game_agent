#!/usr/bin/env python3
"""Show concrete examples of filesystem-first missing audio after reconciliation."""

from __future__ import annotations

import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "tools" / "library" / "scripts"

import sys

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from audio_paths import resolve_library_root  # type: ignore  # noqa: E402
from audio_reality import reconcile_catalog_to_filesystem  # type: ignore  # noqa: E402
from build_audio_jobs_list import build_jobs_list_payload  # type: ignore  # noqa: E402


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    library_root = resolve_library_root()
    catalog = load_json(library_root / "catalog.json")
    reconciled = copy.deepcopy(catalog)
    reconcile_catalog_to_filesystem(reconciled, audio_root=library_root)
    jobs = build_jobs_list_payload(reconciled, desired_total_variants=4, variants_per_request=2)["jobs"]

    pending_asset = [job for job in jobs if job["record_type"] == "asset_family" and job["missing_variants"] > 0]
    pending_semantic = [job for job in jobs if job["record_type"] == "semantic_query" and job["missing_variants"] > 0]

    payload = {
        "library_root": str(library_root.relative_to(ROOT)),
        "pending_asset_family_count": len(pending_asset),
        "pending_semantic_query_count": len(pending_semantic),
        "sample_pending_asset_families": [
            {
                "id": job["id"],
                "existing_count": job["existing_count"],
                "missing_variants": job["missing_variants"],
                "next_destinations": job["next_destinations"][:4],
            }
            for job in pending_asset[:5]
        ],
        "sample_pending_semantic_queries": [
            {
                "id": job["id"],
                "destination_dir": job["destination_dir"],
                "existing_count": job["existing_count"],
                "missing_variants": job["missing_variants"],
                "next_destinations": job["next_destinations"][:4],
            }
            for job in pending_semantic[:5]
        ],
    }
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())