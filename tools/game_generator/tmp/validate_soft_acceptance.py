#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GAME_REFACTORING_ROOT = ROOT.parent / "game_refactoring"
SCRIPT_PATH = GAME_REFACTORING_ROOT / "scripts" / "run_operator_pipeline_game.py"
WORKSPACE = (
    GAME_REFACTORING_ROOT
    / "runs"
    / "run_game_remixer_20260517T140948Z"
    / "games"
    / "gamezone-d694ce4a-dc83-463b-9736-8af3eccdae67"
    / "operator_pipeline"
    / "node_01_remix_v5_super_operator"
    / "attempt_01"
    / "workspace"
)


def load_module():
    spec = spec_from_file_location("run_operator_pipeline_game", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module spec from {SCRIPT_PATH}")
    module = module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> None:
    module = load_module()
    manifest = module.load_remix_v5_template_manifest()
    placeholder = module.inspect_template_placeholders(WORKSPACE, manifest)
    contract = module.inspect_operator_result_contract(WORKSPACE / "operator_result_contract.json")
    result = json.loads((WORKSPACE.parent / "operator_result.json").read_text(encoding="utf-8"))
    payload = module.evaluate_soft_acceptance_candidate(
        WORKSPACE,
        manifest,
        placeholder,
        contract,
        result,
        final_stage=True,
        final_attempt=True,
    )
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()