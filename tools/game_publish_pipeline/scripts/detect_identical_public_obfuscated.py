#!/usr/bin/env python3
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


SCRIPT_PATH = Path(__file__).resolve()
TOOL_ROOT = SCRIPT_PATH.parents[1]
REPO_ROOT = TOOL_ROOT.parents[1]

DEFAULT_PUBLIC_ROOT = REPO_ROOT / "games" / "published" / "public"
DEFAULT_OBFUSCATED_ROOT = REPO_ROOT / "games" / "published" / "obfuscated"
DEFAULT_RUNS_ROOT = REPO_ROOT / "games" / "published" / "runs"
DEFAULT_RAW_ROOT = REPO_ROOT / "games" / "raw"
REFRESH_APP_ARTIFACTS_SCRIPT = TOOL_ROOT / "scripts" / "refresh_app_artifacts.py"
MATERIALIZE_ARTIFACT_VIEW_SCRIPT = TOOL_ROOT / "scripts" / "materialize_artifact_view.py"
VALIDATE_PUBLISHED_OUTPUTS_SCRIPT = TOOL_ROOT / "scripts" / "validate_published_outputs.py"
DEFAULT_COLLECTION_SLUG = "vatsal_app_alpha"
DEFAULT_ANNOTATOR_HTML_NAME = "annotator.html"
DEFAULT_EXTENSIONS = [".html", ".js", ".css"]
DEFAULT_VENDOR_ASSET_DOMAINS = [
    "fonts.googleapis.com",
    "cdn.tailwindcss.com",
    "unpkg.com",
    "cdnjs.cloudflare.com",
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Detect files that are identical between published/public and published/obfuscated "
            "for matching relative paths."
        )
    )
    parser.add_argument(
        "--public-root",
        default=str(DEFAULT_PUBLIC_ROOT),
        help="Published public root to scan.",
    )
    parser.add_argument(
        "--obfuscated-root",
        default=str(DEFAULT_OBFUSCATED_ROOT),
        help="Published obfuscated root to compare against.",
    )
    parser.add_argument(
        "--raw-root",
        default=str(DEFAULT_RAW_ROOT),
        help="Raw root used for optional delete operations.",
    )
    parser.add_argument(
        "--extensions",
        default=",".join(DEFAULT_EXTENSIONS),
        help="Comma-separated extensions to compare (default: .html,.js,.css).",
    )
    parser.add_argument(
        "--report-path",
        help="Optional path to write a JSON report.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return non-zero when any identical file pairs are detected.",
    )
    parser.add_argument(
        "--include-appledouble",
        action="store_true",
        help="Include AppleDouble metadata files (._*) in comparisons.",
    )
    parser.add_argument(
        "--include-annotator",
        action="store_true",
        help="Include annotator.html in comparisons.",
    )
    parser.add_argument(
        "--include-vendor-assets",
        action="store_true",
        help="Include known vendor asset domains under assets/ in comparisons.",
    )
    parser.add_argument(
        "--vendor-asset-domains",
        default=",".join(DEFAULT_VENDOR_ASSET_DOMAINS),
        help=(
            "Comma-separated vendor asset domains used for default filtering under assets/. "
            "Used when --include-vendor-assets is not set."
        ),
    )
    parser.add_argument(
        "--quarentine",
        "--quarantine",
        dest="quarantine_root",
        nargs="?",
        const="__AUTO__",
        help=(
            "Optional output folder. When set with no value, uses "
            "games/published/runs/run_<timestamp>/quarantine."
        ),
    )
    parser.add_argument(
        "--list-affected-gamezones",
        action="store_true",
        help="Print sorted affected gamezone IDs derived from identical matches.",
    )
    parser.add_argument(
        "--delete-affected-gamezones",
        action="store_true",
        help=(
            "Delete affected gamezone folders (derived from identical matches) from raw/public/obfuscated roots."
        ),
    )
    parser.add_argument(
        "--delete-dry-run",
        action="store_true",
        help="Preview delete targets without deleting files.",
    )
    parser.add_argument(
        "--skip-post-cleanup",
        action="store_true",
        help="Skip automatic post-cleanup refresh/materialize/validate after executed cleanup delete.",
    )
    parser.add_argument(
        "--post-cleanup-manifest",
        help="Optional explicit manifest for post-cleanup refresh/validate. Defaults to latest runs/*/artifacts_manifest.json.",
    )
    parser.add_argument(
        "--post-cleanup-run-id",
        help="Optional explicit run id for post-cleanup refresh/materialize/validate outputs.",
    )
    parser.add_argument(
        "--post-cleanup-collection-slug",
        default=DEFAULT_COLLECTION_SLUG,
        help="Collection slug forwarded to post-cleanup refresh/validate.",
    )
    parser.add_argument(
        "--post-cleanup-annotator-html-name",
        default=DEFAULT_ANNOTATOR_HTML_NAME,
        help="Annotator html name forwarded to post-cleanup validate step.",
    )
    return parser


