# game_editorial

## Overview and pipeline position

This is an alternative batch entrypoint for remixing the raw corpus. It chooses
repeatable themed prompt combinations and creates manifests for the existing
refactoring workflow, allowing multiple variants per source game.

```text
games/raw + remix_ideas.json + offset / seed / variant count
                             |
                  deterministic prompt assignment
                             |
                  expanded source-game manifest
                             |
                  sanitized copies (copy mode)
                             |
                  game_refactoring: creative_remix_v5
                             |
                  output runs -> separate publish step
```

This path bypasses prompt matching. Stable game order and seed settings make prompt
assignment repeatable; actual AI-generated results can still vary. `--no-launch`
prepares the batch without starting refactoring. Review the configured output root
below before launching on a different machine.

All commands below run from the repository root. See the
[refactoring tool](../game_refactoring/README.md) and
[workspace overview](../../README.md).

`game_editorial` now provides a deterministic raw-game remix manifest builder for `creative_remix_v5`.

## Purpose

This tool scans `games/raw`, assigns deterministic prompt overrides from `tools/game_editorial/remix_ideas.json`, expands games into one-or-more manifest entries, and launches the existing `game_refactoring` workflow without modifying that tool.

For `copy`-mode launches, `game_editorial` now stages **sanitized source copies** that exclude:

- `.DS_Store`
- `._*` AppleDouble sidecar files

and uses content-only file copies for those staged sources before handing them to `game_refactoring`.

## Locked workflow

- workflow id: `creative_remix_v5`
- output runs root default: `/Volumes/HDD2026/output-May17th`
- input source mode default: `copy`

## Deterministic assignment model

Prompt assignment is derived from:

- stable selected-game index
- prompt variant index
- optional `seed_offset`

The tool builds the full combination space from:

- `thematicStyles`
- `thematicModifiers`
- `remixPremiseSymbols`

and reduces a stable SHA-256 digest into that space.

By default, the effective seed is computed from expanded entry order:

```text
effective_seed = seed_offset + (selected_game_index * prompts_per_game) + variant_index
```

So if you run with `--game-limit 2 --prompts-per-game 2`, the four generated entries naturally receive effective seeds `0, 1, 2, 3`.

## CLI

```bash
python3 tools/game_editorial/scripts/launch_seeded_raw_remix_batch.py \
  --game-limit 2 \
  --prompts-per-game 2 \
  --no-launch \
  --json
```

Remove `--no-launch` to start the actual batch.

You can also launch from an offset inside the stable raw corpus:

```bash
python3 tools/game_editorial/scripts/launch_seeded_raw_remix_batch.py \
  --raw-game-offset 100 \
  --game-limit 100 \
  --prompts-per-game 2 \
  --json
```

If you want `game_refactoring` to mirror cleaned inputs into the run, keep the default:

```bash
--source-mode copy
```

If you want to bypass copy-mode preparation entirely, use:

```bash
--source-mode inplace
```

## Planning 100-game sequential batches

To split the full raw corpus into launchable batches of 100 base games, use:

```bash
python3 tools/game_editorial/scripts/plan_sequential_raw_remix_batches.py \
  --batch-size 100 \
  --prompts-per-game 2
```

This writes a batch plan under:

```text
tools/game_editorial/scripts/workspace/batch_plans/
```

including:

- `plan.json`
- `launch_all_sequential.sh`

Each batch command uses `--raw-game-offset` plus `--game-limit 100`, so prompt assignment remains globally deterministic across batches.

## Output artifacts

Each run writes a workspace folder under:

```text
tools/game_editorial/scripts/workspace/
```

Artifacts include:

- `games_manifest.json`
- `prompt_trace.json`
- `summary.json`

## Manifest contract

Each manifest entry keeps the existing `game_refactoring` contract:

```json
{
  "game_id": "gamezone-...__p01",
  "display_name": "gamezone-...__p01",
  "source_path": "/absolute/path/to/games/raw/gamezone-...",
  "remix_prompt": "Create a deterministic creative remix ..."
}
```

When `--prompts-per-game 1`, the base `game_id` is preserved. When the value is higher than one, the same raw game is repeated with suffixed ids such as `__p01`, `__p02`, etc.