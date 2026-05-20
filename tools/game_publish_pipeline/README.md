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

## Detect identical public vs obfuscated files

```bash
python3 scripts/detect_identical_public_obfuscated.py --strict
```

This check compares matching relative file paths between:

- `games/published/public`
- `games/published/obfuscated`

By default it scans `.html`, `.js`, and `.css` files and reports pairs that are byte-for-byte identical.

### What the detector is for

Use this when you want to find published outputs that appear to have skipped meaningful obfuscation. In practice, the detector is answering:

> “Which published public files are still byte-identical in the published obfuscated tree for the same relative path?”

The script walks the public tree, resolves the same relative path inside the obfuscated tree, hashes both files with SHA-256, and reports identical pairs. It also records files that exist in public but are missing in obfuscated.

### Default filtering

Default filtering excludes non-actionable matches:

- AppleDouble metadata files (`._*`)
- `annotator.html`
- known vendor asset domains under `assets/`:
  - `fonts.googleapis.com`
  - `cdn.tailwindcss.com`
  - `unpkg.com`
  - `cdnjs.cloudflare.com`

These defaults help keep the report focused on files that are more likely to indicate a real public-vs-obfuscated parity problem rather than expected mirrored assets or local filesystem noise.

### Recommended operator workflow

**1. Safe report-only scan**
```bash
python3 scripts/detect_identical_public_obfuscated.py \
  --report-path tmp/identical_public_obfuscated_report.json
```

**2. Strict scan for shell/CI failure**
```bash
python3 scripts/detect_identical_public_obfuscated.py \
  --strict \
  --report-path tmp/identical_public_obfuscated_report.json
```

**3. Print the affected game IDs**
```bash
python3 scripts/detect_identical_public_obfuscated.py \
  --list-affected-gamezones \
  --report-path tmp/identical_public_obfuscated_report.json
```

**4. Copy suspicious identical files to quarantine for review**
```bash
python3 scripts/detect_identical_public_obfuscated.py \
  --quarantine \
  --report-path tmp/identical_public_obfuscated_report.json
```

This is the recommended first containment step when you want to inspect suspicious public-vs-obfuscated parity without deleting anything. The script copies the public-side files into a quarantine area under the published runs tree so you can review exactly what matched.

**5. Preview cleanup without deleting anything**
```bash
python3 scripts/detect_identical_public_obfuscated.py \
  --list-affected-gamezones \
  --delete-affected-gamezones \
  --delete-dry-run \
  --report-path tmp/identical_public_obfuscated_report.json
```

**6. Execute cleanup and let the script reconcile root artifacts**
```bash
python3 scripts/detect_identical_public_obfuscated.py \
  --delete-affected-gamezones \
  --list-affected-gamezones \
  --report-path tmp/identical_public_obfuscated_report.json
```

The cleanup flow deletes affected `gamezone-*` folders from:

- `games/raw`
- `games/published/public`
- `games/published/obfuscated`

After a real cleanup delete, the detector automatically runs post-cleanup reconciliation unless you disable it:

- refresh app artifacts (`refresh_app_artifacts.py`)
- materialize root artifact view (`materialize_artifact_view.py`)
- strict validation (`validate_published_outputs.py --strict`)

### Useful flags

- `--public-root /custom/public/root`
- `--obfuscated-root /custom/obfuscated/root`
- `--raw-root games/raw`
- `--extensions .html,.js,.css`
- `--report-path tmp/identical_public_obfuscated_report.json`
- `--strict` return non-zero when identical file pairs are detected
- `--include-appledouble`
- `--include-annotator`
- `--include-vendor-assets`
- `--vendor-asset-domains fonts.googleapis.com,cdn.tailwindcss.com,unpkg.com,cdnjs.cloudflare.com`
- `--quarentine` (alias: `--quarantine`) to auto-copy identical public files into `games/published/runs/run_<timestamp>/quarantine`
- `--quarentine /custom/path` to copy identical public files to a custom destination
- `--list-affected-gamezones`
- `--delete-affected-gamezones` to remove affected `gamezone-*` folders from raw/public/obfuscated
- `--delete-dry-run` to preview cleanup delete targets
- `--skip-post-cleanup` to disable auto post-steps
- `--post-cleanup-manifest /path/to/artifacts_manifest.json` to override latest-run manifest auto-discovery
- `--post-cleanup-run-id run_cleanup_...` to set run id for post-step outputs
- `--post-cleanup-collection-slug vatsal_app_alpha`
- `--post-cleanup-annotator-html-name annotator.html`

