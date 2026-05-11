#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path("/Users/hassan/repos/game_agent")
PUBLIC_APP_PATH = ROOT / "games/published/public/vatsal_app_alpha-app.json"
OUTPUT_PATH = ROOT / "tmp/verify_obfuscated_path_shape.json"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    public_app = load_json(PUBLIC_APP_PATH)
    checked = []
    with_variant = []
    missing_contract_index = []
    missing_contract_match = []

    for composite_key, item in public_app.items():
        status = item.get("obfuscation_status") or {}
        record = {
            "composite_key": composite_key,
            "public_index_html": item.get("public_index_html") or item.get("index_html"),
            "obfuscated_index_html": item.get("obfuscated_index_html"),
            "has_obfuscated_variant": bool(item.get("has_obfuscated_variant")),
            "contract_source": status.get("contract_source"),
            "contract_matched": bool(status.get("contract_matched")),
            "contract_has_output_path": bool(status.get("contract_has_output_path")),
            "contract_expected_output_path": status.get("contract_expected_output_path"),
            "contract_output_exists": bool(status.get("contract_output_exists")),
            "contract_index_exists": bool(status.get("contract_index_exists")),
        }
        checked.append(record)

        if record["has_obfuscated_variant"]:
            with_variant.append(record)
        if record["contract_matched"] and not record["contract_index_exists"]:
            missing_contract_index.append(record)
        if not record["contract_matched"]:
            missing_contract_match.append(record)

    payload = {
        "checked_count": len(checked),
        "with_variant_count": len(with_variant),
        "missing_contract_index_count": len(missing_contract_index),
        "missing_contract_match_count": len(missing_contract_match),
        "with_variant_examples": with_variant[:20],
        "missing_contract_index_examples": missing_contract_index[:20],
        "missing_contract_match_examples": missing_contract_match[:20],
    }
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(OUTPUT_PATH),
                "checked_count": len(checked),
                "with_variant_count": len(with_variant),
                "missing_contract_index_count": len(missing_contract_index),
                "missing_contract_match_count": len(missing_contract_match),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()