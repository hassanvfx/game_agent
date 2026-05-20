#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MECHANICS_PATH = ROOT / "first_100_mechanics_rows.json"
REFERENCE_MANIFEST_PATH = ROOT / "curated_limit2_prompt_only_manifest.json"
OUT_MANIFEST_PATH = ROOT / "vatsal_top_mechanics.json"
OUT_ANNOTATIONS_PATH = ROOT / "vatsal_top_mechanics.annotations.json"

MOBILE_SUFFIX = (
    " Designed for one-thumb mobile play with touch-friendly interactions, responsive readability, "
    "fast onboarding, and portrait-first UX tuned for iOS and Android in the 4:7 to 9:16 range."
)

GENERIC_GAME_TAGS = {
    "casual",
    "addictive",
    "simulator",
    "arcade",
    "puzzle",
    "multiplayer",
    "driving",
    "runner",
    "tycoon",
    "idle",
    "survival",
    "shooter",
    "platformer",
    "strategy",
    "defense",
}

INSPIRATION_PALETTE = [
    {"source_prompt": "Mario platformer", "brand": "Mario", "clusters": ["cozy", "action", "arcade"]},
    {"source_prompt": "Zelda RPG adventure", "brand": "Zelda", "clusters": ["fantasy", "puzzle", "adventure"]},
    {"source_prompt": "Pokemon creature-collector RPG", "brand": "Pokémon", "clusters": ["cozy", "fantasy", "collecting"]},
    {"source_prompt": "Sonic high-speed runner platformer", "brand": "Sonic", "clusters": ["action", "speed", "arcade"]},
    {"source_prompt": "Grand Theft Auto open-city action", "brand": "Grand Theft Auto", "clusters": ["action", "chaos", "satire"]},
    {"source_prompt": "Harry Potter wizard-school adventure", "brand": "Harry Potter", "clusters": ["fantasy", "cozy", "magic"]},
    {"source_prompt": "Mean Girls social-status strategy", "brand": "Mean Girls", "clusters": ["social", "fashion", "comedy"]},
    {"source_prompt": "Stranger Things sci-fi horror adventure", "brand": "Stranger Things", "clusters": ["horror", "mystery", "retro"]},
    {"source_prompt": "Hocus Pocus witchy Halloween party", "brand": "Hocus Pocus", "clusters": ["horror", "cozy", "magic"]},
    {"source_prompt": "Studio Ghibli fantasy exploration", "brand": "Studio Ghibli", "clusters": ["cozy", "fantasy", "aesthetic"]},
    {"source_prompt": "Spider-Verse comic-pop action", "brand": "Spider-Verse", "clusters": ["style", "action", "youth"]},
    {"source_prompt": "vaporwave Y2K internet-aesthetic", "brand": "vaporwave Y2K internet culture", "clusters": ["style", "retro", "internet"]},
    {"source_prompt": "workplace cringe comedy", "brand": "The Office", "clusters": ["social", "comedy", "satire"]},
    {"source_prompt": "Rick and Morty sci-fi absurdist", "brand": "Rick and Morty", "clusters": ["comedy", "chaos", "sci-fi"]},
    {"source_prompt": "cyberpunk rebellion chase", "brand": "Akira", "clusters": ["style", "action", "cyber"]},
    {"source_prompt": "Sailor Moon magical-girl", "brand": "Sailor Moon", "clusters": ["cozy", "magic", "fashion"]},
    {"source_prompt": "Batman comic-book action stealth", "brand": "Batman", "clusters": ["action", "dark", "stealth"]},
    {"source_prompt": "Shrek fairy-tale parody adventure", "brand": "Shrek", "clusters": ["comedy", "fantasy", "satire"]},
    {"source_prompt": "Gravity Falls paranormal mystery", "brand": "Gravity Falls", "clusters": ["mystery", "cozy", "weird"]},
    {"source_prompt": "retro-future comedy", "brand": "Futurama", "clusters": ["retro", "sci-fi", "comedy"]},
    {"source_prompt": "surreal psychedelic visual", "brand": "Pink Floyd", "clusters": ["style", "surreal", "music"]},
    {"source_prompt": "anime lo-fi neon city", "brand": "anime lo-fi neon city", "clusters": ["style", "cozy", "urban"]},
]


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_token(value: str) -> str:
    return value.strip().casefold()


