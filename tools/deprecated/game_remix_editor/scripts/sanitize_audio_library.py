#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_AUDIO_ROOT = ROOT / "assets" / "audio_library"
DEFAULT_INCOMING_DIR = DEFAULT_AUDIO_ROOT / "incoming"
DEFAULT_UNMATCHED_DIR = DEFAULT_AUDIO_ROOT / "unmatched"
DEFAULT_OUTPUT_PATH = DEFAULT_AUDIO_ROOT / "audios.json"
DEFAULT_REMOTE_BASE_URL = "https://gamezone-virid.vercel.app/assets/audios/"

GROUP_ORDER = [
    "jumps",
    "lands",
    "shoots",
    "projectiles",
    "hits",
    "damages",
    "enemy_hits",
    "enemy_defeats",
    "pickups",
    "bonuses",
    "powerups",
    "explosions",
    "blocked_actions",
    "warnings",
    "successes",
    "failures",
    "game_overs",
    "level_completes",
    "clicks",
    "hovers",
    "starts",
    "pauses",
    "resumes",
    "menu_opens",
    "menu_closes",
    "ambient_loops",
    "action_loops",
    "victory_loops",
    "defeat_loops",
    "soft_magic_loops",
    "spooky_loops",
    "arcade_loops",
]


@dataclass(frozen=True)
class AudioIntent:
    event: str
    group: str
    folder: str
    usage: str
    audio_type: str
    keywords: tuple[str, ...]