### Report shape and interpretation

The detector prints a terminal summary including:

- scanned public file count
- skipped AppleDouble / annotator / vendor asset counts
- comparable pair count
- identical pair count
- affected gamezone count
- missing-in-obfuscated count

When `--report-path` is provided, the JSON report includes keys such as:

- `identical_paths`
- `missing_paths`
- `affected_gamezone_ids`
- `quarantined_paths`
- `deletion`
- `post_cleanup`

A common pattern in this repo is to generate:

- `tmp/identical_public_obfuscated_report.json`

and then inspect or analyze it with helper scripts.

### Notes

- The CLI accepts both `--quarentine` and `--quarantine`; the canonical spelling in prose should be considered `--quarantine`.
- `--strict` is the safest first pass when you want a machine-checkable failure without mutating any files.

### Short practical guidance

When you suspect the obfuscation output may have leaked unchanged artifacts, a good operator sequence is:

1. run a report-only scan
2. rerun with `--strict` if you want shell/CI failure behavior
3. use `--quarantine` to materialize the suspicious identical public files for inspection
4. only then consider `--delete-affected-gamezones` if you intentionally want cleanup + reconciliation

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
- `scripts/sync_to_gcs.py` — sync only top-level `gamezone-*` directories from `games/published/public|obfuscated` to GCS
  - this rule now applies across all targets: `public`, `obfuscated`, and `both`
  - root-level shared artifacts such as `app.json`, `index.json`, annotator HTML, and other non-`gamezone-*` entries are intentionally excluded from this sync path
- `scripts/refresh_app_artifacts.py` — refresh persistent app artifact snapshots
  - defaults to `--reconcile-mode replace` (prunes stale keys; keeps only newest generated key set)
  - use `--reconcile-mode merge` only when you intentionally want cumulative historical keys
- `scripts/materialize_artifact_view.py` — merge run-scoped root view artifacts into `games/published/public|obfuscated`
  - now sanitizes merged records against the actual root asset trees
  - records whose target `index.html` does not exist in the target scope are pruned from `index.json`, `app_tags.json`, and `app.json`
- `scripts/validate_published_outputs.py` — validate outputs/screenshots/artifacts
- `scripts/detect_identical_public_obfuscated.py` — detect `.html/.js/.css` files that are unchanged between public and obfuscated outputs
- `scripts/generate_annotator_entry.py` — render annotator dashboard HTML for run/root published artifact views
- `scripts/deploy_mobile.py` — build run-scoped mobile release bundles under each scope's `bundle/run_<timestamp>/`
  - copies required base artifacts first: `app.json`, `index.json`, `app_tags.json`
  - runs mobile generation using the run-local copied `app.json`
  - copies required mobile artifacts into the same run scope
  - verifies the complete required artifact set before creating `deploy/`, `release.zip`, and `remove.txt`
  - emits very verbose per-item logs for checks, copies, and zip contents
- `scripts/mobile/validate_artifact_orchestration.py` — local mobile artifact validation/generation wrapper
  - defaults to local published input at `games/published/public/app.json`
  - local cloned generator dependencies live under:
    - `scripts/mobile/home_curation/`
    - `scripts/mobile/search/`
    - `scripts/mobile/editorial_feeds/`
    - `scripts/mobile/tmp/`
  - writes run-scoped outputs under `scripts/mobile/run_artifacts/<timestamp>/`
  - compares generated mobile artifacts against a configurable local `--compare-root`
  - defaults to skipping screenshot cleanup in the editorial candidates stage for faster local runs
  - use `--screenshots-cleanup` to opt into the slower screenshot validation/cleanup path
- `scripts/materialize_mobile_artifacts.py` — generate mobile artifacts per scope and materialize them into scope-local `bundle/` directories
  - runs public and obfuscated scopes internally
  - intended target layout is:
    - `games/published/public/bundle/mobile_*.json`
    - `games/published/obfuscated/bundle/mobile_*.json`
  - mobile bundle migration is in progress; existing non-mobile root artifacts are still described by the older flat root layout until the wider namespace migration is completed

