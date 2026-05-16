#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.creative_refactor_runtime import execute_worker_command, load_json, update_json_file, utc_now, write_json
from scripts.media_policy import write_media_policy_report
from scripts.operator_registry_v2 import OperatorDefinition, OperatorRegistry, load_registry, resolve_through


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STYLE_ID = "neutral_prototype"


class OperatorPipelineGameError(RuntimeError):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run operator pipeline v2 for one production game.")
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--game-id", required=True)
    parser.add_argument("--model", default="gpt-5.4")
    parser.add_argument("--agent-timeout", type=int, default=3600)
    parser.add_argument("--style", default=DEFAULT_STYLE_ID)
    parser.add_argument("--remix-prompt")
    parser.add_argument("--through", default="final_code_ui_mobile_repair")
    parser.add_argument("--skip-run-state-update", action="store_true")
    return parser.parse_args()


def repo_relative(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def copy_workspace(source: Path, destination: Path, replace: bool = False) -> None:
    if destination.exists():
        if not replace:
            raise OperatorPipelineGameError(f"Refusing to overwrite workspace: {destination}")
        shutil.rmtree(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(
        source,
        destination,
        symlinks=True,
        ignore=shutil.ignore_patterns("__pycache__", ".DS_Store"),
    )


def attempt_paths(game_dir: Path, operator: OperatorDefinition, attempt_number: int) -> dict[str, Path]:
    attempt_root = game_dir / "operator_pipeline" / operator.stage_slug / f"attempt_{attempt_number:02d}"
    return {
        "attempt_root": attempt_root,
        "workspace": attempt_root / "workspace",
        "operator_stage_state": attempt_root / "operator_stage_state.json",
        "operator_prompt": attempt_root / "operator_prompt.txt",
        "operator_stdout": attempt_root / "operator_stdout.txt",
        "operator_stderr": attempt_root / "operator_stderr.txt",
        "operator_result": attempt_root / "operator_result.json",
        "operator_invocation": attempt_root / "operator_invocation.json",
        "media_policy_report": attempt_root / "media_policy_report.json",
    }


def sanitize_display_name_for_prompt(display_name: Any, game_id: str, remix_prompt: Any) -> str:
    if isinstance(remix_prompt, str):
        prompt_cleaned = remix_prompt.strip()
        if prompt_cleaned:
            return prompt_cleaned

    if not isinstance(display_name, str):
        return "Game Remix"
    cleaned = display_name.strip()
    if not cleaned:
        return "Game Remix"

    lower = cleaned.lower()
    prefixes = (
        "harry potter lab game ",
        "control game ",
        "prompt control game ",
    )
    if lower.startswith(prefixes):
        return "Game Remix"
    return cleaned


def copy_catalogs_into_workspace(workspace: Path) -> dict[str, Path]:
    source_catalog_dir = ROOT / "catalogs"
    if not source_catalog_dir.exists() or not source_catalog_dir.is_dir():
        raise OperatorPipelineGameError(f"Catalog directory is missing: {source_catalog_dir}")

    destination_catalog_dir = workspace / "catalogs"
    destination_catalog_dir.mkdir(parents=True, exist_ok=True)

    required_catalog_names = ("audios.json", "gifs.json", "sprites.json", "fonts.json")
    copied_catalogs: dict[str, Path] = {}
    for catalog_name in required_catalog_names:
        source_catalog_path = source_catalog_dir / catalog_name
        if not source_catalog_path.exists() or not source_catalog_path.is_file():
            raise OperatorPipelineGameError(f"Required catalog file is missing: {source_catalog_path}")
        destination_catalog_path = destination_catalog_dir / catalog_name
        shutil.copy2(source_catalog_path, destination_catalog_path)
        copied_catalogs[catalog_name] = destination_catalog_path.resolve()

    return copied_catalogs


def build_operator_prompt_text(
    run_state: dict[str, Any],
    game_state: dict[str, Any],
    operator: OperatorDefinition,
    attempt_number: int,
    attempt_workspace: Path,
    current_workspace: Path,
    adapted_spec_dir: Path | None,
    workspace_catalogs: dict[str, Path],
    potential_urls_to_remove: list[dict[str, str]] | None = None,
    media_replacement_candidates: list[str] | None = None,
    normalized_media_replacement_refs: list[str] | None = None,
    media_cleanup_plan: list[dict[str, object]] | None = None,
    font_replacement_candidates: list[str] | None = None,
    approved_icon_vocabulary: list[str] | None = None,
) -> str:
    operator_prompt = operator.prompt.read_text(encoding="utf-8")
    retry_context = "No previous attempts for this stage." if attempt_number == 1 else (
        "Use prior attempt stdout/stderr/operator_result artifacts from this stage as retry context."
    )
    prompt_display_name = sanitize_display_name_for_prompt(
        game_state.get("display_name"),
        str(game_state["game_id"]),
        run_state.get("remix_prompt"),
    )

    return f"""# Production Operator Pipeline v2 Prompt Packet

## Invocation

- run_id: {run_state["run_id"]}
- game_id: {game_state["game_id"]}
- display_name: {prompt_display_name}
- operator_id: {operator.id}
- stage_number: {operator.stage_number}
- stage_slug: {operator.stage_slug}
- attempt_number: {attempt_number}
- max_retries_per_stage: {run_state.get("operator_pipeline_v2", {}).get("max_retries_per_stage", 3)}

## Workspace Contract

Edit only this working clone path:

```text
{attempt_workspace}
```

The previous/latest-good workspace copied into this attempt was:

```text
/current
```

Do not modify files outside the working clone path.

## Production Run Context

- run_dir: {run_state.get("run_dir", "unknown")}
- selected_style_id: {run_state.get("selected_style_id")}
- remix_prompt: {run_state.get("remix_prompt")}
- adapted_spec_dir: {adapted_spec_dir if adapted_spec_dir else "NONE"}

## Workspace Catalogs

Use only the workspace-local catalog files listed below for catalog-guided media work:

- catalogs/audios.json:
- catalogs/gifs.json:
- catalogs/sprites.json:
- catalogs/fonts.json:

Do not rely on repo-root catalog paths or other host filesystem catalog references. If mapped media or approved icon/font systems need import plumbing, wire them against these workspace-local catalogs rather than leaving partial setup for a later stage.

## Python Media Policy Hint

REQUIRED URLs to remove for this attempt:

```json
{json.dumps(potential_urls_to_remove or [], indent=2)}
```

This list is computed by Python and is a required main task. Do not invent additional policy rules beyond the provided hint.

## Python Media Replacement Candidates

REQUIRED media references to replace or remap for this attempt:

```json
{json.dumps(media_replacement_candidates or [], indent=2)}
```

If a local or external media reference appears here, do not automatically treat it as acceptable just because it already works. These entries are required mapping/removal work for this stage.

## Generic Replacement Examples

This is what successful replacement looks like:

- audio
  - before: `assets/bgm/0002/old-track.mp3`
  - after: approved catalog-backed audio path or approved replacement wiring
- image
  - before: `assets/sprites/player.png`
  - after: approved sprite/background replacement path
- gif
  - before: `assets/effects/explosion.gif`
  - after: approved GIF replacement path
- video
  - before: `assets/cutscenes/intro.mp4`
  - after: approved replacement path or safe removal when not needed
- font stylesheet
  - before: `assets/fonts.googleapis.com/css2-family_Press_Start_2P_display_swap.css`
  - after: approved `catalogs/fonts.json` choice
- font file
  - before: `assets/fonts/custom.ttf`
  - after: approved catalog-backed font setup

## Python Font / Icon Candidates

REQUIRED font usages to reconsider for this attempt:

```json
{json.dumps(font_replacement_candidates or [], indent=2)}
```

If these font entries are non-empty, treat them as required font-remap work for this stage. Read the existing font usage in the game, inspect `catalogs/fonts.json`, and choose the best matching approved catalog font or font system for each role you find (for example: title/display, HUD/UI, body/readability, retro/pixel accent, or icon-font usage). The replacement choice should be creative, but the cleanup requirement is mandatory: old non-catalog font refs and old mirrored font assets should not remain when they were part of the required remap work for this stage. Approved replacement refs from `catalogs/fonts.json` should not be treated as unresolved just because they are external or catalog-backed.

### Font candidates
```json
{json.dumps(font_replacement_candidates or [], indent=2)}
```

### Icon-font candidates (this section is fixed in the prompt)
```json
[
home
menu
close
search
settings
account_circle
person
group
favorite
favorite_border
star
star_border
check
check_circle
cancel
add
remove
edit
delete
arrow_back
arrow_forward
arrow_upward
arrow_downward
expand_more
expand_less
chevron_left
chevron_right
refresh
sync
download
upload
cloud
cloud_download
cloud_upload
notifications
notifications_none
email
mail
chat
chat_bubble
phone
call
videocam
camera_alt
image
photo
play_arrow
pause
stop
skip_next
skip_previous
volume_up
volume_off
mic
mic_off
lock
lock_open
visibility
visibility_off
shopping_cart
payment
attach_money
credit_card
store
location_on
map
gps_fixed
directions
calendar_today
event
schedule
access_time
alarm
help
info
warning
error
build
code
terminal
bug_report
api
language
public
link
attach_file
folder
folder_open
description
article
dashboard
analytics
bar_chart
pie_chart
trending_up
trending_down
wifi
bluetooth
battery_full
battery_charging_full
power
]
```

If these lists are non-empty, treat them as required Stage 03 signals: font usages must be creatively remapped from `catalogs/fonts.json` where applicable, and icon/font implementations should align with approved catalog-backed systems rather than leaving old non-catalog font usage in place.

## Failure Criteria

This stage failed if any Python-listed bad refs still remain in HTML, JS, CSS, or other actionable source files.

Failure includes:
- required URLs to remove still present
- required media replacement candidates still present
- required bad local `assets/...` refs still present
- operator summaries/comments claiming success while the source files still contain the bad refs

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

    raw_changed = str(parsed["changed_files_raw"]).strip()
    if raw_changed and raw_changed.upper() != "NONE":
        parsed["changed_files"] = [item.strip() for item in raw_changed.split(",") if item.strip()]

    parsed["stdout_contract_present"] = set(expected_keys).issubset(found_keys)
    if not parsed["summary"]:
        stripped = stdout_text.strip()
        parsed["summary"] = stripped.splitlines()[0][:300] if stripped else "No operator summary emitted."
    return parsed


def build_worker_command(prompt: str, workspace: Path, model: str, timeout_seconds: int) -> list[str]:
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


def resolve_adapted_spec_dir(run_state: dict[str, Any]) -> Path | None:
    spec_adaptor = run_state.get("spec_adaptor")
    if isinstance(spec_adaptor, dict):
        adapted = spec_adaptor.get("adapted_dir")
        if adapted:
            return Path(adapted).resolve()
    return None


def write_stage_state(path: Path, operator: OperatorDefinition, attempt_number: int, paths: dict[str, Path]) -> None:
    now = utc_now()
    write_json(
        path,
        {
            "status": "prompt_built",
            "created_at": now,
            "updated_at": now,
            "operator_id": operator.id,
            "stage_number": operator.stage_number,
            "stage_slug": operator.stage_slug,
            "attempt_number": attempt_number,
            "workspace_path": str(paths["workspace"]),
            "operator_prompt_path": str(paths["operator_prompt"]),
            "operator_stdout_path": str(paths["operator_stdout"]),
            "operator_stderr_path": str(paths["operator_stderr"]),
            "operator_result_path": str(paths["operator_result"]),
            "operator_invocation_path": str(paths["operator_invocation"]),
            "media_policy_report_path": str(paths["media_policy_report"]),
            "worker_invoked": False,
        },
    )


def mark_game_failed(game_state_path: Path, message: str) -> None:
    game_state = load_json(game_state_path)
    game_state["status"] = "failed"
    game_state["current_phase"] = "operator_pipeline_failed"
    game_state["creative_phase"] = "operator_pipeline_failed"
    game_state["creative_status"] = "failed"
    game_state["last_error"] = message
    game_state["updated_at"] = utc_now()
    write_json(game_state_path, game_state)


def run_stage_attempt(
    command: list[str],
    workspace: Path,
    paths: dict[str, Path],
    timeout_seconds: int,
) -> Any:
    def heartbeat() -> None:
        def mutate(payload: dict[str, Any]) -> None:
            if payload.get("status") == "running":
                payload["heartbeat_at"] = utc_now()
                payload["updated_at"] = payload["heartbeat_at"]

        update_json_file(paths["operator_stage_state"], mutate)

    return execute_worker_command(
        command=command,
        cwd=workspace,
        stdout_path=paths["operator_stdout"],
        stderr_path=paths["operator_stderr"],
        timeout_seconds=timeout_seconds,
        heartbeat_callback=heartbeat,
    )


def main() -> None:
    args = parse_args()
    run_dir = Path(args.run_dir).resolve()
    game_dir = run_dir / "games" / args.game_id
    game_state_path = game_dir / "game_state.json"
    run_state_path = run_dir / "run_state.json"

    run_state = load_json(run_state_path)
    game_state = load_json(game_state_path)
    registry: OperatorRegistry = load_registry()
    operators = resolve_through(registry, args.through)

    if game_state.get("integrity_status") != "passed":
        raise OperatorPipelineGameError(f"Game {args.game_id} is not integrity-passed and cannot be transformed.")

    input_dir = Path(game_state["input_mirror_path"]).resolve()
    output_dir = Path(game_state["output_path"]).resolve()
    pipeline_dir = game_dir / "operator_pipeline"
    current_workspace = pipeline_dir / "current"
    adapted_spec_dir = resolve_adapted_spec_dir(run_state)

    run_state.setdefault("operator_pipeline_v2", {})
    run_state["operator_pipeline_v2"]["enabled"] = True
    run_state["operator_pipeline_v2"]["max_retries_per_stage"] = registry.max_retries_per_stage
    run_state["operator_pipeline_v2"]["updated_at"] = utc_now()
    write_json(run_state_path, run_state)

    copy_workspace(input_dir, current_workspace, replace=True)

    game_state["status"] = "running"
    game_state["current_phase"] = "operator_pipeline_running"
    game_state["creative_phase"] = "operator_pipeline_running"
    game_state["creative_status"] = "running"
    game_state["selected_style_id"] = args.style
    game_state["remix_prompt"] = args.remix_prompt
    game_state["operator_pipeline_path"] = str(pipeline_dir)
    game_state["creative_output_path"] = str(output_dir)
    game_state["updated_at"] = utc_now()
    write_json(game_state_path, game_state)

    completed_stage_slugs: list[str] = []
    artifacts: list[str] = []

    try:
        for operator in operators:
            stage_completed = False
            last_status = "not_started"

            for attempt_number in range(1, registry.max_retries_per_stage + 1):
                paths = attempt_paths(game_dir, operator, attempt_number)
                copy_workspace(current_workspace, paths["workspace"], replace=False)
                workspace_catalogs = copy_catalogs_into_workspace(paths["workspace"].resolve())
                media_policy_report = write_media_policy_report(paths["workspace"].resolve(), paths["media_policy_report"])
                potential_urls_to_remove = media_policy_report.get("potential_urls_to_remove", [])
                if not isinstance(potential_urls_to_remove, list):
                    potential_urls_to_remove = []
                media_replacement_candidates = media_policy_report.get("actionable_media_replacement_candidate_refs", [])
                if not isinstance(media_replacement_candidates, list):
                    media_replacement_candidates = []
                normalized_media_replacement_refs = media_policy_report.get("normalized_media_replacement_refs", [])
                if not isinstance(normalized_media_replacement_refs, list):
                    normalized_media_replacement_refs = []
                media_cleanup_plan = media_policy_report.get("media_cleanup_plan", [])
                if not isinstance(media_cleanup_plan, list):
                    media_cleanup_plan = []
                font_replacement_candidates = media_policy_report.get("actionable_font_replacement_candidate_refs", [])
                if not isinstance(font_replacement_candidates, list):
                    font_replacement_candidates = []
                approved_icon_vocabulary = media_policy_report.get("approved_icon_vocabulary", [])
                if not isinstance(approved_icon_vocabulary, list):
                    approved_icon_vocabulary = []

                prompt = build_operator_prompt_text(
                    run_state=run_state,
                    game_state=game_state,
                    operator=operator,
                    attempt_number=attempt_number,
                    attempt_workspace=paths["workspace"].resolve(),
                    current_workspace=current_workspace.resolve(),
                    adapted_spec_dir=adapted_spec_dir,
                    workspace_catalogs=workspace_catalogs,
                    potential_urls_to_remove=potential_urls_to_remove,
                    media_replacement_candidates=media_replacement_candidates,
                    normalized_media_replacement_refs=normalized_media_replacement_refs,
                    media_cleanup_plan=media_cleanup_plan,
                    font_replacement_candidates=font_replacement_candidates,
                    approved_icon_vocabulary=approved_icon_vocabulary,
                )
                paths["operator_prompt"].parent.mkdir(parents=True, exist_ok=True)
                paths["operator_prompt"].write_text(prompt, encoding="utf-8")
                write_stage_state(paths["operator_stage_state"], operator, attempt_number, paths)

                command = build_worker_command(prompt, paths["workspace"].resolve(), args.model, args.agent_timeout)
                write_json(
                    paths["operator_invocation"],
                    {
                        "created_at": utc_now(),
                        "command": command[:-1] + ["<prompt omitted; see operator_prompt.txt>"],
                        "model": args.model,
                        "timeout_seconds": args.agent_timeout,
                        "operator_id": operator.id,
                        "stage_slug": operator.stage_slug,
                        "attempt_number": attempt_number,
                    },
                )

                def mark_running(payload: dict[str, Any]) -> None:
                    payload["status"] = "running"
                    payload["worker_invoked"] = True
                    payload["started_at"] = utc_now()
                    payload["updated_at"] = payload["started_at"]
                    payload["model"] = args.model
                    payload["timeout_seconds"] = args.agent_timeout

                update_json_file(paths["operator_stage_state"], mark_running)

                execution = run_stage_attempt(command, paths["workspace"].resolve(), paths, args.agent_timeout)
                result_text = execution.stdout_text if execution.stdout_text.strip() else execution.stderr_text
                parsed = parse_operator_stdout(result_text, execution.status)
                post_media_policy_report = write_media_policy_report(paths["workspace"].resolve(), paths["media_policy_report"])
                remaining_urls = post_media_policy_report.get("potential_urls_to_remove", [])
                if not isinstance(remaining_urls, list):
                    remaining_urls = []
                remaining_media_candidates = post_media_policy_report.get("actionable_media_replacement_candidate_refs", [])
                if not isinstance(remaining_media_candidates, list):
                    remaining_media_candidates = []
                remaining_normalized_media_refs = post_media_policy_report.get("normalized_media_replacement_refs", [])
                if not isinstance(remaining_normalized_media_refs, list):
                    remaining_normalized_media_refs = []
                remaining_media_cleanup_plan = post_media_policy_report.get("media_cleanup_plan", [])
                if not isinstance(remaining_media_cleanup_plan, list):
                    remaining_media_cleanup_plan = []
                remaining_font_candidates = post_media_policy_report.get("actionable_font_replacement_candidate_refs", [])
                if not isinstance(remaining_font_candidates, list):
                    remaining_font_candidates = []
                remaining_icon_candidates = post_media_policy_report.get("actionable_icon_font_candidate_count", 0)
                if not isinstance(remaining_icon_candidates, int):
                    remaining_icon_candidates = 0
                operator_status = str(parsed["operator_status"]).lower()
                if execution.status != "completed" and operator_status == "completed":
                    operator_status = execution.status
                if operator_status not in {"completed", "failed", "timeout"}:
                    operator_status = execution.status

                if operator.id == "media_mapper" and (remaining_urls or remaining_media_candidates):
                    if attempt_number < registry.max_retries_per_stage:
                        operator_status = "failed"
                    else:
                        operator_status = "completed"

                result = {
                    "status": operator_status,
                    "execution_status": execution.status,
                    "returncode": execution.returncode,
                    "timed_out": execution.timed_out,
                    "run_id": run_state["run_id"],
                    "game_id": args.game_id,
                    "operator_id": operator.id,
                    "stage_number": operator.stage_number,
                    "stage_slug": operator.stage_slug,
                    "attempt_number": attempt_number,
                    "summary": parsed["summary"],
                    "changed_files": parsed["changed_files"],
                    "checks": {
                        "mechanics": parsed["mechanics_check"],
                        "visual": parsed["visual_check"],
                        "audio": parsed["audio_check"],
                        "mobile": parsed["mobile_check"],
                    },
                    "stdout_contract_present": parsed["stdout_contract_present"],
                    "stdout_path": str(paths["operator_stdout"]),
                    "stderr_path": str(paths["operator_stderr"]),
                    "workspace_path": str(paths["workspace"]),
                    "started_at": execution.started_at,
                    "finished_at": execution.finished_at,
                    "duration_seconds": execution.duration_seconds,
                    "generated_at": utc_now(),
                    "remaining_potential_urls_to_remove": remaining_urls,
                    "remaining_actionable_media_replacement_candidates": remaining_media_candidates,
                    "remaining_normalized_media_replacement_refs": remaining_normalized_media_refs,
                    "remaining_media_cleanup_plan": remaining_media_cleanup_plan,
                    "remaining_actionable_font_replacement_candidates": remaining_font_candidates,
                    "remaining_actionable_icon_font_candidate_count": remaining_icon_candidates,
                    "media_policy_warning": (
                        "Disallowed URLs or actionable media candidates remain after final media-mapper attempt."
                        if operator.id == "media_mapper" and (remaining_urls or remaining_media_candidates) and attempt_number >= registry.max_retries_per_stage
                        else None
                    ),
                }
                write_json(paths["operator_result"], result)

                def mark_finished(payload: dict[str, Any]) -> None:
                    payload["status"] = operator_status
                    payload["updated_at"] = utc_now()
                    payload["finished_at"] = payload["updated_at"]
                    payload["operator_result_path"] = str(paths["operator_result"])
                    payload["returncode"] = execution.returncode
                    payload["timed_out"] = execution.timed_out

                update_json_file(paths["operator_stage_state"], mark_finished)

                artifacts.extend(
                    [
                        str(paths["operator_prompt"]),
                        str(paths["operator_invocation"]),
                        str(paths["operator_stage_state"]),
                        str(paths["operator_stdout"]),
                        str(paths["operator_stderr"]),
                        str(paths["operator_result"]),
                        str(paths["media_policy_report"]),
                    ]
                )

                last_status = operator_status
                if operator_status == "completed":
                    copy_workspace(paths["workspace"], current_workspace, replace=True)
                    completed_stage_slugs.append(operator.stage_slug)
                    stage_completed = True
                    break

            if not stage_completed:
                raise OperatorPipelineGameError(f"{operator.stage_slug} failed after retries; last_status={last_status}")

        copy_workspace(current_workspace, output_dir, replace=True)

        game_state = load_json(game_state_path)
        game_state["status"] = "completed"
        game_state["current_phase"] = "creative_refactor_completed"
        game_state["creative_phase"] = "creative_refactor_completed"
        game_state["creative_status"] = "completed"
        game_state["creative_output_path"] = str(output_dir)
        game_state["operator_pipeline_completed_stages"] = completed_stage_slugs
        game_state["attempt_count"] = 1
        game_state["last_error"] = None
        game_state["updated_at"] = utc_now()
        game_state["operator_pipeline_artifacts"] = artifacts
        write_json(game_state_path, game_state)
    except Exception as exc:
        mark_game_failed(game_state_path, str(exc))
        raise


if __name__ == "__main__":
    main()