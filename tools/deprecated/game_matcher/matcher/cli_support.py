import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


ROOT_DIR = Path(__file__).resolve().parent.parent
CONSOLIDATED_DIR = ROOT_DIR / "fixtures" / "consolidated"
DEFAULT_QUERIES_PATH = CONSOLIDATED_DIR / "all_queries.json"
DEFAULT_REVERSE_INDEX_PATH = CONSOLIDATED_DIR / "master_game_reverse_index.json"
TOP800_REVERSE_INDEX_PATH = CONSOLIDATED_DIR / "top800_master_game_reverse_index.json"
CHAT_COMPLETIONS_URL = "https://api.openai.com/v1/chat/completions"
MODEL_NAME = "gpt-4.1-mini"


def load_env_file(env_path: Path) -> None:
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()

        if not key or key in os.environ:
            continue

        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]

        os.environ[key] = value


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def tokenize(text: Any) -> list[str]:
    return [
        token
        for token in re.sub(r"[^a-z0-9\\s]+", " ", str(text or "").lower()).split()
        if len(token) > 1
    ]


def overlap_count(a_tokens: list[str], b_tokens: list[str]) -> int:
    b_set = set(b_tokens)
    return sum(1 for token in a_tokens if token in b_set)


def translate_prompt_to_queries(prompt: str, all_queries: list[str], api_key: str) -> list[str]:
    system_prompt = " ".join(
        [
            "You translate a user's game idea into the best matching search queries.",
            "You are given a fixed vocabulary of valid query strings.",
            "Return ONLY a JSON object.",
            'The JSON object must have a "queries" key with an array of up to 10 strings.',
            "Every returned string must be copied exactly from the provided vocabulary.",
            "Do not include any explanation, markdown, or extra text.",
        ]
    )

    request_payload = {
        "model": MODEL_NAME,
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "instruction": {
                            "task": "Select the top 10 best matching query strings for this game idea.",
                            "game_prompt": prompt,
                            "valid_queries": all_queries,
                        },
                        "required_output_shape": {"queries": ["query string 1", "query string 2"]},
                    }
                ),
            },
        ],
    }

    request = urllib.request.Request(
        CHAT_COMPLETIONS_URL,
        data=json.dumps(request_payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Chat Completions request failed: {error.code} {body}") from error
    except urllib.error.URLError as error:
        raise RuntimeError(f"Failed to reach Chat Completions API: {error.reason}") from error

    content = payload.get("choices", [{}])[0].get("message", {}).get("content")
    if not content:
        raise RuntimeError("No content returned from Chat Completions API.")

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as error:
        raise RuntimeError("Model did not return valid JSON.") from error

    allowed = set(all_queries)
    filtered: list[str] = []
    for query in parsed.get("queries", []):
        if isinstance(query, str) and query in allowed and query not in filtered:
            filtered.append(query)

    return filtered[:10]


def rank_games(prompt: str, translated_queries: list[str], reverse_index: dict[str, Any]) -> list[dict[str, Any]]:
    weighted_queries = [
        {
            "query": query,
            "lower": query.lower(),
            "weight": max(0.15, 1 - index * 0.08),
            "tokens": tokenize(query),
        }
        for index, query in enumerate(translated_queries)
    ]

    prompt_tokens = tokenize(prompt)
    games = reverse_index.get("games", [])
    ranked: list[dict[str, Any]] = []
    missing_penalty = 150
    exact_mismatch_penalty = 8
    best_position_penalty_factor = 1.5
    avg_position_penalty_factor = 0.5

    for game in games:
        match_map: dict[str, dict[str, Any]] = {}

        for match in game.get("query_matches", []):
            query = str(match.get("query", "")).lower()
            weighted = next((item for item in weighted_queries if item["lower"] == query), None)
            if not weighted:
                continue

            existing = match_map.get(weighted["lower"])
            if not existing or match.get("feed_position", 9999) < existing["feed_position"]:
                match_map[weighted["lower"]] = {
                    "query": match.get("query"),
                    "feed_position": match.get("feed_position", 9999),
                    "exact_match": bool(match.get("exact_match")),
                    "weight": weighted["weight"],
                }

        matched_entries = sorted(match_map.values(), key=lambda item: item["feed_position"])
        matched_queries = [item["query"] for item in matched_entries]
        matched_count = len(matched_entries)
        coverage = matched_count / len(weighted_queries) if weighted_queries else 0
        exact_match_count = sum(1 for item in matched_entries if item["exact_match"])

        distance = 0.0
        for weighted in weighted_queries:
            match = match_map.get(weighted["lower"])
            if not match:
                distance += weighted["weight"] * missing_penalty
                continue

            effective_position = min(match["feed_position"], 10)
            distance += weighted["weight"] * (effective_position**2)
            if not match["exact_match"]:
                distance += weighted["weight"] * exact_mismatch_penalty

        best_feed_position = (
            min(item["feed_position"] for item in matched_entries) if matched_entries else 9999
        )
        avg_matched_position = (
            sum(item["feed_position"] for item in matched_entries) / matched_count
            if matched_entries
            else 9999
        )

        distance += best_position_penalty_factor * (min(best_feed_position, 10) ** 2)
        distance += avg_position_penalty_factor * (min(avg_matched_position, 10) ** 2)

        game_name_tokens = tokenize(game.get("name"))
        matched_query_tokens = [token for query in matched_queries for token in tokenize(query)]
        prompt_name_overlap = overlap_count(prompt_tokens, game_name_tokens)
        prompt_query_overlap = overlap_count(prompt_tokens, matched_query_tokens)

        query_lexical_bonus = sum(
            weighted["weight"] * overlap_count(weighted["tokens"], game_name_tokens) * 10
            for weighted in weighted_queries
        )

        stats = game.get("stats") or {}
        popularity_boost = min(game.get("query_count") or 0, 100) * 0.05 + min(
            (stats.get("played_count") or 0) / 5000, 20
        )

        final_distance = (
            distance
            - exact_match_count * 25
            - prompt_name_overlap * 40
            - prompt_query_overlap * 15
            - query_lexical_bonus
            - popularity_boost
        )

        ranked.append(
            {
                **game,
                "matched_queries": matched_queries,
                "matched_count": matched_count,
                "coverage": coverage,
                "best_feed_position": best_feed_position if matched_entries else None,
                "avg_matched_position": round(avg_matched_position, 3) if matched_entries else None,
                "distance": round(final_distance, 3),
                "raw_distance": round(distance, 3),
                "exact_match_count": exact_match_count,
                "prompt_name_overlap": prompt_name_overlap,
                "prompt_query_overlap": prompt_query_overlap,
                "played_count": game.get("played_count", stats.get("played_count", 0)),
            }
        )

    ranked.sort(
        key=lambda game: (
            -game["prompt_name_overlap"],
            -game["prompt_query_overlap"],
            -game["coverage"],
            game["distance"],
            game["best_feed_position"] if game["best_feed_position"] is not None else 9999,
            -game["exact_match_count"],
            -(game.get("query_count") or 0),
            -(game.get("played_count") or 0),
        )
    )

    return ranked


def build_output_games(ranked_games: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    output = []
    for game in ranked_games[:limit]:
        output.append(
            {
                "game_id": game.get("game_id"),
                "name": game.get("name"),
                "url": game.get("url"),
                "cover_url": game.get("cover_url"),
                "matched_queries": game.get("matched_queries", []),
                "coverage": game.get("coverage"),
                "distance": game.get("distance"),
                "best_feed_position": game.get("best_feed_position"),
                "played_count": game.get("played_count", 0),
            }
        )
    return output


def normalize_source_url(source_url: str) -> str:
    parsed = urlparse(source_url.strip())
    normalized_path = parsed.path.rstrip("/") or parsed.path
    return parsed._replace(params="", query="", fragment="", path=normalized_path).geturl()


def find_game_by_url(source_url: str, reverse_index: dict[str, Any]) -> dict[str, Any] | None:
    target_url = normalize_source_url(source_url)
    for game in reverse_index.get("games", []):
        game_url = str(game.get("url") or "").strip()
        if game_url and normalize_source_url(game_url) == target_url:
            return game
    return None


def build_single_game_output(game: dict[str, Any]) -> dict[str, Any]:
    stats = game.get("stats") or {}
    return {
        "game_id": game.get("game_id"),
        "name": game.get("name"),
        "url": game.get("url"),
        "cover_url": game.get("cover_url"),
        "description": game.get("description"),
        "creator": game.get("creator"),
        "topic": game.get("topic"),
        "query_count": game.get("query_count"),
        "played_count": game.get("played_count", stats.get("played_count", 0)),
        "queries": game.get("queries", []),
        "query_categories": game.get("query_categories", []),
    }
