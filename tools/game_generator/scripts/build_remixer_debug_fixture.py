#!/usr/bin/env python3
"""Build plain-list debug fixtures for remixer export vs matcher URLs."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MATCHER_ROOT = ROOT.parent / "game_matcher"
DEFAULT_EXPORT_ROOT = (
    ROOT.parent
    / "game_remixer"
    / "exports"
    / "export_top1000_prod_attempt_0001_reconciled_20260426T224528Z"
)
DEFAULT_OUT_DIR = ROOT / "debug" / "remixer_fixture"


def write_text_lines(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def slugify(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "item"


def parse_matcher_output(stdout: str) -> list[dict[str, Any]]:
    decoder = json.JSONDecoder()
    text = stdout.strip()
    if not text:
        raise ValueError("matcher stdout was empty")
    payload = None
    last_error: Exception | None = None
    for start in range(len(text)):
        if text[start] not in "[{":
            continue
        try:
            candidate, _ = decoder.raw_decode(text[start:])
            payload = candidate
            break
        except json.JSONDecodeError as exc:
            last_error = exc
    if payload is None:
        raise ValueError(f"unable to decode matcher JSON from stdout: {last_error}") from last_error

    if isinstance(payload, dict):
        for key in ("results", "matches", "items"):
            value = payload.get(key)
            if isinstance(value, list):
                return value
        raise ValueError("matcher JSON object did not contain results/matches/items list")
    if isinstance(payload, list):
        return payload
    raise ValueError("matcher JSON payload was neither list nor object-with-results")


def extract_game_id(item: dict[str, Any]) -> str:
    for key in ("game_id", "id", "gameId"):
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
        if isinstance(value, int):
            return str(value)
    raise ValueError(f"match item missing game id: {item}")


def extract_url(item: dict[str, Any]) -> str:
    for key in ("url", "game_url", "gameUrl", "source_url", "sourceUrl"):
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    raise ValueError(f"match item missing url: {item}")


def infer_keys(url: str, game_id: str) -> dict[str, str | None]:
    path = urlparse(url).path
    minigame_match = re.search(r"/minigame/([^/]+)/index\.html$", path)
    if minigame_match:
        minigame_id = minigame_match.group(1)
        return {
            "priority_1_minigame_id": minigame_id,
            "priority_2_latest_html": None,
            "priority_3_game_id": f"game-{game_id}",
            "priority_4_slug": slugify(url),
        }

    latest_match = re.search(r"/([^/]*latest-[^/]*\.html)$", path)
    latest_value = latest_match.group(1).rsplit(".", 1)[0] if latest_match else None
    return {
        "priority_1_minigame_id": None,
        "priority_2_latest_html": latest_value,
        "priority_3_game_id": f"game-{game_id}",
        "priority_4_slug": slugify(url),
    }


def list_child_dirs(path: Path) -> list[str]:
    if not path.exists():
        return []
    return sorted(entry.name for entry in path.iterdir() if entry.is_dir())


def run_matcher(prompt: str, matcher_root: Path, limit: int) -> list[dict[str, Any]]:
    command = ["python3", "cli/game_matcher_cli.py", prompt, "--limit", str(limit)]
    completed = subprocess.run(command, cwd=str(matcher_root), capture_output=True, text=True)
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr or completed.stdout or "matcher command failed")
    return parse_matcher_output(completed.stdout)


def load_matches_from_json(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict) and "selected_matches" in payload:
        return payload["selected_matches"]
    if isinstance(payload, dict):
        for key in ("matches", "results", "items"):
            value = payload.get(key)
            if isinstance(value, list):
                return value
    if isinstance(payload, list):
        return payload
    raise ValueError(f"unsupported matcher json payload in {path}")


def normalize_matches(matches: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized = []
    for item in matches:
        game_id = extract_game_id(item)
        url = extract_url(item)
        inferred = infer_keys(url, game_id)
        normalized.append(
            {
                "game_id": game_id,
                "url": url,
                "name": str(item.get("name") or item.get("title") or game_id),
                "inferred_keys": inferred,
                "raw": item,
            }
        )
    return normalized


def build_url_to_inferred_game_id_rows(normalized_matches: list[dict[str, Any]]) -> list[dict[str, str | None]]:
    rows = []
    for match in normalized_matches:
        inferred = match["inferred_keys"]
        rows.append(
            {
                "game_id": match["game_id"],
                "url": match["url"],
                "inferred_game_id": inferred["priority_1_minigame_id"]
                or inferred["priority_2_latest_html"]
                or inferred["priority_3_game_id"]
                or inferred["priority_4_slug"],
            }
        )
    return rows


def build_report(
    normalized_matches: list[dict[str, Any]],
    output_keys: set[str],
    input_keys: set[str],
    export_root: Path,
) -> tuple[dict[str, Any], str]:
    report_rows = []
    text_lines = [
        f"Export root: {export_root}",
        f"Output folder count: {len(output_keys)}",
        f"Input folder count: {len(input_keys)}",
        "",
    ]

    for match in normalized_matches:
        inferred = match["inferred_keys"]
        key_rows = []
        text_lines.append(f"GAME_ID={match['game_id']}")
        text_lines.append(f"URL={match['url']}")
        for label in (
            "priority_1_minigame_id",
            "priority_2_latest_html",
            "priority_3_game_id",
            "priority_4_slug",
        ):
            value = inferred[label]
            if value is None:
                exists_output = False
                exists_input = False
                text_lines.append(f"  {label}: <none>")
            else:
                exists_output = value in output_keys
                exists_input = value in input_keys
                text_lines.append(
                    f"  {label}: {value} | exists_in_output={'yes' if exists_output else 'no'} "
                    f"| exists_in_input={'yes' if exists_input else 'no'}"
                )
            key_rows.append(
                {
                    "label": label,
                    "value": value,
                    "exists_in_output": exists_output,
                    "exists_in_input": exists_input,
                }
            )
        text_lines.append("")
        report_rows.append(
            {
                "game_id": match["game_id"],
                "url": match["url"],
                "name": match["name"],
                "key_checks": key_rows,
            }
        )

    report = {
        "export_root": str(export_root),
        "output_folder_count": len(output_keys),
        "input_folder_count": len(input_keys),
        "matches": report_rows,
    }
    return report, "\n".join(text_lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build debug fixtures for remixer export vs matcher URLs.")
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument("--prompt", help="Run matcher live with this prompt.")
    source_group.add_argument("--matcher-json", help="Load matches from a saved matcher JSON artifact.")
    parser.add_argument("--limit", type=int, default=20, help="Matcher limit when using --prompt.")
    parser.add_argument("--matcher-root", default=str(DEFAULT_MATCHER_ROOT), help="Path to game_matcher root.")
    parser.add_argument("--export-root", default=str(DEFAULT_EXPORT_ROOT), help="Path to remixer export root.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR), help="Output directory for debug fixture files.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    matcher_root = Path(args.matcher_root).resolve()
    export_root = Path(args.export_root).resolve()
    out_dir = Path(args.out_dir).resolve()
    output_dir = export_root / "output"
    input_dir = export_root / "input"

    if args.prompt:
        raw_matches = run_matcher(args.prompt, matcher_root, args.limit)
        write_json(out_dir / "matcher_raw_matches.json", raw_matches)
    else:
        raw_matches = load_matches_from_json(Path(args.matcher_json).resolve())
        write_json(out_dir / "matcher_raw_matches.json", raw_matches)

    normalized_matches = normalize_matches(raw_matches)
    output_keys = list_child_dirs(output_dir)
    input_keys = list_child_dirs(input_dir)
    url_to_inferred_rows = build_url_to_inferred_game_id_rows(normalized_matches)
    output_key_set = set(output_keys)
    inferred_game_ids = [row["inferred_game_id"] for row in url_to_inferred_rows if row["inferred_game_id"]]
    inferred_matches_in_output = [value for value in inferred_game_ids if value in output_key_set]

    write_text_lines(out_dir / "remixer_export_output_keys.txt", output_keys)
    write_text_lines(out_dir / "remixer_export_input_keys.txt", input_keys)
    write_text_lines(out_dir / "matcher_urls.txt", [item["url"] for item in normalized_matches])
    write_text_lines(out_dir / "matcher_game_ids.txt", [item["game_id"] for item in normalized_matches])
    write_json(out_dir / "matcher_normalized_matches.json", normalized_matches)
    write_json(out_dir / "url_to_inferred_game_id.json", url_to_inferred_rows)
    write_text_lines(
        out_dir / "url_to_inferred_game_id.txt",
        [
            f"{row['url']} => {row['inferred_game_id']} => output_match={'yes' if row['inferred_game_id'] in output_key_set else 'no'}"
            for row in url_to_inferred_rows
        ],
    )
    write_text_lines(out_dir / "inferred_game_ids.txt", [value for value in inferred_game_ids])
    write_text_lines(out_dir / "inferred_game_ids_found_in_output.txt", inferred_matches_in_output)

    report, report_text = build_report(normalized_matches, output_key_set, set(input_keys), export_root)
    write_json(out_dir / "matcher_inference_report.json", report)
    (out_dir / "matcher_inference_report.txt").write_text(report_text, encoding="utf-8")

    print(json.dumps({"out_dir": str(out_dir), "match_count": len(normalized_matches)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())