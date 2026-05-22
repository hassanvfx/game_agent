from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path("/Users/hassan/repos/game_agent")
PUBLISH_SCRIPT = REPO_ROOT / "tools/game_publish_pipeline/scripts/publish_games.py"
OUTPUT_PARENT = Path("/Volumes/HDD2026/output-May17th/output")
RUN_SOURCE_ROOT = Path("/Volumes/HDD2026/output-May17th/run_game_remixer_20260517T132133Z/output")
SOURCE_DIRS = [
    RUN_SOURCE_ROOT / "gamezone-0022d901-ea58-4a11-b909-fff27f0ee38f__p01",
    RUN_SOURCE_ROOT / "gamezone-0022d901-ea58-4a11-b909-fff27f0ee38f__p02",
]


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


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
        "screenshots_png": payload.get("screenshots_png"),
        "screenshots_jpg": payload.get("screenshots_jpg"),
        "normalized_screenshot_sources": deploy.get("normalized_screenshot_sources"),
        "source_output_dir": deploy.get("source_output_dir"),
    }


def summarize_deploy_dir(deploy_dir: Path) -> dict[str, Any]:
    shots_dir = deploy_dir / "screenshots"
    shot_files = []
    if shots_dir.exists():
        shot_files = sorted(path.name for path in shots_dir.iterdir() if path.is_file())
    metadata_files = sorted(path for path in deploy_dir.glob("game-obfuscated-*.json"))
    metadata_summary = summarize_metadata(metadata_files[0]) if metadata_files else None
    return {
        "deploy_dir": str(deploy_dir),
        "exists": deploy_dir.exists(),
        "top_level_items": sorted(path.name for path in deploy_dir.iterdir()) if deploy_dir.exists() else [],
        "screenshot_files": shot_files,
        "metadata_summary": metadata_summary,
    }


def summarize_catalog(path: Path) -> dict[str, Any]:
    payload = load_json(path)
    sample_keys = sorted(payload.keys())[:10] if isinstance(payload, dict) else []
    sample_records = {}
    if isinstance(payload, dict):
        for key in sample_keys[:4]:
            record = payload.get(key)
            if isinstance(record, dict):
                sample_records[key] = {
                    "game_id": record.get("game_id"),
                    "title": record.get("title"),
                    "screenshots_count": len(record.get("screenshots") or []),
                    "published_path": record.get("published_path"),
                }
    return {
        "path": str(path),
        "entry_count": len(payload) if isinstance(payload, dict) else None,
        "sample_records": sample_records,
    }


def main() -> None:
    missing_sources = [str(path) for path in SOURCE_DIRS if not path.exists()]
    if missing_sources:
        raise SystemExit(json.dumps({"error": "missing source dirs", "paths": missing_sources}, indent=2))

    probe_root = OUTPUT_PARENT / f"publish_probe_{utc_stamp()}"
    public_root = probe_root / "public"
    obfuscated_root = probe_root / "obfuscated"
    runs_root = probe_root / "runs"
    generated_root = probe_root / "generated"
    manifest_path = probe_root / "manifest.json"
    pipeline_report_path = probe_root / "pipeline_report.json"

    manifest_payload = [str(path) for path in SOURCE_DIRS]
    write_json(manifest_path, manifest_payload)

    command = [
        sys.executable,
        str(PUBLISH_SCRIPT),
        "--manifest",
        str(manifest_path),
        "--published-public-root",
        str(public_root),
        "--published-obfuscated-root",
        str(obfuscated_root),
        "--published-runs-root",
        str(runs_root),
        "--report-path",
        str(pipeline_report_path),
        "--refresh-app-artifacts-collection-slug",
        "may17_probe",
    ]

    completed = run_command(command)

    result: dict[str, Any] = {
        "probe_root": str(probe_root),
        "manifest_path": str(manifest_path),
        "source_dirs": [str(path) for path in SOURCE_DIRS],
        "command": command,
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }

    if completed.returncode == 0 and pipeline_report_path.exists():
        report = load_json(pipeline_report_path)
        deployment_results = ((report.get("deployment") or {}).get("results") or []) if isinstance(report, dict) else []
        result["pipeline_report_path"] = str(pipeline_report_path)
        result["deployment_results"] = deployment_results
        result["deploy_dir_summaries"] = [
            summarize_deploy_dir(Path(item["deploy_dir"]))
            for item in deployment_results
            if isinstance(item, dict) and item.get("deploy_dir")
        ]

        public_app = public_root / "app.json"
        obfuscated_app = obfuscated_root / "app.json"
        public_index = public_root / "index.json"
        result["public_app_summary"] = summarize_catalog(public_app) if public_app.exists() else None
        result["obfuscated_app_summary"] = summarize_catalog(obfuscated_app) if obfuscated_app.exists() else None
        result["public_index_summary"] = summarize_catalog(public_index) if public_index.exists() else None

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
            if result["deploy_dir_summaries"]
            else False,
            "all_deploys_have_packaged_screenshots": all(
                bool(summary.get("screenshot_files")) for summary in result["deploy_dir_summaries"]
            )
            if result["deploy_dir_summaries"]
            else False,
            "any_game_id_contains_prompt_suffix": any("__p" in game_id for game_id in game_ids),
            "game_ids": game_ids,
        }

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()