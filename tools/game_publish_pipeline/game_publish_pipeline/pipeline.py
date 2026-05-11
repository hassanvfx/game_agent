from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

TOOL_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = TOOL_ROOT.parents[1]
GAMES_ROOT = REPO_ROOT / "games"
RAW_ROOT = GAMES_ROOT / "raw"
PUBLISHED_PUBLIC_ROOT = GAMES_ROOT / "published" / "public"
PUBLISHED_OBFUSCATED_ROOT = GAMES_ROOT / "published" / "obfuscated"
OBFUSCATOR_ROOT = REPO_ROOT / "tools" / "game_obfuscator"
DEPLOY_SCRIPT = REPO_ROOT / "tools" / "game_deploy" / "scripts" / "deploy_games.py"
REFRESH_APP_ARTIFACTS_SCRIPT = REPO_ROOT / "tools" / "game_publish_pipeline" / "scripts" / "refresh_app_artifacts.py"
VALIDATE_PUBLISHED_OUTPUTS_SCRIPT = REPO_ROOT / "tools" / "game_publish_pipeline" / "scripts" / "validate_published_outputs.py"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def run_command(command: list[str]) -> dict[str, Any]:
    completed = subprocess.run(command, capture_output=True, text=True)
    stdout = completed.stdout.strip()
    stderr = completed.stderr.strip()
    payload = None
    if stdout:
        try:
            payload = json.loads(stdout)
        except json.JSONDecodeError:
            payload = None
    if completed.returncode != 0:
        raise RuntimeError(stderr or stdout or f"Command failed: {' '.join(command)}")
    return {
        "command": command,
        "stdout": stdout,
        "stderr": stderr,
        "payload": payload,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Stage refactor outputs into raw remix folders, deploy public bundles, then obfuscate them."
    )
    parser.add_argument("--inputs", nargs="+", help="Refactor output game directories.")
    parser.add_argument("--manifest", help="Optional JSON array of refactor output directories.")
    parser.add_argument(
        "--raw-root",
        default=str(RAW_ROOT),
        help="Raw remix staging root. Defaults to games/raw.",
    )
    parser.add_argument(
        "--published-public-root",
        default=str(PUBLISHED_PUBLIC_ROOT),
        help="Published public root. Defaults to games/published/public.",
    )
    parser.add_argument(
        "--published-obfuscated-root",
        default=str(PUBLISHED_OBFUSCATED_ROOT),
        help="Published obfuscated root. Defaults to games/published/obfuscated.",
    )
    parser.add_argument("--report-path", help="Optional explicit final pipeline report path.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing raw remix staging folders.")
    parser.add_argument("--dry-run", action="store_true", help="Prepare and print the plan without running subprocesses.")
    parser.add_argument("--refresh-app-artifacts-manifest", help="Optional manifest used to refresh annotator-facing app artifacts after publish.")
    parser.add_argument("--refresh-app-artifacts-collection-slug", default="vatsal_app_alpha", help="Collection slug for refreshed app artifacts.")
    parser.add_argument("--validate-published-manifest", help="Optional manifest used by the post-publish integrity validator.")
    parser.add_argument(
        "--validate-published-collection-slug",
        default="vatsal_app_alpha",
        help="Collection slug for post-publish integrity validation artifacts.",
    )
    parser.add_argument(
        "--validate-published-annotator-html-name",
        default="565a0bf4-5160-47b8-a905-2f4362475cdf-annotator.html",
        help="Annotator/dashboard file expected by the post-publish integrity validator.",
    )
    parser.add_argument(
        "--validate-published-strict",
        action="store_true",
        help="Fail the pipeline if the post-publish integrity validator reports any required failures.",
    )
    return parser


def resolve_source_inputs(args: argparse.Namespace) -> list[Path]:
    values: list[str] = []
    if args.inputs:
        values.extend(args.inputs)
    if args.manifest:
        payload = load_json(Path(args.manifest))
        if not isinstance(payload, list):
            raise ValueError("Manifest must be a JSON array")
        for item in payload:
            if isinstance(item, str):
                values.append(item)
            elif isinstance(item, dict):
                source = item.get("source") or item.get("path") or item.get("output_dir")
                if not source:
                    raise ValueError("Manifest objects must include source, path, or output_dir")
                values.append(str(source))
            else:
                raise ValueError("Manifest entries must be strings or objects")
    if not values:
        raise ValueError("Provide --inputs or --manifest")
    return [Path(value).resolve() for value in values]


def infer_game_id(source_dir: Path) -> str:
    if source_dir.name.startswith("gamezone-"):
        return source_dir.name
    for candidate in [source_dir, *source_dir.parents[:4]]:
        if candidate.name.startswith("gamezone-"):
            return candidate.name
    raise ValueError(f"Unable to infer game_id from {source_dir}")


