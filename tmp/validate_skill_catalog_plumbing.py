#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GAME_REFACTORING_ROOT = ROOT / "tools" / "game_refactoring"
sys.path.insert(0, str(GAME_REFACTORING_ROOT))

from scripts import media_policy  # noqa: E402
from scripts import run_operator_pipeline_game as pipeline_game  # noqa: E402


SKILL_TYPES_PATH = ROOT / "tools" / "game_refactoring" / "catalogs" / "skills" / "skill_types.json"


@dataclass(frozen=True)
class DummyOperator:
    id: str
    stage_number: int
    prompt: Path

    @property
    def stage_slug(self) -> str:
        return f"node_{self.stage_number:02d}_{self.id}"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def validate_skill_types() -> None:
    payload = json.loads(SKILL_TYPES_PATH.read_text(encoding="utf-8"))
    require(payload.get("schema_version") == "1.0.0", "skill_types.json schema_version must be 1.0.0")
    require(payload.get("catalog_kind") == "game_refactoring_skill_types", "unexpected catalog_kind")
    skill_types = payload.get("skill_types")
    require(isinstance(skill_types, list) and skill_types, "skill_types must be a non-empty list")
    ids = [item.get("id") for item in skill_types if isinstance(item, dict)]
    require(len(ids) == len(set(ids)), "skill type IDs must be unique")
    expected = {"core", "analysis", "rebuild", "world", "visual", "media", "qa"}
    require(expected.issubset(set(ids)), f"missing expected skill type IDs: {sorted(expected - set(ids))}")


def validate_workspace_copy_and_prompt_header() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_root = Path(temp_dir)
        workspace = temp_root / "workspace"
        workspace.mkdir(parents=True)
        copied = pipeline_game.copy_catalogs_into_workspace(workspace)

        required_catalogs = {"audios.json", "gifs.json", "sprites.json", "fonts.json", "skills/"}
        require(required_catalogs.issubset(copied.keys()), f"missing copied catalogs: {sorted(required_catalogs - set(copied))}")
        require((workspace / "catalogs" / "skills" / "skill_types.json").is_file(), "skill_types.json was not copied")

        prompt_path = temp_root / "dummy_prompt.md"
        prompt_path.write_text("# Dummy Prompt\n\nUse #PROMPT#.\n", encoding="utf-8")
        operator = DummyOperator(id="skill_catalog_probe", stage_number=1, prompt=prompt_path)
        prompt_text = pipeline_game.build_operator_prompt_text(
            run_state={"run_id": "test-run", "remix_prompt": "catalog plumbing probe"},
            game_state={"game_id": "test-game", "display_name": "Test Game"},
            operator=operator,  # type: ignore[arg-type]
            attempt_number=1,
            attempt_workspace=workspace,
            previous_contract_status=None,
            previous_contract_detail=None,
            playwright_port=8123,
            workspace_catalogs=copied,
        )

        require("## Skill Catalog Policy" in prompt_text, "prompt header missing Skill Catalog Policy")
        require("- status: available" in prompt_text, "prompt header did not mark skill catalogs available")
        require("workspace_relative_path: catalogs/skills/" in prompt_text, "prompt header missing workspace-relative skills path")
        require("catalog plumbing probe" in prompt_text, "#PROMPT# replacement did not occur")


def validate_media_policy_catalog_ignore() -> None:
    require(media_policy._is_catalog_file("catalogs/skills/skill_types.json"), "media policy should ignore catalogs/skills descendants")


def main() -> None:
    validate_skill_types()
    validate_workspace_copy_and_prompt_header()
    validate_media_policy_catalog_ignore()
    print(
        json.dumps(
            {
                "status": "ok",
                "validated": [
                    "skill_types_schema",
                    "catalog_copy_includes_skills_directory",
                    "prompt_header_exposes_skill_catalog_policy",
                    "media_policy_ignores_catalogs_skills",
                ],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()