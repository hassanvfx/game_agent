#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
TOOL_ROOT = SCRIPT_PATH.parents[1]
REPO_ROOT = TOOL_ROOT.parents[1]

DEFAULT_PUBLIC_ROOT = REPO_ROOT / "games" / "published" / "public"
DEFAULT_OBFUSCATED_ROOT = REPO_ROOT / "games" / "published" / "obfuscated"
DEFAULT_MOBILE_RUNS_ROOT = TOOL_ROOT / "scripts" / "mobile" / "run_artifacts"
MOBILE_VALIDATE_SCRIPT = TOOL_ROOT / "scripts" / "mobile" / "validate_artifact_orchestration.py"

BUNDLE_DIRNAME = "bundle"
APP_NAME = "app.json"

MOBILE_ARTIFACT_NAMES = (
    "home_collections_ids.json",
    "home_filter_manifest.json",
    "editorial_phase3_candidates.json",
    "editorial_layouts.json",
    "taxonomy_search_artifact.json",
    "top_tag_feeds.json",
    "remix_feed.json",
    "tag_registry.json",
    "all_tag_match_counts.json",
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Generate mobile artifacts for public/obfuscated app catalogs and materialize "
            "them into each scope bundle with mobile_ prefixes."
        )
    )
    parser.add_argument("--public-root", default=str(DEFAULT_PUBLIC_ROOT), help="Published public root.")
    parser.add_argument("--obfuscated-root", default=str(DEFAULT_OBFUSCATED_ROOT), help="Published obfuscated root.")
    parser.add_argument(
        "--mobile-runs-root",
        default=str(DEFAULT_MOBILE_RUNS_ROOT),
        help="Root directory used by the mobile validation/generation script.",
    )
    parser.add_argument(
        "--mobile-script",
        default=str(MOBILE_VALIDATE_SCRIPT),
        help="Path to the mobile validation/generation script.",
    )
    parser.add_argument(
        "--run-mobile",
        dest="run_mobile",
        action="store_true",
        help="Run the mobile generator for each scope before materializing outputs (default).",
    )
    parser.add_argument(
        "--no-run-mobile",
        dest="run_mobile",
        action="store_false",
        help="Skip running the mobile generator and materialize from the latest available runs.",
    )
    parser.set_defaults(run_mobile=True)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the materialization plan without copying mobile artifacts into bundle directories.",
    )
    return parser


def run_json_command(command: list[str]) -> dict[str, Any]:
    print(f"[materialize-mobile] command: {' '.join(command)}", flush=True)
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    captured_lines: list[str] = []
    assert process.stdout is not None
    for line in process.stdout:
        print(line, end="")
        captured_lines.append(line)
    returncode = process.wait()
    if returncode != 0:
        raise SystemExit(returncode)
    stdout = "".join(captured_lines).strip()
    if not stdout:
        return {}
    start = stdout.rfind("\n{")
    if start != -1:
        json_text = stdout[start + 1 :]
    elif stdout.startswith("{"):
        json_text = stdout
    else:
        raise SystemExit("Expected JSON object payload from child command.")
    payload = json.loads(json_text)
    if not isinstance(payload, dict):
        raise SystemExit("Expected JSON object payload from child command.")
    return payload


def latest_run_dir(runs_root: Path) -> Path:
    if not runs_root.is_dir():
        raise SystemExit(f"Mobile runs root does not exist or is not a directory: {runs_root}")
    run_dirs = sorted([path for path in runs_root.iterdir() if path.is_dir()])
    if not run_dirs:
        raise SystemExit(f"No mobile run directories found under: {runs_root}")
    return run_dirs[-1]


def ensure_bundle_dir(scope_root: Path) -> Path:
    bundle_dir = scope_root / BUNDLE_DIRNAME
    bundle_dir.mkdir(parents=True, exist_ok=True)
    return bundle_dir