def gather_row_text(row: dict[str, object]) -> str:
    parts: list[str] = [str(row.get("mechanic") or ""), str(row.get("player_context") or "")]
    for key in ("feel", "game_tags", "aesthetic_tags", "meme_tags", "hashtags"):
        for item in row.get(key, []):
            parts.append(str(item))
    return " ".join(parts).casefold()


CLUSTER_KEYWORDS: dict[str, list[str]] = {
    "cozy": ["cozy", "relaxing", "before bed", "weekend chill", "stress relief", "anti anxiety", "kawaii", "pastel", "cottagecore", "plushie", "sanrio", "animal crossing"],
    "action": ["competitive", "futuristic", "leaderboard", "shooter", "runner", "driving", "battle", "sniper", "parkour", "defense", "after work"],
    "horror": ["horror", "sleepover", "monster", "zombie", "escape", "dark academia", "gothcore", "analog horror", "eldritch", "vampire", "backrooms", "liminal"],
    "social": ["dress up", "fashion", "makeover", "love", "story", "tiktok", "streamer", "office", "school", "restaurant", "cooking", "meme quiz"],
    "style": ["vaporwave", "cyberpunk", "synthwave", "chrome aesthetic", "anime aesthetic", "glitchcore", "y2k", "neon aesthetic", "neon noir", "digital aesthetic"],
    "fantasy": ["builder", "kingdom", "farm", "island", "world", "magic", "wizard", "fantasy", "rpg", "mythic"],
    "puzzle": ["puzzle", "brain teaser", "sort", "block", "quiz", "mahjong", "solitaire", "word", "match 3", "liquid sort", "drawing", "ludo"],
    "comedy": ["meme", "brainrot", "awkward", "cringe", "satire", "chaos", "funny", "humor"],
}


def choose_clusters(row: dict[str, object]) -> list[str]:
    text = gather_row_text(row)
    scores: dict[str, int] = {}
    for cluster, keywords in CLUSTER_KEYWORDS.items():
        scores[cluster] = sum(1 for keyword in keywords if keyword in text)
    ordered = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
    primary = ordered[0][0] if ordered and ordered[0][1] > 0 else "cozy"
    secondary = ordered[1][0] if len(ordered) > 1 and ordered[1][1] > 0 else {
        "cozy": "fantasy",
        "action": "style",
        "horror": "mystery",
        "social": "cozy",
        "style": "action",
        "fantasy": "cozy",
        "puzzle": "cozy",
        "comedy": "social",
    }.get(primary, "cozy")
    if secondary == "mystery":
        secondary = "horror"
    return [primary, secondary]


def index_inspirations(reference_prompts: set[str]) -> dict[str, list[dict[str, object]]]:
    by_cluster: dict[str, list[dict[str, object]]] = {}
    for entry in INSPIRATION_PALETTE:
        if entry["source_prompt"] not in reference_prompts:
            continue
        for cluster in entry["clusters"]:
            by_cluster.setdefault(cluster, []).append(entry)
    return by_cluster


def choose_inspirations(row: dict[str, object], inspirations_by_cluster: dict[str, list[dict[str, object]]]) -> list[dict[str, object]]:
    primary, secondary = choose_clusters(row)
    rank = int(row["rank"])
    primary_pool = inspirations_by_cluster.get(primary) or INSPIRATION_PALETTE
    secondary_pool = inspirations_by_cluster.get(secondary) or inspirations_by_cluster.get(primary) or INSPIRATION_PALETTE
    first = primary_pool[(rank - 1) % len(primary_pool)]
    second = secondary_pool[(rank + 2) % len(secondary_pool)]
    if first["source_prompt"] == second["source_prompt"] and len(secondary_pool) > 1:
        second = secondary_pool[(rank + 3) % len(secondary_pool)]
    return [first, second]


def prompt_candidates(row: dict[str, object]) -> list[str]:
    mechanic = str(row["mechanic"]).strip()
    candidates: list[str] = []
    seen: set[str] = set()
    for value in [mechanic, *[str(item) for item in row.get("game_tags", [])]]:
        cleaned = " ".join(value.strip().split())
        if not cleaned:
            continue
        key = cleaned.casefold()
        if key in seen:
            continue
        seen.add(key)
        candidates.append(cleaned)

    filtered = [item for item in candidates if normalize_token(item) not in GENERIC_GAME_TAGS]
    if not filtered:
        filtered = candidates or [mechanic]
    if len(filtered) == 1:
        filtered.append(filtered[0])
    return filtered[:2]


