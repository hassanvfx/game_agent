# Game Remixer

A generic, standalone remixer runtime extracted from the validated creative-line flow.

## Purpose

`/game_remixer/` is intended to become a reusable transformation engine that:

- accepts a manifest or list of source games
- creates a timestamped run by default
- mirrors selected input games locally into the run tree
- verifies input integrity before transform starts
- serves original and transformed artifacts from relative local paths
- generates a per-run dashboard and launcher
- runs creative transforms with bounded parallel execution
- supports watchdog / stale-worker monitoring
- exposes run and per-game runtime state in a dashboard

## Current status

Validated extraction milestone with prompt-aware preset runtime support.

Implemented:

- package directory structure
- timestamped run creation
- run-local directory tree
- local mirrored input copy
- integrity verification report
- task-packet generation
- single-game execution
- tiny sequential multi-game execution
- bounded parallel batch execution
- watchdog / stale-worker failure handling
- richer dashboard generation with active job / heartbeat visibility
- helper launcher for opening the latest dashboard over HTTP
- style preset selection
- prompt-aware runtime spec adaptation
- run-local adapted prompt/spec bundle generation

## Main runtime location on Elements

The active extracted runtime lives at:

- `/Volumes/Elements/game_remix_editor`

Most day-to-day usage should happen from that path, not from the local repo copy.

## Key files

Core scripts:

- `/Volumes/Elements/game_remix_editor/scripts/create_run.py`
- `/Volumes/Elements/game_remix_editor/scripts/prepare_inputs.py`
- `/Volumes/Elements/game_remix_editor/scripts/generate_task_packet.py`
- `/Volumes/Elements/game_remix_editor/scripts/run_single_game.py`
- `/Volumes/Elements/game_remix_editor/scripts/run_sample_batch.py`
- `/Volumes/Elements/game_remix_editor/scripts/run_parallel_batch.py`
- `/Volumes/Elements/game_remix_editor/scripts/spec_adaptor.py`
- `/Volumes/Elements/game_remix_editor/scripts/creative_refactor_cli.py`
- `/Volumes/Elements/game_remix_editor/scripts/creative_refactor_runtime.py`
- `/Volumes/Elements/game_remix_editor/scripts/debug_creative_refactor.py`
- `/Volumes/Elements/game_remix_editor/scripts/build_dashboard.py`
- `/Volumes/Elements/game_remix_editor/scripts/serve_dashboard.py`
- `/Volumes/Elements/game_remix_editor/scripts/write_dashboard_launcher.py`
- `/Volumes/Elements/game_remix_editor/scripts/open_latest_dashboard.sh`

Preset / contract inputs:

- `/Volumes/Elements/game_remix_editor/styles/neutral_prototype/`
- `/Volumes/Elements/game_remix_editor/styles/cyberpunk/`
- `/Volumes/Elements/game_remix_editor/prompts/audio_policy.md`
- `/Volumes/Elements/game_remix_editor/prompts/network_policy.md`
- `/Volumes/Elements/game_remix_editor/prompts/system_contract.md`
- `/Volumes/Elements/game_remix_editor/prompts/refactor_compliance_spec.md`

## Style preset model

The runtime now separates **global invariant policies** from **style-local preset files**.

### Available presets

- `neutral_prototype`
  - default preset
  - generic white-label mobile-first baseline
  - intended to be overrideable by runtime art/game director prompt intent
- `cyberpunk`
  - compatibility preset
  - preserves the previous opinionated neon cyberpunk / futuristic arcade behavior

### Style-local files

Each preset currently owns the style-sensitive files:

- `creative_remix_contract.md`
- `creative_refactor_agent_template.md`
- `visual_identity_contract.md`
- `theme_policy.md`

### Global invariant files

These remain shared and always-on:

- `audio_policy.md`
- `network_policy.md`
- `system_contract.md`
- `refactor_compliance_spec.md`

## Prompt-aware runtime flow

The runtime now supports a minimal prompt-aware adaptation flow.

At a high level:

1. choose a style preset
2. optionally provide a remix prompt
3. create a run
4. prepare mirrored inputs
5. if a remix prompt exists, create a run-local `spec_adaptor/` bundle
6. copy preset-local files into adapted runtime files
7. append runtime override text to the adapted prompt/spec files
8. generate task packets from the adapted files
9. execute the normal worker pipeline

### Current adaptor behavior

The current `spec_adaptor.py` creates a run-local spec recomposition workspace and asks a first-stage CLI agent to rewrite the editable creative bundle in place before worker fanout begins.

At a high level it now:

