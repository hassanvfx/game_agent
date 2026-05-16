from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ExtractedGameMetadata:
    source_dir: Path
    run_id: str | None
    game_id: str
    remix_id: str
    remix_parent_id: str | None
    root_game_id: str
    lineage_depth: int
    reference_json: dict[str, Any] | None
    index_path: Path
    assets_dir: Path | None
    screenshot_files: list[Path]
    screenshot_relpaths_png: list[str]
    screenshot_relpaths_jpg: list[str]
    metadata_payload: dict[str, Any]


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_optional_json(path: Path) -> dict[str, Any] | list[Any] | None:
    if not path.exists() or path.name.startswith("._"):
        return None
    try:
        payload = load_json(path)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None
    return payload


def reference_json_score(payload: dict[str, Any]) -> int:
    score = 0
    if payload.get("game_id"):
        score += 10
    if payload.get("semantic_tags"):
        score += 5
    if payload.get("identity"):
        score += 5
    if payload.get("mechanics_classification"):
        score += 5
    if payload.get("recreation_prompt_markdown"):
        score += 2
    if payload.get("blueprint_markdown"):
        score += 2
    if payload.get("screenshots_png"):
        score += 1
    if payload.get("screenshots_jpg"):
        score += 1
    return score


def dedupe_paths(paths: list[Path]) -> list[Path]:
    seen: set[str] = set()
    unique_paths: list[Path] = []
    for path in paths:
        resolved = str(path.resolve())
        if resolved in seen:
            continue
        seen.add(resolved)
        unique_paths.append(path)
    return unique_paths


def find_run_layout_screenshot_files(source_dir: Path) -> list[Path]:
    screenshots: list[Path] = []
    image_suffixes = {".png", ".jpg", ".jpeg", ".webp"}

    for folder_name in ["screenshots", "screenshot", "shots"]:
        folder = source_dir / folder_name
        if folder.exists() and folder.is_dir():
            for path in sorted(folder.rglob("*")):
                if path.is_file() and path.suffix.lower() in image_suffixes and not path.name.startswith("._"):
                    screenshots.append(path)

    for path in sorted(source_dir.iterdir()):
        if not path.is_file() or path.name.startswith("._") or path.suffix.lower() not in image_suffixes:
            continue
        lower_name = path.name.lower()
        if lower_name.startswith("screens_") or "screenshot" in lower_name:
            screenshots.append(path)

    return dedupe_paths(screenshots)


def find_legacy_layout_screenshot_files(source_dir: Path) -> list[Path]:
    screenshots: list[Path] = []
    for path in sorted(source_dir.iterdir()):
        if not path.is_file() or path.name.startswith("._") or path.suffix.lower() != ".png":
            continue
        lower_name = path.name.lower()
        if lower_name == "playwright_initial.png" or lower_name == "playwright_after_start.png":
            screenshots.append(path)
            continue
        if lower_name.startswith("playwright_after_") or lower_name.startswith("playwright_post_fix"):
            screenshots.append(path)
    return dedupe_paths(screenshots)


def find_screenshot_files(source_dir: Path) -> list[Path]:
    screenshots = find_run_layout_screenshot_files(source_dir)
    if screenshots:
        return screenshots
    return find_legacy_layout_screenshot_files(source_dir)


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


def load_first_optional_json(source_dir: Path, candidate_names: list[str]) -> dict[str, Any] | list[Any] | None:
    for name in candidate_names:
        payload = load_optional_json(source_dir / name)
        if payload is not None:
            return payload
    return None


def classify_source_layout(source_dir: Path) -> str:
    if (source_dir / "semantic_tags.json").exists() or (source_dir / "mechanics_classification.json").exists():
        return "legacy"
    return "run"


def build_screenshot_relpaths(screenshots: list[Path]) -> tuple[list[str], list[str]]:
    screenshots_png: list[str] = []
    screenshots_jpg: list[str] = []
    for idx, path in enumerate(screenshots, start=1):
        ext = path.suffix.lower()
        rel = f"screenshots/{idx:02d}{ext}"
        if ext == ".png":
            screenshots_png.append(rel)
        elif ext in {".jpg", ".jpeg"}:
            screenshots_jpg.append(rel)
    return screenshots_png, screenshots_jpg


