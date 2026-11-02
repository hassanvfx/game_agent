# game_generator

## Overview and pipeline position

This is the top-level prompt orchestrator. It calls sibling tools through CLI/JSON
contracts and records progress, command output, events, and dashboard data. It
currently launches `creative_remix_v5` in `game_refactoring` after matching.

```text
prompt + optional remix prompt
              |
              v
       game_matcher_v2 ---> ranked games + source references
              |
              v
       game_refactoring -> final output folders
              |
              v  (--publish)
   game_publish_pipeline -> public + obfuscated bundles + report
              |
              v  (--upload, after publish)
           GCS sync

All stages -> pipeline_runs/<run_id>/ -> observer / live dashboard
Results    -> output/<run_id>/
```

Inputs require a populated catalog and resolvable local sources. Publishing and
uploading are opt-in; use `--publish --upload` together for the full cloud path.
Cloud upload here uses GCS; the R2 uploader is a separate tool.
`--resume-from-run` continues an existing run from publish/finalize rather than
restarting every stage. Batch execution is serial and has separate persisted state.

All commands below run from `tools/game_generator/`. From the repository root,
prefix script paths with `tools/game_generator/`.

See the [workspace overview](../../README.md) and
[publishing tool](../game_publish_pipeline/README.md).

Observable orchestration CLI for game generation runs.

## Primary CLI scripts

- `scripts/run_pipeline.py` (main orchestrator)
- `scripts/demo_pipeline_launch.py` (convenience launcher + dashboard open)
- `scripts/observe_pipeline_run.py` (state/event observer)
- `scripts/serve_pipeline_dashboard.py` (local dashboard server)

## `run_pipeline.py`

```bash
python3 scripts/run_pipeline.py "your prompt"
```

Arguments (from `parse_args`):

- positional `prompt`
- `--limit`
- `--remix-prompt`
- `--publish`
- `--upload`
- `--poll-seconds`
- `--matcher-mode` (`legacy` or `v2`; default `v2`)
- `--resume-from-run`

When `--upload` is enabled, `run_pipeline.py` now performs a **non-interactive gcloud auth preflight** before expensive work starts. It fails fast if no active `gcloud` account is available.

Run artifacts are persisted under:

- `pipeline_runs/<run_id>/` (state, events, per-step artifacts)
- `output/<run_id>/` (copied final outputs)

## `demo_pipeline_launch.py`

Launches a new run, detects the new run id, starts dashboard serving, and prints `watch live` URL.

```bash
python3 scripts/demo_pipeline_launch.py "your prompt" --poll-seconds 5
```

Useful flags:

- `--limit`
- `--remix-prompt`
- `--publish`
- `--upload`
- `--no-open`

## `run_batch_pipeline.py`

Runs a **durable serial batch** of `run_pipeline.py` items from a manifest with top-level defaults plus per-item overrides.

```bash
python3 scripts/run_batch_pipeline.py --manifest batch_manifest.json
python3 scripts/run_batch_pipeline.py --resume-batch <batch_id>
```

Manifest shape:

```json
{
  "defaults": {
    "limit": 2,
    "remix_prompt": null,
    "publish": false,
    "upload": false,
    "poll_seconds": 60,
    "matcher_mode": "v2"
  },
  "runs": [
    {"prompt": "3d gta"},
    {"prompt": "mario kart in space", "limit": 5, "remix_prompt": "more neon arcade"}
  ]
}
```

Batch artifacts are persisted under:

- `batch_runs/<batch_id>/batch_state.json`
- `batch_runs/<batch_id>/events.jsonl`
- `batch_runs/<batch_id>/items/*.json`
- `batch_runs/<batch_id>/manifest.resolved.json`

When any batch item has `upload: true`, `run_batch_pipeline.py` runs the same **gcloud auth preflight** once before item 1 starts. Failed preflight blocks the batch before matcher/refactor/publish work begins.

## `observe_batch_pipeline.py`

Read a persisted batch run and print JSON or terminal view.

```bash
python3 scripts/observe_batch_pipeline.py --batch-id <batch_id>
python3 scripts/observe_batch_pipeline.py --batch-dir batch_runs/<batch_id> --json
python3 scripts/observe_batch_pipeline.py --batch-id <batch_id> --watch --interval 3
```

## `observe_pipeline_run.py`

Read a persisted run and print JSON or terminal view.

```bash
python3 scripts/observe_pipeline_run.py --run-id <run_id>
python3 scripts/observe_pipeline_run.py --run-dir pipeline_runs/<run_id> --json
python3 scripts/observe_pipeline_run.py --run-id <run_id> --watch --interval 3
```

## `serve_pipeline_dashboard.py`

Serves `pipeline_runs/<run>/dashboard/` via local HTTP.

```bash
python3 scripts/serve_pipeline_dashboard.py --run-id <run_id>
```

Flags:

- `--run-id` or `--run-dir` (required, mutually exclusive)
- `--port` (optional override)

Default port is deterministic from run path hash.

### Dashboard timing and maintenance

The dashboard now displays:

- total run duration in human-readable form (`22s`, `5m 7s`, `1h 2m 9s`)
- per-stage timing for `Match`, `Refactor`, and `Publish`
- a large live stopwatch-style run counter (`MM:SS` / `HH:MM:SS`) that updates every second while the run is active
- timestamp-backed timing for both successful and failed runs when stage artifacts exist

Validated sample artifact cases:

- successful run: `pipeline_runs/run_pipeline_20260517T110057Z`
- failed run: `pipeline_runs/run_pipeline_20260517T124528Z`

For the full maintenance workflow and artifact walkthrough, see:

- `docs/pipeline-dashboard-maintenance.md`

## Architecture boundary

`game_generator` orchestrates multi-repo execution and observability. It calls out to external tools (matcher/refactoring/publish/obfuscation layers) and persists canonical run state/events for inspection.
