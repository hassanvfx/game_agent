#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STYLE_ID = "neutral_prototype"
DEBUG_ROOT = ROOT / "fixtures" / "spec_adaptor_debug"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Permanent debug wrapper for spec_adaptor.py using persistent case directories."
    )
    parser.add_argument("--case-name", required=True, help="Stable case directory name under fixtures/spec_adaptor_debug/")
    parser.add_argument("--style", default=DEFAULT_STYLE_ID)
    parser.add_argument("--remix-prompt", required=True)
    parser.add_argument(
        "--prompt-targets",
        help=(
            "Optional comma-separated list of explicit creative spec targets. "
            "Passed through directly to scripts/spec_adaptor.py."
        ),
    )
    parser.add_argument("--model", default="gpt-5.4")
    parser.add_argument("--agent-timeout", type=int, default=900)
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Delete the existing case directory before regenerating it.",
    )
    return parser.parse_args()


def create_debug_run_state(case_name: str) -> dict:
    return {
        "run_id": f"spec_adaptor_debug_{case_name}",
        "status": "debug_ready",
        "current_phase": "spec_adaptor_debug",
        "games_transform_completed": 0,
        "games_transform_failed": 0,
        "selected_style_id": None,
        "remix_prompt": None,
        "spec_adaptor": None,
        "notes": [
            "Persistent debug workspace for isolated spec_adaptor inspection.",
        ],
        "created_at": utc_now(),
        "updated_at": utc_now(),
    }


def ensure_case_dir(case_dir: Path, case_name: str, clean: bool) -> Path:
    if clean and case_dir.exists():
        shutil.rmtree(case_dir)
    case_dir.mkdir(parents=True, exist_ok=True)

    run_state_path = case_dir / "run_state.json"
    write_json(run_state_path, create_debug_run_state(case_name))
    return run_state_path


def run_spec_adaptor(
    case_dir: Path,
    style: str,
    remix_prompt: str,
    prompt_targets: str | None,
    model: str,
    agent_timeout: int,
) -> Path:
    command = [
        "python3",
        str(ROOT / "scripts" / "spec_adaptor.py"),
        "--run-dir",
        str(case_dir),
        "--style",
        style,
        "--remix-prompt",
        remix_prompt,
        "--model",
        model,
        "--agent-timeout",
        str(agent_timeout),
    ]
    if prompt_targets:
        command.extend(["--prompt-targets", prompt_targets])

    completed = subprocess.run(command, check=True, capture_output=True, text=True)
    report_path = Path(completed.stdout.strip())
    if not report_path.exists():
        raise FileNotFoundError(f"Expected adaptation report was not created: {report_path}")
    return report_path


def build_debug_summary(
    case_name: str,
    style: str,
    remix_prompt: str,
    prompt_targets: str | None,
    report: dict,
    recomposition_summary: dict | None,
) -> dict:
    return {
        "case_name": case_name,
        "generated_at": utc_now(),
        "style_id": style,
        "remix_prompt": remix_prompt,
        "prompt_targets": [item.strip() for item in prompt_targets.split(",") if item.strip()] if prompt_targets else [],
        "mode": report.get("mode"),
        "recomposition_summary_present": report.get("recomposition_summary_present"),
        "editable_creative_files": sorted(report.get("editable_creative_files", {}).keys()),
        "invariant_reference_files": sorted(report.get("invariant_reference_files", {}).keys()),
        "recomposition_agent": report.get("recomposition_agent", {}),
        "adaptation_report_path": report.get("adaptation_report_path"),
        "recomposition_summary_path": report.get("recomposition_summary_path"),
        "recomposition_summary": recomposition_summary,
    }


def main() -> None:
    args = parse_args()
    case_dir = DEBUG_ROOT / args.case_name
    ensure_case_dir(case_dir, args.case_name, args.clean)

    request_path = case_dir / "debug_request.json"
    write_json(
        request_path,
        {
            "case_name": args.case_name,
            "style_id": args.style,
            "remix_prompt": args.remix_prompt,
            "prompt_targets": [item.strip() for item in args.prompt_targets.split(",") if item.strip()]
            if args.prompt_targets
            else [],
            "model": args.model,
            "agent_timeout": args.agent_timeout,
            "generated_at": utc_now(),
        },
    )

    report_path = run_spec_adaptor(
        case_dir,
        args.style,
        args.remix_prompt,
        args.prompt_targets,
        args.model,
        args.agent_timeout,
    )
    report = load_json(report_path)
    report["adaptation_report_path"] = str(report_path)

    recomposition_summary = None
    recomposition_summary_path = report.get("recomposition_summary_path")
    if recomposition_summary_path:
        summary_path = Path(recomposition_summary_path)
        if summary_path.exists():
            recomposition_summary = load_json(summary_path)

    summary = build_debug_summary(
        args.case_name,
        args.style,
        args.remix_prompt,
        args.prompt_targets,
        report,
        recomposition_summary,
    )
    summary_path = case_dir / "debug_summary.json"
    write_json(summary_path, summary)

    print(f"Case directory: {case_dir}")
    print(f"Mode: {summary['mode']}")
    print(f"Editable creative files: {', '.join(summary['editable_creative_files']) or 'none'}")
    print(f"Invariant reference files: {', '.join(summary['invariant_reference_files']) or 'none'}")
    print(f"Recomposition summary present: {summary['recomposition_summary_present']}")
    if recomposition_summary:
        print(f"Recomposition status: {recomposition_summary.get('status', 'unknown')}")
        print(f"Files modified: {', '.join(recomposition_summary.get('files_modified', [])) or 'none'}")
    print(f"Summary: {summary_path}")
    print(f"Report: {report_path}")


if __name__ == "__main__":
    main()