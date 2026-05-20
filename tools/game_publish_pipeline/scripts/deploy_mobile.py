#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import secrets
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
DEFAULT_MOBILE_RUNS_ROOT = TOOL_ROOT / "scripts" / "mobile" / "run_artifacts"
DEFAULT_MOBILE_SCRIPT = TOOL_ROOT / "scripts" / "mobile" / "validate_artifact_orchestration.py"
DEFAULT_SHARED_PASSWORD_PATH = TOOL_ROOT / "scripts" / "mobile" / "release_zip_password.txt"

BASE_ARTIFACT_NAMES = (
    "app.json",
    "index.json",
    "app_tags.json",
)

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

ALL_REQUIRED_ARTIFACT_NAMES = BASE_ARTIFACT_NAMES + MOBILE_ARTIFACT_NAMES


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Create run-scoped mobile release bundles by copying core artifacts, "
            "generating mobile artifacts from a run-local app.json, verifying the "
            "complete artifact set, and zipping a deploy staging directory."
        )
    )
    parser.add_argument(
        "--target",
        choices=("public", "obfuscated", "both"),
        default="both",
        help="Which published scope(s) to package.",
    )
    parser.add_argument("--public-root", default=str(DEFAULT_PUBLIC_ROOT), help="Published public root.")
    parser.add_argument("--obfuscated-root", default=str(DEFAULT_OBFUSCATED_ROOT), help="Published obfuscated root.")
    parser.add_argument(
        "--mobile-runs-root",
        default=str(DEFAULT_MOBILE_RUNS_ROOT),
        help="Root for timestamped mobile generation runs.",
    )
    parser.add_argument(
        "--mobile-script",
        default=str(DEFAULT_MOBILE_SCRIPT),
        help="Path to the mobile validation/generation script.",
    )
    parser.add_argument(
        "--require-screenshots",
        dest="require_screenshots",
        action="store_true",
        help="Require the slower screenshot cleanup/validation path during mobile generation.",
    )
    parser.add_argument(
        "--screenshots-cleanup",
        dest="require_screenshots",
        action="store_true",
        help="Alias for --require-screenshots.",
    )
    parser.add_argument(
        "--password-bytes",
        type=int,
        default=64,
        help="Entropy bytes used when lazily creating the shared release password (default: 64).",
    )
    parser.add_argument(
        "--shared-password-path",
        default=str(DEFAULT_SHARED_PASSWORD_PATH),
        help="Path to the lazily created shared zip password file reused across mobile release runs.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate the base artifact inputs and print the bundle plan without generating or zipping outputs.",
    )
    return parser


def build_run_id() -> str:
    return datetime.now(timezone.utc).strftime("run_%Y%m%dT%H%M%SZ")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def print_scope(scope_name: str, message: str) -> None:
    print(f"[deploy-mobile] [{scope_name}] {message}", flush=True)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def extract_trailing_json(stdout: str) -> dict[str, Any]:
    stripped = stdout.strip()
    if not stripped:
        return {}
    start = stripped.rfind("\n{")
    json_text = stripped[start + 1 :] if start != -1 else stripped
    payload = json.loads(json_text)
    if not isinstance(payload, dict):
        raise RuntimeError("Expected JSON object payload from child command.")
    return payload


