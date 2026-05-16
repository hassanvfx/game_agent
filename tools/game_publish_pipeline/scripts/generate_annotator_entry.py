#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve()
TOOL_ROOT = SCRIPT_PATH.parents[1]
REPO_ROOT = TOOL_ROOT.parents[1]

DEFAULT_TEMPLATE_PATH = REPO_ROOT / "dashboard" / "annotator_template.html"
DEFAULT_PUBLIC_ROOT = REPO_ROOT / "games" / "published" / "public"
DEFAULT_OBFUSCATED_ROOT = REPO_ROOT / "games" / "published" / "obfuscated"

ANNOTATOR_ENTRY_NAME = "annotator.html"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate deployable public/obfuscated annotator HTML entries from the shared template."
    )
    parser.add_argument(
        "--target",
        choices=("public", "obfuscated", "both"),
        default="both",
        help="Which annotator entry roots to generate.",
    )
    parser.add_argument(
        "--template-path",
        default=str(DEFAULT_TEMPLATE_PATH),
        help="Source annotator template HTML.",
    )
    parser.add_argument(
        "--public-root",
        default=str(DEFAULT_PUBLIC_ROOT),
        help="Published public root that should receive the annotator entry.",
    )
    parser.add_argument(
        "--obfuscated-root",
        default=str(DEFAULT_OBFUSCATED_ROOT),
        help="Published obfuscated root that should receive the annotator entry.",
    )
    parser.add_argument(
        "--entry-name",
        default=ANNOTATOR_ENTRY_NAME,
        help="Deployable annotator filename.",
    )
    parser.add_argument(
        "--app-json-name",
        default="app.json",
        help="Relative app metadata filename the annotator should fetch.",
    )
    parser.add_argument(
        "--play-root",
        default="",
        help="Relative play root prefix used when resolving index_html and screenshot paths.",
    )
    return parser


def replace_js_constant(content: str, constant_name: str, value: str) -> str:
    marker = f'const {constant_name} = "'
    start = content.find(marker)
    if start == -1:
        raise SystemExit(f"Could not find JS constant {constant_name} in annotator template.")
    value_start = start + len(marker)
    value_end = content.find('"', value_start)
    if value_end == -1:
        raise SystemExit(f"Could not parse JS constant {constant_name} in annotator template.")
    return content[:value_start] + value + content[value_end:]


def build_annotator_html(template_text: str, app_json_name: str, play_root: str) -> str:
    updated = replace_js_constant(template_text, "APP_DATA_PATH", app_json_name)
    updated = replace_js_constant(updated, "PLAY_ROOT", play_root)
    return updated


def validate_root(path: Path, label: str) -> None:
    if not path.is_dir():
        raise SystemExit(f"{label} root does not exist or is not a directory: {path}")
    app_json_path = path / "app.json"
    if not app_json_path.is_file():
        raise SystemExit(f"{label} root is missing app.json: {app_json_path}")


def write_entry(root: Path, entry_name: str, content: str) -> Path:
    output_path = root / entry_name
    output_path.write_text(content, encoding="utf-8")
    return output_path


def main() -> None:
    args = build_parser().parse_args()

    template_path = Path(args.template_path).resolve()
    public_root = Path(args.public_root).resolve()
    obfuscated_root = Path(args.obfuscated_root).resolve()
    entry_name = str(args.entry_name)
    app_json_name = str(args.app_json_name)
    play_root = str(args.play_root)

    template_text = template_path.read_text(encoding="utf-8")
    annotator_html = build_annotator_html(template_text, app_json_name, play_root)

    results: dict[str, str] = {}

    if args.target in {"public", "both"}:
        validate_root(public_root, "public")
        results["public"] = str(write_entry(public_root, entry_name, annotator_html))

    if args.target in {"obfuscated", "both"}:
        validate_root(obfuscated_root, "obfuscated")
        results["obfuscated"] = str(write_entry(obfuscated_root, entry_name, annotator_html))

    print(
        json.dumps(
            {
                "template_path": str(template_path),
                "entry_name": entry_name,
                "app_json_name": app_json_name,
                "play_root": play_root,
                "results": results,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()