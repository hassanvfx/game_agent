#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT_PATH = ROOT / "dashboard.html"
DEFAULT_CATALOG_PATH = ROOT.parent / "sprites_expanded_merge_ready.json"
DEFAULT_LIVE_DIR = ROOT / "live"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render a taxonomy dashboard from a catalog and live asset tree.")
    parser.add_argument("--catalog", default=str(DEFAULT_CATALOG_PATH))
    parser.add_argument("--live-dir", default=str(DEFAULT_LIVE_DIR))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH))
    parser.add_argument("--title", default="Sprites Taxonomy Dashboard")
    return parser.parse_args()


def load_catalog(catalog_path: Path) -> list[dict]:
    return json.loads(catalog_path.read_text())


def query_from_url(url: str) -> str:
    parts = [part for part in url.replace("https://gamezone-virid.vercel.app/", "").split("/") if part]
    if len(parts) >= 2:
        return parts[-2].replace("_", " ")
    return "unknown"


def flatten_catalog(catalog: list[dict]) -> list[dict]:
    items: list[dict] = []

    # Nested taxonomy shape:
    # [{ "query": "...", "sprites_transparent": [...], "backgrounds_opaque": [...] }]
    if catalog and "query" in catalog[0]:
        for entry in catalog:
            query = entry["query"]
            for group_name, asset_kind in (
                ("sprites_transparent", "sprite_transparent"),
                ("backgrounds_opaque", "background_opaque"),
            ):
                for asset in entry.get(group_name, []):
                    path = asset["url"].replace("https://gamezone-virid.vercel.app/", "")
                    items.append(
                        {
                            "query": query,
                            "group": group_name,
                            "asset_kind": asset_kind,
                            "name": asset["name"],
                            "style": asset.get("style", ""),
                            "prompt": asset["prompt"],
                            "usage": asset.get("usage", ""),
                            "output_relpath": path,
                        }
                    )
        return items

    # Flat V2 shape:
    # [{ "name": "...", "url": "...", "style": "...", "usage": "...", "prompt": "..." }]
    for asset in catalog:
        url = asset["url"]
        path = url.replace("https://gamezone-virid.vercel.app/", "")
        is_background = "/backgrounds/" in path
        items.append(
            {
                "query": query_from_url(url),
                "group": "backgrounds_opaque" if is_background else "sprites_transparent",
                "asset_kind": "background_opaque" if is_background else "sprite_transparent",
                "name": asset["name"],
                "style": asset.get("style", ""),
                "prompt": asset["prompt"],
                "usage": asset.get("usage", ""),
                "output_relpath": path,
            }
        )

    return items


