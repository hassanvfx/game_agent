from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

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


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


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


def read_reference_public_json(source_dir: Path) -> dict[str, Any] | None:
    for path in sorted(source_dir.glob("*.json")):
        try:
            payload = load_json(path)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict) and payload.get("game_id"):
            return payload
    return None


def infer_game_id(source_dir: Path, reference_json: dict[str, Any] | None) -> str:
    if reference_json and isinstance(reference_json.get("game_id"), str):
        return reference_json["game_id"]

    if source_dir.name.startswith("gamezone-"):
        return source_dir.name

    for candidate in [source_dir, *source_dir.parents[:3]]:
        if candidate.name.startswith("gamezone-"):
            return candidate.name

    raise ValueError(f"Unable to infer game_id from {source_dir}")


def find_index_html(source_dir: Path) -> Path:
    direct = source_dir / "index.html"
    if direct.exists():
        return direct
    matches = sorted(source_dir.rglob("index.html"))
    if not matches:
        raise FileNotFoundError(f"No index.html found under {source_dir}")
    return matches[0]


def find_assets_dir(index_path: Path) -> Path | None:
    direct = index_path.parent / "assets"
    if direct.exists() and direct.is_dir():
        return direct
    return None


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


def find_screenshot_files(source_dir: Path) -> list[Path]:
    screenshots: list[Path] = []
    for folder_name in ["screenshots", "screenshot", "shots"]:
        folder = source_dir / folder_name
        if folder.exists() and folder.is_dir():
            for path in sorted(folder.rglob("*")):
                if path.is_file() and path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}:
                    screenshots.append(path)
    if screenshots:
        return screenshots

    for path in sorted(source_dir.rglob("*")):
        if path.is_file() and path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"} and "screenshot" in path.name.lower():
            screenshots.append(path)
    return screenshots


def collect_markdown_text(source_dir: Path, preferred_name_prefixes: list[str]) -> str | None:
    preferred: list[Path] = []
    fallback: list[Path] = []
    for path in sorted(source_dir.rglob("*.md")):
        name = path.name.lower()
        if any(name.startswith(prefix) for prefix in preferred_name_prefixes):
            preferred.append(path)
        else:
            fallback.append(path)
    selected = preferred[0] if preferred else (fallback[0] if fallback else None)
    if not selected:
        return None
    return selected.read_text(encoding="utf-8")


def collect_semantic_tags(reference_json: dict[str, Any] | None) -> tuple[dict[str, Any], str]:
    if reference_json and isinstance(reference_json.get("semantic_tags"), dict):
        return reference_json["semantic_tags"], str(reference_json.get("semantic_tags_source_mode") or "json")
    return {}, "unknown"


def collect_identity(reference_json: dict[str, Any] | None) -> tuple[dict[str, Any], str]:
    if reference_json and isinstance(reference_json.get("identity"), dict):
        return reference_json["identity"], str(reference_json.get("identity_source_mode") or "json")
    return {}, "unknown"


def collect_mechanics_classification(reference_json: dict[str, Any] | None) -> tuple[dict[str, Any], str]:
    if reference_json and isinstance(reference_json.get("mechanics_classification"), dict):
        return reference_json["mechanics_classification"], str(
            reference_json.get("mechanics_classification_source_mode") or "json"
        )
    return {}, "unknown"


def build_obfuscated_metadata(
    *,
    source_dir: Path,
    game_id: str,
    remix_uuid: str,
    reference_json: dict[str, Any] | None,
    screenshot_relpaths_png: list[str],
    screenshot_relpaths_jpg: list[str],
) -> dict[str, Any]:
    recreation_prompt_markdown = None
    blueprint_markdown = None

    if reference_json:
        recreation_prompt_markdown = reference_json.get("recreation_prompt_markdown")
        blueprint_markdown = reference_json.get("blueprint_markdown")

    if not recreation_prompt_markdown:
        recreation_prompt_markdown = collect_markdown_text(source_dir, ["recreation", "prompt"])
    if not blueprint_markdown:
        blueprint_markdown = collect_markdown_text(source_dir, ["blueprint"])

    semantic_tags, semantic_tags_source_mode = collect_semantic_tags(reference_json)
    identity, identity_source_mode = collect_identity(reference_json)
    mechanics_classification, mechanics_classification_source_mode = collect_mechanics_classification(reference_json)

    try:
        source_output_dir = source_dir.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        source_output_dir = source_dir.name

    payload = {
        "game_id": game_id,
        "aggregated_at": utc_now(),
        "recreation_prompt_markdown": recreation_prompt_markdown or "",
        "blueprint_markdown": blueprint_markdown or "",
        "semantic_tags": semantic_tags,
        "semantic_tags_source_mode": semantic_tags_source_mode,
        "identity": identity,
        "identity_source_mode": identity_source_mode,
        "mechanics_classification": mechanics_classification,
        "mechanics_classification_source_mode": mechanics_classification_source_mode,
        "screenshots_png": screenshot_relpaths_png,
        "screenshots_jpg": screenshot_relpaths_jpg,
        "deploy": {
            "remix_uuid": remix_uuid,
            "source_output_dir": source_output_dir,
            "format_version": "1.0.0",
        },
    }
    return payload


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

    reference_json = read_reference_public_json(source)
    game_id = infer_game_id(source, reference_json)
    remix_uuid = compute_folder_content_hash(source)[:32]
    deploy_dir = published_root / game_id / f"remix-{remix_uuid}"
    metadata_path = deploy_dir / f"game-obfuscated-{remix_uuid}.json"

    index_path = find_index_html(source)
    assets_dir = find_assets_dir(index_path)
    screenshot_files = find_screenshot_files(source)

    screenshot_relpaths_png: list[str] = []
    screenshot_relpaths_jpg: list[str] = []
    for idx, path in enumerate(screenshot_files, start=1):
        ext = path.suffix.lower()
        rel = f"screenshots/{idx:02d}{ext}"
        if ext == ".png":
            screenshot_relpaths_png.append(rel)
        elif ext in {".jpg", ".jpeg"}:
            screenshot_relpaths_jpg.append(rel)

    metadata_payload = build_obfuscated_metadata(
        source_dir=source,
        game_id=game_id,
        remix_uuid=remix_uuid,
        reference_json=reference_json,
        screenshot_relpaths_png=screenshot_relpaths_png,
        screenshot_relpaths_jpg=screenshot_relpaths_jpg,
    )

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