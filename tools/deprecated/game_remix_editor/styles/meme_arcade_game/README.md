# Meme Arcade Game Style Preset

## Overview

`meme_arcade_game` is a reusable style preset promoted from a successful spec-adaptor recomposition run rather than authored manually from scratch.

It packages a meme-arcade creative identity into the standard style-preset structure used by the Game Remixer pipeline:

- `style_manifest.json`
- `specs/creative_remix_contract.md`
- `prompts/creative_refactor_agent_template.md`
- `prompts/visual_identity_contract.md`
- `prompts/theme_policy.md`

This preset is intended to preserve gameplay clarity while applying a loud, absurd, neon-comic meme-arcade presentation.

---

## Provenance

This preset was promoted from the following spec-adaptor run artifacts:

- Run: `runs/run_game_remixer_20260502T015442Z/spec_adaptor`
- Selected base style: `neutral_prototype`
- Adaptation report: `runs/run_game_remixer_20260502T015442Z/spec_adaptor/adaptation_report.json`

### Source files used

The permanent preset files were copied directly from the run’s adapted creative bundle:

- `runs/run_game_remixer_20260502T015442Z/spec_adaptor/adapted/creative_remix_contract.md`
  -> `styles/meme_arcade_game/specs/creative_remix_contract.md`

- `runs/run_game_remixer_20260502T015442Z/spec_adaptor/adapted/creative_refactor_agent_template.md`
  -> `styles/meme_arcade_game/prompts/creative_refactor_agent_template.md`

- `runs/run_game_remixer_20260502T015442Z/spec_adaptor/adapted/visual_identity_contract.md`
  -> `styles/meme_arcade_game/prompts/visual_identity_contract.md`

- `runs/run_game_remixer_20260502T015442Z/spec_adaptor/adapted/theme_policy.md`
  -> `styles/meme_arcade_game/prompts/theme_policy.md`

### Files intentionally not promoted

These run artifacts were kept as provenance/debug material only and were not used as live preset files:

- `selected_style.json`
- `recomposition_context.json`
- `recomposition_stdout_attempt_01.txt`
- `recomposition_stderr_attempt_01.txt`
- `recomposition_summary.json`
- `spec_recomposition_harness_attempt_01.md`

---

## Identity Summary

The preset expresses the following direction:

- meme-arcade cabinet energy
- chaotic internet-humor presentation
- neon-comic signal colors on dark anchor surfaces
- reaction-face, sticker, badge, and caption-card motifs
- loud comedic feedback with disciplined gameplay readability
- mobile-first HUD clarity and control-safe layout behavior

### Core creative intent

The style should make a game feel like:
- a viral-joke arcade cabinet skin
- a punchy stream-overlay-inspired remix
- an intentionally silly but still readable casual/mobile game presentation

### Constraints carried forward

The promoted preset preserves the spec-adaptor bundle’s strong constraints:

- preserve mechanics, controls, boot flow, and win/loss logic
- keep critical HUD and controls unobstructed
- prefer `Baloo 2` for UI/body text
- prefer `Bangers` for titles/display/emphasis
- avoid arbitrary networking and remote dependencies
- remain silent-safe by default
- do not let decorative humor overpower gameplay clarity

---

## File Roles

### `style_manifest.json`

Registers the preset with the pipeline and points style resolution to the correct style-local files.

Key fields:
- `style_id`: `meme_arcade_game`
- `display_name`: `Meme Arcade Game`
- `default_for_runtime`: `false`
- `inherits_global_policies`: `true`

### `specs/creative_remix_contract.md`

Defines the top-level remix success criteria and creative boundaries, including:
- what must stay preserved
- what must materially change
- what counts as failure
- required design-system behavior
- playability, readability, and control-safe-zone rules

### `prompts/creative_refactor_agent_template.md`

Provides worker-facing operational instructions for the creative refactor stage, including:
- editing stance
- execution model
- remix expectations
- typography/palette/network/audio rules
- progress tracking expectations

### `prompts/visual_identity_contract.md`

Defines the style’s concrete visual-identity requirements, such as:
- branding/title change expectations
- approved font usage
- palette shift requirements
- atmosphere/material language
- what qualifies as insufficient transformation

### `prompts/theme_policy.md`

Captures the compact high-level style direction:
- tone
- mood targets
- practical guidance
- thematic constraints
- readability-first rules

---

## How the pipeline resolves this style

The preset is loaded by style ID through the existing style resolution flow.

Primary resolution path:
- `scripts/generate_task_packet.py`

Relevant behavior:
- loads `styles/meme_arcade_game/style_manifest.json`
- resolves style-local `specs` and `prompts`
- copies those files into packet refs for use during the run

Related support path:
- `scripts/spec_adaptor.py`

This means the preset behaves like the other built-in styles rather than as a one-off run artifact.

---

## Verification performed

The preset was verified by resolving it through the same helper functions used by task-packet generation.

Validation performed:
- `load_style_manifest("meme_arcade_game")`
- `get_prompt_template_source("creative_refactor", manifest)`
- `get_spec_sources("creative_refactor", manifest)`
- `get_style_policy_sources("creative_refactor", manifest)`

Verified outputs:
- prompt template resolved successfully
- spec path resolved successfully
- style policy paths resolved successfully
- no missing-file errors occurred during style lookup

---

## Usage

Example:

```bash
python3 scripts/creative_refactor_cli.py --json start-batch --manifest fixtures/repeat2_three_game_manifest_20260430.json --style meme_arcade_game
```

Any pipeline entrypoint that already accepts `--style` can now use:

```text
meme_arcade_game
```

---

## Maintenance Notes

If this style is refined later, update the style-local files directly under `styles/meme_arcade_game/` rather than editing old run artifacts.

If a future spec-adaptor run produces a better meme-arcade bundle, compare it against this preset before replacing it wholesale so that:
- provenance remains clear
- changes stay intentional
- regressions in readability or compliance are easier to track