#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

CATALOG_PATH = Path("JabaliApp/Assets/app.json")
BLUEPRINT_PATH = Path("tmp/editorial_phase2_blueprint.json")
OUT_PATH = Path("tmp/editorial_phase3_candidates.json")
IMAGE_BASE_URL = "https://friendjam-game-assets.jabali.ai/games-prod/play/"
VISIBLE_PAGE_COUNT = 2
MAX_IMAGE_RETRIES = 3
MAX_THEME_PER_BUNDLE = 1
MIN_SCORE_FLOOR = 6.0

TAG_FIELDS = [
    "mechanic_tags",
    "semantic_tags",
    "mood_tags",
    "setting_tags",
    "character_tags",
    "games_tags",
    "franchise_tags",
]

MECHANIC_HINTS = {
    "runner": ["runner", "lane", "reflex", "dodge", "sprint", "endless"],
    "portal": ["portal", "science", "multiverse", "warp"],
    "chaos": ["chaos", "chaotic", "absurd", "mess", "meme"],
    "puzzle": ["puzzle", "logic", "match", "signal", "sort", "quiz"],
    "cozy": ["cozy", "calm", "soft", "relaxing", "care", "gentle"],
    "clicker": ["clicker", "tap", "idle", "money", "cash", "merge", "tycoon"],
    "magic": ["magic", "wizard", "spell", "wand", "potion", "arcane"],
    "shooter": ["shooter", "arena", "blast", "gallery", "space"],
    "survival": ["survival", "avoid", "endure", "escape", "zombie"],
    "build": ["build", "builder", "sandbox", "craft", "resource", "system"],
    "style": ["style", "fashion", "dress", "makeover", "romance"],
    "pets": ["pet", "creature", "cat", "animal", "care", "mascot"],
    "race": ["race", "racing", "car", "drive", "route", "taxi"],
    "neon": ["neon", "arcade", "glow", "bright", "sci-fi"],
    "pets-chaos": ["pet", "creature", "chaos", "chaotic", "cute", "absurd"],
}

THEME_SYNONYMS = {
    "runner": ["reflex", "dodge", "sprint", "lane", "speed", "escape"],
    "portal": ["multiverse", "rift", "warp", "science", "dimension"],
    "chaos": ["absurd", "meme", "wild", "mess", "disruption"],
    "puzzle": ["brain", "logic", "sort", "signal", "pattern"],
    "cozy": ["unwind", "soft", "gentle", "bedtime", "comfort"],
    "clicker": ["tap", "idle", "money", "tycoon", "merge"],
    "magic": ["wizard", "spell", "arcane", "wand", "fantasy"],
    "shooter": ["blast", "arena", "gallery", "space", "alien"],
    "survival": ["endure", "avoid", "last", "danger", "fog"],
    "build": ["builder", "sandbox", "craft", "toy systems", "resource"],
    "style": ["fashion", "makeover", "dress", "drama", "romance"],
    "pets": ["creatures", "companions", "animals", "mascots", "care"],
    "race": ["racing", "driving", "engines", "speedway", "route"],
    "neon": ["arcade", "glow", "cyber", "bright", "electric"],
    "pets-chaos": ["weird pets", "creature chaos", "cute mess", "playful absurdity"],
}

