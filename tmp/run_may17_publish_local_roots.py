from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path("/Users/hassan/repos/game_agent")
PUBLISH_SCRIPT = REPO_ROOT / "tools/game_publish_pipeline/scripts/publish_games.py"
RUN_SOURCE_ROOT = Path("/Volumes/HDD2026/output-May17th/run_game_remixer_20260517T132133Z/output")
SOURCE_DIRS = [
    RUN_SOURCE_ROOT / "gamezone-0022d901-ea58-4a11-b909-fff27f0ee38f__p01",
    RUN_SOURCE_ROOT / "gamezone-0022d901-ea58-4a11-b909-fff27f0ee38f__p02",
]
BASE_GAME_PREFIX = "gamezone-0022d901-ea58-4a11-b909-fff27f0ee38f"
REPORT_PATH = REPO_ROOT / "tmp" / "may17_local_publish_overwrite_report.json"
MANIFEST_PATH = REPO_ROOT / "tmp" / "may17_local_publish_overwrite_manifest.json"
PUBLIC_ROOT = REPO_ROOT / "games" / "published" / "public"
OBFUSCATED_ROOT = REPO_ROOT / "games" / "published" / "obfuscated"


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def run_command(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=REPO_ROOT, capture_output=True, text=True)


def summarize_metadata(metadata_path: Path) -> dict[str, Any]:
    payload = load_json(metadata_path)
    deploy = payload.get("deploy") if isinstance(payload.get("deploy"), dict) else {}
    identity = payload.get("identity") if isinstance(payload.get("identity"), dict) else {}
    return {
        "metadata_path": str(metadata_path),
        "game_id": payload.get("game_id"),
        "remix_id": payload.get("remix_id"),
        "identity_title": identity.get("title"),
        "screenshots_jpg": payload.get("screenshots_jpg"),
        "normalized_screenshot_sources": deploy.get("normalized_screenshot_sources"),
        "source_output_dir": deploy.get("source_output_dir"),
    }


def summarize_deploy_dir(deploy_dir: Path) -> dict[str, Any]:
    shots_dir = deploy_dir / "screenshots"
    shot_files = []
    if shots_dir.exists():
        shot_files = sorted(
            path.name for path in shots_dir.iterdir() if path.is_file() and not path.name.startswith("._")
        )
    metadata_files = sorted(path for path in deploy_dir.glob("game-obfuscated-*.json") if not path.name.startswith("._"))
    metadata_summary = summarize_metadata(metadata_files[0]) if metadata_files else None
    return {
        "deploy_dir": str(deploy_dir),
        "exists": deploy_dir.exists(),
        "screenshot_files": shot_files,
        "metadata_summary": metadata_summary,
    }


def summarize_matching_catalog_records(path: Path) -> dict[str, Any]:
    payload = load_json(path) if path.exists() else {}
    if not isinstance(payload, dict):
        return {"path": str(path), "matching_keys": {}, "matching_count": 0}
    matching = {
        key: {
            "game_id": value.get("game_id") if isinstance(value, dict) else None,
            "title": value.get("title") if isinstance(value, dict) else None,
            "screenshots_count": len(value.get("screenshots") or []) if isinstance(value, dict) else None,
            "published_path": value.get("published_path") if isinstance(value, dict) else None,
        }
        for key, value in payload.items()
        if BASE_GAME_PREFIX in key
    }
    return {"path": str(path), "matching_keys": matching, "matching_count": len(matching)}


def main() -> None:
    missing_sources = [str(path) for path in SOURCE_DIRS if not path.exists()]
    if missing_sources:
        raise SystemExit(json.dumps({"error": "missing source dirs", "paths": missing_sources}, indent=2))

    manifest_payload = [str(path) for path in SOURCE_DIRS]
    write_json(MANIFEST_PATH, manifest_payload)

    before_public = summarize_matching_catalog_records(PUBLIC_ROOT / "app.json")
    before_obfuscated = summarize_matching_catalog_records(OBFUSCATED_ROOT / "app.json")

    command = [
        sys.executable,
        str(PUBLISH_SCRIPT),
        "--manifest",
        str(MANIFEST_PATH),
        "--report-path",
        str(REPORT_PATH),
        "--overwrite",
        "--refresh-app-artifacts-collection-slug",
        "may17_local_probe",
    ]
    completed = run_command(command)

    result: dict[str, Any] = {
        "timestamp": utc_stamp(),
        "source_dirs": [str(path) for path in SOURCE_DIRS],
        "manifest_path": str(MANIFEST_PATH),
        "report_path": str(REPORT_PATH),
        "command": command,
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "before_public_app": before_public,
        "before_obfuscated_app": before_obfuscated,
    }

    if completed.returncode == 0 and REPORT_PATH.exists():
        report = load_json(REPORT_PATH)
        deployment_results = ((report.get("deployment") or {}).get("results") or []) if isinstance(report, dict) else []
        result["deployment_results"] = deployment_results
        result["deploy_dir_summaries"] = [
            summarize_deploy_dir(Path(item["deploy_dir"]))
            for item in deployment_results
            if isinstance(item, dict) and item.get("deploy_dir")
        ]
        result["after_public_app"] = summarize_matching_catalog_records(PUBLIC_ROOT / "app.json")
        result["after_obfuscated_app"] = summarize_matching_catalog_records(OBFUSCATED_ROOT / "app.json")
        result["after_public_index"] = summarize_matching_catalog_records(PUBLIC_ROOT / "index.json")
        game_ids = [
            str(item.get("game_id"))
            for item in deployment_results
            if isinstance(item, dict) and item.get("game_id")
        ]
        result["proof_flags"] = {
            "all_identity_titles_present": all(
                bool(((summary.get("metadata_summary") or {}).get("identity_title")))
                for summary in result["deploy_dir_summaries"]
            )
            if result.get("deploy_dir_summaries")
            else False,
            "all_deploys_have_packaged_screenshots": all(
                bool(summary.get("screenshot_files")) for summary in result["deploy_dir_summaries"]
            )
            if result.get("deploy_dir_summaries")
            else False,
            "any_game_id_contains_prompt_suffix": any("__p" in game_id for game_id in game_ids),
            "game_ids": game_ids,
        }

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()