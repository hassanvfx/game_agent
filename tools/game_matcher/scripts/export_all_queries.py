#!/usr/bin/env python3
"""Export the deduped global query vocabulary as a plain JSON string array."""

from __future__ import annotations

import json
from pathlib import Path


def main() -> int:
    consolidated_dir = Path("fixtures/consolidated")
    src = consolidated_dir / "master_query_to_games_index.json"
    dst = consolidated_dir / "all_queries.json"

    payload = json.loads(src.read_text(encoding="utf-8"))
    queries = sorted({item["query"] for item in payload.get("queries", []) if item.get("query")})
    dst.write_text(json.dumps(queries, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(json.dumps({"output_path": str(dst), "query_count": len(queries)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())