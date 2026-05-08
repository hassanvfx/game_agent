#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
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
    parser = argparse.ArgumentParser(description="Build a downloader run dashboard.")
    parser.add_argument("--run-id", required=True, help="Run id under runs/.")
    return parser.parse_args()


def collect_games(run_dir: Path) -> list[dict]:
    games_dir = run_dir / "games"
    items: list[dict] = []
    if not games_dir.exists():
        return items

    for game_dir in sorted(path for path in games_dir.iterdir() if path.is_dir()):
        status_path = game_dir / "status.txt"
        history_path = game_dir / "history.jsonl"
        replay_dir = game_dir / "replay"
        source_path = game_dir / "source.json"
        attempt_dir = game_dir / "attempts"

        latest_replay = None
        if replay_dir.exists():
            replay_attempts = sorted(path for path in replay_dir.iterdir() if path.is_dir())
            if replay_attempts:
                candidate = replay_attempts[-1] / "index.html"
                latest_replay = str(candidate) if candidate.exists() else None

        source = load_json(source_path) if source_path.exists() else {}
        history_count = 0
        if history_path.exists():
            history_count = sum(1 for _ in history_path.open("r", encoding="utf-8"))

        attempt_count = 0
        if attempt_dir.exists():
            attempt_count = sum(1 for path in attempt_dir.iterdir() if path.is_dir())

        items.append(
            {
                "game_key": game_dir.name,
                "game_id": source.get("game_id"),
                "url": source.get("url"),
                "status": status_path.read_text(encoding="utf-8").strip() if status_path.exists() else "unknown",
                "history_count": history_count,
                "attempt_count": attempt_count,
                "latest_replay_index": latest_replay,
            }
        )
    return items


def main() -> int:
    args = parse_args()
    root = Path(__file__).resolve().parents[1]
    run_dir = root / "runs" / args.run_id
    dashboard_dir = run_dir / "dashboard"
    dashboard_dir.mkdir(parents=True, exist_ok=True)

    progress = load_json(run_dir / "reports" / "progress.json")
    games = collect_games(run_dir)

    payload = {
        "generated_at": utc_now(),
        "run_id": args.run_id,
        "run_dir": str(run_dir),
        "progress": progress,
        "games": games,
    }
    write_json(dashboard_dir / "dashboard_data.json", payload)

    html = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Game Downloader Dashboard</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body { font-family: Arial, sans-serif; margin: 24px; background: #0b1220; color: #e5e7eb; }
    .card { background: #111827; border: 1px solid #374151; border-radius: 12px; padding: 16px; margin-bottom: 16px; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; }
    .stat { background: #1f2937; border-radius: 12px; padding: 12px; }
    .muted { color: #9ca3af; }
    a { color: #60a5fa; }
    code { background: #0f172a; padding: 2px 6px; border-radius: 6px; }
  </style>
</head>
<body>
  <h1>Game Downloader Dashboard</h1>
  <div class="card">
    <p><strong>Run:</strong> <code id="runId"></code></p>
    <p class="muted">Queue, attempt, and replay status for the extracted downloader package.</p>
  </div>
  <div id="summary" class="grid"></div>
  <div id="games"></div>
  <script>
    async function main() {
      const res = await fetch('./dashboard_data.json');
      const data = await res.json();
      document.getElementById('runId').textContent = data.run_id;

      const queueCounts = data.progress.queue_counts || {};
      const summary = document.getElementById('summary');
      for (const [key, value] of Object.entries(queueCounts)) {
        const node = document.createElement('div');
        node.className = 'stat';
        node.innerHTML = `<div class="muted">${key}</div><div style="font-size:24px;font-weight:bold">${value}</div>`;
        summary.appendChild(node);
      }

      const games = document.getElementById('games');
      for (const game of data.games) {
        const node = document.createElement('div');
        node.className = 'card';
        node.innerHTML = `
          <h3>${game.game_key}</h3>
          <p><strong>Status:</strong> ${game.status}</p>
          <p><strong>Attempts:</strong> ${game.attempt_count}</p>
          <p><strong>History Entries:</strong> ${game.history_count}</p>
          <p><strong>URL:</strong> <code>${game.url || ''}</code></p>
          <p><strong>Replay:</strong> ${game.latest_replay_index ? `<a href="../games/${game.game_key}/replay/attempt_0001/index.html">open</a>` : 'none'}</p>
        `;
        games.appendChild(node);
      }
    }
    main();
  </script>
</body>
</html>
"""
    (dashboard_dir / "index.html").write_text(html, encoding="utf-8")
    print(dashboard_dir / "index.html")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
