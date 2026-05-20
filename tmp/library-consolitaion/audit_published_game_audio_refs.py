#!/usr/bin/env python3
"""Audit published game audio references against the library catalog.

Scans `games/published/obfuscated/gamezone*` folders for `*.mp3` references,
builds a usage map, and compares the discovered references against the current
library artifacts under `tools/library/assets/audios`.
"""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
PUBLISHED_ROOT = ROOT / "games" / "published" / "obfuscated"
LIBRARY_ROOT = ROOT / "tools" / "library" / "assets" / "audios"
OUTPUT_PATH = ROOT / "tmp" / "library-consolitaion" / "published_game_audio_ref_audit.json"

MP3_REF_RE = re.compile(r"[^\"'\s<>()]+\.mp3(?:\?[^\"'\s<>()]*)?")
GAMEZONE_RE = re.compile(r"^gamezone")
TEXT_SUFFIXES = {
    ".html",
    ".js",
    ".mjs",
    ".cjs",
    ".json",
    ".css",
    ".txt",
    ".map",
    ".md",
    ".svg",
}
MAX_BYTES = 2_000_000


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def looks_textual(path: Path) -> bool:
    if path.suffix.lower() in TEXT_SUFFIXES:
        return True
    try:
        sample = path.read_bytes()[:1024]
    except OSError:
        return False
    return b"\0" not in sample


def extract_gamezone_folder(path: Path) -> str | None:
    for part in path.parts:
        if GAMEZONE_RE.match(part):
            return part
    return None


def normalize_mp3_ref(ref: str) -> dict[str, str | None]:
    raw = ref.strip("'\" ")
    parsed = urlparse(raw)
    path_part = parsed.path or raw
    if "assets/audios/" in path_part:
        after = path_part.split("assets/audios/", 1)[1]
        return {
            "kind": "library_cdn",
            "normalized_location": after,
            "normalized_full_path": f"assets/audios/{after}",
            "basename": Path(after).name,
        }
    return {
        "kind": "other_mp3",
        "normalized_location": None,
        "normalized_full_path": path_part.lstrip("/"),
        "basename": Path(path_part).name,
    }


def classify_source_role(path: Path) -> str:
    path_str = str(path).replace("\\", "/")
    if "/artifacts/simple_obfuscation_report.json" in path_str:
        return "artifact_report"
    if "/artifacts/" in path_str:
        return "artifact_other"
    if path.suffix.lower() in {".html", ".js", ".mjs", ".cjs", ".css"}:
        return "runtime_source"
    return "other_text_source"


def collect_library_locations() -> dict[str, set[str]]:
    audios = load_json(LIBRARY_ROOT / "audios.json")
    catalog_final = load_json(LIBRARY_ROOT / "catalog_final.json")

    audios_locations: set[str] = set()
    audios_basenames: set[str] = set()
    for items in audios.values():
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, dict):
                continue
            location = item.get("location")
            if isinstance(location, str) and location:
                audios_locations.add(location)
                audios_basenames.add(Path(location).name)

    catalog_locations: set[str] = set()
    catalog_basenames: set[str] = set()
    semantic_paths: set[str] = set()
    for record in catalog_final.get("records", []):
        if not isinstance(record, dict):
            continue
        for variant in record.get("variants", []) or []:
            if not isinstance(variant, dict):
                continue
            location = variant.get("location")
            if isinstance(location, str) and location:
                catalog_locations.add(location)
                catalog_basenames.add(Path(location).name)
        for item in record.get("reference_items", []) or []:
            if not isinstance(item, dict):
                continue
            url = item.get("url")
            if not isinstance(url, str) or not url:
                continue
            path_part = urlparse(url).path.lstrip("/")
            if "assets/audios/" in path_part:
                semantic_paths.add(path_part)
                trimmed = path_part.split("assets/audios/", 1)[1]
                catalog_locations.add(trimmed)
                catalog_basenames.add(Path(trimmed).name)

    return {
        "audios_locations": audios_locations,
        "audios_basenames": audios_basenames,
        "catalog_locations": catalog_locations,
        "catalog_basenames": catalog_basenames,
        "semantic_paths": semantic_paths,
    }


def classify_reference(ref_meta: dict[str, str | None], library: dict[str, set[str]]) -> str:
    location = ref_meta["normalized_location"]
    full_path = ref_meta["normalized_full_path"]
    basename = ref_meta["basename"]
    if location and location in library["audios_locations"]:
        return "exact_audios_location_match"
    if location and location in library["catalog_locations"]:
        return "exact_catalog_location_match"
    if basename and basename in library["audios_basenames"]:
        return "basename_only_audios_match"
    if basename and basename in library["catalog_basenames"]:
        return "basename_only_catalog_match"
    if full_path and full_path.startswith("assets/audios/"):
        return "cdn_library_path_missing_from_catalog"
    if full_path and full_path.startswith("assets/audio/"):
        return "obfuscated_local_audio_asset"
    return "other_mp3_reference"


