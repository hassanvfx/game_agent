# game_deploy

## Overview and pipeline position

This tool packages completed game folders into the public build layout. It is the
packaging stage used by `game_publish_pipeline`; a successful local deploy produces
files and metadata for the next stage.

```text
refactoring output folders / input manifest
                     |
             content hash + packaging
                     |
     games/published/public/<game_id>/remix-<hash>/
                     |
       index.html + assets + screenshots + metadata
                     |
      JSON results -> game_publish_pipeline -> obfuscator
```

Inputs are source folders or a manifest. Outputs include the deployed directory,
remix identifier, and metadata path. Cloud synchronization is coordinated separately
by the publish pipeline or upload utilities.

All commands below run from `tools/game_deploy/`. From the repository root, prefix
script paths with `tools/game_deploy/`.

See the [publish pipeline](../game_publish_pipeline/README.md) and
[workspace overview](../../README.md).

Deploy-packaging CLI that converts `game_refactoring` output directories into published public remix bundles.

## CLI entrypoint

```bash
python3 scripts/deploy_games.py --inputs /path/to/refactor/output/gamezone-...
```

`scripts/deploy_games.py` delegates to:

- `game_deploy.deployer.build_parser`
- `game_deploy.deployer.run_deploy`

## Arguments (implementation-grounded)

- `--inputs` (one or more source directories)
- `--manifest` (JSON array of strings or objects with `source` / `path` / `output_dir`)
- `--published-root` (default: `games/published/public`)
- `--overwrite`
- `--dry-run`

If neither `--inputs` nor `--manifest` is provided, the command fails.

## What deploy writes

Per source game output, deploy writes:

```text
games/published/public/<game_id>/remix-<content-hash>/
  index.html
  assets/
  screenshots/
  game-obfuscated-<content-hash>.json
```

Key implementation details:

- remix id uses deterministic folder content hash (`sha256`, truncated to 32 chars)
- `index.html` is copied
- `assets/` is filtered to allowed runtime suffixes (`.js`, `.css`, image/audio/font types)
- screenshots are normalized into numbered JPG files (`screenshots/01.jpg`, ...)
- metadata JSON is emitted as `game-obfuscated-<hash>.json`

## JSON result contract

`run_deploy` prints a JSON object:

- `published_root`
- `dry_run`
- `results` (array of objects containing `source`, `game_id`, `remix_uuid`, `deploy_dir`, `metadata_path`)

## Architecture boundary

`game_deploy` is a packaging/deploy transform only. It is used by `game_publish_pipeline` orchestration and does not own refactor generation or obfuscation execution.