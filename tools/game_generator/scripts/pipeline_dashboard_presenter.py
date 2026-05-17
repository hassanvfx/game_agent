#!/usr/bin/env python3
"""Contract-safe presentation helpers for pipeline dashboards."""

from __future__ import annotations

import json
import shlex
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
PIPELINE_RUNS_DIR = ROOT / "pipeline_runs"
PUBLISHED_PUBLIC_ROOT = ROOT.parent.parent / "games" / "published" / "public"
ROUTE_PREFIX = "/__dashboard__"
RECENT_RUN_CARD_LIMIT = 8


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def safe_read_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    try:
        return read_json(path)
    except Exception:
        return None


def parse_iso_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    normalized = value.replace("Z", "+00:00") if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def format_duration_human(total_seconds: int | None) -> str | None:
    if total_seconds is None:
        return None
    total_seconds = max(0, int(total_seconds))
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    parts: list[str] = []
    if hours:
        parts.append(f"{hours}h")
    if minutes or hours:
        parts.append(f"{minutes}m")
    parts.append(f"{seconds}s")
    return " ".join(parts)


def build_timing_summary(started_at: Any, completed_at: Any = None, fallback_end_at: Any = None) -> dict[str, Any]:
    started_raw = started_at if isinstance(started_at, str) and started_at else None
    completed_raw = completed_at if isinstance(completed_at, str) and completed_at else None
    fallback_raw = fallback_end_at if isinstance(fallback_end_at, str) and fallback_end_at else None

    started_dt = parse_iso_timestamp(started_raw)
    completed_dt = parse_iso_timestamp(completed_raw)
    ended_dt = completed_dt or parse_iso_timestamp(fallback_raw)

    duration_seconds = None
    if started_dt is not None and ended_dt is not None:
        duration_seconds = max(0, int((ended_dt - started_dt).total_seconds()))

    return {
        "started_at": started_raw,
        "completed_at": completed_raw,
        "ended_at": completed_raw or fallback_raw,
        "duration_seconds": duration_seconds,
        "duration_human": format_duration_human(duration_seconds),
    }


def build_stage_flow_item(
    stage_id: str,
    label: str,
    status: str,
    *,
    step_details: dict[str, Any],
    cost_story: str,
    run_updated_at: Any,
) -> dict[str, Any]:
    stage_state = step_details.get("details") if isinstance(step_details.get("details"), dict) else step_details
    stage_started_at = stage_state.get("started_at")
    stage_completed_at = stage_state.get("completed_at")
    fallback_end_at = (stage_state.get("updated_at") or run_updated_at) if stage_started_at or stage_completed_at else None
    return {
        "id": stage_id,
        "label": label,
        "status": status,
        "cost_story": cost_story,
        "timing": build_timing_summary(
            stage_started_at,
            stage_completed_at,
            fallback_end_at,
        ),
    }


def quote_prompt(value: str) -> str:
    return shlex.quote(value)


def build_prompt_helper(base_payload: dict[str, Any]) -> dict[str, Any]:
    prompt = str(base_payload.get("prompt") or "")
    remix_prompt = str(base_payload.get("remix_prompt") or prompt)
    poll_seconds = base_payload.get("poll_seconds") or 5
    publish_enabled = bool(base_payload.get("publish_enabled"))
    upload_enabled = bool(base_payload.get("upload_enabled"))

    command_parts = [
        "python3",
        "scripts/demo_pipeline_launch.py",
        quote_prompt(prompt),
        "--poll-seconds",
        str(poll_seconds),
    ]
    if remix_prompt and remix_prompt != prompt:
        command_parts.extend(["--remix-prompt", quote_prompt(remix_prompt)])
    if publish_enabled:
        command_parts.append("--publish")
    if upload_enabled:
        command_parts.append("--upload")

    return {
        "prompt": prompt,
        "remix_prompt": remix_prompt,
        "poll_seconds": poll_seconds,
        "publish_enabled": publish_enabled,
        "upload_enabled": upload_enabled,
        "command": " ".join(command_parts),
    }


