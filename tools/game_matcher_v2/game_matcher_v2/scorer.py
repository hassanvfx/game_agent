from typing import Any


FAMILY_WEIGHTS = {
    "mechanic_tags": 5.0,
    "games_tags": 4.0,
    "franchise_tags": 4.0,
    "semantic_tags": 3.0,
    "mood_tags": 2.0,
    "character_tags": 2.0,
    "setting_tags": 1.5,
}

def _score_weight(score: Any) -> float:
    try:
        numeric_score = float(score)
    except (TypeError, ValueError):
        return 0.0
    if numeric_score < 0.0 or numeric_score > 1.0:
        return 0.0
    return numeric_score


def _normalize_selected(selected_tags: dict[str, list[dict[str, Any]]]) -> dict[str, dict[str, float]]:
    normalized: dict[str, dict[str, float]] = {}
    for family, items in selected_tags.items():
        family_map: dict[str, float] = {}
        for item in items or []:
            tag = " ".join(str(item.get("tag") or "").strip().split())
            if not tag:
                continue
            weight = _score_weight(item.get("score"))
            if weight <= 0:
                continue
            family_map[tag.casefold()] = max(family_map.get(tag.casefold(), 0.0), weight)
        normalized[family] = family_map
    return normalized


def score_games(
    normalized_games_payload: dict[str, Any],
    selected_tags: dict[str, list[dict[str, Any]]],
    *,
    limit: int = 20,
) -> list[dict[str, Any]]:
    if limit <= 0:
        raise ValueError("limit must be greater than 0")

    selected = _normalize_selected(selected_tags)
    if not any(selected.values()):
        return []

    games = normalized_games_payload.get("games") or []

    ranked: list[dict[str, Any]] = []
    for game in games:
        total_score = 0.0
        matched_details: list[str] = []
        matched_count = 0
        selected_count = 0

        tags_by_family = game.get("tags") or {}
        for family, family_weight in FAMILY_WEIGHTS.items():
            selected_family = selected.get(family, {})
            if not selected_family:
                continue
            selected_count += len(selected_family)

            game_family_tags = {" ".join(str(tag).strip().split()).casefold() for tag in tags_by_family.get(family, [])}
            for selected_tag, rank_weight in selected_family.items():
                if selected_tag in game_family_tags:
                    total_score += family_weight * rank_weight
                    matched_count += 1
                    matched_details.append(f"{family}:{selected_tag}")

        coverage = (matched_count / selected_count) if selected_count else 0.0
        distance = round(max(0.0, 1000.0 - total_score), 3)

        ranked.append(
            {
                "game_id": game.get("game_id"),
                "name": game.get("name"),
                "url": game.get("url"),
                "cover_url": game.get("cover_url"),
                "matched_queries": matched_details,
                "coverage": round(coverage, 4),
                "distance": distance,
                "played_count": int(game.get("played_count") or 0),
                "_score": round(total_score, 6),
            }
        )

    ranked.sort(
        key=lambda item: (
            -item["_score"],
            -item["coverage"],
            str(item.get("name") or "").casefold(),
        )
    )

    output: list[dict[str, Any]] = []
    for idx, item in enumerate(ranked[:limit], start=1):
        output.append(
            {
                "game_id": item["game_id"],
                "name": item["name"],
                "url": item["url"],
                "cover_url": item["cover_url"],
                "matched_queries": item["matched_queries"],
                "coverage": item["coverage"],
                "distance": item["distance"],
                "best_feed_position": idx,
                "played_count": item["played_count"],
            }
        )
    return output