SUBGROUP_HINTS = {
    "neon runner": ["neon", "runner"],
    "lane runner": ["lane", "runner"],
    "void runner": ["void", "runner"],
    "speed runner": ["speed", "runner"],
    "character runner": ["runner", "character"],
    "multiverse comedy": ["multiverse", "portal", "rick", "morty"],
    "portal chase": ["portal", "chase"],
    "portal collapse": ["portal", "collapse"],
    "portal science": ["portal", "science"],
    "sci-fi portal worlds": ["portal", "sci-fi", "science"],
    "brainrot meme": ["brainrot", "meme"],
    "absurd comedy": ["absurd", "chaotic", "comedy"],
    "chaotic arcade": ["chaotic", "arcade"],
    "silly disruption": ["silly", "chaotic"],
    "readable chaos": ["chaotic", "readable"],
    "physics puzzle": ["physics", "puzzle"],
    "memory puzzle": ["memory", "puzzle"],
    "word puzzle": ["word", "quiz", "puzzle"],
    "match puzzle": ["match", "bubble", "puzzle"],
    "quiz puzzle": ["quiz", "puzzle"],
    "asmr relaxing": ["asmr", "relaxing", "cozy"],
    "soft toy play": ["soft", "toy", "cute"],
    "calm care": ["calm", "care", "cozy"],
    "gentle comfort": ["gentle", "comfort", "cozy"],
    "cozy builder": ["cozy", "builder"],
    "money clicker": ["clicker", "money", "cash"],
    "cash clicker": ["cash", "clicker"],
    "idle clicker": ["clicker", "idle"],
    "mascot clicker": ["clicker", "mascot", "cute"],
    "toy clicker": ["clicker", "toy"],
    "wizard school": ["wizard", "school", "magic"],
    "spell practice": ["spell", "magic"],
    "magic exam": ["magic", "exam", "wizard"],
    "fantasy lessons": ["fantasy", "magic", "wizard"],
    "apprentice journey": ["apprentice", "wizard", "magic"],
    "alien shooter": ["alien", "shooter"],
    "space shooter": ["space", "shooter"],
    "bubble shooter": ["bubble", "shooter"],
    "arena shooter": ["arena", "shooter"],
    "gallery shooter": ["gallery", "shooter", "arcade"],
    "arcade survival": ["arcade", "survival"],
    "zombie survival": ["zombie", "survival"],
    "arena survival": ["arena", "survival"],
    "score survival": ["survival", "score"],
    "avoidance survival": ["avoidance", "survival"],
    "sandbox building": ["sandbox", "building", "builder"],
    "resource management": ["resource", "management"],
    "inventory builder": ["inventory", "builder"],
    "base building": ["base", "building", "builder"],
    "toy systems": ["toy", "system", "builder"],
    "dress up": ["dress", "fashion", "style"],
    "makeover": ["makeover", "fashion", "style"],
    "fashion fantasy": ["fashion", "fantasy", "dress"],
    "romance expression": ["romance", "style", "fashion"],
    "paper doll play": ["dress", "doll", "fashion"],
    "pet simulator": ["pet", "simulator"],
    "cat companion": ["cat", "pet"],
    "animal charm": ["animal", "pet", "cute"],
    "tiny creature care": ["creature", "care", "pet"],
    "mascot affection": ["mascot", "cute", "pet"],
    "taxi rush": ["taxi", "rush", "car"],
    "car simulator": ["car", "simulator", "racing"],
    "route racing": ["route", "racing", "car"],
    "pickup urgency": ["pickup", "taxi", "rush"],
    "arcade driving": ["driving", "racing", "arcade"],
    "neon arcade": ["neon", "arcade"],
    "neon sci-fi": ["neon", "sci-fi"],
    "bright neon": ["bright", "neon"],
    "neon puzzle": ["neon", "puzzle"],
    "neon arena": ["neon", "arena"],
    "cute chaos": ["cute", "chaotic"],
    "pet chaos": ["pet", "chaotic"],
    "whimsical mess": ["whimsical", "chaotic"],
    "toy disorder": ["toy", "chaotic"],
    "playful absurdity": ["playful", "absurd"],
}


def slugify(text: str) -> str:
    return text.lower().replace(" ", "-").replace("_", "-")


def build_haystack(item: dict[str, object]) -> str:
    parts: list[str] = []
    for key in ["title", "description", "prompt", "blueprint"]:
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            parts.append(value.lower())

    for field in TAG_FIELDS:
        values = item.get(field)
        if isinstance(values, list):
            parts.extend(str(value).lower() for value in values if str(value).strip())

    return " || ".join(parts)


def classify_token_families(item: dict[str, object]) -> dict[str, set[str]]:
    families: dict[str, set[str]] = {
        "theme": set(),
        "mechanic": set(),
        "mood": set(),
        "semantic": set(),
    }

    lower_values: list[str] = []
    for key in ["title", "description", "prompt"]:
        value = item.get(key)
        if isinstance(value, str):
            lower_values.append(value.lower())

    for field in TAG_FIELDS:
        values = item.get(field)
        if isinstance(values, list):
            lower_values.extend(str(value).lower() for value in values)

    blob = " || ".join(lower_values)

    for theme, hints in MECHANIC_HINTS.items():
        if any(hint in blob for hint in hints):
            families["theme"].add(theme)

    for tag in item.get("mechanic_tags", []) or []:
        families["mechanic"].add(slugify(str(tag)))
    for tag in item.get("mood_tags", []) or []:
        families["mood"].add(slugify(str(tag)))
    for field in ["semantic_tags", "setting_tags", "character_tags", "games_tags", "franchise_tags"]:
        for tag in item.get(field, []) or []:
            families["semantic"].add(slugify(str(tag)))

    return families


