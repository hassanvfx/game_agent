from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


RUN_ROOT = Path("/Volumes/HDD2026/output-May17th/run_game_remixer_20260517T132133Z/output")
EXPECTED_METADATA_FILES = {
    "Identity.json",
    "identity.json",
    "SemanticTags.json",
    "semantic_tags.json",
    "MechanicsClassification.json",
    "mechanics_classification.json",
    "MechanicsRanking.json",
    "mechanics_ranking.json",
}
EXPECTED_SCREENSHOT_DIRS = {"screenshots", "screenshot", "shots"}
DEPLOYER_SCREENSHOT_DIRS = {"screenshots"}
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}
LEGACY_SCREENSHOT_FILENAMES = {"playwright_initial.png", "playwright_after_start.png"}


def rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def find_game_dirs(root: Path) -> list[Path]:
    return sorted(
        path for path in root.iterdir() if path.is_dir() and path.name.startswith("gamezone-")
    )


def collect_md_candidates(game_dir: Path) -> list[str]:
    return sorted(rel(path, game_dir) for path in game_dir.rglob("*.md"))


def collect_top_level_images(game_dir: Path) -> list[str]:
    return sorted(
        path.name
        for path in game_dir.iterdir()
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES and not path.name.startswith("._")
    )


def collect_metadata_extractor_top_level_matches(game_dir: Path) -> list[str]:
    matches: list[str] = []
    for path in sorted(game_dir.iterdir()):
        if not path.is_file() or path.name.startswith("._") or path.suffix.lower() not in IMAGE_SUFFIXES:
            continue
        lower_name = path.name.lower()
        if lower_name.startswith("screens_") or "screenshot" in lower_name:
            matches.append(path.name)
    return matches


def collect_legacy_screenshot_matches(game_dir: Path) -> list[str]:
    matches: list[str] = []
    for path in sorted(game_dir.iterdir()):
        if not path.is_file() or path.name.startswith("._") or path.suffix.lower() != ".png":
            continue
        lower_name = path.name.lower()
        if lower_name in LEGACY_SCREENSHOT_FILENAMES:
            matches.append(path.name)
            continue
        if lower_name.startswith("playwright_after_") or lower_name.startswith("playwright_post_fix"):
            matches.append(path.name)
    return matches


def load_json_if_present(path: Path) -> dict | None:
    if not path.exists() or not path.is_file() or path.name.startswith("._"):
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return payload if isinstance(payload, dict) else None


def collect_image_dirs(game_dir: Path) -> dict[str, list[str]]:
    found: dict[str, list[str]] = {}
    for child in sorted(game_dir.iterdir()):
        if not child.is_dir() or child.name.startswith("."):
            continue
        images = [
            rel(path, game_dir)
            for path in sorted(child.rglob("*"))
            if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES and not path.name.startswith("._")
        ]
        if images:
            found[child.name] = images[:12]
    return found


def inspect_game_dir(game_dir: Path) -> dict:
    top_level_names = {path.name for path in game_dir.iterdir()}
    image_dirs = collect_image_dirs(game_dir)
    metadata_files_present = sorted(name for name in EXPECTED_METADATA_FILES if name in top_level_names)
    identity_payload = load_json_if_present(game_dir / "Identity.json") or load_json_if_present(game_dir / "identity.json") or {}
    md_candidates = collect_md_candidates(game_dir)
    recreation_like = [name for name in md_candidates if Path(name).name.lower().startswith(("recreation", "prompt"))]
    blueprint_like = [name for name in md_candidates if Path(name).name.lower().startswith("blueprint")]
    top_level_images = collect_top_level_images(game_dir)
    metadata_extractor_top_level_matches = collect_metadata_extractor_top_level_matches(game_dir)
    legacy_screenshot_matches = collect_legacy_screenshot_matches(game_dir)
    all_image_dir_names = sorted(image_dirs.keys())
    expected_screenshot_dirs_present = sorted(name for name in all_image_dir_names if name in EXPECTED_SCREENSHOT_DIRS)
    deployer_screenshot_dirs_present = sorted(name for name in all_image_dir_names if name in DEPLOYER_SCREENSHOT_DIRS)
    png_total = sum(1 for path in game_dir.rglob("*") if path.is_file() and path.suffix.lower() == ".png")
    has_prompt_suffix = "__p" in game_dir.name

    return {
        "game_dir": str(game_dir),
        "game_dir_name": game_dir.name,
        "has_prompt_suffix_in_dir_name": has_prompt_suffix,
        "top_level_items_sample": sorted(top_level_names)[:25],
        "metadata_files_present": metadata_files_present,
        "identity_title": identity_payload.get("title"),
        "identity_game_id": identity_payload.get("game_id"),
        "markdown_files": md_candidates[:20],
        "recreation_like_markdown": recreation_like[:10],
        "blueprint_like_markdown": blueprint_like[:10],
        "top_level_images": top_level_images[:20],
        "metadata_extractor_top_level_matches": metadata_extractor_top_level_matches,
        "legacy_screenshot_matches": legacy_screenshot_matches,
        "image_dirs": image_dirs,
        "expected_screenshot_dirs_present": expected_screenshot_dirs_present,
        "deployer_screenshot_dirs_present": deployer_screenshot_dirs_present,
        "png_total": png_total,
        "would_metadata_extractor_find_screenshots": bool(
            expected_screenshot_dirs_present or metadata_extractor_top_level_matches or legacy_screenshot_matches
        ),
        "would_deployer_find_screenshots": bool(top_level_images or deployer_screenshot_dirs_present),
        "likely_title_source": (
            "identity"
            if any(name in {"Identity.json", "identity.json"} for name in metadata_files_present)
            else "fallback_game_id"
        ),
    }