def run_json_command(command: list[str], *, cwd: Path, scope_name: str, label: str, log_path: Path) -> dict[str, Any]:
    effective_command = list(command)
    if effective_command and Path(effective_command[0]).name.startswith("python"):
        effective_command.insert(1, "-u")
    print_scope(scope_name, f"{label} cwd={cwd}")
    print_scope(scope_name, f"{label} command={' '.join(effective_command)}")
    print_scope(scope_name, f"{label} log={log_path}")
    process = subprocess.Popen(
        effective_command,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_handle = log_path.open("w", encoding="utf-8")
    log_handle.write(f"$ (cwd={cwd}) {' '.join(effective_command)}\n\n")
    log_handle.flush()
    captured_lines: list[str] = []
    assert process.stdout is not None
    try:
        for line in process.stdout:
            print(line, end="")
            captured_lines.append(line)
            log_handle.write(line)
            log_handle.flush()
        returncode = process.wait()
        stdout = "".join(captured_lines)
        log_handle.write(f"\n[exit_code] {returncode}\n")
        log_handle.flush()
    finally:
        log_handle.close()
    if returncode != 0:
        print_scope(scope_name, f"{label} failed exit_code={returncode} log={log_path}")
        raise RuntimeError(f"{label} failed for {scope_name} with exit code {returncode}. See log: {log_path}")
    print_scope(scope_name, f"{label} completed log={log_path}")
    return extract_trailing_json(stdout)


def run_checked_command(
    command: list[str],
    *,
    cwd: Path,
    scope_name: str,
    label: str,
    log_path: Path,
    display_command: list[str] | None = None,
) -> None:
    print_scope(scope_name, f"{label} cwd={cwd}")
    print_scope(scope_name, f"{label} command={' '.join(display_command or command)}")
    print_scope(scope_name, f"{label} log={log_path}")
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
    combined_output = result.stdout
    if result.stderr:
        combined_output += ("" if combined_output.endswith("\n") or not combined_output else "\n") + result.stderr
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(
        f"$ (cwd={cwd}) {' '.join(display_command or command)}\n\n{combined_output}\n[exit_code] {result.returncode}\n",
        encoding="utf-8",
    )
    if result.returncode != 0:
        print_scope(scope_name, f"{label} failed exit_code={result.returncode} log={log_path}")
        raise RuntimeError(f"{label} failed for {scope_name} with exit code {result.returncode}. See log: {log_path}")
    print_scope(scope_name, f"{label} completed log={log_path}")


def copy_artifact(
    *,
    scope_name: str,
    artifact_name: str,
    source_path: Path,
    target_path: Path,
    dry_run: bool,
    phase: str,
) -> dict[str, str]:
    if not source_path.is_file():
        raise RuntimeError(f"Missing required artifact for {scope_name}: {source_path}")
    print_scope(scope_name, f"{phase} artifact={artifact_name}")
    print_scope(scope_name, f"{phase} source={source_path}")
    print_scope(scope_name, f"{phase} target={target_path}")
    if dry_run:
        print_scope(scope_name, f"{phase} dry-run skip copy {artifact_name}")
    else:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, target_path)
        print_scope(scope_name, f"{phase} copied {artifact_name}")
    return {"artifact": artifact_name, "source": str(source_path), "target": str(target_path)}


def verify_expected_artifacts(scope_name: str, artifacts_dir: Path, expected_names: tuple[str, ...]) -> list[str]:
    missing: list[str] = []
    print_scope(scope_name, f"verifying expected artifact set in {artifacts_dir}")
    for artifact_name in expected_names:
        artifact_path = artifacts_dir / artifact_name
        exists = artifact_path.is_file()
        print_scope(scope_name, f"verify artifact={artifact_name} exists={exists} path={artifact_path}")
        if not exists:
            missing.append(artifact_name)
    return missing


def build_mobile_command(
    *,
    mobile_script: Path,
    input_catalog: Path,
    mobile_run_root: Path,
    compare_root: Path,
    require_screenshots: bool,
) -> list[str]:
    command = [
        sys.executable,
        str(mobile_script),
        "--input",
        str(input_catalog),
        "--run-root",
        str(mobile_run_root),
        "--compare-root",
        str(compare_root),
    ]
    if require_screenshots:
        command.append("--screenshots-cleanup")
    return command


def resolve_shared_password(
    *,
    shared_password_path: Path,
    password_bytes: int,
    dry_run: bool,
) -> tuple[str | None, bool]:
    if shared_password_path.is_file():
        password = shared_password_path.read_text(encoding="utf-8").strip()
        if not password:
            raise RuntimeError(f"Shared password file is empty: {shared_password_path}")
        try:
            shared_password_path.chmod(0o600)
        except OSError:
            pass
        return password, False

    if dry_run:
        return None, False

    ensure_dir(shared_password_path.parent)
    password = secrets.token_urlsafe(password_bytes)
    shared_password_path.write_text(password + "\n", encoding="utf-8")
    try:
        shared_password_path.chmod(0o600)
    except OSError:
        pass
    return password, True


