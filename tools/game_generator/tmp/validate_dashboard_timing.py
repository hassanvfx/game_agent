#!/usr/bin/env python3
from __future__ import annotations

import json
import py_compile
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from serve_pipeline_dashboard import refresh_dashboard_assets  # noqa: E402


EXPECTED = {
    "run_pipeline_20260517T110057Z": {
        "run_duration_human": "5m 7s",
        "stage_durations": {
            "match": "22s",
            "refactor": "4m 25s",
            "publish": "20s",
        },
    },
    "run_pipeline_20260517T124528Z": {
        "run_duration_human": "20s",
        "stage_durations": {
            "match": "20s",
            "refactor": None,
            "publish": None,
        },
    },
}


def compile_targets() -> None:
    for path in (
        SCRIPTS_DIR / "pipeline_dashboard_presenter.py",
        SCRIPTS_DIR / "run_pipeline.py",
        SCRIPTS_DIR / "serve_pipeline_dashboard.py",
    ):
        py_compile.compile(str(path), doraise=True)


def validate_run(run_id: str, checks: dict[str, object]) -> dict[str, object]:
    run_dir = ROOT / "pipeline_runs" / run_id
    dashboard_dir = run_dir / "dashboard"
    refresh_dashboard_assets(run_dir.resolve(), dashboard_dir.resolve())
    payload = json.loads((dashboard_dir / "dashboard_data.json").read_text())
    html = (dashboard_dir / "index.html").read_text()
    view = payload.get("current_run_view", {})

    actual_run_duration = view.get("timing", {}).get("duration_human")
    expected_run_duration = checks["run_duration_human"]
    if actual_run_duration != expected_run_duration:
        raise SystemExit(
            f"{run_id}: expected run duration {expected_run_duration}, got {actual_run_duration}"
        )

    stage_map = {item.get("id"): item for item in view.get("stage_flow", [])}
    expected_stage_durations = checks["stage_durations"]
    for stage_id, expected_duration in expected_stage_durations.items():
        actual_duration = stage_map.get(stage_id, {}).get("timing", {}).get("duration_human")
        if actual_duration != expected_duration:
            raise SystemExit(
                f"{run_id}:{stage_id}: expected {expected_duration}, got {actual_duration}"
            )

    required_html_markers = [
        "id=\"liveRunTimer\"",
        "renderRunTimer(view, data)",
        "installLiveRunTimerTick()",
        "updateLiveRunTimer()",
    ]
    for marker in required_html_markers:
        if marker not in html:
            raise SystemExit(f"{run_id}: generated dashboard HTML missing marker: {marker}")

    return {
        "run_id": run_id,
        "run_duration_human": actual_run_duration,
        "stage_durations": {
            stage_id: stage_map.get(stage_id, {}).get("timing", {}).get("duration_human")
            for stage_id in expected_stage_durations
        },
        "live_timer_html_verified": True,
    }


def main() -> int:
    compile_targets()
    for run_id, checks in EXPECTED.items():
        print(json.dumps(validate_run(run_id, checks), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())