from pathlib import Path
from collections import Counter
import json
import re


ROOT = Path(__file__).resolve().parent
REPORT_PATH = ROOT / "tmp_audio_usage_report.json"
MEDIA_SUFFIXES = {".mp3", ".wav", ".ogg", ".m4a", ".aac"}

TAG_RE = re.compile(r"<audio\b[^>]*>", re.IGNORECASE | re.DOTALL)
ATTR_RE = re.compile(r"([:\w-]+)\s*=\s*\"([^\"]*)\"", re.IGNORECASE)
ASSIGN_RE = re.compile(
    r"(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*document\.getElementById\([\"']([^\"']+)[\"']\)",
    re.IGNORECASE,
)
DIRECT_PLAY_RE = re.compile(r"document\.getElementById\([\"']([^\"']+)[\"']\)\.play\s*\(", re.IGNORECASE)
DIRECT_PAUSE_RE = re.compile(r"document\.getElementById\([\"']([^\"']+)[\"']\)\.pause\s*\(", re.IGNORECASE)
DIRECT_RESET_RE = re.compile(r"document\.getElementById\([\"']([^\"']+)[\"']\)\.currentTime\s*=\s*0", re.IGNORECASE)
VAR_PLAY_RE = re.compile(r"\b([A-Za-z_$][\w$]*)\.play\s*\(", re.IGNORECASE)
VAR_PAUSE_RE = re.compile(r"\b([A-Za-z_$][\w$]*)\.pause\s*\(", re.IGNORECASE)
VAR_RESET_RE = re.compile(r"\b([A-Za-z_$][\w$]*)\.currentTime\s*=\s*0", re.IGNORECASE)


