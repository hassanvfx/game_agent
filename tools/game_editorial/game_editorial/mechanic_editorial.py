from __future__ import annotations

import json
import math
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

TOOL_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = TOOL_ROOT.parent.parent
MATCHER_TOOL_ROOT = REPO_ROOT / "tools" / "game_matcher_v2"
if str(MATCHER_TOOL_ROOT) not in sys.path:
    sys.path.insert(0, str(MATCHER_TOOL_ROOT))

from game_matcher_v2 import build_artifacts, score_games  # noqa: E402
from game_matcher_v2.builder import load_json  # noqa: E402


DEFAULT_APP_JSON_PATH = REPO_ROOT / "games" / "published" / "public" / "app.json"
DEFAULT_WORKSPACE_ROOT = TOOL_ROOT / "scripts" / "workspace"
TAG_FAMILIES = (
    "mechanic_tags",
    "semantic_tags",
    "mood_tags",
    "setting_tags",
    "character_tags",
    "games_tags",
    "franchise_tags",
)


@dataclass(frozen=True)
class MechanicIdentity:
    normalized_tag: str
    display_tag: str
    support: int
    distinctiveness_score: float
    sample_game_ids: list[str]
    variant_forms: list[str]


@dataclass(frozen=True)
class MechanicIdentityBatchResult:
    source_path: Path
    output_dir: Path
    batch_summary_path: Path
    top_tags_path: Path
    matches_path: Path
    game_refactoring_manifest_path: Path
    total_entries: int
    unique_mechanic_tags: int
    ranked_count: int
    matches_per_tag: int


def utc_timestamp_slug() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).strftime("%Y-%m-%dT%H-%M-%SZ")


def normalize_tag(value: Any) -> str:
    return " ".join(str(value or "").strip().split())


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def slugify(value: str) -> str:
    normalized = normalize_tag(value).casefold()
    chars: list[str] = []
    previous_dash = False
    for char in normalized:
        if char.isalnum():
            chars.append(char)
            previous_dash = False
            continue
        if not previous_dash:
            chars.append("-")
            previous_dash = True
    slug = "".join(chars).strip("-")
    return slug or "mechanic"


def load_source_payload(app_json: str | Path | None = None) -> tuple[Path, dict[str, Any]]:
    source_path = Path(app_json or DEFAULT_APP_JSON_PATH).expanduser().resolve()
    payload = load_json(source_path)
    if not isinstance(payload, dict):
        raise ValueError(f"Expected app.json to contain a JSON object of entries: {source_path}")
    return source_path, payload


def build_source_lookup_by_url(source_payload: dict[str, Any]) -> dict[str, tuple[str, dict[str, Any]]]:
    lookup: dict[str, tuple[str, dict[str, Any]]] = {}
    for entry_id, entry_payload in source_payload.items():
        if not isinstance(entry_payload, dict):
            continue
        for key in ("public_index_html", "index_html"):
            value = entry_payload.get(key)
            if isinstance(value, str) and value.strip():
                lookup[value.strip()] = (entry_id, entry_payload)
    return lookup


