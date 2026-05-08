#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a run-local dashboard scaffold for Game Remixer.")
    parser.add_argument("--run-dir", required=True)
    return parser.parse_args()


def relative_url(path: Path, root: Path) -> str:
    try:
        return "/" + path.relative_to(root).as_posix()
    except ValueError:
        return path.resolve().as_uri()


def parse_utc(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def format_age_seconds(value: str | None, now: datetime) -> float | None:
    parsed = parse_utc(value)
    if parsed is None:
        return None
    return round(max(0.0, (now - parsed).total_seconds()), 1)


def current_job_state_path(run_dir: Path, game_id: str) -> Path:
    return run_dir / "games" / game_id / "attempts" / "attempt_0001" / "job_state.json"


def load_job_state(run_dir: Path, game_id: str) -> dict | None:
    path = current_job_state_path(run_dir, game_id)
    if not path.exists():
        return None
    return load_json(path)


def job_snapshot(job_state: dict | None, now: datetime) -> dict | None:
    if not job_state:
        return None
    heartbeat_at = job_state.get("heartbeat_at") or job_state.get("last_heartbeat_at")
    started_at = job_state.get("started_at")
    finished_at = job_state.get("finished_at")
    return {
        "job_id": job_state.get("job_id"),
        "job_type": job_state.get("job_type"),
        "status": job_state.get("status"),
        "attempt_number": job_state.get("attempt_number"),
        "started_at": started_at,
        "finished_at": finished_at,
        "heartbeat_at": heartbeat_at,
        "heartbeat_age_seconds": format_age_seconds(heartbeat_at, now),
        "runtime_age_seconds": format_age_seconds(started_at, now) if started_at and not finished_at else None,
        "failure_reason": job_state.get("failure_reason"),
        "result_path": job_state.get("result_path"),
        "stdout_path": job_state.get("stdout_path"),
        "stderr_path": job_state.get("stderr_path"),
    }


def main() -> None:
    args = parse_args()
    run_dir = Path(args.run_dir).resolve()
    run_state = load_json(run_dir / "run_state.json")
    manifest = load_json(run_dir / "input_manifest.json")
    now = datetime.now(timezone.utc)

    games_payload = []
    active_jobs = []
    heartbeat_missing_count = 0
    heartbeat_stale_count = 0

    for game in manifest.get("games", []):
        game_id = game["game_id"]
        game_state = load_json(run_dir / "games" / game_id / "game_state.json")
        job_state = load_job_state(run_dir, game_id)
        job = job_snapshot(job_state, now)

        input_dir = Path(game_state["input_mirror_path"])
        output_dir = Path(game_state["output_path"])
        input_index = input_dir / "index.html"
        output_index = output_dir / "index.html"

        if job and job["status"] == "running":
            active_jobs.append(
                {
                    "game_id": game_id,
                    "display_name": game_state.get("display_name"),
                    **job,
                }
            )
            if job["heartbeat_at"] is None:
                heartbeat_missing_count += 1
            elif job["heartbeat_age_seconds"] is not None and job["heartbeat_age_seconds"] > 60:
                heartbeat_stale_count += 1

        games_payload.append(
            {
                "game_id": game_id,
                "display_name": game_state.get("display_name"),
                "status": game_state["status"],
                "current_phase": game_state["current_phase"],
                "integrity_status": game_state.get("integrity_status"),
                "attempt_count": game_state.get("attempt_count"),
                "creative_status": game_state.get("creative_status"),
                "creative_phase": game_state.get("creative_phase"),
                "input_mirror_path": str(input_dir),
                "output_path": str(output_dir),
                "input_index_url": relative_url(input_index, ROOT) if input_index.exists() else None,
                "output_index_url": relative_url(output_index, ROOT) if output_index.exists() else None,
                "last_error": game_state.get("last_error"),
                "updated_at": game_state.get("updated_at"),
                "job": job,
            }
        )

    dashboard_payload = {
        "generated_at": utc_now(),
        "run": {
            "run_id": run_state["run_id"],
            "status": run_state["status"],
            "current_phase": run_state["current_phase"],
            "created_at": run_state.get("created_at"),
            "updated_at": run_state.get("updated_at"),
            "notes": run_state.get("notes", []),
        },
        "summary": {
            "games_total": run_state["games_total"],
            "games_mirrored": run_state["games_mirrored"],
            "games_integrity_passed": run_state["games_integrity_passed"],
            "games_integrity_failed": run_state["games_integrity_failed"],
            "games_transform_completed": run_state["games_transform_completed"],
            "games_transform_failed": run_state["games_transform_failed"],
            "games_running": sum(1 for game in games_payload if game["status"] == "running"),
            "games_completed": sum(1 for game in games_payload if game["status"] == "completed"),
            "games_failed": sum(1 for game in games_payload if game["status"] == "failed"),
            "active_jobs": len(active_jobs),
            "active_jobs_missing_heartbeat": heartbeat_missing_count,
            "active_jobs_stale_over_60s": heartbeat_stale_count,
        },
        "active_jobs": active_jobs,
        "games": games_payload,
    }

    dashboard_dir = run_dir / "dashboard"
    write_json(dashboard_dir / "dashboard_data.json", dashboard_payload)

    html = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Game Remixer Dashboard</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    :root {
      --bg: #0b1220;
      --panel: #111827;
      --panel-2: #1f2937;
      --text: #e5e7eb;
      --muted: #9ca3af;
      --border: #374151;
      --blue: #60a5fa;
      --green: #34d399;
      --yellow: #fbbf24;
      --red: #f87171;
      --purple: #a78bfa;
    }
    * { box-sizing: border-box; }
    body { font-family: Arial, sans-serif; margin: 24px; background: var(--bg); color: var(--text); }
    h1, h2, h3 { margin: 0 0 10px; }
    a { color: var(--blue); }
    code { background: #0f172a; padding: 2px 6px; border-radius: 6px; }
    .meta, .card, .stat, .note { background: var(--panel); border: 1px solid var(--border); border-radius: 12px; }
    .meta, .card { padding: 16px; margin-bottom: 16px; }
    .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 12px; margin-bottom: 16px; }
    .stat { padding: 14px; }
    .stat .label { color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: 0.08em; }
    .stat .value { font-size: 24px; margin-top: 6px; font-weight: bold; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(360px, 1fr)); gap: 16px; }
    .muted { color: var(--muted); }
    .note-list { display: grid; gap: 10px; }
    .note { padding: 12px; }
    .pill { display: inline-block; padding: 4px 10px; border-radius: 999px; font-size: 12px; font-weight: bold; margin-left: 8px; }
    .pill.running { background: rgba(96,165,250,0.18); color: var(--blue); }
    .pill.completed { background: rgba(52,211,153,0.18); color: var(--green); }
    .pill.failed { background: rgba(248,113,113,0.18); color: var(--red); }
    .pill.other { background: rgba(167,139,250,0.18); color: var(--purple); }
    .kv { margin: 6px 0; line-height: 1.45; }
    .section-title { margin: 24px 0 12px; }
    .small { font-size: 13px; }
  </style>
