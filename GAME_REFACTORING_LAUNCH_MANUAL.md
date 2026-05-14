# Game Refactoring Launch Manual

This document is a practical operator manual for launching `tools/game_refactoring` jobs reliably.

It focuses on the current, preferred workflow:

- **workflow CLI**
- **pipeline v2**
- local raw game inputs
- repeatable small-batch testing

---

## 1. Recommended entrypoint

Use the **workflow CLI**:

```bash
python3 tools/game_refactoring/scripts/game_workflow.py
```

This is the preferred top-level launcher when you want:

- a named workflow such as `creative_remix_v4`
- external game manifests
- delegation into the existing batch pipeline
- stable orchestration behavior

The workflow CLI writes a generated workflow manifest under:

```text
tools/game_refactoring/runs/_workflow_manifests/
```

and then launches the batch path through:

```text
tools/game_refactoring/scripts/creative_refactor_cli.py --json start-batch ...
```

---

## 2. Current recommended workflow for remix jobs

For modern remix runs, use:

- **workflow id:** `creative_remix_v4`
- **pipeline:** `v2`

Example:

```bash
python3 tools/game_refactoring/scripts/game_workflow.py \
  --id creative_remix_v4 \
  --games-manifest-source tmp/my_manifest.json \
  --remix-prompt "Kawaii Style" \
  --json
```

---

## 3. Default model

The current default model across the main `game_refactoring` entrypoints is:

```text
gpt-5.5
```

This default now applies in:

- `tools/game_refactoring/scripts/game_workflow.py`
- `tools/game_refactoring/scripts/creative_refactor_cli.py`
- `tools/game_refactoring/scripts/run_operator_pipeline_batch.py`
- `tools/game_refactoring/scripts/run_operator_pipeline_game.py`
- `tools/game_refactoring/scripts/run_single_game.py`
- `tools/game_refactoring/scripts/spec_adaptor.py`

You can still override the model explicitly with `--model`.

Example:

```bash
python3 tools/game_refactoring/scripts/game_workflow.py \
  --id creative_remix_v4 \
  --games-manifest-source tmp/my_manifest.json \
  --remix-prompt "Kawaii Style" \
  --model gpt-5.5 \
  --json
```

---

## 4. Important source-path rule

Your manifest entries must point to **real, existing local paths**.

This failed before because an older fixture manifest referenced stale external paths like:

```text
/Volumes/backup/game_maker/catalogs/raw/gamezone-...
```

If those folders are not mounted locally, `create_run.py` will fail immediately.

### Safest source pool

Use local raw games under:

```text
games/raw/
```

Each game is typically a folder like:

```text
games/raw/gamezone-<uuid>/
```

---

## 5. Manifest shape

A minimal working manifest looks like:

```json
{
  "manifest_version": "1.0.0",
  "run_label": "two-random-kawaii-style-local-raw-test",
  "created_at": "2026-05-13T22:12:00Z",
  "games": [
    {
      "game_id": "a665fa1f-da62-4379-97e1-0da9934c210a",
      "source_path": "/absolute/path/to/games/raw/gamezone-a665fa1f-da62-4379-97e1-0da9934c210a",
      "display_name": "gamezone-a665fa1f-da62-4379-97e1-0da9934c210a"
    }
  ]
}
```

### Practical guidance

For local raw runs:

- `game_id` should usually be the folder UUID portion
- `source_path` should be the absolute local folder path
- `display_name` can be the folder name

---

## 6. Helper script pattern for small experiments

For short experiments, prefer a small script in `tmp/` instead of long shell one-liners.

Example helper script:

```text
tmp/build_two_random_kawaii_manifest_from_local_raw.py
```

This script can:

- scan `games/raw/`
- choose random games
- write a small manifest to `tmp/`

### Run the helper

```bash
python3 tmp/build_two_random_kawaii_manifest_from_local_raw.py
```

Example output:

```text
Created: tmp/game_refactoring_two_random_kawaii_local_raw_manifest.json
a665fa1f-da62-4379-97e1-0da9934c210a -> /Users/hassan/repos/game_agent/games/raw/gamezone-a665fa1f-da62-4379-97e1-0da9934c210a
1a482938-123b-4e60-baf0-e727d5110752 -> /Users/hassan/repos/game_agent/games/raw/gamezone-1a482938-123b-4e60-baf0-e727d5110752
```

---

## 7. Standard local 2-game test flow

### Step 1: build a local raw manifest

```bash
python3 tmp/build_two_random_kawaii_manifest_from_local_raw.py
```

This creates:

```text
tmp/game_refactoring_two_random_kawaii_local_raw_manifest.json
```

### Step 2: launch the workflow

```bash
python3 tools/game_refactoring/scripts/game_workflow.py \
  --id creative_remix_v4 \
  --games-manifest-source tmp/game_refactoring_two_random_kawaii_local_raw_manifest.json \
  --remix-prompt "Kawaii Style" \
  --json
```

### Expected response

The launcher returns a JSON payload like:

```json
{
  "run_id": "run_game_remixer_20260514T042845Z",
  "run_dir": "/.../tools/game_refactoring/runs/run_game_remixer_20260514T042845Z",
  "status_path": "/.../run_state.json",
  "dashboard_path": "/.../dashboard/index.html",
  "output_root": "/.../output",
  "status": "created",
  "current_phase": "run_created",
  "pid": 97271,
  "workflow_id": "creative_remix_v4",
  "workflow_manifest_path": "/.../_workflow_manifests/creative_remix_v4__game_refactoring_two_random_kawaii_local_raw_manifest.json",
  "workflow_games_count": 2
}
```

---

## 8. How to inspect a running batch

### Check run state

Read:

```text
tools/game_refactoring/runs/<run_id>/run_state.json
```

Typical live fields:

- `status`
- `current_phase`
- `games_total`
- `games_transform_completed`
- `games_transform_failed`
- `remix_prompt`

### Check launcher invocation

Read:

```text
tools/game_refactoring/runs/<run_id>/batch_launcher_invocation.json
```

This confirms:

- actual batch runner used
- manifest path
- model
- concurrency
- prompt presence

### Check a game’s node state

Read:

```text
tools/game_refactoring/runs/<run_id>/games/<game_id>/operator_pipeline/<stage_slug>/attempt_01/operator_stage_state.json
```

Useful fields:

- `status`
- `started_at`
- `heartbeat_at`
- `model`
- `timeout_seconds`
- `operator_usage_path`

---

## 9. Cost and usage artifacts

The current system captures usage at several levels.

### Spec adaptor proof path

Artifacts:

```text
spec_adaptor/recomposition_usage.json
spec_adaptor/adaptation_report.json
```

### Per node attempt

Artifacts:

```text
games/<game_id>/operator_pipeline/<stage_slug>/attempt_<nn>/operator_usage.json
games/<game_id>/operator_pipeline/<stage_slug>/attempt_<nn>/operator_result.json
```

### Per game aggregate

Artifact:

```text
games/<game_id>/operator_pipeline/cost_report.json
```

### Per run aggregate

Artifact:

```text
runs/<run_id>/cost_report.json
```

### Captured fields

Usage summaries include:

- `inputTokens`
- `outputTokens`
- `cacheReadTokens`
- `cacheWriteTokens`
- provider-reported `totalCost`
- `totalTokens`
- `totalTokensIncludingCache`
- projected USD cost breakdown
- projected total cost

---

## 10. Projected cost basis

When provider-reported `totalCost` is `0`, projected pricing is computed using:

```text
Input:        $5.00 / 1M tokens
Cached input: $0.50 / 1M tokens
Output:      $30.00 / 1M tokens
```

Projected values are included in usage summaries and aggregate reports.

---

## 11. Common failure modes

### Failure: source_path does not exist

Example:

```text
Game '<id>' source_path does not exist: /Volumes/backup/...
```

Meaning:
- your manifest points to a path not available on this machine

Fix:
- rebuild the manifest from `games/raw/`
- ensure `source_path` is local and absolute

### Failure: workflow launcher works, but batch setup fails

Meaning:
- `game_workflow.py` is fine
- failure is downstream in manifest validation or run setup

Check:
- `batch_launcher_invocation.json`
- `run_state.json`
- the manifest path under `_workflow_manifests/`

### Stale workers

If a game appears stuck, inspect:

```text
operator_stage_state.json
```

especially:
- `status`
- `heartbeat_at`

---

## 12. Recommended small debugging scripts

When debugging, prefer small reusable scripts in `tmp/`.

Examples:

- `tmp/build_two_random_kawaii_manifest_from_local_raw.py`
- `tmp/inspect_workflow_cli_failure.py`
- `tmp/inspect_create_run_failure.py`

Pattern:
- keep scripts focused
- print explicit stdout/stderr
- avoid very long one-line shell commands

---

## 13. Good repeatable launch recipe

This is the safest future recipe for small local tests:

### Build manifest
```bash
python3 tmp/build_two_random_kawaii_manifest_from_local_raw.py
```

### Launch workflow
```bash
python3 tools/game_refactoring/scripts/game_workflow.py \
  --id creative_remix_v4 \
  --games-manifest-source tmp/game_refactoring_two_random_kawaii_local_raw_manifest.json \
  --remix-prompt "Kawaii Style" \
  --json
```

### Inspect run
```bash
python3 - <<'PY'
import json
from pathlib import Path

run_dir = Path("tools/game_refactoring/runs/run_game_remixer_20260514T042845Z")
for rel in [
    "run_state.json",
    "batch_launcher_invocation.json",
]:
    p = run_dir / rel
    print(f"--- {rel} ---")
    print(p.read_text(encoding="utf-8"))
PY
```

---

## 14. Summary

If you want a stable, low-friction launch path:

- use `scripts/game_workflow.py`
- use workflow id `creative_remix_v4`
- use local manifests built from `games/raw/`
- prefer `tmp/` helper scripts for manifest generation and debugging
- inspect `run_state.json` and `batch_launcher_invocation.json` first when something goes wrong

That is the current recommended operating pattern for local `game_refactoring` jobs.