def build_dashboard_html(items: list[dict], live_dir: Path, output_path: Path, title: str, catalog_path: Path) -> str:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for item in items:
        grouped[item["query"]].append(item)

    sections = []
    ready_count = 0
    output_root = output_path.parent.resolve()

    for query, query_items in sorted(grouped.items()):
        cards = []
        for item in sorted(query_items, key=lambda row: row["output_relpath"]):
            live_path = live_dir / item["output_relpath"]
            live_src = live_path.relative_to(output_root).as_posix() if live_path.exists() else ""
            is_ready = bool(live_src)
            if is_ready:
                ready_count += 1

            kind_label = "Sprite" if item["asset_kind"] == "sprite_transparent" else "Background"
            prompt_text = html.escape(item["prompt"])
            style_text = html.escape(item["style"])
            name_text = html.escape(item["name"])
            path_text = html.escape(item["output_relpath"])
            query_text = html.escape(query)

            cards.append(
                f"""
                <article class="card">
                  <div class="thumb-wrap">
                    {'<img class="thumb" src="' + live_src + '" alt="' + name_text + '">' if is_ready else '<div class="missing"><strong>Pending</strong><span>Not generated yet</span></div>'}
                  </div>
                  <div class="meta">
                    <div class="topline">
                      <div class="pill">{kind_label}</div>
                      <button class="prompt-button" type="button" data-prompt="{prompt_text}" data-style="{style_text}" data-name="{name_text}" data-query="{query_text}">ⓘ Prompt</button>
                    </div>
                    <h3>{name_text}</h3>
                    <p class="path">{path_text}</p>
                    <p class="status {'ready' if is_ready else 'pending'}">{'Ready' if is_ready else 'Pending'}</p>
                  </div>
                </article>
                """
            )

        sections.append(
            f"""
            <section class="group">
              <h2>{html.escape(query)}</h2>
              <div class="grid">
                {''.join(cards)}
              </div>
            </section>
            """
        )

    total = len(items)
    pending_count = total - ready_count

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{html.escape(title)}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    :root {{
      --bg: #0b1020; --panel: #131a2e; --panel-2: #1a2340; --text: #eef2ff;
      --muted: #9fb0d1; --accent: #62d4ff; --border: #2a355c;
      --success: #67e8a5; --warning: #fbbf24;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin:0; padding:24px; font-family: Inter, ui-sans-serif, system-ui, sans-serif; background:linear-gradient(180deg,#0b1020 0%,#10172a 100%); color:var(--text); }}
    .shell {{ max-width:1550px; margin:0 auto; }}
    .hero {{ background:rgba(19,26,46,0.92); border:1px solid var(--border); border-radius:20px; padding:24px; margin-bottom:24px; box-shadow:0 20px 50px rgba(0,0,0,0.35); }}
    h1 {{ margin:0 0 8px; font-size:32px; }}
    .sub {{ color:var(--muted); margin:0; line-height:1.5; }}
    .stats {{ display:flex; gap:12px; flex-wrap:wrap; margin-top:18px; }}
    .stat {{ background:var(--panel-2); border:1px solid var(--border); border-radius:14px; padding:12px 16px; min-width:180px; }}
    .stat strong {{ display:block; font-size:20px; margin-bottom:4px; }}
    .group {{ margin-bottom:30px; }}
    .group h2 {{ margin:0 0 14px; font-size:24px; text-transform:capitalize; }}
    .grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(280px,1fr)); gap:16px; }}
    .card {{ background:rgba(19,26,46,0.94); border:1px solid var(--border); border-radius:18px; overflow:hidden; box-shadow:0 12px 30px rgba(0,0,0,0.25); }}
    .thumb-wrap {{ height:240px; background:linear-gradient(45deg,#151d33 25%,transparent 25%),linear-gradient(-45deg,#151d33 25%,transparent 25%),linear-gradient(45deg,transparent 75%,#151d33 75%),linear-gradient(-45deg,transparent 75%,#151d33 75%); background-size:24px 24px; background-position:0 0,0 12px,12px -12px,-12px 0px; display:flex; align-items:center; justify-content:center; padding:14px; }}
    .thumb {{ max-width:100%; max-height:100%; object-fit:contain; display:block; }}
    .missing {{ color:var(--muted); display:flex; flex-direction:column; align-items:center; gap:6px; text-transform:uppercase; letter-spacing:0.04em; font-size:12px; text-align:center; }}
    .missing strong {{ color:var(--warning); font-size:14px; }}
    .meta {{ padding:16px; }}
    .topline {{ display:flex; align-items:center; justify-content:space-between; gap:12px; margin-bottom:10px; }}
    .pill {{ display:inline-block; padding:4px 10px; border-radius:999px; background:rgba(98,212,255,0.12); color:var(--accent); font-size:12px; font-weight:700; letter-spacing:0.05em; text-transform:uppercase; }}
    .prompt-button {{ border:1px solid var(--border); background:var(--panel-2); color:var(--text); border-radius:999px; padding:6px 10px; font-size:12px; cursor:pointer; }}
    .prompt-button:hover {{ border-color:var(--accent); color:var(--accent); }}
    .meta h3 {{ margin:0 0 8px; font-size:18px; }}
    .path {{ margin:0 0 8px; color:var(--muted); font-size:12px; word-break:break-all; }}
    .status {{ margin:0; font-size:13px; font-weight:700; }}
    .status.ready {{ color:var(--success); }}
    .status.pending {{ color:var(--warning); }}
    .modal {{ position:fixed; inset:0; background:rgba(3,8,20,0.72); display:none; align-items:center; justify-content:center; padding:20px; }}
    .modal.open {{ display:flex; }}
    .modal-card {{ width:min(760px,100%); background:#10172a; border:1px solid var(--border); border-radius:20px; box-shadow:0 30px 60px rgba(0,0,0,0.45); overflow:hidden; }}
    .modal-head {{ display:flex; justify-content:space-between; align-items:center; padding:18px 20px; border-bottom:1px solid var(--border); }}
    .modal-head h3 {{ margin:0; font-size:20px; }}
    .close-btn {{ border:0; background:transparent; color:var(--muted); font-size:24px; cursor:pointer; }}
    .modal-body {{ padding:20px; display:grid; gap:14px; }}
    .label {{ font-size:12px; text-transform:uppercase; letter-spacing:0.05em; color:var(--muted); margin-bottom:6px; display:block; }}
    .detail-box {{ background:rgba(26,35,64,0.75); border:1px solid var(--border); border-radius:14px; padding:14px; line-height:1.6; white-space:pre-wrap; word-break:break-word; color:#d7def7; }}
  </style>
</head>
<body>
  <main class="shell">
    <header class="hero">
      <h1>{html.escape(title)}</h1>
      <p class="sub">Catalog: <code>{html.escape(str(catalog_path))}</code> · Live root: <code>{html.escape(str(live_dir))}</code>. Missing items stay visible with empty state cards.</p>
      <div class="stats">
        <div class="stat"><strong>{total}</strong><span>Total taxonomy items</span></div>
        <div class="stat"><strong>{sum(1 for item in items if item["asset_kind"] == "sprite_transparent")}</strong><span>Transparent sprites</span></div>
        <div class="stat"><strong>{sum(1 for item in items if item["asset_kind"] == "background_opaque")}</strong><span>Opaque backgrounds</span></div>
        <div class="stat"><strong>{ready_count}</strong><span>Ready in live</span></div>
        <div class="stat"><strong>{pending_count}</strong><span>Pending / empty state</span></div>
        <div class="stat"><strong>{len(grouped)}</strong><span>Queries</span></div>
      </div>
    </header>
    {''.join(sections)}
  </main>

  <div class="modal" id="promptModal" aria-hidden="true">
    <div class="modal-card">
      <div class="modal-head">
        <h3 id="modalTitle">Prompt details</h3>
        <button class="close-btn" type="button" id="closeModal">×</button>
      </div>
      <div class="modal-body">
        <div><span class="label">Style</span><div class="detail-box" id="modalStyle"></div></div>
        <div><span class="label">Prompt</span><div class="detail-box" id="modalPrompt"></div></div>
      </div>
    </div>
  </div>

  <script>
    const modal = document.getElementById('promptModal');
    const modalTitle = document.getElementById('modalTitle');
    const modalStyle = document.getElementById('modalStyle');
    const modalPrompt = document.getElementById('modalPrompt');
    const closeModal = document.getElementById('closeModal');
    document.querySelectorAll('.prompt-button').forEach((button) => {{
      button.addEventListener('click', () => {{
        const name = button.dataset.name || 'Asset';
        const query = button.dataset.query || '';
        modalTitle.textContent = `${{name}} — ${{query}}`;
        modalStyle.textContent = button.dataset.style || 'No style available';
        modalPrompt.textContent = button.dataset.prompt || 'No prompt available';
        modal.classList.add('open');
        modal.setAttribute('aria-hidden', 'false');
      }});
    }});
    closeModal.addEventListener('click', () => {{
      modal.classList.remove('open');
      modal.setAttribute('aria-hidden', 'true');
    }});
    modal.addEventListener('click', (event) => {{
      if (event.target === modal) {{
        modal.classList.remove('open');
        modal.setAttribute('aria-hidden', 'true');
      }}
    }});
  </script>
</body>
</html>
"""


def main() -> None:
    args = parse_args()
    catalog_path = Path(args.catalog).resolve()
    live_dir = Path(args.live_dir).resolve()
    output_path = Path(args.output).resolve()
    catalog = load_catalog(catalog_path)
    items = flatten_catalog(catalog)
    output_path.write_text(build_dashboard_html(items, live_dir, output_path, args.title, catalog_path))
    print(
        json.dumps(
            {
                "ok": True,
                "catalog": str(catalog_path),
                "live_dir": str(live_dir),
                "output": str(output_path),
                "items": len(items),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()