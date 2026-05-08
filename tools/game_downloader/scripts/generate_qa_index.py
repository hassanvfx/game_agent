#!/usr/bin/env python3

import argparse
import html
import json
import re
from pathlib import Path
from urllib.parse import urlparse


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def find_latest_attempt_name(path: Path) -> str | None:
    if not path.exists():
        return None
    candidates = sorted(child.name for child in path.iterdir() if child.is_dir() and child.name.startswith("attempt_"))
    return candidates[-1] if candidates else None


def safe_int(value: object) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def text_or_fallback(value: object, fallback: str = "—") -> str:
    text = str(value or "").strip()
    return text if text else fallback


def pick_cover_url(source: dict) -> str:
    dynamic_cover_url = str(source.get("dynamic_cover_url") or "").strip()
    if dynamic_cover_url:
        return dynamic_cover_url
    return str(source.get("cover_url") or "").strip()


def slug_to_label(slug: str) -> str:
    return slug.replace("-", " ").strip()


def normalize_tokens(*values: object) -> list[str]:
    tokens: set[str] = set()
    for value in values:
        text = str(value or "").lower()
        for token in re.findall(r"[a-z0-9]+", text):
            if len(token) >= 2:
                tokens.add(token)
    return sorted(tokens)


def collect_url_tokens(url: str) -> list[str]:
    if not url:
        return []
    parsed = urlparse(url)
    host = parsed.netloc.replace(".", " ")
    path = parsed.path.replace("/", " ")
    return normalize_tokens(host, path)


def load_query_tag_map(search_dir: Path) -> dict[str, set[str]]:
    query_map: dict[str, set[str]] = {}
    if not search_dir.exists():
        return query_map

    for query_file in sorted(search_dir.glob("query_*.json")):
        payload = load_json(query_file)
        query = str(payload.get("query") or payload.get("slug") or "").strip()
        slug = str(payload.get("slug") or "").strip()
        if not query and not slug:
            continue

        label = query or slug_to_label(slug)
        normalized_label = label.strip()
        if not normalized_label:
            continue

        for item in payload.get("items") or []:
            game = item.get("game") or {}
            game_url = str(game.get("url") or "").strip()
            if not game_url:
                continue
            game_key = Path(urlparse(game_url).path).parent.name
            if not game_key:
                continue
            query_map.setdefault(game_key, set()).add(normalized_label)

    return query_map


def load_source_metadata(game_dir: Path, query_tag_map: dict[str, set[str]]) -> dict:
    source_path = game_dir / "source.json"
    if not source_path.exists():
        return {}

    source = load_json(source_path)
    creator = source.get("creator") or {}
    topic = source.get("topic") or {}
    stats = source.get("stats") or {}

    title = text_or_fallback(source.get("name"))
    description = str(source.get("description") or "").strip()
    creator_name = text_or_fallback(creator.get("name"))
    topic_name = text_or_fallback(topic.get("name"))
    source_url = str(source.get("url") or "").strip()
    query_tags = sorted(query_tag_map.get(game_dir.name, set()))

    display_tags: list[str] = []
    for tag in query_tags:
        display_tags.append(tag)
    if topic_name != "—":
        display_tags.append(f"topic: {topic_name}")
    if creator_name != "—":
        display_tags.append(f"creator: {creator_name}")

    seen_tags: set[str] = set()
    deduped_display_tags = []
    for tag in display_tags:
        normalized_tag = tag.casefold()
        if normalized_tag in seen_tags:
            continue
        seen_tags.add(normalized_tag)
        deduped_display_tags.append(tag)

    search_tokens = normalize_tokens(
        game_dir.name,
        title,
        description,
        creator_name,
        topic_name,
        source_url,
        " ".join(query_tags),
    )
    search_tokens.extend(token for token in collect_url_tokens(source_url) if token not in search_tokens)

    return {
        "title": title,
        "description": description,
        "creator_name": creator_name,
        "creator_id": text_or_fallback(creator.get("id")),
        "topic_name": topic_name,
        "topic_id": text_or_fallback(topic.get("id")),
        "played_count": safe_int(stats.get("played_count")),
        "liked_count": safe_int(stats.get("liked_count")),
        "shared_count": safe_int(stats.get("shared_count")),
        "comment_count": safe_int(stats.get("comment_count")),
        "exact_match": bool(source.get("exact_match")),
        "source_url": source_url,
        "cover_url": pick_cover_url(source),
        "game_id": text_or_fallback(source.get("game_id")),
        "game_version": text_or_fallback(source.get("game_version")),
        "screen_orientation": text_or_fallback(source.get("screen_orientation")),
        "is_public": str(bool(source.get("is_public"))).lower(),
        "remixable": str(bool(source.get("remixable"))).lower(),
        "remixed_games": safe_int(source.get("remixed_games")),
        "created_at": text_or_fallback(source.get("created_at")),
        "updated_at": text_or_fallback(source.get("updated_at")),
        "query_tags": query_tags,
        "display_tags": deduped_display_tags,
        "search_tokens": sorted(set(search_tokens)),
    }


