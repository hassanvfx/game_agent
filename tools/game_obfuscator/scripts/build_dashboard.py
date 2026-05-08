#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import os
from datetime import datetime, timezone
from pathlib import Path


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a dashboard for a Game Obfuscator run.")
    parser.add_argument("--run-dir", required=True, help="Path to a Game Obfuscator run directory.")
    return parser.parse_args()


def relpath(target: str | Path, start: Path) -> str:
    return os.path.relpath(Path(target).resolve(), start.resolve()).replace("\\", "/")


def badge_class(status: str) -> str:
    value = (status or "").lower()
    if "pass" in value or value == "passed":
        return "ok"
    if "fail" in value or "error" in value:
        return "bad"
    return "warn"


def summarize_run(game_states: list[dict]) -> dict:
    verified = len(game_states)
    verification_passed = sum(1 for state in game_states if state.get("status") == "verification_passed")
    verification_failed = sum(1 for state in game_states if state.get("status") == "verification_failed")
    return {
        "games_verified_actual": verified,
        "games_verification_passed_actual": verification_passed,
        "games_verification_failed_actual": verification_failed,
        "derived_status": "verification_failed" if verification_failed else "verification_passed",
    }


def render_findings(verification: dict) -> str:
    findings = verification.get("findings", [])
    if not findings:
        return '<span class="muted">None</span>'

    items: list[str] = []
    for finding in findings:
        severity = html.escape(finding.get("severity", "info"))
        source = html.escape(finding.get("source", "unknown"))
        message = html.escape(finding.get("message", ""))
        items.append(f'<li><strong>{severity}</strong> — {message} <span class="muted">({source})</span></li>')
    return "<ul>" + "".join(items) + "</ul>"


def render_artifact_links(game_state: dict, run_dir: Path) -> str:
    artifacts = game_state.get("artifacts", {})
    if not artifacts:
        return '<span class="muted">No artifacts</span>'

    links: list[str] = []
    for key, path in sorted(artifacts.items()):
        label = html.escape(key)
        href = html.escape(relpath(path, run_dir / "dashboard"))
        links.append(f'<li><a href="../{href}" target="_blank" rel="noopener">{label}</a></li>')
    return "<ul>" + "".join(links) + "</ul>"


