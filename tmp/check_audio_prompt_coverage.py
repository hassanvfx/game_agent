#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIBRARY_AUDIO_PATH = ROOT / "tools" / "library" / "audio_library" / "audios.json"
LIBRARY_README_PATH = ROOT / "tools" / "library" / "audio_library" / "README.md"
REFACTORING_AUDIO_PATH = ROOT / "tools" / "game_refactoring" / "catalogs" / "audios.json"
REPORT_PATH = ROOT / "tmp" / "audio_prompt_coverage_report.json"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def strip_variant_suffix(name: str) -> str:
    return re.sub(r"_\d+$", "", name)


def extract_library_prompt_blocks() -> dict[str, str]:
    text = LIBRARY_README_PATH.read_text(encoding="utf-8")
    pattern = re.compile(r"^#### `([^`]+)`\n\n```text\n(.*?)\n```", re.MULTILINE | re.DOTALL)
    return {match.group(1): match.group(2).strip() for match in pattern.finditer(text)}


def main() -> int:
    library = load_json(LIBRARY_AUDIO_PATH)
    refactoring = load_json(REFACTORING_AUDIO_PATH)
    prompt_blocks = extract_library_prompt_blocks()

    library_base_names = sorted(
        {strip_variant_suffix(item["name"]) for items in library.values() for item in items if "name" in item}
    )
    missing_library_prompts = [name for name in library_base_names if name not in prompt_blocks]

    output_dirs = sorted(
        {Path(item.get("location", "")).parts[0] for items in library.values() for item in items if item.get("location")}
    )
    refactoring_missing_usage = [entry.get("query", "") for entry in refactoring if not entry.get("usage", "").strip()]

    report = {
        "summary": {
            "library_prompt_block_count": len(prompt_blocks),
            "library_base_name_count": len(library_base_names),
            "missing_library_prompt_count": len(missing_library_prompts),
            "refactoring_record_count": len(refactoring),
            "refactoring_missing_usage_count": len(refactoring_missing_usage),
        },
        "output_dirs": output_dirs,
        "library_prompt_keys": sorted(prompt_blocks),
        "missing_library_prompts": missing_library_prompts,
        "refactoring_missing_usage": refactoring_missing_usage,
    }

    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"], ensure_ascii=False, indent=2))
    print(f"output_dirs={output_dirs}")
    print(f"wrote {REPORT_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