def title_case_prompt(prompt: str) -> str:
    words = prompt.split()
    return " ".join(word.capitalize() if word.islower() else word for word in words)


def build_remix_prompt(prompt: str, row: dict[str, object], inspiration: dict[str, object]) -> str:
    prompt_title = title_case_prompt(prompt)
    mechanic = str(row["mechanic"])
    feel = ", ".join(str(item) for item in row.get("feel", [])[:3])
    context = str(row.get("player_context") or "")
    aesthetics = ", ".join(str(item) for item in row.get("aesthetic_tags", [])[:3])
    memes = ", ".join(str(item) for item in row.get("meme_tags", [])[:2])
    game_tags = ", ".join(str(item) for item in row.get("game_tags", [])[:3])
    inspiration_brand = str(inspiration["brand"])
    return (
        f"{prompt_title}. A satirical game inspired by {inspiration_brand} built around {mechanic} play, with {feel} energy, "
        f"{context} session design, search-friendly hooks like {game_tags}, aesthetics like {aesthetics}, and meme-tone cues such as {memes}."
        f"{MOBILE_SUFFIX}"
    )


def main() -> int:
    mechanics_payload = load_json(MECHANICS_PATH)
    reference_payload = load_json(REFERENCE_MANIFEST_PATH)
    rows = mechanics_payload.get("rows") if isinstance(mechanics_payload, dict) else None
    runs = reference_payload.get("runs") if isinstance(reference_payload, dict) else None
    if not isinstance(rows, list):
        raise SystemExit(f"Invalid mechanics payload in {MECHANICS_PATH}")
    if not isinstance(runs, list):
        raise SystemExit(f"Invalid reference manifest in {REFERENCE_MANIFEST_PATH}")

    reference_prompts = {
        str(item.get("prompt")).strip()
        for item in runs
        if isinstance(item, dict) and isinstance(item.get("prompt"), str)
    }
    inspirations_by_cluster = index_inspirations(reference_prompts)

    manifest_runs: list[dict[str, object]] = []
    annotations: list[dict[str, object]] = []

    for row in rows:
        if not isinstance(row, dict):
            continue
        inspirations = choose_inspirations(row, inspirations_by_cluster)
        prompts = prompt_candidates(row)
        for variant_index, (prompt, inspiration) in enumerate(zip(prompts, inspirations), start=1):
            remix_prompt = build_remix_prompt(prompt, row, inspiration)
            manifest_runs.append({
                "prompt": prompt,
                "remix_prompt": remix_prompt,
            })
            annotations.append(
                {
                    "run_index": len(manifest_runs),
                    "variant_index": variant_index,
                    "rank": row["rank"],
                    "mechanic": row["mechanic"],
                    "prompt": prompt,
                    "inspiration_source_prompt": inspiration["source_prompt"],
                    "inspiration_brand": inspiration["brand"],
                    "inspiration_clusters": inspiration["clusters"],
                    "feel": row.get("feel", []),
                    "player_context": row.get("player_context"),
                    "game_tags": row.get("game_tags", []),
                    "aesthetic_tags": row.get("aesthetic_tags", []),
                    "meme_tags": row.get("meme_tags", []),
                    "hashtags": row.get("hashtags", []),
                }
            )

    manifest_payload = {
        "defaults": {
            "limit": 2,
            "publish": True,
            "upload": False,
            "poll_seconds": 60,
            "matcher_mode": "v2",
        },
        "runs": manifest_runs,
    }
    annotations_payload = {
        "source_mechanics_path": str(MECHANICS_PATH),
        "reference_manifest_path": str(REFERENCE_MANIFEST_PATH),
        "total_runs": len(manifest_runs),
        "items": annotations,
    }

    OUT_MANIFEST_PATH.write_text(json.dumps(manifest_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    OUT_ANNOTATIONS_PATH.write_text(json.dumps(annotations_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(
        json.dumps(
            {
                "manifest_path": str(OUT_MANIFEST_PATH),
                "annotations_path": str(OUT_ANNOTATIONS_PATH),
                "run_count": len(manifest_runs),
                "sample_runs": manifest_runs[:4],
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())