import argparse
import json
import statistics
from html import escape
from pathlib import Path
from typing import Any


DEFAULT_INPUT_PATH = Path(
    "outputs/rezona_crawl/run_20260415T064109Z/summaries/games_grouped_by_game_id.json"
)
DEFAULT_OUTPUT_PATH = Path(
    "outputs/rezona_crawl/run_20260415T064109Z/summaries/games_grouped_by_game_id_dashboard.html"
)


def load_grouped_games(path: Path) -> dict[str, list[dict[str, Any]]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Expected grouped JSON to be a top-level object.")

    grouped: dict[str, list[dict[str, Any]]] = {}
    for game_id, versions in payload.items():
        if isinstance(game_id, str) and isinstance(versions, list):
            grouped[game_id] = [item for item in versions if isinstance(item, dict)]
    return grouped


def build_rows(grouped: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for game_id, versions in grouped.items():
        version_count = len(versions)
        first = versions[0] if versions else {}
        last = versions[-1] if versions else {}
        first_version = first.get("game_version", "—")
        last_version = last.get("game_version", "—")
        latest_name = last.get("name", "—")
        latest_url = last.get("url", "")
        rows.append(
            {
                "game_id": game_id,
                "version_count": version_count,
                "first_version": first_version,
                "last_version": last_version,
                "latest_name": latest_name,
                "latest_url": latest_url,
            }
        )
    rows.sort(key=lambda row: (-row["version_count"], int(row["game_id"])))
    return rows


def render_html(grouped: dict[str, list[dict[str, Any]]]) -> str:
    rows = build_rows(grouped)
    version_counts = [row["version_count"] for row in rows]
    unique_game_ids = len(rows)
    total_versions = sum(version_counts)
    average_versions = statistics.mean(version_counts) if version_counts else 0
    median_versions = statistics.median(version_counts) if version_counts else 0
    max_versions = max(version_counts) if version_counts else 0
    multi_version_ids = sum(1 for count in version_counts if count > 1)
    top_100 = rows[:100]

    table_rows = []
    for index, row in enumerate(top_100, start=1):
        latest_name = escape(str(row["latest_name"]))
        latest_url = str(row["latest_url"]).strip()
        latest_url_html = (
            f'<a href="{escape(latest_url)}" target="_blank" rel="noreferrer">open latest</a>'
            if latest_url
            else "—"
        )
        table_rows.append(
            f"""
            <tr>
              <td>{index}</td>
              <td><code>{escape(row["game_id"])}</code></td>
              <td>{row["version_count"]}</td>
              <td>{escape(str(row["first_version"]))}</td>
              <td>{escape(str(row["last_version"]))}</td>
              <td>{latest_name}</td>
              <td>{latest_url_html}</td>
            </tr>
            """
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Rezona Grouped Game Versions Dashboard</title>
  <style>
    :root {{
      --bg: #0b1020;
      --panel: #151c33;
      --panel-2: #1d2745;
      --text: #e9eefc;
      --muted: #9fb0d9;
      --accent: #6ea8ff;
      --good: #4dd4ac;
      --warn: #ffcc66;
      --border: #2a365f;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.45;
    }}
    .wrap {{
      max-width: 1280px;
      margin: 0 auto;
      padding: 24px;
    }}
    .hero, .panel {{
      background: linear-gradient(180deg, var(--panel), var(--panel-2));
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 20px;
      box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }}
    .hero, .stats, .panel {{
      margin-bottom: 20px;
    }}
    .stats {{
      display: grid;
      grid-template-columns: repeat(5, minmax(0, 1fr));
      gap: 16px;
    }}
    .card {{
      background: rgba(255,255,255,0.03);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 16px;
    }}
    .label {{
      color: var(--muted);
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      margin-bottom: 8px;
    }}
    .value {{
      font-size: 32px;
      font-weight: 700;
    }}
    .sub {{
      color: var(--muted);
      font-size: 14px;
      margin-top: 8px;
    }}
    .two-col {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
      margin-bottom: 20px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 14px;
    }}
    th, td {{
      text-align: left;
      padding: 10px 8px;
      border-bottom: 1px solid var(--border);
      vertical-align: top;
    }}
    th {{
      color: var(--muted);
      font-weight: 600;
    }}
    code {{
      background: rgba(255,255,255,0.06);
      padding: 2px 6px;
      border-radius: 6px;
    }}
    a {{
      color: var(--accent);
      text-decoration: none;
    }}
    a:hover {{
      text-decoration: underline;
    }}
    .meter {{
      width: 100%;
      height: 12px;
      border-radius: 999px;
      background: rgba(255,255,255,0.06);
      overflow: hidden;
      margin-top: 10px;
    }}
    .meter-bar {{
      height: 100%;
      width: {0 if unique_game_ids == 0 else round((multi_version_ids / unique_game_ids) * 100, 2)}%;
      background: linear-gradient(90deg, var(--good), var(--accent));
      border-radius: 999px;
    }}
    @media (max-width: 1000px) {{
      .stats, .two-col {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <section class="hero">
      <h1>Rezona Grouped Game Versions Dashboard</h1>
      <p>
        Companion dashboard for <code>games_grouped_by_game_id.json</code>. This view summarizes
        how many unique game IDs are present, how many total versioned entities exist, and which
        game IDs have the deepest version history.
      </p>
    </section>

    <section class="stats">
      <div class="card">
        <div class="label">Unique game IDs</div>
        <div class="value">{unique_game_ids:,}</div>
        <div class="sub">Top-level dictionary keys</div>
      </div>
      <div class="card">
        <div class="label">Total versions</div>
        <div class="value">{total_versions:,}</div>
        <div class="sub">Sum of all grouped entities</div>
      </div>
      <div class="card">
        <div class="label">Average versions / ID</div>
        <div class="value">{average_versions:.2f}</div>
        <div class="sub">Mean grouped array size</div>
      </div>
      <div class="card">
        <div class="label">Median versions / ID</div>
        <div class="value">{median_versions}</div>
        <div class="sub">Middle grouped array size</div>
      </div>
      <div class="card">
        <div class="label">Max versions on one ID</div>
        <div class="value">{max_versions}</div>
        <div class="sub">Largest version family found</div>
      </div>
    </section>

    <section class="two-col">
      <div class="panel">
        <h2>Version family summary</h2>
        <table>
          <tbody>
            <tr>
              <th>Multi-version game IDs</th>
              <td>{multi_version_ids:,}</td>
            </tr>
            <tr>
              <th>Single-version game IDs</th>
              <td>{unique_game_ids - multi_version_ids:,}</td>
            </tr>
            <tr>
              <th>Multi-version share</th>
              <td>{0 if unique_game_ids == 0 else (multi_version_ids / unique_game_ids) * 100:.2f}%</td>
            </tr>
          </tbody>
        </table>
        <div class="meter"><div class="meter-bar"></div></div>
        <div class="sub">Share of grouped keys that contain more than one versioned entity.</div>
      </div>

      <div class="panel">
        <h2>Interpretation</h2>
        <ul>
          <li><strong>Unique game IDs</strong> tells you how many canonical families exist.</li>
          <li><strong>Total versions</strong> tells you how many versioned entities were captured.</li>
          <li><strong>Average versions / ID</strong> reveals how often games repeat across versions.</li>
          <li><strong>Top 100 table</strong> highlights the deepest version histories first.</li>
        </ul>
      </div>
    </section>

    <section class="panel">
      <h2>Top 100 game IDs by number of versions</h2>
      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>Game ID</th>
            <th>Versions</th>
            <th>First version</th>
            <th>Latest version</th>
            <th>Latest name</th>
            <th>Latest URL</th>
          </tr>
        </thead>
        <tbody>
          {''.join(table_rows)}
        </tbody>
      </table>
    </section>
  </div>
</body>
</html>
"""


def write_dashboard(output_path: Path, html: str) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a companion dashboard for grouped Rezona game version data."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT_PATH,
        help="Path to games_grouped_by_game_id.json.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help="Path to write the dashboard HTML file.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    grouped = load_grouped_games(args.input)
    html = render_html(grouped)
    write_dashboard(args.output, html)
    print(f"Wrote dashboard to {args.output}")


if __name__ == "__main__":
    main()