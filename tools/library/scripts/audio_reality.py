#!/usr/bin/env python3
"""Filesystem-first reconciliation helpers for library audio artifacts."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any

from audio_paths import local_path_from_location, location_from_url


def filter_library_index_against_filesystem(
    library_index: dict[str, list[dict[str, Any]]],
    *,
    audio_root: Path,
) -> tuple[dict[str, list[dict[str, Any]]], bool]:
    changed = False
    filtered: dict[str, list[dict[str, Any]]] = {}
    for group, items in library_index.items():
        kept: list[dict[str, Any]] = []
        for item in items:
            location = item.get("location")
            if not isinstance(location, str) or not location:
                changed = True
                continue
            if not local_path_from_location(audio_root, location).is_file():
                changed = True
                continue
            kept.append(item)
        filtered[group] = kept
    return filtered, changed


def reconcile_catalog_to_filesystem(catalog: dict[str, Any], *, audio_root: Path) -> bool:
    changed = False
    for record in catalog.get("records", []):
        if record.get("record_type") == "semantic_query":
            items = record.get("reference_items") or []
            kept_items: list[dict[str, Any]] = []
            for item in items:
                if not isinstance(item, dict):
                    changed = True
                    continue
                url = item.get("url")
                if not isinstance(url, str) or not url:
                    changed = True
                    continue
                location = location_from_url(url)
                if not local_path_from_location(audio_root, location).is_file():
                    changed = True
                    continue
                kept_items.append(item)
            if kept_items != items:
                record["reference_items"] = kept_items
        else:
            variants = record.get("variants") or []
            kept_variants: list[dict[str, Any]] = []
            for variant in variants:
                if not isinstance(variant, dict):
                    changed = True
                    continue
                location = variant.get("location")
                if not isinstance(location, str) or not location:
                    changed = True
                    continue
                if not local_path_from_location(audio_root, location).is_file():
                    changed = True
                    continue
                kept_variants.append(variant)
            if kept_variants != variants:
                record["variants"] = kept_variants
    return changed


def derive_library_index_from_catalog(catalog: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in catalog.get("records", []):
        if record.get("record_type") != "asset_family":
            continue
        grouped[record["group"]] = list(record.get("variants") or [])
    return dict(grouped)
