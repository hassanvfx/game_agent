# Quarantine Manifest

This document defines a practical keep / review / quarantine classification for non-core material in `game_refactoring`.

It is intentionally non-destructive. Nothing in this document authorizes deletion by itself. Its purpose is to reduce cleanup risk and create a stable boundary between the reusable operator-pipeline core and surrounding legacy, experimental, and generated material.

## Classification meanings

### Keep
Keep in place as part of the current working repository because the area appears core, operator-relevant, or plausibly still active.

### Review
Do not delete or move yet. The area is suspicious, mixed, or transitional and needs dependency confirmation before any quarantine action.

### Quarantine
Treat as non-core by default. Prefer to isolate from the canonical architecture narrative. May later be archived, moved, ignored, or documented as historical/generated-only.

## Keep

These areas should remain part of the primary working surface for now.

### Core runtime and orchestration
- `scripts/`
- `configs/`
- `prompts/`
- `specs/`
- `styles/`

### Current documentation surface
- `README.md`
- `docs/operator_pipeline_manual.md`
- `docs/media_mapper_prompt_packet_spec.md`
- `docs/kill-all-operation.md`
- `docs/repository_taxonomy.md`
- `docs/journals/repo-identity-and-operator-pipeline-reframe.md`

### Support inputs that may still feed the pipeline
- `catalogs/audios.json`
- `catalogs/fonts.json`
- `catalogs/gifs.json`
- `catalogs/sprites.json`
- `assets/audio_library/`
- stable manifest fixtures in `fixtures/`

## Review

These areas appear useful, but they are mixed enough that they should be confirmed before any relocation or cleanup.

### Catalog and asset support areas
- `catalogs/`
  - reason: likely contains both active operator inputs and generated/byproduct material
- `catalogs/sprites/`
  - reason: appears to contain both source tooling and generated dashboards/runs
- `assets/emoji-images-1.2.1/`
  - reason: may still support visual-identity work, but may also be a vendored side utility
- `assets/audios/`
  - reason: appears large and asset-heavy; may be active source material or duplicate library residue

### Test and fixture areas
- `fixtures/`
  - reason: contains a mixture of probably useful manifests and clearly lab/debug-oriented directories
- `scripts/test_creative_refactor_batch_cli_live.py`
  - reason: likely active but should be checked against the intended future execution path
- `scripts/test_media_mapper_prompt_fixture.py`
  - reason: embeds historical run references that may be intentional fixture provenance
- `scripts/test_media_policy_fixture.py`
  - reason: embeds historical run references that may be intentional fixture provenance

### Style metadata with historical provenance
- `styles/meme_arcade_game/`
  - reason: appears active, but includes metadata derived from historical run output and should be reviewed before any further rename normalization

## Quarantine

These areas should be treated as non-core, generated, experimental, or historical by default.

### Runtime-generated outputs
- `runs/`
  - reason: generated run artifacts, dashboards, logs, state snapshots, and historical runtime output

### Historical journals
- most files under `docs/journals/`
  - reason: valuable provenance, but not canonical architecture docs
  - note: keep the current cleanup journal active; treat older journals as historical memory

### Experimental and lab fixture paths
- `fixtures/operator_pipeline_lab/`
- `fixtures/spec_adaptor_debug/`
- `fixtures/spec_adaptor_test_lab/`
- `fixtures/style_resolution_test_run/`
  - reason: explicitly lab/debug/test-run oriented and not part of the clean canonical repo surface

### Experimental/lab script path
- `scripts/operator_pipeline_lab.py`
  - reason: still valuable for reference and possible reuse, but should not be treated as the main runtime center

### Sprite optimization byproducts
- `catalogs/sprites/v2_prompt_optimize/`
- `catalogs/sprites/runs/`
- `catalogs/sprites/dashboard.html`
- `catalogs/sprites/dashboard_v2.html`
- `catalogs/sprites/v2_edit_control.json`
- `catalogs/sprites/v2_edit_progress.json`
- `catalogs/sprites/V2_PROMPT_OPTIMIZATION_REPORT.md`
  - reason: optimization work products, dashboards, control files, progress artifacts, and run outputs rather than core operator-pipeline architecture

## Immediate recommendations

### Safe now
- keep these areas out of the canonical architecture narrative
- explicitly refer to quarantined areas as generated, historical, experimental, or mixed
- avoid using quarantined paths as the primary example in top-level docs

### Do next before moving/deleting anything
- inspect actual code references from core scripts into reviewed/quarantined paths
- determine whether `catalogs/sprites/` has a smaller active subset worth promoting into core support inputs
- determine whether `assets/emoji-images-1.2.1/` is actually depended on by current operator flows
- determine whether `assets/audios/` duplicates `assets/audio_library/` or serves a distinct role

## What this does not do

This manifest does not:
- delete files
- move directories
- change imports or runtime paths
- rewrite generated artifacts
- decide final archive locations

It only establishes a safer cleanup boundary for later action.