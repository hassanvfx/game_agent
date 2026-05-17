#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GAME_REFACTORING_ROOT = ROOT / "tools" / "game_refactoring"
CATALOGS_DIR = GAME_REFACTORING_ROOT / "catalogs" / "skills"
SKILL_TYPES_PATH = CATALOGS_DIR / "skill_types.json"
BUILDER = GAME_REFACTORING_ROOT / "scripts" / "build_remix_v5_super_prompt.py"
OUTPUT_PROMPT = GAME_REFACTORING_ROOT / "prompts" / "operators_v2" / "00_creative_remix_v5_super_operator.md"
WORKFLOW = GAME_REFACTORING_ROOT / "scripts" / "game_workflow.py"
DOCS = GAME_REFACTORING_ROOT / "docs" / "game_workflow_cli.md"
CONTRACT_TEMPLATE_ROOT = GAME_REFACTORING_ROOT / "fixtures" / "remix_v5_contract_templates"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    skill_types_payload = load_json(SKILL_TYPES_PATH)
    ordered_types = [entry["id"] for entry in skill_types_payload["skill_types"]]

    expected_types = ["core", "analysis", "world", "visual", "media", "qa"]
    if ordered_types != expected_types:
        raise AssertionError(f"unexpected skill type order/content: {ordered_types}")

    seen_skill_ids: set[str] = set()
    validated_catalogs: list[str] = []
    for skill_type in ordered_types:
        path = CATALOGS_DIR / f"remix_v5_{skill_type}_skills.json"
        payload = load_json(path)
        if payload.get("skill_type") != skill_type:
            raise AssertionError(f"{path.name} skill_type mismatch")
        if not payload.get("namespace", "").startswith(f"remix_v5.{skill_type}"):
            raise AssertionError(f"{path.name} namespace mismatch")
        subgroups = payload.get("subgroups") or []
        if not subgroups:
            raise AssertionError(f"{path.name} missing subgroups")
        for subgroup in subgroups:
            if not subgroup.get("skills"):
                raise AssertionError(f"{path.name} subgroup {subgroup.get('id')} has no skills")
            for skill in subgroup["skills"]:
                required = ["id", "title", "intent", "required_actions", "required_artifacts", "acceptance_bar", "failure_modes_prevented"]
                missing = [key for key in required if key not in skill]
                if missing:
                    raise AssertionError(f"{path.name} skill {skill.get('id')} missing keys: {missing}")
                skill_id = skill["id"]
                if skill_id in seen_skill_ids:
                    raise AssertionError(f"duplicate skill id: {skill_id}")
                seen_skill_ids.add(skill_id)
        validated_catalogs.append(path.name)

    completed = subprocess.run([sys.executable, str(BUILDER)], check=True, capture_output=True, text=True, cwd=str(ROOT))
    if "remix_v5_super_prompt_built" not in completed.stdout:
        raise AssertionError("builder did not report success")
    prompt_text = OUTPUT_PROMPT.read_text(encoding="utf-8")
    for skill_id in sorted(seen_skill_ids):
        if skill_id not in prompt_text:
            raise AssertionError(f"generated prompt missing skill id: {skill_id}")
    if "## Phase 2 — Direct Rebuild Phase (Non-Catalogized)" not in prompt_text:
        if "## Phase 2 — Direct Rebuild Phase (Regeneration Spine, Non-Catalogized)" not in prompt_text:
            raise AssertionError("generated prompt missing direct rebuild phase heading")
    if "clone_rebuild_from_blueprint_and_old_refs" in prompt_text:
        pass
    if "Rebuild From Blueprint And Old References" not in prompt_text:
        raise AssertionError("generated prompt missing rebuild contract content")

    prompt_text_lower = prompt_text.lower()
    doctrine_phrases = [
        "## reconciliation doctrine",
        "the clone rebuild kernel is the regeneration spine",
        "## prompt steering contract",
        "blueprint-driven regenerator",
        "## governing decision hierarchy",
        "stability of the regenerated public surface",
        "## unifying operating ledger",
        "**preserve**: the real mechanics",
        "## phase relationship",
        "if the output still reads like the source game with themed paint, the operator has failed the v5 bar.",
    ]
    for phrase in doctrine_phrases:
        if phrase not in prompt_text_lower:
            raise AssertionError(f"generated prompt missing doctrine phrase: {phrase}")

    prompt_steering_phrases = [
        "mechanic meaning lens",
        "narrative / world lens",
        "visual / focal identity lens",
        "media / mood lens",
        "qa / judgement lens",
        "prompt_surface_map.md",
        "must visibly propagate across mechanics framing, world semantics, visual identity, media tone, and qa evidence",
    ]
    for phrase in prompt_steering_phrases:
        if phrase not in prompt_text_lower:
            raise AssertionError(f"generated prompt missing prompt-steering phrase: {phrase}")

    if prompt_text.count("#PROMPT#") < 8:
        raise AssertionError("generated prompt does not expose #PROMPT# often enough for multi-phase steering")

    workflow_text = WORKFLOW.read_text(encoding="utf-8")
    if '"creative_remix_v5"' not in workflow_text:
        raise AssertionError("workflow missing creative_remix_v5 id")
    if '"id": "remix_v5_super_operator"' not in workflow_text:
        raise AssertionError("workflow missing remix_v5_super_operator node")
    if "00_creative_remix_v5_super_operator.md" not in workflow_text:
        raise AssertionError("workflow missing v5 prompt file")

    docs_text = DOCS.read_text(encoding="utf-8")
    if "### `creative_remix_v5`" not in docs_text:
        raise AssertionError("workflow docs missing creative_remix_v5 section")

    fixture_manifest = load_json(CONTRACT_TEMPLATE_ROOT / "manifest.json")
    placeholder_token = fixture_manifest.get("placeholder_token")
    if placeholder_token != "__FILL_ME__":
        raise AssertionError("unexpected Remix v5 template placeholder token")
    seeded_dir = CONTRACT_TEMPLATE_ROOT / "seeded"
    for relative_name in fixture_manifest.get("seeded_artifacts", []) + fixture_manifest.get("support_files", []):
        path = seeded_dir / relative_name
        if not path.exists() or not path.is_file():
            raise AssertionError(f"missing Remix v5 template file: {path}")
        text = path.read_text(encoding="utf-8")
        if placeholder_token not in text:
            raise AssertionError(f"template file missing placeholder token: {path.name}")
        if path.suffix == ".json":
            load_json(path)

    if "seeded contract/template files already exist in the workspace" not in prompt_text:
        raise AssertionError("generated prompt missing seeded template guidance")
    if "no `__FILL_ME__` placeholders remain" not in prompt_text:
        raise AssertionError("generated prompt missing placeholder completion rule")

    print(
        json.dumps(
            {
                "status": "ok",
                "validated": [
                    "skill_catalog_schema_and_uniqueness",
                    "super_prompt_builder_execution",
                    "generated_prompt_skill_coverage",
                    "direct_rebuild_phase_preserved_outside_skills",
                    "reconciliation_doctrine_present",
                    "prompt_steering_contract_present",
                    "contract_template_fixtures_present",
                    "workflow_registration",
                    "workflow_docs",
                ],
                "catalogs": validated_catalogs,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()