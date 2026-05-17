#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCRIPT_PATH = Path(__file__).resolve()
TOOL_ROOT = SCRIPT_PATH.parents[1]
REPO_ROOT = TOOL_ROOT.parents[1]

DEFAULT_PUBLIC_ROOT = REPO_ROOT / "games" / "published" / "public"
DEFAULT_OBFUSCATED_ROOT = REPO_ROOT / "games" / "published" / "obfuscated"
DEFAULT_RUNS_ROOT = REPO_ROOT / "games" / "published" / "runs"

INDEX_NAME = "index.json"
APP_TAGS_NAME = "app_tags.json"
APP_NAME = "app.json"
MATERIALIZE_SCRIPT = TOOL_ROOT / "scripts" / "materialize_artifact_view.py"
GENERATE_ANNOTATOR_ENTRY_SCRIPT = TOOL_ROOT / "scripts" / "generate_annotator_entry.py"
ANNOTATOR_ENTRY_NAME = "annotator.html"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Refresh persistent public/obfuscated app artifacts after publishing."
    )
    parser.add_argument("--manifest", required=True, help="Manifest selecting published entries for the collection.")
    parser.add_argument("--collection-slug", default="vatsal_app_alpha", help="Collection slug prefix.")
    parser.add_argument("--public-root", default=str(DEFAULT_PUBLIC_ROOT), help="Published public root.")
    parser.add_argument("--obfuscated-root", default=str(DEFAULT_OBFUSCATED_ROOT), help="Published obfuscated root.")
    parser.add_argument(
        "--generated-output-root",
        default=str(REPO_ROOT / "tmp" / "generated_collections" / "vatsal_app_alpha"),
        help="Temporary generated output root for public catalog generation.",
    )
    parser.add_argument(
        "--approved",
        choices=("true", "false"),
        help="Optionally set approved on every generated app.json record.",
    )
    parser.add_argument(
        "--runs-root",
        default=str(DEFAULT_RUNS_ROOT),
        help="Persistent root for per-run artifact snapshots.",
    )
    parser.add_argument(
        "--run-id",
        help="Optional explicit run id for runs/<run_id>. Defaults to UTC timestamp.",
    )
    parser.add_argument(
        "--reconcile-mode",
        choices=("replace", "merge"),
        default="replace",
        help=(
            "How to reconcile generated app artifacts with existing root artifacts. "
            "'replace' keeps only generated keys (default), 'merge' preserves historical keys and overwrites collisions."
        ),
    )

    materialize_group = parser.add_mutually_exclusive_group()
    materialize_group.add_argument(
        "--materialize-root",
        dest="materialize_root",
        action="store_true",
        help="After writing run-scoped artifacts, invoke materialize_artifact_view.py to refresh root view artifacts (default: enabled).",
    )
    materialize_group.add_argument(
        "--no-materialize-root",
        dest="materialize_root",
        action="store_false",
        help="Skip invoking materialize_artifact_view.py after writing run-scoped artifacts.",
    )
    parser.set_defaults(materialize_root=True)
    return parser