</head>
<body>
  <h1>Game Remixer Dashboard</h1>
  <div class="meta">
    <p><strong>Data source:</strong> <code>dashboard_data.json</code></p>
    <p class="muted small">Run-level and per-game runtime state, including active jobs, heartbeat freshness, and failure reasons.</p>
  </div>
  <div id="app"></div>
  <script>
    function esc(value) {
      const node = document.createElement('div');
      node.textContent = String(value ?? '');
      return node.innerHTML;
    }

    function pillClass(status) {
      if (status === 'running') return 'running';
      if (status === 'completed') return 'completed';
      if (status === 'failed') return 'failed';
      return 'other';
    }

    function formatAge(value) {
      if (value === null || value === undefined) return 'n/a';
      return `${value.toFixed ? value.toFixed(1) : value}s`;
    }

    function renderJob(job) {
      if (!job) {
        return '<p class="kv"><strong>Active Job:</strong> none</p>';
      }
      return `
        <p class="kv"><strong>Job:</strong> ${esc(job.job_type || 'unknown')} <span class="pill ${pillClass(job.status)}">${esc(job.status || 'unknown')}</span></p>
        <p class="kv"><strong>Heartbeat:</strong> ${esc(job.heartbeat_at || 'missing')}</p>
        <p class="kv"><strong>Heartbeat Age:</strong> ${formatAge(job.heartbeat_age_seconds)}</p>
        <p class="kv"><strong>Runtime Age:</strong> ${formatAge(job.runtime_age_seconds)}</p>
        <p class="kv"><strong>Failure Reason:</strong> ${esc(job.failure_reason || 'none')}</p>
      `;
    }

    async function main() {
      const res = await fetch('./dashboard_data.json');
      const data = await res.json();
      const app = document.getElementById('app');

      const summary = `
        <div class="card">
          <h2>Run Summary <span class="pill ${pillClass(data.run.status)}">${esc(data.run.status)}</span></h2>
          <p class="kv"><strong>Run ID:</strong> ${esc(data.run.run_id)}</p>
          <p class="kv"><strong>Phase:</strong> ${esc(data.run.current_phase)}</p>
          <p class="kv"><strong>Created:</strong> ${esc(data.run.created_at || 'n/a')}</p>
          <p class="kv"><strong>Updated:</strong> ${esc(data.run.updated_at || 'n/a')}</p>
        </div>
        <div class="stats">
          <div class="stat"><div class="label">Total Games</div><div class="value">${data.summary.games_total}</div></div>
          <div class="stat"><div class="label">Running</div><div class="value">${data.summary.games_running}</div></div>
          <div class="stat"><div class="label">Completed</div><div class="value">${data.summary.games_completed}</div></div>
          <div class="stat"><div class="label">Failed</div><div class="value">${data.summary.games_failed}</div></div>
          <div class="stat"><div class="label">Active Jobs</div><div class="value">${data.summary.active_jobs}</div></div>
          <div class="stat"><div class="label">Missing Heartbeats</div><div class="value">${data.summary.active_jobs_missing_heartbeat}</div></div>
          <div class="stat"><div class="label">Heartbeat > 60s</div><div class="value">${data.summary.active_jobs_stale_over_60s}</div></div>
          <div class="stat"><div class="label">Transform Failed</div><div class="value">${data.summary.games_transform_failed}</div></div>
        </div>`;

      const activeJobs = `
        <h2 class="section-title">Active Jobs</h2>
        ${data.active_jobs.length ? `<div class="grid">${data.active_jobs.map(job => `
          <div class="card">
            <h3>${esc(job.display_name || job.game_id)}</h3>
            <p class="kv"><strong>Game ID:</strong> ${esc(job.game_id)}</p>
            ${renderJob(job)}
          </div>`).join('')}</div>` : '<div class="card"><p>No active jobs currently.</p></div>'}
      `;

      const notes = `
        <h2 class="section-title">Run Notes</h2>
        ${data.run.notes.length ? `<div class="note-list">${data.run.notes.map(note => `<div class="note">${esc(note)}</div>`).join('')}</div>` : '<div class="card"><p>No notes recorded.</p></div>'}
      `;

      const cards = data.games.map(game => `
        <div class="card">
          <h2>${esc(game.display_name || game.game_id)} <span class="pill ${pillClass(game.status)}">${esc(game.status)}</span></h2>
          <p class="kv"><strong>Game ID:</strong> ${esc(game.game_id)}</p>
          <p class="kv"><strong>Phase:</strong> ${esc(game.current_phase)}</p>
          <p class="kv"><strong>Integrity:</strong> ${esc(game.integrity_status || 'pending')}</p>
          <p class="kv"><strong>Creative Status:</strong> ${esc(game.creative_status || 'n/a')}</p>
          <p class="kv"><strong>Creative Phase:</strong> ${esc(game.creative_phase || 'n/a')}</p>
          <p class="kv"><strong>Attempts:</strong> ${esc(game.attempt_count ?? 'n/a')}</p>
          <p class="kv"><strong>Updated:</strong> ${esc(game.updated_at || 'n/a')}</p>
          ${renderJob(game.job)}
          <p class="kv"><strong>Original:</strong> ${game.input_index_url ? `<a href="${game.input_index_url}" target="_blank">open input</a>` : 'missing'}</p>
          <p class="kv"><strong>Output:</strong> ${game.output_index_url ? `<a href="${game.output_index_url}" target="_blank">open output</a>` : 'not generated yet'}</p>
          <p class="kv"><strong>Error:</strong> ${esc(game.last_error || 'none')}</p>
        </div>`).join('');

      app.innerHTML = summary + activeJobs + notes + `<h2 class="section-title">Games</h2><div class="grid">${cards}</div>`;
    }

    main();
  </script>
</body>
</html>
"""
    (dashboard_dir / "index.html").write_text(html, encoding="utf-8")
    print(dashboard_dir)


if __name__ == "__main__":
    main()