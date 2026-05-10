#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNS_ROOT = Path("/Volumes/HDD2026/output")
LEDGER_PATH = ROOT / "tmp/retry_manifests/known_runs.json"
OUT_DIR = ROOT / "tmp/retry_manifests"
WORKFLOW_SCRIPT = ROOT / "tools/game_refactoring/scripts/game_workflow.py"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt-key")
    parser.add_argument("--run-name")
    parser.add_argument("--json-output", action="store_true")
    return parser.parse_args()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_game_id(entry):
    if isinstance(entry, str):
        return entry
    if isinstance(entry, dict):
        return entry.get("game_id") or entry.get("id") or entry.get("name")
    return None


def classify_run(run_dir: Path) -> dict:
    input_manifest = load_json(run_dir / "input_manifest.json")
    dashboard = load_json(run_dir / "dashboard" / "dashboard_data.json")
    run_state = load_json(run_dir / "run_state.json")

    manifest_games = input_manifest.get("games", [])
    manifest_by_id = {}
    for game in manifest_games:
        game_id = normalize_game_id(game)
        if game_id:
            manifest_by_id[game_id] = game

    manifest_ids = set(manifest_by_id.keys())

    completed_ids = set()
    output_dir = run_dir / "output"
    if output_dir.exists():
        for child in output_dir.iterdir():
            if child.is_dir():
                completed_ids.add(child.name)

    failed_ids = set()
    dashboard_games = dashboard.get("games", [])
    for game in dashboard_games:
        if not isinstance(game, dict):
            continue
        game_id = normalize_game_id(game)
        if not game_id:
            continue
        status = str(game.get("status") or game.get("state") or "").lower()
        if "fail" in status or "error" in status:
            failed_ids.add(game_id)

    pending_ids = set(run_state.get("pending_game_ids", []))
    active_ids = set(run_state.get("active_game_ids", []))
    unresolved_state_ids = pending_ids | active_ids

    missing_ids = manifest_ids - completed_ids - failed_ids - unresolved_state_ids
    retry_ids = (failed_ids | unresolved_state_ids | missing_ids) - completed_ids

    return {
        "run_dir": str(run_dir),
        "manifest_by_id": manifest_by_id,
        "manifest_ids": manifest_ids,
        "completed_ids": completed_ids,
        "failed_ids": failed_ids,
        "pending_ids": pending_ids,
        "active_ids": active_ids,
        "missing_ids": missing_ids,
        "retry_ids": retry_ids,
    }


def consolidate_family(family: dict) -> dict:
    prompt_key = family["prompt_key"]
    remix_prompt = family["remix_prompt"]
    run_names = family["runs"]

    union_manifest_by_id = {}
    resolved_ids = set()
    unresolved_ids = set()
    run_summaries = []

    for run_name in run_names:
        run_dir = RUNS_ROOT / run_name
        classified = classify_run(run_dir)

        for game_id, game_entry in classified["manifest_by_id"].items():
            union_manifest_by_id.setdefault(game_id, game_entry)

        resolved_ids |= classified["completed_ids"]
        unresolved_ids |= classified["retry_ids"]

        run_summaries.append(
            {
                "run_name": run_name,
                "completed": len(classified["completed_ids"]),
                "failed": len(classified["failed_ids"]),
                "pending": len(classified["pending_ids"]),
                "active": len(classified["active_ids"]),
                "missing": len(classified["missing_ids"]),
                "retry": len(classified["retry_ids"]),
            }
        )

    final_retry_ids = sorted(unresolved_ids - resolved_ids)
    retry_games = [union_manifest_by_id[game_id] for game_id in final_retry_ids if game_id in union_manifest_by_id]

    retry_manifest = {
        "prompt_key": prompt_key,
        "remix_prompt": remix_prompt,
        "source_runs": run_names,
        "retry_game_ids": final_retry_ids,
        "games": retry_games,
    }

    manifest_path = OUT_DIR / f"{prompt_key}_consolidated_retry_manifest.json"
    manifest_path.write_text(json.dumps(retry_manifest, indent=2) + "\n", encoding="utf-8")

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_id = f"run_v4_{prompt_key}_retry2_{timestamp}"
    launch_command = (
        f'python3 tools/game_refactoring/scripts/game_workflow.py --json --id creative_remix_v4 '
        f'--games-manifest-source {manifest_path.relative_to(ROOT)} '
        f'--run-id {run_id} --runs-root /Volumes/HDD2026/output --source-mode copy '
        f'--pipeline v2 --model gpt-5.5 --agent-timeout 3600 --max-concurrency 1 '
        f'--poll-seconds 5 --stale-heartbeat-seconds 900 --remix-prompt "{remix_prompt}"'
    )

    return {
        "prompt_key": prompt_key,
        "remix_prompt": remix_prompt,
        "manifest_path": str(manifest_path.relative_to(ROOT)),
        "retry_count": len(final_retry_ids),
        "retry_game_ids": final_retry_ids,
        "run_summaries": run_summaries,
        "launch_command": launch_command,
    }


def select_families(families: list[dict], prompt_key: str | None, run_name: str | None) -> list[dict]:
    selected = families
    if prompt_key:
        selected = [family for family in selected if family.get("prompt_key") == prompt_key]
    if run_name:
        selected = [family for family in selected if run_name in family.get("runs", [])]
    return selected


def main() -> int:
    args = parse_args()

    ledger = load_json(LEDGER_PATH)
    families = ledger.get("run_families", [])
    selected_families = select_families(families, args.prompt_key, args.run_name)

    results = []
    for family in selected_families:
        results.append(consolidate_family(family))

    payload = {
        "selected_prompt_key": args.prompt_key,
        "selected_run_name": args.run_name,
        "results": results,
    }

    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())