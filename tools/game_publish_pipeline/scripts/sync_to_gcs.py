#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Collection

SCRIPT_PATH = Path(__file__).resolve()
TOOL_ROOT = SCRIPT_PATH.parents[1]
REPO_ROOT = TOOL_ROOT.parents[1]

DEFAULT_PUBLIC_ROOT = REPO_ROOT / "games" / "published" / "public"
DEFAULT_OBFUSCATED_ROOT = REPO_ROOT / "games" / "published" / "obfuscated"
DEFAULT_PUBLIC_GCS = "gs://friendjam-ios/games-prod/public"
DEFAULT_OBFUSCATED_GCS = "gs://friendjam-ios/games-prod/play"
DEFAULT_GCLOUD_PROJECT = "jabali-prod"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Sync published public/obfuscated game roots to Google Cloud Storage."
    )
    parser.add_argument(
        "--target",
        choices=("public", "obfuscated", "both"),
        default="both",
        help="Which published root to sync.",
    )
    parser.add_argument(
        "--mode",
        choices=("root", "per-item"),
        default="per-item",
        help="Sync the whole root at once or one top-level item at a time.",
    )
    parser.add_argument(
        "--public-root",
        default=str(DEFAULT_PUBLIC_ROOT),
        help="Local public publish root.",
    )
    parser.add_argument(
        "--obfuscated-root",
        default=str(DEFAULT_OBFUSCATED_ROOT),
        help="Local obfuscated publish root.",
    )
    parser.add_argument(
        "--public-gcs",
        default=DEFAULT_PUBLIC_GCS,
        help="Destination GCS path for the public root.",
    )
    parser.add_argument(
        "--obfuscated-gcs",
        default=DEFAULT_OBFUSCATED_GCS,
        help="Destination GCS path for the obfuscated root.",
    )
    parser.add_argument(
        "--project",
        default=DEFAULT_GCLOUD_PROJECT,
        help="Google Cloud project passed to gcloud storage rsync.",
    )
    parser.add_argument(
        "--only-item",
        action="append",
        default=[],
        help="Restrict per-item sync to specific top-level item names. Repeatable.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the gcloud commands without executing them.",
    )
    parser.add_argument(
        "--prune-remote",
        action="store_true",
        help="After per-item sync, remove stale remote gamezone prefixes so the destination mirrors local state.",
    )
    return parser


def normalize_gcs_root(destination: str) -> str:
    return destination.rstrip("/")


def build_rsync_command(source: Path, destination: str, project: str) -> list[str]:
    return [
        "gcloud",
        "storage",
        "rsync",
        "-r",
        str(source),
        normalize_gcs_root(destination),
        "--project",
        project,
    ]


def build_ls_command(destination: str, project: str) -> list[str]:
    return [
        "gcloud",
        "storage",
        "ls",
        "--recursive",
        f"{normalize_gcs_root(destination)}/**",
        "--project",
        project,
    ]


def build_rm_command(destination: str, item_name: str, project: str) -> list[str]:
    return [
        "gcloud",
        "storage",
        "rm",
        "--recursive",
        f"{normalize_gcs_root(destination)}/{item_name}",
        "--project",
        project,
    ]


def run_command(command: list[str]) -> dict[str, Any]:
    result = subprocess.run(command, capture_output=True, text=True)
    return {
        "command": command,
        "returncode": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
        "status": "passed" if result.returncode == 0 else "failed",
    }


def validate_source_root(path: Path, label: str) -> None:
    if not path.is_dir():
        raise SystemExit(f"{label} source root does not exist or is not a directory: {path}")


def iter_top_level_items(root: Path, only_items: set[str]) -> list[Path]:
    items = [
        path
        for path in sorted(root.iterdir())
        if path.is_dir() and path.name.startswith("gamezone-")
    ]
    if only_items:
        items = [path for path in items if path.name in only_items]
        missing = sorted(only_items - {path.name for path in items})
        if missing:
            raise SystemExit(
                f"Requested gamezone item(s) not found under {root}: {', '.join(missing)}"
            )
    if not items:
        raise SystemExit(f"No top-level gamezone directories found to sync under: {root}")
    return items


def local_item_names(root: Path, only_items: set[str]) -> list[str]:
    return [path.name for path in iter_top_level_items(root, only_items)]


