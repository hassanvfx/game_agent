#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCRIPT_PATH = Path(__file__).resolve()
TOOL_ROOT = SCRIPT_PATH.parents[1]
REPO_ROOT = TOOL_ROOT.parents[1]

DEFAULT_PUBLIC_ROOT = REPO_ROOT / "games" / "published" / "public"
DEFAULT_OBFUSCATED_ROOT = REPO_ROOT / "games" / "published" / "obfuscated"

INDEX_NAME = "index.json"
APP_TAGS_NAME = "app_tags.json"
APP_NAME = "app.json"
ARTIFACT_NAMES = (INDEX_NAME, APP_TAGS_NAME, APP_NAME)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Materialize root published artifact view from one or more run-scoped artifact snapshots."
    )
    parser.add_argument("--runs", nargs="+", required=True, help="Run directories (e.g. games/published/runs/<run_id>).")
    parser.add_argument("--public-root", default=str(DEFAULT_PUBLIC_ROOT), help="Published public root to materialize.")
    parser.add_argument("--obfuscated-root", default=str(DEFAULT_OBFUSCATED_ROOT), help="Published obfuscated root to materialize.")
    parser.add_argument(
        "--precedence",
        choices=("latest-wins", "first-wins"),
        default="latest-wins",
        help="Merge policy when the same composite key appears across runs.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print merge plan without writing files.")
    return parser


def load_json_object(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SystemExit(f"Expected JSON object at {path}, found {type(payload).__name__}")
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def merge_payloads(paths: list[Path], precedence: str) -> tuple[dict[str, Any], dict[str, int]]:
    merged: dict[str, Any] = {}
    stats = {"sources": 0, "records_seen": 0, "records_written": 0}
    iteration = paths if precedence == "first-wins" else list(paths)
    for source_path in iteration:
        payload = load_json_object(source_path)
        stats["sources"] += 1
        for key, value in payload.items():
            if not isinstance(key, str) or not key:
                continue
            if precedence == "first-wins" and key in merged:
                continue
            merged[key] = value
            stats["records_seen"] += 1
    stats["records_written"] = len(merged)
    return merged, stats


def main() -> None:
    args = build_parser().parse_args()
    run_dirs = [Path(item).resolve() for item in args.runs]
    public_root = Path(args.public_root).resolve()
    obfuscated_root = Path(args.obfuscated_root).resolve()

    print("[materialize] =============================", flush=True)
    print("[materialize] Materialize root artifact view", flush=True)
    print(f"[materialize] precedence: {args.precedence}", flush=True)
    print(f"[materialize] dry_run: {args.dry_run}", flush=True)
    print(f"[materialize] run count: {len(run_dirs)}", flush=True)
    for idx, run_dir in enumerate(run_dirs, start=1):
        print(f"[materialize]   run[{idx}]: {run_dir}", flush=True)
    print("[materialize] =============================", flush=True)

    result: dict[str, Any] = {
        "precedence": args.precedence,
        "dry_run": bool(args.dry_run),
        "runs": [str(path) for path in run_dirs],
        "public": {},
        "obfuscated": {},
    }

    for scope_name, scope_root in (("public", public_root), ("obfuscated", obfuscated_root)):
        print(f"[materialize] scope={scope_name} target_root={scope_root}", flush=True)
        scope_report: dict[str, Any] = {}
        for artifact_name in ARTIFACT_NAMES:
            artifact_paths = [run_dir / scope_name / artifact_name for run_dir in run_dirs]
            print(f"[materialize]   artifact={artifact_name}", flush=True)
            for artifact_path in artifact_paths:
                print(f"[materialize]     source={artifact_path}", flush=True)
            merged, stats = merge_payloads(artifact_paths, args.precedence)
            output_path = scope_root / artifact_name
            if not args.dry_run:
                write_json(output_path, merged)
                print(
                    f"[materialize]     wrote={output_path} records={stats['records_written']}",
                    flush=True,
                )
            else:
                print(
                    f"[materialize]     dry-run would write={output_path} records={stats['records_written']}",
                    flush=True,
                )
            scope_report[artifact_name] = {
                "output": str(output_path),
                "sources": [str(path) for path in artifact_paths],
                "records": stats["records_written"],
            }
        result[scope_name] = scope_report

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
