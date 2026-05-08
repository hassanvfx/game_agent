#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path


TOP100_PATH = Path("/Volumes/Elements/games_top_gameplays/top100.json")
OUTPUT_PATH = Path("/Volumes/Elements/game_remix_editor/catalogs/sprites_expanded_merge_ready.json")


GENRE_PATTERNS = [
    ("runner", "runner"),
    ("simulator", "simulator"),
    ("tycoon", "tycoon"),
    ("shooter", "shooter"),
    ("puzzle", "puzzle"),
    ("tower defense", "tower_defense"),
    ("defense", "tower_defense"),
    ("strategy", "strategy"),
    ("builder", "builder"),
    ("building", "builder"),
    ("creator", "social"),
    ("stream", "social"),
    ("influencer", "social"),
    ("social", "social"),
    ("story", "story"),
    ("novel", "story"),
    ("choice", "story"),
    ("football", "sports"),
    ("basketball", "sports"),
    ("skate", "sports"),
    ("racing", "sports"),
]


FAMILY_TEMPLATES = {
    "runner": {
        "sprites": [
            ("player_runner", "runner character, forward motion pose"),
            ("energy_orb", "runner collectible orb, glowing core"),
            ("barrier_obstacle", "runner barrier obstacle, bold silhouette"),
            ("dash_powerup", "runner speed boost power-up, glowing trail"),
        ],
        "backgrounds": [
            ("track_day", "side scrolling runner background, layered track, bright atmosphere"),
            ("track_night", "side scrolling runner background, neon accents, layered skyline"),
        ],
        "sprite_style": [
            "stylized runner character, side view, clean outline, vibrant colors",
            "arcade collectible, glowing core, simple shading",
            "danger object, high contrast, readable silhouette",
            "arcade power-up, glowing edges, premium casual polish",
        ],
        "background_style": [
            "side scrolling parallax, layered environment, bright accents",
            "side scrolling parallax, neon accents, layered skyline",
        ],
    },
    "simulator": {
        "sprites": [
            ("main_avatar", "simulator character, readable pose"),
            ("tool_item", "interactive tool prop, clean silhouette"),
            ("target_object", "core task object, premium casual style"),
            ("reward_token", "reward token, glossy finish"),
        ],
        "backgrounds": [
            ("main_scene", "2D simulator background, interactive environment, polished details"),
            ("upgrade_scene", "2D simulator background, upgraded premium environment, clean layout"),
        ],
        "sprite_style": [
            "casual simulator character, clean outline, soft shading",
            "interactive prop, polished surface, readable shape",
            "task object, premium casual style, simple geometry",
            "reward item, glossy look, vibrant highlight",
        ],
        "background_style": [
            "detailed environment, readable layout, casual simulation style",
            "premium environment, upgraded props, polished lighting",
        ],
    },
    "tycoon": {
        "sprites": [
            ("manager_avatar", "tycoon manager character, confident pose"),
            ("cash_bundle", "money reward bundle, glossy highlights"),
            ("business_prop", "business upgrade prop, polished finish"),
            ("profit_boost", "profit boost item, glowing accent"),
        ],
        "backgrounds": [
            ("starter_business", "2D tycoon background, starter business layout, clean design"),
            ("premium_business", "2D tycoon background, upgraded premium business, bright atmosphere"),
        ],
        "sprite_style": [
            "cartoon manager character, clean outline, premium casual style",
            "cash reward object, shiny finish, simple shading",
            "business prop, polished surface, readable silhouette",
            "boost item, glowing edges, premium tycoon style",
        ],
        "background_style": [
            "top-down or side layout, clean economy scene, readable props",
            "upgraded business scene, bright accents, premium casual polish",
        ],
    },
    "shooter": {
        "sprites": [
            ("hero_unit", "shooter hero character, combat-ready pose"),
            ("enemy_unit", "enemy character, readable silhouette"),
            ("weapon_pickup", "weapon pickup item, metallic finish"),
            ("shield_pickup", "defense pickup, glowing energy core"),
        ],
        "backgrounds": [
            ("combat_zone", "2D shooter background, battle area, cinematic atmosphere"),
            ("boss_zone", "2D shooter background, high intensity combat arena, dramatic lighting"),
        ],
        "sprite_style": [
            "action character, strong silhouette, clean armor detail",
            "enemy unit, readable shape, bold contrast",
            "pickup prop, metallic shading, arcade readability",
            "glowing defense item, sci-fi accents, premium arcade look",
        ],
        "background_style": [
            "combat environment, layered depth, dramatic mood",
            "battle arena, high contrast lighting, cinematic action style",
        ],
    },
    "puzzle": {
        "sprites": [
            ("core_piece", "main puzzle piece, glossy finish"),
            ("special_piece", "special puzzle element, bright accent color"),
            ("blocker_piece", "blocker object, bold silhouette"),
            ("hint_icon", "hint booster icon, glowing outline"),
        ],
        "backgrounds": [
            ("board_scene", "2D puzzle background, clean board layout, soft lighting"),
            ("premium_board", "2D puzzle background, premium themed board, polished details"),
        ],
        "sprite_style": [
            "glossy puzzle piece, rounded edges, simple shading",
            "special game piece, vibrant accent, clean silhouette",
            "blocker object, high contrast, readable form",
            "booster icon, glowing edges, casual puzzle polish",
        ],
        "background_style": [
            "clean board layout, soft gradients, casual puzzle style",
            "premium board theme, polished props, bright atmosphere",
        ],
    },
    "tower_defense": {
        "sprites": [
            ("tower_basic", "basic tower, top-down view, simple design"),
            ("tower_sniper", "sniper tower, long barrel, top-down view"),
            ("enemy_walker", "enemy walker unit, small creature, readable silhouette"),
            ("enemy_tank", "heavy tank enemy, bulky shape, armored detail"),
        ],
        "backgrounds": [
            ("grass_map", "top-down defense map, grass tiles, path layout, clean design"),
            ("lava_map", "top-down defense map, lava cracks, dark terrain, high contrast"),
        ],
        "sprite_style": [
            "top-down, clean geometry, premium casual shading",
            "top-down, long barrel, detailed surface",
            "small creature, readable silhouette, simple detail",
            "heavy armored, bulky shape, strong contrast",
        ],
        "background_style": [
            "top-down grid map, clean tiles, readable pathing",
            "high contrast terrain, glowing lava, tactical layout",
        ],
    },
    "strategy": {
        "sprites": [
            ("commander_unit", "strategy commander unit, top-down view"),
            ("base_node", "base structure, clean shape, readable details"),
            ("assault_unit", "enemy assault unit, top-down silhouette"),
            ("upgrade_module", "upgrade module item, glowing accents"),
        ],
        "backgrounds": [
            ("battle_map", "top-down strategy map, readable lanes, clean terrain"),
            ("hazard_map", "top-down strategy map, dangerous terrain, dramatic contrast"),
        ],
        "sprite_style": [
            "top-down unit, clean geometry, tactical readability",
            "base structure, simple form, premium casual detail",
            "combat unit, readable silhouette, strong contrast",
            "upgrade prop, glowing accents, polished strategy style",
        ],
        "background_style": [
            "top-down tactical layout, readable terrain, clean map design",
            "high contrast battlefield, hazard zones, premium strategy look",
        ],
    },
    "builder": {
        "sprites": [
            ("builder_avatar", "builder character, work pose"),
            ("resource_crate", "construction resource crate, clean edges"),
            ("build_tool", "construction tool item, polished surface"),
            ("upgrade_module", "building upgrade module, premium casual style"),
        ],
        "backgrounds": [
            ("starter_plot", "2D building background, open construction plot, clean layout"),
            ("developed_plot", "2D building background, upgraded constructed world, polished details"),
        ],
        "sprite_style": [
            "builder character, clean outline, soft shading",
            "construction prop, readable shape, simple texture",
            "tool item, polished surface, casual builder style",
            "upgrade item, bright accent, construction theme",
        ],
        "background_style": [
            "buildable terrain, modular layout, clean environment",
            "developed environment, layered structures, polished look",
        ],
    },
    "social": {
        "sprites": [
            ("avatar_star", "social avatar character, expressive pose"),
            ("engagement_token", "engagement token, glossy finish"),
            ("device_prop", "creator device prop, polished surface"),
            ("status_boost", "status boost icon, glowing edges"),
        ],
        "backgrounds": [
            ("social_hub", "2D social hub background, colorful interactive space"),
            ("creator_studio", "2D creator studio background, premium setup, bright accents"),
        ],
        "sprite_style": [
            "stylized avatar, expressive features, vibrant colors",
            "social reward token, glossy highlights, simple shading",
            "tech prop, polished surface, modern casual style",
            "status icon, glowing edges, premium social polish",
        ],
        "background_style": [
            "social hub, layered props, vibrant casual atmosphere",
            "creator studio, premium decor, bright lighting",
        ],
    },
    "story": {
        "sprites": [
            ("lead_avatar", "story lead character, cinematic pose"),
            ("choice_icon", "branching choice icon, clean silhouette"),
            ("memory_token", "memory token, glowing core"),
            ("chapter_unlock", "chapter unlock item, premium finish"),
        ],
        "backgrounds": [
            ("story_scene", "2D narrative background, cinematic environment, layered depth"),
            ("climax_scene", "2D narrative background, dramatic climax setting, moody lighting"),
        ],
        "sprite_style": [
            "story character, cinematic pose, soft shading",
            "UI-style icon, readable shape, polished finish",
            "symbolic token, glowing core, simple detail",
            "unlock item, premium finish, elegant shape",
        ],
        "background_style": [
            "cinematic environment, layered scenery, soft light",
            "dramatic environment, moody tones, premium story style",
        ],
    },
    "sports": {
        "sprites": [
            ("star_player", "sports lead character, action pose"),
            ("core_ball", "main sports ball or equipment item"),
            ("target_marker", "score target marker, bright contrast"),
            ("energy_boost", "athletic boost item, glowing effect"),
        ],
        "backgrounds": [
            ("arena_day", "2D sports background, bright arena, clear field markings"),
            ("arena_night", "2D sports background, stadium lights, dramatic crowd atmosphere"),
        ],
        "sprite_style": [
            "athletic character, dynamic pose, clean outline",
            "sports equipment, polished finish, readable shape",
            "target object, high contrast, bold silhouette",
            "boost item, glowing accents, energetic casual style",
        ],
        "background_style": [
            "sports arena, bright colors, clean field layout",
            "stadium environment, dramatic lights, premium sports feel",
        ],
    },
}


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_")


