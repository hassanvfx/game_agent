#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.creative_refactor_runtime import execute_worker_command, load_json, update_json_file, utc_now, write_json
from scripts.media_policy import write_media_policy_report
from scripts.operator_registry_v2 import OperatorDefinition, OperatorRegistry, load_registry, resolve_through


ROOT = Path(__file__).resolve().parents[1]
REMIX_V5_TEMPLATE_ROOT = ROOT / "fixtures" / "remix_v5_contract_templates"


class OperatorPipelineGameError(RuntimeError):
    pass


@dataclass(frozen=True)
class PipelineNodeDefinition:
    id: str
    sequence_number: int
    prompt: Path
    accepted_upstream_statuses: tuple[str, ...]
    requires_contract: bool

    @property
    def stage_number(self) -> int:
        return self.sequence_number

    @property
    def stage_slug(self) -> str:
        return f"node_{self.sequence_number:02d}_{self.id}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run operator pipeline v2 for one production game.")
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--game-id", required=True)
    parser.add_argument("--model", default="gpt-5.5")
    parser.add_argument("--agent-timeout", type=int, default=3600)
    parser.add_argument("--remix-prompt")
    parser.add_argument("--remix-prompt-source")
    parser.add_argument("--through", default="final_code_ui_mobile_repair")
    parser.add_argument("--registry-config", default=str(ROOT / "configs" / "operator_pipeline_v2.json"))
    parser.add_argument("--playwright-port", type=int)
    parser.add_argument("--skip-run-state-update", action="store_true")
    parser.add_argument(
        "--dry-run-operators",
        action="store_true",
        help="Simulate successful operator stage execution without invoking cline.",
    )
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


def artifacts_post_step_clean(workspace: Path) -> dict[str, list[str]]:
    """Delete explicit `_trash` lifecycle surfaces before promoting a successful stage workspace.

    Deletion contract:
    - files matching `*_trash.*`
    - directories matching `*_trash`
    """
    removed_files: list[str] = []
    removed_dirs: list[str] = []

    for candidate in sorted(workspace.rglob("*_trash.*")):
        if not candidate.is_file():
            continue
        candidate.unlink(missing_ok=True)
        removed_files.append(str(candidate.relative_to(workspace)))

    for candidate in sorted(workspace.rglob("*_trash"), reverse=True):
        if not candidate.is_dir():
            continue
        shutil.rmtree(candidate)
        removed_dirs.append(str(candidate.relative_to(workspace)))

    return {
        "removed_trash_files": removed_files,
        "removed_trash_dirs": removed_dirs,
    }


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
        "operator_result_contract": attempt_root / "workspace" / "operator_result_contract.json",
        "operator_invocation": attempt_root / "operator_invocation.json",
        "operator_usage": attempt_root / "operator_usage.json",
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

    optional_catalog_dir_names = ("skills",)
    for catalog_dir_name in optional_catalog_dir_names:
        source_catalog_subdir = source_catalog_dir / catalog_dir_name
        if not source_catalog_subdir.exists():
            continue
        if not source_catalog_subdir.is_dir():
            raise OperatorPipelineGameError(f"Optional catalog path is not a directory: {source_catalog_subdir}")

        destination_catalog_subdir = destination_catalog_dir / catalog_dir_name
        if destination_catalog_subdir.exists():
            shutil.rmtree(destination_catalog_subdir)
        shutil.copytree(
            source_catalog_subdir,
            destination_catalog_subdir,
            symlinks=True,
            ignore=shutil.ignore_patterns("__pycache__", ".DS_Store"),
        )
        copied_catalogs[f"{catalog_dir_name}/"] = destination_catalog_subdir.resolve()

    return copied_catalogs


def stringify_catalog_paths(workspace_catalogs: dict[str, Path]) -> dict[str, str]:
    return {catalog_name: str(catalog_path) for catalog_name, catalog_path in sorted(workspace_catalogs.items())}


def bullet_list(values: list[str] | None) -> str:
    if not values:
        return "- NONE"
    return "\n".join(f"- {value}" for value in values)


def load_remix_v5_template_manifest() -> dict[str, Any]:
    manifest_path = REMIX_V5_TEMPLATE_ROOT / "manifest.json"
    payload = load_json(manifest_path)
    if not isinstance(payload, dict):
        raise OperatorPipelineGameError(f"Invalid Remix v5 template manifest: {manifest_path}")
    return payload


def copy_remix_v5_contract_templates_into_workspace(workspace: Path, operator_id: str) -> dict[str, Any] | None:
    if operator_id != "remix_v5_super_operator":
        return None

    manifest = load_remix_v5_template_manifest()
    seeded_dir = REMIX_V5_TEMPLATE_ROOT / "seeded"
    if not seeded_dir.exists() or not seeded_dir.is_dir():
        raise OperatorPipelineGameError(f"Missing Remix v5 seeded template directory: {seeded_dir}")

    for relative_name in manifest.get("seeded_artifacts", []):
        source_path = seeded_dir / relative_name
        destination_path = workspace / relative_name
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, destination_path)

    for relative_name in manifest.get("support_files", []):
        source_path = seeded_dir / relative_name
        destination_path = workspace / relative_name
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, destination_path)

    manifest_copy_path = workspace / "remix_v5_contract_manifest.json"
    shutil.copy2(REMIX_V5_TEMPLATE_ROOT / "manifest.json", manifest_copy_path)
    return manifest


