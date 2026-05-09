#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATH = ROOT / "tools/game_refactoring/scripts/game_workflow.py"
PROMPTS_DIR = ROOT / "tools/game_refactoring/prompts/operators_v2"
BUNDLES_DIR = PROMPTS_DIR / "v4_source_bundles"

EXPECTED_NODES = [
    ("remix_inference_plus", "00_creative_remix_v4_remix_inference_plus.md"),
    ("world_design_superprompt", "01_creative_remix_v4_world_design_superprompt.md"),
    ("visuals_base", "02_creative_remix_v4_visuals_base.md"),
    ("visual_ui_refine", "03_creative_remix_v4_visual_ui_refine.md"),
    ("final_mobile_repair_aggressive", "04_creative_remix_v4_final_mobile_repair_aggressive.md"),
]

REQUIRED_PROMPT_PHRASES = {
    "00_creative_remix_v4_remix_inference_plus.md": [
        "Mechanic decomposition",
        "Five-level difficulty progression",
        "Five-level visual evolution",
        "1.5-level core definition",
        "Do not break mechanics.",
    ],
    "01_creative_remix_v4_world_design_superprompt.md": [
        "Mechanic-aware world interpretation",
        "Five-level progression execution",
        "Media and asset mapping",
        "Procedural character/item/prop system",
        "Do not break mechanics.",
    ],
    "02_creative_remix_v4_visuals_base.md": [
        "Implement procedural art library",
        "Implement animated background",
        "Implement recognizable characters/items/props",
        "Implement five-level visual progression",
        "Do not break mechanics.",
    ],
    "03_creative_remix_v4_visual_ui_refine.md": [
        "Runtime discipline",
        "Screenshot-guided visual judgment",
        "Mobile layout refinement",
        "Preserve animated/procedural identity",
        "Do not break mechanics.",
    ],
    "04_creative_remix_v4_final_mobile_repair_aggressive.md": [
        "Absolute runtime discipline",
        "Console repair contract",
        "Required exploration behavior",
        "Multi-screen/state requirement",
        "Do not break mechanics.",
    ],
}


def load_workflow_module():
    spec = importlib.util.spec_from_file_location("game_workflow_check", WORKFLOW_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load game_workflow module spec")
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(WORKFLOW_PATH.parents[1]))
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def find_manifest() -> Path:
    candidates = [
        ROOT / "tmp/game_refactoring_experiments/fixtures/top100_vatsal_first_game_manifest.json",
        ROOT / "tmp/game_refactoring_experiments/fixtures/top107_vatsal_raw_backed_harry_potter_manifest.json",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    for candidate in (ROOT / "tmp").rglob("*manifest*.json"):
        try:
            payload = json.loads(candidate.read_text(encoding="utf-8"))
        except Exception:
            continue
        if isinstance(payload, dict) and isinstance(payload.get("games"), list) and payload["games"]:
            return candidate
    raise FileNotFoundError("No usable games manifest found for dry manifest-build check")


def main() -> None:
    workflow = load_workflow_module()
    definition = workflow.resolve_workflow("creative_remix_v4")
    node_pairs = [(node["id"], Path(node["prompt_file"]).name) for node in definition.nodes]
    if node_pairs != EXPECTED_NODES:
        raise AssertionError(f"Unexpected v4 node list: {node_pairs}")

    for node_id, prompt_name in EXPECTED_NODES:
        prompt_path = PROMPTS_DIR / prompt_name
        if not prompt_path.exists():
            raise AssertionError(f"Missing prompt for {node_id}: {prompt_path}")
        text = prompt_path.read_text(encoding="utf-8")
        if "CREATIVE REMIX V4 PRODUCTION PROMPT" not in text:
            raise AssertionError(f"Missing v4 marker in {prompt_name}")
        if "Source-Derived Instruction Library" not in text:
            raise AssertionError(f"Missing source library in {prompt_name}")
        if "<!-- SOURCE:" not in text:
            raise AssertionError(f"Missing provenance markers in {prompt_name}")
        for phrase in REQUIRED_PROMPT_PHRASES[prompt_name]:
            if phrase not in text:
                raise AssertionError(f"Missing phrase in {prompt_name}: {phrase}")
        bundle_path = BUNDLES_DIR / prompt_name.replace(".md", ".raw_concat.md")
        if not bundle_path.exists():
            raise AssertionError(f"Missing raw concat bundle: {bundle_path}")

    manifest_path = find_manifest()
    games, _ = workflow.resolve_games(manifest_path)
    generated = definition.build_manifest(games=games[:1], source_manifest_path=manifest_path)
    if generated["workflow"]["id"] != "creative_remix_v4":
        raise AssertionError("Generated manifest has wrong workflow id")
    if len(generated["nodes"]) != 5:
        raise AssertionError("Generated manifest does not contain 5 v4 nodes")

    print("creative_remix_v4_readiness_ok")
    print("workflow_nodes", len(generated["nodes"]))
    print("dry_manifest_game_count", len(generated["games"]))
    print("source_manifest", manifest_path)


if __name__ == "__main__":
    main()