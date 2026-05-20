#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


TOOL_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = TOOL_ROOT.parents[1] / "games" / "published" / "public" / "app.json"
DEFAULT_RUN_ROOT = TOOL_ROOT / "scripts" / "mobile" / "run_artifacts"

DEFAULT_COMPARE_ROOT = TOOL_ROOT.parents[1] / "games" / "published" / "public"

ANALYZE_CATALOG = TOOL_ROOT / "scripts" / "mobile" / "home_curation" / "analyze_catalog.py"
GENERATE_FILTER = TOOL_ROOT / "scripts" / "mobile" / "home_curation" / "generate_filter_manifest.py"
GENERATE_LAYOUTS = TOOL_ROOT / "scripts" / "mobile" / "home_curation" / "generate_editorial_layouts.py"
GENERATE_FEEDS = TOOL_ROOT / "scripts" / "mobile" / "editorial_feeds" / "generate_top_feeds.py"
BUILD_TAXONOMY = TOOL_ROOT / "scripts" / "mobile" / "search" / "build_taxonomy_reverse_index.py"
GENERATE_CANDIDATES = TOOL_ROOT / "scripts" / "mobile" / "tmp" / "editorial_phase3_generate_candidates.py"
BLUEPRINT_PATH = TOOL_ROOT / "scripts" / "mobile" / "tmp" / "editorial_phase2_blueprint.json"

ARTIFACT_FILENAMES = [
    "home_collections_ids.json",
    "home_filter_manifest.json",
    "editorial_phase3_candidates.json",
    "editorial_layouts.json",
    "taxonomy_search_artifact.json",
    "top_tag_feeds.json",
    "remix_feed.json",
    "tag_registry.json",
    "all_tag_match_counts.json",
]