- saves the raw remix prompt
- copies preset-local editable files into `spec_adaptor/adapted/`
- copies invariant policy references into `spec_adaptor/invariants/`
- writes a recomposition context + harness
- runs a monitored `cline` recomposition subprocess
- streams recomposition stdout/stderr to run-local files
- emits live spec-adaptor job state and heartbeat updates
- writes a recomposition summary and finalized adaptation report on success

### Spec adaptation runtime observability

Each prompt-aware run emits a run-local `spec_adaptor/` workspace that CLI users can inspect while the batch is running.

Important files:

- `spec_adaptor/spec_adaptor_job_state.json`
  - live spec-adaptor health/status file
  - includes:
    - `status`
    - `started_at`
    - `heartbeat_at`
    - `finished_at`
    - `stdout_path`
    - `stderr_path`
    - `summary_path`
    - `failure_reason`
    - `timeout_seconds`
- `spec_adaptor/spec_adaptor_debug_trace.log`
  - chronological trace of spec-adaptor phases
  - useful for seeing whether the adaptor is in:
    - workspace setup
    - harness creation
    - recomposition launch
    - post-processing / finalization
- `spec_adaptor/recomposition_stdout.txt`
  - streamed stdout from the inner recomposition `cline` process
- `spec_adaptor/recomposition_stderr.txt`
  - streamed stderr from the inner recomposition `cline` process
- `spec_adaptor/recomposition_summary.json`
  - agent-authored completion artifact written by the recomposition step
- `spec_adaptor/adaptation_report.json`
  - finalized structured report written after successful spec-adaptor post-processing
- `spec_adaptor/recomposition_context.json`
  - machine-readable context passed into the recomposition phase
- `spec_adaptor/spec_recomposition_harness.md`
  - full task harness used for the first-stage recomposition agent

#### Status meanings

The most important states to watch are:

- `running`
  - spec adaptation is still active
- `ready`
  - spec adaptation completed successfully and the adapted bundle is ready for downstream workers
- `failed`
  - spec adaptation exited with an error
- `timeout`
  - spec adaptation exceeded its allowed runtime and was terminated

#### How to observe progress from the CLI

Check the run state first:

```zsh
cat /Volumes/Elements/game_remix_editor/runs/<run_id>/run_state.json
```

If the batch is still waiting before worker launch, inspect the spec-adaptor job state:

```zsh
cat /Volumes/Elements/game_remix_editor/runs/<run_id>/spec_adaptor/spec_adaptor_job_state.json
```

Watch the live chronological trace:

```zsh
tail -f /Volumes/Elements/game_remix_editor/runs/<run_id>/spec_adaptor/spec_adaptor_debug_trace.log
```

Watch streamed recomposition stderr/stdout:

```zsh
tail -f /Volumes/Elements/game_remix_editor/runs/<run_id>/spec_adaptor/recomposition_stderr.txt
tail -f /Volumes/Elements/game_remix_editor/runs/<run_id>/spec_adaptor/recomposition_stdout.txt
```

Practical interpretation:

- if `heartbeat_at` keeps moving, the spec-adaptor subprocess is alive
- if `recomposition_summary.json` exists but `adaptation_report.json` does not yet exist, recomposition finished but spec-adaptor finalization is still in progress
- once `run_state["spec_adaptor"]["status"] == "ready"`, the batch can proceed into worker fanout
- if `failure_reason` is populated, inspect the stderr file and debug trace together

## How to run in `/Volumes/Elements/game_remix_editor`

### 1. Open the latest dashboard

Fastest way:

```zsh
zsh /Volumes/Elements/game_remix_editor/scripts/open_latest_dashboard.sh
```

What it does:

- finds the newest run under `/Volumes/Elements/game_remix_editor/runs/`
- kills anything already bound to port `8058`
- starts the Game Remixer HTTP server on port `8058`
- opens the latest dashboard URL

Optional custom port:

```zsh
zsh /Volumes/Elements/game_remix_editor/scripts/open_latest_dashboard.sh 8060
```

### 2. Serve the remixer manually

If you want to serve the runtime yourself:

```zsh
python3 /Volumes/Elements/game_remix_editor/scripts/serve_dashboard.py --port 8058
```

Then open a dashboard URL manually, for example:

```text
http://127.0.0.1:8058/runs/run_game_remixer_20260426T161844Z/dashboard/index.html
```

Important:
- the dashboard is expected to be opened over HTTP
- internal links should be HTTP-served, not opened directly as `file://...`

### 3. Run the tiny sequential sample batch

Default preset-only flow:

```zsh
python3 /Volumes/Elements/game_remix_editor/scripts/run_sample_batch.py \
  --manifest /Volumes/Elements/game_remix_editor/fixtures/sample_manifest_3.json \
  --model gpt-5.4 \
  --agent-timeout 3600
```

Explicit preset:

```zsh
python3 /Volumes/Elements/game_remix_editor/scripts/run_sample_batch.py \
  --manifest /Volumes/Elements/game_remix_editor/fixtures/sample_manifest_3.json \
  --style cyberpunk \
  --model gpt-5.4 \
  --agent-timeout 3600
```

Prompt-aware sequential batch:

```zsh
python3 /Volumes/Elements/game_remix_editor/scripts/run_sample_batch.py \
  --manifest /Volumes/Elements/game_remix_editor/fixtures/sample_manifest_3.json \
  --style neutral_prototype \
  --remix-prompt "Make this feel like a candy-colored toy city with softer HUD treatment, brighter onboarding, and a more playful opening identity." \
  --model gpt-5.4 \
  --agent-timeout 3600
```

This creates a new run under:

- `/Volumes/Elements/game_remix_editor/runs/run_game_remixer_<timestamp>/`

### 4. Manifest-driven batch CLI lifecycle

The user-facing orchestration contract is:

- `start-batch`
  - accepts the manifest-driven run
  - creates the run scaffold
  - launches the batch runner asynchronously
  - returns immediately with the run identity and inspection paths
- `status`
  - authoritative source of truth for whether the run is still running, completed, or failed
- `result`
  - resolves the final output contract for a run
- `finish`
  - alias for `result`

Start a batch asynchronously:

```zsh
python3 /Volumes/Elements/game_remix_editor/scripts/creative_refactor_cli.py --json start-batch \
  --manifest /Volumes/Elements/game_remix_editor/fixtures/sample_manifest_3.json \
  --style neutral_prototype \
  --model gpt-5.4 \
  --agent-timeout 3600 \
  --max-concurrency 2 \
  --poll-seconds 5 \
  --stale-heartbeat-seconds 900
```

Prompt-aware async start:

```zsh
python3 /Volumes/Elements/game_remix_editor/scripts/creative_refactor_cli.py --json start-batch \
  --manifest /Volumes/Elements/game_remix_editor/fixtures/sample_manifest_3.json \
  --style neutral_prototype \
  --remix-prompt "Make this feel like an enchanted wizard-school fantasy world with warm candlelit halls, magical parchment UI, spellbook-inspired panels, whimsical onboarding, house-banner style identity, and a cozy mystical opening mood while keeping the gameplay clear and readable." \
  --model gpt-5.4 \
  --agent-timeout 3600 \
  --max-concurrency 2 \
  --poll-seconds 5 \
  --stale-heartbeat-seconds 900
```

Expected `start-batch` response shape:

```json
{
  "run_id": "run_game_remixer_20260426T000000Z",
  "run_dir": "/Volumes/Elements/game_remix_editor/runs/run_game_remixer_20260426T000000Z",
  "status_path": "/Volumes/Elements/game_remix_editor/runs/run_game_remixer_20260426T000000Z/run_state.json",
  "dashboard_path": "/Volumes/Elements/game_remix_editor/runs/run_game_remixer_20260426T000000Z/dashboard/index.html",
  "output_root": "/Volumes/Elements/game_remix_editor/runs/run_game_remixer_20260426T000000Z/output",
  "status": "created",
  "current_phase": "run_created",
  "updated_at": "2026-04-26T00:00:00Z",
  "pid": 12345,
  "launcher_stdout_path": "/Volumes/Elements/game_remix_editor/runs/run_game_remixer_20260426T000000Z/batch_launcher_stdout.txt",
  "launcher_stderr_path": "/Volumes/Elements/game_remix_editor/runs/run_game_remixer_20260426T000000Z/batch_launcher_stderr.txt",
  "launcher_invocation_path": "/Volumes/Elements/game_remix_editor/runs/run_game_remixer_20260426T000000Z/batch_launcher_invocation.json"
}
```

Poll the run status:

```zsh
python3 /Volumes/Elements/game_remix_editor/scripts/creative_refactor_cli.py --json status \
  --run-id run_game_remixer_20260426T000000Z
```

Expected `status` response shape:

```json
{
  "run_id": "run_game_remixer_20260426T000000Z",
  "run_dir": "/Volumes/Elements/game_remix_editor/runs/run_game_remixer_20260426T000000Z",
  "status": "running",
  "current_phase": "parallel_batch_running",
  "updated_at": "2026-04-26T00:01:00Z",
  "games_total": 3,
  "games_transform_completed": 1,
  "games_transform_failed": 0,
  "dashboard_path": "/Volumes/Elements/game_remix_editor/runs/run_game_remixer_20260426T000000Z/dashboard/index.html",
  "output_root": "/Volumes/Elements/game_remix_editor/runs/run_game_remixer_20260426T000000Z/output",
  "running": true,
  "completed": false,
  "failed": false
}
```

Resolve outputs once complete:

```zsh
python3 /Volumes/Elements/game_remix_editor/scripts/creative_refactor_cli.py --json result \
  --run-id run_game_remixer_20260426T000000Z
```

Equivalent alias:

```zsh
python3 /Volumes/Elements/game_remix_editor/scripts/creative_refactor_cli.py --json finish \
  --run-id run_game_remixer_20260426T000000Z
```

Decision logic:
- if `status.running == true`, the batch is still active
- if `status.completed == true` and `status.failed == false`, the run finished successfully
- if `status.completed == true` and `status.failed == true`, the run reached a terminal failure/incomplete state
- use `result` / `finish` to resolve the final output directory contract

Recommended meanings:
- `--max-concurrency`: max number of active worker games
- `--poll-seconds`: scheduler polling interval
- `--stale-heartbeat-seconds`: stale cutoff before a worker is treated as hung

### 5. Direct batch runner

The lower-level batch runner still exists and remains the validated watchdog-enabled engine behind `start-batch`:

Preset-only:

```zsh
python3 /Volumes/Elements/game_remix_editor/scripts/run_parallel_batch.py \
  --manifest /Volumes/Elements/game_remix_editor/fixtures/sample_manifest_3.json \
  --style neutral_prototype \
  --model gpt-5.4 \
  --agent-timeout 3600 \
  --max-concurrency 2 \
  --poll-seconds 5 \
  --stale-heartbeat-seconds 900
```

Prompt-aware parallel batch:

```zsh
python3 /Volumes/Elements/game_remix_editor/scripts/run_parallel_batch.py \
  --manifest /Volumes/Elements/game_remix_editor/fixtures/sample_manifest_3.json \
  --style neutral_prototype \
  --remix-prompt "Make this feel like an enchanted wizard-school fantasy world with warm candlelit halls, magical parchment UI, spellbook-inspired panels, whimsical onboarding, house-banner style identity, and a cozy mystical opening mood while keeping the gameplay clear and readable." \
  --model gpt-5.4 \
  --agent-timeout 3600 \
  --max-concurrency 2 \
  --poll-seconds 5 \
  --stale-heartbeat-seconds 900
```

### 6. Single-game execution

```zsh
python3 /Volumes/Elements/game_remix_editor/scripts/run_single_game.py \
  --run-dir /Volumes/Elements/game_remix_editor/runs/<run_id> \
  --game-id <game_id> \
  --style neutral_prototype \
  --remix-prompt "flappy bird like" \
  --model gpt-5.4 \
  --agent-timeout 3600
```

### 7. Creative refactor replay CLI

The formal replay CLI supports two modes:

- `replay`
  - low-level mode for replaying a prepared attempt by explicit attempt directory
- `pipeline`
  - higher-level mode that resolves the attempt from `--run-dir` and `--game-id`

Replay a prepared attempt directly:

```zsh
python3 /Volumes/Elements/game_remix_editor/scripts/creative_refactor_cli.py replay \
  --attempt-dir /Volumes/Elements/game_remix_editor/runs/<run_id>/games/<game_id>/attempts/attempt_0001 \
  --timeout 900 \
  --verbose \
  --json-output \
  --reasoning-effort high
```

Resolve the latest attempt from the pipeline layout:

```zsh
python3 /Volumes/Elements/game_remix_editor/scripts/creative_refactor_cli.py pipeline \
  --run-dir /Volumes/Elements/game_remix_editor/runs/<run_id> \
  --game-id <game_id> \
  --timeout 900 \
  --verbose \
  --json-output \
  --reasoning-effort high
```

Replay artifacts are written back into the resolved attempt directory:

- `direct_worker_invocation.json`
- `direct_worker_stdout.txt`
- `direct_worker_stderr.txt`
- `direct_worker_result.json`

The legacy debug entrypoint still exists as a thin compatibility wrapper:

```zsh
python3 /Volumes/Elements/game_remix_editor/scripts/debug_creative_refactor.py replay \
  --attempt-dir /Volumes/Elements/game_remix_editor/runs/<run_id>/games/<game_id>/attempts/attempt_0001 \
  --timeout 900 \
  --verbose \
  --json-output \
  --reasoning-effort high
```