def parse_remote_item_names(stdout: str, destination_root: str) -> list[str]:
    normalized_root = normalize_gcs_root(destination_root)
    prefix = f"{normalized_root}/"
    item_names: set[str] = set()

    for raw_line in stdout.splitlines():
        candidate = raw_line.strip()
        if not candidate:
            continue
        candidate = candidate.rstrip("/")
        if not candidate.startswith(prefix):
            continue
        relative = candidate[len(prefix) :].strip("/")
        if not relative:
            continue
        item_name = relative.split("/", 1)[0]
        if item_name.startswith("gamezone-"):
            item_names.add(item_name)

    return sorted(item_names)


def list_remote_item_names(destination_root: str, project: str) -> list[str]:
    result = run_command(build_ls_command(destination_root, project))
    if result["returncode"] != 0:
        if result["stdout"]:
            print(result["stdout"])
        if result["stderr"]:
            print(result["stderr"], file=sys.stderr)
        raise SystemExit(result["returncode"])
    return parse_remote_item_names(result["stdout"], destination_root)


def build_root_operation(target: str, source_root: Path, destination_root: str, project: str) -> dict[str, Any]:
    return {
        "operation_kind": "sync",
        "target": target,
        "item_name": None,
        "source": str(source_root),
        "destination": destination_root,
        "command": build_rsync_command(source_root, destination_root, project),
    }


def build_per_item_operations(
    target: str,
    source_root: Path,
    destination_root: str,
    project: str,
    only_items: set[str],
) -> list[dict[str, Any]]:
    operations: list[dict[str, Any]] = []
    for item_path in iter_top_level_items(source_root, only_items):
        destination = f"{destination_root.rstrip('/')}/{item_path.name}"
        operations.append(
            {
                "operation_kind": "sync",
                "target": target,
                "item_name": item_path.name,
                "source": str(item_path),
                "destination": destination,
                "command": build_rsync_command(item_path, destination, project),
            }
        )
    return operations


def build_operations_for_target(
    *,
    target: str,
    source_root: Path,
    destination_root: str,
    project: str,
    mode: str,
    only_items: set[str],
) -> list[dict[str, Any]]:
    if mode == "root":
        return [build_root_operation(target, source_root, destination_root, project)]
    return build_per_item_operations(target, source_root, destination_root, project, only_items)


def build_prune_operations_from_item_names(
    *,
    target: str,
    destination_root: str,
    project: str,
    local_names: Collection[str],
    remote_names: Collection[str],
) -> list[dict[str, Any]]:
    stale_remote_names = sorted(set(remote_names) - set(local_names))
    operations: list[dict[str, Any]] = []
    for item_name in stale_remote_names:
        operations.append(
            {
                "operation_kind": "prune",
                "target": target,
                "item_name": item_name,
                "source": None,
                "destination": f"{normalize_gcs_root(destination_root)}/{item_name}",
                "command": build_rm_command(destination_root, item_name, project),
            }
        )
    return operations


