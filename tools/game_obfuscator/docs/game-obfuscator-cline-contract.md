# Game Obfuscator Cline Study Contract

> **DEPRECATED / EXPERIMENTAL**
>
> This study contract is retained for reference only and is scheduled for removal.
> The active product direction is now the simple deterministic pipeline in the main `game_obfuscator` CLI.

## Purpose

This document defines the starter study contract for `game_obfuscator_cline`.

It is no longer the recommended path for ongoing product work.

The goal is to reuse `game_refactoring` as a black-box workflow runner while adding only a new one-step workflow for a narrow human-readable obfuscation study.

This is not a full obfuscation engine.
This is not a runtime repair pass.
This is not a media pipeline.

It is a controlled cross-file code-surface rewrite study.

---

## Black-Box Boundary

`game_refactoring` is treated as a black box.

Allowed change:
- add a new workflow definition
- add a new prompt file used by that workflow

Not allowed:
- modify executor internals
- modify worker runtime internals
- modify batch orchestration internals
- modify polling/state engine internals for convenience

---

## Retained Surface

The study operates only on the retained code surface.

Retained files:
- `index.html`
- retained `.js` files
- retained `.css` files

The retained files must be treated as one linked system.

---

## Strict Pre-Step Preset

For the starter study workspace, keep only:

- `index.html`
- `assets/**/*.js`
- `assets/**/*.css`

Remove:
- images
- audio
- video
- fonts
- JSON/config files not required by retained code
- screenshots
- catalogs
- unrelated docs
- unrelated top-level files and directories

This preset exists to make the study code-surface-only.

---

## Rewrite Goal

The rewrite goal is modest, not exhaustive.

Target behavior:
- build a single global symbol map first
- rename a safe subset of non-visible symbols
- use Spanish-oriented names consistently
- update all retained callsites consistently across HTML, JS, and CSS
- preserve linkage and behavior
- stop early instead of chasing total coverage

A modest change is acceptable.
Approximately 20% meaningful code-surface change is enough if it is clean and consistent.

---

## Allowed Rename Scope

Allowed rename categories:
- local/helper function names
- local variables
- internal constants
- simple DOM reference variables
- internal helper object names
- safe CSS class/id names only when all retained references can be updated consistently

Not allowed:
- visible/player-facing strings
- browser APIs
- DOM built-ins
- library globals
- event names
- uncertain/public contracts
- anything whose retained references cannot be updated consistently

---

## Linkage Preservation Rules

Any accepted rename must preserve:

- HTML ↔ JS linkage
- HTML ↔ CSS linkage
- JS ↔ JS callsites
- CSS selector linkage when touched
- script/style file references

A symbol is eligible only if:
- it is non-visible
- it is fully traceable across retained files
- all retained references can be updated consistently
- changing it does not break retained linkage

If uncertain, skip it.

---

## Required Artifacts

The study prompt should create:

- `retained_surface_manifest.json`
- `obfuscation_symbol_map.json`
- `obfuscation_contract_report.json`

### `retained_surface_manifest.json`
Should include:
- retained files
- file roles
- obvious cross-file linkage points

### `obfuscation_symbol_map.json`
Should include:
- accepted rename map
- old name → new name
- enough structure to inspect the rename families

### `obfuscation_contract_report.json`
Should include:
- retained files
- rename candidates considered
- accepted renames
- skipped renames
- skipped reasons
- linkage-sensitive items preserved intentionally
- short summary of change scope

---

## Workflow Shape

Starter workflow:
- one step only

Workflow id:
- `game_obfuscator_cline_study`

Prompt:
- `prompts/operators_v2/08_game_obfuscator_cline_symbol_map_spanish.md`

This workflow exists for study and comparison, not for production rollout.

---

## Wrapper Intent

`game_obfuscator_cline` should later act as a synchronous wrapper that:

1. prepares the strict retained-surface workspace
2. invokes the black-box workflow
3. polls until terminal completion
4. returns final run/result metadata

This contract only defines the study workflow and retained-surface rules.