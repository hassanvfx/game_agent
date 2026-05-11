#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


REPORT_PATH = Path("tmp/publisher_probe_10_retry/report.json")
PUBLIC_ROOT = Path("tmp/publisher_probe_10_retry/public").resolve()
OBFUSCATED_ROOT = Path("tmp/publisher_probe_10_retry/obfuscated").resolve()


def count_jpgs(path: Path) -> int:
    if not path.exists():
        return 0
    return len(sorted(path.glob("*.jpg")))


def main() -> None:
    report = json.loads(REPORT_PATH.read_text())
    rows: list[dict[str, object]] = []

    for item in report["deployment"]["results"]:
        deploy_dir = Path(item["deploy_dir"]).resolve()
        rel = deploy_dir.relative_to(PUBLIC_ROOT)
        obf_dir = OBFUSCATED_ROOT / rel

        public_shots = count_jpgs(deploy_dir / "screenshots")
        obf_shots = count_jpgs(obf_dir / "screenshots")

        rows.append(
            {
                "game_id": item["game_id"],
                "remix_uuid": item["remix_uuid"],
                "public_count": public_shots,
                "obfuscated_count": obf_shots,
                "public_ok": public_shots > 0,
                "obfuscated_ok": obf_shots > 0,
                "counts_match": public_shots == obf_shots,
            }
        )

    summary = {
        "report_path": str(REPORT_PATH),
        "total_rows": len(rows),
        "public_with_screenshots": sum(1 for row in rows if row["public_ok"]),
        "obfuscated_with_screenshots": sum(1 for row in rows if row["obfuscated_ok"]),
        "matching_counts": sum(1 for row in rows if row["counts_match"]),
        "rows": rows,
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()