def build_remix_v5_template_contract_section(template_manifest: dict[str, Any] | None) -> list[str]:
    if not template_manifest:
        return []

    placeholder_token = str(template_manifest.get("placeholder_token") or "__FILL_ME__")
    seeded_artifacts = template_manifest.get("seeded_artifacts") or []
    support_files = template_manifest.get("support_files") or []
    runtime_generated = template_manifest.get("runtime_generated_artifacts") or []
    return [
        "## Remix v5 Seeded Contract Templates",
        "",
        "The attempt workspace already contains seeded starter files for the v5 contract.",
        "Fill these files in place rather than inventing alternate structure or filenames.",
        "",
        f"Replace every literal placeholder token: `{placeholder_token}`",
        "Do not create parallel variants when one of these files already exists.",
        "",
        "Seeded artifact files:",
        bullet_list(seeded_artifacts),
        "",
        "Seeded support files:",
        bullet_list(support_files),
        "",
        "Runtime-generated evidence files that must be created fresh:",
        bullet_list(runtime_generated),
        "",
        "`operator_result_contract.json` must end valid for ingestion by using:",
        "- `status`: one of `ok`, `warning`, `error`",
        "- `detail`: a short non-empty summary string",
        "Additional rich fields are allowed, but do not omit those two ingestion fields.",
        "",
    ]


def inspect_template_placeholders(workspace: Path, template_manifest: dict[str, Any] | None) -> dict[str, Any]:
    if not template_manifest:
        return {"checked": False, "placeholder_token": None, "unresolved_files": []}

    placeholder_token = str(template_manifest.get("placeholder_token") or "__FILL_ME__")
    unresolved_files: list[str] = []
    for relative_name in list(template_manifest.get("seeded_artifacts", [])) + list(template_manifest.get("support_files", [])):
        path = workspace / relative_name
        if not path.exists() or not path.is_file():
            unresolved_files.append(relative_name)
            continue
        text = path.read_text(encoding="utf-8")
        if placeholder_token in text:
            unresolved_files.append(relative_name)
    return {
        "checked": True,
        "placeholder_token": placeholder_token,
        "unresolved_files": unresolved_files,
    }


