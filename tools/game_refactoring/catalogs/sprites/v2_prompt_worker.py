#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
DEFAULT_CATALOG = ROOT.parent / "sprites_expanded_v2.json"
DEFAULT_CONTROL = ROOT / "v2_edit_control.json"
DEFAULT_PROGRESS = ROOT / "v2_edit_progress.json"
DEFAULT_DASHBOARD = ROOT / "dashboard_v2.html"
DEFAULT_LIVE_DIR = ROOT / "live_v2"


def slug_words(value: str) -> list[str]:
    return [word for word in re.sub(r"[^a-z0-9]+", " ", value.lower()).split() if word not in {"game", "sprites"}]


def title_label(query: str) -> str:
    words = slug_words(query)
    return " ".join(words)


def infer_family(query: str) -> str:
    q = query.lower()
    if "runner" in q or "parkour" in q or "obby" in q:
        return "runner"
    if "shooter" in q or "sniper" in q or "battle royale" in q:
        return "shooter"
    if "puzzle" in q or "sudoku" in q or "word search" in q or "match 3" in q or "tile matching" in q:
        return "puzzle"
    if "tycoon" in q:
        return "tycoon"
    if "builder" in q or "building" in q or "creator" in q or "editor" in q:
        return "builder"
    if "strategy" in q or "defense" in q:
        return "strategy"
    if "football" in q or "basketball" in q or "racing" in q or "skate" in q:
        return "sports"
    if "story" in q or "novel" in q or "choice" in q:
        return "story"
    if "social" in q or "avatar" in q or "chat" in q or "stream" in q or "influencer" in q:
        return "social"
    return "simulator"


def usage_for(query: str, asset_name: str, asset_kind: str) -> str:
    label = title_label(query)
    name = asset_name.replace("_", " ")
    if asset_kind == "background":
        if asset_name in {"main_scene", "starter_business", "starter_plot", "board_scene", "track_day", "combat_zone", "battle_map", "story_scene", "arena_day", "social_hub"}:
            return f"main {label} play scene where the core loop is introduced and the player understands the environment"
        return f"advanced {label} scene used for upgrades, progression, premium moments, or harder gameplay states"

    role_map = {
        "main_avatar": f"main playable or representative avatar for the {label} experience",
        "player_runner": f"main runner character used during active movement and obstacle-dodging gameplay",
        "hero_unit": f"main hero combat unit used by the player in {label}",
        "manager_avatar": f"main management character representing the player in the {label} economy loop",
        "builder_avatar": f"main builder character used to place, arrange, and improve structures",
        "lead_avatar": f"main narrative character used in story scenes and emotional choices",
        "avatar_star": f"main social avatar representing the player in the {label} world",
        "tool_item": f"interactive tool or control item used to perform the core {label} action",
        "target_object": f"main objective object the player interacts with, collects, completes, or upgrades",
        "reward_token": f"reward token earned from successful {label} progression",
        "core_piece": f"primary puzzle piece used in the core {label} interaction",
        "special_piece": f"special high-value piece that creates stronger effects in {label}",
        "blocker_piece": f"obstacle or blocker piece that increases challenge in {label}",
        "hint_icon": f"hint or helper booster used when the player is stuck in {label}",
        "tower_basic": f"basic defensive tower used as the first reliable defense in {label}",
        "tower_sniper": f"long-range defensive tower used for precision damage in {label}",
        "enemy_walker": f"standard enemy unit used to test baseline defenses in {label}",
        "enemy_tank": f"heavy enemy unit used as a durable threat in {label}",
    }
    return role_map.get(asset_name, f"{name} asset used in the {label} gameplay loop")


def prompt_for(query: str, asset_name: str, asset_kind: str) -> str:
    label = title_label(query)
    family = infer_family(query)
    readable = asset_name.replace("_", " ")

    if asset_kind == "background":
        bg_flavors = {
            "main_scene": f"2D {label} main environment, clear readable gameplay layout, distinctive genre-specific props, polished casual game background, full background",
            "upgrade_scene": f"2D {label} upgraded environment, premium progression mood, richer props and lighting, polished casual game background, full background",
            "starter_business": f"2D {label} starter business scene, small early-game operation, readable layout, polished tycoon environment, full background",
            "premium_business": f"2D {label} premium business scene, upgraded successful operation, aspirational lighting, polished tycoon environment, full background",
            "starter_plot": f"2D {label} starter build area, open construction space, readable placement zones, polished builder game background, full background",
            "developed_plot": f"2D {label} developed build area, layered completed structures, satisfying progression mood, polished builder game background, full background",
            "board_scene": f"2D {label} puzzle board scene, clean board layout, tactile puzzle pieces, soft polished casual lighting, full background",
            "premium_board": f"2D {label} premium puzzle board scene, richer theme props, glossy casual puzzle polish, full background",
            "track_day": f"2D {label} daytime runner track, readable path, strong motion direction, layered parallax environment, full background",
            "track_night": f"2D {label} night runner track, dramatic lights, readable path, layered parallax depth, full background",
            "combat_zone": f"2D {label} combat zone, readable cover and threat lanes, high-energy arcade action mood, full background",
            "boss_zone": f"2D {label} boss arena, dramatic lighting, high-stakes composition, polished arcade action environment, full background",
            "battle_map": f"2D {label} tactical battle map, readable lanes and terrain zones, clean strategic layout, full background",
            "hazard_map": f"2D {label} hazard battle map, dangerous terrain, high contrast tactical zones, polished strategy background, full background",
            "story_scene": f"2D {label} story scene, cinematic composition, emotional set dressing, polished narrative game background, full background",
            "climax_scene": f"2D {label} climax scene, dramatic lighting, emotional tension, premium narrative game background, full background",
            "arena_day": f"2D {label} daytime arena, clean action space, bright competitive atmosphere, polished sports game background, full background",
            "arena_night": f"2D {label} night arena, stadium lights, dramatic competitive mood, polished sports game background, full background",
            "social_hub": f"2D {label} social hub, lively avatar gathering space, playful props, polished community game background, full background",
            "creator_studio": f"2D {label} creator studio, premium social setup, stylish lighting, polished creator economy background, full background",
        }
        return bg_flavors.get(asset_name, f"2D {label} {readable} background, distinctive gameplay setting, polished casual game art, full background")

    family_flavor = {
        "runner": "dynamic motion silhouette, strong side-view readability",
        "shooter": "bold combat silhouette, tactical arcade polish",
        "puzzle": "tactile glossy shape, clear puzzle readability",
        "tycoon": "aspirational economy-game polish, clear business identity",
        "builder": "modular construction identity, clean readable forms",
        "strategy": "top-down tactical readability, clean strategic shape",
        "sports": "energetic athletic identity, strong action readability",
        "story": "expressive narrative symbolism, emotional visual clarity",
        "social": "expressive social identity, stylish modern polish",
        "simulator": "clear interactive object identity, polished simulation-game readability",
    }[family]

    return f"{label} {readable}, {family_flavor}, premium casual mobile game asset, transparent background"


