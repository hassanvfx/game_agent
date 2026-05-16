#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any

from creative_refactor_runtime import execute_worker_command, load_json, utc_now, update_json_file, write_json
from operator_registry_v2 import (
    DEFAULT_REGISTRY_PATH,
    REPO_ROOT,
    OperatorDefinition,
    OperatorRegistry,
    OperatorRegistryError,
    load_registry,
    resolve_step,
    resolve_through,
)


FIXTURE_ROOT = REPO_ROOT / "fixtures" / "operator_pipeline_lab"
DEFAULT_LAB_RUN_ID = "dry_run_preview"


class LabRunnerError(ValueError):
    """Raised when the operator pipeline lab fixture or request is invalid."""


def repo_relative(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def fixture_manifest_path(fixture_id: str) -> Path:
    return FIXTURE_ROOT / fixture_id / "lab_manifest.json"


def load_fixture_manifest(fixture_id: str) -> dict[str, Any]:
    path = fixture_manifest_path(fixture_id)
    if not path.exists():
        raise LabRunnerError(f"Fixture manifest not found: {repo_relative(path)}")
    try:
        payload = load_json(path)
    except json.JSONDecodeError as exc:
        raise LabRunnerError(f"Fixture manifest is not valid JSON: {repo_relative(path)}: {exc}") from exc

    if not isinstance(payload, dict):
        raise LabRunnerError(f"Fixture manifest must be a JSON object: {repo_relative(path)}")
    manifest_fixture_id = payload.get("fixture_id")
    if manifest_fixture_id != fixture_id:
        raise LabRunnerError(
            f"Fixture id mismatch in {repo_relative(path)}: expected '{fixture_id}', "
            f"got '{manifest_fixture_id}'"
        )
    return payload


def require_manifest_string(manifest: dict[str, Any], key: str) -> str:
    value = manifest.get(key)
    if not isinstance(value, str) or not value.strip():
        raise LabRunnerError(f"Fixture manifest field '{key}' must be a non-empty string")
    return value


def require_manifest_list(manifest: dict[str, Any], key: str) -> list[str]:
    value = manifest.get(key)
    if not isinstance(value, list) or not value:
        raise LabRunnerError(f"Fixture manifest field '{key}' must be a non-empty array")
    if not all(isinstance(item, str) and item.strip() for item in value):
        raise LabRunnerError(f"Fixture manifest field '{key}' must contain only non-empty strings")
    return value


def resolve_repo_path(path_value: str) -> Path:
    path = Path(path_value)
    if not path.is_absolute():
        path = REPO_ROOT / path
    return path.resolve()


def validate_json_file(path: Path, label: str) -> None:
    if not path.exists():
        raise LabRunnerError(f"{label} not found: {repo_relative(path)}")
    if not path.is_file():
        raise LabRunnerError(f"{label} is not a file: {repo_relative(path)}")
    try:
        load_json(path)
    except json.JSONDecodeError as exc:
        raise LabRunnerError(f"{label} is not valid JSON: {repo_relative(path)}: {exc}") from exc


def validate_directory(path: Path, label: str) -> None:
    if not path.exists():
        raise LabRunnerError(f"{label} not found: {repo_relative(path)}")
    if not path.is_dir():
        raise LabRunnerError(f"{label} is not a directory: {repo_relative(path)}")


def validate_fixture_references(manifest: dict[str, Any]) -> dict[str, Path]:
    known_good_run_dir = resolve_repo_path(require_manifest_string(manifest, "known_good_run_dir"))
    source_manifest_path = resolve_repo_path(require_manifest_string(manifest, "source_manifest_path"))
    optional_extended_manifest_path = resolve_repo_path(
        require_manifest_string(manifest, "optional_extended_manifest_path")
    )
    adapted_spec_dir = resolve_repo_path(require_manifest_string(manifest, "adapted_spec_dir"))
    audio_catalog_path = resolve_repo_path(require_manifest_string(manifest, "audio_catalog_path"))
    emoji_asset_root = resolve_repo_path(require_manifest_string(manifest, "emoji_asset_root"))

    validate_directory(known_good_run_dir, "Known-good run directory")
    validate_json_file(source_manifest_path, "Source manifest")
    validate_json_file(optional_extended_manifest_path, "Optional extended manifest")
    validate_directory(adapted_spec_dir, "Adapted spec directory")
    validate_json_file(audio_catalog_path, "Audio catalog")
    validate_directory(emoji_asset_root, "Emoji asset root")

    require_manifest_string(manifest, "known_good_run_id")
    require_manifest_string(manifest, "default_style_id")
    require_manifest_string(manifest, "default_remix_prompt")
    require_manifest_list(manifest, "expected_games")

    return {
        "known_good_run_dir": known_good_run_dir,
        "source_manifest_path": source_manifest_path,
        "optional_extended_manifest_path": optional_extended_manifest_path,
        "adapted_spec_dir": adapted_spec_dir,
        "audio_catalog_path": audio_catalog_path,
        "emoji_asset_root": emoji_asset_root,
    }


def make_lab_run_id() -> str:
    compact = utc_now().replace("-", "").replace(":", "").replace("+00:00", "Z")
    return f"opv2_{compact}"


def source_manifest_game_ids(source_manifest_path: Path) -> list[str]:
    source_manifest = load_json(source_manifest_path)
    games = source_manifest.get("games")
    if not isinstance(games, list) or not games:
        raise LabRunnerError(
            f"Source manifest must contain a non-empty games array: {repo_relative(source_manifest_path)}"
        )

    game_ids: list[str] = []
    for raw_game in games:
        if not isinstance(raw_game, dict):
            raise LabRunnerError("Source manifest games entries must be objects")
        game_id = raw_game.get("game_id")
        if not isinstance(game_id, str) or not game_id.strip():
            raise LabRunnerError("Source manifest game entry missing non-empty game_id")
        game_ids.append(game_id)
    return game_ids


def load_source_games(source_manifest_path: Path, expected_games: list[str]) -> list[dict[str, Any]]:
    source_manifest = load_json(source_manifest_path)
    games = source_manifest.get("games")
    if not isinstance(games, list) or not games:
        raise LabRunnerError(
            f"Source manifest must contain a non-empty games array: {repo_relative(source_manifest_path)}"
        )

    expected = set(expected_games)
    loaded: list[dict[str, Any]] = []
    for raw_game in games:
        if not isinstance(raw_game, dict):
            raise LabRunnerError("Source manifest games entries must be objects")
        game_id = raw_game.get("game_id")
        source_path_value = raw_game.get("source_path")
        display_name = raw_game.get("display_name", game_id)

        if not isinstance(game_id, str) or not game_id.strip():
            raise LabRunnerError("Source manifest game entry missing non-empty game_id")
        if game_id not in expected:
            continue
        if not isinstance(source_path_value, str) or not source_path_value.strip():
            raise LabRunnerError(f"Source manifest game '{game_id}' missing non-empty source_path")
        if not isinstance(display_name, str) or not display_name.strip():
            display_name = game_id

        source_path = Path(source_path_value).expanduser().resolve()
        validate_directory(source_path, f"Source game workspace for {game_id}")

        loaded.append(
            {
                "game_id": game_id,
                "display_name": display_name,
                "source_path": source_path,
            }
        )

    loaded_ids = {game["game_id"] for game in loaded}
    missing = sorted(expected - loaded_ids)
    if missing:
        raise LabRunnerError(
            "Source manifest does not contain expected fixture games: "
            + ", ".join(missing)
        )

    return sorted(loaded, key=lambda game: expected_games.index(game["game_id"]))


def copy_workspace(source: Path, destination: Path) -> None:
    if destination.exists():
        raise LabRunnerError(f"Refusing to overwrite existing workspace: {repo_relative(destination)}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(
        source,
        destination,
        symlinks=True,
        ignore=shutil.ignore_patterns("__pycache__", ".DS_Store"),
    )


def replace_workspace(source: Path, destination: Path) -> None:
    validate_directory(source, "Workspace to promote")
    if destination.exists():
        shutil.rmtree(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(
        source,
        destination,
        symlinks=True,
        ignore=shutil.ignore_patterns("__pycache__", ".DS_Store"),
    )


def load_lab_run_state(fixture_id: str, lab_run_id: str) -> tuple[Path, dict[str, Any]]:
    root = artifact_root(fixture_id, lab_run_id)
    state_path = root / "lab_run_state.json"
    if not state_path.exists():
        raise LabRunnerError(f"Lab run state not found: {repo_relative(state_path)}")
    state = load_json(state_path)
    if not isinstance(state, dict):
        raise LabRunnerError(f"Lab run state must be a JSON object: {repo_relative(state_path)}")
    if state.get("fixture_id") != fixture_id:
        raise LabRunnerError(
            f"Lab run fixture mismatch: expected '{fixture_id}', got '{state.get('fixture_id')}'"
        )
    if state.get("lab_run_id") != lab_run_id:
        raise LabRunnerError(
            f"Lab run id mismatch: expected '{lab_run_id}', got '{state.get('lab_run_id')}'"
        )
    return state_path, state


def find_game_state(state: dict[str, Any], game_id: str) -> dict[str, Any]:
    games = state.get("games")
    if not isinstance(games, list):
        raise LabRunnerError("Lab run state field 'games' must be an array")
    for game in games:
        if isinstance(game, dict) and game.get("game_id") == game_id:
            return game
    raise LabRunnerError(f"Game '{game_id}' is not present in lab run '{state.get('lab_run_id')}'")


def find_stage_state(game_state: dict[str, Any], operator: OperatorDefinition) -> dict[str, Any]:
    stages = game_state.get("stages")
    if not isinstance(stages, list):
        raise LabRunnerError(f"Game '{game_state.get('game_id')}' field 'stages' must be an array")
    for stage in stages:
        if isinstance(stage, dict) and stage.get("stage_slug") == operator.stage_slug:
            return stage
    raise LabRunnerError(
        f"Stage '{operator.stage_slug}' is not present for game '{game_state.get('game_id')}'"
    )


def artifact_root(fixture_id: str, lab_run_id: str) -> Path:
    return FIXTURE_ROOT / fixture_id / "runs" / lab_run_id


def attempt_paths(game_root: Path, operator: OperatorDefinition, attempt_number: int) -> dict[str, Path]:
    attempt_root = (
        game_root
        / "pipeline"
        / operator.stage_slug
        / f"attempt_{attempt_number:02d}"
    )
    return {
        "attempt_root": attempt_root,
        "workspace": attempt_root / "workspace",
        "operator_stage_state": attempt_root / "operator_stage_state.json",
        "operator_prompt": attempt_root / "operator_prompt.txt",
        "operator_stdout": attempt_root / "operator_stdout.txt",
        "operator_stderr": attempt_root / "operator_stderr.txt",
        "operator_result": attempt_root / "operator_result.json",
        "operator_invocation": attempt_root / "operator_invocation.json",
    }


def selected_operators_from_args(
    registry: OperatorRegistry,
    step: str | None,
    through: str | None,
) -> tuple[OperatorDefinition, ...]:
    if bool(step) == bool(through):
        raise LabRunnerError("Specify exactly one of --step or --through")
    if step:
        return resolve_step(registry, step)
    if through:
        return resolve_through(registry, through)
    raise LabRunnerError("No operator selection provided")


def print_registry(registry: OperatorRegistry) -> None:
    print(json.dumps(registry.to_dict(), indent=2))


def print_fixture_summary(
    fixture_id: str,
    manifest: dict[str, Any],
    paths: dict[str, Path],
) -> None:
    print("Fixture")
    print(f"  id: {fixture_id}")
    print(f"  description: {manifest.get('description', '')}")
    print(f"  known_good_run_id: {manifest['known_good_run_id']}")
    print(f"  known_good_run_dir: {repo_relative(paths['known_good_run_dir'])}")
    print(f"  source_manifest_path: {repo_relative(paths['source_manifest_path'])}")
    print(f"  adapted_spec_dir: {repo_relative(paths['adapted_spec_dir'])}")
    print(f"  audio_catalog_path: {repo_relative(paths['audio_catalog_path'])}")
    print(f"  emoji_asset_root: {repo_relative(paths['emoji_asset_root'])}")
    print(f"  default_style_id: {manifest['default_style_id']}")
    print(f"  default_remix_prompt: {manifest['default_remix_prompt']}")
    print("  expected_games:")
    for game_id in manifest["expected_games"]:
        print(f"    - {game_id}")


def print_operator_plan(registry: OperatorRegistry, operators: tuple[OperatorDefinition, ...]) -> None:
    print("Selected operators")
    print(f"  pipeline_id: {registry.pipeline_id}")
    print(f"  max_retries_per_stage: {registry.max_retries_per_stage}")
    print(f"  default_agent_timeout_seconds: {registry.default_agent_timeout_seconds}")
    for operator in operators:
        print(f"  - {operator.stage_slug}")
        print(f"      id: {operator.id}")
        print(f"      prompt: {repo_relative(operator.prompt)}")
        print(f"      summary_required: {str(operator.summary_required).lower()}")


def build_initial_stage_states(registry: OperatorRegistry) -> list[dict[str, Any]]:
    return [
        {
            "operator_id": operator.id,
            "stage_number": operator.stage_number,
            "stage_slug": operator.stage_slug,
            "status": "pending",
            "attempts": [],
        }
        for operator in registry.operators
    ]


def build_lab_run_state(
    fixture_id: str,
    lab_run_id: str,
    manifest: dict[str, Any],
    paths: dict[str, Path],
    registry: OperatorRegistry,
    source_games: list[dict[str, Any]],
) -> dict[str, Any]:
    root = artifact_root(fixture_id, lab_run_id)
    created_at = utc_now()
    games: list[dict[str, Any]] = []

    for game in source_games:
        game_root = root / "games" / game["game_id"]
        games.append(
            {
                "game_id": game["game_id"],
                "display_name": game["display_name"],
                "status": "initialized",
                "source_path": str(game["source_path"]),
                "input_path": repo_relative(game_root / "input"),
                "current_workspace_path": repo_relative(game_root / "pipeline" / "current"),
                "current_stage": None,
                "completed_stages": [],
                "failed_stages": [],
                "stages": build_initial_stage_states(registry),
            }
        )

    return {
        "lab_run_id": lab_run_id,
        "fixture_id": fixture_id,
        "pipeline_id": registry.pipeline_id,
        "status": "initialized",
        "mode": "lab_local_workspace_initialized",
        "created_at": created_at,
        "updated_at": created_at,
        "creates_production_runs": False,
        "invokes_workers": False,
        "invokes_cline": False,
        "max_retries_per_stage": registry.max_retries_per_stage,
        "default_agent_timeout_seconds": registry.default_agent_timeout_seconds,
        "fixture_manifest_path": repo_relative(fixture_manifest_path(fixture_id)),
        "known_good_run_id": manifest["known_good_run_id"],
        "known_good_run_dir": repo_relative(paths["known_good_run_dir"]),
        "source_manifest_path": repo_relative(paths["source_manifest_path"]),
        "adapted_spec_dir": repo_relative(paths["adapted_spec_dir"]),
        "audio_catalog_path": repo_relative(paths["audio_catalog_path"]),
        "emoji_asset_root": repo_relative(paths["emoji_asset_root"]),
        "default_style_id": manifest["default_style_id"],
        "default_remix_prompt": manifest["default_remix_prompt"],
        "artifact_root": repo_relative(root),
        "games": games,
    }


def print_run_summary(state: dict[str, Any]) -> None:
    print("Operator Pipeline v2 lab run")
    print(f"  lab_run_id: {state['lab_run_id']}")
    print(f"  fixture_id: {state['fixture_id']}")
    print(f"  pipeline_id: {state['pipeline_id']}")
    print(f"  status: {state['status']}")
    print(f"  mode: {state['mode']}")
    print(f"  artifact_root: {state['artifact_root']}")
    print(f"  creates_production_runs: {str(state['creates_production_runs']).lower()}")
    print(f"  invokes_workers: {str(state['invokes_workers']).lower()}")
    print(f"  invokes_cline: {str(state['invokes_cline']).lower()}")
    print(f"  max_retries_per_stage: {state['max_retries_per_stage']}")
    print("  games:")
    for game in state["games"]:
        print(f"    - {game['game_id']}")
        print(f"        display_name: {game['display_name']}")
        print(f"        status: {game['status']}")
        print(f"        input_path: {game['input_path']}")
        print(f"        current_workspace_path: {game['current_workspace_path']}")
        print(f"        completed_stages: {len(game['completed_stages'])}")
        print(f"        failed_stages: {len(game['failed_stages'])}")


def summarize_attempt_state(root: Path, game_id: str, stage_slug: str) -> dict[str, Any] | None:
    stage_root = root / "games" / game_id / "pipeline" / stage_slug
    attempts = sorted(stage_root.glob("attempt_*"))
    if not attempts:
        return None

    latest = attempts[-1]
    state_path = latest / "operator_stage_state.json"
    result_path = latest / "operator_result.json"
    payload: dict[str, Any] = {
        "attempt": latest.name,
        "attempt_root": repo_relative(latest),
        "stage_state_path": repo_relative(state_path),
        "result_path": repo_relative(result_path),
        "stage_status": "missing_state",
        "result_status": None,
        "heartbeat_at": None,
    }

    if state_path.exists():
        state = load_json(state_path)
        if isinstance(state, dict):
            payload["stage_status"] = state.get("status")
            payload["heartbeat_at"] = state.get("heartbeat_at")
            payload["updated_at"] = state.get("updated_at")

    if result_path.exists():
        result = load_json(result_path)
        if isinstance(result, dict):
            payload["result_status"] = result.get("status")
            payload["summary"] = result.get("summary")

    return payload


def print_resume_summary(registry: OperatorRegistry, state: dict[str, Any]) -> None:
    root = REPO_ROOT / state["artifact_root"]
    operators = list(registry.operators)

    print("Operator Pipeline v2 run summary")
    print(f"  lab_run_id: {state['lab_run_id']}")
    print(f"  fixture_id: {state['fixture_id']}")
    print(f"  pipeline_id: {state['pipeline_id']}")
    print(f"  status: {state['status']}")
    print(f"  artifact_root: {state['artifact_root']}")

    games = state.get("games", [])
    if not isinstance(games, list):
        raise LabRunnerError("Lab run state field 'games' must be an array")

    print(f"  games_total: {len(games)}")
    for game in games:
        if not isinstance(game, dict):
            continue
        game_id = game.get("game_id")
        if not isinstance(game_id, str):
            continue

        completed = game.get("completed_stages", [])
        failed = game.get("failed_stages", [])
        completed = completed if isinstance(completed, list) else []
        failed = failed if isinstance(failed, list) else []

        next_operator = next(
            (operator for operator in operators if operator.stage_slug not in completed),
            None,
        )

        print(f"  game: {game_id}")
        print(f"    display_name: {game.get('display_name')}")
        print(f"    status: {game.get('status')}")
        print(f"    completed_stages: {len(completed)}/{len(operators)}")
        print(f"    failed_stages: {len(failed)}")
        print(f"    current_stage: {game.get('current_stage')}")
        print(f"    next_stage: {next_operator.stage_slug if next_operator else 'complete'}")

        for operator in operators:
            attempt_summary = summarize_attempt_state(root, game_id, operator.stage_slug)
            status = "completed" if operator.stage_slug in completed else "pending"
            if operator.stage_slug in failed:
                status = "failed"

            print(f"    - {operator.stage_slug}: {status}")
            if attempt_summary:
                print(f"        latest_attempt: {attempt_summary['attempt']}")
                print(f"        stage_status: {attempt_summary.get('stage_status')}")
                print(f"        result_status: {attempt_summary.get('result_status')}")
                if attempt_summary.get("heartbeat_at"):
                    print(f"        heartbeat_at: {attempt_summary['heartbeat_at']}")

        if next_operator:
            print("    recommended_resume:")
            print(
                "      python3 scripts/operator_pipeline_lab.py run-progressive "
                f"--fixture {state['fixture_id']} "
                f"--lab-run-id {state['lab_run_id']} "
                f"--game-id {game_id} "
                f"--from-stage {next_operator.id} "
                f"--through final_code_ui_mobile_repair "
                "--model gpt-5.4 --agent-timeout 900 --execute"
            )

    fixture_summary = state.get("fixture_run_summary")
    if fixture_summary:
        print("  fixture_run_summary:")
        print(json.dumps(fixture_summary, indent=4))


def build_operator_prompt_text(
    fixture_id: str,
    lab_run_id: str,
    state: dict[str, Any],
    game_state: dict[str, Any],
    operator: OperatorDefinition,
    attempt_number: int,
    attempt_workspace: Path,
    current_workspace: Path,
) -> str:
    operator_prompt = operator.prompt.read_text(encoding="utf-8")
    retry_context = "No previous attempts for this stage." if attempt_number == 1 else (
        "Use prior attempt stdout/stderr/operator_result artifacts from this stage as retry context."
    )

    return f"""# Operator Pipeline v2 Prompt Packet

## Lab Invocation

- fixture_id: {fixture_id}
- lab_run_id: {lab_run_id}
- pipeline_id: {state["pipeline_id"]}
- game_id: {game_state["game_id"]}
- display_name: {game_state["display_name"]}
- operator_id: {operator.id}
- stage_number: {operator.stage_number}
- stage_slug: {operator.stage_slug}
- attempt_number: {attempt_number}
- max_retries_per_stage: {state["max_retries_per_stage"]}

## Workspace Contract

Edit only this working clone path:

```text
{attempt_workspace}
```

The previous/latest-good workspace copied into this attempt was:

```text
{current_workspace}
```

Do not modify files outside the working clone path.

## Fixture Context

- known_good_run_id: {state["known_good_run_id"]}
- known_good_run_dir: {state["known_good_run_dir"]}
- source_manifest_path: {state["source_manifest_path"]}
- adapted_spec_dir: {state["adapted_spec_dir"]}
- audio_catalog_path: {state["audio_catalog_path"]}
- emoji_asset_root: {state["emoji_asset_root"]}
- default_style_id: {state["default_style_id"]}
- default_remix_prompt: {state["default_remix_prompt"]}

## Retry Context

{retry_context}

## Required Stdout Contract

End your response with exactly these lines, using one-line values:

```text
OPERATOR STATUS: completed|failed
CHANGED FILES: file1, file2 or NONE
SUMMARY: one short sentence
MECHANICS CHECK: preserved|issues
VISUAL CHECK: preserved|updated|issues
AUDIO CHECK: integrated|not_applicable|issues
MOBILE CHECK: safe|not_checked|issues
```

---

{operator_prompt}
"""


def build_operator_invocation(
    fixture_id: str,
    lab_run_id: str,
    game_state: dict[str, Any],
    operator: OperatorDefinition,
    attempt_number: int,
    paths: dict[str, Path],
    current_workspace: Path,
) -> dict[str, Any]:
    return {
        "created_at": utc_now(),
        "fixture_id": fixture_id,
        "lab_run_id": lab_run_id,
        "game_id": game_state["game_id"],
        "operator_id": operator.id,
        "stage_number": operator.stage_number,
        "stage_slug": operator.stage_slug,
        "attempt_number": attempt_number,
        "operator_prompt_template": repo_relative(operator.prompt),
        "source_current_workspace": repo_relative(current_workspace),
        "working_clone_path": repo_relative(paths["workspace"]),
        "operator_prompt_path": repo_relative(paths["operator_prompt"]),
        "operator_stage_state_path": repo_relative(paths["operator_stage_state"]),
        "operator_stdout_path": repo_relative(paths["operator_stdout"]),
        "operator_stderr_path": repo_relative(paths["operator_stderr"]),
        "operator_result_path": repo_relative(paths["operator_result"]),
        "operator_invocation_path": repo_relative(paths["operator_invocation"]),
        "execute_worker": False,
    }


def parse_operator_stdout(stdout_text: str, fallback_status: str) -> dict[str, Any]:
    expected_keys = {
        "OPERATOR STATUS": "operator_status",
        "CHANGED FILES": "changed_files_raw",
        "SUMMARY": "summary",
        "MECHANICS CHECK": "mechanics_check",
        "VISUAL CHECK": "visual_check",
        "AUDIO CHECK": "audio_check",
        "MOBILE CHECK": "mobile_check",
    }
    parsed: dict[str, Any] = {
        "operator_status": fallback_status,
        "changed_files": [],
        "changed_files_raw": "NONE",
        "summary": "",
        "mechanics_check": "issues",
        "visual_check": "issues",
        "audio_check": "issues",
        "mobile_check": "issues",
        "stdout_contract_present": False,
    }

    found_keys: set[str] = set()
    for line in stdout_text.splitlines():
        for marker, target_key in expected_keys.items():
            prefix = f"{marker}:"
            if line.startswith(prefix):
                value = line[len(prefix):].strip()
                parsed[target_key] = value
                found_keys.add(marker)

    changed_files_raw = str(parsed["changed_files_raw"]).strip()
    if changed_files_raw and changed_files_raw.upper() != "NONE":
        parsed["changed_files"] = [
            item.strip()
            for item in changed_files_raw.split(",")
            if item.strip()
        ]

    parsed["stdout_contract_present"] = set(expected_keys).issubset(found_keys)
    if not parsed["summary"]:
        stripped = stdout_text.strip()
        parsed["summary"] = stripped.splitlines()[0][:300] if stripped else "No operator summary emitted."

    return parsed


def build_operator_stage_state(
    operator: OperatorDefinition,
    attempt_number: int,
    paths: dict[str, Path],
) -> dict[str, Any]:
    now = utc_now()
    return {
        "status": "prompt_built",
        "created_at": now,
        "updated_at": now,
        "operator_id": operator.id,
        "stage_number": operator.stage_number,
        "stage_slug": operator.stage_slug,
        "attempt_number": attempt_number,
        "workspace_path": repo_relative(paths["workspace"]),
        "operator_prompt_path": repo_relative(paths["operator_prompt"]),
        "operator_stdout_path": repo_relative(paths["operator_stdout"]),
        "operator_stderr_path": repo_relative(paths["operator_stderr"]),
        "operator_result_path": repo_relative(paths["operator_result"]),
        "operator_invocation_path": repo_relative(paths["operator_invocation"]),
        "worker_invoked": False,
    }


def print_artifact_plan(
    fixture_id: str,
    lab_run_id: str,
    expected_games: list[str],
    operators: tuple[OperatorDefinition, ...],
    max_retries_per_stage: int,
) -> None:
    root = artifact_root(fixture_id, lab_run_id)
    print("Planned artifact layout")
    print(f"  lab_run_id: {lab_run_id}")
    print(f"  root: {repo_relative(root)}")
    print(f"  lab_run_state: {repo_relative(root / 'lab_run_state.json')}")

    for game_id in expected_games:
        game_root = root / "games" / game_id
        print(f"  game: {game_id}")
        print(f"    input: {repo_relative(game_root / 'input')}")
        print(f"    current: {repo_relative(game_root / 'pipeline' / 'current')}")
        for operator in operators:
            stage_root = game_root / "pipeline" / operator.stage_slug
            print(f"    stage: {operator.stage_slug}")
            print(f"      stage_root: {repo_relative(stage_root)}")
            for attempt_number in range(1, max_retries_per_stage + 1):
                paths = attempt_paths(game_root, operator, attempt_number)
                print(f"      attempt_{attempt_number:02d}:")
                print(f"        workspace: {repo_relative(paths['workspace'])}")
                print(f"        state: {repo_relative(paths['operator_stage_state'])}")
                print(f"        prompt: {repo_relative(paths['operator_prompt'])}")
                print(f"        stdout: {repo_relative(paths['operator_stdout'])}")
                print(f"        stderr: {repo_relative(paths['operator_stderr'])}")
                print(f"        result: {repo_relative(paths['operator_result'])}")
                print(f"        invocation: {repo_relative(paths['operator_invocation'])}")


def run_dry_run(args: argparse.Namespace) -> int:
    registry = load_registry(args.registry)
    manifest = load_fixture_manifest(args.fixture)
    paths = validate_fixture_references(manifest)
    operators = selected_operators_from_args(registry, args.step, args.through)

    print("Operator Pipeline v2 dry-run")
    print("  mode: plan_only")
    print("  creates_production_runs: false")
    print("  invokes_workers: false")
    print("  invokes_cline: false")
    print()
    print_fixture_summary(args.fixture, manifest, paths)
    print()
    print_operator_plan(registry, operators)
    print()
    print_artifact_plan(
        args.fixture,
        args.lab_run_id,
        manifest["expected_games"],
        operators,
        registry.max_retries_per_stage,
    )
    print()
    print("Validation")
    print("  registry: ok")
    print("  fixture_manifest: ok")
    print("  referenced_paths: ok")
    print("  prompt_paths: ok")
    print("  dry_run_only: ok")
    return 0


def run_init_run(args: argparse.Namespace) -> int:
    registry = load_registry(args.registry)
    manifest = load_fixture_manifest(args.fixture)
    paths = validate_fixture_references(manifest)

    if args.source_manifest:
        source_manifest_path = resolve_repo_path(str(args.source_manifest))
        validate_json_file(source_manifest_path, "Override source manifest")
        paths["source_manifest_path"] = source_manifest_path
        expected_games = source_manifest_game_ids(source_manifest_path)
    else:
        expected_games = require_manifest_list(manifest, "expected_games")

    source_games = load_source_games(paths["source_manifest_path"], expected_games)

    lab_run_id = args.lab_run_id or make_lab_run_id()
    root = artifact_root(args.fixture, lab_run_id)
    if root.exists():
        raise LabRunnerError(f"Lab run already exists: {repo_relative(root)}")

    state = build_lab_run_state(
        args.fixture,
        lab_run_id,
        manifest,
        paths,
        registry,
        source_games,
    )

    root.mkdir(parents=True, exist_ok=False)
    for game in source_games:
        game_root = root / "games" / game["game_id"]
        input_path = game_root / "input"
        current_path = game_root / "pipeline" / "current"
        copy_workspace(game["source_path"], input_path)
        copy_workspace(game["source_path"], current_path)

    write_json(root / "lab_run_state.json", state)

    print("Operator Pipeline v2 lab run initialized")
    print(f"  lab_run_id: {lab_run_id}")
    print(f"  root: {repo_relative(root)}")
    print(f"  lab_run_state: {repo_relative(root / 'lab_run_state.json')}")
    print(f"  games_initialized: {len(source_games)}")
    print("  creates_production_runs: false")
    print("  invokes_workers: false")
    print("  invokes_cline: false")
    return 0


def run_inspect_run(args: argparse.Namespace) -> int:
    _, state = load_lab_run_state(args.fixture, args.lab_run_id)
    print_run_summary(state)
    return 0


def run_summarize_run(args: argparse.Namespace) -> int:
    registry = load_registry(args.registry)
    _, state = load_lab_run_state(args.fixture, args.lab_run_id)
    print_resume_summary(registry, state)
    return 0


def run_build_prompt(args: argparse.Namespace) -> int:
    registry = load_registry(args.registry)
    operator = registry.get(args.step)
    state_path, state = load_lab_run_state(args.fixture, args.lab_run_id)
    game_state = find_game_state(state, args.game_id)
    stage_state = find_stage_state(game_state, operator)

    attempt_number = args.attempt
    if attempt_number <= 0:
        raise LabRunnerError("--attempt must be a positive integer")

    root = artifact_root(args.fixture, args.lab_run_id)
    game_root = root / "games" / args.game_id
    current_workspace = (REPO_ROOT / game_state["current_workspace_path"]).resolve()
    validate_directory(current_workspace, f"Current workspace for {args.game_id}")

    paths = attempt_paths(game_root, operator, attempt_number)
    if paths["attempt_root"].exists():
        raise LabRunnerError(
            f"Attempt already exists: {repo_relative(paths['attempt_root'])}. "
            "Use a new --attempt value for retry-safe prompt generation."
        )

    copy_workspace(current_workspace, paths["workspace"])

    prompt_text = build_operator_prompt_text(
        args.fixture,
        args.lab_run_id,
        state,
        game_state,
        operator,
        attempt_number,
        paths["workspace"].resolve(),
        current_workspace,
    )
    paths["operator_prompt"].write_text(prompt_text, encoding="utf-8")

    invocation = build_operator_invocation(
        args.fixture,
        args.lab_run_id,
        game_state,
        operator,
        attempt_number,
        paths,
        current_workspace,
    )
    write_json(paths["operator_invocation"], invocation)

    operator_stage_state = build_operator_stage_state(operator, attempt_number, paths)
    write_json(paths["operator_stage_state"], operator_stage_state)

    stage_attempts = stage_state.setdefault("attempts", [])
    if not isinstance(stage_attempts, list):
        raise LabRunnerError(f"Stage '{operator.stage_slug}' attempts field must be an array")
    stage_state["status"] = "prompt_built"
    stage_state["updated_at"] = utc_now()
    stage_attempts.append(
        {
            "attempt_number": attempt_number,
            "status": "prompt_built",
            "attempt_root": repo_relative(paths["attempt_root"]),
            "workspace_path": repo_relative(paths["workspace"]),
            "operator_prompt_path": repo_relative(paths["operator_prompt"]),
            "operator_stage_state_path": repo_relative(paths["operator_stage_state"]),
            "operator_invocation_path": repo_relative(paths["operator_invocation"]),
            "worker_invoked": False,
        }
    )
    state["updated_at"] = utc_now()
    write_json(state_path, state)

    print("Operator Pipeline v2 prompt packet built")
    print(f"  lab_run_id: {args.lab_run_id}")
    print(f"  game_id: {args.game_id}")
    print(f"  stage: {operator.stage_slug}")
    print(f"  attempt: attempt_{attempt_number:02d}")
    print(f"  workspace: {repo_relative(paths['workspace'])}")
    print(f"  operator_prompt: {repo_relative(paths['operator_prompt'])}")
    print(f"  operator_invocation: {repo_relative(paths['operator_invocation'])}")
    print(f"  operator_stage_state: {repo_relative(paths['operator_stage_state'])}")
    print("  invokes_workers: false")
    print("  invokes_cline: false")
    return 0


def update_attempt_in_state(
    state: dict[str, Any],
    game_id: str,
    operator: OperatorDefinition,
    attempt_number: int,
    status: str,
) -> None:
    game_state = find_game_state(state, game_id)
    stage_state = find_stage_state(game_state, operator)
    attempts = stage_state.get("attempts")
    if not isinstance(attempts, list):
        raise LabRunnerError(f"Stage '{operator.stage_slug}' attempts field must be an array")

    for attempt in attempts:
        if isinstance(attempt, dict) and attempt.get("attempt_number") == attempt_number:
            attempt["status"] = status
            attempt["updated_at"] = utc_now()
            break
    else:
        raise LabRunnerError(
            f"Attempt {attempt_number} is not present for stage '{operator.stage_slug}'"
        )

    stage_state["status"] = status
    stage_state["updated_at"] = utc_now()
    game_state["current_stage"] = operator.stage_slug
    state["updated_at"] = utc_now()


def promote_attempt_workspace(
    state: dict[str, Any],
    game_id: str,
    operator: OperatorDefinition,
    attempt_number: int,
    paths: dict[str, Path],
) -> None:
    game_state = find_game_state(state, game_id)
    stage_state = find_stage_state(game_state, operator)
    current_workspace = (REPO_ROOT / game_state["current_workspace_path"]).resolve()

    replace_workspace(paths["workspace"], current_workspace)

    completed_stages = game_state.setdefault("completed_stages", [])
    if not isinstance(completed_stages, list):
        raise LabRunnerError(f"Game '{game_id}' completed_stages field must be an array")
    if operator.stage_slug not in completed_stages:
        completed_stages.append(operator.stage_slug)

    failed_stages = game_state.setdefault("failed_stages", [])
    if isinstance(failed_stages, list) and operator.stage_slug in failed_stages:
        failed_stages.remove(operator.stage_slug)

    attempts = stage_state.get("attempts")
    if not isinstance(attempts, list):
        raise LabRunnerError(f"Stage '{operator.stage_slug}' attempts field must be an array")

    for attempt in attempts:
        if isinstance(attempt, dict) and attempt.get("attempt_number") == attempt_number:
            attempt["status"] = "promoted"
            attempt["promoted_at"] = utc_now()
            attempt["promoted_to"] = repo_relative(current_workspace)
            break
    else:
        raise LabRunnerError(
            f"Attempt {attempt_number} is not present for stage '{operator.stage_slug}'"
        )

    stage_state["status"] = "completed"
    stage_state["promoted_attempt"] = attempt_number
    stage_state["promoted_at"] = utc_now()
    stage_state["updated_at"] = stage_state["promoted_at"]
    game_state["current_stage"] = None
    game_state["status"] = "initialized"
    state["updated_at"] = utc_now()


def validate_promotable_result(paths: dict[str, Path]) -> dict[str, Any]:
    if not paths["operator_result"].exists():
        raise LabRunnerError(
            f"Operator result not found: {repo_relative(paths['operator_result'])}. "
            "A completed operator_result.json is required for promotion."
        )
    result = load_json(paths["operator_result"])
    if not isinstance(result, dict):
        raise LabRunnerError(f"Operator result must be a JSON object: {repo_relative(paths['operator_result'])}")
    if result.get("status") != "completed":
        raise LabRunnerError(
            f"Attempt is not promotable because operator_result status is '{result.get('status')}'."
        )
    return result


def build_worker_command(
    prompt: str,
    workspace: Path,
    model: str,
    timeout_seconds: int,
) -> list[str]:
    return [
        "cline",
        "-a",
        "-y",
        "-t",
        str(timeout_seconds),
        "--reasoning-effort",
        "high",
        "-c",
        str(workspace),
        "--model",
        model,
        prompt,
    ]


def run_step_execute(args: argparse.Namespace) -> int:
    if not args.execute:
        raise LabRunnerError(
            "run-step refuses real worker execution unless --execute is passed. "
            "Use build-prompt to prepare an attempt safely."
        )

    registry = load_registry(args.registry)
    operator = registry.get(args.step)
    state_path, state = load_lab_run_state(args.fixture, args.lab_run_id)
    game_state = find_game_state(state, args.game_id)
    find_stage_state(game_state, operator)

    attempt_number = args.attempt
    if attempt_number <= 0:
        raise LabRunnerError("--attempt must be a positive integer")

    root = artifact_root(args.fixture, args.lab_run_id)
    game_root = root / "games" / args.game_id
    paths = attempt_paths(game_root, operator, attempt_number)

    validate_directory(paths["workspace"], "Attempt workspace")
    if not paths["operator_prompt"].exists():
        raise LabRunnerError(
            f"Operator prompt not found: {repo_relative(paths['operator_prompt'])}. "
            "Run build-prompt first."
        )
    if not paths["operator_stage_state"].exists():
        raise LabRunnerError(
            f"Operator stage state not found: {repo_relative(paths['operator_stage_state'])}. "
            "Run build-prompt first."
        )

    prompt = paths["operator_prompt"].read_text(encoding="utf-8")
    timeout_seconds = args.agent_timeout or int(state["default_agent_timeout_seconds"])
    command = build_worker_command(prompt, paths["workspace"].resolve(), args.model, timeout_seconds)

    invocation = load_json(paths["operator_invocation"]) if paths["operator_invocation"].exists() else {}
    if not isinstance(invocation, dict):
        invocation = {}
    invocation.update(
        {
            "execute_worker": True,
            "command": [
                *command[:-1],
                "<prompt omitted; see operator_prompt.txt>",
            ],
            "model": args.model,
            "timeout_seconds": timeout_seconds,
            "execution_started_at": utc_now(),
        }
    )
    write_json(paths["operator_invocation"], invocation)

    def mark_stage_running(payload: dict[str, Any]) -> None:
        payload["status"] = "running"
        payload["updated_at"] = utc_now()
        payload["started_at"] = payload.get("started_at") or payload["updated_at"]
        payload["worker_invoked"] = True
        payload["model"] = args.model
        payload["timeout_seconds"] = timeout_seconds

    update_json_file(paths["operator_stage_state"], mark_stage_running)

    state["invokes_workers"] = True
    update_attempt_in_state(state, args.game_id, operator, attempt_number, "running")
    write_json(state_path, state)

    def heartbeat() -> None:
        def mutate(payload: dict[str, Any]) -> None:
            if payload.get("status") == "running":
                payload["heartbeat_at"] = utc_now()
                payload["updated_at"] = payload["heartbeat_at"]

        update_json_file(paths["operator_stage_state"], mutate)

    execution = execute_worker_command(
        command=command,
        cwd=paths["workspace"].resolve(),
        stdout_path=paths["operator_stdout"],
        stderr_path=paths["operator_stderr"],
        timeout_seconds=timeout_seconds,
        heartbeat_callback=heartbeat,
    )

    result_text = execution.stdout_text if execution.stdout_text.strip() else execution.stderr_text
    parsed_stdout = parse_operator_stdout(result_text, execution.status)
    operator_status = str(parsed_stdout["operator_status"]).lower()
    if execution.status != "completed" and operator_status == "completed":
        operator_status = execution.status
    if operator_status not in {"completed", "failed", "timeout"}:
        operator_status = execution.status

    result = {
        "status": operator_status,
        "execution_status": execution.status,
        "returncode": execution.returncode,
        "timed_out": execution.timed_out,
        "fixture_id": args.fixture,
        "lab_run_id": args.lab_run_id,
        "game_id": args.game_id,
        "operator_id": operator.id,
        "stage_number": operator.stage_number,
        "stage_slug": operator.stage_slug,
        "attempt_number": attempt_number,
        "summary": parsed_stdout["summary"],
        "changed_files": parsed_stdout["changed_files"],
        "checks": {
            "mechanics": parsed_stdout["mechanics_check"],
            "visual": parsed_stdout["visual_check"],
            "audio": parsed_stdout["audio_check"],
            "mobile": parsed_stdout["mobile_check"],
        },
        "stdout_contract_present": parsed_stdout["stdout_contract_present"],
        "stdout_path": repo_relative(paths["operator_stdout"]),
        "stderr_path": repo_relative(paths["operator_stderr"]),
        "workspace_path": repo_relative(paths["workspace"]),
        "started_at": execution.started_at,
        "finished_at": execution.finished_at,
        "duration_seconds": execution.duration_seconds,
        "generated_at": utc_now(),
    }
    write_json(paths["operator_result"], result)

    def mark_stage_finished(payload: dict[str, Any]) -> None:
        payload["status"] = operator_status
        payload["updated_at"] = utc_now()
        payload["finished_at"] = payload["updated_at"]
        payload["operator_result_path"] = repo_relative(paths["operator_result"])
        payload["returncode"] = execution.returncode
        payload["timed_out"] = execution.timed_out

    update_json_file(paths["operator_stage_state"], mark_stage_finished)

    state_path, state = load_lab_run_state(args.fixture, args.lab_run_id)
    update_attempt_in_state(state, args.game_id, operator, attempt_number, operator_status)
    if operator_status == "completed":
        promote_attempt_workspace(state, args.game_id, operator, attempt_number, paths)
    write_json(state_path, state)

    print("Operator Pipeline v2 run-step completed")
    print(f"  status: {operator_status}")
    print(f"  execution_status: {execution.status}")
    print(f"  lab_run_id: {args.lab_run_id}")
    print(f"  game_id: {args.game_id}")
    print(f"  stage: {operator.stage_slug}")
    print(f"  attempt: attempt_{attempt_number:02d}")
    print(f"  workspace: {repo_relative(paths['workspace'])}")
    print(f"  stdout: {repo_relative(paths['operator_stdout'])}")
    print(f"  stderr: {repo_relative(paths['operator_stderr'])}")
    print(f"  result: {repo_relative(paths['operator_result'])}")
    if operator_status == "completed":
        print(f"  promoted_to: {repo_relative((REPO_ROOT / game_state['current_workspace_path']).resolve())}")
    return 0 if operator_status == "completed" else 1


def run_promote_attempt(args: argparse.Namespace) -> int:
    registry = load_registry(args.registry)
    operator = registry.get(args.step)
    state_path, state = load_lab_run_state(args.fixture, args.lab_run_id)
    find_game_state(state, args.game_id)

    attempt_number = args.attempt
    if attempt_number <= 0:
        raise LabRunnerError("--attempt must be a positive integer")

    root = artifact_root(args.fixture, args.lab_run_id)
    game_root = root / "games" / args.game_id
    paths = attempt_paths(game_root, operator, attempt_number)
    validate_directory(paths["workspace"], "Attempt workspace")
    validate_promotable_result(paths)

    promote_attempt_workspace(state, args.game_id, operator, attempt_number, paths)
    write_json(state_path, state)

    current_workspace = (REPO_ROOT / find_game_state(state, args.game_id)["current_workspace_path"]).resolve()

    print("Operator Pipeline v2 attempt promoted")
    print(f"  lab_run_id: {args.lab_run_id}")
    print(f"  game_id: {args.game_id}")
    print(f"  stage: {operator.stage_slug}")
    print(f"  attempt: attempt_{attempt_number:02d}")
    print(f"  promoted_to: {repo_relative(current_workspace)}")
    return 0


def mark_stage_failed(
    state: dict[str, Any],
    game_id: str,
    operator: OperatorDefinition,
    reason: str,
) -> None:
    game_state = find_game_state(state, game_id)
    stage_state = find_stage_state(game_state, operator)

    failed_stages = game_state.setdefault("failed_stages", [])
    if not isinstance(failed_stages, list):
        raise LabRunnerError(f"Game '{game_id}' failed_stages field must be an array")
    if operator.stage_slug not in failed_stages:
        failed_stages.append(operator.stage_slug)

    stage_state["status"] = "failed"
    stage_state["failure_reason"] = reason
    stage_state["updated_at"] = utc_now()
    game_state["status"] = "failed"
    game_state["current_stage"] = operator.stage_slug
    state["status"] = "failed"
    state["updated_at"] = utc_now()


def stage_is_completed(state: dict[str, Any], game_id: str, operator: OperatorDefinition) -> bool:
    game_state = find_game_state(state, game_id)
    completed_stages = game_state.get("completed_stages", [])
    return isinstance(completed_stages, list) and operator.stage_slug in completed_stages


def result_status(paths: dict[str, Path]) -> str | None:
    if not paths["operator_result"].exists():
        return None
    result = load_json(paths["operator_result"])
    if not isinstance(result, dict):
        raise LabRunnerError(f"Operator result must be a JSON object: {repo_relative(paths['operator_result'])}")
    status = result.get("status")
    return status if isinstance(status, str) else None


def build_prompt_for_progressive(args: argparse.Namespace, operator: OperatorDefinition, attempt_number: int) -> None:
    prompt_args = argparse.Namespace(
        registry=args.registry,
        fixture=args.fixture,
        lab_run_id=args.lab_run_id,
        game_id=args.game_id,
        step=operator.id,
        attempt=attempt_number,
    )
    run_build_prompt(prompt_args)


def run_step_for_progressive(args: argparse.Namespace, operator: OperatorDefinition, attempt_number: int) -> int:
    step_args = argparse.Namespace(
        registry=args.registry,
        fixture=args.fixture,
        lab_run_id=args.lab_run_id,
        game_id=args.game_id,
        step=operator.id,
        attempt=attempt_number,
        model=args.model,
        agent_timeout=args.agent_timeout,
        execute=True,
    )
    return run_step_execute(step_args)


def run_progressive_execute(args: argparse.Namespace) -> int:
    if not args.execute:
        raise LabRunnerError(
            "run-progressive refuses real worker execution unless --execute is passed. "
            "Use dry-run to inspect the plan safely."
        )
    if not args.game_id:
        raise LabRunnerError("run-progressive requires --game-id")

    registry = load_registry(args.registry)
    selected = list(resolve_through(registry, args.through))

    if args.from_stage:
        start = registry.get(args.from_stage)
        if start.stage_number > registry.get(args.through).stage_number:
            raise LabRunnerError("--from-stage cannot be after --through")
        selected = [
            operator
            for operator in selected
            if operator.stage_number >= start.stage_number
        ]

    state_path, state = load_lab_run_state(args.fixture, args.lab_run_id)
    find_game_state(state, args.game_id)

    print("Operator Pipeline v2 progressive run")
    print(f"  lab_run_id: {args.lab_run_id}")
    print(f"  game_id: {args.game_id}")
    print(f"  through: {args.through}")
    print(f"  max_retries_per_stage: {registry.max_retries_per_stage}")

    for operator in selected:
        state_path, state = load_lab_run_state(args.fixture, args.lab_run_id)
        if stage_is_completed(state, args.game_id, operator):
            print(f"  skip completed: {operator.stage_slug}")
            continue

        print(f"  stage: {operator.stage_slug}")
        stage_completed = False
        last_status = "not_started"

        for attempt_number in range(1, registry.max_retries_per_stage + 1):
            root = artifact_root(args.fixture, args.lab_run_id)
            game_root = root / "games" / args.game_id
            paths = attempt_paths(game_root, operator, attempt_number)

            if not paths["attempt_root"].exists():
                build_prompt_for_progressive(args, operator, attempt_number)

            current_result_status = result_status(paths)
            if current_result_status == "completed":
                state_path, state = load_lab_run_state(args.fixture, args.lab_run_id)
                promote_attempt_workspace(state, args.game_id, operator, attempt_number, paths)
                write_json(state_path, state)
                print(f"    attempt_{attempt_number:02d}: promoted existing completed result")
                stage_completed = True
                break

            print(f"    attempt_{attempt_number:02d}: running")
            step_exit = run_step_for_progressive(args, operator, attempt_number)
            state_path, state = load_lab_run_state(args.fixture, args.lab_run_id)
            last_status = result_status(paths) or ("completed" if step_exit == 0 else "failed")

            if step_exit == 0:
                print(f"    attempt_{attempt_number:02d}: completed and promoted")
                stage_completed = True
                break

            print(f"    attempt_{attempt_number:02d}: {last_status}")

        if not stage_completed:
            state_path, state = load_lab_run_state(args.fixture, args.lab_run_id)
            mark_stage_failed(
                state,
                args.game_id,
                operator,
                f"All attempts failed. Last status: {last_status}",
            )
            write_json(state_path, state)
            print(f"  stage failed: {operator.stage_slug}")
            return 1

    state_path, state = load_lab_run_state(args.fixture, args.lab_run_id)
    state["status"] = "initialized"
    state["updated_at"] = utc_now()
    write_json(state_path, state)

    print("Operator Pipeline v2 progressive run completed")
    return 0


def run_fixture_execute(args: argparse.Namespace) -> int:
    if not args.execute:
        raise LabRunnerError(
            "run-fixture refuses real worker execution unless --execute is passed. "
            "Use inspect-run to review initialized games safely."
        )

    state_path, state = load_lab_run_state(args.fixture, args.lab_run_id)
    games = state.get("games")
    if not isinstance(games, list) or not games:
        raise LabRunnerError("Lab run state field 'games' must be a non-empty array")

    selected_game_ids = [args.game_id] if args.game_id else [
        game["game_id"]
        for game in games
        if isinstance(game, dict) and isinstance(game.get("game_id"), str)
    ]

    if not selected_game_ids:
        raise LabRunnerError("No games selected for run-fixture")

    print("Operator Pipeline v2 fixture run")
    print(f"  lab_run_id: {args.lab_run_id}")
    print(f"  fixture_id: {args.fixture}")
    print(f"  games_total: {len(selected_game_ids)}")
    print(f"  through: {args.through}")

    game_results: list[dict[str, Any]] = []
    for game_id in selected_game_ids:
        print(f"  game: {game_id}")
        progressive_args = argparse.Namespace(
            registry=args.registry,
            fixture=args.fixture,
            lab_run_id=args.lab_run_id,
            game_id=game_id,
            through=args.through,
            from_stage=args.from_stage,
            model=args.model,
            agent_timeout=args.agent_timeout,
            execute=True,
        )

        try:
            exit_code = run_progressive_execute(progressive_args)
            status = "completed" if exit_code == 0 else "failed"
            failure_reason = None if exit_code == 0 else f"run-progressive exited {exit_code}"
        except LabRunnerError as exc:
            status = "failed"
            failure_reason = str(exc)
            exit_code = 1

        game_results.append(
            {
                "game_id": game_id,
                "status": status,
                "exit_code": exit_code,
                "failure_reason": failure_reason,
                "finished_at": utc_now(),
            }
        )

        if status != "completed" and args.fail_fast:
            print(f"  fail-fast stopping after: {game_id}")
            break

    completed = sum(1 for result in game_results if result["status"] == "completed")
    failed = sum(1 for result in game_results if result["status"] != "completed")

    state_path, state = load_lab_run_state(args.fixture, args.lab_run_id)
    state["fixture_run_summary"] = {
        "updated_at": utc_now(),
        "through": args.through,
        "from_stage": args.from_stage,
        "games_total": len(selected_game_ids),
        "games_attempted": len(game_results),
        "games_completed": completed,
        "games_failed": failed,
        "results": game_results,
    }
    state["updated_at"] = utc_now()
    state["status"] = "failed" if failed else "initialized"
    write_json(state_path, state)

    print("Operator Pipeline v2 fixture run finished")
    print(f"  games_attempted: {len(game_results)}")
    print(f"  games_completed: {completed}")
    print(f"  games_failed: {failed}")
    return 0 if failed == 0 else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Fixture-first dry-run lab runner for Operator Pipeline v2.",
    )
    parser.add_argument(
        "--registry",
        type=Path,
        default=DEFAULT_REGISTRY_PATH,
        help=f"Registry config path. Default: {DEFAULT_REGISTRY_PATH.relative_to(REPO_ROOT)}",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("inspect-registry", help="Validate and print the operator registry.")

    init_run = subparsers.add_parser(
        "init-run",
        help="Create a lab-local run with copied fixture input/current workspaces.",
    )
    init_run.add_argument("--fixture", required=True, help="Fixture id, e.g. harry_potter.")
    init_run.add_argument(
        "--lab-run-id",
        help="Optional lab run id. Defaults to a timestamped opv2 id.",
    )
    init_run.add_argument(
        "--source-manifest",
        type=Path,
        help="Optional source manifest override for selecting a different game set.",
    )

    inspect_run = subparsers.add_parser("inspect-run", help="Inspect an initialized lab-local run.")
    inspect_run.add_argument("--fixture", required=True, help="Fixture id, e.g. harry_potter.")
    inspect_run.add_argument("--lab-run-id", required=True, help="Lab run id to inspect.")

    summarize_run = subparsers.add_parser("summarize-run", help="Print a resume-oriented lab run summary.")
    summarize_run.add_argument("--fixture", required=True, help="Fixture id, e.g. harry_potter.")
    summarize_run.add_argument("--lab-run-id", required=True, help="Lab run id to summarize.")

    build_prompt = subparsers.add_parser(
        "build-prompt",
        help="Build one operator prompt packet for a game/stage attempt without invoking workers.",
    )
    build_prompt.add_argument("--fixture", required=True, help="Fixture id, e.g. harry_potter.")
    build_prompt.add_argument("--lab-run-id", required=True, help="Lab run id.")
    build_prompt.add_argument("--game-id", required=True, help="Game id in the lab run.")
    build_prompt.add_argument("--step", required=True, help="Operator id to build a prompt for.")
    build_prompt.add_argument(
        "--attempt",
        type=int,
        default=1,
        help="Attempt number to build. Default: 1",
    )

    dry_run = subparsers.add_parser("dry-run", help="Validate fixture inputs and print a stage plan.")
    dry_run.add_argument("--fixture", required=True, help="Fixture id, e.g. harry_potter.")
    dry_run.add_argument("--step", help="Plan one operator id.")
    dry_run.add_argument("--through", help="Plan all operators through this operator id.")
    dry_run.add_argument(
        "--lab-run-id",
        default=DEFAULT_LAB_RUN_ID,
        help=f"Preview lab run id. Default: {DEFAULT_LAB_RUN_ID}",
    )

    run_step = subparsers.add_parser("run-step", help="Run one prepared operator stage attempt.")
    run_step.add_argument("--fixture", required=True, help="Fixture id, e.g. harry_potter.")
    run_step.add_argument("--lab-run-id", required=True, help="Lab run id.")
    run_step.add_argument("--game-id", required=True, help="Game id in the lab run.")
    run_step.add_argument("--step", required=True, help="Operator id to run.")
    run_step.add_argument(
        "--attempt",
        type=int,
        default=1,
        help="Attempt number to run. Default: 1",
    )
    run_step.add_argument("--model", default="gpt-5.4", help="Cline model to use.")
    run_step.add_argument("--agent-timeout", type=int, help="Override agent timeout seconds.")
    run_step.add_argument("--execute", action="store_true", help="Required for live execution.")

    promote_attempt = subparsers.add_parser(
        "promote-attempt",
        help="Promote a completed stage attempt workspace to pipeline/current.",
    )
    promote_attempt.add_argument("--fixture", required=True, help="Fixture id, e.g. harry_potter.")
    promote_attempt.add_argument("--lab-run-id", required=True, help="Lab run id.")
    promote_attempt.add_argument("--game-id", required=True, help="Game id in the lab run.")
    promote_attempt.add_argument("--step", required=True, help="Operator id to promote.")
    promote_attempt.add_argument(
        "--attempt",
        type=int,
        default=1,
        help="Attempt number to promote. Default: 1",
    )

    run_progressive = subparsers.add_parser(
        "run-progressive",
        help="Run one game's operator stages progressively with retries.",
    )
    run_progressive.add_argument("--fixture", required=True, help="Fixture id, e.g. harry_potter.")
    run_progressive.add_argument("--lab-run-id", required=True, help="Lab run id.")
    run_progressive.add_argument("--game-id", required=True, help="Game id in the lab run.")
    run_progressive.add_argument("--through", required=True, help="Final operator id to run through.")
    run_progressive.add_argument(
        "--from-stage",
        help="Reserved future resume flag for starting from a specific operator id.",
    )
    run_progressive.add_argument("--model", default="gpt-5.4", help="Cline model to use.")
    run_progressive.add_argument("--agent-timeout", type=int, help="Override agent timeout seconds.")
    run_progressive.add_argument("--execute", action="store_true", help="Required for future live execution.")

    run_fixture = subparsers.add_parser(
        "run-fixture",
        help="Run progressive orchestration across games in a lab run.",
    )
    run_fixture.add_argument("--fixture", required=True, help="Fixture id, e.g. harry_potter.")
    run_fixture.add_argument("--lab-run-id", required=True, help="Lab run id.")
    run_fixture.add_argument("--through", required=True, help="Final operator id to run through.")
    run_fixture.add_argument(
        "--from-stage",
        help="Optional resume flag for starting each game from a specific operator id.",
    )
    run_fixture.add_argument("--game-id", help="Optional single-game filter.")
    run_fixture.add_argument("--model", default="gpt-5.4", help="Cline model to use.")
    run_fixture.add_argument("--agent-timeout", type=int, help="Override agent timeout seconds.")
    run_fixture.add_argument("--fail-fast", action="store_true", help="Stop after the first failed game.")
    run_fixture.add_argument("--execute", action="store_true", help="Required for live execution.")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        if args.command == "inspect-registry":
            print_registry(load_registry(args.registry))
            return 0
        if args.command == "init-run":
            return run_init_run(args)
        if args.command == "inspect-run":
            return run_inspect_run(args)
        if args.command == "summarize-run":
            return run_summarize_run(args)
        if args.command == "build-prompt":
            return run_build_prompt(args)
        if args.command == "dry-run":
            return run_dry_run(args)
        if args.command == "run-step":
            return run_step_execute(args)
        if args.command == "promote-attempt":
            return run_promote_attempt(args)
        if args.command == "run-progressive":
            return run_progressive_execute(args)
        if args.command == "run-fixture":
            return run_fixture_execute(args)
    except (LabRunnerError, OperatorRegistryError) as exc:
        parser.exit(status=2, message=f"operator_pipeline_lab: error: {exc}\n")

    parser.exit(status=2, message=f"operator_pipeline_lab: error: unknown command {args.command}\n")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())