#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.creative_refactor_runtime import load_json, write_json


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class WorkflowDefinition:
    workflow_id: str
    run_label: str
    nodes: list[dict[str, Any]]

    def build_manifest(self, games: list[dict[str, Any]], source_manifest_path: Path) -> dict[str, Any]:
        manifest = {
            "manifest_version": "2.0.0",
            "run_label": self.run_label,
            "nodes": deepcopy(self.nodes),
            "games": deepcopy(games),
            "workflow": {
                "id": self.workflow_id,
                "games_manifest_source": str(source_manifest_path),
            },
        }
        return manifest


WORKFLOWS: dict[str, WorkflowDefinition] = {
    "tag_and_fix": WorkflowDefinition(
        workflow_id="tag_and_fix",
        run_label="tag-and-fix",
        nodes=[
            {
                "id": "inference_outputs",
                "prompt_file": "prompts/operators_v2/01_specimen_inference_outputs.md",
                "accepted_upstream_statuses": ["ok", "warning", "error"],
                "requires_contract": False,
            },
            {
                "id": "playwright_fix",
                "prompt_file": "prompts/operators_v2/03_specimen_playwright_fix.md",
                "accepted_upstream_statuses": ["ok"],
                "requires_contract": True,
            },
        ],
    ),
    "creative_remix_v1": WorkflowDefinition(
        workflow_id="creative_remix_v1",
        run_label="creative-remix-v1",
        nodes=[
            {
                "id": "narrative",
                "prompt_file": "prompts/operators_v2/01_creative_remix_v1_narrative.md",
                "accepted_upstream_statuses": ["ok", "warning", "error"],
                "requires_contract": True,
            },
            {
                "id": "gameplay",
                "prompt_file": "prompts/operators_v2/02_creative_remix_v1_gameplay.md",
                "accepted_upstream_statuses": ["ok", "warning"],
                "requires_contract": True,
            },
            {
                "id": "visuals",
                "prompt_file": "prompts/operators_v2/03_creative_remix_v1_visuals.md",
                "accepted_upstream_statuses": ["ok", "warning"],
                "requires_contract": True,
            },
            {
                "id": "media_mapper",
                "prompt_file": "prompts/operators_v2/04_creative_remix_v1_media_mapper.md",
                "accepted_upstream_statuses": ["ok", "warning"],
                "requires_contract": True,
            },
        ],
    ),
    "creative_remix_v2": WorkflowDefinition(
        workflow_id="creative_remix_v2",
        run_label="creative-remix-v2",
        nodes=[
            {
                "id": "narrative",
                "prompt_file": "prompts/operators_v2/01_creative_remix_v1_narrative.md",
                "accepted_upstream_statuses": ["ok", "warning", "error"],
                "requires_contract": True,
            },
            {
                "id": "gameplay",
                "prompt_file": "prompts/operators_v2/02_creative_remix_v1_gameplay.md",
                "accepted_upstream_statuses": ["ok", "warning"],
                "requires_contract": True,
            },
            {
                "id": "visuals",
                "prompt_file": "prompts/operators_v2/03_creative_remix_v1_visuals.md",
                "accepted_upstream_statuses": ["ok", "warning"],
                "requires_contract": True,
            },
            {
                "id": "media_mapper",
                "prompt_file": "prompts/operators_v2/04_creative_remix_v1_media_mapper.md",
                "accepted_upstream_statuses": ["ok", "warning"],
                "requires_contract": True,
            },
            {
                "id": "narrative_round2",
                "prompt_file": "prompts/operators_v2/01_creative_remix_v1_narrative.md",
                "accepted_upstream_statuses": ["ok", "warning"],
                "requires_contract": True,
            },
            {
                "id": "gameplay_round2",
                "prompt_file": "prompts/operators_v2/02_creative_remix_v1_gameplay.md",
                "accepted_upstream_statuses": ["ok", "warning"],
                "requires_contract": True,
            },
            {
                "id": "visuals_round2",
                "prompt_file": "prompts/operators_v2/03_creative_remix_v1_visuals.md",
                "accepted_upstream_statuses": ["ok", "warning"],
                "requires_contract": True,
            },
            {
                "id": "media_mapper_round2",
                "prompt_file": "prompts/operators_v2/04_creative_remix_v1_media_mapper.md",
                "accepted_upstream_statuses": ["ok", "warning"],
                "requires_contract": True,
            },
        ],
    ),
    "creative_remix_v3": WorkflowDefinition(
        workflow_id="creative_remix_v3",
        run_label="creative-remix-v3",
        nodes=[
            {
                "id": "remix_inference",
                "prompt_file": "prompts/operators_v2/00_creative_remix_v3_remix_inference.md",
                "accepted_upstream_statuses": ["ok", "warning", "error"],
                "requires_contract": True,
            },
            {
                "id": "narrative",
                "prompt_file": "prompts/operators_v2/01_creative_remix_v1_narrative.md",
                "accepted_upstream_statuses": ["ok", "warning", "error"],
                "requires_contract": True,
            },
            {
                "id": "gameplay",
                "prompt_file": "prompts/operators_v2/02_creative_remix_v1_gameplay.md",
                "accepted_upstream_statuses": ["ok", "warning"],
                "requires_contract": True,
            },
            {
                "id": "visuals",
                "prompt_file": "prompts/operators_v2/03_creative_remix_v1_visuals.md",
                "accepted_upstream_statuses": ["ok", "warning"],
                "requires_contract": True,
            },
            {
                "id": "media_mapper",
                "prompt_file": "prompts/operators_v2/04_creative_remix_v1_media_mapper.md",
                "accepted_upstream_statuses": ["ok", "warning"],
                "requires_contract": True,
            },
            {
                "id": "visual_ui_redesign",
                "prompt_file": "prompts/operators_v2/06_creative_remix_v3_visual_ui_redesign.md",
                "accepted_upstream_statuses": ["ok", "warning"],
                "requires_contract": True,
            },
            {
                "id": "final_mobile_repair",
                "prompt_file": "prompts/operators_v2/09_creative_remix_v3_final_mobile_repair.md",
                "accepted_upstream_statuses": ["ok", "warning"],
                "requires_contract": True,
            },
            {
                "id": "level_adapter",
                "prompt_file": "prompts/operators_v2/10_creative_remix_v3_level_adapter.md",
                "accepted_upstream_statuses": ["ok", "warning"],
                "requires_contract": True,
            },
        ],
    ),
    "creative_remix_v4": WorkflowDefinition(
        workflow_id="creative_remix_v4",
        run_label="creative-remix-v4",
        nodes=[
            {
                "id": "remix_inference_plus",
                "prompt_file": "prompts/operators_v2/00_creative_remix_v4_remix_inference_plus.md",
                "accepted_upstream_statuses": ["ok", "warning", "error"],
                "requires_contract": True,
            },
            {
                "id": "world_design_superprompt",
                "prompt_file": "prompts/operators_v2/01_creative_remix_v4_world_design_superprompt.md",
                "accepted_upstream_statuses": ["ok", "warning"],
                "requires_contract": True,
            },
            {
                "id": "visuals_unified",
                "prompt_file": "prompts/operators_v2/03_creative_remix_v4_visuals_unified.md",
                "accepted_upstream_statuses": ["ok", "warning"],
                "requires_contract": True,
            },
            {
                "id": "final_mobile_repair_aggressive",
                "prompt_file": "prompts/operators_v2/04_creative_remix_v4_final_mobile_repair_aggressive.md",
                "accepted_upstream_statuses": ["ok", "warning"],
                "requires_contract": True,
            },
        ],
    ),
    "remix-v4-clone": WorkflowDefinition(
        workflow_id="remix-v4-clone",
        run_label="remix-v4-clone",
        nodes=[
            {
                "id": "clone_remix_inference_plus",
                "prompt_file": "prompts/operators_v2/00_remix_v4_clone_remix_inference_plus.md",
                "accepted_upstream_statuses": ["ok", "warning", "error"],
                "requires_contract": True,
            },
            {
                "id": "clone_rebuild_from_blueprint_and_old_refs",
                "prompt_file": "prompts/operators_v2/01_remix_v4_clone_rebuild_from_blueprint_and_old_refs.md",
                "accepted_upstream_statuses": ["ok", "warning", "error"],
                "requires_contract": True,
            },
            {
                "id": "clone_world_design_superprompt",
                "prompt_file": "prompts/operators_v2/02_remix_v4_clone_world_design_superprompt.md",
                "accepted_upstream_statuses": ["ok", "warning"],
                "requires_contract": True,
            },
            {
                "id": "clone_visuals_unified",
                "prompt_file": "prompts/operators_v2/03_remix_v4_clone_visuals_unified.md",
                "accepted_upstream_statuses": ["ok", "warning"],
                "requires_contract": True,
            },
            {
                "id": "clone_final_mobile_repair_aggressive",
                "prompt_file": "prompts/operators_v2/04_remix_v4_clone_final_mobile_repair_aggressive.md",
                "accepted_upstream_statuses": ["ok", "warning"],
                "requires_contract": True,
            },
        ],
    ),
    "creative_remix_v5": WorkflowDefinition(
        workflow_id="creative_remix_v5",
        run_label="creative-remix-v5",
        nodes=[
            {
                "id": "remix_v5_super_operator",
                "prompt_file": "prompts/operators_v2/00_creative_remix_v5_super_operator.md",
                "accepted_upstream_statuses": ["ok", "warning", "error"],
                "requires_contract": True,
            }
        ],
    ),
    "remix-v4-vite": WorkflowDefinition(
        workflow_id="remix-v4-vite",
        run_label="creative-remix-v4-vite",
        nodes=[
            {
                "id": "vite_surface_unpack",
                "prompt_file": "prompts/operators_v2/00_creative_remix_v4_vite_surface_unpack.md",
                "accepted_upstream_statuses": ["ok", "warning", "error"],
                "requires_contract": True,
            },
            {
                "id": "vite_remix_inference_plus",
                "prompt_file": "prompts/operators_v2/01_creative_remix_v4_vite_remix_inference_plus.md",
                "accepted_upstream_statuses": ["ok", "warning", "error"],
                "requires_contract": True,
            },
            {
                "id": "vite_world_design_superprompt",
                "prompt_file": "prompts/operators_v2/02_creative_remix_v4_vite_world_design_superprompt.md",
                "accepted_upstream_statuses": ["ok", "warning"],
                "requires_contract": True,
            },
            {
                "id": "vite_visuals_unified",
                "prompt_file": "prompts/operators_v2/03_creative_remix_v4_vite_visuals_unified.md",
                "accepted_upstream_statuses": ["ok", "warning"],
                "requires_contract": True,
            },
            {
                "id": "vite_final_mobile_repair_aggressive",
                "prompt_file": "prompts/operators_v2/04_creative_remix_v4_vite_final_mobile_repair_aggressive.md",
                "accepted_upstream_statuses": ["ok", "warning"],
                "requires_contract": True,
            },
        ],
    ),
    "game_obfuscator_cline_study": WorkflowDefinition(
        workflow_id="game_obfuscator_cline_study",
        run_label="game-obfuscator-cline-study",
        nodes=[
            {
                "id": "human_readable_obfuscation",
                "prompt_file": "prompts/operators_v2/08_game_obfuscator_cline_symbol_map_spanish.md",
                "accepted_upstream_statuses": ["ok", "warning", "error"],
                "requires_contract": True,
            }
        ],
    ),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Launch a named workflow by combining a workflow definition with a required external games manifest."
    )
    parser.add_argument("--json", action="store_true", help="Emit structured JSON output.")
    parser.add_argument("--id", required=True, help="Workflow identifier to run.")
    parser.add_argument(
        "--games-manifest-source",
        required=True,
        help="Manifest containing the required games list to inject into the workflow.",
    )
    parser.add_argument("--run-id", help="Optional explicit run id.")
    parser.add_argument("--runs-root", help="Optional custom runs root directory.")
    parser.add_argument(
        "--source-mode",
        choices=["copy", "inplace"],
        default="copy",
        help="How source game directories should be prepared before execution.",
    )
    parser.add_argument("--pipeline", choices=["v2", "legacy"], default="v2", help="Batch pipeline to use.")
    parser.add_argument("--model", default="gpt-5.5", help="Model to use for downstream workers.")
    parser.add_argument("--agent-timeout", type=int, default=3600, help="Per-game worker timeout in seconds.")
    parser.add_argument("--max-concurrency", type=int, default=2, help="Maximum number of active workers.")
    parser.add_argument("--poll-seconds", type=float, default=5.0, help="Scheduler poll interval in seconds.")
    parser.add_argument(
        "--stale-heartbeat-seconds",
        type=int,
        default=900,
        help="Heartbeat age threshold after which a worker is considered stale.",
    )
    parser.add_argument("--playwright-port-base", type=int, help="Optional leased-port pool base override.")
    parser.add_argument("--playwright-port-pool-size", type=int, help="Optional leased-port pool size override.")
    parser.add_argument(
        "--playwright-port-lease-ttl-seconds",
        type=int,
        help="Optional leased-port TTL override in seconds.",
    )
    parser.add_argument("--remix-prompt", help="Optional remix prompt override.")
    parser.add_argument("--remix-prompt-file", help="Optional file containing remix prompt override text.")
    parser.add_argument(
        "--dry-run-operators",
        action="store_true",
        help="Run the operator pipeline shell without invoking cline workers; stage results are simulated.",
    )
    parser.add_argument(
        "--dry-run-spec-adaptor",
        action="store_true",
        help="Run the spec-adaptor shell without invoking cline; shared adapted bundle artifacts are simulated.",
    )
    return parser.parse_args()


