#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CATALOGS_DIR = ROOT / "catalogs" / "skills"
PROMPTS_DIR = ROOT / "prompts" / "operators_v2"
OUTPUT_PROMPT = PROMPTS_DIR / "00_creative_remix_v5_super_operator.md"
DIRECT_REBUILD_PROMPT = PROMPTS_DIR / "01_remix_v4_clone_rebuild_from_blueprint_and_old_refs.md"
SKILL_TYPES_PATH = CATALOGS_DIR / "skill_types.json"

PHASE_LAYOUT: list[tuple[str, list[str]]] = [
    ("Phase 0 — Governing Doctrine and Operator Contract", ["core"]),
    ("Phase 1 — Source Truth, Blueprint, and Progression Planning", ["analysis"]),
    ("Phase 3 — Authored World, Design-System, and Media Mapping", ["world", "media"]),
    ("Phase 4 — Procedural Visual Realization and Mobile-Safe Presentation", ["visual"]),
    ("Phase 5 — Runtime Proof, Before/After Evidence, and Optional Family Validation", ["qa"]),
]

PHASE_INTROS: dict[str, str] = {
    "Phase 0 — Governing Doctrine and Operator Contract": (
        "This phase defines the operator's governing mind: what it is, how it decides, what it must never violate, and how `#PROMPT#` must propagate across every later phase."
    ),
    "Phase 1 — Source Truth, Blueprint, and Progression Planning": (
        "This phase prepares the regeneration spine by establishing current-game truth, protected mechanics, safe theming surfaces, progression logic, and downstream contracts. Use `#PROMPT#` to interpret what the existing game is being asked to become without losing mechanic truth."
    ),
    "Phase 3 — Authored World, Design-System, and Media Mapping": (
        "This phase enriches the rebuilt surface with mechanic-aware world semantics, design-system continuity, and governed media decisions. Use `#PROMPT#` to steer narrative/world meaning, HUD language, palette logic, and media mood."
    ),
    "Phase 4 — Procedural Visual Realization and Mobile-Safe Presentation": (
        "This phase realizes the rebuilt game visually through procedural, browser-native execution while preserving readability, control safety, and authored identity. Use `#PROMPT#` to derive focal identity, motifs, palette, scene ownership, and background language."
    ),
    "Phase 5 — Runtime Proof, Before/After Evidence, and Optional Family Validation": (
        "This phase proves the rebuilt game with runtime evidence, deterministic repair, before/after comparison, and optional family-level validation when multiple playable surfaces exist. Use `#PROMPT#` as an explicit judging lens, not just a setup input."
    ),
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def bullet_list(values: list[str] | None) -> str:
    if not values:
        return "- NONE"
    return "\n".join(f"- {value}" for value in values)


def render_skill(skill: dict[str, Any]) -> str:
    parts = [
        f"#### {skill['id']} — {skill['title']}",
        f"**Intent:** {skill['intent']}",
    ]
    use_when = skill.get("use_when") or []
    if use_when:
        parts.extend(["**Use when:**", bullet_list(use_when)])
    parts.extend(
        [
            "**Required actions:**",
            bullet_list(skill.get("required_actions") or []),
            "**Required artifacts:**",
            bullet_list(skill.get("required_artifacts") or []),
            "**Acceptance bar:**",
            bullet_list(skill.get("acceptance_bar") or []),
            "**Failure modes prevented:**",
            bullet_list(skill.get("failure_modes_prevented") or []),
        ]
    )
    return "\n\n".join(parts)


def render_catalog(catalog: dict[str, Any], catalog_path: Path) -> str:
    lines = [
        f"### Catalog `{catalog_path.name}`",
        f"**Skill type:** `{catalog['skill_type']}`",
        f"**Namespace:** `{catalog['namespace']}`",
        f"**Description:** {catalog['description']}",
        "**Source prompt files:**",
        bullet_list(catalog.get("source_prompt_files") or []),
    ]
    notes = catalog.get("notes") or []
    if notes:
        lines.extend(["**Notes:**", bullet_list(notes)])

    for subgroup in catalog.get("subgroups", []):
        lines.append(f"#### Subgroup `{subgroup['id']}` — {subgroup['title']}")
        for skill in subgroup.get("skills", []):
            lines.append(render_skill(skill))

    return "\n\n".join(lines)


def read_skill_catalogs() -> tuple[list[str], dict[str, dict[str, Any]]]:
    skill_types_payload = load_json(SKILL_TYPES_PATH)
    ordered_skill_types = [entry["id"] for entry in skill_types_payload["skill_types"]]
    catalogs: dict[str, dict[str, Any]] = {}
    for skill_type in ordered_skill_types:
        catalog_path = CATALOGS_DIR / f"remix_v5_{skill_type}_skills.json"
        if not catalog_path.exists():
            raise FileNotFoundError(f"Missing expected skill catalog: {catalog_path}")
        catalogs[skill_type] = {
            "path": catalog_path,
            "payload": load_json(catalog_path),
        }
    return ordered_skill_types, catalogs


def render_direct_rebuild_phase() -> str:
    raw_text = DIRECT_REBUILD_PROMPT.read_text(encoding="utf-8").strip()
    return "\n\n".join(
        [
            "## Phase 2 — Direct Rebuild Phase (Regeneration Spine, Non-Catalogized)",
            "This phase is the regeneration spine of the workflow. Phase 1 prepares it. Phases 3–5 enrich, realize, and prove it. It is preserved directly from the clone rebuild prompt and is intentionally **not** represented as a skill catalog.",
            "The direct rebuild phase owns `_old` preservation, canonical new `index.html` creation, blueprint-first regeneration, subsystem-by-subsystem mechanic verification, and stability-first runtime selection.",
            "Use `#PROMPT#` here to steer how the regenerated public surface expresses mechanic meaning, authored presentation, and stable target identity — without collapsing into legacy imitation.",
            f"**Direct source:** `{DIRECT_REBUILD_PROMPT.relative_to(ROOT.parent)}`",
            raw_text,
        ]
    )


def build_prompt_text() -> str:
    ordered_skill_types, catalogs = read_skill_catalogs()
    generated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    header = "\n".join(
        [
            "<!-- CREATIVE REMIX V5 SUPER OPERATOR -->",
            "<!-- Generated from Remix v5 skill catalogs + direct clone rebuild phase. -->",
            f"<!-- Generated: {generated_at} -->",
            "",
            "# Creative Remix v5 — Super Operator",
            "",
            "You are the single super operator for `creative_remix_v5`.",
            "",
            "This operator must preserve the behavioral integrity of the latest working `remix-v4-clone` pipeline while collapsing it into one coherent long-horizon execution prompt.",
            "",
            "This is **not** permission to become vague, lazy, or magical.",
            "",
            "## Reconciliation Doctrine",
            "",
            "This operator reconciles two upstream truths:",
            "- the non-clone v4 expert creator stack: forensic game analysis, mechanic-aware authored world design, procedural/browser-native technical art direction, and ruthless mobile-first evidence-driven QA",
            "- the clone rebuild kernel: blueprint-first regeneration, `_old` as evidence-only legacy, a new canonical public surface, stability-first implementation selection, subsystem-by-subsystem verification, and explicit testing discipline",
            "",
            "These are not competing ideas. The clone rebuild kernel is the regeneration spine. The non-clone v4 stack is the intelligence wrapped around that spine.",
            "",
            "## Prompt Steering Contract",
            "",
            "The active remix prompt is not a decorative label. It is the primary steering source that must propagate through every phase:",
            "",
            "```text",
            "#PROMPT#",
            "```",
            "",
            "Interpret `#PROMPT#` simultaneously through these lenses:",
            "- **Mechanic Meaning Lens** — use `#PROMPT#` to reinterpret what the existing mechanics mean without changing mechanic truth.",
            "- **Narrative / World Lens** — use `#PROMPT#` to drive authored world semantics, HUD vocabulary, reward fantasy, failure fantasy, and progression framing.",
            "- **Visual / Focal Identity Lens** — use `#PROMPT#` to derive the focal actor, palette, motifs, scene foundation, and background identity.",
            "- **Media / Mood Lens** — use `#PROMPT#` to steer audio tone, font identity, animated feedback, and media choices from approved catalogs.",
            "- **QA / Judgement Lens** — use `#PROMPT#` to judge whether the final result feels authored, coherent, and meaningfully transformed rather than generically reskinned.",
            "",
            "## Required Prompt Propagation Artifact",
            "",
            "Write `prompt_surface_map.md` early and keep it updated across execution.",
            "",
            "`prompt_surface_map.md` must map `#PROMPT#` into:",
            "- mechanic meaning and preserved mechanic truth",
            "- narrative/world semantics and HUD vocabulary",
            "- visual/focal identity, scene language, and background ownership",
            "- media/mood choices and catalog-backed enrichment",
            "- QA judgement criteria and before/after expectations",
            "",
            "If `#PROMPT#` affects only one layer while the others remain generic, the operator has not fully executed the prompt.",
            "",
            "## Operator Stance",
            "",
            "Act at all times as a:",
            "- source-truth analyst",
            "- blueprint-driven regenerator",
            "- authored-world designer",
            "- technical art director",
            "- mobile QA finisher",
            "",
            "## Governing Decision Hierarchy",
            "",
            "When goals compete, decide in this order:",
            "1. mechanic truth",
            "2. stability of the regenerated public surface",
            "3. mobile actionability",
            "4. authored world coherence",
            "5. procedural originality",
            "6. media richness and polish",
            "",
            "## Unifying Operating Ledger",
            "",
            "Maintain one compact through-line across all phases:",
            "- **Preserve**: the real mechanics, controls, loop truth, and any stable subsystem that should survive regeneration",
            "- **Reinterpret**: the meaning, world semantics, copy, role mapping, and progression framing without lying about mechanics",
            "- **Regenerate**: the canonical public surface, authored scene foundation, procedural visual identity, and stable runtime implementation",
            "- **Verify**: subsystem behavior, mobile actionability, runtime cleanliness, and before/after evidence",
            "",
            "## Phase Relationship",
            "",
            "- Phase 1 prepares the rebuild kernel with source truth and planning contracts.",
            "- Phase 2 regenerates the canonical public surface from blueprint truth.",
            "- Phases 3 and 4 enrich and realize that regenerated surface as an authored world.",
            "- Phase 5 proves the result with runtime evidence rather than claims.",
            "",
            "You must execute in explicit phases:",
            "- analyze the current game truthfully",
            "- preserve mechanic truth",
            "- run the direct rebuild phase that preserves `_old` runtime references and creates a new canonical public surface",
            "- construct the authored world",
            "- execute procedural visual transformation",
            "- integrate media safely when applicable",
            "- perform runtime/mobile QA and before/after comparison",
            "",
            "## Global Remix v5 Non-Negotiables",
            "",
            "- Do not break mechanics.",
            "- Treat `catalogs/skills/` as authoritative read-only execution rails when present.",
            "- Treat media catalogs as authoritative approved asset references when applicable.",
            "- The rebuild / `_old` preservation phase lives directly in this prompt, not in a skill catalog.",
            "- Prefer browser-native, mobile-safe, inspectable implementation patterns.",
            "- Produce real artifacts and real runtime evidence rather than narrative-only reporting.",
            "- If seeded contract/template files already exist in the workspace, fill them in place instead of inventing alternate artifact structure.",
            "- If the output still reads like the source game with themed paint, the operator has failed the v5 bar.",
            "- Every major transformation should be explainable in terms of source truth, rebuild doctrine, and runtime evidence.",
            "- `#PROMPT#` must visibly propagate across mechanics framing, world semantics, visual identity, media tone, and QA evidence.",
            "",
            "## Skill Catalog Manifest",
            "",
            f"**Skill types discovered:** `{', '.join(ordered_skill_types)}`",
            "",
            "These catalogs are the execution rails for the v5 super operator:",
            bullet_list(
                [
                    str((CATALOGS_DIR / f"remix_v5_{skill_type}_skills.json").relative_to(ROOT.parent))
                    for skill_type in ordered_skill_types
                ]
            ),
            "",
            "## Execution Phase Layout",
            "",
            "Phase order:",
            "- Phase 0: Governing doctrine and operator contract",
            "- Phase 1: Source truth, blueprint, and progression planning",
            "- Phase 2: Direct rebuild phase (the regeneration spine: preserve old runtime / create new canonical surface)",
            "- Phase 3: Authored world, design-system, and media mapping",
            "- Phase 4: Procedural visual realization and mobile-safe presentation",
            "- Phase 5: Runtime proof, before/after evidence, and optional family validation",
        ]
    )

    sections = [header]
    for phase_title, phase_skill_types in PHASE_LAYOUT[:2]:
        sections.append("\n\n".join([f"## {phase_title}", PHASE_INTROS[phase_title]]))
        for skill_type in phase_skill_types:
            sections.append(render_catalog(catalogs[skill_type]["payload"], catalogs[skill_type]["path"]))

    sections.append(render_direct_rebuild_phase())

    for phase_title, phase_skill_types in PHASE_LAYOUT[2:]:
        sections.append("\n\n".join([f"## {phase_title}", PHASE_INTROS[phase_title]]))
        for skill_type in phase_skill_types:
            sections.append(render_catalog(catalogs[skill_type]["payload"], catalogs[skill_type]["path"]))

    sections.append(
        "\n\n".join(
            [
                "## Final Completion Standard",
                "The operator is complete only when:",
                "- the remixed game remains mechanically truthful",
                "- the preserve / reinterpret / regenerate / verify ledger stays coherent from analysis through QA",
                "- `prompt_surface_map.md` exists and shows how `#PROMPT#` propagated across mechanics, narrative, world, visual, media, and QA layers",
                "- the direct rebuild phase has preserved `_old` surfaces and created a new canonical public surface",
                "- that rebuilt public surface is the true spine of the finished game rather than a thin wrapper over legacy presentation",
                "- `#PROMPT#` is visible in the final result across more than one layer and does not collapse into a single cosmetic treatment",
                "- authored world, visual identity, and media behavior are coherent",
                "- runtime/mobile QA has been performed with real evidence",
                "- before/after differences are documented when evidence is available",
                "- any pre-seeded contract templates were filled in place and no `__FILL_ME__` placeholders remain",
                "- all required artifacts and contracts are written honestly",
            ]
        )
    )

    return "\n\n".join(sections).rstrip() + "\n"


def main() -> None:
    OUTPUT_PROMPT.write_text(build_prompt_text(), encoding="utf-8")
    print("remix_v5_super_prompt_built")


if __name__ == "__main__":
    main()