def build_dashboard_html(run_dir: Path, run_state: dict, game_states: list[dict]) -> str:
    derived = summarize_run(game_states)

    rows: list[str] = []
    for state in sorted(game_states, key=lambda item: item["game_id"]):
        game_id = html.escape(state["game_id"])
        display_name = html.escape(state.get("display_name", state["game_id"]))
        status = html.escape(state.get("status", "unknown"))
        phase = html.escape(state.get("current_phase", "unknown"))
        last_error = html.escape(state.get("last_error") or "")
        verification_path = Path(state["artifacts_path"]) / "verification.json"
        verification = load_json(verification_path) if verification_path.exists() else {}
        verification_status = html.escape(verification.get("status", "missing"))
        verification_badge = badge_class(verification_status)

        rows.append(
            f"""
            <tr>
              <td><code>{game_id}</code></td>
              <td>{display_name}</td>
              <td><span class="badge {badge_class(status)}">{status}</span></td>
              <td><span class="badge {verification_badge}">{verification_status}</span></td>
              <td><code>{phase}</code></td>
              <td>{html.escape(last_error) if last_error else '<span class="muted">None</span>'}</td>
              <td>{render_findings(verification)}</td>
              <td>{render_artifact_links(state, run_dir)}</td>
            </tr>
            """
        )

    notes_html = "".join(f"<li>{html.escape(note)}</li>" for note in run_state.get("notes", []))

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Game Obfuscator Dashboard - {html.escape(run_state['run_id'])}</title>
  <style>
    :root {{
      --bg: #0b1220;
      --panel: #121a2b;
      --panel-2: #1a2438;
      --text: #e8eefc;
      --muted: #9db0d1;
      --ok: #1f9d5c;
      --warn: #b98522;
      --bad: #c94949;
      --border: #2c3954;
      --link: #8cc4ff;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.45;
    }}
    .wrap {{
      max-width: 1400px;
      margin: 0 auto;
      padding: 24px;
    }}
    h1, h2 {{ margin: 0 0 12px; }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 16px;
      margin: 20px 0 28px;
    }}
    .card {{
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 16px;
    }}
    .card .label {{
      color: var(--muted);
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      margin-bottom: 8px;
    }}
    .card .value {{
      font-size: 22px;
      font-weight: 700;
    }}
    .badge {{
      display: inline-block;
      padding: 4px 10px;
      border-radius: 999px;
      font-size: 12px;
      font-weight: 700;
    }}
    .badge.ok {{ background: rgba(31, 157, 92, 0.18); color: #8ef0b6; }}
    .badge.warn {{ background: rgba(185, 133, 34, 0.18); color: #ffd98a; }}
    .badge.bad {{ background: rgba(201, 73, 73, 0.18); color: #ff9d9d; }}
    table {{
      width: 100%;
      border-collapse: collapse;
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 12px;
      overflow: hidden;
    }}
    th, td {{
      border-bottom: 1px solid var(--border);
      padding: 12px;
      text-align: left;
      vertical-align: top;
      font-size: 14px;
    }}
    th {{
      background: var(--panel-2);
      position: sticky;
      top: 0;
    }}
    code {{
      font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
      font-size: 12px;
    }}
    a {{ color: var(--link); text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    .muted {{ color: var(--muted); }}
    ul {{
      margin: 0;
      padding-left: 18px;
    }}
    .section {{
      margin-top: 28px;
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <h1>Game Obfuscator Dashboard</h1>
    <p class="muted">Generated at {html.escape(utc_now())}</p>

    <div class="grid">
      <div class="card">
        <div class="label">Run ID</div>
        <div class="value"><code>{html.escape(run_state['run_id'])}</code></div>
      </div>
      <div class="card">
        <div class="label">Run Status (stored)</div>
        <div class="value"><span class="badge {badge_class(run_state.get('status', 'unknown'))}">{html.escape(run_state.get('status', 'unknown'))}</span></div>
      </div>
      <div class="card">
        <div class="label">Run Status (derived)</div>
        <div class="value"><span class="badge {badge_class(derived['derived_status'])}">{html.escape(derived['derived_status'])}</span></div>
      </div>
      <div class="card">
        <div class="label">Games Total</div>
        <div class="value">{run_state.get('games_total', len(game_states))}</div>
      </div>
      <div class="card">
        <div class="label">Verified</div>
        <div class="value">{derived['games_verified_actual']}</div>
      </div>
      <div class="card">
        <div class="label">Verification Passed</div>
        <div class="value">{derived['games_verification_passed_actual']}</div>
      </div>
      <div class="card">
        <div class="label">Verification Failed</div>
        <div class="value">{derived['games_verification_failed_actual']}</div>
      </div>
      <div class="card">
        <div class="label">Current Phase</div>
        <div class="value"><code>{html.escape(run_state.get('current_phase', 'unknown'))}</code></div>
      </div>
    </div>

    <div class="section">
      <h2>Per-game Status</h2>
      <table>
        <thead>
          <tr>
            <th>Game ID</th>
            <th>Name</th>
            <th>Status</th>
            <th>Verification</th>
            <th>Phase</th>
            <th>Last Error</th>
            <th>Findings</th>
            <th>Artifacts</th>
          </tr>
        </thead>
        <tbody>
          {''.join(rows)}
        </tbody>
      </table>
    </div>

    <div class="section">
      <h2>Run Notes</h2>
      <div class="card">
        <ul>{notes_html}</ul>
      </div>
    </div>
  </div>
</body>
</html>
"""


def main() -> None:
    args = parse_args()
    run_dir = Path(args.run_dir).resolve()
    run_state = load_json(run_dir / "run_state.json")
    manifest = load_json(run_dir / "input_manifest.json")

    game_states: list[dict] = []
    for game in manifest.get("games", []):
        game_id = game["game_id"]
        game_state = load_json(run_dir / "games" / game_id / "game_state.json")
        game_states.append(game_state)

    dashboard_dir = run_dir / "dashboard"
    dashboard_dir.mkdir(parents=True, exist_ok=True)
    dashboard_path = dashboard_dir / "index.html"
    dashboard_path.write_text(build_dashboard_html(run_dir, run_state, game_states), encoding="utf-8")

    print(dashboard_path)


if __name__ == "__main__":
    main()