def resolve_workflow(workflow_id: str) -> WorkflowDefinition:
    try:
        return WORKFLOWS[workflow_id]
    except KeyError as exc:
        valid_ids = ", ".join(sorted(WORKFLOWS))
        raise ValueError(f"Unknown workflow id '{workflow_id}'. Valid ids: {valid_ids}") from exc


def resolve_games(source_manifest_path: Path) -> tuple[list[dict[str, Any]], str | None]:
    if not source_manifest_path.exists():
        raise FileNotFoundError(f"Games manifest source not found: {source_manifest_path}")

    source_manifest = load_json(source_manifest_path)
    games = source_manifest.get("games")
    if not isinstance(games, list) or not games:
        raise ValueError(f"Games manifest source must contain a non-empty 'games' list: {source_manifest_path}")

    run_label = source_manifest.get("run_label")
    return games, run_label if isinstance(run_label, str) and run_label.strip() else None


def build_generated_manifest_path(workflow_id: str, source_manifest_path: Path) -> Path:
    generated_dir = ROOT / "runs" / "_workflow_manifests"
    generated_dir.mkdir(parents=True, exist_ok=True)
    return generated_dir / f"{workflow_id}__{source_manifest_path.stem}.json"


def write_workflow_manifest(args: argparse.Namespace) -> tuple[Path, dict[str, Any]]:
    workflow = resolve_workflow(args.id)
    source_manifest_path = Path(args.games_manifest_source).resolve()
    games, source_run_label = resolve_games(source_manifest_path)

    manifest = workflow.build_manifest(games=games, source_manifest_path=source_manifest_path)
    if source_run_label:
        manifest["run_label"] = f"{manifest['run_label']}-{source_run_label}"

    manifest_path = build_generated_manifest_path(args.id, source_manifest_path)
    write_json(manifest_path, manifest)
    return manifest_path, manifest


