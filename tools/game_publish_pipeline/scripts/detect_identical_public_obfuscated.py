#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import time
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve()
TOOL_ROOT = SCRIPT_PATH.parents[1]
REPO_ROOT = TOOL_ROOT.parents[1]

DEFAULT_PUBLIC_ROOT = REPO_ROOT / "games" / "published" / "public"
DEFAULT_OBFUSCATED_ROOT = REPO_ROOT / "games" / "published" / "obfuscated"
DEFAULT_RUNS_ROOT = REPO_ROOT / "games" / "published" / "runs"
DEFAULT_RAW_ROOT = REPO_ROOT / "games" / "raw"
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
    if args.delete_affected_gamezones:
        deletion_summary = delete_affected_gamezones(
            affected_gamezones=affected_gamezones,
            raw_root=raw_root,
            public_root=public_root,
            obfuscated_root=obfuscated_root,
            dry_run=bool(args.delete_dry_run),
        )
        report["deletion"] = deletion_summary

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
