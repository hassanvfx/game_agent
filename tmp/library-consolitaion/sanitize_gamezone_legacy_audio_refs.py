#!/usr/bin/env python3
"""One-time sanitization pass for legacy/outlier audio refs in published gamezone folders."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GAMES_ROOT = ROOT / "games"
OUTPUT_REPORT = ROOT / "tmp" / "library-consolitaion" / "gamezone_legacy_audio_sanitization_report.json"
TEXT_SUFFIXES = {".html", ".js", ".css", ".json", ".txt", ".md"}

LEGACY_AUDIO_RE = re.compile(
    r"assets/(?:bgm/0001/|sfx/0001/|audio/0000/)[^\"'()\s<>]+\.mp3"
)


def candidate_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for gamezone_dir in sorted(root.rglob("gamezone-*")):
        if not gamezone_dir.is_dir():
            continue
        for path in gamezone_dir.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix.lower() in TEXT_SUFFIXES:
                files.append(path)
    return files


def sanitize_text(text: str) -> tuple[str, list[str]]:
    matches = LEGACY_AUDIO_RE.findall(text)
    if not matches:
        return text, []
    sanitized = LEGACY_AUDIO_RE.sub("", text)
    return sanitized, matches


def main() -> int:
    scanned_files = 0
    changed_files = 0
    total_replacements = 0
    changed_entries: list[dict[str, object]] = []

    for path in candidate_files(GAMES_ROOT):
        scanned_files += 1
        try:
            original = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        sanitized, matches = sanitize_text(original)
        if not matches:
            continue

        path.write_text(sanitized, encoding="utf-8")
        changed_files += 1
        total_replacements += len(matches)
        changed_entries.append(
            {
                "path": str(path.relative_to(ROOT)),
                "replacement_count": len(matches),
                "replacements": matches,
            }
        )

    payload = {
        "games_root": str(GAMES_ROOT.relative_to(ROOT)),
        "scanned_file_count": scanned_files,
        "changed_file_count": changed_files,
        "total_replacements": total_replacements,
        "changed_entries": changed_entries,
    }
    OUTPUT_REPORT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"wrote {OUTPUT_REPORT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())