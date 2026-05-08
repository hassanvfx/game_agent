#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Apply staged minification/obfuscation to bundled outputs.")
    parser.add_argument("--run-dir", required=True, help="Path to a Game Obfuscator run directory.")
    parser.add_argument(
        "--profile",
        choices=["safe", "minify", "mangle", "max"],
        default="safe",
        help="Obfuscation strength profile.",
    )
    return parser.parse_args()


def run_minifier(input_path: Path, output_path: Path, profile: str) -> None:
    command = [
        "node",
        "scripts/minify_html.js",
        str(input_path),
        str(output_path),
        profile,
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "Unknown minifier failure")


def obfuscate_with_profile(pre_obfuscation_path: Path, minified_artifact_path: Path, obfuscated_artifact_path: Path, profile: str) -> tuple[str, str]:
    source_html = pre_obfuscation_path.read_text(encoding="utf-8", errors="ignore")

    if profile == "safe":
        minified_html = source_html
        obfuscated_html = source_html
        minified_artifact_path.write_text(minified_html, encoding="utf-8")
        obfuscated_artifact_path.write_text(obfuscated_html, encoding="utf-8")
        return minified_html, obfuscated_html

    run_minifier(pre_obfuscation_path, minified_artifact_path, "minify")
    minified_html = minified_artifact_path.read_text(encoding="utf-8", errors="ignore")

    if profile == "minify":
        obfuscated_html = minified_html
        obfuscated_artifact_path.write_text(obfuscated_html, encoding="utf-8")
        return minified_html, obfuscated_html

    run_minifier(pre_obfuscation_path, obfuscated_artifact_path, profile)
    obfuscated_html = obfuscated_artifact_path.read_text(encoding="utf-8", errors="ignore")
    return minified_html, obfuscated_html


def obfuscate_game_output(game_state: dict, profile: str) -> dict:
    artifacts_dir = Path(game_state["artifacts_path"])
    pre_obfuscation_path = artifacts_dir / "index.pre_obfuscation.html"
    if not pre_obfuscation_path.exists():
        raise FileNotFoundError(f"Missing pre-obfuscation HTML: {pre_obfuscation_path}")

    source_html = pre_obfuscation_path.read_text(encoding="utf-8", errors="ignore")
    minified_artifact_path = artifacts_dir / "index.minified.html"
    obfuscated_artifact_path = artifacts_dir / "index.obfuscated.html"

    attempted_profiles: list[str] = []
    selected_profile = profile

    if profile == "max":
        for candidate in ["max", "mangle", "minify", "safe"]:
            attempted_profiles.append(candidate)
            try:
                minified_html, obfuscated_html = obfuscate_with_profile(
                    pre_obfuscation_path,
                    minified_artifact_path,
                    obfuscated_artifact_path,
                    candidate,
                )
                selected_profile = candidate
                break
            except RuntimeError:
                continue
        else:
            raise RuntimeError("All obfuscation profiles failed during generation")
    else:
        attempted_profiles.append(profile)
        minified_html, obfuscated_html = obfuscate_with_profile(
            pre_obfuscation_path,
            minified_artifact_path,
            obfuscated_artifact_path,
            profile,
        )

    final_runtime_path = Path(game_state["output_path"]) / "index.html"
    final_runtime_path.write_text(obfuscated_html, encoding="utf-8")

    obfuscation_report = {
        "generated_at": utc_now(),
        "game_id": game_state["game_id"],
        "source_file": str(pre_obfuscation_path),
        "minified_artifact": str(minified_artifact_path),
        "obfuscated_artifact": str(obfuscated_artifact_path),
        "runtime_entrypoint": str(final_runtime_path),
        "requested_profile": profile,
        "selected_profile": selected_profile,
        "attempted_profiles": attempted_profiles,
        "source_size_bytes": len(source_html.encode("utf-8")),
        "minified_size_bytes": len(minified_html.encode("utf-8")),
        "obfuscated_size_bytes": len(obfuscated_html.encode("utf-8")),
        "transforms": {
            "safe_profile_preserves_source": selected_profile == "safe",
            "minified_artifact_emitted": True,
            "js_symbol_mangling_enabled": selected_profile in {"mangle", "max"},
            "strongest_first_enabled": profile == "max",
        },
    }

    write_json(artifacts_dir / "obfuscation_report.json", obfuscation_report)
    return obfuscation_report


def main() -> None:
    args = parse_args()
    run_dir = Path(args.run_dir).resolve()
    manifest = load_json(run_dir / "input_manifest.json")
    run_state = load_json(run_dir / "run_state.json")

    obfuscated_games = 0
    obfuscation_failed = 0

    for game in manifest.get("games", []):
        game_id = game["game_id"]
        game_state_path = run_dir / "games" / game_id / "game_state.json"
        game_state = load_json(game_state_path)

        try:
            obfuscate_game_output(game_state, args.profile)
        except (FileNotFoundError, RuntimeError) as exc:
            game_state["status"] = "failed"
            game_state["current_phase"] = "obfuscation_failed"
            game_state["last_error"] = str(exc)
            game_state["updated_at"] = utc_now()
            write_json(game_state_path, game_state)
            obfuscation_failed += 1
            continue

        obfuscated_games += 1
        artifacts_dir = Path(game_state["artifacts_path"])
        game_state["status"] = "obfuscated"
        game_state["current_phase"] = "obfuscation_complete"
        game_state["last_error"] = None
        game_state["updated_at"] = utc_now()
        game_state["artifacts"] = {
            **game_state.get("artifacts", {}),
            "obfuscation_report": str(artifacts_dir / "obfuscation_report.json"),
            "minified_html": str(artifacts_dir / "index.minified.html"),
            "obfuscated_html": str(artifacts_dir / "index.obfuscated.html"),
        }
        write_json(game_state_path, game_state)

    run_state["games_obfuscated"] = obfuscated_games
    run_state["games_obfuscation_failed"] = obfuscation_failed
    run_state["current_phase"] = "obfuscation_complete"
    run_state["status"] = "ready_for_verification" if obfuscation_failed == 0 else "failed"
    run_state["updated_at"] = utc_now()
    run_state.setdefault("notes", []).append(f"Obfuscation completed with profile '{args.profile}'.")
    write_json(run_dir / "run_state.json", run_state)

    print(run_dir)


if __name__ == "__main__":
    main()