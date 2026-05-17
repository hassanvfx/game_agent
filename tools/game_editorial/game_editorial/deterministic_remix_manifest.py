from __future__ import annotations

import hashlib
import json
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_RAW_ROOT = ROOT / "games" / "raw"
DEFAULT_REMIX_IDEAS_PATH = ROOT / "tools" / "game_editorial" / "remix_ideas.json"
DEFAULT_WORKSPACE_ROOT = ROOT / "tools" / "game_editorial" / "scripts" / "workspace"
DEFAULT_OUTPUT_RUNS_ROOT = Path("/Volumes/HDD2026/output-May17th")
DEFAULT_WORKFLOW_ID = "creative_remix_v5"


@dataclass(frozen=True)
class RawGame:
    index: int
    game_id: str
    source_path: Path


@dataclass(frozen=True)
class PromptCatalog:
    thematic_styles: tuple[str, ...]
    thematic_modifiers: tuple[str, ...]
    remix_premise_symbols: tuple[str, ...]

    @property
    def total_combinations(self) -> int:
        return len(self.thematic_styles) * len(self.thematic_modifiers) * len(self.remix_premise_symbols)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def should_ignore_copy_artifact(name: str) -> bool:
    return name == ".DS_Store" or name.startswith("._")


def count_ignored_copy_artifacts(source: Path) -> int:
    return sum(1 for path in source.rglob("*") if should_ignore_copy_artifact(path.name))


def copy_sanitized_directory(source: Path, destination: Path) -> dict[str, Any]:
    if destination.exists():
        shutil.rmtree(destination)

    ignored_count = count_ignored_copy_artifacts(source)

    def ignore_patterns(_directory: str, names: list[str]) -> set[str]:
        return {name for name in names if should_ignore_copy_artifact(name)}

    shutil.copytree(
        source,
        destination,
        copy_function=shutil.copyfile,
        ignore=ignore_patterns,
    )

    return {
        "source_path": str(source),
        "destination_path": str(destination),
        "ignored_artifact_count": ignored_count,
    }


def load_remix_ideas(remix_ideas_path: Path = DEFAULT_REMIX_IDEAS_PATH) -> PromptCatalog:
    payload = load_json(remix_ideas_path)
    thematic_styles = tuple(payload.get("thematicStyles", []))
    thematic_modifiers = tuple(payload.get("thematicModifiers", []))
    remix_premise_symbols = tuple(payload.get("remixPremiseSymbols", []))
    if not thematic_styles or not thematic_modifiers or not remix_premise_symbols:
        raise ValueError(
            "remix_ideas.json must contain non-empty thematicStyles, thematicModifiers, and remixPremiseSymbols arrays"
        )
    return PromptCatalog(
        thematic_styles=thematic_styles,
        thematic_modifiers=thematic_modifiers,
        remix_premise_symbols=remix_premise_symbols,
    )


def build_prompt_catalog(catalog: PromptCatalog) -> list[dict[str, Any]]:
    combinations: list[dict[str, Any]] = []
    combo_index = 0
    for style in catalog.thematic_styles:
        for modifier in catalog.thematic_modifiers:
            for premise_symbol in catalog.remix_premise_symbols:
                combinations.append(
                    {
                        "combo_index": combo_index,
                        "style": style,
                        "modifier": modifier,
                        "premise_symbol": premise_symbol,
                    }
                )
                combo_index += 1
    return combinations


def discover_raw_games(raw_root: Path = DEFAULT_RAW_ROOT) -> list[RawGame]:
    if not raw_root.exists():
        raise FileNotFoundError(f"Raw games root not found: {raw_root}")
    game_dirs = sorted(path for path in raw_root.iterdir() if path.is_dir())
    if not game_dirs:
        raise ValueError(f"No raw game directories found under: {raw_root}")
    return [RawGame(index=index, game_id=path.name, source_path=path.resolve()) for index, path in enumerate(game_dirs)]


def compose_remix_prompt(style: str, modifier: str, premise_symbol: str) -> str:
    return (
        f"Create a deterministic creative remix in a {style} style, centered on a {premise_symbol}, "
        f"{modifier}. Preserve the core playable mechanic loop while rebuilding the theme, identity, surface art, "
        f"world language, and presentation around this new premise."
    )