def screenshot_urls(item: dict[str, Any], image_base_url: str) -> list[str]:
    urls: list[str] = []
    screenshots = item.get("screenshots")
    if not isinstance(screenshots, list):
        return urls

    for value in screenshots:
        if not isinstance(value, str) or not value.strip():
            continue
        relative_path = value.lstrip("/")
        urls.append(f"{image_base_url}{relative_path}")
    return urls


def curl_url_exists(url: str) -> bool:
    for attempt in range(MAX_IMAGE_RETRIES):
        command = [
            "curl",
            "--silent",
            "--show-error",
            "--location",
            "--head",
            "--fail",
            "--max-time",
            "10",
            url,
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode == 0:
            return True
        if attempt < MAX_IMAGE_RETRIES - 1:
            time.sleep(0.25)
    return False


def validate_images(
    catalog: dict[str, dict[str, Any]],
    image_base_url: str,
    limit: int | None = None,
) -> tuple[set[str], dict[str, list[str]]]:
    excluded_games: set[str] = set()
    valid_image_map: dict[str, list[str]] = {}
    entries = list(catalog.items())
    if limit is not None:
        entries = entries[:limit]
    total = len(entries)

    print(f"[images] validating screenshots for {total} catalog games")
    print(f"[images] using base url: {image_base_url}")

    for index, (game_id, item) in enumerate(entries, start=1):
        urls = screenshot_urls(item, image_base_url)
        title = str(item.get("title", game_id))
        print(f"[images] {index}/{total} checking {title} screenshots={len(urls)}")
        for url_index, url in enumerate(urls, start=1):
            print(f"[images]   url[{url_index}]={url}")

        valid_urls = [url for url in urls if curl_url_exists(url)]
        if valid_urls:
            valid_image_map[game_id] = valid_urls
            print(f"[images] kept {title} valid={len(valid_urls)}")
        else:
            excluded_games.add(game_id)
            print(f"[images] excluded {title} no valid screenshots")

    print(
        f"[images] complete kept={len(valid_image_map)} excluded={len(excluded_games)}"
    )

    return excluded_games, valid_image_map


def score_item(
    record: dict[str, Any],
    subgroup: str,
    theme: str,
    used_game_ids: set[str],
    visible_theme_pressure: dict[str, int],
    visible_mechanics: set[str],
    visible_moods: set[str],
    visible_semantics: set[str],
) -> float:
    haystack = str(record["haystack"])
    theme_slug = slugify(theme)
    subgroup_slug = slugify(subgroup)

    hint_terms = list(SUBGROUP_HINTS.get(subgroup, []))
    hint_terms.extend(MECHANIC_HINTS.get(theme, []))
    hint_terms.extend(THEME_SYNONYMS.get(theme, []))

    hint_terms = list(dict.fromkeys(slugify(term).replace("-", " ") for term in hint_terms))
    subgroup_terms = [slugify(word).replace("-", " ") for word in subgroup.split() if word.strip()]

    score = 0.0
    for hint in hint_terms:
        if hint and hint in haystack:
            score += 4.0
    for token in subgroup_terms:
        if token and token in haystack:
            score += 1.25
    if theme_slug.replace("-", " ") in haystack:
        score += 2.5
    if subgroup_slug.replace("-", " ") in haystack:
        score += 2.0

    record_families = record["families"]

    if theme_slug in record_families["theme"]:
        score += 5.0

    new_mechanics = record_families["mechanic"] - visible_mechanics
    new_moods = record_families["mood"] - visible_moods
    new_semantics = record_families["semantic"] - visible_semantics

    score += len(new_mechanics) * 0.8
    score += len(new_moods) * 0.8
    score += min(len(new_semantics), 4) * 0.35

    score -= visible_theme_pressure.get(theme_slug, 0) * 5.5
    score -= record["reuse_count"] * 3.5

    if record["id"] in used_game_ids:
        score -= 1000.0

    if record["has_valid_image"] is False:
        score -= 1000.0

    return score


def chunked(sequence: list[dict[str, Any]], size: int) -> list[list[dict[str, Any]]]:
    return [sequence[index:index + size] for index in range(0, len(sequence), size)]


def page_uniqueness_penalty(page_collections: list[dict[str, Any]]) -> float:
    seen_themes: dict[str, int] = defaultdict(int)
    penalty = 0.0
    for collection in page_collections:
        theme = slugify(str(collection["theme"]))
        seen_themes[theme] += 1
        if seen_themes[theme] > 1:
            penalty += 3.0 * (seen_themes[theme] - 1)
    return penalty


def can_place_collection_theme(theme: str, visible_theme_pressure: dict[str, int]) -> bool:
    return visible_theme_pressure.get(slugify(theme), 0) < MAX_THEME_PER_BUNDLE


def collection_family_overlap_score(
    record: dict[str, Any],
    visible_mechanics: set[str],
    visible_moods: set[str],
    visible_semantics: set[str],
) -> float:
    families = record["families"]
    overlap = 0.0
    overlap += len(families["mechanic"] & visible_mechanics) * 1.2
    overlap += len(families["mood"] & visible_moods) * 0.9
    overlap += min(len(families["semantic"] & visible_semantics), 6) * 0.35
    return overlap


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--image-base-url",
        default=IMAGE_BASE_URL,
        help="Base URL prefix used to validate screenshots",
    )
    parser.add_argument(
        "--validate-images-only",
        action="store_true",
        help="Only run screenshot validation and stop before collection generation",
    )
    parser.add_argument(
        "--screenshots-cleanup",
        action="store_true",
        help="Opt in to screenshot validation/cleanup. By default this expensive phase is skipped.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit image validation to the first N catalog games for debugging",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    catalog: dict[str, dict[str, Any]] = json.loads(CATALOG_PATH.read_text())
    blueprint = json.loads(BLUEPRINT_PATH.read_text())

    if args.validate_images_only and not args.screenshots_cleanup:
        raise SystemExit("--validate-images-only requires --screenshots-cleanup")

    if args.screenshots_cleanup:
        print("[images] screenshots cleanup enabled")
        excluded_games, valid_image_map = validate_images(
            catalog,
            image_base_url=args.image_base_url,
            limit=args.limit,
        )
    else:
        print("[images] screenshots cleanup skipped by default")
        excluded_games = set()
        valid_image_map = {game_id: [] for game_id in catalog.keys()}

    if args.validate_images_only:
        print("[images] validate-only mode enabled, stopping before collection generation")
        return

    records: list[dict[str, Any]] = []
    record_by_id: dict[str, dict[str, Any]] = {}
    for game_id, item in catalog.items():
        if game_id in excluded_games:
            continue

        haystack = build_haystack(item)
        record = {
            "id": game_id,
            "title": item.get("title", ""),
            "haystack": haystack,
            "families": classify_token_families(item),
            "reuse_count": 0,
            "has_valid_image": game_id in valid_image_map,
        }
        records.append(record)
        record_by_id[game_id] = record

    visible_row_bundle_size = VISIBLE_PAGE_COUNT * 5
    blueprint_collections = list(blueprint["collections"])
    bundle_groups = chunked(blueprint_collections, visible_row_bundle_size)

    populated: list[dict[str, Any]] = []
    visible_bundle_audits: list[dict[str, Any]] = []

    for bundle_index, bundle in enumerate(bundle_groups):
        print(
            f"[bundle] starting bundle {bundle_index + 1}/{len(bundle_groups)} "
            f"collections={len(bundle)} visible_pages={VISIBLE_PAGE_COUNT}"
        )

        used_game_ids: set[str] = set()
        visible_theme_pressure: dict[str, int] = defaultdict(int)
        visible_mechanics: set[str] = set()
        visible_moods: set[str] = set()
        visible_semantics: set[str] = set()
        selected_bundle_collections: list[dict[str, Any]] = []

        for collection_index, collection in enumerate(bundle, start=1):
            size = int(collection["size"])
            subgroup = str(collection["subgroup"])
            theme = str(collection["theme"])
            title = str(collection["title"])

            print(
                f"[collection] bundle={bundle_index + 1} "
                f"{collection_index}/{len(bundle)} id={collection['id']} "
                f"title={title} size={size} theme={theme} subgroup={subgroup}"
            )

            ranked = sorted(
                records,
                key=lambda record: (
                    score_item(
                        record,
                        subgroup=subgroup,
                        theme=theme,
                        used_game_ids=used_game_ids,
                        visible_theme_pressure=visible_theme_pressure,
                        visible_mechanics=visible_mechanics,
                        visible_moods=visible_moods,
                        visible_semantics=visible_semantics,
                    )
                    - collection_family_overlap_score(
                        record,
                        visible_mechanics=visible_mechanics,
                        visible_moods=visible_moods,
                        visible_semantics=visible_semantics,
                    ),
                    str(record["title"]),
                ),
                reverse=True,
            )

            selected: list[dict[str, Any]] = []
            attempted = 0
            skipped_used = 0
            skipped_reuse = 0
            skipped_score = 0
            skipped_theme_cap = 0

            if not can_place_collection_theme(theme, visible_theme_pressure):
                print(
                    f"[collection] theme cap reached for theme={theme} in bundle={bundle_index + 1}; "
                    "collection will remain underfilled"
                )

            for record in ranked:
                if len(selected) >= size:
                    break
                attempted += 1
                game_id = str(record["id"])
                if game_id in used_game_ids:
                    skipped_used += 1
                    continue
                if record["reuse_count"] >= 3:
                    skipped_reuse += 1
                    continue
                if not can_place_collection_theme(theme, visible_theme_pressure):
                    skipped_theme_cap += 1
                    continue

                score = score_item(
                    record,
                    subgroup=subgroup,
                    theme=theme,
                    used_game_ids=used_game_ids,
                    visible_theme_pressure=visible_theme_pressure,
                    visible_mechanics=visible_mechanics,
                    visible_moods=visible_moods,
                    visible_semantics=visible_semantics,
                )
                score -= collection_family_overlap_score(
                    record,
                    visible_mechanics=visible_mechanics,
                    visible_moods=visible_moods,
                    visible_semantics=visible_semantics,
                )
                if score < MIN_SCORE_FLOOR:
                    skipped_score += 1
                    continue

                picked = {
                    "id": game_id,
                    "title": record["title"],
                    "match_score": round(score, 2),
                }
                selected.append(picked)
                print(
                    f"[pick] collection={collection['id']} game={picked['title']} "
                    f"score={picked['match_score']}"
                )
                used_game_ids.add(game_id)
                record["reuse_count"] += 1

                families = record["families"]
                visible_mechanics.update(families["mechanic"])
                visible_moods.update(families["mood"])
                visible_semantics.update(families["semantic"])

            if selected:
                visible_theme_pressure[slugify(theme)] += 1

            print(
                f"[collection] completed id={collection['id']} "
                f"filled={len(selected)}/{size} attempted={attempted} "
                f"skipped_used={skipped_used} skipped_reuse={skipped_reuse} "
                f"skipped_score={skipped_score} skipped_theme_cap={skipped_theme_cap}"
            )

            selected_collection = {
                **collection,
                "games": selected,
                "filled_count": len(selected),
                "target_count": size,
            }
            selected_bundle_collections.append(selected_collection)
            populated.append(selected_collection)

        print(
            f"[bundle] completed bundle {bundle_index + 1} "
            f"unique_games={len(used_game_ids)} mechanics={len(visible_mechanics)} "
            f"moods={len(visible_moods)} semantics={len(visible_semantics)}"
        )

        visible_bundle_audits.append(
            {
                "bundle_index": bundle_index,
                "visible_collections": len(selected_bundle_collections),
                "unique_games": len(used_game_ids),
                "theme_pressure": dict(visible_theme_pressure),
                "visible_mechanics": sorted(visible_mechanics),
                "visible_moods": sorted(visible_moods),
                "visible_semantics_sample": sorted(list(visible_semantics))[:25],
                "page_uniqueness_penalty": page_uniqueness_penalty(selected_bundle_collections),
            }
        )

    payload = {
        "meta": blueprint["meta"],
        "collections": populated,
        "reuse_summary": {
            "reused_games": len([record for record in records if record["reuse_count"] > 1]),
            "max_reuse": max((record["reuse_count"] for record in records), default=0),
            "excluded_broken_image_games": len(excluded_games),
        },
        "visible_bundle_audits": visible_bundle_audits,
    }

    OUT_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {OUT_PATH}")
    print(json.dumps(payload["reuse_summary"], indent=2))
    print(json.dumps(visible_bundle_audits[:2], indent=2))


if __name__ == "__main__":
    main()