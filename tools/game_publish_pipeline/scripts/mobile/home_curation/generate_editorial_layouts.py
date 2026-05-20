#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

DEFAULT_CANDIDATES_PATH = Path("JabaliApp/Assets/editorial_phase3_candidates.json")
DEFAULT_OUT_PATH = Path("JabaliApp/Assets/editorial_layouts.json")
ROW_TYPES = [1, 2, 4, 5, 6]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate mixed-theme editorial layout pages from editorial candidate collections."
    )
    parser.add_argument(
        "--candidates",
        type=Path,
        default=DEFAULT_CANDIDATES_PATH,
        help="Path to editorial_phase3_candidates.json",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_OUT_PATH,
        help="Output path for editorial_layouts.json",
    )
    return parser.parse_args()


def load_candidates(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text())
    collections = payload.get("collections", [])
    if not isinstance(collections, list) or not collections:
        raise ValueError(f"No collections found in {path}")
    return collections


def build_layouts(collections: list[dict[str, Any]]) -> list[dict[str, Any]]:
    collections_by_size: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for collection in collections:
        size = int(collection["size"])
        collections_by_size[size].append(collection)

    missing_sizes = [size for size in ROW_TYPES if not collections_by_size.get(size)]
    if missing_sizes:
        raise ValueError(f"Missing collections for row sizes: {missing_sizes}")

    page_count = min(len(collections_by_size[size]) for size in ROW_TYPES)
    layouts: list[dict[str, Any]] = []

    for page_index in range(page_count):
        rows: list[dict[str, Any]] = []
        seen_themes: set[str] = set()

        for row_type in ROW_TYPES:
            size_bucket = collections_by_size[row_type]
            selected = None

            for offset in range(len(size_bucket)):
                candidate = size_bucket[(page_index + offset) % len(size_bucket)]
                theme = str(candidate["theme"])
                if theme in seen_themes:
                    continue
                selected = candidate
                seen_themes.add(theme)
                break

            if selected is None:
                selected = size_bucket[page_index % len(size_bucket)]
                seen_themes.add(str(selected["theme"]))

            rows.append(
                {
                    "type": row_type,
                    "collection_id": selected["id"],
                }
            )

        layouts.append(
            {
                "id": f"layout-{page_index + 1:02d}",
                "rows": rows,
            }
        )

    return layouts


def main() -> None:
    args = parse_args()
    collections = load_candidates(args.candidates)
    layouts = build_layouts(collections)

    payload = {
        "version": 2,
        "source_collections": args.candidates.name,
        "row_types": ROW_TYPES,
        "layouts": layouts,
    }

    args.out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {args.out}")
    print(f"Generated {len(layouts)} layouts")
    for layout in layouts[:5]:
        print(layout["id"], [row["collection_id"] for row in layout["rows"]])


if __name__ == "__main__":
    main()