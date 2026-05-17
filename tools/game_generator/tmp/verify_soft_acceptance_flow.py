#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GAME_REFACTORING_ROOT = ROOT.parent / "game_refactoring"
SOURCE_RUN_DIR = GAME_REFACTORING_ROOT / "runs" / "run_game_remixer_20260517T140948Z"
FIXTURE_RUN_DIR = ROOT / "tmp" / "soft_acceptance_fixture_run"
FAILED_GAME_ID = "gamezone-d694ce4a-dc83-463b-9736-8af3eccdae67"


def load_module(name: str, path: Path):
    spec = spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module spec from {path}")
    module = module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def rewrite_fixture_paths() -> None:
    run_state_path = FIXTURE_RUN_DIR / "run_state.json"
    run_state = json.loads(run_state_path.read_text(encoding="utf-8"))
    run_state["run_dir"] = str(FIXTURE_RUN_DIR)
    run_state["runs_root"] = str(FIXTURE_RUN_DIR.parent)
    run_state["status"] = "transform_completed_with_warnings"
    run_state["current_phase"] = "parallel_batch_finished"
    run_state["games_transform_completed"] = 2
    run_state["games_transform_soft_completed"] = 1
    run_state["games_transform_failed"] = 0
    run_state["updated_at"] = utc_now()
    run_state.setdefault("notes", []).append("Fixture updated to represent soft-accepted completion.")
    run_state_path.write_text(json.dumps(run_state, indent=2) + "\n", encoding="utf-8")

    games_dir = FIXTURE_RUN_DIR / "games"
    for game_dir in games_dir.iterdir():
        if not game_dir.is_dir():
            continue
        game_state_path = game_dir / "game_state.json"
        game_state = json.loads(game_state_path.read_text(encoding="utf-8"))
        game_id = game_state["game_id"]
        game_state["input_mirror_path"] = str(FIXTURE_RUN_DIR / "input" / game_id)
        game_state["working_clone_path"] = str(game_dir / "working")
        game_state["output_path"] = str(FIXTURE_RUN_DIR / "output" / game_id)
        if isinstance(game_state.get("operator_pipeline_cost_report_path"), str):
            game_state["operator_pipeline_cost_report_path"] = str(game_dir / "operator_pipeline" / "cost_report.json")
        game_state_path.write_text(json.dumps(game_state, indent=2) + "\n", encoding="utf-8")


def apply_soft_acceptance_to_failed_game() -> dict:
    validator = load_module(
        "run_operator_pipeline_game_fixture",
        GAME_REFACTORING_ROOT / "scripts" / "run_operator_pipeline_game.py",
    )
    workspace = (
        FIXTURE_RUN_DIR
        / "games"
        / FAILED_GAME_ID
        / "operator_pipeline"
        / "node_01_remix_v5_super_operator"
        / "attempt_01"
        / "workspace"
    )
    manifest = validator.load_remix_v5_template_manifest()
    placeholder = validator.inspect_template_placeholders(workspace, manifest)
    contract = validator.inspect_operator_result_contract(workspace / "operator_result_contract.json")
    result_path = workspace.parent / "operator_result.json"
    result = json.loads(result_path.read_text(encoding="utf-8"))
    soft = validator.evaluate_soft_acceptance_candidate(
        workspace,
        manifest,
        placeholder,
        contract,
        result,
        final_stage=True,
        final_attempt=True,
    )
    if not soft.get("eligible"):
        raise RuntimeError(f"Fixture soft acceptance unexpectedly ineligible: {json.dumps(soft, indent=2)}")

    output_dir = FIXTURE_RUN_DIR / "output" / FAILED_GAME_ID
    if output_dir.exists():
        shutil.rmtree(output_dir)
    shutil.copytree(workspace, output_dir)

    result["status"] = "soft_completed"
    result["soft_accepted"] = True
    result["soft_acceptance"] = soft
    result["soft_acceptance_reason"] = soft.get("reason")
    result_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    game_state_path = FIXTURE_RUN_DIR / "games" / FAILED_GAME_ID / "game_state.json"
    game_state = json.loads(game_state_path.read_text(encoding="utf-8"))
    game_state["status"] = "soft_completed"
    game_state["current_phase"] = "creative_refactor_soft_completed"
    game_state["creative_phase"] = "creative_refactor_soft_completed"
    game_state["creative_status"] = "soft_completed"
    game_state["creative_output_path"] = str(output_dir)
    game_state["last_error"] = None
    game_state["soft_acceptance"] = soft
    game_state["soft_acceptance_reason"] = soft.get("reason")
    game_state["soft_acceptance_warning_count"] = len(soft.get("warnings") or [])
    game_state["updated_at"] = utc_now()
    game_state_path.write_text(json.dumps(game_state, indent=2) + "\n", encoding="utf-8")
    return soft


