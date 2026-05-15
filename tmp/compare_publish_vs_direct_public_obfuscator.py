
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_RUN_DIR = REPO_ROOT / "tools" / "game_obfuscator" / "runs" / "run_game_obfuscator_raw_random4_baseline"
PUBLISH_RUN_DIR = REPO_ROOT / "tools" / "game_obfuscator" / "runs" / "run_game_obfuscator_20260515T004641Z"
DIRECT_PUBLIC_RUN_DIR = REPO_ROOT / "tools" / "game_obfuscator" / "runs" / "run_game_obfuscator_publish_public_random4_direct"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_game_report(run_dir: Path) -> dict[str, dict]:
    manifest = load_json(run_dir / "input_manifest.json")
    reports: dict[str, dict] = {}
    for game in manifest.get("games", []):
        entry_key = game["entry_key"]
        report_path = run_dir / "games" / entry_key / "game_state.json"
        game_state = load_json(report_path)
        simple_report = load_json(Path(game_state["artifacts_path"]) / "simple_obfuscation_report.json")
        reports[game["game_id"]] = {
            "entry_key": entry_key,
            "source_path": game.get("source_path"),
            "output_path": game_state["output_path"],
            "kept_files": simple_report.get("prune_report", {}).get("kept_files", []),
            "removed_files_count": len(simple_report.get("prune_report", {}).get("removed_files", [])),
            "removed_dirs_count": len(simple_report.get("prune_report", {}).get("removed_dirs", [])),
            "html_files": simple_report.get("transformer_report", {}).get("html_files", []),
            "css_files": simple_report.get("transformer_report", {}).get("css_files", []),
            "js_files": simple_report.get("transformer_report", {}).get("js_files", []),
            "preserved_surface_folders": simple_report.get("preserved_surface_folders", []),
        }
    return reports


def simplify(report: dict) -> dict:
    return {
        "kept_files": report["kept_files"],
        "removed_files_count": report["removed_files_count"],
        "removed_dirs_count": report["removed_dirs_count"],
        "html_inline_transforms": [
            [item.get("transform"), item.get("mode"), item.get("reason")]
            for html in report["html_files"]
            for item in html.get("inline_scripts", [])
        ],
        "css_paths": [item.get("path") for item in report["css_files"]],
        "js_paths": [item.get("path") for item in report["js_files"]],
        "js_sizes": [[item.get("path"), item.get("original_bytes"), item.get("transformed_bytes")] for item in report["js_files"]],
    }


def main() -> None:
    raw_reports = load_game_report(RAW_RUN_DIR)
    publish_reports = load_game_report(PUBLISH_RUN_DIR)
    direct_reports = load_game_report(DIRECT_PUBLIC_RUN_DIR)

    comparison = {}
    for game_id, raw_report in raw_reports.items():
        publish_report = publish_reports[game_id]
        direct_report = direct_reports[game_id]
        comparison[game_id] = {
            "publish_matches_direct_public": simplify(publish_report) == simplify(direct_report),
            "raw_matches_publish": simplify(raw_report) == simplify(publish_report),
            "raw_source_path": raw_report["source_path"],
            "publish_source_path": publish_report["source_path"],
            "direct_public_source_path": direct_report["source_path"],
            "raw": simplify(raw_report),
            "publish": simplify(publish_report),
            "direct_public": simplify(direct_report),
        }

    print(json.dumps(comparison, indent=2))


if __name__ == "__main__":
    main()