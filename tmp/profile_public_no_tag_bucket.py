#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


ROOT = Path("/Users/hassan/repos/game_agent")
AUDIT_PATH = ROOT / "tmp/generated_metadata_repair_probe_20260521T2227Z/audit.json"
PUBLIC_ROOT = ROOT / "games/published/public"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def metadata_path_for_key(composite_key: str) -> Path:
    game_id, remix_suffix = composite_key.split("__remix-", 1)
    remix_id = f"remix-{remix_suffix}"
    return PUBLIC_ROOT / game_id / remix_id / f"game-obfuscated-{remix_suffix}.json"


def prompt_line(text: str) -> str:
    lines = [line.strip() for line in str(text or "").splitlines() if line.strip()]
    for line in lines:
        if line.startswith("#"):
            continue
        return line
    return ""


def classify_prompt(line: str) -> str:
    normalized = line.lower()
    if "called " in normalized or "called **" in normalized or "called `" in normalized:
        return "called_title"
    if "named " in normalized:
        return "named_title"
    if " as **" in normalized or " as `" in normalized:
        return "as_title"
    if normalized.startswith("create "):
        return "create_title"
    if normalized.startswith("recreate "):
        return "recreate_no_explicit_title"
    return "other"


def main() -> None:
    audit = load_json(AUDIT_PATH)
    keys = audit["public"]["no_tags_keys"]

    semantic_nonempty = 0
    identity_nonempty = 0
    mechanics_nonempty = 0
    alternate_semantic_shapes = 0
    ranked_mechanics_present = 0
    prompt_pattern_counter: Counter[str] = Counter()
    examples: dict[str, list[dict[str, str]]] = {}

    for key in keys:
        metadata = load_json(metadata_path_for_key(key))
        semantic = metadata.get("semantic_tags") if isinstance(metadata.get("semantic_tags"), dict) else {}
        identity = metadata.get("identity") if isinstance(metadata.get("identity"), dict) else {}
        mechanics = metadata.get("mechanics_classification") if isinstance(metadata.get("mechanics_classification"), dict) else {}

        if semantic:
            semantic_nonempty += 1
            if any(k in semantic for k in ["mechanic_tags", "mood_tags", "setting_tags", "presentation_tags", "prompt_requested_tags"]):
                alternate_semantic_shapes += 1
        if identity:
            identity_nonempty += 1
        if mechanics:
            mechanics_nonempty += 1
            if isinstance(mechanics.get("ranked_mechanics"), list) and mechanics.get("ranked_mechanics"):
                ranked_mechanics_present += 1

        first_prompt = prompt_line(metadata.get("recreation_prompt_markdown") or "")
        bucket = classify_prompt(first_prompt)
        prompt_pattern_counter[bucket] += 1
        examples.setdefault(bucket, [])
        if len(examples[bucket]) < 3:
            examples[bucket].append({"key": key, "prompt": first_prompt})

    print(json.dumps(
        {
            "audit_path": str(AUDIT_PATH),
            "no_tags_count": len(keys),
            "structured_presence": {
                "semantic_nonempty": semantic_nonempty,
                "identity_nonempty": identity_nonempty,
                "mechanics_nonempty": mechanics_nonempty,
                "alternate_semantic_shapes": alternate_semantic_shapes,
                "ranked_mechanics_present": ranked_mechanics_present,
            },
            "prompt_pattern_counts": dict(prompt_pattern_counter),
            "prompt_pattern_examples": examples,
        },
        indent=2,
    ))


if __name__ == "__main__":
    main()