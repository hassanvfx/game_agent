from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise RuntimeError(f"Missing expected text for {label}")
    return text.replace(old, new, 1)


path = Path("tools/game_refactoring/prompts/operators_v2/00_creative_remix_v6_semantic_inference_plus.md")
text = path.read_text()

text = replace_once(
    text,
    "## Remix v4 Shared Context",
    "## Remix v6 Shared Context",
    "shared context header",
)
text = replace_once(
    text,
    "Remix v4 in brief:",
    "Remix v6 in brief:",
    "shared context summary",
)
text = replace_once(
    text,
    "You are performing the first v4 planning pass. This stage replaces the old split between early remix inference and late level adaptation. It must infer the game, decompose its mechanics, choose a safe remix direction, and produce a complete five-level progression plan before downstream stages touch the presentation.",
    "You are performing the v6 semantic planning pass. This stage establishes source truth, decomposes mechanics, chooses a safe remix direction, and produces the semantic regeneration brief that the downstream super operator must rebuild from.",
    "stage intro paragraph 1",
)
text = replace_once(
    text,
    "This is not a short summary stage. It is a comprehensive planning harness. Preserve the full power of the source prompts while removing the old problem where level reasoning arrived too late in the workflow.",
    "This is not a short summary stage. It is a comprehensive planning harness. Preserve the full power of the source prompts while shifting v6 away from legacy runtime preservation and toward semantic-first regeneration.",
    "stage intro paragraph 2",
)

path.write_text(text)
print("Polished v6 semantic intro wording.")