def parse_extensions(raw: str) -> set[str]:
    tokens = [token.strip().lower() for token in raw.split(",") if token.strip()]
    if not tokens:
        raise SystemExit("--extensions must include at least one extension.")

    normalized: set[str] = set()
    for token in tokens:
        normalized.add(token if token.startswith(".") else f".{token}")
    return normalized


def parse_csv_tokens(raw: str) -> set[str]:
    return {token.strip() for token in raw.split(",") if token.strip()}


def is_appledouble(rel_path: Path) -> bool:
    return any(part.startswith("._") for part in rel_path.parts)


def is_vendor_asset(rel_path: Path, vendor_domains: set[str]) -> bool:
    parts = rel_path.parts
    for idx, part in enumerate(parts):
        if part == "assets" and idx + 1 < len(parts):
            return parts[idx + 1] in vendor_domains
    return False


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_quarantine_root(raw_value: str | None) -> Path | None:
    if raw_value is None:
        return None

    if raw_value == "__AUTO__":
        run_id = time.strftime("run_%Y%m%dT%H%M%SZ", time.gmtime())
        return (DEFAULT_RUNS_ROOT / run_id / "quarantine").resolve()

    return Path(raw_value).resolve()


def parse_json_payload_from_stdout(stdout: str) -> dict[str, Any] | None:
    text = stdout.strip()
    if not text:
        return None

    try:
        payload = json.loads(text)
        if isinstance(payload, dict):
            return payload
    except json.JSONDecodeError:
        pass

    open_brace_positions = [index for index, char in enumerate(text) if char == "{"]
    for index in reversed(open_brace_positions):
        candidate = text[index:]
        try:
            payload = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            return payload
    return None


def run_checked_command(command: list[str], *, label: str) -> dict[str, Any]:
    print(f"[cleanup-post] {label} command: {' '.join(command)}")
    completed = subprocess.run(command, capture_output=True, text=True)
    stdout = completed.stdout.strip()
    stderr = completed.stderr.strip()

    if stdout:
        print(stdout)
    if stderr:
        print(stderr, file=sys.stderr)

    if completed.returncode != 0:
        raise SystemExit(f"{label} failed with exit code {completed.returncode}")

    return {
        "label": label,
        "command": command,
        "stdout": stdout,
        "stderr": stderr,
        "payload": parse_json_payload_from_stdout(stdout),
    }


def find_latest_run_manifest(runs_root: Path) -> Path:
    candidates: list[Path] = []
    for run_dir in sorted(runs_root.glob("run_*")):
        if not run_dir.is_dir():
            continue
        manifest_path = run_dir / "artifacts_manifest.json"
        if manifest_path.is_file():
            candidates.append(manifest_path)

    if not candidates:
        raise SystemExit(f"No run artifacts manifests found under {runs_root}")
    return candidates[-1]


