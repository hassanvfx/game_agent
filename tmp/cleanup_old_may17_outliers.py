from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path("/Users/hassan/repos/game_agent")
REPORT_PATH = REPO_ROOT / "tmp" / "may17_local_publish_overwrite_report.json"
PUBLIC_ROOT = REPO_ROOT / "games" / "published" / "public"
OBFUSCATED_ROOT = REPO_ROOT / "games" / "published" / "obfuscated"
RUNS_ROOT = REPO_ROOT / "games" / "published" / "runs"
MATERIALIZE_SCRIPT = REPO_ROOT / "tools" / "game_publish_pipeline" / "scripts" / "materialize_artifact_view.py"
GENERATE_ANNOTATOR_ENTRY_SCRIPT = REPO_ROOT / "tools" / "game_publish_pipeline" / "scripts" / "generate_annotator_entry.py"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def run_command(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=REPO_ROOT, capture_output=True, text=True)


def summarize_matching_catalog(path: Path, prefix: str) -> dict[str, Any]:
    payload = load_json(path) if path.exists() else {}
    if not isinstance(payload, dict):
        return {"path": str(path), "matching_count": 0, "matching_keys": {}}
    matching = {
        key: {
            "game_id": value.get("game_id") if isinstance(value, dict) else None,
            "title": value.get("title") if isinstance(value, dict) else None,
            "screenshots_count": len(value.get("screenshots") or []) if isinstance(value, dict) else None,
            "published_path": value.get("published_path") if isinstance(value, dict) else None,
        }
        for key, value in payload.items()
        if prefix in key
    }
    return {"path": str(path), "matching_count": len(matching), "matching_keys": matching}


def main() -> None:
    report = load_json(REPORT_PATH)
    before_public = ((report.get("before_public_app") or {}).get("matching_keys") or {})
    if not isinstance(before_public, dict):
        raise SystemExit("Report missing before_public_app.matching_keys")

    stale_records: list[dict[str, Any]] = []
    for key, record in before_public.items():
        if not isinstance(record, dict):
            continue
        game_id = str(record.get("game_id") or "")
        published_path = str(record.get("published_path") or "")
        screenshots_count = int(record.get("screenshots_count") or 0)
        if "__p" not in key:
            continue
        if screenshots_count != 0:
            continue
        if not published_path:
            continue
        stale_records.append(
            {
                "key": key,
                "game_id": game_id,
                "published_path": published_path,
                "public_dir": str(PUBLIC_ROOT / published_path),
                "obfuscated_dir": str(OBFUSCATED_ROOT / published_path),
            }
        )

    deleted_paths: list[str] = []
    for record in stale_records:
        for root in (PUBLIC_ROOT, OBFUSCATED_ROOT):
            target = root / str(record["published_path"])
            if target.exists():
                shutil.rmtree(target)
                deleted_paths.append(str(target))

    materialize_cmd = [
        sys.executable,
        str(MATERIALIZE_SCRIPT),
        "--runs-root",
        str(RUNS_ROOT),
        "--public-root",
        str(PUBLIC_ROOT),
        "--obfuscated-root",
        str(OBFUSCATED_ROOT),
        "--precedence",
        "latest-wins",
    ]
    materialize_result = run_command(materialize_cmd)

    annotator_cmd = [
        sys.executable,
        str(GENERATE_ANNOTATOR_ENTRY_SCRIPT),
        "--target",
        "both",
        "--public-root",
        str(PUBLIC_ROOT),
        "--obfuscated-root",
        str(OBFUSCATED_ROOT),
    ]
    annotator_result = run_command(annotator_cmd)

    prefix = "gamezone-0022d901-ea58-4a11-b909-fff27f0ee38f"
    result = {
        "stale_records": stale_records,
        "deleted_paths": deleted_paths,
        "materialize": {
            "command": materialize_cmd,
            "returncode": materialize_result.returncode,
            "stdout": materialize_result.stdout,
            "stderr": materialize_result.stderr,
        },
        "annotator": {
            "command": annotator_cmd,
            "returncode": annotator_result.returncode,
            "stdout": annotator_result.stdout,
            "stderr": annotator_result.stderr,
        },
        "after_public_app": summarize_matching_catalog(PUBLIC_ROOT / "app.json", prefix),
        "after_obfuscated_app": summarize_matching_catalog(OBFUSCATED_ROOT / "app.json", prefix),
        "after_public_index": summarize_matching_catalog(PUBLIC_ROOT / "index.json", prefix),
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()