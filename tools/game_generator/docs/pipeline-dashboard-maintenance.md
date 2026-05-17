# Pipeline Dashboard Maintenance

This document explains how the local pipeline dashboard is assembled, which run artifacts drive it, and how to validate timing behavior using known sample runs.

---

## Purpose

The dashboard under `pipeline_runs/<run_id>/dashboard/` is the operator-friendly view over a persisted pipeline run. It is backed by JSON artifacts written during orchestration and refreshed by the local dashboard server.

The dashboard is intended to answer:

- Which stage is the run in?
- Did the run succeed or fail?
- How long did the overall run take?
- How long did each stage take?
- How long has the run been active right now?
- Which artifacts should I inspect next?

---

## Source of Truth

### Orchestrator payload writer

- `scripts/run_pipeline.py`

`PipelineRun.save_state()` writes:

- `pipeline_runs/<run_id>/run_state.json`
- `pipeline_runs/<run_id>/dashboard/dashboard_data.json`

The base dashboard payload includes:

- run-level timing
  - `started_at`
  - `updated_at`
  - `completed_at`
- run metadata
  - `run_id`
  - `prompt`
  - `status`
  - `current_step`
- step records
  - `steps[*].id`
  - `steps[*].status`
  - `steps[*].details.started_at`
  - `steps[*].details.completed_at`

### Presenter / view-model enricher

- `scripts/pipeline_dashboard_presenter.py`

This module enriches the base payload with:

- `prompt_helper`
- `current_run_view`
- `recent_runs`
- `cost_story`

The timing display is derived here, not in the orchestrator core.

It now powers both:

- static human-readable duration summaries
- a large browser-side live stopwatch that counts from `started_at` until the run ends

### Local server refresh

- `scripts/serve_pipeline_dashboard.py`

`refresh_dashboard_assets(...)` reloads `dashboard_data.json`, enriches it with presenter fields, and rewrites the file before serving `index.html`.

---

## Human-Readable Timing Rules

The dashboard uses the following formatting:

- `< 60s` → `22s`
- `>= 60s and < 3600s` → `5m 7s`
- `>= 3600s` → `1h 2m 9s`

The large live counter uses clock-style formatting:

- under one hour → `MM:SS`
- one hour or more → `HH:MM:SS`

Fallback rules:

- If a run has `started_at` and `completed_at`, duration is computed from those values.
- If `completed_at` is missing, the dashboard may fall back to `updated_at` as the effective end marker.
- For a stage, timing is only shown when the stage has real persisted timing fields.
- Pending stages with no start time remain unset.
- The live stopwatch counts in the browser every second until an end timestamp is available.

---

## Sample Cases

Use these persisted runs as the baseline maintenance fixtures.

### 1) Successful sample run

- Run ID: `run_pipeline_20260517T110057Z`
- Path: `pipeline_runs/run_pipeline_20260517T110057Z`

Expected timing after dashboard refresh:

- total run: `5m 7s`
- match: `22s`
- refactor: `4m 25s`
- publish: `20s`

This run is useful for validating:

- full happy-path stage timing
- run-level total duration
- live stopwatch rendering for a completed run
- stage ordering
- successful publish visuals

### 2) Failed sample run

- Run ID: `run_pipeline_20260517T124528Z`
- Path: `pipeline_runs/run_pipeline_20260517T124528Z`

Expected timing after dashboard refresh:

- total run: `20s`
- match failed after `20s`
- refactor: pending / no duration
- publish: pending / no duration

This run is useful for validating:

- failed-stage timing
- pending-stage blanks
- live stopwatch rendering for a failed run with an end timestamp
- error-state rendering

---

## Maintenance Workflow

### Refresh a run dashboard

```bash
python3 scripts/serve_pipeline_dashboard.py --run-id run_pipeline_20260517T110057Z
```

This refreshes the dashboard assets and serves the run locally.

### Validate the observer payload

```bash
python3 scripts/observe_pipeline_run.py --run-id run_pipeline_20260517T110057Z --json
```

Use this when you want to compare the observer-friendly payload against the dashboard payload.

### Re-enrich sample dashboards in a quick script

```bash
python3 - <<'PY'
from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path('scripts').resolve()))
from serve_pipeline_dashboard import refresh_dashboard_assets

for run_id in [
    'run_pipeline_20260517T110057Z',
    'run_pipeline_20260517T124528Z',
]:
    run_dir = Path('pipeline_runs') / run_id
    refresh_dashboard_assets(run_dir.resolve(), (run_dir / 'dashboard').resolve())
    payload = json.loads((run_dir / 'dashboard' / 'dashboard_data.json').read_text())
    print(run_id, json.dumps(payload.get('current_run_view', {}).get('timing', {}), indent=2))
PY
```

---

## Troubleshooting

### Stage durations are blank

Check whether the stage record has timing fields under:

- `dashboard_data.json` → `steps[*].details.started_at`
- `dashboard_data.json` → `steps[*].details.completed_at`

If those are missing, the presenter cannot compute a duration.

### Total duration looks correct but stage durations do not

This usually means the run-level fields exist, but the presenter is reading the wrong step shape or the stage data was not refreshed after a code change.

Refresh the dashboard assets again via `serve_pipeline_dashboard.py`.

### The large live timer does not update

Check that the generated dashboard HTML still contains:

- `renderRunTimer(...)`
- `updateLiveRunTimer()`
- `installLiveRunTimerTick()`

Also confirm the timer element is rendered with `data-started-at` and `data-ended-at` attributes.

### Completed run has no `completed_at`

Check whether the base payload from `scripts/run_pipeline.py` includes `completed_at`. The presenter can fall back to `updated_at`, but completed runs should ideally expose the explicit field.

---

## Related Files

- `scripts/run_pipeline.py`
- `scripts/pipeline_dashboard_presenter.py`
- `scripts/serve_pipeline_dashboard.py`
- `scripts/observe_pipeline_run.py`
- `docs/journals/game-pipeline-orchestrator.md`