def is_media_file(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in MEDIA_SUFFIXES


def find_index_files(root: Path):
    files = []
    for path in root.rglob("index.html"):
        if "bundle" in path.parts:
            continue
        files.append(path)
    return sorted(files)


def parse_audio_tags(text: str):
    items = []
    for match in TAG_RE.finditer(text):
        tag = match.group(0)
        attrs = {key.lower(): value for key, value in ATTR_RE.findall(tag)}
        if "id" not in attrs or "src" not in attrs:
            continue
        items.append(
            {
                "id": attrs["id"],
                "src": attrs["src"],
                "preload": attrs.get("preload", ""),
                "loop": bool(re.search(r"\bloop\b", tag, re.IGNORECASE)),
            }
        )
    return items


def category_for_src(src: str) -> str:
    lowered = src.lower()
    if "/assets/audios/ui/" in lowered:
        return "ui"
    if "/assets/audios/sfx/" in lowered:
        return "sfx"
    if "/assets/audios/music/" in lowered:
        return "music"
    if "/assets/audios/bgm/" in lowered:
        return "bgm"
    if "/assets/audios/ambience/" in lowered:
        return "ambience"
    if "/assets/audio/" in lowered or "/assets/audios/" in lowered:
        return "local_hashed_or_local"
    return "other"


def audio_file_count(game_dir: Path) -> int:
    count = 0
    for subdir in (game_dir / "assets" / "audio", game_dir / "assets" / "audios"):
        if not subdir.exists():
            continue
        for path in subdir.rglob("*"):
            if is_media_file(path):
                count += 1
    return count


def analyze_file(index_path: Path):
    text = index_path.read_text(errors="ignore")
    game_dir = index_path.parent
    tags = parse_audio_tags(text)
    tag_ids = [tag["id"] for tag in tags]
    categories = Counter(category_for_src(tag["src"]) for tag in tags)
    variable_map = {match.group(1): match.group(2) for match in ASSIGN_RE.finditer(text)}

    play_by_id = Counter()
    pause_by_id = Counter()
    reset_by_id = Counter()

    for audio_id in tag_ids:
        play_by_id[audio_id] += len(re.findall(rf"\b{re.escape(audio_id)}\.play\s*\(", text))
        pause_by_id[audio_id] += len(re.findall(rf"\b{re.escape(audio_id)}\.pause\s*\(", text))
        reset_by_id[audio_id] += len(re.findall(rf"\b{re.escape(audio_id)}\.currentTime\s*=\s*0", text))

    for match in DIRECT_PLAY_RE.finditer(text):
        play_by_id[match.group(1)] += 1
    for match in DIRECT_PAUSE_RE.finditer(text):
        pause_by_id[match.group(1)] += 1
    for match in DIRECT_RESET_RE.finditer(text):
        reset_by_id[match.group(1)] += 1

    for match in VAR_PLAY_RE.finditer(text):
        audio_id = variable_map.get(match.group(1))
        if audio_id:
            play_by_id[audio_id] += 1
    for match in VAR_PAUSE_RE.finditer(text):
        audio_id = variable_map.get(match.group(1))
        if audio_id:
            pause_by_id[audio_id] += 1
    for match in VAR_RESET_RE.finditer(text):
        audio_id = variable_map.get(match.group(1))
        if audio_id:
            reset_by_id[audio_id] += 1

    approx_play_calls = sum(play_by_id.values())
    preload_auto_count = sum(1 for tag in tags if tag["preload"].lower() == "auto")
    preload_none_count = sum(1 for tag in tags if tag["preload"].lower() == "none")
    loop_count = sum(1 for tag in tags if tag["loop"])
    remote_audio_refs = sum(1 for tag in tags if tag["src"].startswith("http://") or tag["src"].startswith("https://"))
    local_audio_refs = len(tags) - remote_audio_refs
    local_audio_files = audio_file_count(game_dir)
    uses_audio_context = bool(re.search(r"AudioContext|webkitAudioContext", text))
    uses_new_audio = bool(re.search(r"new\s+Audio\s*\(", text))
    uses_clone_node = bool(re.search(r"cloneNode\s*\(", text))

    notes = []
    if local_audio_files and not local_audio_refs and remote_audio_refs:
        notes.append("bundled local audio exists but active HTML audio refs are remote URLs")
    if preload_auto_count >= 4:
        notes.append("many eager preloads may increase startup/decode pressure")
    if categories.get("ui", 0) + categories.get("sfx", 0) >= 4 and approx_play_calls >= 4:
        notes.append("heavy UI/SFX surface likely to overlap during play")
    if loop_count >= 1 and approx_play_calls >= 4:
        notes.append("mixes looping audio with multiple one-shot play paths")

    risk_score = (
        len(tags) * 2
        + preload_auto_count * 2
        + approx_play_calls
        + remote_audio_refs
        + (3 if uses_audio_context else 0)
        + (2 if uses_new_audio else 0)
        + (2 if uses_clone_node else 0)
        + (4 if local_audio_files and not local_audio_refs and remote_audio_refs else 0)
    )

    return {
        "relative_path": str(index_path.relative_to(ROOT)),
        "audio_tag_count": len(tags),
        "unique_sources": len({tag["src"] for tag in tags}),
        "categories": dict(sorted(categories.items())),
        "preload_auto_count": preload_auto_count,
        "preload_none_count": preload_none_count,
        "loop_count": loop_count,
        "remote_audio_refs": remote_audio_refs,
        "local_audio_refs": local_audio_refs,
        "local_audio_files": local_audio_files,
        "approx_play_calls": approx_play_calls,
        "approx_pause_calls": sum(pause_by_id.values()),
        "approx_reset_calls": sum(reset_by_id.values()),
        "uses_audio_context": uses_audio_context,
        "uses_new_audio": uses_new_audio,
        "uses_clone_node": uses_clone_node,
        "risk_score": risk_score,
        "notes": notes,
        "audio_ids": [
            {
                "id": tag["id"],
                "src": tag["src"],
                "category": category_for_src(tag["src"]),
                "preload": tag["preload"],
                "loop": tag["loop"],
                "approx_play_calls": play_by_id.get(tag["id"], 0),
                "approx_pause_calls": pause_by_id.get(tag["id"], 0),
                "approx_reset_calls": reset_by_id.get(tag["id"], 0),
            }
            for tag in tags
        ],
    }


def main():
    index_files = find_index_files(ROOT)
    results = [analyze_file(path) for path in index_files]
    results.sort(key=lambda item: (-item["risk_score"], item["relative_path"]))

    summary = {
        "games_scanned": len(results),
        "games_with_audio": sum(1 for item in results if item["audio_tag_count"] > 0),
        "total_audio_tags": sum(item["audio_tag_count"] for item in results),
        "total_remote_audio_refs": sum(item["remote_audio_refs"] for item in results),
        "total_local_audio_refs": sum(item["local_audio_refs"] for item in results),
        "total_local_audio_files": sum(item["local_audio_files"] for item in results),
        "total_approx_play_calls": sum(item["approx_play_calls"] for item in results),
    }

    report = {"summary": summary, "top_risk_pages": results[:20], "all_pages": results}
    REPORT_PATH.write_text(json.dumps(report, indent=2))

    print(f"Scanned pages: {summary['games_scanned']}")
    print(f"Pages with audio tags: {summary['games_with_audio']}")
    print(f"Total audio tags: {summary['total_audio_tags']}")
    print(f"Total remote audio refs: {summary['total_remote_audio_refs']}")
    print(f"Total local audio refs: {summary['total_local_audio_refs']}")
    print(f"Total bundled local audio files: {summary['total_local_audio_files']}")
    print(f"Approx play() calls discovered: {summary['total_approx_play_calls']}")
    print("")
    print("Top heuristic audio-risk pages:")
    for item in results[:10]:
        cats = ", ".join(f"{k}:{v}" for k, v in item["categories"].items()) or "none"
        print(
            f"- risk={item['risk_score']:>3} tags={item['audio_tag_count']:<2} plays={item['approx_play_calls']:<2} "
            f"preload_auto={item['preload_auto_count']:<2} remote={item['remote_audio_refs']:<2} "
            f"local_files={item['local_audio_files']:<2} :: {item['relative_path']} :: {cats}"
        )
        for note in item["notes"]:
            print(f"    note: {note}")

    target = None
    for item in results:
        if item["relative_path"].startswith("gamezone-0a01fa77-8b8b-4c02-93db-07cf4e05ee06/"):
            target = item
            break
    if target is None and results:
        target = results[0]

    if target:
        print("")
        print("Representative page detail:")
        print(f"- page: {target['relative_path']}")
        print(f"- tags: {target['audio_tag_count']}, approx plays: {target['approx_play_calls']}, remote refs: {target['remote_audio_refs']}")
        for audio in target["audio_ids"]:
            print(
                f"  - {audio['id']} :: {audio['category']} :: preload={audio['preload'] or 'default'} "
                f"loop={audio['loop']} plays≈{audio['approx_play_calls']} :: {audio['src']}"
            )

    print("")
    print(f"Report written to: {REPORT_PATH}")


if __name__ == "__main__":
    main()