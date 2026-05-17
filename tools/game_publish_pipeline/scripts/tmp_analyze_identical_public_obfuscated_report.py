#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


REPORT_PATH = Path("tmp/identical_public_obfuscated_report.json")


def main() -> int:
    if not REPORT_PATH.is_file():
        print(f"Report not found: {REPORT_PATH}")
        print("Run detector first with --report-path tmp/identical_public_obfuscated_report.json")
        return 1

    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    paths = report.get("identical_paths", [])

    ext_counts = Counter(Path(p).suffix.lower() for p in paths)
    index_count = sum(1 for p in paths if p == "index.html" or p.endswith("/index.html"))
    annotator_count = sum(1 for p in paths if p == "annotator.html" or p.endswith("/annotator.html"))
    appledouble_count = sum(1 for p in paths if "/._" in p or Path(p).name.startswith("._"))

    asset_domain_counts = Counter()
    for p in paths:
        parts = Path(p).parts
        if len(parts) >= 5 and parts[2] == "assets":
            # gamezone-*/remix-*/assets/<domain>/...
            asset_domain_counts[parts[3]] += 1

    by_game = Counter()
    for p in paths:
        parts = Path(p).parts
        if parts and parts[0].startswith("gamezone-"):
            by_game[parts[0]] += 1

    print("== Identical Public vs Obfuscated Report Analysis ==")
    print(f"Report: {REPORT_PATH.resolve()}")
    print(f"Scanned public files: {report.get('scanned_public_files', 0)}")
    print(f"Comparable pairs: {report.get('comparable_pairs', 0)}")
    print(f"Identical pairs: {report.get('identical_pairs', 0)}")
    print(f"Missing in obfuscated: {report.get('missing_in_obfuscated', 0)}")

    print("\nBy extension:")
    for ext, count in sorted(ext_counts.items(), key=lambda item: (-item[1], item[0])):
        label = ext or "<no-extension>"
        print(f"  {label}: {count}")

    print("\nSpecial counts:")
    print(f"  index.html entries: {index_count}")
    print(f"  annotator.html entries: {annotator_count}")
    print(f"  AppleDouble (._*) entries: {appledouble_count}")

    print("\nTop asset domains among identical files:")
    for domain, count in asset_domain_counts.most_common(10):
        print(f"  {domain}: {count}")

    print("\nTop game IDs by identical-file count:")
    for game_id, count in by_game.most_common(10):
        print(f"  {game_id}: {count}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