def run_command(args: list[str], cwd: Path) -> str:
    completed = subprocess.run(args, cwd=str(cwd), capture_output=True, text=True, check=True)
    return completed.stdout.strip()


def main() -> None:
    if FIXTURE_RUN_DIR.exists():
        shutil.rmtree(FIXTURE_RUN_DIR)
    shutil.copytree(SOURCE_RUN_DIR, FIXTURE_RUN_DIR)
    rewrite_fixture_paths()
    soft = apply_soft_acceptance_to_failed_game()

    run_command(["python3", "scripts/build_dashboard.py", "--run-dir", str(FIXTURE_RUN_DIR)], GAME_REFACTORING_ROOT)
    status_payload = json.loads(
        run_command(["python3", "scripts/creative_refactor_cli.py", "--json", "status", "--run-dir", str(FIXTURE_RUN_DIR)], GAME_REFACTORING_ROOT)
    )
    result_payload = json.loads(
        run_command(["python3", "scripts/creative_refactor_cli.py", "--json", "result", "--run-dir", str(FIXTURE_RUN_DIR)], GAME_REFACTORING_ROOT)
    )
    dashboard_payload = json.loads((FIXTURE_RUN_DIR / "dashboard" / "dashboard_data.json").read_text(encoding="utf-8"))

    presenter = load_module("pipeline_dashboard_presenter_fixture", ROOT / "scripts" / "pipeline_dashboard_presenter.py")
    output_dirs = sorted(str(path.resolve()) for path in (FIXTURE_RUN_DIR / "output").iterdir() if path.is_dir())
    pipeline_payload = {
        "run_id": "fixture_soft_acceptance_pipeline",
        "prompt": "3d gta game",
        "status": "completed",
        "current_step": "done",
        "started_at": utc_now(),
        "updated_at": utc_now(),
        "completed_at": utc_now(),
        "publish_enabled": False,
        "poll_seconds": 60,
        "remix_prompt": "3d gta game",
        "upload_enabled": False,
        "projected_cdn_urls": [],
        "artifacts": {
            "refactoring": {
                "run_dir": str(FIXTURE_RUN_DIR),
                "dashboard_path": str(FIXTURE_RUN_DIR / "dashboard" / "index.html"),
            }
        },
        "links": {
            "final_output_dir": str(FIXTURE_RUN_DIR / "output"),
            "final_output_dirs": output_dirs,
        },
        "steps": [
            {"id": "matcher", "status": "completed", "details": {"status": "completed", "started_at": utc_now(), "completed_at": utc_now()}},
            {
                "id": "refactoring",
                "status": "completed",
                "details": {
                    "status": "completed",
                    "run_dir": str(FIXTURE_RUN_DIR),
                    "last_known_status": "transform_completed_with_warnings",
                    "games_transform_completed": 2,
                    "games_transform_soft_completed": 1,
                    "games_transform_failed": 0,
                    "started_at": utc_now(),
                    "completed_at": utc_now(),
                },
            },
            {"id": "publish", "status": "skipped", "details": {"status": "skipped", "reason": "fixture"}},
            {"id": "finalize", "status": "completed", "details": {"status": "completed", "destination": str(FIXTURE_RUN_DIR / "output")}},
        ],
        "recent_events": [],
        "error": None,
    }
    view = presenter.build_current_run_view(pipeline_payload, ROOT / "pipeline_runs" / "run_pipeline_20260517T140907Z")

    summary = {
        "soft_acceptance": soft,
        "status_payload": status_payload,
        "result_payload": result_payload,
        "dashboard_summary": dashboard_payload.get("summary"),
        "dashboard_failed_game": next(
            (game for game in dashboard_payload.get("games", []) if isinstance(game, dict) and game.get("game_id") == FAILED_GAME_ID),
            None,
        ),
        "pipeline_refactor_stage": next(
            (stage for stage in view.get("stage_flow", []) if isinstance(stage, dict) and stage.get("id") == "refactor"),
            None,
        ),
        "pipeline_refactor_card": next(
            (card for card in view.get("refactor_cards", []) if isinstance(card, dict) and card.get("game_id") == FAILED_GAME_ID),
            None,
        ),
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()