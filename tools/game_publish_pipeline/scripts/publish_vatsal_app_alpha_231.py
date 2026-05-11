#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve()
TOOL_ROOT = SCRIPT_PATH.parents[1]
REPO_ROOT = TOOL_ROOT.parents[1]

RUN_TOP107_SCRIPT = REPO_ROOT / "tmp" / "run_top107_legacy_deploy_real.py"
RUN_124_SCRIPT = REPO_ROOT / "tmp" / "run_124_real_deploy.py"
REFRESH_APP_ARTIFACTS_SCRIPT = TOOL_ROOT / "scripts" / "refresh_app_artifacts.py"
DEFAULT_COLLECTION_MANIFEST = REPO_ROOT / "tmp" / "retry_manifests" / "vatsal_app_alpha_231_manifest.json"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Canonical 231-entry publish + refresh entrypoint for Vatsal App Alpha."
    )
    parser.add_argument(
        "--collection-manifest",
        default=str(DEFAULT_COLLECTION_MANIFEST),
        help="Manifest selecting the 231 published entries for app artifact refresh.",
    )
    parser.add_argument(
        "--collection-slug",
        default="vatsal_app_alpha",
        help="Collection slug for public/obfuscated app artifacts.",
    )
    return parser


def run_command(command: list[str]) -> dict:
    result = subprocess.run(command, capture_output=True, text=True)
    payload = {
        "command": command,
        "returncode": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }
    if result.stdout.strip():
        try:
            payload["parsed"] = json.loads(result.stdout)
        except json.JSONDecodeError:
            payload["parsed"] = None
    else:
        payload["parsed"] = None
    if result.returncode != 0:
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        raise SystemExit(result.returncode)
    return payload


def main() -> None:
    args = build_parser().parse_args()
    collection_manifest = Path(args.collection_manifest).resolve()

    top107_result = run_command([sys.executable, str(RUN_TOP107_SCRIPT)])
    run124_result = run_command([sys.executable, str(RUN_124_SCRIPT)])
    refresh_result = run_command(
        [
            sys.executable,
            str(REFRESH_APP_ARTIFACTS_SCRIPT),
            "--manifest",
            str(collection_manifest),
            "--collection-slug",
            str(args.collection_slug),
        ]
    )

    print(
        json.dumps(
            {
                "collection_manifest": str(collection_manifest),
                "collection_slug": str(args.collection_slug),
                "top107_deploy": top107_result.get("parsed"),
                "run124_deploy": run124_result.get("parsed"),
                "app_artifacts_refresh": refresh_result.get("parsed"),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()