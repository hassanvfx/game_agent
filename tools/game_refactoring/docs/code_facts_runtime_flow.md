# Code Facts: Runtime Flow

This document records concrete observations from the current codebase about top-level runtime flow.

It is an evidence document, not a design proposal.

## Confidence legend

- **Confirmed**: directly supported by the cited code
- **Unconfirmed**: plausible but not yet validated in the inspected files
- **Unknown**: not yet inspected

## Sources read

- `scripts/creative_refactor_cli.py`
- `scripts/creative_refactor_runtime.py`
- `scripts/run_operator_pipeline_batch.py`
- `scripts/run_operator_pipeline_game.py`
- `scripts/operator_registry_v2.py`
- `configs/operator_pipeline_v2.json`

## Observation 1 — The top-level CLI chooses between legacy and v2 batch runners

**Status:** Confirmed

**Evidence:**
- `scripts/creative_refactor_cli.py`
  - `add_batch_args()` defines `--pipeline` with choices `v2` and `legacy`
  - `start_batch()` selects:
    - `run_operator_pipeline_batch.py` when `args.pipeline == "v2"`
    - `run_parallel_batch.py` otherwise

**Interpretation:**
The formal CLI is already structured to switch between two orchestration paths:
- legacy batch path
- operator-pipeline v2 batch path

## Observation 2 — `start-batch` creates the run first, then launches the batch runner as a background process

**Status:** Confirmed

**Evidence:**
- `scripts/creative_refactor_cli.py`
  - `start_batch()` calls `create_run.py`
  - resolves remix prompt from CLI args, then falls back to manifest top-level `remix_prompt`
  - constructs a batch runner command
  - launches it with `subprocess.Popen(...)`
  - writes:
    - `batch_launcher_stdout.txt`
    - `batch_launcher_stderr.txt`
    - `batch_launcher_invocation.json`

**Interpretation:**
The CLI does not perform orchestration inline. It creates a run, launches a separate orchestrator process, and returns a payload pointing to run artifacts.

When no CLI prompt override is supplied, the launcher can still carry a manifest-wide baseline `remix_prompt` into the run.

## Observation 3 — runtime worker execution is centralized in `execute_worker_command()`

**Status:** Confirmed

**Evidence:**
- `scripts/creative_refactor_runtime.py`
  - `execute_worker_command()`:
    - launches subprocess in a new session
    - streams stdout/stderr to files
    - supports timeout
    - kills timed-out process group
    - supports heartbeat callback
    - returns a structured `WorkerExecutionResult`

**Interpretation:**
There is already a reusable worker execution primitive shared across subsystems.

## Observation 4 — the v2 batch runner prepares inputs before launching per-game workers

**Status:** Confirmed

**Evidence:**
- `scripts/run_operator_pipeline_batch.py`
  - `main()` calls:
    - `prepare_inputs.py`
    - optionally `run_spec_adaptor(...)`
    - `initialize_run_status(...)`
    - `build_dashboard.py`
    - `write_dashboard_launcher.py`

**Interpretation:**
The v2 batch path is:
1. ensure run exists
2. prepare inputs
3. optionally adapt specs
4. initialize run status
5. launch per-game workers with bounded concurrency

## Observation 5 — game concurrency is managed at the batch-runner level

**Status:** Confirmed

**Evidence:**
- `scripts/run_operator_pipeline_batch.py`
  - `pending` list is built from `run_dir/input_manifest.json`
  - `active` worker dictionary tracks live game workers
  - launch loop only schedules new workers while `len(active) < args.max_concurrency`
  - poll loop watches active worker processes and heartbeat freshness

**Interpretation:**
Parallelism is across games, controlled centrally by the batch runner.

The v2 batch runner is also the place where effective per-game prompt resolution now occurs.

## Observation 6 — per-game operator stages run sequentially inside one game worker

**Status:** Confirmed

**Evidence:**
- `scripts/run_operator_pipeline_game.py`
  - `operators = resolve_through(registry, args.through)`
  - outer loop iterates operators in order
  - inner loop iterates attempts for one operator
  - next operator starts only after current operator succeeds
  - failure after retries raises `OperatorPipelineGameError`

**Interpretation:**
Current concurrency model is:
- many games in parallel
- one ordered stage sequence per game

The effective prompt used by that game worker can now differ across games in the same run.

## Observation 6A — v2 prompt resolution is now per game, not only per run

**Status:** Confirmed

**Evidence:**
- `scripts/create_run.py`
  - stores top-level manifest baseline in `run_state["manifest_remix_prompt"]`
  - stores per-game override in `game_state["manifest_remix_prompt"]`
- `scripts/run_operator_pipeline_batch.py`
  - resolves effective game prompt in this order:
    - CLI prompt
    - per-game manifest prompt
    - top-level manifest prompt
    - fallback
- `scripts/run_operator_pipeline_game.py`
  - receives the already-resolved effective prompt
  - builds operator prompt text from that effective per-game prompt

**Interpretation:**
The v2 runtime no longer assumes one prompt for every game in the same run. Manifest-driven multi-game prompt variation is now supported without duplicating the workflow definition.