def build_step_map(base_payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    steps = base_payload.get("steps", [])
    if not isinstance(steps, list):
        return {}
    result: dict[str, dict[str, Any]] = {}
    for step in steps:
        if not isinstance(step, dict):
            continue
        step_id = step.get("id")
        if isinstance(step_id, str):
            result[step_id] = step
    return result


def load_match_payload(run_dir: Path) -> dict[str, Any]:
    payload = safe_read_json(run_dir / "matcher" / "parsed_matches.json")
    return payload if isinstance(payload, dict) else {}


def load_match_name_map(run_dir: Path) -> dict[str, str]:
    payload = load_match_payload(run_dir)
    items: list[dict[str, Any]] = []
    for key in ("selected_matches", "matches"):
        value = payload.get(key)
        if isinstance(value, list):
            items.extend([item for item in value if isinstance(item, dict)])

    result: dict[str, str] = {}
    for item in items:
        game_id = item.get("game_id")
        name = item.get("name")
        if isinstance(game_id, str) and isinstance(name, str) and game_id not in result:
            result[game_id] = name
    return result


def path_relative_to(base_dir: Path, target: Path) -> str | None:
    try:
        return target.resolve().relative_to(base_dir.resolve()).as_posix()
    except Exception:
        return None


def derive_cdn_screenshot(url: str | None) -> str | None:
    if not isinstance(url, str) or not url:
        return None
    if not url.endswith("/index.html"):
        return None
    return url[: -len("index.html")] + "screenshots/01.jpg"


def resolve_match_dirs(run_dir: Path) -> dict[str, Path]:
    payload = load_match_payload(run_dir)
    matches = payload.get("matches")
    result: dict[str, Path] = {}
    if not isinstance(matches, list):
        return result
    for match in matches:
        if not isinstance(match, dict):
            continue
        game_id = match.get("game_id")
        url = match.get("url")
        if not isinstance(game_id, str) or not isinstance(url, str):
            continue
        base_dir = (PUBLISHED_PUBLIC_ROOT / Path(url).parent).resolve()
        if base_dir.exists() and base_dir.is_dir():
            result[game_id] = base_dir
    return result


def resolve_output_dirs(base_payload: dict[str, Any]) -> dict[str, Path]:
    links = base_payload.get("links", {})
    if not isinstance(links, dict):
        return {}
    final_output_dirs = links.get("final_output_dirs")
    if not isinstance(final_output_dirs, list):
        return {}

    result: dict[str, Path] = {}
    for item in final_output_dirs:
        if not isinstance(item, str):
            continue
        path = Path(item).resolve()
        if path.exists() and path.is_dir():
            result[path.name] = path
    return result


def resolve_publish_dirs(base_payload: dict[str, Any]) -> dict[str, dict[str, Path]]:
    entries = base_payload.get("projected_cdn_urls")
    result = {"public": {}, "play": {}}
    if not isinstance(entries, list):
        return result

    for entry in entries:
        if not isinstance(entry, dict):
            continue
        game_id = entry.get("game_id")
        if not isinstance(game_id, str):
            continue

        public_local_dir = entry.get("public_local_dir")
        play_local_dir = entry.get("play_local_dir")
        if isinstance(public_local_dir, str):
            public_path = Path(public_local_dir).resolve()
            if public_path.exists() and public_path.is_dir():
                result["public"][game_id] = public_path
        if isinstance(play_local_dir, str):
            play_path = Path(play_local_dir).resolve()
            if play_path.exists() and play_path.is_dir():
                result["play"][game_id] = play_path
    return result


def build_match_cards(run_dir: Path) -> list[dict[str, Any]]:
    payload = load_match_payload(run_dir)
    matches = payload.get("matches")
    if not isinstance(matches, list):
        return []

    match_dirs = resolve_match_dirs(run_dir)
    cards: list[dict[str, Any]] = []
    for match in matches[:2]:
        if not isinstance(match, dict):
            continue
        game_id = match.get("game_id")
        title = match.get("name")
        if not isinstance(game_id, str) or not isinstance(title, str):
            continue

        base_dir = match_dirs.get(game_id)
        poster_path = None
        cover_url = match.get("cover_url")
        url = match.get("url")
        if base_dir and isinstance(cover_url, str) and isinstance(url, str):
            cover_target = (PUBLISHED_PUBLIC_ROOT / cover_url).resolve()
            poster_path = path_relative_to(base_dir, cover_target)

        cards.append(
            {
                "game_id": game_id,
                "title": title,
                "rank": match.get("best_feed_position") or match.get("match_rank"),
                "coverage": match.get("coverage"),
                "matched_queries": match.get("matched_queries") if isinstance(match.get("matched_queries"), list) else [],
                "preview_url": f"{ROUTE_PREFIX}/match/{urllib.parse.quote(game_id)}/index.html",
                "poster_url": (
                    f"{ROUTE_PREFIX}/match/{urllib.parse.quote(game_id)}/{poster_path}"
                    if poster_path
                    else None
                ),
            }
        )
    return cards


def build_refactor_cards(base_payload: dict[str, Any], name_map: dict[str, str]) -> list[dict[str, Any]]:
    finalized_output_dirs = resolve_output_dirs(base_payload)
    upstream_payload = load_refactoring_dashboard_payload(base_payload)
    upstream_games = upstream_payload.get("games")
    cards: list[dict[str, Any]] = []

    if isinstance(upstream_games, list):
        for item in upstream_games:
            if not isinstance(item, dict):
                continue
            game_id = item.get("game_id")
            if not isinstance(game_id, str) or not game_id:
                continue

            finalized_path = finalized_output_dirs.get(game_id)
            preview_url = None
            if finalized_path is not None and (finalized_path / "index.html").exists():
                preview_url = f"{ROUTE_PREFIX}/output/{urllib.parse.quote(game_id)}/index.html"

            display_name = item.get("display_name") if isinstance(item.get("display_name"), str) else None
            upstream_output_path = item.get("output_path") if isinstance(item.get("output_path"), str) else None
            input_mirror_path = item.get("input_mirror_path") if isinstance(item.get("input_mirror_path"), str) else None
            last_error = item.get("last_error") if isinstance(item.get("last_error"), str) and item.get("last_error") else None

            cards.append(
                {
                    "game_id": game_id,
                    "title": display_name or name_map.get(game_id, game_id),
                    "status": str(item.get("status") or item.get("creative_status") or "unknown"),
                    "phase": item.get("current_phase") or item.get("creative_phase"),
                    "local_path": str(finalized_path) if finalized_path is not None else upstream_output_path,
                    "finalized_path": str(finalized_path) if finalized_path is not None else None,
                    "upstream_output_path": upstream_output_path,
                    "input_mirror_path": input_mirror_path,
                    "last_error": last_error,
                    "preview_url": preview_url,
                }
            )
        return cards

    for game_id, path in finalized_output_dirs.items():
        cards.append(
            {
                "game_id": game_id,
                "title": name_map.get(game_id, game_id),
                "status": "completed",
                "phase": "finalized_output_available",
                "local_path": str(path),
                "finalized_path": str(path),
                "upstream_output_path": None,
                "input_mirror_path": None,
                "last_error": None,
                "preview_url": f"{ROUTE_PREFIX}/output/{urllib.parse.quote(game_id)}/index.html",
            }
        )
    return cards


def build_publish_cards(base_payload: dict[str, Any], name_map: dict[str, str]) -> list[dict[str, Any]]:
    entries = base_payload.get("projected_cdn_urls")
    publish_dirs = resolve_publish_dirs(base_payload)
    cards: list[dict[str, Any]] = []
    if not isinstance(entries, list):
        entries = []

    for entry in entries:
        if not isinstance(entry, dict):
            continue
        game_id = entry.get("game_id")
        if not isinstance(game_id, str):
            continue

        poster_url = None
        if game_id in publish_dirs["public"]:
            screenshot_path = publish_dirs["public"][game_id] / "screenshots" / "01.jpg"
            if screenshot_path.exists():
                poster_url = f"{ROUTE_PREFIX}/publish/public/{urllib.parse.quote(game_id)}/screenshots/01.jpg"

        cards.append(
            {
                "game_id": game_id,
                "title": name_map.get(game_id, game_id),
                "status": "completed",
                "poster_url": poster_url or derive_cdn_screenshot(entry.get("public_cdn_url") or entry.get("play_cdn_url")),
                "public_cdn_url": entry.get("public_cdn_url"),
                "play_cdn_url": entry.get("play_cdn_url"),
                "local_public_preview_url": (
                    f"{ROUTE_PREFIX}/publish/public/{urllib.parse.quote(game_id)}/index.html"
                    if game_id in publish_dirs["public"]
                    else None
                ),
                "local_play_preview_url": (
                    f"{ROUTE_PREFIX}/publish/play/{urllib.parse.quote(game_id)}/index.html"
                    if game_id in publish_dirs["play"]
                    else None
                ),
            }
        )
    if cards:
        return cards

    step_map = build_step_map(base_payload)
    publish_step = step_map.get("publish", {})
    if not isinstance(publish_step, dict):
        publish_step = {}
    publish_details = publish_step.get("details") if isinstance(publish_step.get("details"), dict) else publish_step
    publish_status = str(publish_step.get("status") or publish_details.get("status") or ("pending" if base_payload.get("publish_enabled") else "disabled"))
    publish_reason = publish_details.get("reason") if isinstance(publish_details.get("reason"), str) else None
    return [
        {
            "kind": "status",
            "title": "Publish",
            "status": publish_status,
            "reason": publish_reason,
        }
    ]


def build_finalize_cards(base_payload: dict[str, Any], name_map: dict[str, str]) -> list[dict[str, Any]]:
    step_map = build_step_map(base_payload)
    finalize_step = step_map.get("finalize", {})
    if not isinstance(finalize_step, dict):
        finalize_step = {}
    finalize_details = finalize_step.get("details") if isinstance(finalize_step.get("details"), dict) else finalize_step

    source_by_game_id: dict[str, str] = {}
    source_dirs = finalize_details.get("source_dirs")
    if isinstance(source_dirs, list):
        for item in source_dirs:
            if not isinstance(item, str):
                continue
            path = Path(item).resolve()
            if path.exists():
                source_by_game_id[path.name] = str(path)

    destination = finalize_details.get("destination") if isinstance(finalize_details.get("destination"), str) else None
    finalized_output_dirs = resolve_output_dirs(base_payload)
    cards: list[dict[str, Any]] = []
    for game_id, path in finalized_output_dirs.items():
        cards.append(
            {
                "game_id": game_id,
                "title": name_map.get(game_id, game_id),
                "status": str(finalize_step.get("status") or finalize_details.get("status") or "completed"),
                "local_path": str(path),
                "source_path": source_by_game_id.get(game_id),
                "destination": destination,
                "preview_url": f"{ROUTE_PREFIX}/output/{urllib.parse.quote(game_id)}/index.html",
            }
        )
    if cards:
        return cards

    if finalize_step or destination or base_payload.get("final_output_dir"):
        return [
            {
                "kind": "status",
                "title": "Finalize",
                "status": str(finalize_step.get("status") or finalize_details.get("status") or "pending"),
                "destination": destination or base_payload.get("final_output_dir"),
            }
        ]
    return []


def resolve_refactoring_run_dir(base_payload: dict[str, Any]) -> Path | None:
    artifacts = base_payload.get("artifacts", {})
    if isinstance(artifacts, dict):
        refactoring = artifacts.get("refactoring", {})
        if isinstance(refactoring, dict):
            run_dir = refactoring.get("run_dir")
            if isinstance(run_dir, str) and run_dir:
                path = Path(run_dir).resolve()
                if path.exists():
                    return path
    steps = build_step_map(base_payload)
    refactoring = steps.get("refactoring", {}).get("details", {})
    if isinstance(refactoring, dict):
        run_dir = refactoring.get("run_dir")
        if isinstance(run_dir, str) and run_dir:
            path = Path(run_dir).resolve()
            if path.exists():
                return path
    return None


def load_refactoring_dashboard_payload(base_payload: dict[str, Any]) -> dict[str, Any]:
    refactoring_run_dir = resolve_refactoring_run_dir(base_payload)
    if refactoring_run_dir is None:
        return {}
    payload = safe_read_json(refactoring_run_dir / "dashboard" / "dashboard_data.json")
    return payload if isinstance(payload, dict) else {}


def build_cost_story(base_payload: dict[str, Any], name_map: dict[str, str]) -> dict[str, Any]:
    refactoring_run_dir = resolve_refactoring_run_dir(base_payload)
    summary = {
        "tracked": False,
        "headline": "No spend artifacts were found for this run yet.",
        "stages": [
            {"id": "match", "label": "Match", "tracked": False, "story": "No local spend artifact found."},
            {"id": "refactor", "label": "Refactor", "tracked": False, "story": "No local spend artifact found."},
            {"id": "publish", "label": "Publish", "tracked": False, "story": "No local spend artifact found."},
        ],
        "games": [],
        "operators": [],
    }
    if refactoring_run_dir is None:
        return summary

    cost_report = safe_read_json(refactoring_run_dir / "cost_report.json")
    if not isinstance(cost_report, dict):
        return summary

    run_summary = cost_report.get("summary", {})
    if not isinstance(run_summary, dict):
        return summary

    stage_items = summary["stages"]
    stage_items[1] = {
        "id": "refactor",
        "label": "Refactor",
        "tracked": True,
        "story": "Refactor spend is tracked from upstream operator pipeline cost reports.",
        "total_cost": run_summary.get("totalCost"),
        "projected_cost_usd": run_summary.get("projectedCostUsd"),
        "input_tokens": run_summary.get("inputTokens"),
        "output_tokens": run_summary.get("outputTokens"),
        "total_tokens": run_summary.get("totalTokens"),
        "total_tokens_including_cache": run_summary.get("totalTokensIncludingCache"),
    }

    operator_totals: dict[str, dict[str, Any]] = {}
    game_cards: list[dict[str, Any]] = []
    games = cost_report.get("games")
    if isinstance(games, list):
        for game in games:
            if not isinstance(game, dict):
                continue
            game_id = game.get("game_id")
            game_summary = game.get("summary", {})
            if not isinstance(game_id, str) or not isinstance(game_summary, dict):
                continue

            game_cards.append(
                {
                    "game_id": game_id,
                    "title": name_map.get(game_id, game_id),
                    "total_cost": game_summary.get("totalCost"),
                    "projected_cost_usd": game_summary.get("projectedCostUsd"),
                    "total_tokens": game_summary.get("totalTokens"),
                    "total_tokens_including_cache": game_summary.get("totalTokensIncludingCache"),
                }
            )

            game_cost_report_path = game.get("cost_report_path")
            if not isinstance(game_cost_report_path, str):
                continue
            game_cost_report = safe_read_json(Path(game_cost_report_path))
            if not isinstance(game_cost_report, dict):
                continue

            steps = game_cost_report.get("steps")
            if not isinstance(steps, list):
                continue
            for step in steps:
                if not isinstance(step, dict):
                    continue
                stage_slug = step.get("stage_slug") or step.get("operator_id") or "unknown_stage"
                usage_summary = step.get("usage_summary", {})
                if not isinstance(stage_slug, str) or not isinstance(usage_summary, dict):
                    continue
                usage = usage_summary.get("usage", {})
                projected = usage_summary.get("projectedCost", {})
                if not isinstance(usage, dict) or not isinstance(projected, dict):
                    continue

                bucket = operator_totals.setdefault(
                    stage_slug,
                    {
                        "stage_slug": stage_slug,
                        "operator_id": step.get("operator_id"),
                        "invocation_count": 0,
                        "duration_ms": 0,
                        "total_cost": 0.0,
                        "projected_cost_usd": 0.0,
                        "total_tokens": 0,
                    },
                )
                bucket["invocation_count"] += 1
                bucket["duration_ms"] += int(usage_summary.get("durationMs") or 0)
                bucket["total_cost"] += float(usage.get("totalCost") or 0.0)
                bucket["projected_cost_usd"] += float(projected.get("total") or 0.0)
                token_totals = usage_summary.get("tokenTotals", {})
                if isinstance(token_totals, dict):
                    bucket["total_tokens"] += int(token_totals.get("totalTokens") or 0)

    summary.update(
        {
            "tracked": True,
            "headline": "Spend data is currently tracked for the refactor stage. Match and publish do not expose spend artifacts in this run.",
            "refactor_run_id": cost_report.get("run_id"),
            "totals": {
                "total_cost": run_summary.get("totalCost"),
                "projected_cost_usd": run_summary.get("projectedCostUsd"),
                "input_tokens": run_summary.get("inputTokens"),
                "output_tokens": run_summary.get("outputTokens"),
                "cache_read_tokens": run_summary.get("cacheReadTokens"),
                "total_tokens": run_summary.get("totalTokens"),
                "total_tokens_including_cache": run_summary.get("totalTokensIncludingCache"),
            },
            "games": game_cards,
            "operators": sorted(operator_totals.values(), key=lambda item: item["projected_cost_usd"], reverse=True),
            "report_path": str(refactoring_run_dir / "cost_report.json"),
        }
    )
    return summary


def build_recent_runs(current_run_id: str, *, limit: int = RECENT_RUN_CARD_LIMIT) -> list[dict[str, Any]]:
    run_cards: list[dict[str, Any]] = []
    if not PIPELINE_RUNS_DIR.exists():
        return run_cards

    run_dirs = sorted(
        [path for path in PIPELINE_RUNS_DIR.iterdir() if path.is_dir() and path.name.startswith("run_pipeline_")],
        key=lambda path: path.name,
        reverse=True,
    )
    for run_dir in run_dirs:
        if run_dir.name == current_run_id:
            continue
        dashboard_payload = safe_read_json(run_dir / "dashboard" / "dashboard_data.json")
        if not isinstance(dashboard_payload, dict):
            continue
        if dashboard_payload.get("status") != "completed":
            continue
        entries = dashboard_payload.get("projected_cdn_urls")
        if not isinstance(entries, list) or not entries:
            continue

        prompt = str(dashboard_payload.get("prompt") or "")
        completed_at = dashboard_payload.get("updated_at") or dashboard_payload.get("completed_at")
        name_map = load_match_name_map(run_dir)
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            game_id = entry.get("game_id")
            if not isinstance(game_id, str):
                continue
            play_url = entry.get("play_cdn_url")
            public_url = entry.get("public_cdn_url")
            poster_url = derive_cdn_screenshot(public_url if isinstance(public_url, str) else play_url)
            run_cards.append(
                {
                    "run_id": run_dir.name,
                    "prompt": prompt,
                    "title": name_map.get(game_id, game_id),
                    "game_id": game_id,
                    "poster_url": poster_url,
                    "play_url": play_url,
                    "public_url": public_url,
                    "completed_at": completed_at,
                }
            )
            if len(run_cards) >= limit:
                return run_cards
    return run_cards


def build_current_run_view(base_payload: dict[str, Any], run_dir: Path) -> dict[str, Any]:
    name_map = load_match_name_map(run_dir)
    step_map = build_step_map(base_payload)
    match_step = step_map.get("matcher", {})
    if not isinstance(match_step, dict):
        match_step = {}
    refactor_step = step_map.get("refactoring", {})
    if not isinstance(refactor_step, dict):
        refactor_step = {}
    finalize_step = step_map.get("finalize", {})
    if not isinstance(finalize_step, dict):
        finalize_step = {}
    publish_status = "disabled"
    publish_step = step_map.get("publish")
    if not isinstance(publish_step, dict):
        publish_step = {}
    if publish_step:
        publish_status = str(publish_step.get("status") or "unknown")
    elif base_payload.get("publish_enabled"):
        publish_status = "pending"

    refactor_state = refactor_step.get("details") if isinstance(refactor_step.get("details"), dict) else refactor_step
    refactor_failed = False
    if isinstance(refactor_state, dict):
        refactor_failed = bool(refactor_state.get("failed")) or (
            isinstance(refactor_state.get("games_transform_failed"), int)
            and int(refactor_state.get("games_transform_failed") or 0) > 0
        ) or str(refactor_state.get("last_known_status") or "").endswith("failed")
    raw_refactor_status = str(refactor_step.get("status") or refactor_state.get("status") or "pending")
    refactor_status = "failed" if refactor_failed else raw_refactor_status
    match_status = str(match_step.get("status") or "pending")
    finalize_status = str(finalize_step.get("status") or ("completed" if base_payload.get("final_output_dir") else "pending"))
    cost_story = build_cost_story(base_payload, name_map)
    refactor_stage = next((item for item in cost_story.get("stages", []) if item.get("id") == "refactor"), {})
    run_timing = build_timing_summary(
        base_payload.get("started_at"),
        base_payload.get("completed_at"),
        base_payload.get("updated_at"),
    )

    return {
        "run_id": base_payload.get("run_id"),
        "prompt": base_payload.get("prompt"),
        "status": base_payload.get("status"),
        "timing": run_timing,
        "stage_flow": [
            build_stage_flow_item(
                "match",
                "Match",
                match_status,
                step_details=match_step,
                cost_story="Not tracked",
                run_updated_at=base_payload.get("updated_at"),
            ),
            build_stage_flow_item(
                "refactor",
                "Refactor",
                refactor_status,
                step_details=refactor_step,
                cost_story=(
                    f"${float(refactor_stage.get('projected_cost_usd')):.2f} projected"
                    if refactor_stage.get("tracked") and refactor_stage.get("projected_cost_usd") is not None
                    else "No spend artifact"
                ),
                run_updated_at=base_payload.get("updated_at"),
            ),
            build_stage_flow_item(
                "publish",
                "Publish",
                publish_status,
                step_details=publish_step,
                cost_story="Not tracked",
                run_updated_at=base_payload.get("updated_at"),
            ),
            build_stage_flow_item(
                "finalize",
                "Finalize",
                finalize_status,
                step_details=finalize_step,
                cost_story="Local output copy",
                run_updated_at=base_payload.get("updated_at"),
            ),
        ],
        "match_cards": build_match_cards(run_dir),
        "refactor_cards": build_refactor_cards(base_payload, name_map),
        "publish_cards": build_publish_cards(base_payload, name_map),
        "finalize_cards": build_finalize_cards(base_payload, name_map),
        "dig_deeper": {
            "artifacts_anchor": "#dig-deeper",
            "refactoring_dashboard_path": (
                base_payload.get("artifacts", {}).get("refactoring", {}).get("dashboard_path")
                if isinstance(base_payload.get("artifacts"), dict)
                else None
            ),
        },
    }


def build_dashboard_contract_extensions(run_dir: Path, base_payload: dict[str, Any]) -> dict[str, Any]:
    run_id = str(base_payload.get("run_id") or run_dir.name)
    return {
        "prompt_helper": build_prompt_helper(base_payload),
        "current_run_view": build_current_run_view(base_payload, run_dir),
        "recent_runs": build_recent_runs(run_id),
        "cost_story": build_cost_story(base_payload, load_match_name_map(run_dir)),
    }


def resolve_dashboard_request_path(run_dir: Path, request_path: str) -> Path | None:
    decoded = urllib.parse.unquote(request_path)
    if not decoded.startswith(ROUTE_PREFIX + "/"):
        return None

    suffix = decoded[len(ROUTE_PREFIX) + 1 :]
    parts = [part for part in suffix.split("/") if part]
    if len(parts) < 2:
        return None

    match_dirs = resolve_match_dirs(run_dir)
    output_dirs = resolve_output_dirs(safe_read_json(run_dir / "dashboard" / "dashboard_data.json") or {})
    publish_dirs = resolve_publish_dirs(safe_read_json(run_dir / "dashboard" / "dashboard_data.json") or {})

    base_dir: Path | None = None
    subparts: list[str] = []

    if parts[0] == "match" and len(parts) >= 2:
        base_dir = match_dirs.get(parts[1])
        subparts = parts[2:] or ["index.html"]
    elif parts[0] == "output" and len(parts) >= 2:
        base_dir = output_dirs.get(parts[1])
        subparts = parts[2:] or ["index.html"]
    elif parts[0] == "publish" and len(parts) >= 3:
        kind = parts[1]
        game_id = parts[2]
        if kind in publish_dirs:
            base_dir = publish_dirs[kind].get(game_id)
            subparts = parts[3:] or ["index.html"]

    if base_dir is None:
        return None

    candidate = (base_dir / Path(*subparts)).resolve()
    try:
        candidate.relative_to(base_dir.resolve())
    except Exception:
        return None
    if not candidate.exists() or not candidate.is_file():
        return None
    return candidate


def generate_dashboard_html() -> str:
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Game Generator Dashboard</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    :root {
      color-scheme: dark;
      --bg: #08111f;
      --panel: #0f1b2d;
      --panel-alt: #15243a;
      --panel-soft: rgba(255,255,255,0.04);
      --border: rgba(148, 163, 184, 0.24);
      --text: #f8fafc;
      --muted: #a5b4cc;
      --accent: #7dd3fc;
      --accent-2: #c084fc;
      --success: #4ade80;
      --warning: #fbbf24;
      --danger: #fb7185;
      --shadow: 0 24px 60px rgba(0, 0, 0, 0.28);
      --radius: 18px;
    }

    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background:
        radial-gradient(circle at top left, rgba(125, 211, 252, 0.16), transparent 28%),
        radial-gradient(circle at top right, rgba(192, 132, 252, 0.16), transparent 24%),
        var(--bg);
      color: var(--text);
      line-height: 1.45;
      padding: 28px;
    }

    a { color: var(--accent); text-decoration: none; }
    button {
      border: 0;
      border-radius: 999px;
      padding: 10px 16px;
      font: inherit;
      cursor: pointer;
      color: var(--text);
      background: linear-gradient(135deg, #2563eb, #7c3aed);
      box-shadow: 0 10px 24px rgba(59, 130, 246, 0.2);
    }
    button.ghost {
      background: rgba(255,255,255,0.06);
      box-shadow: none;
      border: 1px solid var(--border);
    }

    input[type="text"] {
      width: 100%;
      border-radius: 14px;
      border: 1px solid var(--border);
      background: rgba(8, 17, 31, 0.55);
      color: var(--text);
      padding: 14px 16px;
      font: inherit;
    }

    .page {
      max-width: 1320px;
      margin: 0 auto;
      display: grid;
      gap: 20px;
    }

    .hero,
    .section,
    .card,
    details {
      border: 1px solid var(--border);
      border-radius: var(--radius);
      background: linear-gradient(180deg, rgba(15, 27, 45, 0.92), rgba(11, 18, 31, 0.98));
      box-shadow: var(--shadow);
    }

    .hero,
    .section {
      padding: 22px;
    }

    .timer-hero {
      padding: 26px 22px;
      display: grid;
      gap: 10px;
      align-items: center;
      justify-items: start;
      background:
        linear-gradient(180deg, rgba(25, 42, 68, 0.96), rgba(11, 18, 31, 0.98));
    }

    .timer-display {
      font-size: clamp(2.6rem, 10vw, 5.4rem);
      line-height: 1;
      font-weight: 800;
      letter-spacing: 0.04em;
      font-variant-numeric: tabular-nums;
      color: var(--text);
      text-shadow: 0 10px 30px rgba(125, 211, 252, 0.12);
    }

    .timer-caption {
      color: var(--muted);
      font-size: 0.95rem;
    }

    .eyebrow {
      text-transform: uppercase;
      letter-spacing: 0.12em;
      color: var(--accent);
      font-size: 0.78rem;
      margin-bottom: 10px;
      font-weight: 700;
    }

    h1, h2, h3, p { margin: 0; }
    h1 { font-size: clamp(1.8rem, 3vw, 2.7rem); }
    h2 { font-size: 1.2rem; margin-bottom: 14px; }
    h3 { font-size: 1rem; }

    .hero-subtitle,
    .muted {
      color: var(--muted);
    }

    .prompt-helper {
      display: grid;
      gap: 14px;
      margin-top: 18px;
    }

    .prompt-actions {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      align-items: center;
    }

    .toggle {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      color: var(--muted);
      font-size: 0.92rem;
    }

    .command-preview {
      border-radius: 14px;
      padding: 14px 16px;
      background: rgba(8, 17, 31, 0.75);
      border: 1px solid var(--border);
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
      white-space: pre-wrap;
      word-break: break-word;
    }

    .summary-grid,
    .cost-grid,
    .stage-flow,
    .card-grid,
    .recent-grid {
      display: grid;
      gap: 14px;
    }

    .summary-grid {
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      margin-bottom: 18px;
    }

    .summary-item,
    .cost-chip,
    .stage-tile,
    .card,
    .recent-card {
      background: var(--panel-soft);
      border: 1px solid var(--border);
      border-radius: 16px;
    }

    .summary-item,
    .cost-chip,
    .stage-tile,
    .card,
    .recent-card {
      padding: 16px;
    }

    .summary-item .label,
    .cost-chip .label,
    .meta,
    .card-meta {
      color: var(--muted);
      font-size: 0.84rem;
    }

    .summary-item .value,
    .cost-chip .value {
      margin-top: 6px;
      font-size: 1.1rem;
      font-weight: 700;
    }

    .stage-flow {
      grid-template-columns: repeat(3, minmax(0, 1fr));
      margin-bottom: 20px;
    }

    .status-pill {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      border-radius: 999px;
      padding: 6px 10px;
      background: rgba(255,255,255,0.06);
      font-size: 0.82rem;
      font-weight: 700;
      margin-top: 10px;
    }

    .status-running { color: var(--warning); }
    .status-completed, .status-done, .status-success { color: var(--success); }
    .status-failed, .status-error { color: var(--danger); }
    .status-pending, .status-skipped, .status-disabled, .status-unknown { color: var(--muted); }

    .cost-chip,
    .card-grid,
    .recent-grid {
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    }

    .card,
    .recent-card {
      display: grid;
      gap: 12px;
      align-content: start;
    }

    .poster {
      width: 100%;
      aspect-ratio: 4 / 3;
      border-radius: 14px;
      border: 1px solid var(--border);
      background: linear-gradient(135deg, rgba(125,211,252,0.18), rgba(192,132,252,0.18));
      object-fit: cover;
      overflow: hidden;
    }

    .poster-placeholder {
      display: grid;
      place-items: center;
      width: 100%;
      aspect-ratio: 4 / 3;
      border-radius: 14px;
      border: 1px dashed var(--border);
      color: var(--muted);
      background: rgba(255,255,255,0.03);
    }

    .card-actions {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
    }

    .section-stack {
      display: grid;
      gap: 18px;
    }

    details {
      padding: 18px;
    }

    details summary {
      cursor: pointer;
      font-weight: 700;
      margin-bottom: 12px;
    }

    pre {
      margin: 0;
      border-radius: 14px;
      padding: 14px;
      background: rgba(8, 17, 31, 0.8);
      border: 1px solid var(--border);
      overflow: auto;
      white-space: pre-wrap;
      word-break: break-word;
      color: #dbeafe;
      font-size: 0.88rem;
    }

    .list {
      margin: 0;
      padding-left: 18px;
      color: var(--muted);
    }

    .empty {
      color: var(--muted);
      font-style: italic;
      padding: 8px 0;
    }

    @media (max-width: 900px) {
      body { padding: 16px; }
      .stage-flow { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <div id="app" class="page">Loading dashboard…</div>
  <script>
    async function loadData() {
      const response = await fetch("./dashboard_data.json?ts=" + Date.now(), { cache: "no-store" });
      if (!response.ok) throw new Error("Failed to load dashboard data");
      return response.json();
    }

    function esc(value) {
      return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;");
    }

    function prettyJson(value) {
      return esc(JSON.stringify(value ?? null, null, 2));
    }

    function formatMoney(value) {
      if (typeof value !== "number" || Number.isNaN(value)) return "—";
      return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", minimumFractionDigits: 2, maximumFractionDigits: 4 }).format(value);
    }

    function formatNumber(value) {
      if (typeof value !== "number" || Number.isNaN(value)) return "—";
      return new Intl.NumberFormat("en-US").format(value);
    }

    function humanStatus(value) {
      return String(value || "unknown").replaceAll("_", " ");
    }

    function parseIsoTimestamp(value) {
      if (!value) return null;
      const parsed = new Date(value);
      if (Number.isNaN(parsed.getTime())) return null;
      return parsed;
    }

    function formatClockDuration(totalSeconds) {
      if (typeof totalSeconds !== "number" || Number.isNaN(totalSeconds) || totalSeconds < 0) return "--:--";
      const seconds = Math.max(0, Math.floor(totalSeconds));
      const hours = Math.floor(seconds / 3600);
      const minutes = Math.floor((seconds % 3600) / 60);
      const remainder = seconds % 60;
      const two = (value) => String(value).padStart(2, "0");
      if (hours > 0) {
        return `${two(hours)}:${two(minutes)}:${two(remainder)}`;
      }
      return `${two(minutes)}:${two(remainder)}`;
    }

    function computeLiveDurationSeconds(startedAt, endedAt) {
      const start = parseIsoTimestamp(startedAt);
      if (!start) return null;
      const end = parseIsoTimestamp(endedAt) || new Date();
      return Math.max(0, Math.floor((end.getTime() - start.getTime()) / 1000));
    }

    function formatTimingLines(timing, endedLabel = "Ended") {
      if (!timing) {
        return '<div class="meta" style="margin-top:10px;"><div><strong>Duration:</strong> —</div></div>';
      }
      const rows = [
        ["Duration", timing.duration_human || "—"],
        ["Started", timing.started_at || "—"],
        [endedLabel, timing.completed_at || timing.ended_at || "—"],
      ];
      return `
        <div class="meta" style="margin-top:10px; display:grid; gap:4px;">
          ${rows.map(([label, value]) => `<div><strong>${esc(label)}:</strong> ${esc(value)}</div>`).join("")}
        </div>
      `;
    }

    function openPreview(url) {
      if (!url) return;
      window.open(url, "previewWindow", "popup=yes,width=400,height=700");
    }

    function posterMarkup(url, alt) {
      if (!url) return '<div class="poster-placeholder">No poster yet</div>';
      return `<img class="poster" src="${esc(url)}" alt="${esc(alt || "Poster")}">`;
    }

    function renderPromptHelper(helper) {
      const prompt = esc(helper?.prompt || "");
      const remixPrompt = esc(helper?.remix_prompt || helper?.prompt || "");
      const pollSeconds = esc(helper?.poll_seconds || 5);
      const publishChecked = helper?.publish_enabled ? "checked" : "";
      const uploadChecked = helper?.upload_enabled ? "checked" : "";
      return `
        <section class="hero">
          <div class="eyebrow">Game Generator Dashboard</div>
          <h1>Simple local viewer for this run</h1>
          <p class="hero-subtitle">Keep the existing dashboard contract, but make the experience feel consumer-grade and easy to scan.</p>
          <div class="prompt-helper">
            <label>
              <div class="muted" style="margin-bottom:8px;">Prompt Helper</div>
              <input id="promptInput" type="text" value="${prompt}" data-remix-prompt="${remixPrompt}" data-poll-seconds="${pollSeconds}">
            </label>
            <div class="prompt-actions">
              <label class="toggle"><input id="publishToggle" type="checkbox" ${publishChecked}> publish</label>
              <label class="toggle"><input id="uploadToggle" type="checkbox" ${uploadChecked}> upload</label>
              <button id="copyCommandButton" type="button">Copy Command</button>
            </div>
            <div id="commandPreview" class="command-preview"></div>
          </div>
        </section>
      `;
    }

    function renderRunTimer(view, data) {
      const timing = view?.timing || {};
      const startedAt = timing.started_at || data.started_at || "";
      const endedAt = timing.completed_at || timing.ended_at || data.completed_at || (data.status === "completed" || data.status === "failed" ? data.updated_at : "");
      const initialSeconds = computeLiveDurationSeconds(startedAt, endedAt);
      const statusLabel = humanStatus(view?.status || data.status || "unknown");
      return `
        <section class="section timer-hero">
          <div class="eyebrow">Live Run Timer</div>
          <div
            id="liveRunTimer"
            class="timer-display"
            data-started-at="${esc(startedAt)}"
            data-ended-at="${esc(endedAt)}"
          >${esc(formatClockDuration(initialSeconds))}</div>
          <div class="timer-caption">Elapsed since run start · status: ${esc(statusLabel)}</div>
        </section>
      `;
    }

    function renderSummary(view, data) {
      const timing = view?.timing || {};
      return `
        <div class="summary-grid">
          <div class="summary-item"><div class="label">Prompt</div><div class="value">${esc(view?.prompt || data.prompt || "")}</div></div>
          <div class="summary-item"><div class="label">Run ID</div><div class="value">${esc(view?.run_id || data.run_id || "")}</div></div>
          <div class="summary-item"><div class="label">Status</div><div class="value">${esc(humanStatus(view?.status || data.status))}</div></div>
          <div class="summary-item"><div class="label">Started</div><div class="value">${esc(timing.started_at || data.started_at || "—")}</div></div>
          <div class="summary-item"><div class="label">Finished</div><div class="value">${esc(timing.completed_at || timing.ended_at || data.completed_at || data.updated_at || "—")}</div></div>
          <div class="summary-item"><div class="label">Total Time</div><div class="value">${esc(timing.duration_human || "—")}</div></div>
          <div class="summary-item"><div class="label">Updated</div><div class="value">${esc(data.updated_at || "—")}</div></div>
        </div>
      `;
    }

    function renderStageFlow(stageFlow) {
      if (!Array.isArray(stageFlow) || !stageFlow.length) return "";
      return `
        <div class="stage-flow">
          ${stageFlow.map((item) => `
            <div class="stage-tile">
              <div class="eyebrow" style="margin-bottom:6px;">${esc(item.label)}</div>
              <h3>${esc(humanStatus(item.status))}</h3>
              <div class="status-pill status-${esc(item.status)}">${esc(humanStatus(item.status))}</div>
              <div class="meta" style="margin-top:10px;">${esc(item.cost_story || "")}</div>
              ${formatTimingLines(item.timing, "Ended")}
            </div>
          `).join("")}
        </div>
      `;
    }

    function renderMatchCards(cards) {
      if (!Array.isArray(cards) || !cards.length) return '<div class="empty">Match cards appear as soon as matcher results are available.</div>';
      return `<div class="card-grid">${cards.map((card) => `
        <article class="card">
          ${posterMarkup(card.poster_url, card.title)}
          <div>
            <div class="eyebrow" style="margin-bottom:6px;">Match Result</div>
            <h3>${esc(card.title)}</h3>
            <div class="card-meta">game_id: ${esc(card.game_id)} · rank ${esc(card.rank || "—")}</div>
          </div>
          <div class="muted">${(card.matched_queries || []).map((item) => esc(item)).join(" · ")}</div>
          <div class="card-actions">
            <button type="button" onclick="openPreview('${esc(card.preview_url)}')">Open 400x700</button>
          </div>
        </article>
      `).join("")}</div>`;
    }

    function renderRefactorCards(cards) {
      if (!Array.isArray(cards) || !cards.length) return '<div class="empty">Refactor outputs appear after the refactor step completes.</div>';
      return `<div class="card-grid">${cards.map((card) => `
        <article class="card">
          <div>
            <div class="eyebrow" style="margin-bottom:6px;">${esc(card.status === 'failed' ? 'Refactor Failed' : 'Refactor')}</div>
            <h3>${esc(card.title)}</h3>
            <div class="card-meta">${esc(card.game_id)} · ${esc(humanStatus(card.status || 'unknown'))}</div>
          </div>
          ${card.phase ? `<div class="muted"><strong>Phase:</strong> ${esc(card.phase)}</div>` : ''}
          ${card.local_path ? `<div class="muted"><strong>Path:</strong> ${esc(card.local_path)}</div>` : ''}
          ${card.input_mirror_path ? `<div class="muted"><strong>Input:</strong> ${esc(card.input_mirror_path)}</div>` : ''}
          ${card.upstream_output_path && card.upstream_output_path !== card.local_path ? `<div class="muted"><strong>Upstream Output:</strong> ${esc(card.upstream_output_path)}</div>` : ''}
          ${card.last_error ? `<div class="muted" style="color:#ffb4bf;"><strong>Error:</strong> ${esc(card.last_error)}</div>` : ''}
          <div class="card-actions">
            ${card.preview_url ? `<button type="button" onclick="openPreview('${esc(card.preview_url)}')">Open 400x700</button>` : ''}
          </div>
        </article>
      `).join("")}</div>`;
    }

    function renderPublishCards(cards) {
      if (!Array.isArray(cards) || !cards.length) return '<div class="empty">Publish links appear after publish completes.</div>';
      return `<div class="card-grid">${cards.map((card) => `
        <article class="card">
          ${card.kind === 'status' ? '' : posterMarkup(card.poster_url, card.title)}
          <div>
            <div class="eyebrow" style="margin-bottom:6px;">${esc(card.kind === 'status' ? `Publish ${humanStatus(card.status || 'unknown')}` : 'Published')}</div>
            <h3>${esc(card.title)}</h3>
            ${card.game_id ? `<div class="card-meta">${esc(card.game_id)}</div>` : ''}
          </div>
          ${card.reason ? `<div class="muted"><strong>Reason:</strong> ${esc(card.reason)}</div>` : ''}
          <div class="card-actions">
            ${card.play_cdn_url ? `<button type="button" onclick="window.open('${esc(card.play_cdn_url)}', '_blank')">Open CDN</button>` : ""}
            ${card.local_play_preview_url ? `<button class="ghost" type="button" onclick="openPreview('${esc(card.local_play_preview_url)}')">Open Local 400x700</button>` : ""}
          </div>
        </article>
      `).join("")}</div>`;
    }

    function renderFinalizeCards(cards) {
      if (!Array.isArray(cards) || !cards.length) return '<div class="empty">Finalize paths appear after local output copy completes.</div>';
      return `<div class="card-grid">${cards.map((card) => `
        <article class="card">
          <div>
            <div class="eyebrow" style="margin-bottom:6px;">${esc(card.kind === 'status' ? `Finalize ${humanStatus(card.status || 'unknown')}` : 'Finalized Output')}</div>
            <h3>${esc(card.title)}</h3>
            ${card.game_id ? `<div class="card-meta">${esc(card.game_id)} · ${esc(humanStatus(card.status || 'unknown'))}</div>` : ''}
          </div>
          ${card.local_path ? `<div class="muted"><strong>Path:</strong> ${esc(card.local_path)}</div>` : ''}
          ${card.source_path ? `<div class="muted"><strong>Source:</strong> ${esc(card.source_path)}</div>` : ''}
          ${card.destination ? `<div class="muted"><strong>Destination:</strong> ${esc(card.destination)}</div>` : ''}
          <div class="card-actions">
            ${card.preview_url ? `<button type="button" onclick="openPreview('${esc(card.preview_url)}')">Open 400x700</button>` : ''}
          </div>
        </article>
      `).join("")}</div>`;
    }

    function renderCostStory(costStory) {
      if (!costStory?.tracked) {
        return `
          <section class="section">
            <h2>Spend Story</h2>
            <div class="empty">${esc(costStory?.headline || 'No spend artifacts found yet.')}</div>
          </section>
        `;
      }

      const totals = costStory.totals || {};
      const stageGrid = Array.isArray(costStory.stages) ? costStory.stages : [];
      const games = Array.isArray(costStory.games) ? costStory.games : [];
      const operators = Array.isArray(costStory.operators) ? costStory.operators : [];

      return `
        <section class="section">
          <h2>Spend Story</h2>
          <p class="muted" style="margin-bottom:16px;">${esc(costStory.headline || '')}</p>
          <div class="cost-grid" style="grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); margin-bottom:16px;">
            <div class="cost-chip"><div class="label">Observed API Cost</div><div class="value">${formatMoney(totals.total_cost)}</div></div>
            <div class="cost-chip"><div class="label">Projected USD</div><div class="value">${formatMoney(totals.projected_cost_usd)}</div></div>
            <div class="cost-chip"><div class="label">Total Tokens</div><div class="value">${formatNumber(totals.total_tokens)}</div></div>
            <div class="cost-chip"><div class="label">Tokens incl. cache</div><div class="value">${formatNumber(totals.total_tokens_including_cache)}</div></div>
          </div>
          <div class="stage-flow" style="margin-bottom:16px;">
            ${stageGrid.map((stage) => `
              <div class="stage-tile">
                <div class="eyebrow" style="margin-bottom:6px;">${esc(stage.label)}</div>
                <h3>${stage.tracked ? formatMoney(stage.projected_cost_usd ?? stage.total_cost) : '—'}</h3>
                <div class="meta">${esc(stage.story || '')}</div>
              </div>
            `).join("")}
          </div>
          ${games.length ? `
            <h3 style="margin-bottom:10px;">Per Game</h3>
            <div class="card-grid" style="margin-bottom:16px;">
              ${games.map((game) => `
                <article class="card">
                  <div>
                    <h3>${esc(game.title)}</h3>
                    <div class="card-meta">${esc(game.game_id)}</div>
                  </div>
                  <div class="muted">Observed: ${formatMoney(game.total_cost)} · Projected: ${formatMoney(game.projected_cost_usd)}</div>
                  <div class="muted">Tokens incl. cache: ${formatNumber(game.total_tokens_including_cache)}</div>
                </article>
              `).join("")}
            </div>
          ` : ''}
          ${operators.length ? `
            <h3 style="margin-bottom:10px;">Tracked Operator Steps</h3>
            <div class="card-grid">
              ${operators.map((operator) => `
                <article class="card">
                  <div>
                    <h3>${esc(operator.stage_slug)}</h3>
                    <div class="card-meta">invocations: ${formatNumber(operator.invocation_count)} · duration: ${formatNumber(Math.round((operator.duration_ms || 0) / 1000))}s</div>
                  </div>
                  <div class="muted">Observed: ${formatMoney(operator.total_cost)} · Projected: ${formatMoney(operator.projected_cost_usd)}</div>
                  <div class="muted">Tokens: ${formatNumber(operator.total_tokens)}</div>
                </article>
              `).join("")}
            </div>
          ` : ''}
        </section>
      `;
    }

    function renderRecentRuns(cards) {
      if (!Array.isArray(cards) || !cards.length) {
        return `
          <section class="section">
            <h2>Recent Runs</h2>
            <div class="empty">Published recent runs will show up here with posters and CDN links.</div>
          </section>
        `;
      }

      return `
        <section class="section">
          <h2>Recent Runs</h2>
          <div class="recent-grid">
            ${cards.map((card) => `
              <article class="recent-card">
                ${posterMarkup(card.poster_url, card.title)}
                <div>
                  <h3>${esc(card.title)}</h3>
                  <div class="card-meta">${esc(card.game_id)}</div>
                </div>
                <div class="muted">${esc(card.prompt || '')}</div>
                <div class="card-actions">
                  ${card.play_url ? `<button type="button" onclick="window.open('${esc(card.play_url)}', '_blank')">Open CDN</button>` : ''}
                </div>
              </article>
            `).join("")}
          </div>
        </section>
      `;
    }

    function renderDetails(data, view) {
      return `
        <details id="dig-deeper">
          <summary>Dig deeper</summary>
          <div class="section-stack">
            <section>
              <h3 style="margin-bottom:10px;">Artifacts</h3>
              <pre>${prettyJson(data.artifacts)}</pre>
            </section>
            <section>
              <h3 style="margin-bottom:10px;">Steps</h3>
              <pre>${prettyJson(data.steps)}</pre>
            </section>
            <section>
              <h3 style="margin-bottom:10px;">Recent Events</h3>
              <pre>${prettyJson(data.recent_events)}</pre>
            </section>
            <section>
              <h3 style="margin-bottom:10px;">Error</h3>
              <pre>${prettyJson(data.error)}</pre>
            </section>
            ${view?.dig_deeper?.refactoring_dashboard_path ? `
              <section>
                <h3 style="margin-bottom:10px;">Upstream Refactoring Dashboard Path</h3>
                <pre>${esc(view.dig_deeper.refactoring_dashboard_path)}</pre>
              </section>
            ` : ''}
          </div>
        </details>
      `;
    }

    function refreshCommandPreview() {
      const promptInput = document.getElementById('promptInput');
      const publishToggle = document.getElementById('publishToggle');
      const uploadToggle = document.getElementById('uploadToggle');
      const commandPreview = document.getElementById('commandPreview');
      if (!promptInput || !publishToggle || !uploadToggle || !commandPreview) return;

      const prompt = promptInput.value.trim() || promptInput.defaultValue || '';
      const remixPrompt = promptInput.dataset.remixPrompt || prompt;
      const pollSeconds = promptInput.dataset.pollSeconds || '5';
      const shellQuote = (value) => `'${String(value).replaceAll("'", `'\\''`)}'`;
      const parts = ['python3', 'scripts/demo_pipeline_launch.py', shellQuote(prompt), '--poll-seconds', pollSeconds];
      if (remixPrompt && remixPrompt !== prompt) {
        parts.push('--remix-prompt', shellQuote(remixPrompt));
      }
      if (publishToggle.checked) parts.push('--publish');
      if (uploadToggle.checked) parts.push('--upload');
      commandPreview.textContent = parts.join(' ');
    }

    async function copyCommand() {
      const commandPreview = document.getElementById('commandPreview');
      if (!commandPreview) return;
      await navigator.clipboard.writeText(commandPreview.textContent || '');
      const button = document.getElementById('copyCommandButton');
      if (!button) return;
      const original = button.textContent;
      button.textContent = 'Copied';
      setTimeout(() => { button.textContent = original; }, 1200);
    }

    function updateLiveRunTimer() {
      const timer = document.getElementById('liveRunTimer');
      if (!timer) return;
      const startedAt = timer.dataset.startedAt || '';
      const endedAt = timer.dataset.endedAt || '';
      const seconds = computeLiveDurationSeconds(startedAt, endedAt);
      timer.textContent = formatClockDuration(seconds);
    }

    function installLiveRunTimerTick() {
      if (window.__dashboardLiveRunTimerInterval) {
        window.clearInterval(window.__dashboardLiveRunTimerInterval);
      }
      updateLiveRunTimer();
      window.__dashboardLiveRunTimerInterval = window.setInterval(updateLiveRunTimer, 1000);
    }

    async function render() {
      const app = document.getElementById('app');
      try {
        const data = await loadData();
        const helper = data.prompt_helper || {};
        const view = data.current_run_view || {};

        app.innerHTML = `
          ${renderPromptHelper(helper)}
          ${renderRunTimer(view, data)}
          <section class="section">
            <h2>Current Run</h2>
            ${renderSummary(view, data)}
            ${renderStageFlow(view.stage_flow)}
            <div class="section-stack">
              <section>
                <div class="eyebrow">Match</div>
                ${renderMatchCards(view.match_cards)}
              </section>
              <section>
                <div class="eyebrow">Refactor</div>
                ${renderRefactorCards(view.refactor_cards)}
              </section>
              <section>
                <div class="eyebrow">Publish</div>
                ${renderPublishCards(view.publish_cards)}
              </section>
              <section>
                <div class="eyebrow">Finalize</div>
                ${renderFinalizeCards(view.finalize_cards)}
              </section>
              <div>
                <button class="ghost" type="button" onclick="document.getElementById('dig-deeper').open = true; document.getElementById('dig-deeper').scrollIntoView({behavior:'smooth'});">Dig deeper</button>
              </div>
            </div>
          </section>
          ${renderCostStory(data.cost_story || {})}
          ${renderRecentRuns(data.recent_runs || [])}
          ${renderDetails(data, view)}
        `;

        refreshCommandPreview();
        installLiveRunTimerTick();
        document.getElementById('promptInput')?.addEventListener('input', refreshCommandPreview);
        document.getElementById('publishToggle')?.addEventListener('change', refreshCommandPreview);
        document.getElementById('uploadToggle')?.addEventListener('change', refreshCommandPreview);
        document.getElementById('copyCommandButton')?.addEventListener('click', copyCommand);
      } catch (error) {
        app.innerHTML = `<section class="section"><h2>Dashboard failed to load</h2><div class="empty">${esc(error.message)}</div></section>`;
      }
    }

    render();
    setInterval(render, 5000);
  </script>
</body>
</html>
"""