def launch_batch(args: argparse.Namespace, manifest_path: Path) -> dict[str, Any]:
    command = [
        "python3",
        str(ROOT / "scripts" / "creative_refactor_cli.py"),
        "--json",
        "start-batch",
        "--manifest",
        str(manifest_path),
        "--pipeline",
        args.pipeline,
        "--model",
        args.model,
        "--agent-timeout",
        str(args.agent_timeout),
        "--max-concurrency",
        str(args.max_concurrency),
        "--poll-seconds",
        str(args.poll_seconds),
        "--stale-heartbeat-seconds",
        str(args.stale_heartbeat_seconds),
        "--source-mode",
        args.source_mode,
    ]
    if args.run_id:
        command.extend(["--run-id", args.run_id])
    if args.runs_root:
        command.extend(["--runs-root", args.runs_root])
    if args.remix_prompt:
        command.extend(["--remix-prompt", args.remix_prompt])
    if args.remix_prompt_file:
        command.extend(["--remix-prompt-file", args.remix_prompt_file])
    if args.playwright_port_base is not None:
        command.extend(["--playwright-port-base", str(args.playwright_port_base)])
    if args.playwright_port_pool_size is not None:
        command.extend(["--playwright-port-pool-size", str(args.playwright_port_pool_size)])
    if args.playwright_port_lease_ttl_seconds is not None:
        command.extend(["--playwright-port-lease-ttl-seconds", str(args.playwright_port_lease_ttl_seconds)])
    if args.dry_run_operators:
        command.append("--dry-run-operators")
    if args.dry_run_spec_adaptor:
        command.append("--dry-run-spec-adaptor")

    completed = subprocess.run(command, check=True, capture_output=True, text=True, cwd=str(ROOT))
    payload = json.loads(completed.stdout)
    payload["workflow_id"] = args.id
    payload["workflow_manifest_path"] = str(manifest_path)
    return payload


def emit_output(payload: dict[str, Any], as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, indent=2))
        return
    if "run_id" in payload:
        print(payload["run_id"])
        return
    print(json.dumps(payload, indent=2))


def main() -> None:
    args = parse_args()
    manifest_path, manifest = write_workflow_manifest(args)
    payload = launch_batch(args, manifest_path)
    payload["workflow_games_count"] = len(manifest["games"])
    emit_output(payload, args.json)


if __name__ == "__main__":
    main()