def write_temp_manifest(payload: Any) -> Path:
    handle = tempfile.NamedTemporaryFile(prefix="cleanup-post-manifest-", suffix=".json", delete=False)
    path = Path(handle.name)
    handle.close()
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def build_post_cleanup_manifest(
    *,
    source_manifest_path: Path,
    public_root: Path,
    excluded_gamezones: set[str],
) -> tuple[Path, dict[str, Any]]:
    payload = json.loads(source_manifest_path.read_text(encoding="utf-8"))

    if isinstance(payload, dict) and isinstance(payload.get("entries"), list):
        entries = payload.get("entries") or []
        filtered_entries: list[Any] = []
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            game_id = str(entry.get("game_id") or "")
            if game_id and game_id in excluded_gamezones:
                continue

            published_path = str(entry.get("published_path") or "")
            if published_path:
                if not (public_root / published_path).is_dir():
                    continue
            elif game_id:
                if not (public_root / game_id).is_dir():
                    continue

            filtered_entries.append(entry)

        filtered_payload = dict(payload)
        filtered_payload["entries"] = filtered_entries
        filtered_payload["entry_count"] = len(filtered_entries)
        manifest_path = write_temp_manifest(filtered_payload)
        return manifest_path, {
            "source_manifest": str(source_manifest_path),
            "effective_manifest": str(manifest_path),
            "filtered": True,
            "entries_before": len(entries),
            "entries_after": len(filtered_entries),
        }

    if isinstance(payload, list):
        filtered_list: list[Any] = []
        for item in payload:
            if isinstance(item, str):
                game_id = Path(item).name
                if game_id in excluded_gamezones:
                    continue
                if not (public_root / game_id).is_dir():
                    continue
            filtered_list.append(item)
        manifest_path = write_temp_manifest(filtered_list)
        return manifest_path, {
            "source_manifest": str(source_manifest_path),
            "effective_manifest": str(manifest_path),
            "filtered": True,
            "entries_before": len(payload),
            "entries_after": len(filtered_list),
        }

    return source_manifest_path, {
        "source_manifest": str(source_manifest_path),
        "effective_manifest": str(source_manifest_path),
        "filtered": False,
        "entries_before": None,
        "entries_after": None,
        "note": "Manifest shape unsupported for filtering; using source manifest as-is.",
    }


def run_post_cleanup_steps(
    *,
    runs_root: Path,
    raw_root: Path,
    public_root: Path,
    obfuscated_root: Path,
    affected_gamezones: list[str],
    explicit_manifest: str | None,
    explicit_run_id: str | None,
    collection_slug: str,
    annotator_html_name: str,
) -> dict[str, Any]:
    if explicit_manifest:
        source_manifest_path = Path(explicit_manifest).resolve()
    else:
        source_manifest_path = find_latest_run_manifest(runs_root)

    excluded_gamezones = set(affected_gamezones)
    effective_manifest_path, manifest_meta = build_post_cleanup_manifest(
        source_manifest_path=source_manifest_path,
        public_root=public_root,
        excluded_gamezones=excluded_gamezones,
    )

    run_id = explicit_run_id or f"run_cleanup_{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}"
    run_dir = runs_root / run_id

    refresh_command = [
        sys.executable,
        str(REFRESH_APP_ARTIFACTS_SCRIPT),
        "--manifest",
        str(effective_manifest_path),
        "--runs-root",
        str(runs_root),
        "--run-id",
        str(run_id),
        "--collection-slug",
        str(collection_slug),
        "--public-root",
        str(public_root),
        "--obfuscated-root",
        str(obfuscated_root),
        "--reconcile-mode",
        "replace",
        "--no-materialize-root",
    ]
    refresh_result = run_checked_command(refresh_command, label="refresh_app_artifacts")

    materialize_command = [
        sys.executable,
        str(MATERIALIZE_ARTIFACT_VIEW_SCRIPT),
        "--runs",
        str(run_dir),
        "--public-root",
        str(public_root),
        "--obfuscated-root",
        str(obfuscated_root),
        "--precedence",
        "latest-wins",
    ]
    materialize_result = run_checked_command(materialize_command, label="materialize_artifact_view")

    validate_report_path = (
        REPO_ROOT
        / "tmp"
        / f"post_cleanup_validate_{run_id}.json"
    ).resolve()
    validate_command = [
        sys.executable,
        str(VALIDATE_PUBLISHED_OUTPUTS_SCRIPT),
        "--manifest",
        str(effective_manifest_path),
        "--public-root",
        str(public_root),
        "--obfuscated-root",
        str(obfuscated_root),
        "--runs-root",
        str(runs_root),
        "--run-id",
        str(run_id),
        "--collection-slug",
        str(collection_slug),
        "--annotator-html-name",
        str(annotator_html_name),
        "--report-path",
        str(validate_report_path),
        "--strict",
    ]
    validate_result = run_checked_command(validate_command, label="validate_published_outputs")
    validate_summary = ((validate_result.get("payload") or {}).get("summary") or {})

    return {
        "raw_root": str(raw_root),
        "public_root": str(public_root),
        "obfuscated_root": str(obfuscated_root),
        "runs_root": str(runs_root),
        "run_id": run_id,
        "run_dir": str(run_dir),
        "manifest": manifest_meta,
        "refresh": {
            "result": refresh_result.get("payload"),
        },
        "materialize": {
            "result": materialize_result.get("payload"),
        },
        "validate": {
            "report_path": str(validate_report_path),
            "summary": validate_summary,
            "result": validate_result.get("payload"),
        },
    }