def format_count_label(label: str, value: int) -> str:
    return f'<span class="metric-pill"><strong>{value}</strong> {html.escape(label)}</span>'


def build_tag_chips(tags: list[str]) -> str:
    if not tags:
        return '<p class="tag-row muted">No tags</p>'
    chips = "".join(
        f'<button type="button" class="tag-chip" data-tag="{html.escape(tag.lower())}">{html.escape(tag)}</button>'
        for tag in tags
    )
    return f'<div class="tag-row">{chips}</div>'


def build_card(index: int, item: dict) -> str:
    title = html.escape(item["title"])
    game_key = html.escape(item["game_key"])
    readiness = html.escape(item["offline_readiness"])
    creator_name = html.escape(item["creator_name"])
    topic_name = html.escape(item["topic_name"])
    localhost_url = html.escape(item["url"])
    source_url = html.escape(item["source_url"])
    exact_match = "yes" if item["exact_match"] else "no"
    filter_text = html.escape(" ".join(item["search_tokens"]))
    filter_tags = html.escape(" || ".join(tag.lower() for tag in item["display_tags"]))

    if item["cover_url"]:
        cover_html = (
            f'<img class="cover" src="{html.escape(item["cover_url"])}" '
            f'alt="Cover for {title}" loading="lazy" referrerpolicy="no-referrer">'
        )
    else:
        cover_html = '<div class="cover cover-fallback">No cover</div>'

    source_link_html = (
        f'<a href="{source_url}" target="_blank" rel="noreferrer">open source URL</a>'
        if item["source_url"]
        else '<span class="muted">No source URL</span>'
    )

    description_html = ""
    if item["description"]:
        description_html = f'<p class="description">{html.escape(item["description"])}</p>'

    return (
        f'<article class="qa-card" data-readiness="{html.escape(item["offline_readiness"])}" '
        f'data-filter-text="{filter_text}" data-filter-tags="{filter_tags}">'
        f'<div class="card-index">#{index}</div>'
        '<div class="card-main">'
        f"{cover_html}"
        '<div class="card-content">'
        '<div class="headline-row">'
        f'<h3>{title}</h3>'
        f'<span class="badge badge-{html.escape(item["offline_readiness"])}">{readiness}</span>'
        '</div>'
        f'<p class="subhead"><code>{game_key}</code></p>'
        f"{description_html}"
        f'{build_tag_chips(item["display_tags"])}'
        '<div class="metric-row">'
        f'{format_count_label("remote refs", item["remaining_remote_ref_count"])}'
        f'{format_count_label("unresolved URLs", item["unresolved_url_count"])}'
        f'{format_count_label("failed assets", item["failed_asset_count"])}'
        f'{format_count_label("plays", item["played_count"])}'
        f'{format_count_label("likes", item["liked_count"])}'
        f'{format_count_label("shares", item["shared_count"])}'
        f'{format_count_label("comments", item["comment_count"])}'
        '</div>'
        '<div class="link-row">'
        f'<a href="{localhost_url}" target="_blank">open local replay</a>'
        f'<code class="url-code">{localhost_url}</code>'
        '</div>'
        '<details class="details-panel">'
        '<summary>Details</summary>'
        '<div class="details-grid">'
        f'<div><span class="label">Creator</span><span>{creator_name}</span></div>'
        f'<div><span class="label">Creator ID</span><span>{html.escape(item["creator_id"])}</span></div>'
        f'<div><span class="label">Topic</span><span>{topic_name}</span></div>'
        f'<div><span class="label">Topic ID</span><span>{html.escape(item["topic_id"])}</span></div>'
        f'<div><span class="label">Exact match</span><span>{exact_match}</span></div>'
        f'<div><span class="label">Game ID</span><span>{html.escape(item["game_id"])}</span></div>'
        f'<div><span class="label">Game version</span><span>{html.escape(item["game_version"])}</span></div>'
        f'<div><span class="label">Orientation</span><span>{html.escape(item["screen_orientation"])}</span></div>'
        f'<div><span class="label">Public</span><span>{html.escape(item["is_public"])}</span></div>'
        f'<div><span class="label">Remixable</span><span>{html.escape(item["remixable"])}</span></div>'
        f'<div><span class="label">Remixed games</span><span>{item["remixed_games"]}</span></div>'
        f'<div><span class="label">Created at</span><span>{html.escape(item["created_at"])}</span></div>'
        f'<div><span class="label">Updated at</span><span>{html.escape(item["updated_at"])}</span></div>'
        f'<div><span class="label">Source query tags</span><span>{html.escape(", ".join(item["query_tags"]) or "—")}</span></div>'
        f'<div><span class="label">Source URL</span><span>{source_link_html}</span></div>'
        f'<div><span class="label">Local replay URL</span><span><code>{localhost_url}</code></span></div>'
        '</div>'
        '</details>'
        '</div>'
        '</div>'
        '</article>'
    )