def inspect_runtime_evidence(workspace: Path) -> dict[str, Any]:
    evidence_path = workspace / "runtime_evidence.json"
    if not evidence_path.exists() or not evidence_path.is_file():
        return {
            "present": False,
            "valid": False,
            "path": str(evidence_path),
            "payload": None,
            "checks": {},
            "screenshots": [],
        }

    try:
        payload = json.loads(evidence_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {
            "present": True,
            "valid": False,
            "path": str(evidence_path),
            "payload": None,
            "checks": {},
            "screenshots": [],
        }

    if not isinstance(payload, dict):
        return {
            "present": True,
            "valid": False,
            "path": str(evidence_path),
            "payload": None,
            "checks": {},
            "screenshots": [],
        }

    checks = payload.get("checks") if isinstance(payload.get("checks"), dict) else {}
    screenshots = payload.get("screenshots") if isinstance(payload.get("screenshots"), list) else []
    return {
        "present": True,
        "valid": True,
        "path": str(evidence_path),
        "payload": payload,
        "checks": checks,
        "screenshots": [item for item in screenshots if isinstance(item, str) and item],
    }


def evaluate_soft_acceptance_candidate(
    workspace: Path,
    template_manifest: dict[str, Any] | None,
    placeholder_inspection: dict[str, Any],
    contract_inspection: dict[str, Any],
    result: dict[str, Any],
    *,
    final_stage: bool,
    final_attempt: bool,
) -> dict[str, Any]:
    runtime_evidence = inspect_runtime_evidence(workspace)
    warnings: list[str] = []
    blockers: list[str] = []

    if not final_stage:
        blockers.append("soft_acceptance_only_applies_to_terminal_stage_outputs")
    if not final_attempt:
        blockers.append("soft_acceptance_is_only_evaluated_after_the_final_attempt")

    index_path = workspace / "index.html"
    assets_path = workspace / "assets"
    if not index_path.exists() or not index_path.is_file():
        blockers.append("workspace_missing_index_html")
    if not assets_path.exists() or not assets_path.is_dir():
        blockers.append("workspace_missing_assets_directory")

    if not runtime_evidence["present"] or not runtime_evidence["valid"]:
        blockers.append("runtime_evidence_missing_or_invalid")

    required_checks = (
        "boot_load",
        "spawn_flow",
        "merge_flow",
        "mobile_viewport",
        "controls_reachable",
    )
    failed_checks = [
        check_name
        for check_name in required_checks
        if runtime_evidence["checks"].get(check_name) is not True
    ]
    if failed_checks:
        blockers.append("runtime_checks_failed:" + ",".join(failed_checks))

    screenshot_names = runtime_evidence["screenshots"]
    realized_screenshots = [name for name in screenshot_names if (workspace / name).exists()]
    if not realized_screenshots:
        blockers.append("runtime_screenshots_missing")

    unresolved_files = [
        name for name in (placeholder_inspection.get("unresolved_files") or []) if isinstance(name, str) and name
    ]
    allowed_unresolved_files = {"operator_result_contract.json"}
    disallowed_unresolved_files = [name for name in unresolved_files if name not in allowed_unresolved_files]
    if disallowed_unresolved_files:
        blockers.append("unexpected_unresolved_template_files:" + ",".join(disallowed_unresolved_files))

    procedural_issue_present = (
        not bool(contract_inspection.get("valid"))
        or bool(unresolved_files)
        or result.get("execution_status") != "completed"
        or int(result.get("returncode") or 0) != 0
    )
    if not procedural_issue_present:
        blockers.append("no_procedural_issue_requiring_soft_acceptance")

    if bool(result.get("timed_out")):
        blockers.append("execution_timed_out")

    if not bool(contract_inspection.get("valid")):
        warnings.append("operator_result_contract_invalid_or_missing")
    if unresolved_files:
        warnings.append("template_artifacts_left_unresolved:" + ",".join(unresolved_files))
    if result.get("execution_status") != "completed":
        warnings.append(f"execution_status={result.get('execution_status')}")
    if int(result.get("returncode") or 0) != 0:
        warnings.append(f"returncode={result.get('returncode')}")
    console_error_count = runtime_evidence["checks"].get("console_errors")
    if isinstance(console_error_count, int) and console_error_count > 0:
        warnings.append(f"console_errors={console_error_count}")

    remaining_urls = result.get("remaining_potential_urls_to_remove")
    if isinstance(remaining_urls, list) and remaining_urls:
        warnings.append(f"remaining_url_findings={len(remaining_urls)}")
    remaining_font_candidates = result.get("remaining_actionable_font_replacement_candidates")
    if isinstance(remaining_font_candidates, list) and remaining_font_candidates:
        warnings.append(f"remaining_font_findings={len(remaining_font_candidates)}")

    eligible = not blockers
    reason = None
    if eligible:
        reason = (
            "Playable runtime evidence and screenshots are present, but final contract/cleanup artifacts remain incomplete."
        )

    return {
        "eligible": eligible,
        "reason": reason,
        "warnings": warnings,
        "blockers": blockers,
        "basis": {
            "workspace_index_path": str(index_path),
            "workspace_assets_path": str(assets_path),
            "runtime_evidence_path": runtime_evidence["path"],
            "required_checks": list(required_checks),
            "failed_checks": failed_checks,
            "screenshots": realized_screenshots,
            "contract_valid": bool(contract_inspection.get("valid")),
            "template_unresolved_files": unresolved_files,
            "allowed_unresolved_files": sorted(allowed_unresolved_files),
        },
    }


def build_skill_catalog_policy_section(workspace_catalogs: dict[str, Path]) -> list[str]:
    skill_catalog_path = workspace_catalogs.get("skills/")
    section = [
        "## Skill Catalog Policy",
        "",
    ]
    if skill_catalog_path is None:
        section.extend(
            [
                "- status: not_available",
                "- path: NONE",
                "",
                "No `catalogs/skills/` directory was copied into this attempt workspace.",
                "If this stage expects skill catalogs, treat their absence as a setup issue rather than inventing unavailable catalog entries.",
            ]
        )
    else:
        section.extend(
            [
                "- status: available",
                f"- path: {skill_catalog_path}",
                "- workspace_relative_path: catalogs/skills/",
                "",
                "`catalogs/skills/` contains read-only operator skill catalogs.",
                "Use skill catalogs as capability references when the current stage or workflow asks for catalog-backed skills.",
                "For `creative_remix_v5`, these catalogs are intended to be authoritative execution rails once the v5 super-operator is introduced.",
            ]
        )

    section.extend(
        [
            "",
            "Mandatory rules:",
            "- Do not edit files under `catalogs/`.",
            "- Treat `catalogs/` as runtime/reference input, not authored game output.",
            "- When a catalog skill requires artifacts, write those artifacts outside `catalogs/` in the attempt workspace.",
        ]
    )
    return section


def build_retry_context_text(attempt_number: int) -> str:
    return "No previous attempts for this node." if attempt_number == 1 else (
        "Use prior attempt stdout/stderr/operator_result artifacts from this node as retry context."
    )


def build_operator_stdout_contract_section() -> str:
    return """## Required Stdout Contract

End your response with exactly these lines, using one-line values:

```text
OPERATOR STATUS: completed|failed
CHANGED FILES: file1, file2 or NONE
SUMMARY: one short sentence
MECHANICS CHECK: preserved|issues
VISUAL CHECK: preserved|updated|issues
AUDIO CHECK: integrated|not_applicable|issues
MOBILE CHECK: safe|not_checked|issues
```"""


def build_operator_prompt_text(
    run_state: dict[str, Any],
    game_state: dict[str, Any],
    operator: OperatorDefinition,
    effective_remix_prompt: str | None,
    attempt_number: int,
    attempt_workspace: Path,
    previous_contract_status: str | None,
    previous_contract_detail: str | None,
    playwright_port: int | None,
    workspace_catalogs: dict[str, Path] | None = None,
    template_manifest: dict[str, Any] | None = None,
) -> str:
    operator_prompt = operator.prompt.read_text(encoding="utf-8")
    retry_context = build_retry_context_text(attempt_number)
    workspace_catalogs = workspace_catalogs or {}
    raw_user_prompt = effective_remix_prompt
    has_explicit_user_prompt = isinstance(raw_user_prompt, str) and bool(raw_user_prompt.strip())
    prompt_text = raw_user_prompt
    if not isinstance(prompt_text, str) or not prompt_text.strip():
        prompt_text = sanitize_display_name_for_prompt(
            game_state.get("display_name"),
            str(game_state["game_id"]),
            effective_remix_prompt,
        )

    prompt_template_value = raw_user_prompt.strip() if has_explicit_user_prompt else "neutral prompt"
    operator_prompt = operator_prompt.replace("#PROMPT#", prompt_template_value)

    user_prompt_section = []
    if has_explicit_user_prompt:
        user_prompt_section = [
            "## User Remix Prompt",
            "",
            "Use this as the primary user steering input for the current workflow stage:",
            "",
            "```text",
            prompt_template_value,
            "```",
            "",
        ]

    matcher_context_section: list[str] = []
    matcher_context = game_state.get("matcher_context")
    if isinstance(matcher_context, dict) and matcher_context:
        matcher_context_section = [
            "## Upstream Matcher Context",
            "",
            "This game was selected by the upstream matcher. Use this as additional steering context when it helps theme selection, mechanic interpretation, and remix framing.",
            "",
            "```json",
            json.dumps(matcher_context, indent=2, ensure_ascii=False),
            "```",
            "",
        ]

    runtime_validation_section = [
        "## Validation Runtime Contract",
        "",
    ]
    if playwright_port is None:
        runtime_validation_section.extend(
            [
                "- validation_host: NONE_ASSIGNED",
                "- validation_port: NONE_ASSIGNED",
                "- validation_root_url: NONE_ASSIGNED",
                "- validation_assignment_status: no_assigned_port",
            ]
        )
    else:
        runtime_validation_section.extend(
            [
                "- validation_host: 127.0.0.1",
                f"- validation_port: {playwright_port}",
                f"- validation_root_url: http://127.0.0.1:{playwright_port}/",
                "- validation_assignment_status: assigned_exclusive_port",
                "",
                "Required rules for any browser/runtime verification in this node:",
                "- Use only the assigned validation_host / validation_port / validation_root_url.",
                "- Do not choose another localhost port, even if you think it is free.",
                "- Do not attach to another existing local server.",
                "- If the assigned server cannot be started or validated reliably, treat that as a blocked runtime condition.",
                "- Write screenshots and browser-grounded evidence only inside the current attempt workspace.",
            ]
        )

    prompt_sections = [
        "## Workspace",
        "",
        "Edit only this working clone path:",
        "",
        "```text",
        str(attempt_workspace),
        "```",
        "",
        "Do not modify files outside the working clone path.",
        "",
        *runtime_validation_section,
        "",
        "## Stage Safety Harness",
        "",
        "These constraints are mandatory unless the current stage explicitly states otherwise:",
        "- Preserve the core mechanics exactly as implemented.",
        "- Do not change gameplay rules, scoring semantics, win/loss semantics, progression semantics, or input semantics.",
        "- Do not rewrite the main loop, collision model, physics model, or rendering architecture just to achieve theme or polish goals.",
        "- Do not make risky broad JS refactors, rendering rewrites, or logic migrations when a visual / perceptual / procedural change can achieve the goal.",
        "- Prefer cosmetic, perceptual, graphical, procedural, copy-level, and asset-mapping-level changes over logic changes.",
        "- If a change could compromise playability, control reliability, rendering stability, or mobile actionability, do not make that change in this stage.",
        "- When in doubt, leave mechanics and structural code alone and strengthen theme through character design, background identity, props, UI styling, wording, and lightweight procedural graphics.",
        "",
        "## Runtime Context",
        "",
        f"- run_id: {run_state['run_id']}",
        f"- game_id: {game_state['game_id']}",
        f"- node_id: {operator.id}",
        f"- node_number: {operator.stage_number}",
        f"- attempt_number: {attempt_number}",
        "",
        *user_prompt_section,
        *matcher_context_section,
        *build_remix_v5_template_contract_section(template_manifest),
        "## Catalog Media Policy",
        "",
        "Use only approved remote media URLs from these catalog files:",
        "- catalogs/audios.json -> approved remote audio sources",
        "- catalogs/gifs.json -> approved remote GIF / animated media sources",
        "- catalogs/sprites.json -> approved remote image / sprite / background sources",
        "- catalogs/fonts.json -> approved remote font sources",
        "",
        "Mandatory rules:",
        "- Do not use media files from assets/",
        "- From assets/, only CSS and JS files may be used",
        "- For media replacement or new media selection, prefer remote URLs represented in the catalog files",
        "",
        *build_skill_catalog_policy_section(workspace_catalogs),
        "",
        "",
        f"- status: {previous_contract_status or 'NONE'}",
        f"- detail: {previous_contract_detail or 'NONE'}",
        "",
        "## Retry Context",
        "",
        retry_context,
        "",
        build_operator_stdout_contract_section(),
        "",
        "---",
        "",
        operator_prompt,
        "",
    ]
    return "\n".join(prompt_sections)


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
        "--json",
        "-v",
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


def write_operator_usage_artifact(
    path: Path,
    execution: Any,
    *,
    simulated: bool,
    operator: OperatorDefinition,
    game_id: str,
    workspace_catalogs: dict[str, Path] | None = None,
) -> None:
    payload: dict[str, Any] = {
        "generated_at": utc_now(),
        "game_id": game_id,
        "operator_id": operator.id,
        "stage_slug": operator.stage_slug,
        "simulated": simulated,
        "workspace_catalogs": stringify_catalog_paths(workspace_catalogs or {}),
    }

    if simulated:
        payload.update(
            {
                "status": "usage_unavailable",
                "reason": "dry_run_no_cline_invocation",
                "usage_summary": None,
            }
        )
    elif getattr(execution, "usage_summary", None) is None:
        payload.update(
            {
                "status": "usage_unavailable",
                "reason": "no_run_result_event_found",
                "usage_summary": None,
            }
        )
    else:
        payload.update(
            {
                "status": "captured",
                "reason": None,
                "usage_summary": execution.usage_summary,
            }
        )

    write_json(path, payload)


def build_game_cost_report(run_id: str, game_id: str, usage_paths: list[Path]) -> dict[str, Any]:
    steps: list[dict[str, Any]] = []
    totals = {
        "inputTokens": 0,
        "outputTokens": 0,
        "cacheReadTokens": 0,
        "cacheWriteTokens": 0,
        "totalCost": 0,
    }
    token_totals = {
        "totalTokens": 0,
        "totalTokensIncludingCache": 0,
    }
    projected_cost_total = 0.0
    completed_count = 0
    missing_usage_count = 0

    for usage_path in usage_paths:
        payload = load_json(usage_path)
        usage_summary = payload.get("usage_summary")
        if isinstance(usage_summary, dict) and isinstance(usage_summary.get("usage"), dict):
            usage = usage_summary["usage"]
            completed_count += 1
            for key in totals:
                value = usage.get(key, 0)
                if isinstance(value, (int, float)):
                    totals[key] += value
            token_totals_payload = usage_summary.get("tokenTotals") if isinstance(usage_summary.get("tokenTotals"), dict) else {}
            for key in token_totals:
                value = token_totals_payload.get(key, 0)
                if isinstance(value, (int, float)):
                    token_totals[key] += value
            projected_cost_payload = usage_summary.get("projectedCost") if isinstance(usage_summary.get("projectedCost"), dict) else {}
            projected_total = projected_cost_payload.get("total", 0)
            if isinstance(projected_total, (int, float)):
                projected_cost_total += projected_total
        else:
            missing_usage_count += 1

        steps.append(
            {
                "artifact_path": str(usage_path),
                "operator_id": payload.get("operator_id"),
                "stage_slug": payload.get("stage_slug"),
                "status": payload.get("status"),
                "reason": payload.get("reason"),
                "simulated": payload.get("simulated", False),
                "usage_summary": usage_summary,
            }
        )

    return {
        "generated_at": utc_now(),
        "run_id": run_id,
        "game_id": game_id,
        "summary": {
            "invocation_count": len(usage_paths),
            "completed_count": completed_count,
            "missing_usage_count": missing_usage_count,
            **totals,
            **token_totals,
            "projectedCostUsd": round(projected_cost_total, 6),
        },
        "steps": steps,
    }


def write_stage_state(
    path: Path,
    operator: OperatorDefinition,
    attempt_number: int,
    paths: dict[str, Path],
    playwright_port: int | None,
    workspace_catalogs: dict[str, Path] | None = None,
) -> None:
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
            "operator_result_contract_path": str(paths["operator_result_contract"]),
            "operator_invocation_path": str(paths["operator_invocation"]),
            "operator_usage_path": str(paths["operator_usage"]),
            "media_policy_report_path": str(paths["media_policy_report"]),
            "workspace_catalogs": stringify_catalog_paths(workspace_catalogs or {}),
            "worker_invoked": False,
            "playwright_port": playwright_port,
            "validation_root_url": f"http://127.0.0.1:{playwright_port}/" if playwright_port is not None else None,
        },
    )


