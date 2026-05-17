# game_generator

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
- `--remix-prompt`
- `--publish`
- `--upload`
- `--poll-seconds`
- `--matcher-mode` (`v1` or `v2`)
- `--resume-from-run`

Run artifacts are persisted under:

- `pipeline_runs/<run_id>/` (state, events, per-step artifacts)
- `output/<run_id>/` (copied final outputs)

## `demo_pipeline_launch.py`

Launches a new run, detects the new run id, starts dashboard serving, and prints `watch live` URL.

```bash
python3 scripts/demo_pipeline_launch.py "your prompt" --poll-seconds 5
```

Useful flags:

- `--remix-prompt`
- `--publish`
- `--upload`
- `--no-open`

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
