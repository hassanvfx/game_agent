#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.creative_refactor_runtime import execute_worker_command, update_json_file, write_json as runtime_write_json

ROOT = Path(__file__).resolve().parents[1]
DEBUG_TRACE_FILENAME = "spec_adaptor_debug_trace.log"
STYLES_ROOT = ROOT / "styles"
PROMPTS_ROOT = ROOT / "prompts"
DEFAULT_STYLE_ID = "neutral_prototype"
SPEC_ADAPTOR_JOB_STATE_FILENAME = "spec_adaptor_job_state.json"
SPEC_ADAPTOR_MAX_ATTEMPTS = 3
RECOMPOSITION_SUMMARY_REQUIRED_KEYS = (
    "status",
    "summary",
    "editable_files_reviewed",
    "files_modified",
    "notes",
)

EDITABLE_CREATIVE_FILE_ORDER = (
    "creative_remix_contract.md",
    "visual_identity_contract.md",
    "theme_policy.md",
    "creative_refactor_agent_template.md",
)

INVARIANT_REFERENCE_FILES = (
    "audio_policy.md",
    "network_policy.md",
    "system_contract.md",
    "refactor_compliance_spec.md",
)

FILE_LABELS = {
    "creative_remix_contract.md": "creative_remix_contract",
    "visual_identity_contract.md": "visual_identity_contract",
    "theme_policy.md": "theme_policy",
    "creative_refactor_agent_template.md": "creative_refactor_agent_template",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_usage_artifact(path: Path, execution: Any | None, *, simulated: bool = False, note: str | None = None) -> None:
    payload: dict[str, Any] = {
        "generated_at": utc_now(),
        "simulated": simulated,
    }
    if simulated:
        payload.update(
            {
                "status": "usage_unavailable",
                "reason": note or "dry_run_no_cline_invocation",
                "usage_summary": None,
            }
        )
    elif execution is None:
        payload.update(
            {
                "status": "usage_unavailable",
                "reason": note or "missing_execution",
                "usage_summary": None,
            }
        )
    elif execution.usage_summary is None:
        payload.update(
            {
                "status": "usage_unavailable",
                "reason": note or "no_run_result_event_found",
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


def append_debug_trace(trace_path: Path, message: str) -> None:
    trace_path.parent.mkdir(parents=True, exist_ok=True)
    with trace_path.open("a", encoding="utf-8") as handle:
        handle.write(f"[{utc_now()}] {message}\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a spec recomposition workspace and run a first-stage CLI agent to rewrite creative specs."
    )
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--style", default=DEFAULT_STYLE_ID)
    parser.add_argument("--remix-prompt", required=True)
    parser.add_argument(
        "--prompt-targets",
        help=(
            "Optional comma-separated list of editable creative spec targets to focus the recomposition step. "
            "Supported values: creative_remix_contract, visual_identity_contract, theme_policy, creative_refactor_agent_template."
        ),
    )
    parser.add_argument("--model", default="gpt-5.4")
    parser.add_argument("--agent-timeout", type=int, default=900)
    parser.add_argument(
        "--dry-run-spec-adaptor",
        action="store_true",
        help="Simulate spec-adaptor completion without invoking cline.",
    )
    return parser.parse_args()


def load_style_manifest(style_id: str) -> dict:
    manifest_path = STYLES_ROOT / style_id / "style_manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Style manifest not found for style '{style_id}': {manifest_path}")
    return load_json(manifest_path)


def parse_prompt_targets(raw_targets: str | None) -> list[str]:
    if not raw_targets:
        return []

    supported = set(FILE_LABELS.values())
    parsed = []
    for item in raw_targets.split(","):
        target = item.strip()
        if not target:
            continue
        if target not in supported:
            raise ValueError(
                f"Unsupported prompt target '{target}'. Supported targets: {', '.join(sorted(supported))}"
            )
        parsed.append(target)
    return parsed


def copy_editable_creative_bundle(style_manifest: dict, adapted_dir: Path) -> dict[str, str]:
    copied: dict[str, str] = {}

    for group in ("specs", "prompts"):
        for relative_path in style_manifest["style_local_files"].get(group, []):
            source = ROOT / relative_path
            destination = adapted_dir / Path(relative_path).name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            copied[destination.name] = str(destination)

    return copied


def copy_invariant_reference_files(references_dir: Path) -> dict[str, str]:
    copied: dict[str, str] = {}
    for filename in INVARIANT_REFERENCE_FILES:
        source = PROMPTS_ROOT / filename
        destination = references_dir / filename
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        copied[filename] = str(destination)
    return copied


def build_retry_guidance_section(
    attempt_number: int,
    max_attempts: int,
    previous_failure: dict[str, Any] | None,
) -> str:
    if attempt_number <= 1 or not previous_failure:
        return ""

    missing_files = previous_failure.get("missing_files") or []
    missing_keys = previous_failure.get("missing_required_keys") or []
    mismatches = previous_failure.get("mismatches") or []
    previous_stdout_summary = previous_failure.get("stdout_summary") or "NONE"
    previous_failure_reason = previous_failure.get("failure_reason") or "unknown_failure"

    lines = [
        "## Retry Correction Context",
        f"This is retry attempt {attempt_number} of {max_attempts}.",
        f"Previous attempt failed because: `{previous_failure_reason}`",
    ]
    if missing_files:
        lines.append("### Missing required files from previous attempt")
        lines.extend(f"- `{item}`" for item in missing_files)
    if missing_keys:
        lines.append("### Missing required JSON keys from previous attempt")
        lines.extend(f"- `{item}`" for item in missing_keys)
    if mismatches:
        lines.append("### Contract mismatches from previous attempt")
        lines.extend(f"- `{item}`" for item in mismatches)
    lines.extend(
        [
            "### Previous stdout summary",
            f"- `{previous_stdout_summary}`",
            "### Mandatory repair instructions for this retry",
            "- Create every missing required file listed above.",
            "- Ensure `recomposition_summary.json` exists on disk before finishing.",
            "- Ensure `recomposition_summary.json` is valid JSON.",
            "- Ensure all required keys are present in `recomposition_summary.json`.",
            "- Do not claim a file in `CHANGED FILES` unless it actually exists on disk when you finish.",
            "- Before finishing, re-check the filesystem state of all required output artifacts.",
        ]
    )
    return "\n".join(lines) + "\n\n"


def build_recomposition_harness(
    style_id: str,
    remix_prompt: str,
    explicit_targets: list[str],
    editable_files: dict[str, str],
    invariant_files: dict[str, str],
    attempt_number: int = 1,
    max_attempts: int = SPEC_ADAPTOR_MAX_ATTEMPTS,
    previous_failure: dict[str, Any] | None = None,
) -> str:
    target_line = ", ".join(explicit_targets) if explicit_targets else "all editable creative files"

    editable_lines = "\n".join(
        f"- {filename}: {path}"
        for filename, path in editable_files.items()
    )
    invariant_lines = "\n".join(
        f"- {filename}: {path}"
        for filename, path in invariant_files.items()
    )
    retry_guidance = build_retry_guidance_section(attempt_number, max_attempts, previous_failure)

    return f"""# Spec Recomposition Harness

You are performing the first-stage spec recomposition pass for Game Remixer.

## Goal
Rewrite the editable creative spec bundle so it reflects the runtime user remix prompt as strongly and coherently as possible while preserving all invariant safety, system, and compliance constraints.

## Selected style preset
`{style_id}`

## Runtime user remix prompt
`{remix_prompt}`

{retry_guidance}## Editable target scope
`{target_line}`

If explicit targets are provided, focus your strongest modifications on those target files, but keep the whole editable creative bundle coherent.

## Editable creative files
{editable_lines}

These files are editable in place:
- `creative_remix_contract.md` carries broad remix framing and gameplay-aware remix guidance
- `visual_identity_contract.md` carries branding / palette / visual identity guidance
- `theme_policy.md` carries theme / mood / atmosphere guidance
- `creative_refactor_agent_template.md` carries the worker-facing interpretation framing

## Fixed invariant reference files
{invariant_lines}

These files are NOT editable. They must be treated as hard constraints only:
- no network
- no audio
- system/compliance boundaries
- required artifact/evidence expectations

## Editing instructions
1. Read the runtime user remix prompt carefully.
2. Read every editable creative file completely before rewriting.
3. Read the invariant reference files completely before rewriting.
4. Rewrite the editable creative files in place so they become a coherent adapted bundle.
5. Keep gameplay-related creative guidance editable through `creative_remix_contract.md` when the prompt implies gameplay shifts.
6. Do not rewrite or contradict the invariant reference files.
7. Do not create new editable spec files in this first pass.
8. Prefer strong, culturally aware interpretation of symbolic references over literal keyword dependence.
9. Keep the resulting bundle internally aligned across theme, visual identity, remix framing, gameplay framing, and worker framing.
10. Preserve playability, controls, win/loss semantics, boot flow, readability, and control-safe behavior as non-negotiable.

## Canalization / activation rules
- Theme-heavy prompts should strongly influence `theme_policy.md`
- Visual / art-direction prompts should strongly influence `visual_identity_contract.md`
- Gameplay-leaning prompts should strongly influence gameplay-related guidance inside `creative_remix_contract.md`
- Broad cultural or franchise prompts may influence several creative files together
- `creative_refactor_agent_template.md` should be updated so the downstream worker interprets the recomposed bundle correctly

## Output requirements
When finished, create:
- `recomposition_summary.json`

This summary file must contain JSON with at least:
- `status`
- `summary`
- `editable_files_reviewed`
- `files_modified`
- `notes`

After updating the editable files and writing `recomposition_summary.json`, return exactly these four lines and nothing else:
CHANGED FILES: file1, file2 or NONE
SUMMARY: one short sentence describing the recomposed bundle
PRIMARY SHIFT: one short sentence naming the dominant reinterpretation
INVARIANTS: preserved|issues
"""


def build_recomposition_context(
    style_id: str,
    remix_prompt: str,
    explicit_targets: list[str],
    editable_files: dict[str, str],
    invariant_files: dict[str, str],
) -> dict:
    return {
        "generated_at": utc_now(),
        "style_id": style_id,
        "remix_prompt": remix_prompt,
        "explicit_prompt_targets": explicit_targets,
        "editable_creative_files": editable_files,
        "invariant_reference_files": invariant_files,
        "notes": [
            "Editable creative files should be rewritten by the first-stage CLI recomposition agent.",
            "Invariant files are fixed context only and must not be modified.",
            "Gameplay-related creative adaptation currently lives inside creative_remix_contract.md.",
        ],
    }


def base_spec_adaptor_job_state(
    run_id: str,
    adaptor_dir: Path,
    style: str,
    remix_prompt: str,
    model: str,
    timeout_seconds: int,
) -> dict:
    return {
        "job_id": f"{run_id}_spec_adaptor",
        "job_type": "spec_adaptor",
        "status": "queued",
        "style_id": style,
        "remix_prompt": remix_prompt,
        "model": model,
        "timeout_seconds": timeout_seconds,
        "started_at": None,
        "heartbeat_at": None,
        "finished_at": None,
        "result_path": None,
        "stdout_path": str(adaptor_dir / "recomposition_stdout.txt"),
        "stderr_path": str(adaptor_dir / "recomposition_stderr.txt"),
        "summary_path": str(adaptor_dir / "recomposition_summary.json"),
        "failure_reason": None,
        "validation": None,
    }


def build_recomposition_summary_scaffold() -> dict[str, Any]:
    return {
        "status": "__UNSET_STATUS__",
        "summary": "__UNSET_SUMMARY__",
        "editable_files_reviewed": ["__UNSET__"],
        "files_modified": ["__UNSET__"],
        "notes": [
            "PLACEHOLDER: this file must be rewritten by the recomposition agent"
        ],
    }


def validate_recomposition_summary(summary_path: Path) -> dict[str, Any]:
    result: dict[str, Any] = {
        "exists": summary_path.exists(),
        "valid_json": False,
        "required_keys_present": False,
        "missing_required_keys": [],
        "placeholder_values_present": False,
        "placeholder_fields": [],
        "payload": None,
        "failure_reason": None,
    }
    if not result["exists"]:
        result["failure_reason"] = "missing_recomposition_summary"
        return result

    try:
        payload = load_json(summary_path)
    except Exception as exc:
        result["failure_reason"] = f"invalid_recomposition_summary_json: {exc}"
        return result

    result["valid_json"] = True
    result["payload"] = payload
    if not isinstance(payload, dict):
        result["failure_reason"] = "invalid_recomposition_summary_shape"
        return result

    missing_keys = [key for key in RECOMPOSITION_SUMMARY_REQUIRED_KEYS if key not in payload]
    result["missing_required_keys"] = missing_keys
    result["required_keys_present"] = not missing_keys
    if missing_keys:
        result["failure_reason"] = f"recomposition_summary_missing_keys: {', '.join(missing_keys)}"
        return result

    placeholder_fields: list[str] = []
    if payload.get("status") == "__UNSET_STATUS__":
        placeholder_fields.append("status")
    if payload.get("summary") == "__UNSET_SUMMARY__":
        placeholder_fields.append("summary")
    if payload.get("editable_files_reviewed") == ["__UNSET__"]:
        placeholder_fields.append("editable_files_reviewed")
    if payload.get("files_modified") == ["__UNSET__"]:
        placeholder_fields.append("files_modified")
    notes = payload.get("notes")
    if notes == ["PLACEHOLDER: this file must be rewritten by the recomposition agent"]:
        placeholder_fields.append("notes")

    result["placeholder_fields"] = placeholder_fields
    result["placeholder_values_present"] = bool(placeholder_fields)
    if placeholder_fields:
        result["failure_reason"] = f"recomposition_summary_placeholders_not_replaced: {', '.join(placeholder_fields)}"
        return result

    return result


def parse_recomposition_stdout_contract(stdout_text: str) -> dict[str, Any]:
    parsed = {
        "changed_files_raw": "NONE",
        "changed_files": [],
        "summary": "",
        "primary_shift": "",
        "invariants": "",
    }
    markers = {
        "CHANGED FILES:": "changed_files_raw",
        "SUMMARY:": "summary",
        "PRIMARY SHIFT:": "primary_shift",
        "INVARIANTS:": "invariants",
    }
    for line in stdout_text.splitlines():
        for marker, key in markers.items():
            if line.startswith(marker):
                parsed[key] = line[len(marker):].strip()
    raw_changed = str(parsed["changed_files_raw"]).strip()
    if raw_changed and raw_changed.upper() != "NONE":
        parsed["changed_files"] = [item.strip() for item in raw_changed.split(",") if item.strip()]
    return parsed


def evaluate_recomposition_contract(summary_path: Path, stdout_text: str) -> dict[str, Any]:
    summary_validation = validate_recomposition_summary(summary_path)
    stdout_contract = parse_recomposition_stdout_contract(stdout_text)
    claimed_files = stdout_contract["changed_files"]
    mismatches: list[str] = []

    if "recomposition_summary.json" in claimed_files and not summary_validation["exists"]:
        mismatches.append("stdout_claimed_recomposition_summary_but_file_missing")

    success = (
        summary_validation["exists"]
        and summary_validation["valid_json"]
        and summary_validation["required_keys_present"]
        and not summary_validation["placeholder_values_present"]
        and not mismatches
    )
    failure_reason = None if success else (summary_validation["failure_reason"] or ("; ".join(mismatches) if mismatches else "recomposition_contract_validation_failed"))

    return {
        "success": success,
        "failure_reason": failure_reason,
        "summary_validation": summary_validation,
        "stdout_contract": stdout_contract,
        "mismatches": mismatches,
    }


def run_recomposition_agent(
    workspace_dir: Path,
    harness_path: Path,
    model: str,
    timeout_seconds: int,
    stdout_path: Path,
    stderr_path: Path,
    job_state_path: Path,
    trace_path: Path | None = None,
):
    command = [
        "cline",
        "-a",
        "-y",
        "--json",
        "-v",
        "-t",
        str(timeout_seconds),
        "--reasoning-effort",
        "low",
        "-c",
        str(workspace_dir),
        "--model",
        model,
        harness_path.read_text(encoding="utf-8"),
    ]
    if trace_path is not None:
        append_debug_trace(
            trace_path,
            f"Launching recomposition agent with timeout_seconds={timeout_seconds}, model={model}, cwd={workspace_dir}",
        )
        append_debug_trace(trace_path, f"Command: {json.dumps(command)}")

    def update_job_heartbeat() -> None:
        def mutate(job_state_payload: dict) -> None:
            if job_state_payload.get("status") == "running":
                job_state_payload["heartbeat_at"] = utc_now()

        update_json_file(job_state_path, mutate)

    execution = execute_worker_command(
        command=command,
        cwd=workspace_dir,
        stdout_path=stdout_path,
        stderr_path=stderr_path,
        timeout_seconds=timeout_seconds,
        heartbeat_callback=update_job_heartbeat,
    )
    if trace_path is not None:
        append_debug_trace(trace_path, f"Recomposition agent completed with returncode={execution.returncode}")
        append_debug_trace(
            trace_path,
            f"Captured stdout chars={len(execution.stdout_text)} stderr chars={len(execution.stderr_text)} timed_out={execution.timed_out}",
        )
    return execution


def main() -> None:
    args = parse_args()
    run_dir = Path(args.run_dir).resolve()
    run_state_path = run_dir / "run_state.json"
    run_state = load_json(run_state_path)

    adaptor_dir = run_dir / "spec_adaptor"
    adapted_dir = adaptor_dir / "adapted"
    invariant_dir = adaptor_dir / "invariants"
    trace_path = adaptor_dir / DEBUG_TRACE_FILENAME
    append_debug_trace(trace_path, f"spec_adaptor.py starting for run_dir={run_dir}")
    append_debug_trace(
        trace_path,
        f"Arguments: style={args.style}, model={args.model}, agent_timeout={args.agent_timeout}, prompt_targets={args.prompt_targets!r}, dry_run_spec_adaptor={args.dry_run_spec_adaptor}",
    )

    style_manifest = load_style_manifest(args.style)
    explicit_targets = parse_prompt_targets(args.prompt_targets)

    adapted_dir.mkdir(parents=True, exist_ok=True)
    invariant_dir.mkdir(parents=True, exist_ok=True)
    append_debug_trace(trace_path, f"Adaptor workspace ready at {adaptor_dir}")

    remix_prompt = args.remix_prompt.strip()
    remix_prompt_path = adaptor_dir / "user_remix_prompt.txt"
    write_text(remix_prompt_path, remix_prompt + "\n")
    append_debug_trace(trace_path, f"Remix prompt written to {remix_prompt_path}")

    selected_style_path = adaptor_dir / "selected_style.json"
    write_json(
        selected_style_path,
        {
            "style_id": args.style,
            "style_manifest_path": str((STYLES_ROOT / args.style / "style_manifest.json").resolve()),
            "generated_at": utc_now(),
        },
    )

    job_state_path = adaptor_dir / SPEC_ADAPTOR_JOB_STATE_FILENAME
    job_state = base_spec_adaptor_job_state(
        run_state["run_id"],
        adaptor_dir,
        args.style,
        remix_prompt,
        args.model,
        args.agent_timeout,
    )
    job_state["status"] = "running"
    job_state["started_at"] = utc_now()
    job_state["heartbeat_at"] = job_state["started_at"]
    runtime_write_json(job_state_path, job_state)
    append_debug_trace(trace_path, f"Initialized spec adaptor job state at {job_state_path}")

    editable_files = copy_editable_creative_bundle(style_manifest, adapted_dir)
    invariant_files = copy_invariant_reference_files(invariant_dir)
    append_debug_trace(trace_path, f"Copied editable files: {sorted(editable_files)}")
    append_debug_trace(trace_path, f"Copied invariant files: {sorted(invariant_files)}")

    context_path = adaptor_dir / "recomposition_context.json"
    write_json(
        context_path,
        build_recomposition_context(
            args.style,
            remix_prompt,
            explicit_targets,
            editable_files,
            invariant_files,
        ),
    )
    append_debug_trace(trace_path, f"Recomposition context written to {context_path}")

    report_path = adaptor_dir / "adaptation_report.json"
    summary_path = adaptor_dir / "recomposition_summary.json"
    usage_path = adaptor_dir / "recomposition_usage.json"

    if args.dry_run_spec_adaptor:
        write_json(
            summary_path,
            {
                "status": "completed",
                "summary": "Dry-run spec adaptor simulation completed without invoking cline.",
                "editable_files_reviewed": sorted(editable_files.keys()),
                "files_modified": [],
                "notes": [
                    "DRY RUN: spec-adaptor execution was simulated.",
                    "Editable and invariant bundles were copied into the adaptor workspace.",
                ],
            },
        )
        stdout_path = adaptor_dir / "recomposition_stdout_attempt_01.txt"
        stderr_path = adaptor_dir / "recomposition_stderr_attempt_01.txt"
        write_text(stdout_path, "DRY RUN: spec-adaptor execution simulated; cline was not invoked.\n")
        write_text(stderr_path, "DRY RUN: no stderr; spec-adaptor execution was simulated.\n")
        final_contract_evaluation = evaluate_recomposition_contract(summary_path, "")
        final_summary_exists = True
        final_execution = {
            "returncode": 0,
            "status": "completed",
            "timed_out": False,
            "started_at": job_state["started_at"],
            "finished_at": utc_now(),
            "duration_seconds": 0.0,
        }
        write_usage_artifact(usage_path, None, simulated=True)
        append_debug_trace(trace_path, "Dry-run spec adaptor completed without invoking recomposition agent")
    else:
        previous_failure: dict[str, Any] | None = None
        final_execution = None
        final_contract_evaluation = None
        final_summary_exists = False

        for attempt_number in range(1, SPEC_ADAPTOR_MAX_ATTEMPTS + 1):
            append_debug_trace(trace_path, f"Starting spec adaptor attempt {attempt_number}/{SPEC_ADAPTOR_MAX_ATTEMPTS}")
            write_json(summary_path, build_recomposition_summary_scaffold())
            append_debug_trace(trace_path, f"Seeded recomposition summary scaffold at {summary_path}")
            harness_path = adaptor_dir / f"spec_recomposition_harness_attempt_{attempt_number:02d}.md"
            write_text(
                harness_path,
                build_recomposition_harness(
                    args.style,
                    remix_prompt,
                    explicit_targets,
                    editable_files,
                    invariant_files,
                    attempt_number=attempt_number,
                    max_attempts=SPEC_ADAPTOR_MAX_ATTEMPTS,
                    previous_failure=previous_failure,
                ),
            )
            append_debug_trace(trace_path, f"Harness written to {harness_path}")

            stdout_path = adaptor_dir / f"recomposition_stdout_attempt_{attempt_number:02d}.txt"
            stderr_path = adaptor_dir / f"recomposition_stderr_attempt_{attempt_number:02d}.txt"

            execution = run_recomposition_agent(
                adaptor_dir,
                harness_path,
                args.model,
                args.agent_timeout,
                stdout_path,
                stderr_path,
                job_state_path,
                trace_path=trace_path,
            )
            append_debug_trace(trace_path, f"Recomposition stdout streamed to {stdout_path}")
            append_debug_trace(trace_path, f"Recomposition stderr streamed to {stderr_path}")

            contract_evaluation = evaluate_recomposition_contract(summary_path, execution.stdout_text)
            summary_exists = contract_evaluation["summary_validation"]["exists"]
            append_debug_trace(trace_path, f"Summary present={summary_exists} at {summary_path}")
            append_debug_trace(
                trace_path,
                f"Summary valid_json={contract_evaluation['summary_validation']['valid_json']} required_keys_present={contract_evaluation['summary_validation']['required_keys_present']}",
            )
            if contract_evaluation["summary_validation"]["missing_required_keys"]:
                append_debug_trace(trace_path, f"Summary missing_required_keys={contract_evaluation['summary_validation']['missing_required_keys']}")
            if contract_evaluation["summary_validation"]["placeholder_fields"]:
                append_debug_trace(trace_path, f"Summary placeholder_fields={contract_evaluation['summary_validation']['placeholder_fields']}")
            if contract_evaluation["mismatches"]:
                append_debug_trace(trace_path, f"Contract mismatches={contract_evaluation['mismatches']}")

            final_execution = execution
            final_contract_evaluation = contract_evaluation
            final_summary_exists = summary_exists

            if execution.returncode == 0 and contract_evaluation["success"]:
                append_debug_trace(trace_path, f"Attempt {attempt_number} succeeded with valid recomposition contract")
                break

            previous_failure = {
                "failure_reason": (
                    contract_evaluation["failure_reason"]
                    if execution.returncode == 0
                    else ("spec_adaptor_command_timed_out" if execution.timed_out else "spec_adaptor_command_failed")
                ),
                "missing_files": (
                    ["recomposition_summary.json"]
                    if not contract_evaluation["summary_validation"]["exists"]
                    else []
                ),
                "missing_required_keys": contract_evaluation["summary_validation"]["missing_required_keys"],
                "placeholder_fields": contract_evaluation["summary_validation"]["placeholder_fields"],
                "mismatches": contract_evaluation["mismatches"],
                "stdout_summary": contract_evaluation["stdout_contract"]["summary"],
            }
            append_debug_trace(trace_path, f"Attempt {attempt_number} failed; previous_failure={previous_failure}")

        assert final_execution is not None
        assert final_contract_evaluation is not None
        write_usage_artifact(usage_path, final_execution)

    adaptation_report = {
        "generated_at": utc_now(),
        "run_id": run_state["run_id"],
        "style_id": args.style,
        "remix_prompt_path": str(remix_prompt_path),
        "selected_style_path": str(selected_style_path),
        "recomposition_context_path": str(context_path),
        "adapted_dir": str(adapted_dir),
        "invariant_dir": str(invariant_dir),
        "editable_creative_files": editable_files,
        "invariant_reference_files": invariant_files,
        "explicit_prompt_targets": explicit_targets,
        "mode": "dry_run_spec_recomposition" if args.dry_run_spec_adaptor else "agent_authored_spec_recomposition",
        "recomposition_agent": {
            "model": args.model,
            "timeout_seconds": args.agent_timeout,
            "returncode": final_execution["returncode"] if args.dry_run_spec_adaptor else final_execution.returncode,
            "status": final_execution["status"] if args.dry_run_spec_adaptor else final_execution.status,
            "timed_out": final_execution["timed_out"] if args.dry_run_spec_adaptor else final_execution.timed_out,
            "started_at": final_execution["started_at"] if args.dry_run_spec_adaptor else final_execution.started_at,
            "finished_at": final_execution["finished_at"] if args.dry_run_spec_adaptor else final_execution.finished_at,
            "duration_seconds": final_execution["duration_seconds"] if args.dry_run_spec_adaptor else final_execution.duration_seconds,
            "usage_summary": None if args.dry_run_spec_adaptor else final_execution.usage_summary,
        },
        "recomposition_usage_path": str(usage_path),
        "recomposition_summary_path": str(summary_path) if final_summary_exists else None,
        "recomposition_summary_present": final_summary_exists,
        "recomposition_contract_validation": final_contract_evaluation,
        "max_attempts": SPEC_ADAPTOR_MAX_ATTEMPTS,
        "simulated": args.dry_run_spec_adaptor,
        "notes": [
            "Editable creative spec files were copied into a recomposition workspace.",
            "Invariant policy files were copied as fixed reference context only.",
            (
                "Spec-adaptor execution was simulated without invoking cline."
                if args.dry_run_spec_adaptor
                else "A first-stage CLI agent was asked to rewrite the editable creative spec bundle and write recomposition_summary.json."
            ),
            "Gameplay-related creative adaptation currently lives inside creative_remix_contract.md.",
        ],
    }
    write_json(report_path, adaptation_report)
    append_debug_trace(trace_path, f"Adaptation report written to {report_path}")

    job_state = load_json(job_state_path)
    if args.dry_run_spec_adaptor:
        job_state["status"] = "ready"
        job_state["finished_at"] = utc_now()
        job_state["heartbeat_at"] = job_state["finished_at"]
        job_state["result_path"] = str(report_path)
        job_state["failure_reason"] = None
        job_state["validation"] = final_contract_evaluation
        job_state["simulated"] = True
    else:
        contract_failure_reason = final_contract_evaluation["failure_reason"]
        job_state["status"] = "ready" if final_execution.returncode == 0 and final_contract_evaluation["success"] else final_execution.status
        if final_execution.returncode == 0 and not final_contract_evaluation["success"]:
            job_state["status"] = "failed"
        job_state["finished_at"] = utc_now()
        job_state["heartbeat_at"] = job_state["finished_at"]
        job_state["result_path"] = str(report_path)
        job_state["failure_reason"] = (
            None
            if final_execution.returncode == 0 and final_contract_evaluation["success"]
            else (
                contract_failure_reason
                if final_execution.returncode == 0
                else ("spec_adaptor_command_timed_out" if final_execution.timed_out else "spec_adaptor_command_failed")
            )
        )
        job_state["validation"] = final_contract_evaluation
    runtime_write_json(job_state_path, job_state)
    append_debug_trace(trace_path, f"Updated spec adaptor job state with status={job_state['status']}")

    run_state["selected_style_id"] = args.style
    run_state["remix_prompt"] = remix_prompt
    run_state["spec_adaptor"] = {
        "status": job_state["status"],
        "job_state_path": str(job_state_path),
        "adapted_dir": str(adapted_dir),
        "invariant_dir": str(invariant_dir),
        "adaptation_report_path": str(report_path),
        "remix_prompt_path": str(remix_prompt_path),
        "recomposition_context_path": str(context_path),
        "explicit_prompt_targets": explicit_targets,
        "recomposition_summary_path": str(summary_path) if final_summary_exists else None,
        "recomposition_summary_present": final_summary_exists,
        "failure_reason": job_state["failure_reason"],
        "validation": final_contract_evaluation,
        "max_attempts": SPEC_ADAPTOR_MAX_ATTEMPTS,
        "simulated": args.dry_run_spec_adaptor,
    }
    run_state["updated_at"] = utc_now()
    run_state.setdefault("notes", []).append(
        (
            f"Dry-run spec adaptor workspace created for style {args.style}."
            if args.dry_run_spec_adaptor
            else f"Agent-authored spec recomposition workspace created for style {args.style}."
        )
    )
    write_json(run_state_path, run_state)
    append_debug_trace(trace_path, f"Updated run_state.json with spec_adaptor status={run_state['spec_adaptor']['status']}")

    if not args.dry_run_spec_adaptor:
        if final_execution.returncode != 0:
            append_debug_trace(trace_path, "Exiting with failure because recomposition agent returned non-zero.")
            raise RuntimeError(
                f"Spec recomposition agent failed with exit code {final_execution.returncode}. See {job_state_path} and {trace_path}."
            )
        if not final_contract_evaluation["success"]:
            append_debug_trace(trace_path, f"Exiting with failure because recomposition contract validation failed: {final_contract_evaluation['failure_reason']}")
            raise RuntimeError(
                f"Spec recomposition contract validation failed ({final_contract_evaluation['failure_reason']}). See {job_state_path} and {trace_path}."
            )
    append_debug_trace(trace_path, f"spec_adaptor.py completed successfully; report_path={report_path}")
    print(report_path)


if __name__ == "__main__":
    main()