def write_remove_file(scope_name: str, run_dir: Path, password: str, shared_password_path: Path) -> Path:
    remove_path = run_dir / "remove.txt"
    lines = [
        f"scope={scope_name}",
        f"run_dir={run_dir}",
        f"shared_password_path={shared_password_path}",
        "This release.zip password is shared across mobile release runs.",
        "Remove this file when you no longer need a run-local password reminder.",
        "",
        f"password={password}",
    ]
    remove_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print_scope(scope_name, f"wrote password companion file: {remove_path}")
    return remove_path


def create_release_zip(
    scope_name: str,
    *,
    run_dir: Path,
    deploy_dir: Path,
    password: str,
    log_path: Path,
) -> Path:
    release_zip = run_dir / "release.zip"
    if release_zip.exists():
        release_zip.unlink()
        print_scope(scope_name, f"removed existing zip before rebuild: {release_zip}")
    zip_command = ["zip", "-r", "-P", password, str(release_zip.name), str(deploy_dir.name)]
    zip_display_command = ["zip", "-r", "-P", "<redacted>", str(release_zip.name), str(deploy_dir.name)]
    print_scope(scope_name, f"zip file list source={deploy_dir}")
    for file_path in sorted(path for path in deploy_dir.rglob("*") if path.is_file()):
        print_scope(scope_name, f"zip include {file_path.relative_to(run_dir)}")
    run_checked_command(
        zip_command,
        cwd=run_dir,
        scope_name=scope_name,
        label="zip_release",
        log_path=log_path,
        display_command=zip_display_command,
    )
    if not release_zip.is_file():
        raise RuntimeError(f"release zip was not created for {scope_name}: {release_zip}")
    print_scope(scope_name, f"created release zip: {release_zip}")
    return release_zip