def build_game_refactoring_manifest_rows(
    *,
    source_path: Path,
    source_payload: dict[str, Any],
    ranked_identities: list[MechanicIdentity],
    matches_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    public_root = source_path.parent
    source_lookup = build_source_lookup_by_url(source_payload)
    games: list[dict[str, Any]] = []

    for identity, matches_row in zip(ranked_identities, matches_rows):
        mechanic_slug = slugify(identity.display_tag)
        top_matches = matches_row.get("top_matches") or []
        for match_index, top_match in enumerate(top_matches, start=1):
            match_url = str(top_match.get("url") or "").strip()
            lookup_hit = source_lookup.get(match_url)
            if lookup_hit is None:
                continue

            entry_id, entry_payload = lookup_hit
            published_path = entry_payload.get("published_path")
            if not isinstance(published_path, str) or not published_path.strip():
                continue

            original_game_id = str(entry_payload.get("game_id") or top_match.get("game_id") or entry_id)
            synthetic_game_id = f"editorial-{mechanic_slug}-{match_index:02d}__{entry_id}"
            source_dir = (public_root / published_path).resolve()

            games.append(
                {
                    "game_id": synthetic_game_id,
                    "original_game_id": original_game_id,
                    "source_entry_id": entry_id,
                    "display_name": top_match.get("name") or entry_payload.get("title") or original_game_id,
                    "source_path": str(source_dir),
                    "source_url": match_url,
                    "match_rank": match_index,
                    "mechanic_name": identity.display_tag,
                    "matcher_context": {
                        "mechanic_name": identity.display_tag,
                        "mechanic_rank": matches_row.get("rank"),
                        "mechanic_support": identity.support,
                        "mechanic_distinctiveness_score": round(identity.distinctiveness_score, 6),
                        "match_rank_within_mechanic": match_index,
                        "matched_queries": top_match.get("matched_queries") or [],
                        "coverage": top_match.get("coverage"),
                        "distance": top_match.get("distance"),
                        "original_game_id": original_game_id,
                        "source_entry_id": entry_id,
                        "published_path": published_path,
                    },
                }
            )

    return {
        "manifest_version": "2.0.0",
        "run_label": f"top-{len(ranked_identities)}-mechanic-groups-for-game-workflow",
        "games": games,
    }


def iter_normalized_mechanic_tags(entry_payload: dict[str, Any]) -> list[tuple[str, str]]:
    raw_tags = entry_payload.get("mechanic_tags") or []
    seen: set[str] = set()
    normalized_pairs: list[tuple[str, str]] = []
    for raw_tag in raw_tags:
        display_tag = normalize_tag(raw_tag)
        normalized_tag = display_tag.casefold()
        if not display_tag or normalized_tag in seen:
            continue
        seen.add(normalized_tag)
        normalized_pairs.append((normalized_tag, display_tag))
    return normalized_pairs


def collect_mechanic_identity_stats(source_payload: dict[str, Any]) -> tuple[int, dict[str, dict[str, Any]]]:
    stats: dict[str, dict[str, Any]] = {}
    total_entries = len(source_payload)

    for entry_id, entry_payload in source_payload.items():
        game_id = str(entry_payload.get("game_id") or entry_id)
        for normalized_tag, display_tag in iter_normalized_mechanic_tags(entry_payload):
            record = stats.setdefault(
                normalized_tag,
                {
                    "variant_counter": Counter(),
                    "support": 0,
                    "sample_game_ids": [],
                    "seen_game_ids": set(),
                },
            )
            record["variant_counter"][display_tag] += 1
            record["support"] += 1
            if game_id not in record["seen_game_ids"]:
                record["seen_game_ids"].add(game_id)
                record["sample_game_ids"].append(game_id)

    return total_entries, stats


def choose_display_tag(variant_counter: Counter[str]) -> str:
    if not variant_counter:
        return ""
    return sorted(variant_counter.items(), key=lambda item: (-item[1], item[0].casefold()))[0][0]


def calculate_distinctiveness_score(support: int, total_entries: int) -> float:
    if support <= 0 or total_entries <= 0:
        return 0.0
    if support >= total_entries:
        return 0.0
    return support * math.log(total_entries / support)


def rank_mechanic_identities(
    source_payload: dict[str, Any],
    *,
    top_n: int = 100,
    min_support: int = 2,
) -> tuple[int, int, list[MechanicIdentity]]:
    if top_n <= 0:
        raise ValueError("top_n must be greater than 0")
    if min_support <= 0:
        raise ValueError("min_support must be greater than 0")

    total_entries, stats = collect_mechanic_identity_stats(source_payload)
    ranked: list[MechanicIdentity] = []

    for normalized_tag, record in stats.items():
        support = int(record["support"])
        if support < min_support:
            continue

        variant_counter: Counter[str] = record["variant_counter"]
        ranked.append(
            MechanicIdentity(
                normalized_tag=normalized_tag,
                display_tag=choose_display_tag(variant_counter),
                support=support,
                distinctiveness_score=calculate_distinctiveness_score(support, total_entries),
                sample_game_ids=list(record["sample_game_ids"][:10]),
                variant_forms=sorted(variant_counter.keys(), key=str.casefold),
            )
        )

    ranked.sort(
        key=lambda item: (
            -item.distinctiveness_score,
            -item.support,
            item.normalized_tag,
        )
    )
    return total_entries, len(stats), ranked[:top_n]


def empty_selected_tags_payload() -> dict[str, list[dict[str, Any]]]:
    return {family: [] for family in TAG_FAMILIES}


def build_selected_tags_payload(tag: str, *, score: float = 1.0) -> dict[str, list[dict[str, Any]]]:
    payload = empty_selected_tags_payload()
    payload["mechanic_tags"] = [{"tag": tag, "score": score}]
    return payload


def ensure_output_dir(out_dir: str | Path | None = None) -> Path:
    if out_dir:
        output_dir = Path(out_dir).expanduser().resolve()
    else:
        output_dir = DEFAULT_WORKSPACE_ROOT / f"mechanic_identity_batch_{utc_timestamp_slug()}"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def generate_mechanic_identity_batch(
    *,
    app_json: str | Path | None = None,
    top_n: int = 100,
    matches_per_tag: int = 10,
    min_support: int = 2,
    out_dir: str | Path | None = None,
    force_rebuild: bool = False,
) -> MechanicIdentityBatchResult:
    if matches_per_tag <= 0:
        raise ValueError("matches_per_tag must be greater than 0")

    source_path, source_payload = load_source_payload(app_json)
    total_entries, unique_mechanic_tags, ranked_identities = rank_mechanic_identities(
        source_payload,
        top_n=top_n,
        min_support=min_support,
    )

    matcher_artifacts = build_artifacts(app_json=source_path, force=force_rebuild)
    normalized_games_payload = load_json(matcher_artifacts.artifacts_dir / "normalized_games.json")
    output_dir = ensure_output_dir(out_dir)

    top_tags_path = output_dir / "top_100_mechanic_tags.json"
    matches_path = output_dir / "matches_by_mechanic_tag.json"
    batch_summary_path = output_dir / "batch_summary.json"
    grouped_manifest_path = output_dir / "game_refactoring_games_manifest.json"

    top_tags_rows: list[dict[str, Any]] = []
    matches_rows: list[dict[str, Any]] = []

    for rank, identity in enumerate(ranked_identities, start=1):
        selected_tags_payload = build_selected_tags_payload(identity.display_tag)
        top_matches = score_games(
            normalized_games_payload,
            selected_tags_payload,
            limit=matches_per_tag,
        )

        top_tags_rows.append(
            {
                "rank": rank,
                "tag": identity.display_tag,
                "normalized_tag": identity.normalized_tag,
                "support": identity.support,
                "distinctiveness_score": round(identity.distinctiveness_score, 6),
                "sample_game_ids": identity.sample_game_ids,
                "variant_forms": identity.variant_forms,
            }
        )
        matches_rows.append(
            {
                "rank": rank,
                "tag": identity.display_tag,
                "normalized_tag": identity.normalized_tag,
                "support": identity.support,
                "distinctiveness_score": round(identity.distinctiveness_score, 6),
                "selected_tags_payload": selected_tags_payload,
                "top_matches": top_matches,
            }
        )

    batch_summary = {
        "source_path": str(source_path),
        "output_dir": str(output_dir),
        "total_entries": total_entries,
        "unique_mechanic_tags": unique_mechanic_tags,
        "ranked_count": len(ranked_identities),
        "top_n": top_n,
        "matches_per_tag": matches_per_tag,
        "min_support": min_support,
        "distinctiveness_formula": "support * ln(total_entries / support)",
        "matcher_artifacts_dir": str(matcher_artifacts.artifacts_dir),
        "files": {
            "batch_summary": str(batch_summary_path),
            "top_100_mechanic_tags": str(top_tags_path),
            "matches_by_mechanic_tag": str(matches_path),
            "game_refactoring_games_manifest": str(grouped_manifest_path),
        },
    }

    grouped_manifest = build_game_refactoring_manifest_rows(
        source_path=source_path,
        source_payload=source_payload,
        ranked_identities=ranked_identities,
        matches_rows=matches_rows,
    )

    write_json(top_tags_path, top_tags_rows)
    write_json(matches_path, matches_rows)
    write_json(grouped_manifest_path, grouped_manifest)
    write_json(batch_summary_path, batch_summary)

    return MechanicIdentityBatchResult(
        source_path=source_path,
        output_dir=output_dir,
        batch_summary_path=batch_summary_path,
        top_tags_path=top_tags_path,
        matches_path=matches_path,
        game_refactoring_manifest_path=grouped_manifest_path,
        total_entries=total_entries,
        unique_mechanic_tags=unique_mechanic_tags,
        ranked_count=len(ranked_identities),
        matches_per_tag=matches_per_tag,
    )