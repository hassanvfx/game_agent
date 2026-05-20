#!/usr/bin/env python3
"""Build weighted taxonomy search artifacts from a published game catalog."""

from __future__ import annotations

import argparse
import json
import math
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

DEFAULT_INPUT_PATH = "/Users/hassan/repos/game_agent/games/published/public/app.json"
DEFAULT_OUTPUT_DIR = "tmp/taxonomy_search"

TEXT_FAMILY_NAME = "lexical_tags"
TEXT_FAMILY_WEIGHT = 1.0
TEXT_SOURCE_FIELDS = ["title", "description"]
MIN_TEXT_TOKEN_LENGTH = 3
MIN_TEXT_DOCUMENT_FREQUENCY = 2
MAX_TEXT_DOCUMENT_FREQUENCY_RATIO = 0.35

FAMILY_CONFIG = {
    "mechanics": {
        "source_fields": ["mechanic_tags"],
        "weight": 5.0,
    },
    "semantics": {
        "source_fields": ["semantic_tags"],
        "weight": 3.0,
    },
    "moods": {
        "source_fields": ["mood_tags"],
        "weight": 1.5,
    },
    "settings": {
        "source_fields": ["setting_tags"],
        "weight": 1.25,
    },
    "characters": {
        "source_fields": ["character_tags"],
        "weight": 1.0,
    },
    "references": {
        "source_fields": ["games_tags", "franchise_tags"],
        "weight": 2.0,
    },
    TEXT_FAMILY_NAME: {
        "source_fields": TEXT_SOURCE_FIELDS,
        "weight": TEXT_FAMILY_WEIGHT,
    },
}

STOPWORDS = {
    "a",
    "about",
    "after",
    "all",
    "an",
    "and",
    "any",
    "arcade",
    "around",
    "as",
    "at",
    "based",
    "be",
    "before",
    "browser",
    "build",
    "button",
    "by",
    "called",
    "can",
    "clear",
    "click",
    "create",
    "dark",
    "design",
    "drag",
    "each",
    "end",
    "experience",
    "for",
    "from",
    "full",
    "game",
    "gameplay",
    "games",
    "give",
    "has",
    "have",
    "in",
    "include",
    "into",
    "is",
    "it",
    "its",
    "just",
    "keep",
    "layout",
    "like",
    "make",
    "mobile",
    "mode",
    "mouse",
    "must",
    "near",
    "of",
    "on",
    "or",
    "overall",
    "overlays",
    "page",
    "panel",
    "player",
    "players",
    "playfield",
    "polished",
    "presentation",
    "responsive",
    "screen",
    "session",
    "should",
    "show",
    "simple",
    "single",
    "small",
    "start",
    "style",
    "styled",
    "system",
    "tap",
    "that",
    "the",
    "their",
    "them",
    "there",
    "this",
    "through",
    "to",
    "touch",
    "ui",
    "up",
    "use",
    "using",
    "visual",
    "web",
    "when",
    "where",
    "while",
    "with",
    "within",
    "your",
}

TOKEN_SPLIT_RE = re.compile(r"[^a-z0-9]+")
MULTISPACE_RE = re.compile(r"\s+")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Precompute weighted taxonomy reverse indexes and vectors from app.json."
    )
    parser.add_argument(
        "--input",
        default=DEFAULT_INPUT_PATH,
        help="Path to source app.json catalog.",
    )
    parser.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help="Directory where generated search artifacts will be written.",
    )
    return parser.parse_args()


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    normalized = normalized.encode("ascii", "ignore").decode("ascii")
    normalized = normalized.lower().strip()
    normalized = MULTISPACE_RE.sub(" ", normalized)
    return normalized


def slugify(value: str) -> str:
    normalized = normalize_text(value)
    slug = TOKEN_SPLIT_RE.sub("-", normalized).strip("-")
    return slug


def tokenize_phrase(value: str) -> list[str]:
    normalized = normalize_text(value)
    return [token for token in TOKEN_SPLIT_RE.split(normalized) if token]


def normalize_token(token: str) -> str:
    token = normalize_text(token)
    token = token.strip("-_ ")
    return token


def is_meaningful_text_token(token: str) -> bool:
    token = normalize_token(token)
    if not token:
        return False
    if len(token) < MIN_TEXT_TOKEN_LENGTH:
        return False
    if token in STOPWORDS:
        return False
    if token.isdigit():
        return False
    return True