def audit() -> dict:
    library = collect_library_locations()

    refs: list[dict] = []
    files_scanned = 0
    files_with_mp3_refs = 0
    game_folders_seen: set[str] = set()

    for game_dir in sorted(PUBLISHED_ROOT.iterdir()):
        if not game_dir.is_dir() or not GAMEZONE_RE.match(game_dir.name):
            continue
        game_folders_seen.add(game_dir.name)

    for path in sorted(PUBLISHED_ROOT.rglob("*")):
        if not path.is_file():
            continue
        gamezone_folder = extract_gamezone_folder(path.relative_to(PUBLISHED_ROOT))
        if not gamezone_folder:
            continue
        try:
            if path.stat().st_size > MAX_BYTES:
                continue
        except OSError:
            continue
        if not looks_textual(path):
            continue

        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue

        files_scanned += 1
        if ".mp3" not in text:
            continue
        file_had_ref = False
        for lineno, line in enumerate(text.splitlines(), 1):
            matches = MP3_REF_RE.findall(line)
            if not matches:
                continue
            file_had_ref = True
            for match in matches:
                ref_meta = normalize_mp3_ref(match)
                refs.append(
                    {
                        "gamezone_folder": gamezone_folder,
                        "source_file": str(path.relative_to(ROOT)),
                        "source_role": classify_source_role(path),
                        "line": lineno,
                        "reference": match,
                        **ref_meta,
                        "classification": classify_reference(ref_meta, library),
                    }
                )
        if file_had_ref:
            files_with_mp3_refs += 1

    unique_refs = {(
        ref["gamezone_folder"],
        ref["source_file"],
        ref["line"],
        ref["reference"],
    ): ref for ref in refs}
    refs = list(unique_refs.values())

    by_classification = Counter(ref["classification"] for ref in refs)
    by_source_role = Counter(ref["source_role"] for ref in refs)
    by_game = Counter(ref["gamezone_folder"] for ref in refs)
    by_basename = Counter(ref["basename"] for ref in refs if ref.get("basename"))
    mismatches = [
        ref for ref in refs
        if ref["classification"] not in {
            "exact_audios_location_match",
            "exact_catalog_location_match",
        }
    ]
    runtime_refs = [ref for ref in refs if ref["source_role"] == "runtime_source"]
    runtime_mismatches = [
        ref for ref in runtime_refs
        if ref["classification"] not in {
            "exact_audios_location_match",
            "exact_catalog_location_match",
        }
    ]
    runtime_by_classification = Counter(ref["classification"] for ref in runtime_refs)

    games_by_audio: dict[str, set[str]] = defaultdict(set)
    files_by_audio: dict[str, set[str]] = defaultdict(set)
    for ref in refs:
        key = ref.get("normalized_location") or ref.get("normalized_full_path") or ref["reference"]
        games_by_audio[key].add(ref["gamezone_folder"])
        files_by_audio[key].add(ref["source_file"])

    top_audio_usage = []
    for key, games in sorted(games_by_audio.items(), key=lambda item: (-len(item[1]), item[0]))[:50]:
        top_audio_usage.append(
            {
                "audio_key": key,
                "games": sorted(games),
                "game_count": len(games),
                "file_count": len(files_by_audio[key]),
            }
        )

    return {
        "published_root": str(PUBLISHED_ROOT.relative_to(ROOT)),
        "library_root": str(LIBRARY_ROOT.relative_to(ROOT)),
        "summary": {
            "gamezone_folder_count": len(game_folders_seen),
            "files_scanned": files_scanned,
            "files_with_mp3_refs": files_with_mp3_refs,
            "reference_count": len(refs),
            "mismatch_count": len(mismatches),
            "source_role_counts": dict(by_source_role),
            "classification_counts": dict(by_classification),
        },
        "runtime_summary": {
            "reference_count": len(runtime_refs),
            "mismatch_count": len(runtime_mismatches),
            "classification_counts": dict(runtime_by_classification),
        },
        "top_games_by_reference_count": [
            {"gamezone_folder": game, "reference_count": count}
            for game, count in by_game.most_common(50)
        ],
        "top_audio_basenames": [
            {"basename": name, "reference_count": count}
            for name, count in by_basename.most_common(50)
        ],
        "top_audio_usage": top_audio_usage,
        "runtime_mismatches": runtime_mismatches[:5000],
        "mismatches": mismatches[:5000],
        "references": refs[:5000],
    }


def main() -> int:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = audit()
    OUTPUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload["summary"], ensure_ascii=False, indent=2))
    print(f"wrote {OUTPUT_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())