#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path("/Users/hassan/repos/game_agent")
PUBLIC_ROOT = ROOT / "games/published/public"
OBFUSCATED_ROOT = ROOT / "games/published/obfuscated"
TMP_OUTPUT_ROOT = ROOT / "tmp/generated_metadata_public_tag_recovery_latest"
BACKUP_ROOT = ROOT / "tmp/catalog_promotions"
AUDIT_SCRIPT = ROOT / "tmp/audit_published_catalog_regressions.py"
GENERATOR_SCRIPT = ROOT / "scripts/generate_published_app_metadata.py"


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def run(command: list[str]) -> None:
    subprocess.run(command, check=True)


def transform_obfuscated_payload(payload: dict) -> dict:
    transformed: dict = {}
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


def backup_file(src: Path, dest_dir: Path) -> None:
    dest_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest_dir / src.name)


def main() -> None:
    stamp = utc_stamp()
    backup_dir = BACKUP_ROOT / f"promotion_{stamp}"
    backup_public_dir = backup_dir / "public"
    backup_obfuscated_dir = backup_dir / "obfuscated"

    for name in ("index.json", "app_tags.json", "app.json"):
        backup_file(PUBLIC_ROOT / name, backup_public_dir)
        backup_file(OBFUSCATED_ROOT / name, backup_obfuscated_dir)

    run(
        [
            sys.executable,
            str(GENERATOR_SCRIPT),
            "--published-root",
            str(PUBLIC_ROOT),
            "--output-root",
            str(TMP_OUTPUT_ROOT),
            "--strict",
        ]
    )

    public_index = load_json(TMP_OUTPUT_ROOT / "index.json")
    public_app_tags = load_json(TMP_OUTPUT_ROOT / "app_tags.json")
    public_app = load_json(TMP_OUTPUT_ROOT / "app.json")

    write_json(PUBLIC_ROOT / "index.json", public_index)
    write_json(PUBLIC_ROOT / "app_tags.json", public_app_tags)
    write_json(PUBLIC_ROOT / "app.json", public_app)

    write_json(OBFUSCATED_ROOT / "index.json", transform_obfuscated_payload(public_index))
    write_json(OBFUSCATED_ROOT / "app_tags.json", transform_obfuscated_payload(public_app_tags))
    write_json(OBFUSCATED_ROOT / "app.json", transform_obfuscated_payload(public_app))

    real_audit_path = backup_dir / "real_catalog_audit.json"
    run(
        [
            sys.executable,
            str(AUDIT_SCRIPT),
            "--public-app",
            str(PUBLIC_ROOT / "app.json"),
            "--obfuscated-app",
            str(OBFUSCATED_ROOT / "app.json"),
            "--report-path",
            str(real_audit_path),
            "--label",
            "real_structured_only_promotion",
        ]
    )

    print(
        json.dumps(
            {
                "backup_dir": str(backup_dir),
                "public_app": str(PUBLIC_ROOT / "app.json"),
                "obfuscated_app": str(OBFUSCATED_ROOT / "app.json"),
                "real_audit_path": str(real_audit_path),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()