INTENTS = [
    AudioIntent(
        "soft_magic_loop",
        "soft_magic_loops",
        "ambience",
        "Calm magical ambience",
        "loop",
        ("soft magic", "magic ambience", "airy shimmer", "twinkles", "enchanted atmosphere"),
    ),
    AudioIntent(
        "spooky_loop",
        "spooky_loops",
        "ambience",
        "Spooky ambience",
        "loop",
        ("spooky", "ghostly", "creaks", "magical mystery"),
    ),
    AudioIntent(
        "arcade_loop",
        "arcade_loops",
        "ambience",
        "Arcade ambience",
        "loop",
        ("arcade ambience", "retro room tone", "electronic sparkle"),
    ),
    AudioIntent(
        "ambient_loop",
        "ambient_loops",
        "music",
        "Default background music",
        "loop",
        ("ambient background", "ambient loop", "casual game ambient", "default background"),
    ),
    AudioIntent(
        "action_loop",
        "action_loops",
        "music",
        "Active gameplay music",
        "loop",
        ("action gameplay", "action loop", "upbeat arcade", "gameplay loop"),
    ),
    AudioIntent(
        "victory_loop",
        "victory_loops",
        "music",
        "Victory or results music",
        "loop",
        ("victory", "results music", "celebratory", "bright harmony"),
    ),
    AudioIntent(
        "defeat_loop",
        "defeat_loops",
        "music",
        "Defeat or retry music",
        "loop",
        ("defeat", "retry music", "bittersweet", "descending harmony"),
    ),
    AudioIntent(
        "level_complete",
        "level_completes",
        "sfx",
        "Level clear or win state",
        "one_shot",
        ("level complete", "level-complete", "level clear", "win state", "upbeat resolution"),
    ),
    AudioIntent(
        "game_over",
        "game_overs",
        "sfx",
        "Game over or loss state",
        "one_shot",
        ("game over", "game-over", "loss state", "loss sting"),
    ),
    AudioIntent(
        "enemy_defeat",
        "enemy_defeats",
        "sfx",
        "Enemy disappears or is defeated",
        "one_shot",
        ("enemy defeat", "enemy defeated", "disappear", "vanish", "poof"),
    ),
    AudioIntent(
        "enemy_hit",
        "enemy_hits",
        "sfx",
        "Enemy receives damage",
        "one_shot",
        ("enemy hit", "enemy receives", "enemy damage"),
    ),
    AudioIntent(
        "menu_open",
        "menu_opens",
        "ui",
        "Open menu or panel",
        "one_shot",
        ("menu open", "menu-open", "open menu", "card unfold", "reveal shimmer"),
    ),
    AudioIntent(
        "menu_close",
        "menu_closes",
        "ui",
        "Close menu or panel",
        "one_shot",
        ("menu close", "menu-close", "close menu", "fold-away", "reverse shimmer"),
    ),
    AudioIntent(
        "projectile",
        "projectiles",
        "sfx",
        "Projectile spawn or travel",
        "one_shot",
        ("projectile", "energy bolt", "travel", "magical zip", "particle sparkle"),
    ),
    AudioIntent(
        "powerup",
        "powerups",
        "sfx",
        "Power-up activation",
        "one_shot",
        ("power up", "power-up", "powerup", "activation", "rising magical energy"),
    ),
    AudioIntent(
        "explosion",
        "explosions",
        "sfx",
        "Arcade burst or destruction",
        "one_shot",
        ("explosion", "burst", "destruction", "debris"),
    ),
    AudioIntent(
        "blocked",
        "blocked_actions",
        "sfx",
        "Invalid or blocked action",
        "one_shot",
        ("blocked", "invalid action", "wooden clack", "dull tick"),
    ),
    AudioIntent(
        "warning",
        "warnings",
        "sfx",
        "Danger, low health, urgent state",
        "one_shot",
        ("warning", "danger", "low health", "urgent"),
    ),
    AudioIntent(
        "success",
        "successes",
        "sfx",
        "Checkpoint or completed action",
        "one_shot",
        ("success", "checkpoint", "completed action", "positive chime"),
    ),
    AudioIntent(
        "failure",
        "failures",
        "sfx",
        "Failed action or error feedback",
        "one_shot",
        ("fail", "failure", "error", "descending wobble", "muted thunk"),
    ),
    AudioIntent(
        "pickup",
        "pickups",
        "sfx",
        "Collectible item pickup",
        "one_shot",
        ("pickup", "collectible", "item pickup", "upward sparkle"),
    ),
    AudioIntent(
        "bonus",
        "bonuses",
        "sfx",
        "Bonus reward or score boost",
        "one_shot",
        ("bonus", "reward burst", "score boost"),
    ),
    AudioIntent(
        "damage",
        "damages",
        "sfx",
        "Player damage or hurt feedback",
        "one_shot",
        ("damage", "hurt", "player damage"),
    ),
    AudioIntent(
        "shoot",
        "shoots",
        "sfx",
        "Magical shot or cast action",
        "one_shot",
        ("shoot", "shot", "cast", "casting", "wand"),
    ),
    AudioIntent(
        "jump",
        "jumps",
        "sfx",
        "Player jump, bounce, upward movement",
        "one_shot",
        ("jump", "upward", "bounce"),
    ),
    AudioIntent(
        "land",
        "lands",
        "sfx",
        "Player landing or ground contact",
        "one_shot",
        ("land", "landing", "ground contact"),
    ),
    AudioIntent(
        "hit",
        "hits",
        "sfx",
        "Generic collision or impact",
        "one_shot",
        ("hit", "collision", "impact", "bonk"),
    ),
    AudioIntent(
        "click",
        "clicks",
        "ui",
        "Button click",
        "one_shot",
        ("click", "button click", "ui click"),
    ),
    AudioIntent(
        "hover",
        "hovers",
        "ui",
        "UI hover",
        "one_shot",
        ("hover", "ui hover"),
    ),
    AudioIntent(
        "start",
        "starts",
        "ui",
        "Start game",
        "one_shot",
        ("start", "start game", "start-game"),
    ),
    AudioIntent(
        "pause",
        "pauses",
        "ui",
        "Pause game",
        "one_shot",
        ("pause", "pause game"),
    ),
    AudioIntent(
        "resume",
        "resumes",
        "ui",
        "Resume game",
        "one_shot",
        ("resume", "resume game", "restart cue"),
    ),
]

INTENT_BY_EVENT = {intent.event: intent for intent in INTENTS}
INTENT_BY_GROUP = {intent.group: intent for intent in INTENTS}
MP3_SUFFIX = ".mp3"