def build_split_reference_json(source_dir: Path, game_id: str, *, layout: str | None = None) -> dict[str, Any] | None:
    resolved_layout = layout or classify_source_layout(source_dir)

    if resolved_layout == "legacy":
        identity_payload = load_first_optional_json(source_dir, ["Identity.json", "identity.json"])
        semantic_payload = load_first_optional_json(source_dir, ["semantic_tags.json", "SemanticTags.json"])
        mechanics_payload = load_first_optional_json(
            source_dir,
            [
                "mechanics_classification.json",
                "MechanicsClassification.json",
                "mechanics_ranking.json",
                "MechanicsRanking.json",
                "MechanicsRationale.json",
                "mechanics_rationale.json",
                "mechanics_ranking_reasoning.json",
            ],
        )
        screenshots = find_legacy_layout_screenshot_files(source_dir)
        source_mode = "split-json-legacy"
    else:
        identity_payload = load_first_optional_json(source_dir, ["Identity.json", "identity.json"])
        semantic_payload = load_first_optional_json(source_dir, ["SemanticTags.json", "semantic_tags.json"])
        mechanics_payload = load_first_optional_json(
            source_dir,
            [
                "MechanicsClassification.json",
                "mechanics_classification.json",
                "MechanicsRanking.json",
                "mechanics_ranking.json",
                "MechanicsRationale.json",
                "mechanics_rationale.json",
                "mechanics_ranking_reasoning.json",
            ],
        )
        screenshots = find_run_layout_screenshot_files(source_dir)
        source_mode = "split-json"

    recreation_prompt_markdown = collect_markdown_text(source_dir, ["recreation", "prompt"])
    blueprint_markdown = collect_markdown_text(source_dir, ["blueprint"])
    screenshots_png, screenshots_jpg = build_screenshot_relpaths(screenshots)

    has_any_structured = any(
        isinstance(payload, dict) and payload
        for payload in [identity_payload, semantic_payload, mechanics_payload]
    ) or bool(recreation_prompt_markdown) or bool(blueprint_markdown)

    if not has_any_structured:
        return None

    return {
        "game_id": game_id,
        "recreation_prompt_markdown": recreation_prompt_markdown or "",
        "blueprint_markdown": blueprint_markdown or "",
        "semantic_tags": semantic_payload if isinstance(semantic_payload, dict) else {},
        "semantic_tags_source_mode": source_mode if isinstance(semantic_payload, dict) else "unknown",
        "identity": identity_payload if isinstance(identity_payload, dict) else {},
        "identity_source_mode": source_mode if isinstance(identity_payload, dict) else "unknown",
        "mechanics_classification": mechanics_payload if isinstance(mechanics_payload, dict) else {},
        "mechanics_classification_source_mode": source_mode if isinstance(mechanics_payload, dict) else "unknown",
        "screenshots_png": screenshots_png,
        "screenshots_jpg": screenshots_jpg,
    }


def read_reference_public_json(source_dir: Path) -> dict[str, Any] | None:
    inferred_game_id = source_dir.name if source_dir.name.startswith("gamezone-") else None
    split_reference = build_split_reference_json(
        source_dir,
        inferred_game_id or "",
        layout=classify_source_layout(source_dir),
    )
    if split_reference and split_reference.get("game_id"):
        return split_reference

    best_payload: dict[str, Any] | None = None
    best_score = -1

    for path in sorted(source_dir.glob("*.json")):
        if path.name.startswith("._"):
            continue
        try:
            payload = load_json(path)
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        if not isinstance(payload, dict) or not payload.get("game_id"):
            continue

        score = reference_json_score(payload)
        if score > best_score:
            best_payload = payload
            best_score = score

    return best_payload


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
    run_id: str | None,
    game_id: str,
    remix_id: str,
    remix_parent_id: str | None,
    root_game_id: str,
    lineage_depth: int,
    reference_json: dict[str, Any] | None,
    screenshot_relpaths_png: list[str],
    screenshot_relpaths_jpg: list[str],
    source_output_dir: str,
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

    return {
        "game_id": game_id,
        "run_id": run_id,
        "remix_id": remix_id,
        "remix_parent_id": remix_parent_id,
        "root_game_id": root_game_id,
        "lineage_depth": lineage_depth,
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
            "remix_uuid": remix_id,
            "source_output_dir": source_output_dir,
            "format_version": "1.0.0",
        },
    }


def extract_game_metadata(
    *,
    source_dir: Path,
    remix_uuid: str,
    repo_root: Path | None = None,
) -> ExtractedGameMetadata:
    reference_json = read_reference_public_json(source_dir)
    game_id = infer_game_id(source_dir, reference_json)
    remix_id = f"remix-{remix_uuid}"
    run_id = None
    output_indices = [idx for idx, part in enumerate(source_dir.parts) if part == "output"]
    if output_indices:
        output_index = output_indices[-1]
        if output_index > 0:
            run_id = source_dir.parts[output_index - 1]
    remix_parent_id = None
    root_game_id = game_id
    lineage_depth = 0
    index_path = find_index_html(source_dir)
    assets_dir = find_assets_dir(index_path)
    screenshot_files = find_screenshot_files(source_dir)

    screenshot_relpaths_png, screenshot_relpaths_jpg = build_screenshot_relpaths(screenshot_files)

    if repo_root is not None:
        try:
            source_output_dir = source_dir.relative_to(repo_root).as_posix()
        except ValueError:
            source_output_dir = source_dir.name
    else:
        source_output_dir = source_dir.name

    metadata_payload = build_obfuscated_metadata(
        source_dir=source_dir,
        run_id=run_id,
        game_id=game_id,
        remix_id=remix_id,
        remix_parent_id=remix_parent_id,
        root_game_id=root_game_id,
        lineage_depth=lineage_depth,
        reference_json=reference_json,
        screenshot_relpaths_png=screenshot_relpaths_png,
        screenshot_relpaths_jpg=screenshot_relpaths_jpg,
        source_output_dir=source_output_dir,
    )

    return ExtractedGameMetadata(
        source_dir=source_dir,
        run_id=run_id,
        game_id=game_id,
        remix_id=remix_id,
        remix_parent_id=remix_parent_id,
        root_game_id=root_game_id,
        lineage_depth=lineage_depth,
        reference_json=reference_json,
        index_path=index_path,
        assets_dir=assets_dir,
        screenshot_files=screenshot_files,
        screenshot_relpaths_png=screenshot_relpaths_png,
        screenshot_relpaths_jpg=screenshot_relpaths_jpg,
        metadata_payload=metadata_payload,
    )
