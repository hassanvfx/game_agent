#!/usr/bin/env python3
"""Validate mirrored library root resolution and filesystem-first reconciliation."""

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
from audio_reality import derive_library_index_from_catalog, reconcile_catalog_to_filesystem  # type: ignore  # noqa: E402
from build_audio_jobs_list import build_jobs_list_payload  # type: ignore  # noqa: E402


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def count_asset_variants(catalog: dict) -> int:
    total = 0
    for record in catalog.get("records", []):
        if record.get("record_type") == "asset_family":
            total += len(record.get("variants") or [])
    return total


def count_semantic_items(catalog: dict) -> int:
    total = 0
    for record in catalog.get("records", []):
        if record.get("record_type") == "semantic_query":
            total += len(record.get("reference_items") or [])
    return total


def main() -> int:
    library_root = resolve_library_root()
    catalog_path = library_root / "catalog.json"
    audios_path = library_root / "audios.json"

    catalog = load_json(catalog_path)
    audios = load_json(audios_path)
    before_asset_variants = count_asset_variants(catalog)
    before_semantic_items = count_semantic_items(catalog)

    reconciled_catalog = copy.deepcopy(catalog)
    changed = reconcile_catalog_to_filesystem(reconciled_catalog, audio_root=library_root)
    after_asset_variants = count_asset_variants(reconciled_catalog)
    after_semantic_items = count_semantic_items(reconciled_catalog)
    derived_index = derive_library_index_from_catalog(reconciled_catalog)
    jobs_payload = build_jobs_list_payload(
        reconciled_catalog,
        desired_total_variants=4,
        variants_per_request=2,
    )

    output = {
        "library_root": str(library_root.relative_to(ROOT)),
        "catalog_path": str(catalog_path.relative_to(ROOT)),
        "audios_path": str(audios_path.relative_to(ROOT)),
        "root_is_mirrored": library_root == ROOT / "tools" / "library" / "assets" / "audios",
        "reconciliation_changed_catalog": changed,
        "asset_variants_before": before_asset_variants,
        "asset_variants_after": after_asset_variants,
        "semantic_items_before": before_semantic_items,
        "semantic_items_after": after_semantic_items,
        "library_groups_before": len(audios),
        "library_groups_after": len(derived_index),
        "jobs_summary_after_reconciliation": jobs_payload.get("summary", {}),
    }
    print(json.dumps(output, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())