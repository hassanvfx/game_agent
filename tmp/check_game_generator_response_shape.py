#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def load_run_pipeline_module():
    module_path = Path("tools/game_generator/scripts/run_pipeline.py")
    spec = importlib.util.spec_from_file_location("run_pipeline", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    mod = load_run_pipeline_module()

    run = mod.PipelineRun(
        "tmp_shape_probe_20260514",
        "mario bros",
        "mario bros",
        False,
        mod.DEFAULT_POLL_SECONDS,
        mod.DEFAULT_MATCHER_MODE,
        True,
    )

    run.state["status"] = "completed"
    run.state["final_output_dir"] = "/tmp/final"
    run.state["final_output_dirs"] = ["/tmp/final/game-a", "/tmp/final/game-b"]
    run.state["projected_cdn_urls"] = [
        {
            "game_id": "game-a",
            "public_local_dir": "/tmp/public/game-a",
            "public_cdn_url": "https://example.com/public/game-a/index.html",
            "play_local_dir": "/tmp/play/game-a",
            "play_cdn_url": "https://example.com/play/game-a/index.html",
        }
    ]
    run.state["upload"] = {
        "enabled": True,
        "status": "completed",
        "sync_result": {"summary": {"status": "passed"}},
    }
    run.state["steps"]["matcher"] = {
        "status": "completed",
        "validated_selected_tags_path": "/tmp/validated_selected_tags.json",
    }
    run.state["steps"]["refactoring"] = {
        "status": "completed",
        "games_manifest_path": "/tmp/games_manifest.json",
        "run_dir": "/tmp/refactor_run",
        "dashboard_path": "/tmp/refactor_dashboard/index.html",
        "workflow_manifest_path": "/tmp/workflow_manifest.json",
    }
    run.state["steps"]["publish"] = {"status": "completed"}

    payload = mod.build_final_response(
        run,
        upload_payload=run.state["upload"],
        projected_cdn_urls=run.state["projected_cdn_urls"],
        resumed_from_run="run_pipeline_prev",
    )
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())