def iter_files(root: Path) -> list[Path]:
    return [path for path in sorted(root.rglob("*")) if path.is_file()]


def sha256_for_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def compute_folder_content_hash(source_dir: Path) -> str:
    digest = hashlib.sha256()
    for path in iter_files(source_dir):
        digest.update(path.relative_to(source_dir).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(sha256_for_file(path).encode("utf-8"))
        digest.update(b"\0")
    return digest.hexdigest()[:32]


def build_publish_input(source_dir: Path) -> dict[str, Any]:
    game_id = infer_game_id(source_dir)
    remix_hash = compute_folder_content_hash(source_dir)
    return {
        "source_input": str(source_dir),
        "game_id": game_id,
        "remix_hash": remix_hash,
        "publish_source_dir": str(source_dir),
    }


def write_temp_manifest(prefix: str, payload: Any) -> Path:
    handle = tempfile.NamedTemporaryFile(prefix=prefix, suffix=".json", delete=False)
    path = Path(handle.name)
    handle.close()
    write_json(path, payload)
    return path


def build_deploy_manifest(staged_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{"source": item["publish_source_dir"]} for item in staged_items]


def build_obfuscator_manifest_from_public_deploys(
    deploy_results: list[dict[str, Any]], published_obfuscated_root: Path
) -> dict[str, Any]:
    games = []
    for item in deploy_results:
        deploy_dir = Path(item["deploy_dir"])
        games.append(
            {
                "game_id": item["game_id"],
                "source_path": str(deploy_dir),
                "output_path": str((published_obfuscated_root / item["game_id"] / f"remix-{item['remix_uuid']}").resolve()),
            }
        )
    return {"games": games}


def build_report_path(args: argparse.Namespace) -> Path:
    if args.report_path:
        return Path(args.report_path).resolve()
    timestamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    return (REPO_ROOT / "tmp" / f"game_publish_pipeline_report_{timestamp}.json").resolve()


def run_pipeline(args: argparse.Namespace) -> int:
    raw_root = Path(args.raw_root).resolve()
    published_public_root = Path(args.published_public_root).resolve()
    published_obfuscated_root = Path(args.published_obfuscated_root).resolve()
    source_inputs = resolve_source_inputs(args)
    report_path = build_report_path(args)

    total_inputs = len(source_inputs)
    print(f"[pipeline] source inputs: {total_inputs}", flush=True)
    print(f"[pipeline] public root (stage): {published_public_root}", flush=True)
    print(f"[pipeline] obfuscated root: {published_obfuscated_root}", flush=True)
    print(f"[pipeline] report path: {report_path}", flush=True)

    print(f"[1/4] Public stage deploy ({total_inputs} items)", flush=True)
    staged_items = []
    for index, source in enumerate(source_inputs, start=1):
        staged_item = build_publish_input(source)
        staged_items.append(staged_item)
        print(
            f"[public-stage {index}/{total_inputs}] {staged_item['game_id']} -> remix-{staged_item['remix_hash']}",
            flush=True,
        )

    deploy_manifest = build_deploy_manifest(staged_items)
    deploy_manifest_path = write_temp_manifest("game-publish-pipeline-deploy-", deploy_manifest)
    print(f"[pipeline] deploy manifest: {deploy_manifest_path}", flush=True)

    if args.dry_run:
        payload = {
            "source_inputs": [str(path) for path in source_inputs],
            "publish_inputs": staged_items,
            "deploy_manifest_path": str(deploy_manifest_path),
            "published_public_root": str(published_public_root),
            "published_obfuscated_root": str(published_obfuscated_root),
            "report_path": str(report_path),
        }
        print(json.dumps(payload, indent=2))
        return 0

    print(f"[1/4] Public stage deploy ({total_inputs} items)", flush=True)
    deploy_command = [
        sys.executable,
        str(DEPLOY_SCRIPT),
        "--manifest",
        str(deploy_manifest_path),
        "--published-root",
        str(published_public_root),
    ]
    if args.overwrite:
        deploy_command.append("--overwrite")
    print(f"[pipeline] deploy command: {' '.join(deploy_command)}", flush=True)
    deploy_result = run_command(deploy_command)
    deploy_payload = deploy_result["payload"] or {}
    deploy_results = deploy_payload.get("results", [])
    if not isinstance(deploy_results, list):
        raise RuntimeError("game_deploy did not return a results array")

    for index, item in enumerate(deploy_results, start=1):
        print(
            f"[deploy {index}/{len(deploy_results)}] {item['game_id']} -> {item['deploy_dir']}",
            flush=True,
        )

    print(f"[2/4] Obfuscation ({len(deploy_results)} items)", flush=True)
    obfuscator_manifest = build_obfuscator_manifest_from_public_deploys(deploy_results, published_obfuscated_root)
    obfuscator_manifest_path = write_temp_manifest("game-publish-pipeline-obfuscator-", obfuscator_manifest)
    print(f"[pipeline] obfuscator manifest: {obfuscator_manifest_path}", flush=True)

    start_command = [
            sys.executable,
            str(OBFUSCATOR_ROOT / "scripts" / "game_obfuscator_cli.py"),
            "start",
            "--manifest",
            str(obfuscator_manifest_path),
            "--output-root",
            str(published_obfuscated_root),
        ]
    print(f"[pipeline] obfuscator command: {' '.join(start_command)}", flush=True)
    start_result = run_command(
        start_command
    )
    start_payload = start_result["payload"] or {}
    run_id = start_payload.get("run_id")
    if not run_id:
        raise RuntimeError("Obfuscator start did not return run_id")

    print(f"[pipeline] obfuscator run id: {run_id}", flush=True)
    print(f"[pipeline] obfuscator run dir: {start_payload.get('run_dir')}", flush=True)
    print(f"[pipeline] obfuscator dashboard: {start_payload.get('dashboard_path')}", flush=True)
    output_payload = {
        "run_id": start_payload.get("run_id"),
        "run_dir": start_payload.get("run_dir"),
        "status": start_payload.get("status"),
        "current_phase": start_payload.get("current_phase"),
        "output_path": start_payload.get("output_root"),
        "completed": start_payload.get("completed"),
        "game_outputs": start_payload.get("game_outputs", []),
    }
    obfuscation_game_outputs = output_payload.get("game_outputs", [])

    final_report = {
        "source_inputs": [str(path) for path in source_inputs],
        "public_stage_inputs": staged_items,
        "deployment": {
            "manifest_path": str(deploy_manifest_path),
            "published_public_root": str(published_public_root),
            "results": deploy_results,
        },
        "obfuscation": {
            "manifest_path": str(obfuscator_manifest_path),
            "published_obfuscated_root": str(published_obfuscated_root),
            "start": start_payload,
            "final_status": start_payload,
            "output": output_payload,
            "game_outputs": obfuscation_game_outputs,
        },
    }

    if args.refresh_app_artifacts_manifest:
        print("[3/4] Refresh app artifacts", flush=True)
        refresh_manifest_path = Path(args.refresh_app_artifacts_manifest).resolve()
        refresh_command = [
                sys.executable,
                str(REFRESH_APP_ARTIFACTS_SCRIPT),
                "--manifest",
                str(refresh_manifest_path),
                "--collection-slug",
                str(args.refresh_app_artifacts_collection_slug),
                "--public-root",
                str(published_public_root),
                "--obfuscated-root",
                str(published_obfuscated_root),
            ]
        print(f"[pipeline] refresh command: {' '.join(refresh_command)}", flush=True)
        refresh_result = run_command(
            refresh_command
        )
        final_report["app_artifacts_refresh"] = {
            "manifest_path": str(refresh_manifest_path),
            "collection_slug": str(args.refresh_app_artifacts_collection_slug),
            "result": refresh_result.get("payload"),
        }

    if args.validate_published_manifest:
        print("[4/4] Validate published outputs", flush=True)
        validate_manifest_path = Path(args.validate_published_manifest).resolve()
        validate_command = [
            sys.executable,
            str(VALIDATE_PUBLISHED_OUTPUTS_SCRIPT),
            "--manifest",
            str(validate_manifest_path),
            "--public-root",
            str(published_public_root),
            "--obfuscated-root",
            str(published_obfuscated_root),
            "--collection-slug",
            str(args.validate_published_collection_slug),
            "--annotator-html-name",
            str(args.validate_published_annotator_html_name),
        ]
        if args.validate_published_strict:
            validate_command.append("--strict")
        print(f"[pipeline] validation command: {' '.join(validate_command)}", flush=True)
        validate_result = run_command(validate_command)
        final_report["validation"] = {
            "manifest_path": str(validate_manifest_path),
            "collection_slug": str(args.validate_published_collection_slug),
            "annotator_html_name": str(args.validate_published_annotator_html_name),
            "strict": bool(args.validate_published_strict),
            "result": validate_result.get("payload"),
        }

    write_json(report_path, final_report)
    print(f"[pipeline] wrote final report: {report_path}", flush=True)
    if "validation" in final_report:
        summary = ((final_report.get("validation") or {}).get("result") or {}).get("summary") or {}
        if summary:
            print(
                "[pipeline] validation summary: "
                f"status={summary.get('status')} "
                f"entries_passed={summary.get('entries_passed')} "
                f"entries_failed={summary.get('entries_failed')} "
                f"failure_count={summary.get('failure_count')}",
                flush=True,
            )
    print(json.dumps(final_report, indent=2))
    return 0
