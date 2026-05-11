# Game Publish Pipeline

A higher-order orchestration tool that chains `game_obfuscator` and `game_deploy` into one machine-facing publish pipeline.

## Scope

This tool is focused on orchestration only:

- accept one or more `game_refactoring` output directories
- stage them into deterministic raw remix folders under `games/raw/<game_id>/remix-<hash>/`
- deploy those staged games into `games/published/public/...`
- build an obfuscator manifest from the public deploy outputs
- launch `game_obfuscator` using its simplified synchronous external contract
- pass `games/published/obfuscated` as the obfuscator output root
- use the terminal `start` response as the primary obfuscation result
- emit one final pipeline report JSON

It intentionally excludes any direct remix generation, obfuscation logic, or deploy transformation logic of its own.

## Current workflow

```bash
python3 scripts/publish_games.py \
  --inputs /path/to/refactor/output/game-a /path/to/refactor/output/game-b
```

Dry-run:

```bash
python3 scripts/publish_games.py \
  --inputs /path/to/refactor/output/game-a \
  --dry-run
```

## Runtime flow

1. stage each input into `games/raw/<game_id>/remix-<hash>/`
2. call `tools/game_deploy/scripts/deploy_games.py` to publish public copies
3. build a `game_obfuscator` manifest from the deployed public directories
4. call `game_obfuscator_cli.py start --manifest ... --output-root games/published/obfuscated`
5. wait for the synchronous `start` command to finish
6. use the returned per-game output paths from the terminal response
7. write the final pipeline report

## Output report

The pipeline emits one machine-readable JSON report containing:

- `source_inputs`
- `raw_remix_staging`
- `deployment.manifest_path`
- `deployment.published_public_root`
- `deployment.results`
- `obfuscation.manifest_path`
- `obfuscation.published_obfuscated_root`
- `obfuscation.start`
- `obfuscation.final_status`
- `obfuscation.output`
- `obfuscation.game_outputs`

`obfuscation.final_status` currently mirrors the terminal synchronous `start` payload.

## External tool surfaces used

### game_obfuscator
- `start --manifest <manifest> --output-root <published-obfuscated-root>`

### game_deploy
- `--manifest <deploy-manifest>`
- `--published-root <published-public-root>`

## Key arguments

- `--inputs` - one or more refactor output game directories
- `--manifest` - optional JSON array of inputs
- `--raw-root` - optional raw staging root
- `--published-public-root` - optional published public root forwarded to `game_deploy`
- `--published-obfuscated-root` - recorded in the final report for downstream consumers
- `--report-path` - optional explicit pipeline report path
- `--overwrite` - overwrite an existing staged raw remix folder
- `--dry-run` - print orchestration plan without running subprocesses

## Separate GCS sync step

After local publish completes, you can sync the two published roots to Google Cloud Storage as a separate final step.

Dry-run both targets:

```bash
python3 scripts/sync_to_gcs.py --target both --dry-run
```

Sync only public:

```bash
python3 scripts/sync_to_gcs.py --target public
```

Sync only obfuscated:

```bash
python3 scripts/sync_to_gcs.py --target obfuscated
```

Per-item mode is now the default, so each top-level game folder is synced with its own `gcloud storage rsync -r ...` command. You can also narrow the sync to a specific item:

```bash
python3 scripts/sync_to_gcs.py --target public --only-item gamezone-0f3dc736-8159-48cf-93d0-bd78a54b8cd0
```

The canonical wrapper can also chain this final step after publish + refresh + validation:

```bash
python3 scripts/publish_vatsal_app_alpha_231.py --sync-to-gcs
```

Dry-run the coordinated publish+sync handoff:

```bash
python3 scripts/publish_vatsal_app_alpha_231.py --sync-to-gcs --sync-gcs-dry-run
```

Default destinations:
- public:
  - `gs://friendjam-ios/games-prod/public`
- obfuscated:
  - `gs://friendjam-ios/games-prod/play`
- project:
  - `jabali-prod`

This keeps cloud sync isolated from the local publish pipeline, so you can rerun:
- publish only
- sync only
- public-only sync
- obfuscated-only sync

## Directory layout

```text
game_publish_pipeline/
  README.md
  game_publish_pipeline/
    __init__.py
    pipeline.py
  scripts/
    publish_games.py
    sync_to_gcs.py
```
