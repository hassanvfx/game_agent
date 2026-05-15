from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
OBF_ROOT = REPO_ROOT / "tools" / "game_obfuscator"
RUN_ID = "run_game_obfuscator_raw_random4_baseline"
RUN_DIR = OBF_ROOT / "runs" / RUN_ID


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def existing_relpaths(root: Path) -> list[str]:
    if not root.exists():
        return []
    return sorted(path.relative_to(root).as_posix() for path in root.rglob("*"))


def main() -> None:
    run_state_path = RUN_DIR / "run_state.json"
    manifest_path = RUN_DIR / "input_manifest.json"
    if not run_state_path.exists():
        raise SystemExit(f"Missing run state: {run_state_path}")
    if not manifest_path.exists():
        raise SystemExit(f"Missing input manifest: {manifest_path}")

    run_state = load_json(run_state_path)
    manifest = load_json(manifest_path)

    summary: dict[str, object] = {
        "run_dir": str(RUN_DIR.resolve()),
        "status": run_state.get("status"),
        "current_phase": run_state.get("current_phase"),
        "games_total": run_state.get("games_total"),
        "games_succeeded": run_state.get("games_succeeded"),
        "games_failed": run_state.get("games_failed"),
        "games": [],
    }

    games_summary: list[dict[str, object]] = []

    for game in manifest.get("games", []):
        entry_key = game["entry_key"]
        game_state_path = RUN_DIR / "games" / entry_key / "game_state.json"
        game_state = load_json(game_state_path)
        output_dir = Path(game_state["output_path"])
        artifacts_dir = Path(game_state["artifacts_path"])
        report_path = artifacts_dir / "simple_obfuscation_report.json"
        report = load_json(report_path) if report_path.exists() else {}

        games_summary.append(
            {
                "entry_key": entry_key,
                "game_id": game_state.get("game_id"),
                "status": game_state.get("status"),
                "current_phase": game_state.get("current_phase"),
                "source_path": game_state.get("source_path"),
                "output_path": game_state.get("output_path"),
                "last_error": game_state.get("last_error"),
                "top_level_output_entries": existing_relpaths(output_dir),
                "preserved_surface_folders": report.get("preserved_surface_folders"),
                "kept_files": report.get("prune_report", {}).get("kept_files", []),
                "removed_files_count": len(report.get("prune_report", {}).get("removed_files", [])),
                "removed_dirs_count": len(report.get("prune_report", {}).get("removed_dirs", [])),
                "html_files": report.get("transformer_report", {}).get("html_files", []),
                "css_files": report.get("transformer_report", {}).get("css_files", []),
                "js_files": report.get("transformer_report", {}).get("js_files", []),
            }
        )

    summary["games"] = games_summary
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()