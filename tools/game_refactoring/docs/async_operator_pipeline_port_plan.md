# Async Operator Pipeline Launcher Plan

## Goal

Confirm whether this repository still needs an async orchestration port from the sibling `game_remix_editor`, and if not, document the exact remaining work.

## Conclusion

The async launcher pattern is already present in this repository.

The important async behavior from the sibling repo is:

1. create a run scaffold
2. launch the long-running batch runner with `subprocess.Popen(...)`
3. detach it with `start_new_session=True`
4. write launcher stdout/stderr + invocation metadata
5. return immediately with a pollable run payload
6. expose separate `status` and `result`/`finish` commands

This repository's `scripts/creative_refactor_cli.py` already implements that same pattern.

## Evidence

### Async detached launch already exists

In `scripts/creative_refactor_cli.py`, `start_batch()`:

- creates the run via `create_run.py`
- selects the batch runner
- launches it with `subprocess.Popen(...)`
- uses `start_new_session=True`
- writes:
  - `batch_launcher_stdout.txt`
  - `batch_launcher_stderr.txt`
  - `batch_launcher_invocation.json`
- returns a payload containing:
  - `run_id`
  - `run_dir`
  - `pid`
  - launcher artifact paths

### Pollable status/result endpoints already exist

The same file already exposes:

- `start-batch`
- `status`
- `result`
- `finish`

Those commands resolve `run_state.json` and output pollable run status and final output directories.

## Delta Assessment

## What does **not** need to be ported

No deep `asyncio` rewrite is needed for:

- `scripts/run_operator_pipeline_batch.py`
- `scripts/run_operator_pipeline_game.py`

The sibling repo's async model is not based on converting workers to async coroutines.
It is based on detached process orchestration at the CLI launcher layer.

That launcher layer is already here.

## What remains to validate

The real remaining task is not "port async".
It is:

1. validate the detached launcher path in this repo end to end
2. run the real generic two-node chain through `creative_refactor_cli.py start-batch`
3. poll with `status`
4. finish with `result` / `finish`
5. confirm the two-node Spanish + palette inversion flow works under the detached launcher path

## Files involved

### Already sufficient
- `scripts/creative_refactor_cli.py`
- `scripts/run_operator_pipeline_batch.py`
- `scripts/run_operator_pipeline_game.py`

### Current proving assets
- `fixtures/sample_manifest_generic_spanish.json`
- `prompts/operators_v2/01_gameplay_narrative.md`
- `prompts/operators_v2/02_invert_palette_after_translation.md`

## Next execution steps

1. start the real two-node run via:
   - `python3 scripts/creative_refactor_cli.py start-batch ...`
2. capture the returned `run_id`
3. poll:
   - `python3 scripts/creative_refactor_cli.py status --run-id <run_id>`
4. when complete, resolve:
   - `python3 scripts/creative_refactor_cli.py finish --run-id <run_id>`
5. inspect:
   - second node execution
   - contract gating
   - final output artifacts

## Expected success criteria

- `start-batch` returns immediately
- the run continues in the background
- `status` shows pollable progress
- `finish` returns a completed run
- the second node only runs after a valid upstream Spanish contract
- the second node applies the palette inversion and emits a valid contract