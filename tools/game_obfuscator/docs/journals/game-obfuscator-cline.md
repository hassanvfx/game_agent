# Game Obfuscator Cline - Implementation Journal

> **DEPRECATED / EXPERIMENTAL**
>
> This journal is retained for history/reference only.
> The active product direction is now the simple deterministic pipeline in the main `game_obfuscator` CLI.

**Last Updated:** 2026-05-10  
**Feature Spec:** Black-box workflow study wrapper around `game_refactoring`  
**Backend Reference:** `../game_refactoring`

---

## Purpose

`game_obfuscator_cline` is a small synchronous wrapper around the existing black-box workflow system in `game_refactoring`.

It does not implement a native obfuscation engine.

Instead, it:
- prepares a strict retained-surface workspace
- launches a one-step workflow in `game_refactoring`
- polls until terminal completion
- returns structured results

---

## Current Study Scope

Starter study mode is intentionally narrow.

### Retained surface
- `index.html`
- `assets/**/*.js`
- `assets/**/*.css`

Everything else is removed from the prepared workspace.

### Black-box workflow
- workflow id: `game_obfuscator_cline_study`

### Prompt
- `../game_refactoring/prompts/operators_v2/08_game_obfuscator_cline_symbol_map_spanish.md`

### Expected output style
- global symbol map first
- modest English → Spanish non-visible renaming
- consistent cross-file linkage preservation
- no exhaustive refactor ambition

---

## Files Added

### In `game_refactoring`
- `prompts/operators_v2/08_game_obfuscator_cline_symbol_map_spanish.md`
- updated `scripts/game_workflow.py` with workflow:
  - `game_obfuscator_cline_study`

### In `game_obfuscator`
- `docs/game-obfuscator-cline-contract.md`
- `game_obfuscator_cline/README.md`
- `game_obfuscator_cline/scripts/prepare_study_inputs.py`
- `game_obfuscator_cline/scripts/run_game_obfuscator_cline.py`

---

## Architecture

```text
source manifest
   ↓
prepare_study_inputs.py
   ↓
strict retained-surface prepared manifest
   ↓
run_game_obfuscator_cline.py
   ↓
game_refactoring/scripts/game_workflow.py --id game_obfuscator_cline_study
   ↓
game_refactoring black-box batch execution
   ↓
creative_refactor_cli.py status polling
   ↓
terminal run summary returned
```

---

## Design Constraints

### Black-box rule
`game_refactoring` is treated as a black box.

Allowed changes were limited to:
- adding a new prompt
- adding a new workflow definition

No executor or runtime internals were changed.

### Study-first rule
This is not yet a production obfuscator.
It is a controlled study path.

### Linkage rule
Renames must preserve:
- HTML ↔ JS linkage
- HTML ↔ CSS linkage
- JS ↔ JS callsites
- CSS selector linkage when touched

---

## Next Steps

- [ ] Run `game_obfuscator_cline/scripts/run_game_obfuscator_cline.py` against a small one-game manifest
- [ ] Inspect generated prepared manifest and purge report
- [ ] Verify the black-box workflow launches and reaches terminal state
- [ ] Inspect operator-emitted artifacts:
  - `retained_surface_manifest.json`
  - `obfuscation_symbol_map.json`
  - `obfuscation_contract_report.json`
- [ ] Tighten the prompt if the rename pass is too weak, too broad, or breaks linkage

---

## Status

**Deprecated / Retained for Reference**
