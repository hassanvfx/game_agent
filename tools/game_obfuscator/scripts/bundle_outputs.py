#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

from orchestration_state import load_json, recompute_run_state, update_game_state, write_json


CSS_LINK_RE = re.compile(r'<link[^>]+rel=["\']stylesheet["\'][^>]+href=["\']([^"\']+)["\'][^>]*>', re.IGNORECASE)
SCRIPT_SRC_RE = re.compile(r'<script[^>]+src=["\']([^"\']+)["\'][^>]*>\s*</script>', re.IGNORECASE)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bundle rewritten Game Obfuscator outputs into pre-obfuscation HTML.")
    parser.add_argument("--run-dir", required=True, help="Path to a Game Obfuscator run directory.")
    return parser.parse_args()


def inline_styles(html: str, output_dir: Path) -> tuple[str, list[str]]:
    inlined_files: list[str] = []

    def replacer(match: re.Match[str]) -> str:
        href = match.group(1)
        if href.startswith(("http://", "https://", "data:")):
            return match.group(0)

        css_path = output_dir / href
        if not css_path.exists() or not css_path.is_file():
            return match.group(0)

        css_text = css_path.read_text(encoding="utf-8", errors="ignore")
        inlined_files.append(href)
        return f"<style data-source=\"{href}\">\n{css_text}\n</style>"

    return CSS_LINK_RE.sub(replacer, html), inlined_files


def inline_scripts(html: str, output_dir: Path) -> tuple[str, list[str]]:
    inlined_files: list[str] = []

    def replacer(match: re.Match[str]) -> str:
        src = match.group(1)
        if src.startswith(("http://", "https://", "data:")):
            return match.group(0)

        js_path = output_dir / src
        if not js_path.exists() or not js_path.is_file():
            return match.group(0)

        js_text = js_path.read_text(encoding="utf-8", errors="ignore")
        inlined_files.append(src)
        return f"<script data-source=\"{src}\">\n{js_text}\n</script>"

    return SCRIPT_SRC_RE.sub(replacer, html), inlined_files


def snapshot_prebundle_site(output_dir: Path, artifacts_dir: Path) -> Path:
    snapshot_dir = artifacts_dir / "pre_bundle_site"
    if snapshot_dir.exists():
        shutil.rmtree(snapshot_dir)

    def ignore_filter(directory: str, names: list[str]) -> set[str]:
        ignored: set[str] = set()
        if Path(directory).resolve() == output_dir.resolve() and "artifacts" in names:
            ignored.add("artifacts")
        return ignored

    shutil.copytree(output_dir, snapshot_dir, ignore=ignore_filter)
    return snapshot_dir


def bundle_game_output(game_state: dict) -> dict:
    output_dir = Path(game_state["output_path"])
    artifacts_dir = Path(game_state["artifacts_path"])
    index_path = output_dir / "index.html"
    if not index_path.exists():
        raise FileNotFoundError(f"Missing rewritten index.html: {index_path}")

    prebundle_snapshot_dir = snapshot_prebundle_site(output_dir, artifacts_dir)
    html = index_path.read_text(encoding="utf-8", errors="ignore")
    html, inlined_css_files = inline_styles(html, output_dir)
    html, inlined_js_files = inline_scripts(html, output_dir)

    bundled_path = artifacts_dir / "index.pre_obfuscation.html"
    bundled_path.write_text(html, encoding="utf-8")

    bundle_report = {
        "generated_at": utc_now(),
        "game_id": game_state["game_id"],
        "source_index": str(index_path),
        "bundled_html": str(bundled_path),
        "inlined_css_files": inlined_css_files,
        "inlined_js_files": inlined_js_files,
        "pre_bundle_site": str(prebundle_snapshot_dir),
        "emoji_assets_remain_external": True,
    }
    write_json(artifacts_dir / "bundle_report.json", bundle_report)
    return bundle_report


def main() -> None:
    args = parse_args()
    run_dir = Path(args.run_dir).resolve()
    manifest = load_json(run_dir / "input_manifest.json")
    run_state = load_json(run_dir / "run_state.json")
    recompute_run_state(run_dir, current_phase="bundle_started", note="Bundle stage started.")

    bundled_games = 0
    bundle_failed = 0

    for game in manifest.get("games", []):
        game_id = game["game_id"]
        game_state_path = run_dir / "games" / game_id / "game_state.json"
        game_state = load_json(game_state_path)

        update_game_state(
            run_dir,
            game_id,
            status="running",
            phase="bundle_started",
            last_error=None,
            mark_started=True,
            heartbeat=True,
            progress=True,
        )

        try:
            bundle_report = bundle_game_output(game_state)
        except FileNotFoundError as exc:
            update_game_state(
                run_dir,
                game_id,
                status="failed",
                phase="bundle_failed",
                last_error=str(exc),
                heartbeat=True,
                progress=True,
            )
            bundle_failed += 1
            continue

        bundled_games += 1
        artifacts_dir = Path(game_state["artifacts_path"])
        update_game_state(
            run_dir,
            game_id,
            status="ready",
            phase="bundle_created",
            last_error=None,
            heartbeat=True,
            progress=True,
            artifacts={
                "bundle_report": str(artifacts_dir / "bundle_report.json"),
                "pre_bundle_site": str(artifacts_dir / "pre_bundle_site"),
                "pre_obfuscation_html": str(artifacts_dir / "index.pre_obfuscation.html"),
            },
        )

    run_state["games_bundled"] = bundled_games
    run_state["games_bundle_failed"] = bundle_failed
    run_state["current_phase"] = "bundle_complete"
    run_state["status"] = "ready_for_obfuscation" if bundle_failed == 0 else "failed"
    run_state["updated_at"] = utc_now()
    run_state.setdefault("notes", []).append("Pre-obfuscation bundling completed.")
    write_json(run_dir / "run_state.json", run_state)
    recompute_run_state(run_dir, current_phase="bundle_complete")

    print(run_dir)


if __name__ == "__main__":
    main()