# Game Obfuscator Deprecation & Removal Plan

## Objective

Consolidate the project around the new simple deterministic pipeline and phase out both:

1. the old legacy multi-stage pipeline
2. the experimental `game_obfuscator_cline` study path

This document is the recap and execution plan for deprecating those older paths before removing them.

---

## Current Recommended Product Surface

### Keep
- `scripts/game_obfuscator_cli.py`
  - default `start` path with `--pipeline simple`
- `scripts/run_game_obfuscator_simple_pipeline.py`
- `scripts/obfuscate_simple_outputs.py`
- `scripts/transform_web_assets.js`
- `scripts/prepare_inputs.py`
- `scripts/create_run.py`
- run-state / polling / output-path orchestration surface

### Why this stays
The new simple path now provides the desired behavior:
- deterministic
- local
- no LLM/Cline dependency
- retained-surface prune
- inline HTML script obfuscation in place
- safer than script extraction
- simpler operational model

---

## Paths To Deprecate

### 1. Experimental `game_obfuscator_cline`
These were useful for exploration but should no longer be treated as active product surfaces:

- `game_obfuscator_cline/`
- `docs/game-obfuscator-cline-contract.md`
- `docs/journals/game-obfuscator-cline.md`

### Why deprecate
- depends on `game_refactoring` black-box workflow machinery
- was exploratory/study-oriented
- adds orchestration and prompt complexity not needed for the new main product
- no longer matches the selected direction

---

### 2. Legacy multi-stage pipeline
These represent the older transform-heavy path that is no longer the default product direction:

- `scripts/run_game_obfuscator_pipeline.py`
- `scripts/analyze_inputs.py`
- `scripts/plan_rewrites.py`
- `scripts/apply_rewrites.py`
- `scripts/bundle_outputs.py`
- `scripts/obfuscate_separate_outputs.py`
- `scripts/obfuscate_outputs.py`
- `scripts/verify_outputs.py`

### Why deprecate
- more moving parts
- harder to reason about
- includes older rewrite/extraction/verification complexity
- no longer aligned with the simpler deterministic pipeline now chosen as primary

---

## Proposed Deprecation Phases

## Phase 1 — Mark As Deprecated
Goal: stop presenting old paths as active.

### Actions
- Update `README.md`
  - state that `simple` is the only recommended path
  - explicitly mark `--pipeline legacy` as deprecated
  - explicitly mark `game_obfuscator_cline` as experimental/deactivated
- Add header comments in deprecated scripts/docs:
  - `DEPRECATED: scheduled for removal`
- Update journals/handoffs:
  - note that legacy + cline paths are retained temporarily for transition only

### Exit Criteria
- No top-level docs present legacy or cline paths as primary
- Deprecation status is visible in code/docs

---

## Phase 2 — Disable By Default
Goal: make accidental use of old paths unlikely.

### Actions
- Keep `--pipeline simple` as default
- Add a warning in CLI when `--pipeline legacy` is used
- Remove legacy examples from README main flow
- Move cline-study references into an archive/deprecated section

### Exit Criteria
- Main onboarding/docs mention only the simple path
- Legacy use requires explicit opt-in and shows a warning

---

## Phase 3 — Remove Experimental Cline Path
Goal: remove the dead exploratory branch first.

### Actions
- Delete:
  - `game_obfuscator_cline/`
  - `docs/game-obfuscator-cline-contract.md`
- Keep a short archived recap in main journal or a deprecated archive note if needed
- Remove stale references from docs

### Exit Criteria
- No runtime/tooling dependency remains on `game_obfuscator_cline`
- No user-facing docs point to it

---

## Phase 4 — Remove Legacy Pipeline
Goal: fully consolidate around the simple deterministic path.

### Actions
- Delete legacy pipeline scripts:
  - `scripts/run_game_obfuscator_pipeline.py`
  - `scripts/analyze_inputs.py`
  - `scripts/plan_rewrites.py`
  - `scripts/apply_rewrites.py`
  - `scripts/bundle_outputs.py`
  - `scripts/obfuscate_separate_outputs.py`
  - `scripts/obfuscate_outputs.py`
  - `scripts/verify_outputs.py`
- Remove `--pipeline legacy` from CLI
- Simplify README and journal references accordingly
- Re-run smoke validation on the simple path after removals

### Exit Criteria
- only one pipeline remains
- CLI no longer exposes legacy mode
- docs describe a single canonical workflow

---

## Recommended Removal Order

1. mark both old paths as deprecated
2. stop documenting them as active
3. remove `game_obfuscator_cline` first
4. remove legacy multi-stage pipeline second
5. finally simplify CLI/docs to a single-path product

This order is safest because:
- `game_obfuscator_cline` is already non-primary and isolated
- legacy pipeline still shares some naming/history with the active CLI surface
- removing in phases reduces accidental breakage and confusion

---

## Risks

### Risk: hidden dependency on legacy scripts
Mitigation:
- grep references before deletion
- remove only after docs and CLI have already been narrowed

### Risk: loss of historical debugging context
Mitigation:
- keep recap in journal/docs before deletion
- preserve rationale in commit history and deprecation doc

### Risk: users still invoking `--pipeline legacy`
Mitigation:
- add explicit warning before final removal
- remove from README examples first

---

## Immediate Next Step Recommendation

Next implementation step should be:

### Deprecation pass
- mark `game_obfuscator_cline` as experimental/deactivated
- mark `--pipeline legacy` as deprecated in CLI/docs
- add removal notes to affected files

After that, do a cleanup pass to remove `game_obfuscator_cline`, then remove the legacy pipeline.

---

## Summary

Target end state:
- one product
- one pipeline
- one documented path

That path is the simple deterministic pipeline:
- retained-surface prune
- inline HTML script obfuscation in place
- CSS minification
- external JS obfuscation
- straightforward launch/status/output orchestration