def build_section(title: str, items: list[dict], start_index: int) -> tuple[str, int]:
    cards = []
    current_index = start_index
    for item in items:
        cards.append(build_card(current_index, item))
        current_index += 1

    section_html = (
        '<section class="group-section">'
        f'<div class="group-header"><h2>{html.escape(title)}</h2><p>Included items: {len(items)}</p></div>'
        f'<div class="card-grid">{"".join(cards)}</div>'
        '</section>'
    )
    return section_html, current_index


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a localhost QA index for processed mirror replays.")
    parser.add_argument("--run-dir", required=True, help="Mirror run directory.")
    parser.add_argument("--limit", type=int, default=100, help="Maximum number of items to scan/include.")
    parser.add_argument(
        "--base-url",
        default="http://localhost:8000/mirror_runs",
        help="Base localhost URL that maps to the mirror_runs directory from the repo root server.",
    )
    parser.add_argument(
        "--search-dir",
        default="outputs/rezona_crawl/run_20260415T064109Z/search",
        help="Directory containing crawl search query JSON files used to derive query tags.",
    )
    args = parser.parse_args()

    run_dir = Path(args.run_dir)
    reports_dir = run_dir / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    query_tag_map = load_query_tag_map(Path(args.search_dir))
    fully_ready_items = []
    partially_ready_items = []

    for game_dir in sorted(path for path in (run_dir / "games").iterdir() if path.is_dir()):
        replay_root = game_dir / "replay"
        latest_replay_attempt = find_latest_attempt_name(replay_root)
        if latest_replay_attempt is None:
            continue

        summary_path = replay_root / latest_replay_attempt / "mirror_build_summary.json"
        if not summary_path.exists():
            continue

        summary = load_json(summary_path)
        readiness = str(summary.get("offline_readiness") or "").strip()
        if readiness not in {"fully_offline_ready", "partially_offline_ready"}:
            continue

        replay_rel = Path(run_dir.name) / "games" / game_dir.name / "replay" / latest_replay_attempt / "index.html"
        source_metadata = load_source_metadata(game_dir, query_tag_map)

        item = {
            "game_key": game_dir.name,
            "offline_readiness": readiness,
            "remaining_remote_ref_count": safe_int(summary.get("remaining_remote_ref_count")),
            "unresolved_url_count": safe_int(summary.get("unresolved_url_count")),
            "failed_asset_count": safe_int(summary.get("failed_asset_count")),
            "url": f"{args.base_url.rstrip('/')}/{replay_rel.as_posix()}",
            **source_metadata,
        }

        if readiness == "fully_offline_ready":
            fully_ready_items.append(item)
        else:
            partially_ready_items.append(item)

        if len(fully_ready_items) + len(partially_ready_items) >= args.limit:
            break

    combined_items = fully_ready_items + partially_ready_items
    all_display_tags = sorted({tag for item in combined_items for tag in item["display_tags"]})
    featured_tags = all_display_tags[:40]

    txt_path = reports_dir / f"sample_test_urls_{args.limit}.txt"
    txt_path.write_text("\n".join(item["url"] for item in combined_items) + "\n", encoding="utf-8")

    fully_ready_section, next_index = build_section("Fully Offline Ready", fully_ready_items, 1)
    partially_ready_section, _ = build_section("Partially Offline Ready", partially_ready_items, next_index)

    tag_filter_buttons = "".join(
        f'<button type="button" class="filter-chip" data-filter-tag="{html.escape(tag.lower())}">{html.escape(tag)}</button>'
        for tag in featured_tags
    )

    html_path = reports_dir / f"qa_index_{args.limit}.html"
    html_path.write_text(
        f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>QA Index - {html.escape(run_dir.name)} - top {args.limit}</title>
  <style>
    :root {{
      color-scheme: dark;
      --bg: #0f172a;
      --panel: #111827;
      --panel-strong: #1f2937;
      --panel-soft: #0b1220;
      --border: #334155;
      --text: #f8fafc;
      --muted: #94a3b8;
      --link: #60a5fa;
    }}

    * {{ box-sizing: border-box; }}
    body {{
      font-family: Arial, sans-serif;
      margin: 0;
      background: linear-gradient(180deg, #020617 0%, var(--bg) 100%);
      color: var(--text);
    }}
    main {{
      max-width: 1440px;
      margin: 0 auto;
      padding: 24px;
    }}
    a {{ color: var(--link); }}
    code {{
      background: var(--panel-strong);
      padding: 2px 6px;
      border-radius: 4px;
      overflow-wrap: anywhere;
    }}
    .hero {{
      background: rgba(15, 23, 42, 0.88);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 24px;
      margin-bottom: 24px;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.22);
    }}
    .hero p {{ color: var(--muted); line-height: 1.5; }}
    .summary-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 12px;
      margin: 20px 0 8px;
    }}
    .summary-card {{
      background: var(--panel-strong);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 14px;
    }}
    .summary-card strong {{
      display: block;
      font-size: 1.35rem;
      margin-top: 6px;
    }}
    .filter-panel {{
      margin-top: 20px;
      display: grid;
      gap: 12px;
    }}
    .filter-grid {{
      display: grid;
      grid-template-columns: minmax(280px, 2fr) minmax(180px, 1fr) auto;
      gap: 12px;
      align-items: end;
    }}
    .control-group label {{
      display: block;
      margin-bottom: 6px;
      color: var(--muted);
      font-size: 0.9rem;
    }}
    input[type="search"], select {{
      width: 100%;
      padding: 10px 12px;
      border-radius: 10px;
      border: 1px solid var(--border);
      background: var(--panel-soft);
      color: var(--text);
    }}
    .clear-button, .filter-chip, .tag-chip {{
      border-radius: 999px;
      border: 1px solid var(--border);
      background: var(--panel-strong);
      color: var(--text);
      cursor: pointer;
    }}
    .clear-button {{
      padding: 10px 14px;
      min-height: 42px;
    }}
    .filter-chip-row, .tag-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }}
    .filter-chip, .tag-chip {{
      padding: 6px 10px;
      font-size: 0.88rem;
    }}
    .filter-chip.active, .tag-chip.active {{
      border-color: #60a5fa;
      background: rgba(96, 165, 250, 0.16);
    }}
    .filter-status {{
      color: var(--muted);
      font-size: 0.95rem;
    }}
    .group-section {{ margin: 28px 0 40px; }}
    .group-section.is-hidden {{ display: none; }}
    .group-header {{
      display: flex;
      justify-content: space-between;
      align-items: baseline;
      gap: 16px;
      margin-bottom: 16px;
      flex-wrap: wrap;
    }}
    .group-header h2 {{ margin: 0; }}
    .group-header p {{ margin: 0; color: var(--muted); }}
    .card-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(380px, 1fr));
      gap: 16px;
    }}
    .qa-card {{
      background: rgba(17, 24, 39, 0.96);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 16px;
      position: relative;
      overflow: hidden;
    }}
    .qa-card.is-hidden {{ display: none; }}
    .card-index {{
      position: absolute;
      top: 12px;
      right: 12px;
      color: var(--muted);
      font-size: 0.9rem;
    }}
    .card-main {{
      display: grid;
      grid-template-columns: 104px minmax(0, 1fr);
      gap: 16px;
      align-items: start;
    }}
    .cover {{
      width: 104px;
      height: 104px;
      object-fit: cover;
      border-radius: 12px;
      border: 1px solid var(--border);
      background: var(--panel-soft);
    }}
    .cover-fallback {{
      display: flex;
      align-items: center;
      justify-content: center;
      color: var(--muted);
      font-size: 0.85rem;
      text-align: center;
      padding: 8px;
    }}
    .headline-row {{
      display: flex;
      align-items: start;
      justify-content: space-between;
      gap: 12px;
      margin-right: 44px;
    }}
    .headline-row h3 {{
      margin: 0;
      font-size: 1.1rem;
      line-height: 1.3;
      overflow-wrap: anywhere;
    }}
    .subhead {{
      margin: 6px 0 10px;
      color: var(--muted);
    }}
    .description {{
      margin: 0 0 12px;
      color: #cbd5e1;
      line-height: 1.5;
    }}
    .badge {{
      display: inline-flex;
      align-items: center;
      border-radius: 999px;
      padding: 5px 10px;
      font-size: 0.82rem;
      font-weight: 700;
      text-transform: lowercase;
      white-space: nowrap;
      border: 1px solid transparent;
    }}
    .badge-fully_offline_ready {{
      background: rgba(16, 185, 129, 0.14);
      color: #6ee7b7;
      border-color: rgba(16, 185, 129, 0.35);
    }}
    .badge-partially_offline_ready {{
      background: rgba(245, 158, 11, 0.14);
      color: #fcd34d;
      border-color: rgba(245, 158, 11, 0.35);
    }}
    .metric-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin: 12px 0;
    }}
    .metric-pill {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 6px 10px;
      border-radius: 999px;
      background: var(--panel-strong);
      border: 1px solid var(--border);
      color: #e2e8f0;
      font-size: 0.9rem;
    }}
    .metric-pill strong {{ font-size: 0.95rem; }}
    .link-row {{
      display: flex;
      flex-direction: column;
      gap: 8px;
      margin: 12px 0;
    }}
    .url-code {{
      display: inline-block;
      padding: 8px 10px;
      line-height: 1.45;
    }}
    .details-panel {{
      margin-top: 12px;
      border-top: 1px solid var(--border);
      padding-top: 12px;
    }}
    .details-panel summary {{
      cursor: pointer;
      color: #cbd5e1;
      font-weight: 700;
    }}
    .details-grid {{
      margin-top: 12px;
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 12px;
    }}
    .details-grid > div {{
      background: var(--panel-soft);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 10px;
      min-width: 0;
    }}
    .label {{
      display: block;
      color: var(--muted);
      font-size: 0.8rem;
      margin-bottom: 6px;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }}
    .muted {{ color: var(--muted); }}

    @media (max-width: 900px) {{
      .filter-grid {{
        grid-template-columns: 1fr;
      }}
    }}

    @media (max-width: 720px) {{
      main {{ padding: 16px; }}
      .card-grid {{ grid-template-columns: 1fr; }}
      .card-main {{ grid-template-columns: 1fr; }}
      .cover {{
        width: 100%;
        max-width: 180px;
        height: auto;
        aspect-ratio: 1 / 1;
      }}
      .headline-row {{
        flex-direction: column;
        margin-right: 0;
      }}
    }}
  </style>
