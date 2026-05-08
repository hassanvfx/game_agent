# Dry-Run Mode Plan

This document defines a code-grounded plan for validating the orchestrator and stage pipeline without invoking the external `cline` worker.

It is a design and validation document, not yet an implementation claim.

## Purpose

The current repository mixes several concerns:

- run-level orchestration
- optional spec adaptation
- per-game stage sequencing
- bounded concurrency
- worker invocation
- prompt quality and stage guidance

A dry-run mode is needed so that orchestration can be validated independently from worker intelligence and prompt quality.

## Primary goal

Validate the **pipeline shell** without depending on actual agent execution.

That means validating:

- run creation and reuse
- input preparation
- optional spec-adaptor decision path
- run/game state transitions
- bounded concurrency scheduling
- per-game stage order
- attempt artifact layout
- workspace promotion flow
- final output copying
- dashboard and launcher integration

## Non-goals

Dry-run mode should not claim to validate:

- worker intelligence
- prompt quality
- creative quality
- media mapping accuracy
- final transformed gameplay correctness
- spec-adaptor content quality

## Code-grounded baseline

Based on current inspected code:

### Run-level facts
- `creative_refactor_cli.py start-batch` creates the run and launches a batch runner
- `run_operator_pipeline_batch.py`:
  - calls `prepare_inputs.py`
  - conditionally calls `spec_adaptor.py` when remix prompt exists
  - initializes run state
  - schedules one worker process per game up to concurrency limit
  - watches heartbeat freshness
  - finalizes run status

### Game-level facts
- `run_operator_pipeline_game.py`:
  - copies input mirror to `operator_pipeline/current`
  - resolves ordered operators from the registry
  - creates per-attempt workspaces and artifacts
  - invokes `cline`
  - writes result/state artifacts
  - promotes successful workspace into `current`
  - copies final `current` workspace into output on success

### Important boundary
The spec adaptor is currently separate from the operator chain and should remain separately controllable in dry-run design.

## Recommended dry-run architecture

Dry-run should be split into **two independent simulation surfaces**.

### 1. Operator dry-run
Simulates per-game stage execution without invoking `cline`.

### 2. Spec-adaptor dry-run
Simulates run-level spec adaptation behavior without invoking `cline`.

This separation follows current architecture and avoids collapsing run-scope and game-scope concerns.

## Proposed flags

These are proposed interface ideas, not yet implementation decisions.

### CLI-level
Propagate from `creative_refactor_cli.py start-batch`:

- `--dry-run-operators`
- `--dry-run-spec-adaptor`

### Batch-runner level
`run_operator_pipeline_batch.py` should accept and forward:

- `--dry-run-operators`
- `--dry-run-spec-adaptor`

### Game-runner level
`run_operator_pipeline_game.py` should accept:

- `--dry-run-operators`

### Optional future extension
Later, if needed:

- `--dry-run-fail-stage <stage_id>`
- `--dry-run-timeout-stage <stage_id>`
- `--dry-run-stale-heartbeat`

These should not be part of the first implementation slice.

## Recommended first implementation slice

The safest first slice is:

### Stage 1 — operator dry-run only
Implement:
- `--dry-run-operators`

Behavior:
- do everything the game runner does up to stage execution
- do not invoke `cline`
- synthesize a deterministic successful result for each operator stage
- still write:
  - `operator_prompt.txt`
  - `operator_invocation.json`
  - `operator_stage_state.json`
  - `operator_result.json`
  - `media_policy_report.json`
  - placeholder stdout/stderr files
- still promote stage workspace into `pipeline/current`
- still copy final `pipeline/current` to output
- still update game state as completed

Why this first:
- it validates most of the orchestration shell
- it avoids touching spec-adaptor behavior first
- it gives fast end-to-end validation of the per-game pipeline

## Proposed synthesized stage behavior

When `--dry-run-operators` is active:

### Keep real
- registry loading
- stage ordering
- attempt workspace creation
- catalog copying
- media policy report generation
- prompt packet generation
- stage-state path creation
- promotion behavior
- final output copy
- game/run status updates

### Replace
- actual `cline` invocation
- parsing of real worker stdout

### Synthesize
- a deterministic result payload such as:
  - `status: completed`
  - `execution_status: completed`
  - `returncode: 0`
  - `timed_out: false`
  - `summary: "Dry-run operator simulation completed."`
  - `changed_files: []`
  - checks marked to a dry-run-safe default
- stdout/stderr files containing explicit dry-run markers

### Stage-state rule
`operator_stage_state.json` should still move through expected transitions:
- `prompt_built`
- `running`
- `completed`