def materialize_scope(
    *,
    scope_name: str,
    scope_root: Path,
    mobile_script: Path,
    mobile_runs_root: Path,
    run_mobile: bool,
    dry_run: bool,
) -> dict[str, Any]:
    print(f"[materialize-mobile] scope={scope_name} start", flush=True)
    source_app_json = scope_root / APP_NAME
    if not source_app_json.is_file():
        raise SystemExit(f"[materialize-mobile] missing source app.json for {scope_name}: {source_app_json}")

    run_payload: dict[str, Any] | None = None
    selected_run_dir: Path

    if run_mobile:
        print(f"[materialize-mobile] scope={scope_name} generating mobile artifacts from {source_app_json}", flush=True)
        run_payload = run_json_command(
            [
                sys.executable,
                str(mobile_script),
                "--input",
                str(source_app_json),
                "--run-root",
                str(mobile_runs_root / scope_name),
            ]
        )
        run_dir_value = str(run_payload.get("run_dir") or "")
        if not run_dir_value:
            raise SystemExit(f"[materialize-mobile] mobile generator did not return run_dir for {scope_name}")
        selected_run_dir = Path(run_dir_value).resolve()
    else:
        print(f"[materialize-mobile] scope={scope_name} using latest existing mobile run", flush=True)
        selected_run_dir = latest_run_dir(mobile_runs_root / scope_name).resolve()

    print(f"[materialize-mobile] scope={scope_name} selected_run_dir={selected_run_dir}", flush=True)
    artifacts_dir = selected_run_dir / "artifacts"
    if not artifacts_dir.is_dir():
        raise SystemExit(f"[materialize-mobile] artifacts dir missing for {scope_name}: {artifacts_dir}")

    bundle_dir = ensure_bundle_dir(scope_root)
    print(f"[materialize-mobile] scope={scope_name} bundle_dir={bundle_dir}", flush=True)
    copies: list[dict[str, str]] = []

    for artifact_name in MOBILE_ARTIFACT_NAMES:
        source_path = artifacts_dir / artifact_name
        if not source_path.is_file():
            raise SystemExit(f"[materialize-mobile] missing mobile artifact for {scope_name}: {source_path}")
        target_name = f"mobile_{artifact_name}"
        target_path = bundle_dir / target_name
        copies.append({"source": str(source_path), "target": str(target_path)})
        if dry_run:
            print(f"[materialize-mobile] scope={scope_name} dry-run copy {source_path} -> {target_path}", flush=True)
        else:
            print(f"[materialize-mobile] scope={scope_name} copy {source_path} -> {target_path}", flush=True)
            shutil.copy2(source_path, target_path)

    print(f"[materialize-mobile] scope={scope_name} done copies={len(copies)}", flush=True)
    return {
        "scope": scope_name,
        "source_app_json": str(source_app_json),
        "run_mobile": bool(run_mobile),
        "dry_run": bool(dry_run),
        "run_dir": str(selected_run_dir),
        "artifacts_dir": str(artifacts_dir),
        "bundle_dir": str(bundle_dir),
        "copies": copies,
        "generator_result": run_payload,
    }


def main() -> None:
    args = build_parser().parse_args()

    public_root = Path(args.public_root).resolve()
    obfuscated_root = Path(args.obfuscated_root).resolve()
    mobile_runs_root = Path(args.mobile_runs_root).resolve()
    mobile_script = Path(args.mobile_script).resolve()

    print("[materialize-mobile] =============================", flush=True)
    print("[materialize-mobile] Materialize mobile artifacts", flush=True)
    print(f"[materialize-mobile] public root: {public_root}", flush=True)
    print(f"[materialize-mobile] obfuscated root: {obfuscated_root}", flush=True)
    print(f"[materialize-mobile] mobile runs root: {mobile_runs_root}", flush=True)
    print(f"[materialize-mobile] mobile script: {mobile_script}", flush=True)
    print(f"[materialize-mobile] run_mobile: {args.run_mobile}", flush=True)
    print(f"[materialize-mobile] dry_run: {args.dry_run}", flush=True)
    print("[materialize-mobile] =============================", flush=True)

    result = {
        "public": materialize_scope(
            scope_name="public",
            scope_root=public_root,
            mobile_script=mobile_script,
            mobile_runs_root=mobile_runs_root,
            run_mobile=bool(args.run_mobile),
            dry_run=bool(args.dry_run),
        ),
        "obfuscated": materialize_scope(
            scope_name="obfuscated",
            scope_root=obfuscated_root,
            mobile_script=mobile_script,
            mobile_runs_root=mobile_runs_root,
            run_mobile=bool(args.run_mobile),
            dry_run=bool(args.dry_run),
        ),
        "migration_notes": [
            "Canonical current artifact location is migrating toward <scope>/bundle/.",
            "Downstream sibling consumers such as tool_app_matcher_v2 and game_matcher_v2 may require follow-up path updates.",
        ],
    }

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()