def stage_scope_release(
    *,
    scope_name: str,
    scope_root: Path,
    run_id: str,
    mobile_script: Path,
    mobile_runs_root: Path,
    shared_password_path: Path,
    shared_password: str | None,
    require_screenshots: bool,
    password_bytes: int,
    dry_run: bool,
) -> dict[str, Any]:
    bundle_root = scope_root / "bundle"
    run_dir = bundle_root / run_id
    artifacts_dir = run_dir / "artifacts"
    deploy_dir = run_dir / "deploy"
    logs_dir = run_dir / "logs"
    mobile_run_root = mobile_runs_root / scope_name
    compare_root = bundle_root
    run_local_app_json = artifacts_dir / "app.json"

    print_scope(scope_name, "=================================")
    print_scope(scope_name, f"scope root={scope_root}")
    print_scope(scope_name, f"bundle root={bundle_root}")
    print_scope(scope_name, f"run dir={run_dir}")
    print_scope(scope_name, f"artifacts dir={artifacts_dir}")
    print_scope(scope_name, f"deploy dir={deploy_dir}")
    print_scope(scope_name, f"logs dir={logs_dir}")
    print_scope(scope_name, f"mobile run root={mobile_run_root}")
    print_scope(scope_name, f"mobile compare root={compare_root}")
    print_scope(scope_name, f"shared password path={shared_password_path}")
    print_scope(scope_name, f"dry_run={dry_run}")
    print_scope(scope_name, "=================================")

    if not scope_root.is_dir():
        raise RuntimeError(f"Scope root does not exist or is not a directory for {scope_name}: {scope_root}")

    if not dry_run:
        ensure_dir(bundle_root)
        ensure_dir(run_dir)
        ensure_dir(artifacts_dir)
        ensure_dir(logs_dir)

    base_copies: list[dict[str, str]] = []
    for artifact_name in BASE_ARTIFACT_NAMES:
        base_copies.append(
            copy_artifact(
                scope_name=scope_name,
                artifact_name=artifact_name,
                source_path=scope_root / artifact_name,
                target_path=artifacts_dir / artifact_name,
                dry_run=dry_run,
                phase="stage-base",
            )
        )

    mobile_command = build_mobile_command(
        mobile_script=mobile_script,
        input_catalog=run_local_app_json,
        mobile_run_root=mobile_run_root,
        compare_root=compare_root,
        require_screenshots=require_screenshots,
    )

    if dry_run:
        print_scope(scope_name, "dry-run stopping before mobile generation and zip creation")
        return {
            "scope": scope_name,
            "scope_root": str(scope_root),
            "bundle_root": str(bundle_root),
            "run_dir": str(run_dir),
            "artifacts_dir": str(artifacts_dir),
            "deploy_dir": str(deploy_dir),
            "logs_dir": str(logs_dir),
            "dry_run": True,
            "shared_password_path": str(shared_password_path),
            "base_copies": base_copies,
            "mobile_command": mobile_command,
            "expected_base_artifacts": list(BASE_ARTIFACT_NAMES),
            "expected_mobile_artifacts": list(MOBILE_ARTIFACT_NAMES),
            "expected_complete_artifacts": list(ALL_REQUIRED_ARTIFACT_NAMES),
        }

    mobile_payload = run_json_command(
        mobile_command,
        cwd=TOOL_ROOT,
        scope_name=scope_name,
        label="mobile_generate",
        log_path=logs_dir / "mobile_generate.log",
    )
    mobile_artifacts_dir_value = str(mobile_payload.get("artifacts_dir") or "")
    if not mobile_artifacts_dir_value:
        raise RuntimeError(f"Mobile generator did not return artifacts_dir for {scope_name}")
    mobile_artifacts_dir = Path(mobile_artifacts_dir_value).resolve()
    print_scope(scope_name, f"selected mobile artifacts dir={mobile_artifacts_dir}")

    mobile_copies: list[dict[str, str]] = []
    for artifact_name in MOBILE_ARTIFACT_NAMES:
        mobile_copies.append(
            copy_artifact(
                scope_name=scope_name,
                artifact_name=artifact_name,
                source_path=mobile_artifacts_dir / artifact_name,
                target_path=artifacts_dir / artifact_name,
                dry_run=False,
                phase="stage-mobile",
            )
        )

    missing_after_stage = verify_expected_artifacts(scope_name, artifacts_dir, ALL_REQUIRED_ARTIFACT_NAMES)
    if missing_after_stage:
        raise RuntimeError(
            f"Cannot create release for {scope_name}; missing staged artifacts: {', '.join(missing_after_stage)}"
        )

    ensure_dir(deploy_dir)
    deploy_copies: list[dict[str, str]] = []
    for artifact_name in ALL_REQUIRED_ARTIFACT_NAMES:
        deploy_copies.append(
            copy_artifact(
                scope_name=scope_name,
                artifact_name=artifact_name,
                source_path=artifacts_dir / artifact_name,
                target_path=deploy_dir / artifact_name,
                dry_run=False,
                phase="stage-deploy",
            )
        )

    missing_in_deploy = verify_expected_artifacts(scope_name, deploy_dir, ALL_REQUIRED_ARTIFACT_NAMES)
    if missing_in_deploy:
        raise RuntimeError(
            f"Cannot create release for {scope_name}; missing deploy artifacts: {', '.join(missing_in_deploy)}"
        )

    if not shared_password:
        raise RuntimeError(f"Shared password was not available for {scope_name}")
    remove_path = write_remove_file(scope_name, run_dir, shared_password, shared_password_path)
    release_zip = create_release_zip(
        scope_name,
        run_dir=run_dir,
        deploy_dir=deploy_dir,
        password=shared_password,
        log_path=logs_dir / "zip_release.log",
    )

    summary = {
        "scope": scope_name,
        "scope_root": str(scope_root),
        "bundle_root": str(bundle_root),
        "run_dir": str(run_dir),
        "artifacts_dir": str(artifacts_dir),
        "deploy_dir": str(deploy_dir),
        "logs_dir": str(logs_dir),
        "release_zip": str(release_zip),
        "remove_file": str(remove_path),
        "shared_password_path": str(shared_password_path),
        "mobile_run_dir": str(mobile_payload.get("run_dir") or ""),
        "mobile_artifacts_dir": str(mobile_artifacts_dir),
        "require_screenshots": bool(require_screenshots),
        "base_copies": base_copies,
        "mobile_copies": mobile_copies,
        "deploy_copies": deploy_copies,
        "expected_complete_artifacts": list(ALL_REQUIRED_ARTIFACT_NAMES),
    }
    write_json(run_dir / "summary.json", summary)
    print_scope(scope_name, f"wrote summary: {run_dir / 'summary.json'}")
    return summary