## Observation 7 — the registry/config already defines ordered operators through manifest-like JSON

**Status:** Confirmed

**Evidence:**
- `configs/operator_pipeline_v2.json`
  - contains:
    - `pipeline_id`
    - `max_retries_per_stage`
    - `default_agent_timeout_seconds`
    - ordered `operators`
- `scripts/operator_registry_v2.py`
  - validates unique operator ids
  - validates unique stage numbers
  - requires prompt files
  - requires stage numbers to be sequential starting at 1
  - resolves one step or all steps through a target operator id

**Interpretation:**
The current operator chain is already partially abstracted through config + prompt files.

## Observation 8 — the current abstraction is operator-config driven, but runtime behavior is not fully generic

**Status:** Confirmed

**Evidence:**
- `scripts/run_operator_pipeline_game.py`
  - uses generic registry loading and ordered operator resolution
  - but still contains operator-specific logic:
    - `if operator.id == "media_mapper" and (remaining_urls or remaining_media_candidates): ...`

**Interpretation:**
The chain order is configurable, but at least some stage semantics remain hard-coded in Python.

## Observation 9 — the game worker always resets `pipeline/current` from the game input mirror before stage execution

**Status:** Confirmed

**Evidence:**
- `scripts/run_operator_pipeline_game.py`
  - `input_dir = Path(game_state["input_mirror_path"]).resolve()`
  - `current_workspace = pipeline_dir / "current"`
  - `copy_workspace(input_dir, current_workspace, replace=True)`

**Interpretation:**
The per-game pipeline starts from a fresh copy of the prepared input mirror, not from prior output state.

## Observation 10 — each stage attempt gets its own copied workspace and artifacts

**Status:** Confirmed

**Evidence:**
- `scripts/run_operator_pipeline_game.py`
  - `attempt_paths()` defines per-attempt paths
  - each attempt has:
    - `workspace/`
    - `operator_stage_state.json`
    - `operator_prompt.txt`
    - `operator_stdout.txt`
    - `operator_stderr.txt`
    - `operator_result.json`
    - `operator_invocation.json`
    - `media_policy_report.json`

**Interpretation:**
The runtime preserves stage-attempt artifacts explicitly, which supports retry and inspection.

## Observation 11 — successful stages promote their attempt workspace back into `pipeline/current`

**Status:** Confirmed

**Evidence:**
- `scripts/run_operator_pipeline_game.py`
  - if `operator_status == "completed"`:
    - `copy_workspace(paths["workspace"], current_workspace, replace=True)`
    - append stage slug to completed list
    - continue to next stage

**Interpretation:**
Promotion is workspace-based. `pipeline/current` acts as the latest-good state for the next stage.

## Observation 12 — final game output is produced by copying `pipeline/current` to the game output directory

**Status:** Confirmed

**Evidence:**
- `scripts/run_operator_pipeline_game.py`
  - after all stages succeed:
    - `copy_workspace(current_workspace, output_dir, replace=True)`

**Interpretation:**
The final transformed game artifact is the promoted end-state workspace after the last successful stage.

## Observation 13 — stale-heartbeat handling exists at the batch-runner level

**Status:** Confirmed

**Evidence:**
- `scripts/run_operator_pipeline_batch.py`
  - watches `heartbeat_at` from either:
    - current operator stage state
    - fallback job state
  - detects gap beyond `--stale-heartbeat-seconds`
  - terminates worker
  - marks game failed
  - updates run state counters

**Interpretation:**
Stale worker detection is owned by the batch orchestrator, not the per-stage executor.

## Observation 14 — run/game state writing is distributed across multiple layers

**Status:** Confirmed

**Evidence:**
- `scripts/run_operator_pipeline_batch.py`
  - initializes and finalizes run status
  - increments completed/failed counters
- `scripts/run_operator_pipeline_game.py`
  - updates per-game status before, during, and after operator execution
- `scripts/spec_adaptor.py`
  - writes into both spec-adaptor job state and top-level run state

**Interpretation:**
State management is not fully centralized in one module. Multiple layers write into overlapping run/game state surfaces.

## Open questions

### 1. Where exactly is `input_manifest.json` produced and how much shape does it guarantee?
**Status:** Unknown  
**Next file to inspect:** `scripts/prepare_inputs.py`

### 2. How much of the legacy flow still overlaps with the v2 flow in practice?
**Status:** Unknown  
**Next files to inspect:** `scripts/run_parallel_batch.py`, `scripts/run_single_game.py`

### 3. Are there additional hard-coded operator semantics beyond `media_mapper`?
**Status:** Unknown  
**Next supporting files to inspect:** prompt files and media-policy helpers

## Delta hints vs intended architecture

These are not final conclusions; they are preliminary deltas.

### Likely aligned
- run-level orchestrator exists
- per-game concurrency exists
- ordered per-game stage pipeline exists
- config-driven operator order exists
- promotion-based workspace model exists

### Likely misaligned with a future generic pipeline goal
- operator-specific logic still exists in Python
- prompt packet contains heavy stage-specific media instructions
- some retry/failure logic is stage-aware rather than fully generic

These hints need deeper validation before any change is proposed.