#!/usr/bin/env python3
import json
from pathlib import Path

RUN_DIR = Path("tools/game_generator/pipeline_runs/run_pipeline_20260514T233040Z")
STATE_PATH = RUN_DIR / "run_state.json"
DATA_PATH = RUN_DIR / "dashboard" / "dashboard_data.json"

state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
steps = state.get("steps", {})
if "remixer_lookup" in steps:
    del steps["remixer_lookup"]

state["steps"] = steps

recent_events = []
events_path = RUN_DIR / "events.jsonl"
if events_path.exists():
    lines = events_path.read_text(encoding="utf-8").splitlines()
    recent_events = [json.loads(line) for line in lines[-25:]][::-1]

dashboard_data = {
    "run_id": state.get("run_id"),
    "prompt": state.get("prompt"),
    "status": state.get("status"),
    "current_step": state.get("current_step"),
    "updated_at": state.get("updated_at"),
    "started_at": state.get("started_at"),
    "obfuscation_enabled": state.get("obfuscation_enabled"),
    "remix_prompt": state.get("remix_prompt"),
    "upload_enabled": state.get("upload_enabled"),
    "upload": state.get("upload"),
    "projected_cdn_urls": state.get("projected_cdn_urls", []),
    "artifacts": state.get("artifacts"),
    "steps": [
        {
            "id": step_id,
            "label": step_id.replace("_", " ").title(),
            "status": step_state.get("status", "unknown"),
            "details": step_state,
        }
        for step_id, step_state in steps.items()
        if step_id != "remixer_lookup"
    ],
    "recent_events": recent_events,
    "links": {
        **state.get("artifacts", {}),
        "final_output_dir": state.get("final_output_dir"),
        "final_output_dirs": state.get("final_output_dirs", []),
    },
    "error": state.get("error"),
}

DATA_PATH.write_text(json.dumps(dashboard_data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(DATA_PATH)