#!/usr/bin/env python3
import json
from pathlib import Path

RUN_DIR = Path("tools/game_generator/pipeline_runs/run_pipeline_20260514T182119Z/dashboard")
HTML_PATH = RUN_DIR / "index.html"
DATA_PATH = RUN_DIR / "dashboard_data.json"

html = HTML_PATH.read_text(encoding="utf-8")
data = json.loads(DATA_PATH.read_text(encoding="utf-8"))

checks = {
    "stage_flow_copy": "match → refactor → publish → finalize" in html,
    "stage_labels_present": all(label in html for label in ["Match", "Refactor", "Publish", "Finalize"]),
    "artifacts_section_present": "<h2>Artifacts</h2>" in html,
    "final_output_dirs_section_present": "<h2>Final Output Dirs</h2>" in html,
    "upload_section_present": "<h2>Upload</h2>" in html,
    "projected_cdn_section_present": "<h2>Projected CDN URLs</h2>" in html,
    "steps_array_present_in_payload": isinstance(data.get("steps"), list),
    "links_final_output_dirs_present_in_payload": isinstance(data.get("links", {}).get("final_output_dirs"), list),
    "artifacts_present_in_payload": isinstance(data.get("artifacts"), dict),
}

print(json.dumps(checks, indent=2, sort_keys=True))