def infer_family(label: str) -> str:
    lowered = label.lower()
    for needle, family in GENRE_PATTERNS:
        if needle in lowered:
            return family
    return "simulator"


def folder_slug(label: str) -> str:
    return slugify(label).replace("_game", "")


def build_entry(label: str) -> dict:
    family = infer_family(label)
    template = FAMILY_TEMPLATES[family]
    folder = folder_slug(label)

    sprites = []
    for index, (name, prompt_seed) in enumerate(template["sprites"]):
        sprites.append(
            {
                "name": name,
                "url": f"https://gamezone-virid.vercel.app/assets/images/sprites/{folder}/{name}.png",
                "style": template["sprite_style"][index],
                "prompt": f"{prompt_seed}, cartoon style, transparent background",
            }
        )

    backgrounds = []
    for index, (name, prompt_seed) in enumerate(template["backgrounds"]):
        backgrounds.append(
            {
                "name": name,
                "url": f"https://gamezone-virid.vercel.app/assets/images/backgrounds/{folder}/{name}.png",
                "style": template["background_style"][index],
                "prompt": f"{prompt_seed}, full background",
            }
        )

    return {
        "query": f"{label.lower()} sprites",
        "sprites_transparent": sprites,
        "backgrounds_opaque": backgrounds,
    }


def main() -> None:
    labels = json.loads(TOP100_PATH.read_text())
    catalog = [build_entry(label) for label in labels]
    OUTPUT_PATH.write_text(json.dumps(catalog, indent=2) + "\n")
    print(
        json.dumps(
            {
                "ok": True,
                "source": str(TOP100_PATH),
                "output": str(OUTPUT_PATH),
                "entries": len(catalog),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()