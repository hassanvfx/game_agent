# Game Deploy

A standalone deploy-packaging tool for converting `game_refactoring` output game directories into deployable published remix bundles.

## Scope

This tool is focused on four capabilities only:

- resolving one or more `game_refactoring` output game directories
- creating a published remix path under `games/published/public/<game_id>/remix-<uuid>/`
- copying only the public runtime artifacts needed for deployment
- aggregating source JSON/markdown metadata into a single `game-obfuscated-<uuid>.json`

It intentionally excludes generation, refactoring, queue orchestration, or upload logic.

## Output contract

For each source game output, the tool produces exactly:

```text
games/published/public/<game_id>/remix-<uuid>/
  index.html
  assets/
  screenshots/
  game-obfuscated-<uuid>.json
```

## Metadata contract

The generated `game-obfuscated-<uuid>.json` is based on the unified public reference shape and aggregates fields such as:

- `game_id`
- `aggregated_at`
- `recreation_prompt_markdown`
- `blueprint_markdown`
- `semantic_tags`
- `semantic_tags_source_mode`
- `identity`
- `identity_source_mode`
- `mechanics_classification`
- `mechanics_classification_source_mode`
- `screenshots_png`
- `screenshots_jpg`

Screenshot paths must be relative public paths, for example:

- `screenshots/01.png`
- `screenshots/02.jpg`

## Public purge policy

The deploy output should keep only public deployment artifacts:

- `index.html`
- `assets/`
- `screenshots/`
- `game-obfuscated-<uuid>.json`

All raw internal stage artifacts are considered aggregation inputs only and should not be published directly.

## Current workflow

Deploy one or more refactoring output directories directly:

```bash
python3 scripts/deploy_games.py \
  --inputs /path/to/refactor/output/gamezone-abc...
```

Deploy from a manifest of source directories:

```bash
python3 scripts/deploy_games.py \
  --manifest deploy_inputs.json
```

Dry-run without writing output:

```bash
python3 scripts/deploy_games.py \
  --inputs /path/to/refactor/output/gamezone-abc... \
  --dry-run
```

## Key arguments

- `--inputs` - one or more refactoring output game directories
- `--manifest` - optional JSON array of source directories or objects with `source`, `path`, or `output_dir`
- `--published-root` - published destination root, defaults to `games/published/public`
- `--overwrite` - allow overwriting an existing deploy destination
- `--dry-run` - print deploy results without writing files

## Directory layout

```text
game_deploy/
  README.md
  game_deploy/
    __init__.py
    deployer.py
  scripts/
    deploy_games.py
```

## Notes

- The tool prefers an existing reference JSON in the source directory when available and uses that as the source-of-truth metadata shape.
- If markdown prompt/blueprint files are present, they can be folded into the unified obfuscated JSON.
- Runtime assets are filtered into a cleaner public bundle instead of copying every internal artifact verbatim.