def rewrite_catalog(catalog: list[dict[str, Any]], batch_size: int, batch_index: int | None, force: bool) -> tuple[list[dict[str, Any]], list[str]]:
    changed_queries: list[str] = []
    start = (batch_index - 1) * batch_size if batch_index else 0
    end = start + batch_size if batch_index else len(catalog)

    for entry in catalog[start:end]:
        query = entry["query"]
        changed = False
        for group_name, asset_kind in (("sprites_transparent", "sprite"), ("backgrounds_opaque", "background")):
            for asset in entry.get(group_name, []):
                if force or not asset.get("usage"):
                    asset["usage"] = usage_for(query, asset["name"], asset_kind)
                    asset["prompt"] = prompt_for(query, asset["name"], asset_kind)
                    if not asset.get("style"):
                        asset["style"] = ""
                    changed = True
        if changed:
            changed_queries.append(query)
    return catalog, changed_queries


def refresh_dashboard(catalog_path: Path, live_dir: Path, output_path: Path) -> None:
    subprocess.run(
        [
            "python3",
            str(ROOT / "render_dashboard.py"),
            "--catalog",
            str(catalog_path),
            "--live-dir",
            str(live_dir),
            "--output",
            str(output_path),
            "--title",
            "Sprites Taxonomy Dashboard V2",
        ],
        check=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="V2 prompt batch worker for sprites_expanded_v2.json.")
    parser.add_argument("--catalog", default=str(DEFAULT_CATALOG))
    parser.add_argument("--control", default=str(DEFAULT_CONTROL))
    parser.add_argument("--progress", default=str(DEFAULT_PROGRESS))
    parser.add_argument("--batch", type=int, help="1-based batch number to process.")
    parser.add_argument("--batch-size", type=int, default=10)
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--force", action="store_true", help="Rewrite records even when usage already exists.")
    parser.add_argument("--refresh-dashboard", action="store_true", default=True)
    args = parser.parse_args()

    catalog_path = Path(args.catalog)
    progress_path = Path(args.progress)
    control_path = Path(args.control)

    catalog = json.loads(catalog_path.read_text())

    batch_index = None if args.all else args.batch
    if not args.all and not batch_index:
        progress = json.loads(progress_path.read_text()) if progress_path.exists() else {}
        batch_index = int(progress.get("current_batch", 1))

    catalog, changed_queries = rewrite_catalog(catalog, args.batch_size, batch_index, args.force)
    catalog_path.write_text(json.dumps(catalog, indent=2) + "\n")

    if args.refresh_dashboard:
        refresh_dashboard(catalog_path, DEFAULT_LIVE_DIR, DEFAULT_DASHBOARD)

    progress = {
        "catalog_path": str(catalog_path.resolve()),
        "dashboard_path": str(DEFAULT_DASHBOARD.resolve()),
        "total_queries": len(catalog),
        "last_batch_processed": batch_index if not args.all else "all",
        "last_changed_queries": changed_queries,
        "last_updated": datetime.now().astimezone().isoformat(),
        "review_status": "worker_batch_complete",
        "next_action": "Review dashboard_v2.html or run next worker batch.",
    }
    progress_path.write_text(json.dumps(progress, indent=2) + "\n")

    if control_path.exists():
        control = json.loads(control_path.read_text())
        if isinstance(batch_index, int):
            completed = set(control.get("completed_batches", []))
            pending = [batch for batch in control.get("pending_batches", []) if batch != batch_index]
            completed.add(batch_index)
            control["completed_batches"] = sorted(completed)
            control["pending_batches"] = pending
            control["status"] = "batch_complete"
            control["last_updated"] = progress["last_updated"]
            control_path.write_text(json.dumps(control, indent=2) + "\n")

    print(json.dumps({"ok": True, "changed_queries": changed_queries, "batch": batch_index if not args.all else "all"}, indent=2))


if __name__ == "__main__":
    main()