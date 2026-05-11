#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

ROOT = Path("/Users/hassan/repos/game_agent")
PUBLIC_ROOT = ROOT / "games/published/public"
OBFUSCATED_ROOT = ROOT / "games/published/obfuscated"

PUBLIC_INDEX_PATH = PUBLIC_ROOT / "vatsal_app_alpha-index.json"
PUBLIC_APP_TAGS_PATH = PUBLIC_ROOT / "vatsal_app_alpha-app_tags.json"
PUBLIC_APP_PATH = PUBLIC_ROOT / "vatsal_app_alpha-app.json"

OBFUSCATED_INDEX_PATH = OBFUSCATED_ROOT / "vatsal_app_alpha-index.json"
OBFUSCATED_APP_TAGS_PATH = OBFUSCATED_ROOT / "vatsal_app_alpha-app_tags.json"
OBFUSCATED_APP_PATH = OBFUSCATED_ROOT / "vatsal_app_alpha-app.json"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def obfuscated_game_path(record: dict[str, Any]) -> str:
    obfuscated_index_html = record.get("obfuscated_index_html")
    if isinstance(obfuscated_index_html, str) and obfuscated_index_html.strip():
        return obfuscated_index_html
    return ""


def transform_payload(payload: dict[str, Any]) -> dict[str, Any]:
    transformed: dict[str, Any] = {}
    for composite_key, record in payload.items():
        if not isinstance(record, dict):
            continue
        obfuscated_index_html = obfuscated_game_path(record)
        if not obfuscated_index_html:
            continue

        game_id = str(record.get("game_id") or "")
        screenshots = record.get("screenshots")
        if isinstance(screenshots, list):
            normalized_screenshots = []
            for value in screenshots:
                text = str(value)
                prefix = f"{game_id}/"
                if game_id and text.startswith(prefix):
                    normalized_screenshots.append(text[len(prefix):])
                else:
                    normalized_screenshots.append(text)
            screenshots = normalized_screenshots

        transformed_record = dict(record)
        transformed_record["index_html"] = obfuscated_index_html
        transformed_record["public_index_html"] = obfuscated_index_html
        transformed_record["published_path"] = game_id
        transformed_record["game_root"] = game_id
        transformed_record["screenshots"] = screenshots if isinstance(screenshots, list) else record.get("screenshots", [])

        for key in ("screenshots_png", "screenshots_jpg", "assets_css", "assets_js", "all_files"):
            value = transformed_record.get(key)
            if isinstance(value, list):
                normalized = []
                for item in value:
                    text = str(item)
                    prefix = f"{game_id}/"
                    if game_id and text.startswith(prefix):
                        normalized.append(text[len(prefix):])
                    else:
                        normalized.append(text)
                transformed_record[key] = normalized

        transformed[composite_key] = transformed_record
    return transformed


def copy_annotator() -> Path:
    source = PUBLIC_ROOT / "565a0bf4-5160-47b8-a905-2f4362475cdf-annotator.html"
    target = OBFUSCATED_ROOT / "565a0bf4-5160-47b8-a905-2f4362475cdf-annotator.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    return target


def main() -> None:
    public_index = load_json(PUBLIC_INDEX_PATH)
    public_app_tags = load_json(PUBLIC_APP_TAGS_PATH)
    public_app = load_json(PUBLIC_APP_PATH)

    obfuscated_index = transform_payload(public_index)
    obfuscated_app_tags = transform_payload(public_app_tags)
    obfuscated_app = transform_payload(public_app)

    write_json(OBFUSCATED_INDEX_PATH, obfuscated_index)
    write_json(OBFUSCATED_APP_TAGS_PATH, obfuscated_app_tags)
    write_json(OBFUSCATED_APP_PATH, obfuscated_app)
    annotator_path = copy_annotator()

    sample_key = next(iter(obfuscated_app), None)
    sample_record = obfuscated_app[sample_key] if sample_key else {}

    print(
        json.dumps(
            {
                "entries_written": len(obfuscated_app),
                "obfuscated_index": str(OBFUSCATED_INDEX_PATH),
                "obfuscated_app_tags": str(OBFUSCATED_APP_TAGS_PATH),
                "obfuscated_app": str(OBFUSCATED_APP_PATH),
                "annotator_html": str(annotator_path),
                "sample_key": sample_key,
                "sample_index_html": sample_record.get("index_html"),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()