</head>
<body>
  <main>
    <section class="hero">
      <h1>QA Index - {html.escape(run_dir.name)}</h1>
      <p>This QA page represents the latest replay attempt for each game and groups the run into fully offline-ready and partially offline-ready mirrors. It now includes bag-of-words search, query-derived tags, and refinement filters to make the 7K index easier to explore.</p>
      <p>Server root command: <code>python3 -m http.server 8000</code> from the repo root.</p>
      <p>Open this QA page at: <code>http://localhost:8000/mirror_runs/{html.escape(run_dir.name)}/reports/{html.escape(html_path.name)}</code></p>
      <p>URL list file: <code>mirror_runs/{html.escape(run_dir.name)}/reports/{html.escape(txt_path.name)}</code></p>

      <div class="summary-grid">
        <div class="summary-card">Scanned limit<strong>{args.limit}</strong></div>
        <div class="summary-card">Fully offline ready<strong>{len(fully_ready_items)}</strong></div>
        <div class="summary-card">Partially offline ready<strong>{len(partially_ready_items)}</strong></div>
        <div class="summary-card">Featured tags<strong>{len(featured_tags)}</strong></div>
      </div>

      <section class="filter-panel" aria-label="QA filters">
        <div class="filter-grid">
          <div class="control-group">
            <label for="searchBox">Search titles, tags, creators, topics</label>
            <input id="searchBox" type="search" placeholder="Try: minecraft, obby, topic, creator, horror..." autocomplete="off">
          </div>
          <div class="control-group">
            <label for="readinessFilter">Readiness</label>
            <select id="readinessFilter">
              <option value="all">All</option>
              <option value="fully_offline_ready">Fully offline ready</option>
              <option value="partially_offline_ready">Partially offline ready</option>
            </select>
          </div>
          <button type="button" id="clearFilters" class="clear-button">Clear filters</button>
        </div>

        <div>
          <div class="filter-chip-row">{tag_filter_buttons}</div>
        </div>

        <p class="filter-status">
          Showing <strong id="visibleCount">{len(combined_items)}</strong> of <strong id="totalCount">{len(combined_items)}</strong> games.
          <span id="activeFilterSummary">No active filters.</span>
        </p>
      </section>
    </section>

    {fully_ready_section}
    {partially_ready_section}
  </main>

  <script>
    (() => {{
      const searchBox = document.getElementById("searchBox");
      const readinessFilter = document.getElementById("readinessFilter");
      const clearFiltersButton = document.getElementById("clearFilters");
      const visibleCount = document.getElementById("visibleCount");
      const totalCount = document.getElementById("totalCount");
      const activeFilterSummary = document.getElementById("activeFilterSummary");
      const cards = Array.from(document.querySelectorAll(".qa-card"));
      const sections = Array.from(document.querySelectorAll(".group-section"));
      const tagButtons = Array.from(document.querySelectorAll("[data-filter-tag]"));
      const inlineTagButtons = Array.from(document.querySelectorAll(".tag-chip"));
      const cardRecords = cards.map((card) => {{
        const section = card.closest(".group-section");
        return {{
          element: card,
          section,
          readiness: card.dataset.readiness || "",
          text: (card.dataset.filterText || "").toLowerCase(),
          tags: (card.dataset.filterTags || "").toLowerCase(),
        }};
      }});

      totalCount.textContent = String(cards.length);

      let activeTag = "";
      let searchTimer = null;

      function normalizeQuery(text) {{
        return (text || "").trim().toLowerCase().replace(/\\s+/g, " ");
      }}

      function updateActiveTagButtons() {{
        for (const button of tagButtons) {{
          button.classList.toggle("active", button.dataset.filterTag === activeTag);
        }}
        for (const button of inlineTagButtons) {{
          button.classList.toggle("active", button.dataset.tag === activeTag);
        }}
      }}

      function applyFilters() {{
        const query = normalizeQuery(searchBox.value);
        const readiness = readinessFilter.value;

        let visible = 0;

        for (const record of cardRecords) {{
          const passesReadiness = readiness === "all" || record.readiness === readiness;
          const passesTag = !activeTag || record.tags.includes(activeTag);
          const passesSearch = !query || record.text.includes(query);
          const show = passesReadiness && passesTag && passesSearch;

          record.element.classList.toggle("is-hidden", !show);
          if (show) {{
            visible += 1;
          }}
        }}

        for (const section of sections) {{
          const hasVisibleCards = Array.from(section.querySelectorAll(".qa-card")).some((card) => !card.classList.contains("is-hidden"));
          section.classList.toggle("is-hidden", !hasVisibleCards);
        }}

        visibleCount.textContent = String(visible);

        const summaryParts = [];
        if (query) {{
          summaryParts.push(`query: "${{query}}"`);
        }}
        if (readiness !== "all") {{
          summaryParts.push(`readiness: ${{readiness.replaceAll("_", " ")}}`);
        }}
        if (activeTag) {{
          summaryParts.push(`tag: ${{activeTag}}`);
        }}
        activeFilterSummary.textContent = summaryParts.length > 0 ? `Active filters: ${{summaryParts.join(" · ")}}.` : "No active filters.";
        updateActiveTagButtons();
      }}

      function scheduleApplyFilters() {{
        if (searchTimer) {{
          window.clearTimeout(searchTimer);
        }}
        searchTimer = window.setTimeout(() => {{
          applyFilters();
        }}, 180);
      }}

      searchBox.addEventListener("input", scheduleApplyFilters);
      readinessFilter.addEventListener("change", applyFilters);

      clearFiltersButton.addEventListener("click", () => {{
        searchBox.value = "";
        readinessFilter.value = "all";
        activeTag = "";
        applyFilters();
      }});

      for (const button of tagButtons) {{
        button.addEventListener("click", () => {{
          activeTag = activeTag === button.dataset.filterTag ? "" : button.dataset.filterTag;
          applyFilters();
        }});
      }}

      for (const button of inlineTagButtons) {{
        button.addEventListener("click", () => {{
          activeTag = activeTag === button.dataset.tag ? "" : button.dataset.tag;
          applyFilters();
          window.scrollTo({{ top: 0, behavior: "smooth" }});
        }});
      }}

      applyFilters();
    }})();
  </script>
</body>
</html>
""",
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "run_dir": str(run_dir),
                "included_count": len(combined_items),
                "fully_offline_ready_count": len(fully_ready_items),
                "partially_offline_ready_count": len(partially_ready_items),
                "html_path": str(html_path),
                "txt_path": str(txt_path),
                "qa_page_url": f"http://localhost:8000/mirror_runs/{run_dir.name}/reports/{html_path.name}",
                "base_url": args.base_url,
                "search_dir": args.search_dir,
                "query_tagged_games": sum(1 for item in combined_items if item["query_tags"]),
                "featured_tag_count": len(featured_tags),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())