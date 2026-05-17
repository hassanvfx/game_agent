#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCRIPT_PATH = Path(__file__).resolve()
TOOL_ROOT = SCRIPT_PATH.parents[1]
REPO_ROOT = TOOL_ROOT.parents[1]

DEFAULT_RUNS_ROOT = REPO_ROOT / "games" / "published" / "runs"
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
    parser.add_argument(
        "--runs",
        nargs="+",
        help="Optional explicit run directories (e.g. games/published/runs/<run_id>). If omitted, auto-discover run_* dirs under --runs-root.",
    )
    parser.add_argument(
        "--runs-root",
        default=str(DEFAULT_RUNS_ROOT),
        help="Runs root used for automatic run discovery when --runs is omitted.",
    )
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


def discover_run_dirs(runs_root: Path) -> list[Path]:
    if not runs_root.exists() or not runs_root.is_dir():
        raise SystemExit(f"Runs root does not exist or is not a directory: {runs_root}")

    run_dirs = sorted(
        [path for path in runs_root.iterdir() if path.is_dir() and path.name.startswith("run_")],
        key=lambda path: path.name,
    )
    if not run_dirs:
        raise SystemExit(f"No run_* directories found under runs root: {runs_root}")
    return run_dirs


def resolve_run_dirs(explicit_runs: list[str] | None, runs_root: Path) -> tuple[list[Path], str]:
    if explicit_runs:
        return [Path(item).resolve() for item in explicit_runs], "explicit"
    return discover_run_dirs(runs_root), "auto-discovered"


def _safe_join(root: Path, relative_path: str) -> Path | None:
    candidate = (root / relative_path).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError:
        return None
    return candidate


def candidate_index_paths(record: dict[str, Any], *, scope_root: Path, scope_name: str) -> list[Path]:
    fields: list[str] = []
    if scope_name == "public":
        fields.extend(["public_index_html", "index_html"])
    else:
        fields.extend(["obfuscated_index_html", "public_index_html", "index_html"])

    candidates: list[Path] = []
    seen: set[Path] = set()

    for field in fields:
        raw_value = record.get(field)
        if not isinstance(raw_value, str) or not raw_value.strip():
            continue
        candidate = _safe_join(scope_root, raw_value.strip())
        if candidate is not None and candidate not in seen:
            candidates.append(candidate)
            seen.add(candidate)

    published_path = record.get("published_path")
    if isinstance(published_path, str) and published_path.strip():
        fallback = _safe_join(scope_root, str(Path(published_path.strip()) / "index.html"))
        if fallback is not None and fallback not in seen:
            candidates.append(fallback)
            seen.add(fallback)

    return candidates


def sanitize_merged_payload(
    merged: dict[str, Any],
    *,
    scope_root: Path,
    scope_name: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    sanitized: dict[str, Any] = {}
    removed_details: list[dict[str, Any]] = []

    for key, value in merged.items():
        if not isinstance(key, str) or not key:
            continue
        if not isinstance(value, dict):
            removed_details.append({"key": key, "reason": "record_not_object"})
            continue

        candidates = candidate_index_paths(value, scope_root=scope_root, scope_name=scope_name)
        if not candidates:
            removed_details.append({"key": key, "reason": "no_index_candidate_paths"})
            continue

        if any(candidate.is_file() for candidate in candidates):
            sanitized[key] = value
            continue

        removed_details.append(
            {
                "key": key,
                "reason": "missing_index_html",
                "candidate_paths": [str(path) for path in candidates],
            }
        )

    stats = {
        "records_before": len(merged),
        "records_after": len(sanitized),
        "records_removed": len(removed_details),
        "removed_samples": removed_details[:10],
    }
    return sanitized, stats


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
    runs_root = Path(args.runs_root).resolve()
    run_dirs, run_source = resolve_run_dirs(args.runs, runs_root)
    public_root = Path(args.public_root).resolve()
    obfuscated_root = Path(args.obfuscated_root).resolve()

    print("[materialize] =============================", flush=True)
    print("[materialize] Materialize root artifact view", flush=True)
    print(f"[materialize] run source: {run_source}", flush=True)
    print(f"[materialize] runs root: {runs_root}", flush=True)
    print(f"[materialize] precedence: {args.precedence}", flush=True)
    print(f"[materialize] dry_run: {args.dry_run}", flush=True)
    print(f"[materialize] run count: {len(run_dirs)}", flush=True)
    for idx, run_dir in enumerate(run_dirs, start=1):
        print(f"[materialize]   run[{idx}]: {run_dir}", flush=True)
    print("[materialize] =============================", flush=True)

    result: dict[str, Any] = {
        "run_source": run_source,
        "runs_root": str(runs_root),
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
            sanitized, sanitize_stats = sanitize_merged_payload(
                merged,
                scope_root=scope_root,
                scope_name=scope_name,
            )
            output_path = scope_root / artifact_name
            if not args.dry_run:
                write_json(output_path, sanitized)
                print(
                    f"[materialize]     wrote={output_path} records={sanitize_stats['records_after']} removed={sanitize_stats['records_removed']}",
                    flush=True,
                )
            else:
                print(
                    f"[materialize]     dry-run would write={output_path} records={sanitize_stats['records_after']} removed={sanitize_stats['records_removed']}",
                    flush=True,
                )
            scope_report[artifact_name] = {
                "output": str(output_path),
                "sources": [str(path) for path in artifact_paths],
                "merged_records": stats["records_written"],
                "records": sanitize_stats["records_after"],
                "records_removed": sanitize_stats["records_removed"],
                "removed_samples": sanitize_stats["removed_samples"],
            }
        result[scope_name] = scope_report

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
