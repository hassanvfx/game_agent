from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RUNS_DIR = ROOT / "tools" / "game_refactoring" / "runs"


def extract_remix_prompt(run_dir: Path) -> str | None:
    run_state_path = run_dir / "run_state.json"
    if run_state_path.exists():
        payload = json.loads(run_state_path.read_text(encoding="utf-8"))
        remix_prompt = payload.get("remix_prompt")
        if isinstance(remix_prompt, str) and remix_prompt.strip():
            return remix_prompt.strip()

    invocation_path = run_dir / "batch_launcher_invocation.json"
    if invocation_path.exists():
        payload = json.loads(invocation_path.read_text(encoding="utf-8"))
        command = payload.get("command")
        if isinstance(command, list):
            for index, token in enumerate(command[:-1]):
                if token == "--remix-prompt":
                    value = command[index + 1]
                    if isinstance(value, str) and value.strip():
                        return value.strip()
    return None


def main() -> None:
    candidates: list[tuple[float, Path]] = []
    for path in RUNS_DIR.rglob("input_manifest.json"):
        try:
            stat = path.stat()
        except FileNotFoundError:
            continue
        candidates.append((stat.st_mtime, path))

    if not candidates:
        raise SystemExit("No input_manifest.json files found under tools/game_refactoring/runs")

    _, latest = max(candidates, key=lambda item: item[0])
    payload = json.loads(latest.read_text(encoding="utf-8"))
    games = payload.get("games") or []
    workflow: dict[str, Any] = payload.get("workflow") or {}
    run_dir = latest.parent

    print(
        json.dumps(
            {
                "latest_manifest": str(latest),
                "run_dir": str(run_dir),
                "workflow_id": workflow.get("id"),
                "source_games_manifest": workflow.get("games_manifest_source"),
                "remix_prompt": extract_remix_prompt(run_dir),
                "game_count": len(games),
                "first_game_id": games[0].get("game_id") if games else None,
                "first_game_display_name": games[0].get("display_name") if games else None,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()