def iter_list(values: Any) -> list[str]:
    if not isinstance(values, list):
        return []
    return [item.strip() for item in values if isinstance(item, str) and item.strip()]


def build_family_entries(
    game: dict[str, Any],
    family_name: str,
    config: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    entries: dict[str, dict[str, Any]] = {}

    for source_field in config["source_fields"]:
        for raw_value in iter_list(game.get(source_field)):
            normalized_value = normalize_text(raw_value)
            if not normalized_value:
                continue

            key = slugify(normalized_value)
            if not key:
                continue

            phrase_tokens = tokenize_phrase(normalized_value)
            entry = entries.setdefault(
                key,
                {
                    "token": key,
                    "label": raw_value.strip(),
                    "normalized_label": normalized_value,
                    "family": family_name,
                    "source_fields": set(),
                    "phrase_tokens": [],
                },
            )
            entry["source_fields"].add(source_field)
            if not entry["phrase_tokens"]:
                entry["phrase_tokens"] = phrase_tokens

    return entries


def extract_text_candidates(game: dict[str, Any]) -> set[str]:
    candidates: set[str] = set()

    for field in TEXT_SOURCE_FIELDS:
        raw_value = game.get(field)
        if not isinstance(raw_value, str) or not raw_value.strip():
            continue

        normalized = normalize_text(raw_value)
        tokens = [token for token in tokenize_phrase(normalized) if is_meaningful_text_token(token)]
        candidates.update(tokens)

        if len(tokens) >= 2:
            for left, right in zip(tokens, tokens[1:]):
                phrase = f"{left} {right}"
                candidates.add(phrase)

    return candidates


def build_text_entries(
    game: dict[str, Any],
    allowed_text_terms: set[str],
) -> dict[str, dict[str, Any]]:
    entries: dict[str, dict[str, Any]] = {}

    for term in sorted(extract_text_candidates(game)):
        if term not in allowed_text_terms:
            continue

        key = slugify(term)
        if not key:
            continue

        normalized_value = normalize_text(term)
        phrase_tokens = [token for token in tokenize_phrase(normalized_value) if is_meaningful_text_token(token)]
        if not phrase_tokens:
            continue

        label = term.title() if " " in term else term
        entries[key] = {
            "token": key,
            "label": label,
            "normalized_label": normalized_value,
            "family": TEXT_FAMILY_NAME,
            "source_fields": set(TEXT_SOURCE_FIELDS),
            "phrase_tokens": phrase_tokens,
        }

    return entries


def load_catalog(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SystemExit(f"Expected top-level object in {path}")
    return payload


def collect_allowed_text_terms(catalog: dict[str, Any]) -> set[str]:
    document_frequency: Counter[str] = Counter()
    total_games = 0

    for game in catalog.values():
        if not isinstance(game, dict):
            continue
        total_games += 1
        document_frequency.update(extract_text_candidates(game))

    max_allowed_df = max(1, int(total_games * MAX_TEXT_DOCUMENT_FREQUENCY_RATIO))
    allowed_terms: set[str] = set()

    for term, df in document_frequency.items():
        if df < MIN_TEXT_DOCUMENT_FREQUENCY:
            continue
        if df > max_allowed_df:
            continue
        allowed_terms.add(term)

    return allowed_terms


def main() -> int:
    args = parse_args()
    input_path = Path(args.input)
    output_dir = Path(args.output_dir)

    if not input_path.exists():
        raise SystemExit(f"Input catalog not found: {input_path}")

    catalog = load_catalog(input_path)
    allowed_text_terms = collect_allowed_text_terms(catalog)

    reverse_index_by_family: dict[str, dict[str, list[str]]] = {
        family: defaultdict(list) for family in FAMILY_CONFIG
    }
    token_document_frequency_by_family: dict[str, Counter[str]] = {
        family: Counter() for family in FAMILY_CONFIG
    }
    family_vocabularies: dict[str, dict[str, dict[str, Any]]] = {
        family: {} for family in FAMILY_CONFIG
    }
    game_vectors: dict[str, dict[str, Any]] = {}

    total_games = 0

    for catalog_key, game in catalog.items():
        if not isinstance(game, dict):
            continue

        game_id = str(game.get("game_id") or catalog_key)
        title = game.get("title") or ""
        description = game.get("description") or ""

        families_payload: dict[str, Any] = {}
        weighted_terms: dict[str, float] = {}
        searchable_terms: set[str] = set()

        for family_name, config in FAMILY_CONFIG.items():
            if family_name == TEXT_FAMILY_NAME:
                entries = build_text_entries(game, allowed_text_terms)
            else:
                entries = build_family_entries(game, family_name, config)

            families_payload[family_name] = {
                "weight": config["weight"],
                "terms": sorted(
                    [
                        {
                            "token": entry["token"],
                            "label": entry["label"],
                            "normalized_label": entry["normalized_label"],
                            "source_fields": sorted(entry["source_fields"]),
                            "phrase_tokens": entry["phrase_tokens"],
                        }
                        for entry in entries.values()
                    ],
                    key=lambda item: item["token"],
                ),
            }

            for token, entry in entries.items():
                reverse_index_by_family[family_name][token].append(game_id)
                token_document_frequency_by_family[family_name][token] += 1
                family_vocabularies[family_name].setdefault(
                    token,
                    {
                        "token": token,
                        "label": entry["label"],
                        "normalized_label": entry["normalized_label"],
                        "family": family_name,
                        "source_fields": sorted(entry["source_fields"]),
                        "phrase_tokens": entry["phrase_tokens"],
                    },
                )
                weighted_terms[f"{family_name}:{token}"] = config["weight"]
                searchable_terms.add(token)
                searchable_terms.add(entry["normalized_label"])

                for phrase_token in entry["phrase_tokens"]:
                    searchable_terms.add(phrase_token)

        game_vectors[game_id] = {
            "game_id": game_id,
            "catalog_key": catalog_key,
            "title": title,
            "description": description,
            "published_path": game.get("published_path"),
            "screenshots": game.get("screenshots") if isinstance(game.get("screenshots"), list) else [],
            "families": families_payload,
            "weighted_terms": dict(sorted(weighted_terms.items())),
            "searchable_terms": sorted(searchable_terms),
        }
        total_games += 1

    reverse_index_payload = {
        "meta": {
            "source_catalog": str(input_path),
            "game_count": total_games,
            "family_weights": {family: config["weight"] for family, config in FAMILY_CONFIG.items()},
            "family_order": list(FAMILY_CONFIG.keys()),
            "lexical_term_count": len(allowed_text_terms),
        },
        "families": {
            family: {
                "tokens": {
                    token: sorted(game_ids)
                    for token, game_ids in sorted(tokens.items())
                }
            }
            for family, tokens in reverse_index_by_family.items()
        },
    }

    game_vectors_payload = {
        "meta": reverse_index_payload["meta"],
        "games": dict(sorted(game_vectors.items())),
    }

    stats_payload = {
        "meta": reverse_index_payload["meta"],
        "families": {},
    }

    for family, vocab in family_vocabularies.items():
        family_stats = []
        game_count = max(total_games, 1)

        for token, entry in sorted(vocab.items()):
            df = token_document_frequency_by_family[family][token]
            idf = math.log((1 + game_count) / (1 + df)) + 1.0
            family_stats.append(
                {
                    "token": token,
                    "label": entry["label"],
                    "normalized_label": entry["normalized_label"],
                    "document_frequency": df,
                    "idf": round(idf, 6),
                    "source_fields": entry["source_fields"],
                    "phrase_tokens": entry["phrase_tokens"],
                }
            )

        stats_payload["families"][family] = {
            "weight": FAMILY_CONFIG[family]["weight"],
            "token_count": len(family_stats),
            "tokens": family_stats,
        }

    artifact_payload = {
        "meta": {
            **reverse_index_payload["meta"],
            "version": 2,
        },
        "families": stats_payload["families"],
        "games": game_vectors_payload["games"],
    }

    write_json(output_dir / "taxonomy_reverse_index.json", reverse_index_payload)
    write_json(output_dir / "game_taxonomy_vectors.json", game_vectors_payload)
    write_json(output_dir / "taxonomy_stats.json", stats_payload)
    write_json(output_dir / "taxonomy_search_artifact.json", artifact_payload)

    print(
        json.dumps(
            {
                "input": str(input_path),
                "output_dir": str(output_dir),
                "game_count": total_games,
                "family_count": len(FAMILY_CONFIG),
                "lexical_term_count": len(allowed_text_terms),
                "artifact_files": [
                    "taxonomy_reverse_index.json",
                    "game_taxonomy_vectors.json",
                    "taxonomy_stats.json",
                    "taxonomy_search_artifact.json",
                ],
            },
            indent=2,
            ensure_ascii=False,
        )
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())