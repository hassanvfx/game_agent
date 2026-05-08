#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMPTS_ROOT = ROOT / "prompts"
STYLES_ROOT = ROOT / "styles"
AUDIO_CATALOG_SOURCE = ROOT / "assets" / "audio_library" / "audios.json"

DEFAULT_STYLE_ID = "neutral_prototype"

GLOBAL_POLICY_PATHS_BY_JOB = {
    "creative_refactor": [
        PROMPTS_ROOT / "audio_policy.md",
        PROMPTS_ROOT / "network_policy.md",
        PROMPTS_ROOT / "system_contract.md",
        PROMPTS_ROOT / "refactor_compliance_spec.md",
        PROMPTS_ROOT / "creative_recovery_policy.md",
    ],
}


def load_json(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8").strip()
    decoder = json.JSONDecoder()
    payload, _ = decoder.raw_decode(raw)
    return payload


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def load_style_manifest(style_id: str) -> dict:
    manifest_path = STYLES_ROOT / style_id / "style_manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Style manifest not found for style '{style_id}': {manifest_path}")
    manifest = load_json(manifest_path)
    manifest["_manifest_path"] = str(manifest_path)
    return manifest


def resolve_style_file(path_str: str) -> Path:
    path = ROOT / path_str
    if not path.exists():
        raise FileNotFoundError(f"Referenced style file does not exist: {path}")
    return path


def get_prompt_template_source(job_type: str, style_manifest: dict) -> Path:
    if job_type != "creative_refactor":
        raise ValueError(f"Unsupported job type for style resolution: {job_type}")
    prompt_paths = style_manifest["style_local_files"]["prompts"]
    for path_str in prompt_paths:
        if Path(path_str).name == "creative_refactor_agent_template.md":
            return resolve_style_file(path_str)
    raise FileNotFoundError(
        f"Style '{style_manifest.get('style_id')}' does not define creative_refactor_agent_template.md"
    )


def get_spec_sources(job_type: str, style_manifest: dict) -> list[Path]:
    if job_type != "creative_refactor":
        raise ValueError(f"Unsupported job type for style resolution: {job_type}")
    spec_paths = style_manifest["style_local_files"]["specs"]
    return [resolve_style_file(path_str) for path_str in spec_paths]


def get_style_policy_sources(job_type: str, style_manifest: dict) -> list[Path]:
    if job_type != "creative_refactor":
        raise ValueError(f"Unsupported job type for style resolution: {job_type}")
    prompt_paths = style_manifest["style_local_files"]["prompts"]
    return [
        resolve_style_file(path_str)
        for path_str in prompt_paths
        if Path(path_str).name != "creative_refactor_agent_template.md"
    ]


def get_audio_catalog_source() -> Path | None:
    return AUDIO_CATALOG_SOURCE if AUDIO_CATALOG_SOURCE.exists() else None


def get_adapted_file_sources(run_dir: Path) -> dict[str, Path] | None:
    run_state_path = run_dir / "run_state.json"
    if not run_state_path.exists():
        return None
    run_state = load_json(run_state_path)
    spec_adaptor = run_state.get("spec_adaptor")
    if not spec_adaptor or spec_adaptor.get("status") != "ready":
        return None

    adapted_dir = Path(spec_adaptor["adapted_dir"])
    file_map = {}
    for filename in (
        "creative_refactor_agent_template.md",
        "creative_remix_contract.md",
        "visual_identity_contract.md",
        "theme_policy.md",
    ):
        candidate = adapted_dir / filename
        if candidate.exists():
            file_map[filename] = candidate
    return file_map if file_map else None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a Game Remixer task packet with creative-line parity semantics.")
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--game-id", required=True)
    parser.add_argument("--job-type", required=True, choices=sorted(GLOBAL_POLICY_PATHS_BY_JOB.keys()))
    parser.add_argument("--attempt-number", type=int, required=True)
    parser.add_argument("--target-path", required=True)
    parser.add_argument("--input-reference-path", required=True)
    parser.add_argument("--style", default=DEFAULT_STYLE_ID)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_dir = Path(args.run_dir).resolve()
    run_state = load_json(run_dir / "run_state.json")
    game_dir = run_dir / "games" / args.game_id
    game_state = load_json(game_dir / "game_state.json")

    style_manifest = load_style_manifest(args.style)
    adapted_sources = get_adapted_file_sources(run_dir)

    attempt_dir = game_dir / "attempts" / f"attempt_{args.attempt_number:04d}"
    refs_dir = attempt_dir / "refs"
    refs_dir.mkdir(parents=True, exist_ok=True)

    prompt_source = adapted_sources.get("creative_refactor_agent_template.md") if adapted_sources else get_prompt_template_source(args.job_type, style_manifest)
    prompt_ref = refs_dir / prompt_source.name
    prompt_ref.write_text(prompt_source.read_text(encoding="utf-8"), encoding="utf-8")

    spec_refs: list[str] = []
    spec_sources = [adapted_sources["creative_remix_contract.md"]] if adapted_sources and "creative_remix_contract.md" in adapted_sources else get_spec_sources(args.job_type, style_manifest)
    for source in spec_sources:
        destination = refs_dir / source.name
        destination.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
        spec_refs.append(str(destination))

    audio_catalog_source = get_audio_catalog_source()
    audio_catalog_ref = None
    if audio_catalog_source is not None:
        audio_catalog_destination = refs_dir / audio_catalog_source.name
        audio_catalog_destination.write_text(audio_catalog_source.read_text(encoding="utf-8"), encoding="utf-8")
        audio_catalog_ref = str(audio_catalog_destination)

    policy_refs: list[str] = []
    style_policy_sources = (
        [
            adapted_sources[name]
            for name in ("visual_identity_contract.md", "theme_policy.md")
            if adapted_sources and name in adapted_sources
        ]
        if adapted_sources
        else get_style_policy_sources(args.job_type, style_manifest)
    )
    policy_sources = style_policy_sources + GLOBAL_POLICY_PATHS_BY_JOB.get(args.job_type, [])
    for source in policy_sources:
        destination = refs_dir / source.name
        destination.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
        policy_refs.append(str(destination))

    packet = {
        "packet_version": "1.3.0",
        "run_id": run_state["run_id"],
        "game_id": args.game_id,
        "job_type": args.job_type,
        "attempt_number": args.attempt_number,
        "style_id": style_manifest["style_id"],
        "style_manifest_path": style_manifest["_manifest_path"],
        "adapted_refs_active": bool(adapted_sources),
        "adapted_refs_dir": str(Path(run_state["spec_adaptor"]["adapted_dir"])) if adapted_sources else None,
        "source_path": game_state["source_path"],
        "working_clone_path": game_state["working_clone_path"],
        "target_path": str(Path(args.target_path).resolve()),
        "input_reference_path": str(Path(args.input_reference_path).resolve()),
        "seeded_clone_mode": True,
        "edit_strategy": "in_place_on_target_path",
        "prompt_template_path": str(prompt_ref),
        "spec_paths": spec_refs,
        "policy_paths": policy_refs,
        "audio_catalog_path": audio_catalog_ref,
        "previous_result_path": None,
        "previous_judge_result_path": None,
    }

    packet_path = attempt_dir / f"{args.job_type}_task_packet.json"
    write_json(packet_path, packet)
    print(packet_path)


if __name__ == "__main__":
    main()