def mark_game_failed(game_state_path: Path, message: str) -> None:
    game_state = load_json(game_state_path)
    game_state["status"] = "failed"
    game_state["current_phase"] = "operator_pipeline_failed"
    game_state["creative_phase"] = "operator_pipeline_failed"
    game_state["creative_status"] = "failed"
    game_state["soft_acceptance"] = None
    game_state["soft_acceptance_reason"] = None
    game_state["soft_acceptance_warning_count"] = 0
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


def run_stage_attempt_dry_run(
    operator: OperatorDefinition,
    workspace: Path,
    paths: dict[str, Path],
) -> dict[str, Any]:
    now = utc_now()
    stdout_text = "\n".join(
        [
            "DRY RUN: operator execution simulated; cline was not invoked.",
            "OPERATOR STATUS: completed",
            "CHANGED FILES: NONE",
            f"SUMMARY: dry-run stage simulation completed for {operator.id}",
            "MECHANICS CHECK: preserved",
            "VISUAL CHECK: preserved",
            "AUDIO CHECK: not_applicable",
            "MOBILE CHECK: safe",
            "",
        ]
    )
    stderr_text = "DRY RUN: no stderr; operator execution was simulated.\n"
    paths["operator_stdout"].write_text(stdout_text, encoding="utf-8")
    paths["operator_stderr"].write_text(stderr_text, encoding="utf-8")
    write_json(
        paths["operator_result_contract"],
        {
            "status": "ok",
            "detail": f"Dry-run contract synthesized for {operator.id}.",
        },
    )
    return {
        "status": "completed",
        "returncode": 0,
        "timed_out": False,
        "started_at": now,
        "finished_at": now,
        "duration_seconds": 0.0,
        "stdout_text": stdout_text,
        "stderr_text": stderr_text,
    }