PROMPT_PREFIX_TO_EVENT = [
    ("Playful upward jump sound", "jump"),
    ("Soft landing thump", "land"),
    ("Magical casting shot", "shoot"),
    ("Fast magical projectile zip", "projectile"),
    ("Compact arcade hit sound", "hit"),
    ("Player damage cue", "damage"),
    ("Enemy hit cue", "enemy_hit"),
    ("Whimsical enemy defeat poof", "enemy_defeat"),
    ("Bright collectible pickup chime", "pickup"),
    ("Joyful bonus reward burst", "bonus"),
    ("Power-up activation", "powerup"),
    ("Soft arcade explosion pop", "explosion"),
    ("Blocked action cue", "blocked"),
    ("Brief warning pulse", "warning"),
    ("Positive success chime", "success"),
    ("Gentle fail cue", "failure"),
    ("Gentle game-over sting", "game_over"),
    ("Short level-complete flourish", "level_complete"),
    ("Tiny UI click", "click"),
    ("Subtle UI hover cue", "hover"),
    ("Start-game confirmation", "start"),
    ("Pause cue", "pause"),
    ("Resume cue", "resume"),
    ("Menu-open cue", "menu_open"),
    ("Menu-close cue", "menu_close"),
    ("Seamless casual game ambient loop", "ambient_loop"),
    ("Seamless action gameplay loop", "action_loop"),
    ("Seamless victory results loop", "victory_loop"),
    ("Seamless defeat results loop", "defeat_loop"),
    ("Seamless soft magic ambience loop", "soft_magic_loop"),
    ("Seamless family-friendly spooky ambience loop", "spooky_loop"),
    ("Seamless arcade ambience loop", "arcade_loop"),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Copy prompt-named generated MP3 audio files into clean audio-library names and write grouped audios.json."
    )
    parser.add_argument("--incoming", default=str(DEFAULT_INCOMING_DIR), help="Directory containing messy prompt-named MP3 files.")
    parser.add_argument("--audio-root", default=str(DEFAULT_AUDIO_ROOT), help="Audio library root directory.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH), help="Grouped audios.json output path.")
    parser.add_argument("--remote-base-url", default=DEFAULT_REMOTE_BASE_URL, help="Remote CDN base URL.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="Preview planned copies and index without writing.")
    mode.add_argument("--apply", action="store_true", help="Copy files and write audios.json.")
    return parser.parse_args()


def normalize_text(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[_\-]+", " ", value)
    value = re.sub(r"[^a-z0-9\s]+", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def match_intent(path: Path) -> AudioIntent | None:
    normalized = normalize_text(path.stem)
    for prompt_prefix, event in PROMPT_PREFIX_TO_EVENT:
        if normalized.startswith(normalize_text(prompt_prefix)):
            return INTENT_BY_EVENT[event]
    return None


def empty_index() -> dict[str, list[dict[str, str]]]:
    return {group: [] for group in GROUP_ORDER}


def url_join(base_url: str, location: str) -> str:
    return base_url.rstrip("/") + "/" + location.lstrip("/")


def parse_variant_number(stem: str, event: str) -> int | None:
    match = re.fullmatch(rf"{re.escape(event)}_(\d+)", stem)
    if match is None:
        return None
    return int(match.group(1))


def next_variant_number(audio_root: Path, intent: AudioIntent) -> int:
    folder = audio_root / intent.folder
    numbers = []
    for candidate in folder.glob(f"{intent.event}_*{MP3_SUFFIX}"):
        number = parse_variant_number(candidate.stem, intent.event)
        if number is not None:
            numbers.append(number)
    return max(numbers, default=0) + 1


def audio_item(intent: AudioIntent, location: str, remote_base_url: str) -> dict[str, str]:
    return {
        "name": Path(location).stem,
        "url": url_join(remote_base_url, location),
        "location": location,
        "usage": intent.usage,
        "audio_type": intent.audio_type,
    }


def scan_clean_audio(audio_root: Path, remote_base_url: str) -> dict[str, list[dict[str, str]]]:
    index = empty_index()
    for intent in INTENTS:
        folder = audio_root / intent.folder
        if not folder.exists():
            continue
        for path in sorted(folder.glob(f"{intent.event}_*{MP3_SUFFIX}")):
            location = path.relative_to(audio_root).as_posix()
            index[intent.group].append(audio_item(intent, location, remote_base_url))
    return index


def incoming_files(incoming_dir: Path) -> list[Path]:
    if not incoming_dir.exists():
        return []
    return sorted(
        path
        for path in incoming_dir.iterdir()
        if path.is_file() and path.suffix.lower() == MP3_SUFFIX
    )


def process_incoming(
    audio_root: Path,
    incoming_dir: Path,
    unmatched_dir: Path,
    remote_base_url: str,
    apply: bool,
) -> tuple[dict[str, list[dict[str, str]]], list[dict[str, str]], list[dict[str, str]]]:
    planned_index = empty_index()
    planned_copies: list[dict[str, str]] = []
    unmatched: list[dict[str, str]] = []
    variant_counters: dict[str, int] = {}

    for source in incoming_files(incoming_dir):
        intent = match_intent(source)
        if intent is None:
            unmatched_location = f"unmatched/{source.name}"
            unmatched.append({"source": str(source), "target": unmatched_location})
            if apply:
                unmatched_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, unmatched_dir / source.name)
            continue

        number = variant_counters.get(intent.event)
        if number is None:
            number = next_variant_number(audio_root, intent)
        variant_counters[intent.event] = number + 1

        target_name = f"{intent.event}_{number:02d}{MP3_SUFFIX}"
        relative_location = f"{intent.folder}/{target_name}"
        target = audio_root / relative_location

        planned_copies.append(
            {
                "source": str(source),
                "target": str(target),
                "group": intent.group,
            }
        )
        planned_index[intent.group].append(audio_item(intent, relative_location, remote_base_url))

        if apply:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)

    return planned_index, planned_copies, unmatched


def merge_indexes(
    existing_index: dict[str, list[dict[str, str]]],
    planned_index: dict[str, list[dict[str, str]]],
) -> dict[str, list[dict[str, str]]]:
    merged = empty_index()
    for group in GROUP_ORDER:
        merged[group] = [*existing_index.get(group, []), *planned_index.get(group, [])]
    return merged


def write_json(path: Path, payload: dict[str, list[dict[str, str]]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    if not args.apply and not args.dry_run:
        args.dry_run = True

    audio_root = Path(args.audio_root).resolve()
    incoming_dir = Path(args.incoming).resolve()
    output_path = Path(args.output).resolve()
    unmatched_dir = DEFAULT_UNMATCHED_DIR if Path(args.audio_root) == DEFAULT_AUDIO_ROOT else audio_root / "unmatched"

    for group in GROUP_ORDER:
        intent = INTENT_BY_GROUP[group]
        if args.apply:
            (audio_root / intent.folder).mkdir(parents=True, exist_ok=True)

    if args.apply:
        incoming_dir.mkdir(parents=True, exist_ok=True)
        unmatched_dir.mkdir(parents=True, exist_ok=True)

    existing_index = scan_clean_audio(audio_root, args.remote_base_url)
    planned_index, planned_copies, unmatched = process_incoming(
        audio_root=audio_root,
        incoming_dir=incoming_dir,
        unmatched_dir=unmatched_dir,
        remote_base_url=args.remote_base_url,
        apply=args.apply,
    )
    merged_index = merge_indexes(existing_index, planned_index)

    if args.apply:
        write_json(output_path, merged_index)

    result = {
        "mode": "apply" if args.apply else "dry_run",
        "incoming_dir": str(incoming_dir),
        "audio_root": str(audio_root),
        "output_path": str(output_path),
        "remote_base_url": args.remote_base_url,
        "planned_copy_count": len(planned_copies),
        "unmatched_count": len(unmatched),
        "planned_copies": planned_copies,
        "unmatched": unmatched,
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()