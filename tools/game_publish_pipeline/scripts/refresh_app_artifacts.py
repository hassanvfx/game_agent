#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

SCRIPT_PATH = Path(__file__).resolve()
TOOL_ROOT = SCRIPT_PATH.parents[1]
REPO_ROOT = TOOL_ROOT.parents[1]

DEFAULT_PUBLIC_ROOT = REPO_ROOT / "games" / "published" / "public"
DEFAULT_OBFUSCATED_ROOT = REPO_ROOT / "games" / "published" / "obfuscated"

INDEX_NAME = "index.json"
APP_TAGS_NAME = "app_tags.json"
APP_NAME = "app.json"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Refresh persistent public/obfuscated app artifacts after publishing."
    )
    parser.add_argument("--manifest", required=True, help="Manifest selecting published entries for the collection.")
    parser.add_argument("--collection-slug", default="vatsal_app_alpha", help="Collection slug prefix.")
    parser.add_argument("--public-root", default=str(DEFAULT_PUBLIC_ROOT), help="Published public root.")
    parser.add_argument("--obfuscated-root", default=str(DEFAULT_OBFUSCATED_ROOT), help="Published obfuscated root.")
    parser.add_argument(
        "--generated-output-root",
        default=str(REPO_ROOT / "tmp" / "generated_collections" / "vatsal_app_alpha"),
        help="Temporary generated output root for public catalog generation.",
    )
    return parser


def run_command(command: list[str]) -> None:
    result = subprocess.run(command, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_json_object(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    payload = load_json(path)
    if not isinstance(payload, dict):
        raise SystemExit(f"Expected JSON object at {path}, found {type(payload).__name__}.")
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def merge_records(existing: dict[str, Any], updates: dict[str, Any]) -> dict[str, Any]:
    merged = dict(existing)
    for composite_key, record in updates.items():
        if isinstance(composite_key, str) and composite_key and isinstance(record, dict):
            merged[composite_key] = record
    return merged


def merge_artifact(existing_path: Path, generated_path: Path) -> dict[str, Any]:
    existing_payload = load_json_object(existing_path)
    generated_payload = load_json_object(generated_path)
    merged_payload = merge_records(existing_payload, generated_payload)
    write_json(existing_path, merged_payload)
    return merged_payload


def build_public_catalog(
    manifest_path: Path,
    public_root: Path,
    generated_output_root: Path,
    public_index_path: Path,
    public_app_tags_path: Path,
    public_app_path: Path,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    if generated_output_root.exists():
        shutil.rmtree(generated_output_root)
    generated_output_root.mkdir(parents=True, exist_ok=True)

    command = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "generate_published_app_metadata.py"),
        "--manifest",
        str(manifest_path),
        "--published-root",
        str(public_root),
        "--output-root",
        str(generated_output_root),
        "--strict",
    ]
    run_command(command)

    public_index = merge_artifact(public_index_path, generated_output_root / INDEX_NAME)
    public_app_tags = merge_artifact(public_app_tags_path, generated_output_root / APP_TAGS_NAME)
    public_app = merge_artifact(public_app_path, generated_output_root / APP_NAME)
    return public_index, public_app_tags, public_app


def transform_obfuscated_payload(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    transformed: dict[str, dict[str, Any]] = {}
    for composite_key, record in payload.items():
        if not isinstance(composite_key, str) or not composite_key or not isinstance(record, dict):
            continue

        obfuscated_index_html = record.get("obfuscated_index_html")
        if not isinstance(obfuscated_index_html, str) or not obfuscated_index_html.strip():
            continue

        game_id = str(record.get("game_id") or "")
        published_path = str(record.get("published_path") or "")
        transformed_record = dict(record)
        transformed_record["index_html"] = obfuscated_index_html
        transformed_record["public_index_html"] = obfuscated_index_html
        transformed_record["published_path"] = published_path
        transformed_record["game_root"] = game_id

        for key in ("assets_css", "assets_js", "all_files"):
            value = transformed_record.get(key)
            if isinstance(value, list):
                transformed_record[key] = [
                    item[len(game_id) + 1 :] if game_id and str(item).startswith(f"{game_id}/") else item
                    for item in value
                ]

        transformed[composite_key] = transformed_record
    return transformed


def build_obfuscated_catalog(
    obfuscated_root: Path,
    public_index: dict[str, Any],
    public_app_tags: dict[str, Any],
    public_app: dict[str, Any],
) -> tuple[Path, Path, Path]:
    obfuscated_index_path = obfuscated_root / INDEX_NAME
    obfuscated_app_tags_path = obfuscated_root / APP_TAGS_NAME
    obfuscated_app_path = obfuscated_root / APP_NAME

    write_json(
        obfuscated_index_path,
        merge_records(load_json_object(obfuscated_index_path), transform_obfuscated_payload(public_index)),
    )
    write_json(
        obfuscated_app_tags_path,
        merge_records(load_json_object(obfuscated_app_tags_path), transform_obfuscated_payload(public_app_tags)),
    )
    write_json(
        obfuscated_app_path,
        merge_records(load_json_object(obfuscated_app_path), transform_obfuscated_payload(public_app)),
    )
    return obfuscated_index_path, obfuscated_app_tags_path, obfuscated_app_path


def main() -> None:
    args = build_parser().parse_args()

    manifest_path = Path(args.manifest).resolve()
    public_root = Path(args.public_root).resolve()
    obfuscated_root = Path(args.obfuscated_root).resolve()
    generated_output_root = Path(args.generated_output_root).resolve()

    public_index_path = public_root / INDEX_NAME
    public_app_tags_path = public_root / APP_TAGS_NAME
    public_app_path = public_root / APP_NAME

    public_index, public_app_tags, public_app = build_public_catalog(
        manifest_path,
        public_root,
        generated_output_root,
        public_index_path,
        public_app_tags_path,
        public_app_path,
    )
    obfuscated_index_path, obfuscated_app_tags_path, obfuscated_app_path = build_obfuscated_catalog(
        obfuscated_root,
        public_index,
        public_app_tags,
        public_app,
    )

    print(
        json.dumps(
            {
                "manifest": str(manifest_path),
                "collection_slug": str(args.collection_slug),
                "public_index": str(public_index_path),
                "public_app_tags": str(public_app_tags_path),
                "public_app": str(public_app_path),
                "obfuscated_index": str(obfuscated_index_path),
                "obfuscated_app_tags": str(obfuscated_app_tags_path),
                "obfuscated_app": str(obfuscated_app_path),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()