def build_prune_operations_for_target(
    *,
    target: str,
    source_root: Path,
    destination_root: str,
    project: str,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    local_names = local_item_names(source_root, set())
    remote_names = list_remote_item_names(destination_root, project)
    operations = build_prune_operations_from_item_names(
        target=target,
        destination_root=destination_root,
        project=project,
        local_names=local_names,
        remote_names=remote_names,
    )
    return operations, {
        "target": target,
        "local_item_names": local_names,
        "remote_item_names": remote_names,
        "stale_remote_item_names": [operation["item_name"] for operation in operations],
    }


def print_stage_banner(title: str) -> None:
    print(f"[sync] {title}", flush=True)


def print_operation_progress(index: int, total: int, operation: dict[str, Any], dry_run: bool) -> None:
    operation_kind = operation.get("operation_kind") or "sync"
    target = operation["target"]
    item_name = operation["item_name"] or "<root>"
    source = operation.get("source")
    destination = operation["destination"]
    mode_label = "dry-run" if dry_run else "run"
    if source:
        print(
            f"[sync] [{index}/{total}] {target} :: {item_name} :: {operation_kind} :: {mode_label}\n"
            f"[sync]         source: {source}\n"
            f"[sync]         destination: {destination}",
            flush=True,
        )
    else:
        print(
            f"[sync] [{index}/{total}] {target} :: {item_name} :: {operation_kind} :: {mode_label}\n"
            f"[sync]         destination: {destination}",
            flush=True,
        )
    print(f"[sync]         command: {' '.join(operation['command'])}", flush=True)


def main() -> None:
    args = build_parser().parse_args()

    public_root = Path(args.public_root).resolve()
    obfuscated_root = Path(args.obfuscated_root).resolve()
    only_items = {item for item in args.only_item if item}

    if args.prune_remote and args.mode != "per-item":
        raise SystemExit("--prune-remote currently requires --mode per-item.")
    if args.prune_remote and only_items:
        raise SystemExit("--prune-remote cannot be combined with --only-item.")

    operations: list[dict[str, Any]] = []
    prune_plans: list[dict[str, Any]] = []

    print_stage_banner(f"starting sync planning target={args.target} mode={args.mode} project={args.project}")

    if args.target in {"public", "both"}:
        validate_source_root(public_root, "public")
        public_ops = build_operations_for_target(
            target="public",
            source_root=public_root,
            destination_root=str(args.public_gcs),
            project=str(args.project),
            mode=str(args.mode),
            only_items=only_items,
        )
        print_stage_banner(f"planned public operations: {len(public_ops)}")
        operations.extend(public_ops)
        if args.prune_remote:
            public_prune_ops, public_prune_plan = build_prune_operations_for_target(
                target="public",
                source_root=public_root,
                destination_root=str(args.public_gcs),
                project=str(args.project),
            )
            print_stage_banner(f"planned public prune operations: {len(public_prune_ops)}")
            operations.extend(public_prune_ops)
            prune_plans.append(public_prune_plan)

    if args.target in {"obfuscated", "both"}:
        validate_source_root(obfuscated_root, "obfuscated")
        obfuscated_ops = build_operations_for_target(
            target="obfuscated",
            source_root=obfuscated_root,
            destination_root=str(args.obfuscated_gcs),
            project=str(args.project),
            mode=str(args.mode),
            only_items=only_items,
        )
        print_stage_banner(f"planned obfuscated operations: {len(obfuscated_ops)}")
        operations.extend(obfuscated_ops)
        if args.prune_remote:
            obfuscated_prune_ops, obfuscated_prune_plan = build_prune_operations_for_target(
                target="obfuscated",
                source_root=obfuscated_root,
                destination_root=str(args.obfuscated_gcs),
                project=str(args.project),
            )
            print_stage_banner(f"planned obfuscated prune operations: {len(obfuscated_prune_ops)}")
            operations.extend(obfuscated_prune_ops)
            prune_plans.append(obfuscated_prune_plan)

    print_stage_banner(f"total operations queued: {len(operations)}")

    results: list[dict[str, Any]] = []
    total = len(operations)

    for index, operation in enumerate(operations, start=1):
        command = operation["command"]
        print_operation_progress(index, total, operation, args.dry_run)

        if args.dry_run:
            results.append(
                {
                    "operation_kind": operation.get("operation_kind") or "sync",
                    "target": operation["target"],
                    "item_name": operation["item_name"],
                    "source": operation["source"],
                    "destination": operation["destination"],
                    "command": command,
                    "status": "dry_run",
                }
            )
            continue

        result = run_command(command)
        results.append(
            {
                "operation_kind": operation.get("operation_kind") or "sync",
                "target": operation["target"],
                "item_name": operation["item_name"],
                "source": operation["source"],
                "destination": operation["destination"],
                **result,
            }
        )
        if result["returncode"] != 0:
            if result["stdout"]:
                print(result["stdout"])
            if result["stderr"]:
                print(result["stderr"], file=sys.stderr)
            raise SystemExit(result["returncode"])
        print(f"[sync] [{index}/{total}] completed", flush=True)

    summary = {
        "target": args.target,
        "mode": args.mode,
        "project": str(args.project),
        "dry_run": bool(args.dry_run),
        "prune_remote": bool(args.prune_remote),
        "only_items": sorted(only_items),
        "operation_count": len(results),
        "sync_operation_count": sum(1 for result in results if result.get("operation_kind") == "sync"),
        "prune_operation_count": sum(1 for result in results if result.get("operation_kind") == "prune"),
        "status": "dry_run" if args.dry_run else "passed",
    }

    print_stage_banner("sync summary")
    print(
        json.dumps(
            {
                "results": results,
                "prune_plans": prune_plans,
                "summary": summary,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()