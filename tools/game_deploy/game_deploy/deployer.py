from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .metadata_extractor import extract_game_metadata, load_json

TOOL_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = TOOL_ROOT.parents[1]
DEFAULT_GAMES_ROOT = REPO_ROOT / "games"
DEFAULT_PUBLISHED_ROOT = DEFAULT_GAMES_ROOT / "published" / "public"


@dataclass(frozen=True)
class DeployInput:
    source: Path


@dataclass(frozen=True)
class DeployResult:
    source: Path
    game_id: str
    remix_uuid: str
    deploy_dir: Path
    metadata_path: Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Convert game_refactoring outputs into deployable published remix bundles."
    )
    parser.add_argument(
        "--inputs",
        nargs="+",
        help="One or more refactoring output game directories.",
    )
    parser.add_argument(
        "--manifest",
        help="Optional JSON file containing an array of input directories or objects with a source/path field.",
    )
    parser.add_argument(
        "--published-root",
        default=str(DEFAULT_PUBLISHED_ROOT),
        help="Published output root. Defaults to games/published/public.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow overwriting an existing deploy target if the same remix UUID already exists.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the deploy plan without writing files.",
    )
    return parser


def resolve_input_paths(args: argparse.Namespace) -> list[DeployInput]:
    raw_inputs: list[str] = []

    if args.inputs:
        raw_inputs.extend(args.inputs)

    if args.manifest:
        payload = load_json(Path(args.manifest))
        if not isinstance(payload, list):
            raise ValueError("Manifest must be a JSON array")
        for item in payload:
            if isinstance(item, str):
                raw_inputs.append(item)
            elif isinstance(item, dict):
                source = item.get("source") or item.get("path") or item.get("output_dir")
                if not source:
                    raise ValueError("Manifest objects must include source, path, or output_dir")
                raw_inputs.append(str(source))
            else:
                raise ValueError("Manifest items must be strings or objects")

    if not raw_inputs:
        raise ValueError("Provide --inputs or --manifest")

    return [DeployInput(source=Path(value).resolve()) for value in raw_inputs]


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
        relative_path = path.relative_to(source_dir).as_posix().encode("utf-8")
        digest.update(relative_path)
        digest.update(b"\0")
        digest.update(sha256_for_file(path).encode("utf-8"))
        digest.update(b"\0")
    return digest.hexdigest()


def copy_assets_filtered(source_assets_dir: Path, target_assets_dir: Path) -> None:
    keep_suffixes = {".js", ".css", ".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg", ".woff", ".woff2", ".ttf", ".otf", ".mp3", ".wav", ".ogg", ".m4a"}
    for path in sorted(source_assets_dir.rglob("*")):
        if path.is_dir():
            continue
        if path.suffix.lower() not in keep_suffixes:
            continue
        relative = path.relative_to(source_assets_dir)
        destination = target_assets_dir / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, destination)


def deploy_one(source: Path, published_root: Path, overwrite: bool, dry_run: bool) -> DeployResult:
    if not source.exists() or not source.is_dir():
        raise FileNotFoundError(f"Deploy source directory not found: {source}")

    remix_uuid = compute_folder_content_hash(source)[:32]
    extracted = extract_game_metadata(source_dir=source, remix_uuid=remix_uuid, repo_root=REPO_ROOT)
    game_id = extracted.game_id
    deploy_dir = published_root / game_id / f"remix-{remix_uuid}"
    metadata_path = deploy_dir / f"game-obfuscated-{remix_uuid}.json"

    index_path = extracted.index_path
    assets_dir = extracted.assets_dir
    screenshot_files = extracted.screenshot_files
    metadata_payload = extracted.metadata_payload

    if dry_run:
        return DeployResult(
            source=source,
            game_id=game_id,
            remix_uuid=remix_uuid,
            deploy_dir=deploy_dir,
            metadata_path=metadata_path,
        )

    if deploy_dir.exists():
        if not overwrite:
            raise FileExistsError(f"Deploy destination already exists: {deploy_dir}")
        shutil.rmtree(deploy_dir)

    deploy_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(index_path, deploy_dir / "index.html")

    target_assets_dir = deploy_dir / "assets"
    if assets_dir:
        target_assets_dir.mkdir(parents=True, exist_ok=True)
        copy_assets_filtered(assets_dir, target_assets_dir)

    screenshots_dir = deploy_dir / "screenshots"
    screenshots_dir.mkdir(parents=True, exist_ok=True)
    for idx, path in enumerate(screenshot_files, start=1):
        destination = screenshots_dir / f"{idx:02d}{path.suffix.lower()}"
        shutil.copy2(path, destination)

    metadata_path.write_text(json.dumps(metadata_payload, indent=2) + "\n", encoding="utf-8")

    return DeployResult(
        source=source,
        game_id=game_id,
        remix_uuid=remix_uuid,
        deploy_dir=deploy_dir,
        metadata_path=metadata_path,
    )


def run_deploy(args: argparse.Namespace) -> int:
    published_root = Path(args.published_root).resolve()
    inputs = resolve_input_paths(args)
    results: list[dict[str, Any]] = []

    for deploy_input in inputs:
        result = deploy_one(
            source=deploy_input.source,
            published_root=published_root,
            overwrite=args.overwrite,
            dry_run=args.dry_run,
        )
        results.append(
            {
                "source": str(result.source),
                "game_id": result.game_id,
                "remix_uuid": result.remix_uuid,
                "deploy_dir": str(result.deploy_dir),
                "metadata_path": str(result.metadata_path),
            }
        )

    print(json.dumps({"results": results}, indent=2))
    return 0