@dataclass
class StepResult:
    name: str
    command: list[str]
    cwd: str
    log_path: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate generated mobile JSON artifacts against current bundled iOS Assets before optional deploy."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help="Input catalog path. Defaults to games/published/public/app.json.",
    )
    parser.add_argument(
        "--run-root",
        type=Path,
        default=DEFAULT_RUN_ROOT,
        help="Directory where timestamped runs will be created.",
    )
    parser.add_argument(
        "--compare-root",
        type=Path,
        default=DEFAULT_COMPARE_ROOT,
        help="Root containing the current artifact files to compare against.",
    )
    parser.add_argument(
        "--deploy",
        action="store_true",
        help="After validation, copy generated artifact files into --compare-root.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Create the run structure and print the execution plan without running generation steps.",
    )
    parser.add_argument(
        "--screenshots-cleanup",
        action="store_true",
        help="Forward screenshot validation/cleanup to the editorial candidates stage.",
    )
    return parser.parse_args()


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def run_step(
    name: str,
    command: list[str],
    cwd: Path,
    log_path: Path,
    *,
    step_index: int,
    step_total: int,
) -> StepResult:
    print(f"[mobile-validate] [{step_index}/{step_total}] start {name}", flush=True)
    print(f"[mobile-validate] [{step_index}/{step_total}] cwd={cwd}", flush=True)
    print(f"[mobile-validate] [{step_index}/{step_total}] command={' '.join(command)}", flush=True)
    process = subprocess.Popen(
        command,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    combined = [f"$ (cwd={cwd}) {' '.join(command)}"]
    assert process.stdout is not None
    for line in process.stdout:
        print(line, end="")
        combined.append(line.rstrip())
    returncode = process.wait()
    combined.append(f"[exit_code] {returncode}")
    log_path.write_text("\n".join(combined) + "\n", encoding="utf-8")
    print(f"[mobile-validate] [{step_index}/{step_total}] log={log_path}", flush=True)
    if returncode != 0:
        print(f"[mobile-validate] [{step_index}/{step_total}] failed {name}", flush=True)
        raise RuntimeError(f"Step failed: {name}. See log: {log_path}")
    print(f"[mobile-validate] [{step_index}/{step_total}] done {name}", flush=True)
    return StepResult(name=name, command=command, cwd=str(cwd), log_path=str(log_path))


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def compare_artifact(current_path: Path, generated_path: Path) -> dict[str, Any]:
    if not generated_path.exists():
        return {
            "status": "missing-generated",
            "current_path": str(current_path),
            "generated_path": str(generated_path),
        }

    if not current_path.exists():
        return {
            "status": "missing-current",
            "current_path": str(current_path),
            "generated_path": str(generated_path),
        }

    current_payload = load_json(current_path)
    generated_payload = load_json(generated_path)
    if current_payload == generated_payload:
        return {
            "status": "unchanged",
            "current_path": str(current_path),
            "generated_path": str(generated_path),
        }

    return {
        "status": "changed",
        "current_path": str(current_path),
        "generated_path": str(generated_path),
    }


def main() -> int:
    args = parse_args()
    input_path = args.input.resolve()
    if not input_path.exists():
        raise SystemExit(f"Input catalog not found: {input_path}")

    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    run_dir = args.run_root.resolve() / timestamp
    input_dir = run_dir / "input"
    artifacts_dir = run_dir / "artifacts"
    logs_dir = run_dir / "logs"
    support_dir = run_dir / "support"
    workspace_dir = run_dir / "workspace"
    taxonomy_dir = support_dir / "taxonomy"

    print("[mobile-validate] =============================", flush=True)
    print("[mobile-validate] Validate mobile artifacts", flush=True)
    print(f"[mobile-validate] input catalog: {input_path}", flush=True)
    print(f"[mobile-validate] run root: {args.run_root}", flush=True)
    print(f"[mobile-validate] run dir: {run_dir}", flush=True)
    print(f"[mobile-validate] artifacts dir: {artifacts_dir}", flush=True)
    print(f"[mobile-validate] compare root: {args.compare_root}", flush=True)
    print(f"[mobile-validate] deploy: {args.deploy}", flush=True)
    print(f"[mobile-validate] dry_run: {args.dry_run}", flush=True)
    print(f"[mobile-validate] screenshots_cleanup: {args.screenshots_cleanup}", flush=True)
    print("[mobile-validate] =============================", flush=True)

    for path in [input_dir, artifacts_dir, logs_dir, support_dir, workspace_dir, taxonomy_dir]:
        ensure_dir(path)

    run_input_catalog = input_dir / "app.json"
    shutil.copy2(input_path, run_input_catalog)
    print(f"[mobile-validate] copied input snapshot to {run_input_catalog}", flush=True)

    if args.dry_run:
        dry_run_payload = {
            "input_catalog": str(input_path),
            "run_input_catalog": str(run_input_catalog),
            "run_root": str(args.run_root),
            "run_dir": str(run_dir),
            "artifacts_dir": str(artifacts_dir),
            "logs_dir": str(logs_dir),
            "support_dir": str(support_dir),
            "workspace_dir": str(workspace_dir),
            "compare_root": str(args.compare_root),
            "deploy_requested": bool(args.deploy),
            "dry_run": True,
            "planned_steps": [
                {
                    "name": "home_collections",
                    "command": ["python3", str(ANALYZE_CATALOG), str(run_input_catalog), "--output-dir", str(artifacts_dir)],
                    "cwd": str(TOOL_ROOT),
                },
                {
                    "name": "home_filter_manifest",
                    "command": ["python3", str(GENERATE_FILTER), str(run_input_catalog), "--output-dir", str(artifacts_dir)],
                    "cwd": str(TOOL_ROOT),
                },
                {
                    "name": "taxonomy_search_artifact",
                    "command": ["python3", str(BUILD_TAXONOMY), "--input", str(run_input_catalog), "--output-dir", str(taxonomy_dir)],
                    "cwd": str(TOOL_ROOT),
                },
                {
                    "name": "editorial_feeds",
                    "command": [
                        "python3",
                        str(GENERATE_FEEDS),
                        "--app",
                        str(run_input_catalog),
                        "--out-dir",
                        str(artifacts_dir),
                        "--all-tag-match-counts-out",
                        str(artifacts_dir / "all_tag_match_counts.json"),
                    ],
                    "cwd": str(TOOL_ROOT),
                },
                {
                    "name": "editorial_candidates",
                    "command": [
                        "python3",
                        str(GENERATE_CANDIDATES),
                        *(["--screenshots-cleanup"] if args.screenshots_cleanup else []),
                    ],
                    "cwd": str(workspace_dir),
                },
                {
                    "name": "editorial_layouts",
                    "command": [
                        "python3",
                        str(GENERATE_LAYOUTS),
                        "--candidates",
                        str(artifacts_dir / "editorial_phase3_candidates.json"),
                        "--out",
                        str(artifacts_dir / "editorial_layouts.json"),
                    ],
                    "cwd": str(TOOL_ROOT),
                },
            ],
        }
        print(json.dumps(dry_run_payload, indent=2, ensure_ascii=False))
        return 0

    executed_steps: list[StepResult] = []
    step_total = 6

    executed_steps.append(
        run_step(
            name="home_collections",
            command=["python3", str(ANALYZE_CATALOG), str(run_input_catalog), "--output-dir", str(artifacts_dir)],
            cwd=TOOL_ROOT,
            log_path=logs_dir / "home_collections.log",
            step_index=1,
            step_total=step_total,
        )
    )

    executed_steps.append(
        run_step(
            name="home_filter_manifest",
            command=["python3", str(GENERATE_FILTER), str(run_input_catalog), "--output-dir", str(artifacts_dir)],
            cwd=TOOL_ROOT,
            log_path=logs_dir / "home_filter_manifest.log",
            step_index=2,
            step_total=step_total,
        )
    )

    executed_steps.append(
        run_step(
            name="taxonomy_search_artifact",
            command=["python3", str(BUILD_TAXONOMY), "--input", str(run_input_catalog), "--output-dir", str(taxonomy_dir)],
            cwd=TOOL_ROOT,
            log_path=logs_dir / "taxonomy_search_artifact.log",
            step_index=3,
            step_total=step_total,
        )
    )
    shutil.copy2(taxonomy_dir / "taxonomy_search_artifact.json", artifacts_dir / "taxonomy_search_artifact.json")
    print(
        f"[mobile-validate] copied taxonomy artifact to {artifacts_dir / 'taxonomy_search_artifact.json'}",
        flush=True,
    )

    executed_steps.append(
        run_step(
            name="editorial_feeds",
            command=[
                "python3",
                str(GENERATE_FEEDS),
                "--app",
                str(run_input_catalog),
                "--out-dir",
                str(artifacts_dir),
                "--all-tag-match-counts-out",
                str(artifacts_dir / "all_tag_match_counts.json"),
            ],
            cwd=TOOL_ROOT,
            log_path=logs_dir / "editorial_feeds.log",
            step_index=4,
            step_total=step_total,
        )
    )

    workspace_assets_dir = workspace_dir / "JabaliApp" / "Assets"
    workspace_tmp_dir = workspace_dir / "tmp"
    ensure_dir(workspace_assets_dir)
    ensure_dir(workspace_tmp_dir)
    shutil.copy2(run_input_catalog, workspace_assets_dir / "app.json")
    shutil.copy2(BLUEPRINT_PATH, workspace_tmp_dir / "editorial_phase2_blueprint.json")
    print(f"[mobile-validate] prepared workspace assets dir: {workspace_assets_dir}", flush=True)
    print(f"[mobile-validate] prepared workspace tmp dir: {workspace_tmp_dir}", flush=True)

    executed_steps.append(
        run_step(
            name="editorial_candidates",
            command=[
                "python3",
                str(GENERATE_CANDIDATES),
                *(["--screenshots-cleanup"] if args.screenshots_cleanup else []),
            ],
            cwd=workspace_dir,
            log_path=logs_dir / "editorial_candidates.log",
            step_index=5,
            step_total=step_total,
        )
    )
    shutil.copy2(workspace_tmp_dir / "editorial_phase3_candidates.json", artifacts_dir / "editorial_phase3_candidates.json")
    print(
        f"[mobile-validate] copied editorial candidates to {artifacts_dir / 'editorial_phase3_candidates.json'}",
        flush=True,
    )

    executed_steps.append(
        run_step(
            name="editorial_layouts",
            command=[
                "python3",
                str(GENERATE_LAYOUTS),
                "--candidates",
                str(artifacts_dir / "editorial_phase3_candidates.json"),
                "--out",
                str(artifacts_dir / "editorial_layouts.json"),
            ],
            cwd=TOOL_ROOT,
            log_path=logs_dir / "editorial_layouts.log",
            step_index=6,
            step_total=step_total,
        )
    )

    comparisons: dict[str, Any] = {}
    changed: list[str] = []
    unchanged: list[str] = []
    missing_generated: list[str] = []
    missing_current: list[str] = []

    compare_root = args.compare_root.resolve()
    print(f"[mobile-validate] starting artifact comparison against {compare_root}...", flush=True)
    for artifact_name in ARTIFACT_FILENAMES:
        current_path = compare_root / artifact_name
        generated_path = artifacts_dir / artifact_name
        comparison = compare_artifact(current_path, generated_path)
        comparisons[artifact_name] = comparison
        status = comparison["status"]
        print(f"[mobile-validate] comparison {artifact_name}: {status}", flush=True)
        if status == "changed":
            changed.append(artifact_name)
        elif status == "unchanged":
            unchanged.append(artifact_name)
        elif status == "missing-generated":
            missing_generated.append(artifact_name)
        elif status == "missing-current":
            missing_current.append(artifact_name)

    deployed = False
    if args.deploy:
        if missing_generated:
            raise RuntimeError("Cannot deploy because some generated artifacts are missing")
        for artifact_name in ARTIFACT_FILENAMES:
            shutil.copy2(artifacts_dir / artifact_name, compare_root / artifact_name)
        deployed = True

    summary = {
        "timestamp": timestamp,
        "input_catalog": str(input_path),
        "run_input_catalog": str(run_input_catalog),
        "run_dir": str(run_dir),
        "artifacts_dir": str(artifacts_dir),
        "deploy_requested": bool(args.deploy),
        "deployed": deployed,
        "compare_root": str(compare_root),
        "changed_artifacts": changed,
        "unchanged_artifacts": unchanged,
        "missing_generated_artifacts": missing_generated,
        "missing_current_artifacts": missing_current,
        "steps": [step.__dict__ for step in executed_steps],
        "comparisons": comparisons,
    }

    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    summary_lines = [
        f"# Mobile Artifact Validation Run {timestamp}",
        "",
        f"- Input catalog: `{input_path}`",
        f"- Run directory: `{run_dir}`",
        f"- Artifacts directory: `{artifacts_dir}`",
        f"- Deploy requested: `{args.deploy}`",
        f"- Deployed: `{deployed}`",
        f"- Compare root: `{compare_root}`",
        "",
        "## Comparison Result",
        "",
        f"- Changed artifacts: **{len(changed)}**",
        f"- Unchanged artifacts: **{len(unchanged)}**",
        f"- Missing generated artifacts: **{len(missing_generated)}**",
        f"- Missing current artifacts: **{len(missing_current)}**",
        "",
        "### Changed",
    ]
    summary_lines.extend([f"- `{name}`" for name in changed] or ["- none"])
    summary_lines.extend(["", "### Unchanged"])
    summary_lines.extend([f"- `{name}`" for name in unchanged] or ["- none"])
    summary_lines.extend(["", "### Missing Generated"])
    summary_lines.extend([f"- `{name}`" for name in missing_generated] or ["- none"])
    summary_lines.extend(["", "### Missing Current"])
    summary_lines.extend([f"- `{name}`" for name in missing_current] or ["- none"])

    (run_dir / "summary.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())