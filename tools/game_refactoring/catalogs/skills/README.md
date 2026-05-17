# Operator Skill Catalogs

This directory contains normalized operator skill catalogs.

Skill catalogs are intended to complement the existing media catalogs:

- media catalogs define approved assets an operator may use;
- skill catalogs define operational capabilities an operator must apply when a workflow asks for them.

## Runtime copy behavior

`tools/game_refactoring/scripts/run_operator_pipeline_game.py` copies this directory into every operator attempt workspace when it exists:

```text
workspace/catalogs/skills/
```

The copy is read-only reference material for the operator. Operators should not edit files under `catalogs/`.

## Stage 1 scope

This scaffold only defines the shared skill type vocabulary. Remix v5-specific skill catalogs will be added in the second implementation stage.

## Files

- `skill_types.json` - Shared skill type taxonomy used by future workflow-specific skill catalogs.
- `remix_v5_core_skills.json` - Global execution contracts, evidence discipline, and anti-laziness rails.
- `remix_v5_analysis_skills.json` - Source inspection, mechanic decomposition, blueprinting, and progression planning.
- `remix_v5_world_skills.json` - Mechanic-aware world mapping, authored narrative framing, and design-system definition.
- `remix_v5_visual_skills.json` - Procedural visual execution, background replacement, HUD hierarchy, and mobile-safe visual polish.
- `remix_v5_media_skills.json` - Catalog-guided audio/GIF/font selection and safe runtime wiring.
- `remix_v5_qa_skills.json` - Runtime repair, screenshot evidence, before/after comparison, and optional family QA.

## Remix v5 structure note

For `creative_remix_v5`, there is intentionally **no separate rebuild skill file**.

The rebuild/preserve-old-runtime phase from `remix-v4-clone` is meant to live directly inside the assembled v5 super prompt as a first-class execution phase, not as a reusable skill catalog.

That means the skill catalogs cover the indexed types only:

- `core`
- `analysis`
- `world`
- `visual`
- `media`
- `qa`

Each file may contain multiple subgroups within its skill type.