### 8. Prompt from file

All runtime entrypoints also support:

- `--remix-prompt-file /path/to/prompt.txt`

Use either:
- `--remix-prompt`
or
- `--remix-prompt-file`

but not both.

## Run layout

```text
game_remixer/
  scripts/
  prompts/
  specs/
  styles/
    neutral_prototype/
    cyberpunk/
  runs/
    <run_id>/
      input_manifest.json
      run_state.json
      spec_adaptor/
        remix_prompt.txt
        selected_style.json
        adaptation_report.json
        adapted/
          creative_remix_contract.md
          creative_refactor_agent_template.md
          visual_identity_contract.md
          theme_policy.md
      input/
        <game_id>/
      output/
        <game_id>/
      games/
        <game_id>/
          game_state.json
          attempts/
            attempt_0001/
              refs/
                creative_refactor_agent_template.md
                creative_remix_contract.md
                visual_identity_contract.md
                theme_policy.md
                audio_policy.md
                network_policy.md
                system_contract.md
                refactor_compliance_spec.md
              job_state.json
              creative_refactor_result.json
      dashboard/
        index.html
        dashboard_data.json
      serve_dashboard.sh
```

## Dashboard behavior

The generated dashboard now surfaces:

- run status
- run phase
- total / running / completed / failed counts
- active jobs
- heartbeat freshness
- heartbeat age
- stale/failure reason visibility
- run notes
- per-game output/input links

## Runtime expectations

The extracted runtime currently assumes:

- manifests point to valid source game paths
- mirrored inputs contain a usable `index.html`
- the remix contract and prompt template exist
- the `cline` CLI is available for creative transform execution

## Current limitations / next planned evolution

The current prompt-aware runtime is **visual-first**.

Implemented:
- preset selection
- prompt-aware adapted runtime bundle
- run-local prompt/spec adaptation
- packet generation from adapted refs

Not yet implemented:
- structured prompt decomposition schema
- explicit intent routing into:
  - `visual_only`
  - `gameplay_only`
  - `combined`
- separate gameplay transformation lane
- combined gameplay-first, visual-second flow

The current visual lane can already be treated as the baseline for future intent routing and gameplay expansion.

## Creative remix rules source

Original creative remix contract reference:

- `/Volumes/Elements/full_7k_qa_whitelabl_agent/specs/creative_remix_contract.md`

That contract carries the main creative/compliance requirements, including:
- preserve mechanics and controls
- remove or mute audio
- use compliant fonts only
- remove or replace nonessential decorative images / videos / GIFs where practical
- preserve readability and control-safe zones
- make the remix materially different in multiple dimensions

## Validated sample run

A known successful bounded parallel validation run was:

- `/Volumes/Elements/game_remix_editor/runs/run_game_remixer_20260425T224512Z`

Observed final state:
- `status = transform_completed`
- `current_phase = parallel_batch_finished`
- `games_transform_completed = 3`
- `games_transform_failed = 0`

A known successful prompt-aware validation run was:

- `/Volumes/Elements/game_remix_editor/runs/run_game_remixer_20260426T161844Z`

Observed runtime traits:
- `selected_style_id = neutral_prototype`
- remix prompt present
- `spec_adaptor/` created
- adapted refs active in task packets

## Design principles

- generic engine, not a single-run replica
- prototype-preserving extraction
- relative run paths under the remixer root
- timestamped runs by default unless overridden
- parity-gated progression
- dashboard-first observability
- central scheduler ownership for aggregate parallel run state
- preset-driven baseline behavior
- prompt-aware run-local adaptation
- global mobile readability and compact HUD safety invariants

## Prototype reference

The oracle implementation lives externally at:

- `/Volumes/Elements/full_7k_qa_whitelabl_agent/scripts/run_creative_only_lane.py`
- `/Volumes/Elements/full_7k_qa_whitelabl_agent/scripts/run_sequential_lane.py`
- `/Volumes/Elements/full_7k_qa_whitelabl_agent/scripts/orchestrator.py`
- `/Volumes/Elements/full_7k_qa_whitelabl_agent/scripts/generate_task_packet.py`

## Remaining optional follow-up

Possible future work, but not required for the extraction milestone:

- structured prompt decomposition
- gameplay-only and combined transformation lanes
- richer adaptor metadata persistence
- additional dashboard polish
- larger-scale validation beyond the tiny sample manifest
- packaging / commit hygiene in a clean Elements-side repo context