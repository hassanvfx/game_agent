# game_publish_pipeline

Orchestration CLI that stages refactor outputs, deploys public bundles, runs obfuscation, and writes a pipeline report.

## Main entrypoint

```bash
python3 scripts/publish_games.py --inputs /path/to/game-a /path/to/game-b
```

`scripts/publish_games.py` delegates to `game_publish_pipeline/pipeline.py` (`build_parser` + `run_pipeline`).

## Batch delta entrypoint

```bash
python3 scripts/publish_all_raw.py
```

`scripts/publish_all_raw.py` scans `games/raw`, subtracts any top-level `gamezone-*` IDs already present under `games/published/public`, writes a generated delta manifest, invokes `scripts/publish_games.py`, and always requests the built-in GCS sync step at the end.

Useful flags:

- `--dry-run`
- `--limit 25`
- `--overwrite`
- `--sync-gcs-project jabali-prod`
- `--sync-gcs-dry-run`
- `--include-existing-public` to disable delta filtering and republish every raw game discovered

## Core arguments

- `--inputs` (one or more source dirs)
- `--manifest` (optional JSON input list/object form)
- `--raw-root`
- `--published-public-root`
- `--published-obfuscated-root`
- `--published-runs-root`
- `--report-path`
- `--overwrite`
- `--dry-run`

Post-publish helpers wired in pipeline args:

- `--refresh-app-artifacts-manifest`
- `--refresh-app-artifacts-collection-slug`
- `--validate-published-manifest`
- `--validate-published-collection-slug`
- `--validate-published-annotator-html-name`
- `--validate-published-strict`

## Runtime flow (from implementation)

1. build deploy manifest from input sources
2. run `tools/game_deploy/scripts/deploy_games.py`
3. build obfuscator manifest from deployed public outputs
4. run `tools/game_obfuscator/scripts/game_obfuscator_cli.py start ... --output-root ...`
5. use terminal `start` payload as obfuscation result source
6. optionally refresh app artifacts and validate published outputs
7. write final JSON report

Artifact refresh now also renders annotator dashboards at two scopes:
- per-run dashboards under `games/published/runs/<run_id>/public|obfuscated/annotator.html`
- root dashboards under `games/published/public/annotator.html` and `games/published/obfuscated/annotator.html`

## Additional scripts

- `scripts/publish_all_raw.py` — build a raw-vs-public delta manifest, publish only missing raw game IDs, then sync to GCS
- `scripts/sync_to_gcs.py` — sync `games/published/public|obfuscated` to GCS
- `scripts/refresh_app_artifacts.py` — refresh persistent app artifact snapshots
  - defaults to `--reconcile-mode replace` (prunes stale keys; keeps only newest generated key set)
  - use `--reconcile-mode merge` only when you intentionally want cumulative historical keys
- `scripts/validate_published_outputs.py` — validate outputs/screenshots/artifacts
- `scripts/generate_annotator_entry.py` — render annotator dashboard HTML for run/root published artifact views

## Architecture boundary

`game_publish_pipeline` is an orchestrator layer. It does not implement deploy/obfuscation transforms itself; it coordinates external tool contracts and emits pipeline-level reports.
