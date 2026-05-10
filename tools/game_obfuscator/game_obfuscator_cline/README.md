# game_obfuscator_cline

> **DEPRECATED / EXPERIMENTAL**
>
> This path is retained temporarily for reference only and is scheduled for removal.
> The active product direction is now the simple deterministic pipeline in the main `game_obfuscator` CLI.

A small synchronous wrapper around `game_refactoring`'s black-box workflow runner.

## Purpose

> This document describes a deprecated study path, not the recommended production workflow.

`game_obfuscator_cline` does not implement its own obfuscation engine.

Instead, it:

1. prepares a strict retained-surface workspace
2. builds a temporary games manifest pointing at that prepared workspace
3. invokes the `game_refactoring` black-box workflow:
   - `game_obfuscator_cline_study`
4. polls until terminal completion
5. returns a compact machine-readable result

## Current Study Mode

Starter study mode keeps only:

- `index.html`
- `assets/**/*.js`
- `assets/**/*.css`

Everything else is removed from the prepared workspace.

The downstream workflow uses the prompt:

- `../game_refactoring/prompts/operators_v2/08_game_obfuscator_cline_symbol_map_spanish.md`

That prompt is designed to:
- build a symbol map first
- apply a modest cross-file English → Spanish rename pass
- preserve linkage across retained HTML/CSS/JS
- emit study artifacts

## Contract

See:

- `../docs/game-obfuscator-cline-contract.md`

## Planned Scripts

- `scripts/prepare_study_inputs.py`
- `scripts/run_game_obfuscator_cline.py`

## Notes

`game_refactoring` is treated as a black box.
This wrapper is only allowed to rely on its public workflow/CLI surface.