def normalize_media_mapper_post_run_status(
    operator: OperatorDefinition,
    attempt_number: int,
    max_retries_per_stage: int,
    operator_status: str,
    remaining_urls: list[Any],
    remaining_media_candidates: list[Any],
) -> tuple[str, str | None]:
    if operator.id != "media_mapper":
        return operator_status, None

    if not (remaining_urls or remaining_media_candidates):
        return operator_status, None

    if attempt_number < max_retries_per_stage:
        return operator_status, None

    return (
        "completed",
        "Disallowed URLs or actionable media candidates remain after final media-mapper attempt.",
    )


def _require_manifest_dict(payload: Any, context: str) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise OperatorPipelineGameError(f"{context} must be an object")
    return payload


def _require_manifest_nonempty_string(payload: dict[str, Any], key: str, context: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise OperatorPipelineGameError(f"{context} field '{key}' must be a non-empty string")
    return value.strip()


def _read_manifest_nodes(run_dir: Path) -> tuple[PipelineNodeDefinition, ...] | None:
    manifest_path = run_dir / "input_manifest.json"
    manifest = load_json(manifest_path)
    if manifest.get("manifest_version") != "2.0.0":
        return None

    raw_nodes = manifest.get("nodes")
    if not isinstance(raw_nodes, list) or not raw_nodes:
        raise OperatorPipelineGameError("Generic manifest v2 requires a non-empty 'nodes' array")

    allowed_statuses = {"ok", "warning", "error"}
    nodes: list[PipelineNodeDefinition] = []
    seen_ids: set[str] = set()

    for index, raw_node in enumerate(raw_nodes, start=1):
        node_payload = _require_manifest_dict(raw_node, f"nodes[{index}]")
        node_id = _require_manifest_nonempty_string(node_payload, "id", f"nodes[{index}]")
        if node_id in seen_ids:
            raise OperatorPipelineGameError(f"Duplicate node id in generic manifest: {node_id}")
        seen_ids.add(node_id)

        prompt_file = _require_manifest_nonempty_string(node_payload, "prompt_file", f"nodes[{index}]")
        prompt_path = (ROOT / prompt_file).resolve()
        if not prompt_path.exists() or not prompt_path.is_file():
            raise OperatorPipelineGameError(f"Node '{node_id}' prompt_file does not exist: {prompt_path}")

        raw_statuses = node_payload.get("accepted_upstream_statuses", ["ok", "warning", "error"])
        if not isinstance(raw_statuses, list) or not raw_statuses:
            raise OperatorPipelineGameError(
                f"Node '{node_id}' field 'accepted_upstream_statuses' must be a non-empty array"
            )
        accepted_statuses: list[str] = []
        for raw_status in raw_statuses:
            if not isinstance(raw_status, str) or raw_status not in allowed_statuses:
                raise OperatorPipelineGameError(
                    f"Node '{node_id}' field 'accepted_upstream_statuses' must contain only {sorted(allowed_statuses)}"
                )
            accepted_statuses.append(raw_status)

        requires_contract = node_payload.get("requires_contract", False)
        if not isinstance(requires_contract, bool):
            raise OperatorPipelineGameError(f"Node '{node_id}' field 'requires_contract' must be boolean")

        nodes.append(
            PipelineNodeDefinition(
                id=node_id,
                sequence_number=index,
                prompt=prompt_path,
                accepted_upstream_statuses=tuple(accepted_statuses),
                requires_contract=requires_contract,
            )
        )

    return tuple(nodes)


def inspect_operator_result_contract(path: Path) -> dict[str, Any]:
    if not path.exists() or not path.is_file():
        return {
            "present": False,
            "valid": False,
            "payload": None,
        }

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {
            "present": True,
            "valid": False,
            "payload": None,
        }

    if not isinstance(payload, dict):
        return {
            "present": True,
            "valid": False,
            "payload": None,
        }

    status = payload.get("status")
    detail = payload.get("detail")
    if status not in {"ok", "warning", "error"}:
        return {
            "present": True,
            "valid": False,
            "payload": None,
        }
    if not isinstance(detail, str) or not detail.strip():
        return {
            "present": True,
            "valid": False,
            "payload": None,
        }

    payload["status"] = status
    payload["detail"] = detail.strip()
    return {
        "present": True,
        "valid": True,
        "payload": payload,
    }


def main() -> None:
    args = parse_args()
    run_dir = Path(args.run_dir).resolve()
    game_dir = run_dir / "games" / args.game_id
    game_state_path = game_dir / "game_state.json"
    run_state_path = run_dir / "run_state.json"

    run_state = load_json(run_state_path)
    game_state = load_json(game_state_path)
    manifest_nodes = _read_manifest_nodes(run_dir)
    registry: OperatorRegistry | None = None
    if manifest_nodes is None:
        registry = load_registry(Path(args.registry_config))
        operators: tuple[OperatorDefinition | PipelineNodeDefinition, ...] = resolve_through(registry, args.through)
        max_retries_per_stage = registry.max_retries_per_stage
        pipeline_mode = "legacy_registry"
    else:
        operators = manifest_nodes
        max_retries_per_stage = 1
        pipeline_mode = "generic_manifest_v2"

    if game_state.get("integrity_status") != "passed":
        raise OperatorPipelineGameError(f"Game {args.game_id} is not integrity-passed and cannot be transformed.")

    input_dir = Path(game_state["input_mirror_path"]).resolve()
    output_dir = Path(game_state["output_path"]).resolve()
    pipeline_dir = game_dir / "operator_pipeline"
    current_workspace = pipeline_dir / "current"
    run_state.setdefault("operator_pipeline_v2", {})
    run_state["operator_pipeline_v2"]["enabled"] = True
    run_state["operator_pipeline_v2"]["max_retries_per_stage"] = max_retries_per_stage
    run_state["operator_pipeline_v2"]["pipeline_mode"] = pipeline_mode
    run_state["operator_pipeline_v2"]["assigned_playwright_port"] = args.playwright_port
    run_state["operator_pipeline_v2"]["validation_root_url"] = (
        f"http://127.0.0.1:{args.playwright_port}/" if args.playwright_port is not None else None
    )
    run_state["operator_pipeline_v2"]["updated_at"] = utc_now()
    write_json(run_state_path, run_state)

    copy_workspace(input_dir, current_workspace, replace=True)

    game_state["status"] = "running"
    game_state["current_phase"] = "operator_pipeline_running"
    game_state["creative_phase"] = "operator_pipeline_running"
    game_state["creative_status"] = "running"
    game_state["remix_prompt"] = args.remix_prompt
    game_state["effective_remix_prompt_source"] = args.remix_prompt_source
    game_state["operator_pipeline_path"] = str(pipeline_dir)
    game_state["creative_output_path"] = str(output_dir)
    game_state["assigned_playwright_port"] = args.playwright_port
    game_state["validation_root_url"] = f"http://127.0.0.1:{args.playwright_port}/" if args.playwright_port is not None else None
    game_state["updated_at"] = utc_now()
    write_json(game_state_path, game_state)

    completed_stage_slugs: list[str] = []
    artifacts: list[str] = []
    usage_artifacts: list[Path] = []
    previous_contract_status: str | None = None
    soft_acceptance_summary: dict[str, Any] | None = None
    final_stage_slug = operators[-1].stage_slug if operators else None

    try:
        for operator in operators:
            stage_completed = False
            last_status = "not_started"

            if previous_contract_status is not None and previous_contract_status not in operator.accepted_upstream_statuses:
                raise OperatorPipelineGameError(
                    f"{operator.stage_slug} blocked by upstream contract status "
                    f"'{previous_contract_status}' not in accepted statuses {list(operator.accepted_upstream_statuses)}"
                )

            for attempt_number in range(1, max_retries_per_stage + 1):
                paths = attempt_paths(game_dir, operator, attempt_number)
                copy_workspace(current_workspace, paths["workspace"], replace=False)
                template_manifest = copy_remix_v5_contract_templates_into_workspace(paths["workspace"].resolve(), operator.id)
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
                    effective_remix_prompt=args.remix_prompt,
                    attempt_number=attempt_number,
                    attempt_workspace=paths["workspace"].resolve(),
                    previous_contract_status=previous_contract_status,
                    previous_contract_detail=None,
                    playwright_port=args.playwright_port,
                    workspace_catalogs=workspace_catalogs,
                    template_manifest=template_manifest,
                )
                paths["operator_prompt"].parent.mkdir(parents=True, exist_ok=True)
                paths["operator_prompt"].write_text(prompt, encoding="utf-8")
                write_stage_state(
                    paths["operator_stage_state"],
                    operator,
                    attempt_number,
                    paths,
                    args.playwright_port,
                    workspace_catalogs,
                )

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
                        "playwright_port": args.playwright_port,
                        "validation_root_url": (
                            f"http://127.0.0.1:{args.playwright_port}/" if args.playwright_port is not None else None
                        ),
                        "workspace_catalogs": stringify_catalog_paths(workspace_catalogs),
                    },
                )

                def mark_running(payload: dict[str, Any]) -> None:
                    payload["status"] = "running"
                    payload["worker_invoked"] = True
                    payload["started_at"] = utc_now()
                    payload["updated_at"] = payload["started_at"]
                    payload["model"] = args.model
                    payload["timeout_seconds"] = args.agent_timeout
                    payload["playwright_port"] = args.playwright_port
                    payload["validation_root_url"] = (
                        f"http://127.0.0.1:{args.playwright_port}/" if args.playwright_port is not None else None
                    )

                update_json_file(paths["operator_stage_state"], mark_running)

                if args.dry_run_operators:
                    execution = run_stage_attempt_dry_run(operator, paths["workspace"].resolve(), paths)
                    write_operator_usage_artifact(
                        paths["operator_usage"],
                        execution,
                        simulated=True,
                        operator=operator,
                        game_id=args.game_id,
                        workspace_catalogs=workspace_catalogs,
                    )
                    result_text = execution["stdout_text"] if execution["stdout_text"].strip() else execution["stderr_text"]
                    parsed = parse_operator_stdout(result_text, execution["status"])
                else:
                    execution = run_stage_attempt(command, paths["workspace"].resolve(), paths, args.agent_timeout)
                    write_operator_usage_artifact(
                        paths["operator_usage"],
                        execution,
                        simulated=False,
                        operator=operator,
                        game_id=args.game_id,
                        workspace_catalogs=workspace_catalogs,
                    )
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
                execution_status_value = execution["status"] if args.dry_run_operators else execution.status
                execution_returncode = execution["returncode"] if args.dry_run_operators else execution.returncode
                execution_timed_out = execution["timed_out"] if args.dry_run_operators else execution.timed_out
                execution_started_at = execution["started_at"] if args.dry_run_operators else execution.started_at
                execution_finished_at = execution["finished_at"] if args.dry_run_operators else execution.finished_at
                execution_duration_seconds = execution["duration_seconds"] if args.dry_run_operators else execution.duration_seconds
                if execution_status_value != "completed" and operator_status == "completed":
                    operator_status = execution_status_value
                if operator_status not in {"completed", "failed", "timeout"}:
                    operator_status = execution_status_value

                media_policy_warning: str | None = None
                if operator.id == "media_mapper" and (remaining_urls or remaining_media_candidates):
                    if attempt_number < max_retries_per_stage:
                        operator_status = "failed"
                    else:
                        operator_status, media_policy_warning = normalize_media_mapper_post_run_status(
                            operator=operator,
                            attempt_number=attempt_number,
                            max_retries_per_stage=max_retries_per_stage,
                            operator_status=operator_status,
                            remaining_urls=remaining_urls,
                            remaining_media_candidates=remaining_media_candidates,
                        )

                contract_inspection = inspect_operator_result_contract(paths["operator_result_contract"])
                operator_result_contract = contract_inspection["payload"]
                contract_present = bool(contract_inspection["present"])
                contract_valid = bool(contract_inspection["valid"])
                contract_status = operator_result_contract["status"] if operator_result_contract else None
                contract_detail = operator_result_contract["detail"] if operator_result_contract else None
                placeholder_inspection = inspect_template_placeholders(paths["workspace"].resolve(), template_manifest)

                result = {
                    "status": operator_status,
                    "execution_status": execution_status_value,
                    "returncode": execution_returncode,
                    "timed_out": execution_timed_out,
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
                    "contract_present": contract_present,
                    "contract_valid": contract_valid,
                    "contract_status": contract_status,
                    "contract_detail": contract_detail,
                    "operator_result_contract": operator_result_contract,
                    "operator_result_contract_path": str(paths["operator_result_contract"]),
                    "template_placeholders_checked": placeholder_inspection["checked"],
                    "template_placeholder_token": placeholder_inspection["placeholder_token"],
                    "template_unresolved_files": placeholder_inspection["unresolved_files"],
                    "stdout_path": str(paths["operator_stdout"]),
                    "stderr_path": str(paths["operator_stderr"]),
                    "workspace_path": str(paths["workspace"]),
                    "workspace_catalogs": stringify_catalog_paths(workspace_catalogs),
                    "playwright_port": args.playwright_port,
                    "validation_root_url": (
                        f"http://127.0.0.1:{args.playwright_port}/" if args.playwright_port is not None else None
                    ),
                    "started_at": execution_started_at,
                    "finished_at": execution_finished_at,
                    "duration_seconds": execution_duration_seconds,
                    "generated_at": utc_now(),
                    "remaining_potential_urls_to_remove": remaining_urls,
                    "remaining_actionable_media_replacement_candidates": remaining_media_candidates,
                    "remaining_normalized_media_replacement_refs": remaining_normalized_media_refs,
                    "remaining_media_cleanup_plan": remaining_media_cleanup_plan,
                    "remaining_actionable_font_replacement_candidates": remaining_font_candidates,
                    "remaining_actionable_icon_font_candidate_count": remaining_icon_candidates,
                    "media_policy_warning": media_policy_warning,
                    "simulated": args.dry_run_operators,
                    "mode": "dry_run" if args.dry_run_operators else "live",
                    "operator_usage_path": str(paths["operator_usage"]),
                    "usage_summary": None if args.dry_run_operators else execution.usage_summary,
                }
                soft_acceptance: dict[str, Any] | None = None
                if operator.stage_slug == final_stage_slug and attempt_number == max_retries_per_stage:
                    evaluated_soft_acceptance = evaluate_soft_acceptance_candidate(
                        paths["workspace"].resolve(),
                        template_manifest,
                        placeholder_inspection,
                        contract_inspection,
                        result,
                        final_stage=True,
                        final_attempt=True,
                    )
                    if evaluated_soft_acceptance["eligible"]:
                        soft_acceptance = evaluated_soft_acceptance
                        result["status"] = "soft_completed"
                        result["soft_accepted"] = True
                        result["soft_acceptance"] = evaluated_soft_acceptance
                        result["soft_acceptance_reason"] = evaluated_soft_acceptance["reason"]
                write_json(paths["operator_result"], result)

                stage_result_status = str(result["status"])

                def mark_finished(payload: dict[str, Any]) -> None:
                    payload["status"] = stage_result_status
                    payload["updated_at"] = utc_now()
                    payload["finished_at"] = payload["updated_at"]
                    payload["operator_result_path"] = str(paths["operator_result"])
                    payload["returncode"] = execution_returncode
                    payload["timed_out"] = execution_timed_out
                    if soft_acceptance is not None:
                        payload["soft_acceptance"] = soft_acceptance

                update_json_file(paths["operator_stage_state"], mark_finished)

                artifacts.extend(
                    [
                        str(paths["operator_prompt"]),
                        str(paths["operator_invocation"]),
                        str(paths["operator_stage_state"]),
                        str(paths["operator_stdout"]),
                        str(paths["operator_stderr"]),
                        str(paths["operator_result"]),
                        str(paths["operator_result_contract"]),
                        str(paths["operator_usage"]),
                        str(paths["media_policy_report"]),
                    ]
                )
                usage_artifacts.append(paths["operator_usage"])

                last_status = stage_result_status
                if stage_result_status == "completed":
                    if placeholder_inspection["checked"] and placeholder_inspection["unresolved_files"]:
                        last_status = "failed"
                        continue
                    if getattr(operator, "requires_contract", False) and not contract_valid:
                        last_status = "failed"
                        continue
                    previous_contract_status = contract_status
                    trash_cleanup = artifacts_post_step_clean(paths["workspace"].resolve())

                    def mark_post_step_cleanup(payload: dict[str, Any]) -> None:
                        payload["artifacts_post_step_clean"] = trash_cleanup
                        payload["updated_at"] = utc_now()

                    update_json_file(paths["operator_stage_state"], mark_post_step_cleanup)

                    def mark_post_step_cleanup_result(payload: dict[str, Any]) -> None:
                        payload["artifacts_post_step_clean"] = trash_cleanup

                    update_json_file(paths["operator_result"], mark_post_step_cleanup_result)
                    copy_workspace(paths["workspace"], current_workspace, replace=True)
                    completed_stage_slugs.append(operator.stage_slug)
                    stage_completed = True
                    break
                if stage_result_status == "soft_completed" and soft_acceptance is not None:
                    previous_contract_status = contract_status or "warning"
                    copy_workspace(paths["workspace"], current_workspace, replace=True)
                    completed_stage_slugs.append(operator.stage_slug)
                    soft_acceptance_summary = soft_acceptance
                    stage_completed = True
                    break

            if not stage_completed:
                raise OperatorPipelineGameError(f"{operator.stage_slug} failed after retries; last_status={last_status}")

        copy_workspace(current_workspace, output_dir, replace=True)

        game_state = load_json(game_state_path)
        completion_status = "soft_completed" if soft_acceptance_summary is not None else "completed"
        completion_phase = "creative_refactor_soft_completed" if soft_acceptance_summary is not None else "creative_refactor_completed"
        game_state["status"] = completion_status
        game_state["current_phase"] = completion_phase
        game_state["creative_phase"] = completion_phase
        game_state["creative_status"] = completion_status
        game_state["creative_output_path"] = str(output_dir)
        game_state["operator_pipeline_completed_stages"] = completed_stage_slugs
        game_state["attempt_count"] = 1
        game_state["last_error"] = None
        game_state["soft_acceptance"] = soft_acceptance_summary
        game_state["soft_acceptance_reason"] = (
            soft_acceptance_summary.get("reason") if isinstance(soft_acceptance_summary, dict) else None
        )
        game_state["soft_acceptance_warning_count"] = (
            len(soft_acceptance_summary.get("warnings") or []) if isinstance(soft_acceptance_summary, dict) else 0
        )
        game_state["updated_at"] = utc_now()
        game_state["operator_pipeline_artifacts"] = artifacts
        cost_report_path = pipeline_dir / "cost_report.json"
        write_json(cost_report_path, build_game_cost_report(run_state["run_id"], args.game_id, usage_artifacts))
        game_state["operator_pipeline_cost_report_path"] = str(cost_report_path)
        game_state["assigned_playwright_port"] = args.playwright_port
        game_state["validation_root_url"] = f"http://127.0.0.1:{args.playwright_port}/" if args.playwright_port is not None else None
        write_json(game_state_path, game_state)
    except Exception as exc:
        mark_game_failed(game_state_path, str(exc))
        raise


if __name__ == "__main__":
    main()