def extract_affected_gamezones(identical_rel_paths: list[str]) -> list[str]:
    affected: set[str] = set()
    for rel in identical_rel_paths:
        parts = Path(rel).parts
        if parts and parts[0].startswith("gamezone-"):
            affected.add(parts[0])
    return sorted(affected)


def delete_affected_gamezones(
    *,
    affected_gamezones: list[str],
    raw_root: Path,
    public_root: Path,
    obfuscated_root: Path,
    dry_run: bool,
) -> dict[str, object]:
    deleted: list[str] = []
    missing: list[str] = []

    for game_id in affected_gamezones:
        targets = {
            "raw": raw_root / game_id,
            "public": public_root / game_id,
            "obfuscated": obfuscated_root / game_id,
        }
        for scope, path in targets.items():
            marker = f"{scope}:{path}"
            if path.exists():
                deleted.append(marker)
                if not dry_run:
                    shutil.rmtree(path)
            else:
                missing.append(marker)

    return {
        "dry_run": dry_run,
        "deleted_count": len(deleted),
        "deleted_targets": deleted,
        "missing_count": len(missing),
        "missing_targets": missing,
    }


def main() -> int:
    args = build_parser().parse_args()
    raw_root = Path(args.raw_root).resolve()
    public_root = Path(args.public_root).resolve()
    obfuscated_root = Path(args.obfuscated_root).resolve()
    target_extensions = parse_extensions(args.extensions)
    vendor_domains = parse_csv_tokens(args.vendor_asset_domains)
    quarantine_root = resolve_quarantine_root(args.quarantine_root)

    if not public_root.is_dir():
        raise SystemExit(f"Public root is not a directory: {public_root}")
    if not obfuscated_root.is_dir():
        raise SystemExit(f"Obfuscated root is not a directory: {obfuscated_root}")

    scanned_public_files = 0
    skipped_appledouble = 0
    skipped_annotator = 0
    skipped_vendor_assets = 0
    comparable_pairs = 0
    identical_pairs: list[str] = []
    quarantined_paths: list[str] = []
    missing_in_obfuscated: list[str] = []

    for public_path in sorted(public_root.rglob("*")):
        if not public_path.is_file():
            continue
        if public_path.suffix.lower() not in target_extensions:
            continue

        scanned_public_files += 1
        rel_path = public_path.relative_to(public_root)

        if not args.include_appledouble and is_appledouble(rel_path):
            skipped_appledouble += 1
            continue

        if not args.include_annotator and rel_path.name == "annotator.html":
            skipped_annotator += 1
            continue

        if not args.include_vendor_assets and is_vendor_asset(rel_path, vendor_domains):
            skipped_vendor_assets += 1
            continue

        obfuscated_path = obfuscated_root / rel_path

        if not obfuscated_path.is_file():
            missing_in_obfuscated.append(str(rel_path))
            continue

        comparable_pairs += 1
        if sha256_file(public_path) == sha256_file(obfuscated_path):
            rel_str = str(rel_path)
            identical_pairs.append(rel_str)

            if quarantine_root is not None:
                quarantine_path = quarantine_root / rel_path
                quarantine_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(public_path, quarantine_path)
                quarantined_paths.append(rel_str)

    report = {
        "raw_root": str(raw_root),
        "public_root": str(public_root),
        "obfuscated_root": str(obfuscated_root),
        "extensions": sorted(target_extensions),
        "scanned_public_files": scanned_public_files,
        "skipped_appledouble": skipped_appledouble,
        "skipped_annotator": skipped_annotator,
        "skipped_vendor_assets": skipped_vendor_assets,
        "comparable_pairs": comparable_pairs,
        "identical_pairs": len(identical_pairs),
        "quarantine_root": str(quarantine_root) if quarantine_root else None,
        "quarantined_files": len(quarantined_paths),
        "quarantined_paths": quarantined_paths,
        "missing_in_obfuscated": len(missing_in_obfuscated),
        "identical_paths": identical_pairs,
        "missing_paths": missing_in_obfuscated,
    }

    affected_gamezones = extract_affected_gamezones(identical_pairs)
    report["affected_gamezone_count"] = len(affected_gamezones)
    report["affected_gamezone_ids"] = affected_gamezones

    deletion_summary: dict[str, object] | None = None
    post_cleanup_summary: dict[str, Any] | None = None
    if args.delete_affected_gamezones:
        deletion_summary = delete_affected_gamezones(
            affected_gamezones=affected_gamezones,
            raw_root=raw_root,
            public_root=public_root,
            obfuscated_root=obfuscated_root,
            dry_run=bool(args.delete_dry_run),
        )
        report["deletion"] = deletion_summary

        if not args.delete_dry_run and not args.skip_post_cleanup:
            post_cleanup_summary = run_post_cleanup_steps(
                runs_root=DEFAULT_RUNS_ROOT.resolve(),
                raw_root=raw_root,
                public_root=public_root,
                obfuscated_root=obfuscated_root,
                affected_gamezones=affected_gamezones,
                explicit_manifest=args.post_cleanup_manifest,
                explicit_run_id=args.post_cleanup_run_id,
                collection_slug=str(args.post_cleanup_collection_slug),
                annotator_html_name=str(args.post_cleanup_annotator_html_name),
            )
            report["post_cleanup"] = post_cleanup_summary

    print("== Detect Identical Public vs Obfuscated Files ==")
    print(f"Raw root: {raw_root}")
    print(f"Public root: {public_root}")
    print(f"Obfuscated root: {obfuscated_root}")
    print(f"Extensions: {', '.join(sorted(target_extensions))}")
    print(f"Scanned public files: {scanned_public_files}")
    print(f"Skipped AppleDouble (._*): {skipped_appledouble}")
    print(f"Skipped annotator.html: {skipped_annotator}")
    print(f"Skipped vendor assets: {skipped_vendor_assets}")
    print(f"Comparable file pairs: {comparable_pairs}")
    print(f"Identical file pairs: {len(identical_pairs)}")
    if quarantine_root is not None:
        print(f"Quarantine root: {quarantine_root}")
        print(f"Quarantined files copied: {len(quarantined_paths)}")
    print(f"Affected gamezone IDs: {len(affected_gamezones)}")
    print(f"Missing in obfuscated: {len(missing_in_obfuscated)}")

    if args.list_affected_gamezones and affected_gamezones:
        print("\nAffected gamezone IDs:")
        for game_id in affected_gamezones:
            print(f"  - {game_id}")

    if deletion_summary is not None:
        mode = "DRY RUN" if deletion_summary.get("dry_run") else "EXECUTED"
        print(f"\nDelete affected gamezones ({mode}):")
        print(f"  Deleted targets: {deletion_summary.get('deleted_count', 0)}")
        print(f"  Missing targets: {deletion_summary.get('missing_count', 0)}")

    if post_cleanup_summary is not None:
        validate_summary = ((post_cleanup_summary.get("validate") or {}).get("summary") or {})
        print("\nPost-cleanup steps:")
        print(f"  run_id: {post_cleanup_summary.get('run_id')}")
        print(f"  manifest: {(post_cleanup_summary.get('manifest') or {}).get('effective_manifest')}")
        print(
            "  validate summary: "
            f"status={validate_summary.get('status')} "
            f"entries_passed={validate_summary.get('entries_passed')} "
            f"entries_failed={validate_summary.get('entries_failed')} "
            f"failure_count={validate_summary.get('failure_count')}"
        )

    if identical_pairs:
        print("\nIdentical paths (first 20):")
        for rel_path in identical_pairs[:20]:
            print(f"  - {rel_path}")
        remaining = len(identical_pairs) - 20
        if remaining > 0:
            print(f"  ... {remaining} more")

    if args.report_path:
        report_path = Path(args.report_path).resolve()
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(f"\nReport written to: {report_path}")

    if args.strict and identical_pairs:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
