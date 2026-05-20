#!/usr/bin/env python3
"""
Generate curated home/feed collection manifests from app.json.

This script intentionally emits mostly ID-based outputs so the app can later
resolve ids through bundled metadata / reverse index logic.

Outputs:
- home_collections_ids.json
- home_collections_report.json
- home_collections_report.md
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import Any


BASE_PUBLIC_URL = "https://friendjam-game-assets.jabali.ai/games-prod/play/"
WORD_RE = re.compile(r"[a-zA-Z0-9][a-zA-Z0-9&'\-]+")


@dataclass
class GameRecord:
    entry_id: str
    title: str
    description: str
    prompt: str
    blueprint: str
    playable_url: str | None
    screenshot_urls: list[str] = field(default_factory=list)
    tags: dict[str, list[str]] = field(default_factory=dict)

    @property
    def combined_text(self) -> str:
        parts = [self.title, self.description, self.prompt, self.blueprint]
        for values in self.tags.values():
            parts.extend(values)
        return " \n ".join(part for part in parts if part).lower()

    @property
    def all_tag_values(self) -> list[str]:
        values: list[str] = []
        for tag_values in self.tags.values():
            values.extend(tag_values)
        return values


@dataclass(frozen=True)
class EditorialShelfDefinition:
    shelf_id: str
    title: str
    description: str
    strategy_type: str
    score_names: tuple[str, ...]
    include_keywords: tuple[str, ...] = ()
    include_tag_keywords: tuple[str, ...] = ()
    required_keywords: tuple[str, ...] = ()
    excluded_keywords: tuple[str, ...] = ()
    excluded_tag_keywords: tuple[str, ...] = ()
    preferred_tag_groups: tuple[str, ...] = ()
    min_screenshot_count: int = 0
    min_total_score: float = 0.0
    min_entries: int = 6


def normalize_tag_list(value: Any) -> list[str]:
    if not value:
        return []
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    return [str(value).strip()] if str(value).strip() else []


def public_url(relative_path: str | None) -> str | None:
    if not relative_path:
        return None
    return BASE_PUBLIC_URL + relative_path.lstrip("/")


def load_catalog(path: Path) -> list[GameRecord]:
    raw = json.loads(path.read_text())
    tag_fields = [
        "mechanic_tags",
        "semantic_tags",
        "mood_tags",
        "setting_tags",
        "character_tags",
        "games_tags",
        "franchise_tags",
    ]

    records: list[GameRecord] = []
    for entry_id, item in raw.items():
        tags = {field: normalize_tag_list(item.get(field)) for field in tag_fields}
        screenshot_urls = []
        for value in normalize_tag_list(item.get("screenshots")):
            url = public_url(value)
            if url:
                screenshot_urls.append(url)

        playable_url = public_url(item.get("public_index_html") or item.get("published_path"))

        records.append(
            GameRecord(
                entry_id=entry_id,
                title=(item.get("title") or "").strip(),
                description=(item.get("description") or "").strip(),
                prompt=(item.get("prompt") or "").strip(),
                blueprint=(item.get("blueprint") or "").strip(),
                playable_url=playable_url,
                screenshot_urls=screenshot_urls,
                tags=tags,
            )
        )

    return records


def score_keywords(record: GameRecord, keywords: list[str]) -> float:
    haystack = record.combined_text
    return float(sum(1 for keyword in keywords if keyword.lower() in haystack))


def tag_match_score(record: GameRecord, keywords: list[str]) -> float:
    all_tags = " | ".join(record.all_tag_values).lower()
    return float(sum(1 for keyword in keywords if keyword.lower() in all_tags))


def screenshot_score(record: GameRecord) -> float:
    return min(len(record.screenshot_urls), 5) / 5.0


def count_tag_matches(record: GameRecord, keywords: tuple[str, ...]) -> int:
    all_tags = " | ".join(record.all_tag_values).lower()
    return sum(1 for keyword in keywords if keyword.lower() in all_tags)


def count_text_matches(record: GameRecord, keywords: tuple[str, ...]) -> int:
    haystack = record.combined_text
    return sum(1 for keyword in keywords if keyword.lower() in haystack)


def combined_signal_matches(record: GameRecord, keywords: tuple[str, ...]) -> int:
    haystack = f"{record.combined_text} || {' | '.join(record.all_tag_values).lower()}"
    return sum(1 for keyword in keywords if keyword.lower() in haystack)


def distinct_tag_group_matches(record: GameRecord, tag_groups: tuple[str, ...]) -> int:
    count = 0
    for tag_group in tag_groups:
        if record.tags.get(tag_group):
            count += 1
    return count


def compute_scores(record: GameRecord) -> dict[str, float]:
    mechanics = " ".join(record.tags.get("mechanic_tags", [])).lower()
    moods = " ".join(record.tags.get("mood_tags", [])).lower()
    franchise_count = len(record.tags.get("franchise_tags", []))
    semantic_count = len(record.tags.get("semantic_tags", []))
    setting_count = len(record.tags.get("setting_tags", []))
    games_count = len(record.tags.get("games_tags", []))
    character_count = len(record.tags.get("character_tags", []))

    viral_keywords = [
        "meme", "brainrot", "viral", "cute", "chaos", "cat", "romance",
        "date", "dress", "gift", "tap", "clicker", "runner"
    ]
    onboarding_keywords = [
        "simple", "easy", "quick", "one-button", "one screen", "tap",
        "responsive", "short-session", "accessible", "readable", "immediate"
    ]
    trend_keywords = [
        "viral", "trend", "trending", "meme", "brainrot", "chaos", "absurd",
        "cute", "cat", "fashion", "date", "dress", "celebrity"
    ]
    mechanic_keywords = [
        "runner", "clicker", "puzzle", "memory", "quiz", "match", "shooter",
        "boss", "arcade", "fight", "survival", "builder", "management"
    ]
    cozy_keywords = [
        "cozy", "calm", "soothing", "asmr", "comfort", "satisfying", "gentle",
        "dreamy", "soft", "relaxing"
    ]
    franchise_keywords = [
        "harry potter", "rick and morty", "cut the rope", "sonic", "barbie",
        "gacha", "wizard", "portal", "multiverse", "hogwarts"
    ]
    fantasy_keywords = [
        "wizard", "magic", "spell", "fantasy", "portal", "multiverse",
        "creature", "dragon", "kingdom"
    ]

    viral = (
        score_keywords(record, viral_keywords) * 1.6
        + tag_match_score(record, ["meme", "brainrot", "cute", "chaos", "romance"]) * 1.2
        + screenshot_score(record) * 3.0
    )

    onboarding = (
        score_keywords(record, onboarding_keywords) * 1.4
        + screenshot_score(record) * 2.0
        + (1.5 if any(value in mechanics for value in ["runner", "clicker", "memory", "match", "puzzle"]) else 0.0)
    )

    franchise = (
        franchise_count * 2.2
        + tag_match_score(record, franchise_keywords) * 1.8
        + score_keywords(record, ["harry potter", "rick and morty", "mother's day", "momverse", "wizard", "portal"]) * 1.3
    )

    visual = (
        screenshot_score(record) * 4.0
        + semantic_count * 0.2
        + len(record.tags.get("mood_tags", [])) * 0.2
        + setting_count * 0.15
    )

    cozy = (
        tag_match_score(record, cozy_keywords) * 2.0
        + (1.0 if any(value in moods for value in ["cozy", "calm", "soothing", "dreamy", "gentle"]) else 0.0)
    )

    action = (
        tag_match_score(record, ["boss", "shooter", "arcade", "fight", "runner", "survival"]) * 1.8
        + score_keywords(record, ["boss", "combat", "pursuit", "survival", "fight", "shooter"]) * 1.1
    )

    trend = (
        score_keywords(record, trend_keywords) * 1.5
        + tag_match_score(record, trend_keywords) * 1.2
        + screenshot_score(record) * 1.8
    )

    mechanic = (
        score_keywords(record, mechanic_keywords) * 1.2
        + tag_match_score(record, mechanic_keywords) * 1.8
        + len(record.tags.get("mechanic_tags", [])) * 0.8
    )

    mood = (
        score_keywords(record, cozy_keywords + ["chaotic", "romantic", "dreamy", "spooky"]) * 1.0
        + tag_match_score(record, cozy_keywords + ["chaotic", "romantic", "dreamy", "spooky"]) * 1.8
        + len(record.tags.get("mood_tags", [])) * 0.8
    )

    semantic = (
        semantic_count * 0.9
        + games_count * 0.7
        + setting_count * 0.6
        + character_count * 0.5
    )

    fantasy = (
        score_keywords(record, fantasy_keywords) * 1.2
        + tag_match_score(record, fantasy_keywords) * 1.5
        + franchise_count * 0.6
    )

    return {
        "viral": round(viral, 3),
        "onboarding": round(onboarding, 3),
        "franchise": round(franchise, 3),
        "visual": round(visual, 3),
        "cozy": round(cozy, 3),
        "action": round(action, 3),
        "trend": round(trend, 3),
        "mechanic": round(mechanic, 3),
        "mood": round(mood, 3),
        "semantic": round(semantic, 3),
        "fantasy": round(fantasy, 3),
    }


def ranked_records(records: list[GameRecord], score_name: str) -> list[tuple[GameRecord, dict[str, float]]]:
    scored = [(record, compute_scores(record)) for record in records]
    return sorted(scored, key=lambda item: item[1][score_name], reverse=True)


def minimal_payload(record: GameRecord, scores: dict[str, float]) -> dict[str, Any]:
    return {
        "entry_id": record.entry_id,
        "title": record.title,
        "scores": scores,
    }


def feed_definitions() -> list[EditorialShelfDefinition]:
    return [
        EditorialShelfDefinition(
            shelf_id="for-you-tonight",
            title="For You Tonight",
            description="Instantly readable picks with broad appeal and fast payoff.",
            strategy_type="trend",
            score_names=("trend", "onboarding", "visual"),
            include_keywords=("easy", "quick", "tap", "runner", "clicker", "viral", "cute"),
            include_tag_keywords=("runner", "clicker", "cute", "meme"),
            min_screenshot_count=1,
            min_total_score=6.0,
        ),
        EditorialShelfDefinition(
            shelf_id="franchise-fever",
            title="Franchise Fever",
            description="Recognizable worlds, fanfic energy, and familiar hooks.",
            strategy_type="franchise",
            score_names=("franchise", "visual", "trend"),
            include_keywords=("harry potter", "rick and morty", "wizard", "portal", "multiverse", "barbie", "sonic"),
            include_tag_keywords=("harry potter", "rick and morty", "wizard", "portal", "barbie", "sonic"),
            preferred_tag_groups=("franchise_tags",),
            min_total_score=5.0,
        ),
        EditorialShelfDefinition(
            shelf_id="cozy-corners",
            title="Cozy Corners",
            description="Soft, satisfying, low-pressure games with comfort energy.",
            strategy_type="mood",
            score_names=("cozy", "mood", "visual"),
            include_keywords=("cozy", "soothing", "asmr", "comfort", "relaxing", "satisfying"),
            include_tag_keywords=("cozy", "calm", "soothing", "dreamy", "gentle", "comfort"),
            preferred_tag_groups=("mood_tags",),
            min_total_score=4.0,
        ),
        EditorialShelfDefinition(
            shelf_id="brainy-little-loops",
            title="Brainy Little Loops",
            description="Short puzzle, quiz, memory, and matching loops that feel clever fast.",
            strategy_type="mechanic",
            score_names=("mechanic", "onboarding", "visual"),
            include_keywords=("puzzle", "memory", "quiz", "match", "word", "search"),
            include_tag_keywords=("puzzle", "memory", "quiz", "match", "word"),
            preferred_tag_groups=("mechanic_tags",),
            min_total_score=5.0,
        ),
        EditorialShelfDefinition(
            shelf_id="arcade-after-dark",
            title="Arcade After Dark",
            description="Louder, faster, bossy picks with survival and reflex energy.",
            strategy_type="mechanic",
            score_names=("action", "mechanic", "visual"),
            include_keywords=("boss", "arcade", "fight", "combat", "shooter", "survival", "runner"),
            include_tag_keywords=("boss", "arcade", "fight", "shooter", "survival", "runner"),
            preferred_tag_groups=("mechanic_tags", "semantic_tags"),
            min_total_score=5.0,
        ),
        EditorialShelfDefinition(
            shelf_id="dreamworld-drift",
            title="Dreamworld Drift",
            description="Fantasy, magical, and world-rich picks with stronger scene-building.",
            strategy_type="theme",
            score_names=("fantasy", "visual", "semantic"),
            include_keywords=("wizard", "magic", "fantasy", "portal", "multiverse", "kingdom", "creature"),
            include_tag_keywords=("wizard", "magic", "fantasy", "portal", "kingdom", "creature"),
            preferred_tag_groups=("setting_tags", "semantic_tags", "franchise_tags"),
            min_total_score=4.0,
        ),
        EditorialShelfDefinition(
            shelf_id="makeover-mayhem",
            title="Makeover Mayhem",
            description="Fashion, romance, expression, and dramatic play.",
            strategy_type="theme",
            score_names=("trend", "mood", "visual"),
            include_keywords=("romance", "dress", "makeover", "date", "fashion", "gift"),
            include_tag_keywords=("romance", "dress", "makeover", "date", "fashion"),
            preferred_tag_groups=("mood_tags", "semantic_tags"),
            min_total_score=4.0,
        ),
        EditorialShelfDefinition(
            shelf_id="tiny-worlds-big-energy",
            title="Tiny Worlds, Big Energy",
            description="Builder, sandbox, management, and system-heavy toyboxes.",
            strategy_type="mechanic",
            score_names=("mechanic", "semantic", "visual"),
            include_keywords=("builder", "sandbox", "management", "collector", "village", "tycoon", "farm"),
            include_tag_keywords=("builder", "sandbox", "management", "collector", "village", "tycoon", "farm"),
            preferred_tag_groups=("mechanic_tags", "setting_tags"),
            min_total_score=4.0,
        ),
    ]


def hero_definitions() -> list[EditorialShelfDefinition]:
    return [
        EditorialShelfDefinition(
            shelf_id="hero-franchise-worlds",
            title="Familiar Worlds, Strange Twists",
            description="Big recognizable hooks with strong shelf presence.",
            strategy_type="franchise",
            score_names=("franchise", "visual", "trend"),
            include_keywords=("harry potter", "rick and morty", "wizard", "portal", "multiverse", "barbie", "sonic"),
            include_tag_keywords=("harry potter", "rick and morty", "wizard", "portal", "barbie", "sonic"),
            preferred_tag_groups=("franchise_tags", "semantic_tags"),
            min_total_score=6.0,
            min_entries=3,
        ),
        EditorialShelfDefinition(
            shelf_id="hero-trend-chaos",
            title="Internet Energy Right Now",
            description="Meme-forward, weird, surprising, and highly clickable.",
            strategy_type="trend",
            score_names=("trend", "viral", "visual"),
            include_keywords=("meme", "brainrot", "viral", "chaos", "cute", "absurd", "cat"),
            include_tag_keywords=("meme", "brainrot", "cute", "chaos", "cat"),
            min_total_score=6.0,
            min_entries=3,
        ),
        EditorialShelfDefinition(
            shelf_id="hero-worlds-to-fall-into",
            title="Worlds to Fall Into",
            description="Atmospheric scene-rich picks with fantasy or immersive settings.",
            strategy_type="theme",
            score_names=("fantasy", "visual", "semantic"),
            include_keywords=("wizard", "magic", "fantasy", "portal", "kingdom", "creature", "dream"),
            include_tag_keywords=("wizard", "magic", "fantasy", "portal", "kingdom", "creature"),
            preferred_tag_groups=("setting_tags", "semantic_tags", "franchise_tags"),
            min_total_score=5.0,
            min_entries=3,
        ),
    ]


def compute_editorial_fit(
    record: GameRecord,
    scores: dict[str, float],
    definition: EditorialShelfDefinition,
) -> float:
    include_hits = combined_signal_matches(record, definition.include_keywords)
    include_tag_hits = count_tag_matches(record, definition.include_tag_keywords)
    required_hits = combined_signal_matches(record, definition.required_keywords)
    excluded_hits = combined_signal_matches(record, definition.excluded_keywords)
    excluded_tag_hits = count_tag_matches(record, definition.excluded_tag_keywords)
    tag_group_hits = distinct_tag_group_matches(record, definition.preferred_tag_groups)

    if definition.required_keywords and required_hits == 0:
        return -1.0
    if excluded_hits > 0 or excluded_tag_hits > 0:
        return -1.0
    if len(record.screenshot_urls) < definition.min_screenshot_count:
        return -1.0

    base_score = sum(scores.get(score_name, 0.0) for score_name in definition.score_names)
    if base_score < definition.min_total_score:
        return -1.0

    fit_score = (
        base_score
        + include_hits * 2.4
        + include_tag_hits * 2.1
        + tag_group_hits * 1.25
        + len(record.screenshot_urls) * 0.45
    )

    return round(fit_score, 4)


def build_editorial_collection(
    definition: EditorialShelfDefinition,
    records: list[GameRecord],
) -> dict[str, Any] | None:
    ranked: list[tuple[GameRecord, dict[str, float], float]] = []

    for record in records:
        scores = compute_scores(record)
        fit_score = compute_editorial_fit(record, scores, definition)
        if fit_score < 0:
            continue
        ranked.append((record, scores, fit_score))

    ranked.sort(
        key=lambda item: (
            item[2],
            sum(item[1].get(score_name, 0.0) for score_name in definition.score_names),
            item[1]["visual"],
            item[0].entry_id,
        ),
        reverse=True,
    )

    if len(ranked) < definition.min_entries:
        return None

    featured_items = ranked[:9]
    game_items = ranked[:50]

    return {
        "id": definition.shelf_id,
        "title": definition.title,
        "description": definition.description,
        "strategy_type": definition.strategy_type,
        "score_names": list(definition.score_names),
        "candidate_pool_ids": [record.entry_id for record, _, _ in game_items],
        "game_ids": [record.entry_id for record, _, _ in game_items],
        "featured_game_ids": [record.entry_id for record, _, _ in featured_items],
        "top_candidates": [
            {
                **minimal_payload(record, scores),
                "editorial_fit": fit_score,
            }
            for record, scores, fit_score in ranked[:12]
        ],
        "rules": {
            "include_keywords": list(definition.include_keywords),
            "include_tag_keywords": list(definition.include_tag_keywords),
            "required_keywords": list(definition.required_keywords),
            "excluded_keywords": list(definition.excluded_keywords),
            "excluded_tag_keywords": list(definition.excluded_tag_keywords),
            "preferred_tag_groups": list(definition.preferred_tag_groups),
            "min_screenshot_count": definition.min_screenshot_count,
            "min_total_score": definition.min_total_score,
        },
    }


def build_feed_collections(records: list[GameRecord]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}

    for definition in feed_definitions():
        collection = build_editorial_collection(definition, records)
        if collection:
            result[definition.shelf_id] = collection

    return result


def build_hero_collections(records: list[GameRecord]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}

    for definition in hero_definitions():
        collection = build_editorial_collection(definition, records)
        if collection:
            result[definition.shelf_id] = collection

    return result


def build_30_day_rotation(
    hero_collections: dict[str, dict[str, Any]],
    feed_collections: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    hero_ids = list(hero_collections.keys()) or ["hero-franchise-worlds"]
    feed_ids = list(feed_collections.keys()) or ["for-you-tonight"]

    start = date.today()
    rotation: list[dict[str, Any]] = []

    for offset in range(30):
        current_day = start + timedelta(days=offset)
        hero_slots = [hero_ids[(offset + index) % len(hero_ids)] for index in range(min(3, len(hero_ids)))]
        feed_slots = [feed_ids[(offset * 2 + index) % len(feed_ids)] for index in range(min(3, len(feed_ids)))]

        rotation.append(
            {
                "date": current_day.isoformat(),
                "hero_collection_ids": hero_slots,
                "feed_collection_ids": feed_slots,
            }
        )

    return rotation


def build_report(
    records: list[GameRecord],
    hero_collections: dict[str, dict[str, Any]],
    feed_collections: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    keyword_counter = Counter()
    mechanic_counter = Counter()
    mood_counter = Counter()
    franchise_counter = Counter()
    strategy_counter = Counter()

    for record in records:
        keyword_counter.update(token.lower() for token in WORD_RE.findall(record.combined_text) if len(token) > 2)
        mechanic_counter.update(record.tags.get("mechanic_tags", []))
        mood_counter.update(record.tags.get("mood_tags", []))
        franchise_counter.update(record.tags.get("franchise_tags", []))

    for collection in [*hero_collections.values(), *feed_collections.values()]:
        strategy_counter.update([collection.get("strategy_type", "unknown")])

    return {
        "game_count": len(records),
        "top_keywords": [{"keyword": key, "count": count} for key, count in keyword_counter.most_common(60)],
        "top_mechanics": [{"mechanic": key, "count": count} for key, count in mechanic_counter.most_common(40)],
        "top_moods": [{"mood": key, "count": count} for key, count in mood_counter.most_common(40)],
        "top_franchises": [{"franchise": key, "count": count} for key, count in franchise_counter.most_common(40)],
        "top_onboarding_candidates": [
            minimal_payload(record, scores) for record, scores in ranked_records(records, "onboarding")[:15]
        ],
        "top_viral_candidates": [
            minimal_payload(record, scores) for record, scores in ranked_records(records, "viral")[:15]
        ],
        "top_visual_candidates": [
            minimal_payload(record, scores) for record, scores in ranked_records(records, "visual")[:15]
        ],
        "top_trend_candidates": [
            minimal_payload(record, scores) for record, scores in ranked_records(records, "trend")[:15]
        ],
        "top_mechanic_candidates": [
            minimal_payload(record, scores) for record, scores in ranked_records(records, "mechanic")[:15]
        ],
        "top_mood_candidates": [
            minimal_payload(record, scores) for record, scores in ranked_records(records, "mood")[:15]
        ],
        "top_theme_candidates": [
            minimal_payload(record, scores) for record, scores in ranked_records(records, "fantasy")[:15]
        ],
        "hero_collection_ids": list(hero_collections.keys()),
        "feed_collection_ids": list(feed_collections.keys()),
        "strategy_counts": [{"strategy_type": key, "count": count} for key, count in strategy_counter.most_common()],
        "hero_collections": [
            {
                "id": collection["id"],
                "title": collection["title"],
                "strategy_type": collection.get("strategy_type"),
                "candidate_count": len(collection.get("game_ids", [])),
            }
            for collection in hero_collections.values()
        ],
        "feed_collections": [
            {
                "id": collection["id"],
                "title": collection["title"],
                "strategy_type": collection.get("strategy_type"),
                "candidate_count": len(collection.get("game_ids", [])),
            }
            for collection in feed_collections.values()
        ],
    }


def ensure_output_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_markdown_report(
    path: Path,
    records: list[GameRecord],
    hero_collections: dict[str, dict[str, Any]],
    feed_collections: dict[str, dict[str, Any]],
    rotation_30_days: list[dict[str, Any]],
) -> None:
    lines = [
        "# Home Collection ID Manifest",
        "",
        f"- Games analyzed: **{len(records)}**",
        f"- Hero collections: **{len(hero_collections)}**",
        f"- Feed collections: **{len(feed_collections)}**",
        "",
        "## Hero Collections",
        "",
    ]

    for hero_id, payload in hero_collections.items():
        lines.append(
            f"- **{hero_id}** → {payload['title']} "
            f"[{payload.get('strategy_type', 'unknown')}] "
            f"({len(payload['game_ids'])} ids)"
        )

    lines.extend(["", "## Feed Collections", ""])
    for feed_id, payload in feed_collections.items():
        lines.append(
            f"- **{feed_id}** → {payload['title']} "
            f"[{payload.get('strategy_type', 'unknown')}] "
            f"({len(payload['game_ids'])} ids, {len(payload['featured_game_ids'])} featured)"
        )

    lines.extend(["", "## Rotation Preview", ""])
    for item in rotation_30_days[:7]:
        lines.append(
            f"- **{item['date']}** heroes={', '.join(item['hero_collection_ids'])} feeds={', '.join(item['feed_collection_ids'])}"
        )

    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("catalog_path", type=Path, help="Path to app.json catalog file")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("tmp/home_curation"),
        help="Directory where analysis artifacts will be written",
    )
    args = parser.parse_args()

    records = load_catalog(args.catalog_path)
    ensure_output_dir(args.output_dir)

    hero_collections = build_hero_collections(records)
    feed_collections = build_feed_collections(records)
    rotation_30_days = build_30_day_rotation(hero_collections, feed_collections)
    report = build_report(records, hero_collections, feed_collections)

    ids_manifest = {
        "catalog_path": str(args.catalog_path),
        "generated_at": date.today().isoformat(),
        "home_shape": {
            "hero_slots": 3,
            "feed_slots": 3,
            "feed_featured_size": 9,
            "feed_pool_size": 50,
            "rotation_days": 30,
        },
        "hero_collections": hero_collections,
        "feed_collections": feed_collections,
        "rotation_30_days": rotation_30_days,
    }

    (args.output_dir / "home_collections_ids.json").write_text(
        json.dumps(ids_manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (args.output_dir / "home_collections_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    write_markdown_report(
        args.output_dir / "home_collections_report.md",
        records,
        hero_collections,
        feed_collections,
        rotation_30_days,
    )

    print(f"Wrote analysis artifacts to: {args.output_dir}")
    print(f"Games analyzed: {len(records)}")
    print(f"Hero collections: {len(hero_collections)}")
    print(f"Feed collections: {len(feed_collections)}")
    print("Feed ids:")
    for feed_id in feed_collections.keys():
        print(f" - {feed_id}")


if __name__ == "__main__":
    main()