def run_command(command: list[str]) -> None:
    print(f"[refresh] command: {' '.join(command)}", flush=True)
    result = subprocess.run(command, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def run_json_command(command: list[str]) -> dict[str, Any]:
    print(f"[refresh] command: {' '.join(command)}", flush=True)
    result = subprocess.run(command, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    if result.returncode != 0:
        raise SystemExit(result.returncode)
    stdout = result.stdout.strip()
    if not stdout:
        return {}
    payload = json.loads(stdout)
    if not isinstance(payload, dict):
        raise SystemExit("Expected JSON object payload from child command.")
    return payload


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_json_object(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    payload = load_json(path)
    if not isinstance(payload, dict):
        raise SystemExit(f"Expected JSON object at {path}, found {type(payload).__name__}.")
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def default_run_id() -> str:
    return datetime.now(timezone.utc).strftime("run_%Y%m%dT%H%M%SZ")


def merge_records(existing: dict[str, Any], updates: dict[str, Any]) -> dict[str, Any]:
    merged = dict(existing)
    for composite_key, record in updates.items():
        if isinstance(composite_key, str) and composite_key and isinstance(record, dict):
            merged[composite_key] = record
    return merged


def reconcile_artifact(existing_path: Path, generated_path: Path, reconcile_mode: str) -> dict[str, Any]:
    generated_payload = load_json_object(generated_path)
    if reconcile_mode == "replace":
        write_json(existing_path, generated_payload)
        return generated_payload

    existing_payload = load_json_object(existing_path)
    merged_payload = merge_records(existing_payload, generated_payload)
    write_json(existing_path, merged_payload)
    return merged_payload


def write_run_snapshot(run_dir: Path, public_index: dict[str, Any], public_app_tags: dict[str, Any], public_app: dict[str, Any]) -> tuple[Path, Path, Path]:
    run_public_dir = run_dir / "public"
    public_index_out = run_public_dir / INDEX_NAME
    public_app_tags_out = run_public_dir / APP_TAGS_NAME
    public_app_out = run_public_dir / APP_NAME
    write_json(public_index_out, public_index)
    write_json(public_app_tags_out, public_app_tags)
    write_json(public_app_out, public_app)
    print(f"[refresh] wrote run public snapshot: {run_public_dir}", flush=True)
    return public_index_out, public_app_tags_out, public_app_out


def build_public_catalog(
    manifest_path: Path,
    public_root: Path,
    generated_output_root: Path,
    public_index_path: Path,
    public_app_tags_path: Path,
    public_app_path: Path,
    approved: str | None,
    reconcile_mode: str,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    if generated_output_root.exists():
        shutil.rmtree(generated_output_root)
    generated_output_root.mkdir(parents=True, exist_ok=True)

    command = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "generate_published_app_metadata.py"),
        "--manifest",
        str(manifest_path),
        "--published-root",
        str(public_root),
        "--output-root",
        str(generated_output_root),
        "--strict",
    ]
    if approved is not None:
        command.extend(["--approved", approved])
    run_command(command)

    public_index = reconcile_artifact(public_index_path, generated_output_root / INDEX_NAME, reconcile_mode)
    public_app_tags = reconcile_artifact(public_app_tags_path, generated_output_root / APP_TAGS_NAME, reconcile_mode)
    public_app = reconcile_artifact(public_app_path, generated_output_root / APP_NAME, reconcile_mode)
    return public_index, public_app_tags, public_app


def transform_obfuscated_payload(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    transformed: dict[str, dict[str, Any]] = {}
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


def build_obfuscated_catalog(
    obfuscated_root: Path,
    public_index: dict[str, Any],
    public_app_tags: dict[str, Any],
    public_app: dict[str, Any],
    reconcile_mode: str,
) -> tuple[Path, Path, Path]:
    obfuscated_index_path = obfuscated_root / INDEX_NAME
    obfuscated_app_tags_path = obfuscated_root / APP_TAGS_NAME
    obfuscated_app_path = obfuscated_root / APP_NAME

    transformed_index = transform_obfuscated_payload(public_index)
    transformed_app_tags = transform_obfuscated_payload(public_app_tags)
    transformed_app = transform_obfuscated_payload(public_app)

    if reconcile_mode == "replace":
        write_json(obfuscated_index_path, transformed_index)
        write_json(obfuscated_app_tags_path, transformed_app_tags)
        write_json(obfuscated_app_path, transformed_app)
    else:
        write_json(
            obfuscated_index_path,
            merge_records(load_json_object(obfuscated_index_path), transformed_index),
        )
        write_json(
            obfuscated_app_tags_path,
            merge_records(load_json_object(obfuscated_app_tags_path), transformed_app_tags),
        )
        write_json(
            obfuscated_app_path,
            merge_records(load_json_object(obfuscated_app_path), transformed_app),
        )
    return obfuscated_index_path, obfuscated_app_tags_path, obfuscated_app_path


def write_obfuscated_run_snapshot(run_dir: Path, obfuscated_index: dict[str, Any], obfuscated_app_tags: dict[str, Any], obfuscated_app: dict[str, Any]) -> tuple[Path, Path, Path]:
    run_obfuscated_dir = run_dir / "obfuscated"
    obfuscated_index_out = run_obfuscated_dir / INDEX_NAME
    obfuscated_app_tags_out = run_obfuscated_dir / APP_TAGS_NAME
    obfuscated_app_out = run_obfuscated_dir / APP_NAME
    write_json(obfuscated_index_out, obfuscated_index)
    write_json(obfuscated_app_tags_out, obfuscated_app_tags)
    write_json(obfuscated_app_out, obfuscated_app)
    print(f"[refresh] wrote run obfuscated snapshot: {run_obfuscated_dir}", flush=True)
    return obfuscated_index_out, obfuscated_app_tags_out, obfuscated_app_out


def generate_dashboard_entries(
    *,
    public_root: Path,
    obfuscated_root: Path,
    entry_name: str = ANNOTATOR_ENTRY_NAME,
    app_json_name: str = APP_NAME,
    play_root: str = "",
) -> dict[str, Any]:
    command = [
        sys.executable,
        str(GENERATE_ANNOTATOR_ENTRY_SCRIPT),
        "--target",
        "both",
        "--public-root",
        str(public_root),
        "--obfuscated-root",
        str(obfuscated_root),
        "--entry-name",
        str(entry_name),
        "--app-json-name",
        str(app_json_name),
        "--play-root",
        str(play_root),
    ]
    return run_json_command(command)


def main() -> None:
    args = build_parser().parse_args()

    manifest_path = Path(args.manifest).resolve()
    public_root = Path(args.public_root).resolve()
    obfuscated_root = Path(args.obfuscated_root).resolve()
    generated_output_root = Path(args.generated_output_root).resolve()
    runs_root = Path(args.runs_root).resolve()
    run_id = args.run_id or default_run_id()
    run_dir = runs_root / run_id

    print("[refresh] =============================", flush=True)
    print("[refresh] Refresh app artifacts", flush=True)
    print(f"[refresh] manifest: {manifest_path}", flush=True)
    print(f"[refresh] public root: {public_root}", flush=True)
    print(f"[refresh] obfuscated root: {obfuscated_root}", flush=True)
    print(f"[refresh] runs root: {runs_root}", flush=True)
    print(f"[refresh] run id: {run_id}", flush=True)
    print(f"[refresh] run dir: {run_dir}", flush=True)
    print(f"[refresh] reconcile mode: {args.reconcile_mode}", flush=True)
    print("[refresh] =============================", flush=True)

    public_index_path = public_root / INDEX_NAME
    public_app_tags_path = public_root / APP_TAGS_NAME
    public_app_path = public_root / APP_NAME

    public_index, public_app_tags, public_app = build_public_catalog(
        manifest_path,
        public_root,
        generated_output_root,
        public_index_path,
        public_app_tags_path,
        public_app_path,
        args.approved,
        str(args.reconcile_mode),
    )
    obfuscated_index_path, obfuscated_app_tags_path, obfuscated_app_path = build_obfuscated_catalog(
        obfuscated_root,
        public_index,
        public_app_tags,
        public_app,
        str(args.reconcile_mode),
    )

    print("[refresh] [run snapshot] writing public run artifacts...", flush=True)
    run_public_index, run_public_app_tags, run_public_app = write_run_snapshot(
        run_dir,
        public_index,
        public_app_tags,
        public_app,
    )

    print("[refresh] [run snapshot] writing obfuscated run artifacts...", flush=True)
    obfuscated_index_payload = load_json_object(obfuscated_index_path)
    obfuscated_app_tags_payload = load_json_object(obfuscated_app_tags_path)
    obfuscated_app_payload = load_json_object(obfuscated_app_path)
    run_obfuscated_index, run_obfuscated_app_tags, run_obfuscated_app = write_obfuscated_run_snapshot(
        run_dir,
        obfuscated_index_payload,
        obfuscated_app_tags_payload,
        obfuscated_app_payload,
    )

    print("[refresh] [run dashboard] generating run-scoped annotator dashboards...", flush=True)
    run_dashboard_result = generate_dashboard_entries(
        public_root=run_dir / "public",
        obfuscated_root=run_dir / "obfuscated",
    )

    materialize_result: dict[str, Any] | None = None
    if args.materialize_root:
        print("[refresh] [materialize] invoking materialize_artifact_view.py...", flush=True)
        materialize_command = [
            sys.executable,
            str(MATERIALIZE_SCRIPT),
            "--runs-root",
            str(runs_root),
            "--public-root",
            str(public_root),
            "--obfuscated-root",
            str(obfuscated_root),
            "--precedence",
            "latest-wins",
        ]
        run_command(materialize_command)
        materialize_result = {
            "script": str(MATERIALIZE_SCRIPT),
            "runs_root": str(runs_root),
            "run_source": "auto-discovered",
            "precedence": "latest-wins",
        }

    print("[refresh] [root dashboard] generating root annotator dashboards...", flush=True)
    root_dashboard_result = generate_dashboard_entries(
        public_root=public_root,
        obfuscated_root=obfuscated_root,
    )

    print(
        json.dumps(
            {
                "manifest": str(manifest_path),
                "collection_slug": str(args.collection_slug),
                "public_index": str(public_index_path),
                "public_app_tags": str(public_app_tags_path),
                "public_app": str(public_app_path),
                "approved": args.approved,
                "reconcile_mode": str(args.reconcile_mode),
                "obfuscated_index": str(obfuscated_index_path),
                "obfuscated_app_tags": str(obfuscated_app_tags_path),
                "obfuscated_app": str(obfuscated_app_path),
                "run_id": run_id,
                "run_dir": str(run_dir),
                "run_public_index": str(run_public_index),
                "run_public_app_tags": str(run_public_app_tags),
                "run_public_app": str(run_public_app),
                "run_obfuscated_index": str(run_obfuscated_index),
                "run_obfuscated_app_tags": str(run_obfuscated_app_tags),
                "run_obfuscated_app": str(run_obfuscated_app),
                "run_dashboards": run_dashboard_result,
                "materialize_root": bool(args.materialize_root),
                "materialize": materialize_result,
                "root_dashboards": root_dashboard_result,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()