This preserves orchestration realism.

## Spec-adaptor dry-run options

There are three plausible designs.

### Option A — skip entirely
If `--dry-run-spec-adaptor` is active:
- do not invoke `spec_adaptor.py`
- mark in run state that spec adaptor was intentionally bypassed

Pros:
- smallest implementation
- simplest behavior

Cons:
- does not validate adaptor artifact consumers
- less realistic when remix prompt exists

### Option B — synthesize pass-through adapted bundle
If `--dry-run-spec-adaptor` is active:
- create `run_dir/spec_adaptor/`
- copy editable style-local files and invariant files
- do not invoke `cline`
- write synthetic:
  - `spec_adaptor_job_state.json`
  - `adaptation_report.json`
  - `recomposition_summary.json`
- mark result as simulated pass-through or simulated ready

Pros:
- validates downstream consumers of adapted bundle path
- aligns better with intended “adapt or pass through” architecture

Cons:
- larger implementation surface

### Option C — simulate full adaptor result without file copying
Not recommended for first pass.

Reason:
- less faithful to the current artifact model
- higher risk of false confidence

## Recommendation for spec-adaptor dry-run
Use a staged rollout:

### First
Implement operator dry-run only.

### Second
Implement spec-adaptor dry-run as **Option B**:
- simulated pass-through adapted bundle
- explicit “simulated” markers in artifacts

That is the most useful long-term behavior.

## Artifact requirements for dry-run

Dry-run should still create artifacts that look structurally real.

### Run-level
- `run_state.json`
- dashboard output
- launcher invocation/output files
- optional `spec_adaptor/` subtree when simulated

### Game-level
- `game_state.json`
- `operator_pipeline/current/`
- `operator_pipeline/stage_XX.../attempt_YY/`
- prompt/invocation/result/state/stdout/stderr/media-policy files
- final copied game output

### Explicit marker requirement
Every dry-run-generated artifact that could be mistaken for real worker output should include a clear marker such as:
- `"simulated": true`
- `"mode": "dry_run"`
- stdout text beginning with `DRY RUN: ...`

This avoids future confusion.

## Validation criteria for dry-run success

A successful dry-run implementation should allow us to confirm:

### Run-level
- run reaches expected final state
- counters update correctly
- dashboard generation still works
- concurrency scheduling still works

### Game-level
- stage sequence is executed in configured order
- workspaces are created and promoted correctly
- stage artifacts are written consistently
- final output copy occurs
- game state reaches completed

### Boundary-level
- operator dry-run does not collapse spec-adaptor boundary
- spec-adaptor dry-run, when added, produces artifacts compatible with downstream expectations

## Risks to watch

### Risk 1 — false realism
Dry-run may hide actual worker integration issues.

Mitigation:
- clearly label dry-run artifacts
- treat dry-run as orchestration validation only

### Risk 2 — diverging code paths
If dry-run uses too much separate logic, it may stop validating the real path.

Mitigation:
- reuse as much real orchestration code as possible
- only replace the minimal worker-invocation segment

### Risk 3 — spec-adaptor confusion
If dry-run mixes spec-adaptor simulation with operator simulation, boundaries may become muddy.

Mitigation:
- keep separate flags and separate responsibilities

## Recommended implementation order

### Step 1
Write this plan and keep refining it with code evidence.

### Step 2
Read more supporting files:
- `scripts/media_policy.py`
- `scripts/prepare_inputs.py`
- legacy flow scripts
- operator prompts

### Step 3
Implement `--dry-run-operators` only.

### Step 4
Validate end-to-end run artifact behavior.

### Step 5
Implement `--dry-run-spec-adaptor` as pass-through bundle simulation.

### Step 6
Validate that downstream operator prompt assembly still works with simulated adapted bundle.

## Open questions

### 1. Should dry-run stages always complete successfully in the first implementation?
**Current recommendation:** yes

### 2. Should media policy scanning remain real in dry-run?
**Current recommendation:** yes, because it validates artifact generation and current specialization boundaries

### 3. Should dry-run write fake stdout in the same stdout-contract format?
**Current recommendation:** yes, if the current result parser depends on it; otherwise write the result JSON directly and keep stdout clearly marked as simulated

### 4. Should spec-adaptor dry-run be required for operator dry-run?
**Current recommendation:** no

## Working summary

The safest path is:

1. validate orchestrator shell first
2. keep spec adaptor and operator chain separate
3. add operator dry-run before spec-adaptor dry-run
4. reuse real orchestration logic and replace only the actual worker invocation layer
5. treat dry-run as orchestration validation, not transformation validation