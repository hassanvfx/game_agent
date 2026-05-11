#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve()
TOOL_ROOT = SCRIPT_PATH.parents[1]
REPO_ROOT = TOOL_ROOT.parents[1]

DEFAULT_PUBLIC_ROOT = REPO_ROOT / "games" / "published" / "public"
DEFAULT_OBFUSCATED_ROOT = REPO_ROOT / "games" / "published" / "obfuscated"
DEFAULT_ANNOTATOR_HTML_NAME = "565a0bf4-5160-47b8-a905-2f4362475cdf-annotator.html"

PUBLIC_INDEX_NAME = "vatsal_app_alpha-index.json"
PUBLIC_APP_TAGS_NAME = "vatsal_app_alpha-app_tags.json"
PUBLIC_APP_NAME = "vatsal_app_alpha-app.json"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Refresh public/obfuscated annotator-facing app artifacts after publishing."
    )
    parser.add_argument("--manifest", required=True, help="Manifest selecting published entries for the collection.")
    parser.add_argument("--collection-slug", default="vatsal_app_alpha", help="Collection slug prefix.")
    parser.add_argument("--public-root", default=str(DEFAULT_PUBLIC_ROOT), help="Published public root.")
    parser.add_argument("--obfuscated-root", default=str(DEFAULT_OBFUSCATED_ROOT), help="Published obfuscated root.")
    parser.add_argument(
        "--annotator-html-name",
        default=DEFAULT_ANNOTATOR_HTML_NAME,
        help="Annotator HTML file name copied into the obfuscated root.",
    )
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


def build_public_catalog(
    manifest_path: Path,
    public_root: Path,
    generated_output_root: Path,
    public_index_path: Path,
    public_app_tags_path: Path,
    public_app_path: Path,
) -> None:
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

    shutil.copy2(generated_output_root / "index.json", public_index_path)
    shutil.copy2(generated_output_root / "app_tags.json", public_app_tags_path)
    shutil.copy2(generated_output_root / "app.json", public_app_path)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def transform_obfuscated_payload(payload: dict[str, dict]) -> dict[str, dict]:
    transformed: dict[str, dict] = {}
    for composite_key, record in payload.items():
        if not isinstance(record, dict):
            continue
        obfuscated_index_html = record.get("obfuscated_index_html")
        if not isinstance(obfuscated_index_html, str) or not obfuscated_index_html.strip():
            continue

        game_id = str(record.get("game_id") or "")
        transformed_record = dict(record)
        transformed_record["index_html"] = obfuscated_index_html
        transformed_record["public_index_html"] = obfuscated_index_html
        transformed_record["published_path"] = game_id
        transformed_record["game_root"] = game_id

        screenshots = transformed_record.get("screenshots")
        if isinstance(screenshots, list):
            transformed_record["screenshots"] = [f"{game_id}/screenshots/{Path(str(item)).name}" for item in screenshots]

        screenshots_png = transformed_record.get("screenshots_png")
        if isinstance(screenshots_png, list):
            transformed_record["screenshots_png"] = [f"{game_id}/screenshots/{Path(str(item)).name}" for item in screenshots_png]

        screenshots_jpg = transformed_record.get("screenshots_jpg")
        if isinstance(screenshots_jpg, list):
            transformed_record["screenshots_jpg"] = [f"{game_id}/screenshots/{Path(str(item)).name}" for item in screenshots_jpg]

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
    public_index_path: Path,
    public_app_tags_path: Path,
    public_app_path: Path,
    collection_slug: str,
) -> tuple[Path, Path, Path]:
    obfuscated_index_path = obfuscated_root / f"{collection_slug}-index.json"
    obfuscated_app_tags_path = obfuscated_root / f"{collection_slug}-app_tags.json"
    obfuscated_app_path = obfuscated_root / f"{collection_slug}-app.json"

    public_index = load_json(public_index_path)
    public_app_tags = load_json(public_app_tags_path)
    public_app = load_json(public_app_path)

    write_json(obfuscated_index_path, transform_obfuscated_payload(public_index))
    write_json(obfuscated_app_tags_path, transform_obfuscated_payload(public_app_tags))
    write_json(obfuscated_app_path, transform_obfuscated_payload(public_app))
    return obfuscated_index_path, obfuscated_app_tags_path, obfuscated_app_path


def copy_annotator(public_root: Path, obfuscated_root: Path, annotator_html_name: str) -> tuple[Path, Path]:
    public_annotator_path = public_root / annotator_html_name
    obfuscated_annotator_path = obfuscated_root / annotator_html_name
    obfuscated_annotator_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(public_annotator_path, obfuscated_annotator_path)
    return public_annotator_path, obfuscated_annotator_path


def main() -> None:
    args = build_parser().parse_args()

    manifest_path = Path(args.manifest).resolve()
    public_root = Path(args.public_root).resolve()
    obfuscated_root = Path(args.obfuscated_root).resolve()
    generated_output_root = Path(args.generated_output_root).resolve()
    collection_slug = str(args.collection_slug)
    annotator_html_name = str(args.annotator_html_name)

    public_index_path = public_root / f"{collection_slug}-index.json"
    public_app_tags_path = public_root / f"{collection_slug}-app_tags.json"
    public_app_path = public_root / f"{collection_slug}-app.json"

    build_public_catalog(
        manifest_path,
        public_root,
        generated_output_root,
        public_index_path,
        public_app_tags_path,
        public_app_path,
    )
    obfuscated_index_path, obfuscated_app_tags_path, obfuscated_app_path = build_obfuscated_catalog(
        obfuscated_root,
        public_index_path,
        public_app_tags_path,
        public_app_path,
        collection_slug,
    )
    public_annotator_path, obfuscated_annotator_path = copy_annotator(public_root, obfuscated_root, annotator_html_name)

    print(
        json.dumps(
            {
                "manifest": str(manifest_path),
                "collection_slug": collection_slug,
                "public_index": str(public_index_path),
                "public_app_tags": str(public_app_tags_path),
                "public_app": str(public_app_path),
                "obfuscated_index": str(obfuscated_index_path),
                "obfuscated_app_tags": str(obfuscated_app_tags_path),
                "obfuscated_app": str(obfuscated_app_path),
                "public_annotator": str(public_annotator_path),
                "obfuscated_annotator": str(obfuscated_annotator_path),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()