def main() -> int:
    args = build_parser().parse_args()
    public_root = Path(args.public_root).resolve()
    obfuscated_root = Path(args.obfuscated_root).resolve()
    mobile_runs_root = Path(args.mobile_runs_root).resolve()
    mobile_script = Path(args.mobile_script).resolve()
    shared_password_path = Path(args.shared_password_path).resolve()
    run_id = build_run_id()

    if not mobile_script.is_file():
        raise SystemExit(f"Mobile script not found: {mobile_script}")
    if args.password_bytes <= 0:
        raise SystemExit("--password-bytes must be greater than zero")

    shared_password, created_shared_password = resolve_shared_password(
        shared_password_path=shared_password_path,
        password_bytes=int(args.password_bytes),
        dry_run=bool(args.dry_run),
    )

    targets: list[tuple[str, Path]] = []
    if args.target in {"public", "both"}:
        targets.append(("public", public_root))
    if args.target in {"obfuscated", "both"}:
        targets.append(("obfuscated", obfuscated_root))

    print("[deploy-mobile] =============================", flush=True)
    print("[deploy-mobile] Deploy mobile release bundles", flush=True)
    print(f"[deploy-mobile] target={args.target}", flush=True)
    print(f"[deploy-mobile] run_id={run_id}", flush=True)
    print(f"[deploy-mobile] mobile_runs_root={mobile_runs_root}", flush=True)
    print(f"[deploy-mobile] mobile_script={mobile_script}", flush=True)
    print(f"[deploy-mobile] shared_password_path={shared_password_path}", flush=True)
    print(f"[deploy-mobile] shared_password_created={created_shared_password}", flush=True)
    print(f"[deploy-mobile] require_screenshots={args.require_screenshots}", flush=True)
    print(f"[deploy-mobile] dry_run={args.dry_run}", flush=True)
    if not args.require_screenshots:
        recommended_command = [
            sys.executable,
            str(SCRIPT_PATH),
            "--target",
            str(args.target),
            "--require-screenshots",
        ]
        if args.shared_password_path != str(DEFAULT_SHARED_PASSWORD_PATH):
            recommended_command.extend(["--shared-password-path", str(args.shared_password_path)])
        if args.mobile_runs_root != str(DEFAULT_MOBILE_RUNS_ROOT):
            recommended_command.extend(["--mobile-runs-root", str(args.mobile_runs_root)])
        if args.mobile_script != str(DEFAULT_MOBILE_SCRIPT):
            recommended_command.extend(["--mobile-script", str(args.mobile_script)])
        if args.public_root != str(DEFAULT_PUBLIC_ROOT):
            recommended_command.extend(["--public-root", str(args.public_root)])
        if args.obfuscated_root != str(DEFAULT_OBFUSCATED_ROOT):
            recommended_command.extend(["--obfuscated-root", str(args.obfuscated_root)])
        if args.password_bytes != 64:
            recommended_command.extend(["--password-bytes", str(args.password_bytes)])
        if args.dry_run:
            recommended_command.append("--dry-run")
        print(
            "[deploy-mobile] WARNING: running without --require-screenshots is testing-only and is not the proper production release path.",
            flush=True,
        )
        print(
            "[deploy-mobile] Recommended production command: "
            + " ".join(recommended_command),
            flush=True,
        )
    print("[deploy-mobile] =============================", flush=True)

    result = {
        "run_id": run_id,
        "target": args.target,
        "shared_password_path": str(shared_password_path),
        "shared_password_created": created_shared_password,
        "require_screenshots": bool(args.require_screenshots),
        "dry_run": bool(args.dry_run),
        "scopes": {},
    }

    for scope_name, scope_root in targets:
        result["scopes"][scope_name] = stage_scope_release(
            scope_name=scope_name,
            scope_root=scope_root,
            run_id=run_id,
            mobile_script=mobile_script,
            mobile_runs_root=mobile_runs_root,
            shared_password_path=shared_password_path,
            shared_password=shared_password,
            require_screenshots=bool(args.require_screenshots),
            password_bytes=int(args.password_bytes),
            dry_run=bool(args.dry_run),
        )

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())