def build_common_shape(games: list[dict]) -> dict:
    image_dir_counter: Counter[str] = Counter()
    metadata_counter: Counter[str] = Counter()
    top_level_image_presence = 0
    extractor_ok = 0
    deployer_ok = 0
    identity_ok = 0
    recreation_ok = 0
    blueprint_ok = 0
    prompt_suffix_count = 0
    extractor_miss_but_deployer_hit = 0

    for game in games:
        for name in game["image_dirs"].keys():
            image_dir_counter[name] += 1
        for name in game["metadata_files_present"]:
            metadata_counter[name] += 1
        if game["top_level_images"]:
            top_level_image_presence += 1
        if game["would_metadata_extractor_find_screenshots"]:
            extractor_ok += 1
        if game["would_deployer_find_screenshots"]:
            deployer_ok += 1
        if game["likely_title_source"] == "identity":
            identity_ok += 1
        if game["recreation_like_markdown"]:
            recreation_ok += 1
        if game["blueprint_like_markdown"]:
            blueprint_ok += 1
        if game["has_prompt_suffix_in_dir_name"]:
            prompt_suffix_count += 1
        if (not game["would_metadata_extractor_find_screenshots"]) and game["would_deployer_find_screenshots"]:
            extractor_miss_but_deployer_hit += 1

    total = len(games)
    return {
        "sample_size": total,
        "image_dir_frequency": dict(image_dir_counter),
        "metadata_file_frequency": dict(metadata_counter),
        "games_with_top_level_images": top_level_image_presence,
        "games_metadata_extractor_screenshot_compatible": extractor_ok,
        "games_deployer_screenshot_compatible": deployer_ok,
        "games_with_identity_json": identity_ok,
        "games_with_recreation_like_markdown": recreation_ok,
        "games_with_blueprint_like_markdown": blueprint_ok,
        "games_with_prompt_suffix_in_dir_name": prompt_suffix_count,
        "games_where_metadata_extractor_misses_but_deployer_still_finds_images": extractor_miss_but_deployer_hit,
    }


def main() -> None:
    if not RUN_ROOT.exists():
        raise SystemExit(json.dumps({"error": f"run root not found: {RUN_ROOT}"}, indent=2))

    game_dirs = find_game_dirs(RUN_ROOT)
    sample = game_dirs[:5]
    inspected = [inspect_game_dir(path) for path in sample]
    payload = {
        "run_root": str(RUN_ROOT),
        "total_game_dirs": len(game_dirs),
        "sampled_game_dirs": [str(path) for path in sample],
        "common_shape": build_common_shape(inspected),
        "expected_by_metadata_extractor": {
            "metadata_files": sorted(EXPECTED_METADATA_FILES),
            "screenshot_dirs": sorted(EXPECTED_SCREENSHOT_DIRS),
            "prompt_markdown_prefixes": ["recreation*", "prompt*"],
            "blueprint_markdown_prefixes": ["blueprint*"],
        },
        "expected_by_deployer": {
            "top_level_images": True,
            "screenshots_dir_only": sorted(DEPLOYER_SCREENSHOT_DIRS),
            "top_level_image_name_rule": "accepts any top-level image except index.html and dot-underscore files",
        },
        "sample_details": inspected,
    }
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()