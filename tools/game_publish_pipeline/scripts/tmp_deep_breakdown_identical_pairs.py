#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path


REPORT_PATH = Path("tmp/identical_public_obfuscated_report.json")


def bucket_path_kind(rel_path: Path) -> str:
    name = rel_path.name
    suffix = rel_path.suffix.lower()
    if name == "index.html":
        return "index.html"
    if suffix == ".html":
        return "other_html"
    if suffix == ".js":
        return "js"
    if suffix == ".css":
        return "css"
    return suffix or "<no_ext>"


def main() -> int:
    if not REPORT_PATH.is_file():
        print(f"Missing report: {REPORT_PATH}")
        print("Run detector first with --report-path tmp/identical_public_obfuscated_report.json")
        return 1

    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    paths = [Path(p) for p in report.get("identical_paths", [])]

    ext_counts = Counter(p.suffix.lower() for p in paths)
    kind_counts = Counter(bucket_path_kind(p) for p in paths)
    filename_counts = Counter(p.name for p in paths)

    by_game = Counter()
    by_game_kinds: dict[str, Counter[str]] = defaultdict(Counter)
    for p in paths:
        parts = p.parts
        game_id = parts[0] if parts and parts[0].startswith("gamezone-") else "<root>"
        kind = bucket_path_kind(p)
        by_game[game_id] += 1
        by_game_kinds[game_id][kind] += 1

    game_counts = [count for game, count in by_game.items() if game != "<root>"]
    game_count = len(game_counts)
    avg_per_game = (sum(game_counts) / game_count) if game_count else 0

    print("== Deep Breakdown: Identical Public vs Obfuscated Pairs ==")
    print(f"Report: {REPORT_PATH.resolve()}")
    print(f"Identical pairs total: {len(paths)}")
    print(f"Comparable pairs: {report.get('comparable_pairs', 0)}")
    if report.get("comparable_pairs"):
        pct = (len(paths) / report["comparable_pairs"]) * 100
        print(f"Identical rate: {pct:.2f}%")

    print("\nBy extension:")
    for ext, count in sorted(ext_counts.items(), key=lambda x: (-x[1], x[0])):
        label = ext or "<no_ext>"
        print(f"  {label}: {count}")

    print("\nBy kind:")
    for kind, count in sorted(kind_counts.items(), key=lambda x: (-x[1], x[0])):
        print(f"  {kind}: {count}")

    print("\nTop identical filenames:")
    for name, count in filename_counts.most_common(12):
        print(f"  {name}: {count}")

    print("\nPer-game concentration:")
    print(f"  Games with >=1 identical pair: {game_count}")
    if game_count:
        print(f"  Avg identical pairs per affected game: {avg_per_game:.2f}")
        print(f"  Max identical pairs in one game: {max(game_counts)}")

    print("\nTop affected game IDs (with kind mix):")
    for game_id, total in by_game.most_common(12):
        if game_id == "<root>":
            continue
        kinds = by_game_kinds[game_id]
        top_mix = ", ".join(f"{k}:{v}" for k, v in kinds.most_common(3))
        print(f"  {game_id}: {total} ({top_mix})")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