## Mobile artifact implementation status
- mobile generation has been cloned into this repo and no longer needs to execute generator scripts from `jabaliapp`
- the local mobile validator now streams child-step output live so slow phases are visible in real time
- the slowest known phase is `scripts/mobile/editorial_feeds/generate_top_feeds.py`, especially the `all_tag_match_counts` build
- bundle namespace migration is intentionally being treated as a separate follow-up refactor from the core mobile localization work

## Mobile release bundle flow

Use the mobile release orchestrator when you want a run-scoped bundle package containing the full required artifact set.

```bash
python3 scripts/deploy_mobile.py --target both
```

For a real operator run with saved terminal output:

```bash
python3 scripts/deploy_mobile.py --target both 2>&1 | tee /tmp/deploy_mobile.log
```

> **Important:** running without `--require-screenshots` should be treated as a **testing / fast iteration path only**. It is useful when you want to exercise the bundle assembly flow quickly, but it is **not** the proper production release path.

Proper production-oriented command:

```bash
python3 scripts/deploy_mobile.py --target both --require-screenshots 2>&1 | tee /tmp/deploy_mobile.log
```

What it does per scope:

- creates `games/published/<scope>/bundle/run_<timestamp>/`
- copies root base artifacts into `artifacts/`:
  - `app.json`
  - `index.json`
  - `app_tags.json`
- fails immediately if any base artifact is missing
- runs `scripts/mobile/validate_artifact_orchestration.py` using the copied run-local `artifacts/app.json`
- copies the required generated mobile artifacts into the same run `artifacts/` directory
- verifies the complete expected set before release creation
- copies the verified set into `deploy/`
- writes child command logs under `bundle/run_<timestamp>/logs/`
- creates `release.zip`
- lazily creates and then reuses a shared strong password at `scripts/mobile/release_zip_password.txt`
- writes `remove.txt` with the shared password and its source path

Run structure per scope:

- `games/published/<scope>/bundle/run_<timestamp>/artifacts/`
- `games/published/<scope>/bundle/run_<timestamp>/deploy/`
- `games/published/<scope>/bundle/run_<timestamp>/logs/`
- `games/published/<scope>/bundle/run_<timestamp>/release.zip`
- `games/published/<scope>/bundle/run_<timestamp>/remove.txt`

The terminal output is intentionally concise for child commands:

- `deploy_mobile.py` still logs all artifact checks and copies
- heavy child command stdout/stderr is redirected into run-local logs
- the terminal prints the child command summary and the log file path instead of streaming the full inner output

Current log files written by the orchestrator include:

- `logs/mobile_generate.log`
- `logs/zip_release.log`

Shared password behavior:

- the first real run lazily creates `scripts/mobile/release_zip_password.txt`
- later runs reuse that same strong password automatically
- each run-local `remove.txt` records both the password and the source shared password path
- zip command logging redacts the password value from terminal/log command summaries

Required mobile artifacts enforced by the release step:

- `home_collections_ids.json`
- `home_filter_manifest.json`
- `editorial_phase3_candidates.json`
- `editorial_layouts.json`
- `taxonomy_search_artifact.json`
- `top_tag_feeds.json`
- `remix_feed.json`
- `tag_registry.json`
- `all_tag_match_counts.json`

Useful flags:

- `--target public|obfuscated|both`
- `--require-screenshots` to forward the slower screenshot cleanup/validation path
- `--shared-password-path /custom/password.txt` to override the shared password location
- `--dry-run` to validate base inputs and print the release plan without running generation or zip creation

Testing-vs-production note:

- without `--require-screenshots`: faster testing path only
- with `--require-screenshots`: proper production-oriented path

Recommended operator commands:

```bash
# safe plan / structure preview
python3 scripts/deploy_mobile.py --target both --dry-run

# real run with concise terminal output + saved transcript
python3 scripts/deploy_mobile.py --target both 2>&1 | tee /tmp/deploy_mobile.log

# proper production-oriented run with the screenshot cleanup path enabled
python3 scripts/deploy_mobile.py --target both --require-screenshots 2>&1 | tee /tmp/deploy_mobile.log
```

## Architecture boundary

`game_publish_pipeline` is an orchestrator layer. It does not implement deploy/obfuscation transforms itself; it coordinates external tool contracts and emits pipeline-level reports.