def stable_combo_selection(effective_seed: int, total_combinations: int) -> int:
    if total_combinations <= 0:
        raise ValueError("total_combinations must be positive")
    digest = hashlib.sha256(f"{effective_seed}".encode("utf-8")).digest()
    return int.from_bytes(digest[:16], "big") % total_combinations


def build_expanded_entries(
    raw_games: list[RawGame],
    prompt_catalog: list[dict[str, Any]],
    prompts_per_game: int,
    seed_offset: int = 0,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if prompts_per_game <= 0:
        raise ValueError("prompts_per_game must be >= 1")

    manifest_entries: list[dict[str, Any]] = []
    trace_entries: list[dict[str, Any]] = []
    total_combinations = len(prompt_catalog)

    for selected_game_index, raw_game in enumerate(raw_games):
        used_combo_indices: set[int] = set()
        for variant_index in range(prompts_per_game):
            effective_seed = seed_offset + (selected_game_index * prompts_per_game) + variant_index
            candidate_offset = 0
            combo_index = stable_combo_selection(effective_seed=effective_seed, total_combinations=total_combinations)
            while combo_index in used_combo_indices and candidate_offset < total_combinations:
                candidate_offset += 1
                combo_index = (combo_index + 1) % total_combinations
            used_combo_indices.add(combo_index)

            combo = prompt_catalog[combo_index]
            prompt_text = compose_remix_prompt(
                style=combo["style"],
                modifier=combo["modifier"],
                premise_symbol=combo["premise_symbol"],
            )
            variant_suffix = f"p{variant_index + 1:02d}"
            manifest_game_id = raw_game.game_id if prompts_per_game == 1 else f"{raw_game.game_id}__{variant_suffix}"
            manifest_entries.append(
                {
                    "game_id": manifest_game_id,
                    "display_name": manifest_game_id,
                    "source_path": str(raw_game.source_path),
                    "remix_prompt": prompt_text,
                }
            )
            trace_entries.append(
                {
                    "base_game_id": raw_game.game_id,
                    "manifest_game_id": manifest_game_id,
                    "source_game_index": raw_game.index,
                    "selected_game_index": selected_game_index,
                    "variant_index": variant_index,
                    "effective_seed": effective_seed,
                    "total_combinations": total_combinations,
                    "selected_combo_index": combo_index,
                    "style": combo["style"],
                    "modifier": combo["modifier"],
                    "premise_symbol": combo["premise_symbol"],
                    "remix_prompt": prompt_text,
                }
            )
    return manifest_entries, trace_entries


def build_run_label(prompts_per_game: int, selected_raw_games_count: int, seed_offset: int = 0) -> str:
    label = f"game-editorial-raw-remix-v5-index-seeded-g{selected_raw_games_count}-ppg-{prompts_per_game}"
    if seed_offset:
        label += f"-offset-{seed_offset}"
    return label


def build_manifest_payload(
    entries: list[dict[str, Any]],
    prompts_per_game: int,
    selected_raw_games_count: int,
    seed_offset: int = 0,
    raw_game_offset: int = 0,
) -> dict[str, Any]:
    return {
        "manifest_version": "1.0.0",
        "run_label": build_run_label(
            prompts_per_game=prompts_per_game,
            selected_raw_games_count=selected_raw_games_count,
            seed_offset=seed_offset,
        ),
        "raw_game_offset": raw_game_offset,
        "games": entries,
    }


def generate_batch_artifacts(
    *,
    prompts_per_game: int,
    raw_root: Path = DEFAULT_RAW_ROOT,
    remix_ideas_path: Path = DEFAULT_REMIX_IDEAS_PATH,
    workspace_root: Path = DEFAULT_WORKSPACE_ROOT,
    game_limit: int | None = None,
    seed_offset: int = 0,
    raw_game_offset: int = 0,
    source_mode: str = "copy",
) -> dict[str, Any]:
    catalog = load_remix_ideas(remix_ideas_path)
    prompt_catalog = build_prompt_catalog(catalog)
    if raw_game_offset < 0:
        raise ValueError("raw_game_offset must be >= 0")

    all_raw_games = discover_raw_games(raw_root)
    if raw_game_offset >= len(all_raw_games):
        raise ValueError(f"raw_game_offset {raw_game_offset} is outside the raw corpus of {len(all_raw_games)} games")

    raw_games = all_raw_games[raw_game_offset:]
    if game_limit is not None:
        if game_limit <= 0:
            raise ValueError("game_limit must be >= 1 when provided")
        raw_games = raw_games[:game_limit]
    if not raw_games:
        raise ValueError("No raw games selected after applying raw_game_offset / game_limit")

    effective_seed_offset = seed_offset + (raw_game_offset * prompts_per_game)

    run_slug = build_run_label(
        prompts_per_game=prompts_per_game,
        selected_raw_games_count=len(raw_games),
        seed_offset=effective_seed_offset,
    )
    if raw_game_offset:
        run_slug += f"-raw-offset-{raw_game_offset}"
    artifact_dir = workspace_root / run_slug
    artifact_dir.mkdir(parents=True, exist_ok=True)

    staged_source_reports: list[dict[str, Any]] = []
    manifest_source_games = raw_games
    if source_mode == "copy":
        sanitized_root = artifact_dir / "sanitized_sources"
        if sanitized_root.exists():
            shutil.rmtree(sanitized_root)
        sanitized_root.mkdir(parents=True, exist_ok=True)

        sanitized_games: list[RawGame] = []
        for raw_game in raw_games:
            sanitized_source_path = sanitized_root / raw_game.game_id
            staged_source_reports.append(copy_sanitized_directory(raw_game.source_path, sanitized_source_path))
            sanitized_games.append(
                RawGame(
                    index=raw_game.index,
                    game_id=raw_game.game_id,
                    source_path=sanitized_source_path.resolve(),
                )
            )
        manifest_source_games = sanitized_games

    manifest_entries, trace_entries = build_expanded_entries(
        raw_games=manifest_source_games,
        prompt_catalog=prompt_catalog,
        prompts_per_game=prompts_per_game,
        seed_offset=effective_seed_offset,
    )

    manifest_payload = build_manifest_payload(
        manifest_entries,
        prompts_per_game=prompts_per_game,
        selected_raw_games_count=len(manifest_source_games),
        seed_offset=effective_seed_offset,
        raw_game_offset=raw_game_offset,
    )
    manifest_path = artifact_dir / "games_manifest.json"
    trace_path = artifact_dir / "prompt_trace.json"
    summary_path = artifact_dir / "summary.json"

    write_json(manifest_path, manifest_payload)
    write_json(trace_path, trace_entries)

    summary = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "workflow_id": DEFAULT_WORKFLOW_ID,
        "prompts_per_game": prompts_per_game,
        "seed_mode": "expanded_entry_index",
        "seed_offset": seed_offset,
        "effective_seed_offset": effective_seed_offset,
        "raw_game_offset": raw_game_offset,
        "source_mode": source_mode,
        "raw_games_count": len(all_raw_games),
        "selected_raw_games_count": len(manifest_source_games),
        "expanded_manifest_entries": len(manifest_entries),
        "total_prompt_combinations": len(prompt_catalog),
        "workspace_root": str(workspace_root),
        "artifact_dir": str(artifact_dir),
        "manifest_path": str(manifest_path),
        "trace_path": str(trace_path),
        "runs_root": str(DEFAULT_OUTPUT_RUNS_ROOT),
        "sanitized_source_root": str(artifact_dir / "sanitized_sources") if source_mode == "copy" else None,
        "staged_source_reports": staged_source_reports,
        "catalog_sizes": {
            "thematic_styles": len(catalog.thematic_styles),
            "thematic_modifiers": len(catalog.thematic_modifiers),
            "remix_premise_symbols": len(catalog.remix_premise_symbols),
        },
        "selected_base_game_ids_sample": [raw_game.game_id for raw_game in manifest_source_games[:5]],
        "sample_effective_seeds": [entry["effective_seed"] for entry in trace_entries[: min(5, len(trace_entries))]],
        "sample_manifest_game_ids": [entry["game_id"] for entry in manifest_entries[:5]],
    }
    write_json(summary_path, summary)
    summary["summary_path"] = str(summary_path)
    return summary