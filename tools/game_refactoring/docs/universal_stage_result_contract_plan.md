# Universal Stage Result Contract Plan

This document captures the grounded planning state for moving the operator pipeline toward a universal stage-result contract.

It is intentionally written as a working planning artifact, not as a finalized architecture promise. Its purpose is to preserve current observations, identify the files likely to change, record side-effect and regression concerns, and define a safe execution sequence for future implementation.

## Objective

Replace stage-specific Python-side success interpretation with a generic pipeline contract where:

1. each stage performs its own internal evaluation
2. each stage emits a machine-readable result artifact
3. the executor reads the result artifact generically
4. downstream stages declare which upstream result states they accept
5. chaining policy is config-driven rather than hardcoded in `run_operator_pipeline_game.py`

## Target abstraction

### Stage output contract

Each operator stage should produce a JSON result file with, at minimum:

```json
{
  "status": "ok",
  "detail": "Short explanation of what was achieved."
}
```

### Allowed universal statuses

- `ok`
- `warning`
- `error`

### Stage input policy

Each stage definition should eventually declare which upstream statuses are acceptable to continue.

Example:

```json
{
  "accepted_upstream_statuses": ["ok", "warning"]
}
```

This would allow the pipeline to answer, generically:

- can the next stage run?
- should the run stop?
- should the run continue with warning state propagation?

## What problem this solves

The current pipeline is not yet fully generic because some success/failure decisions still live in Python control flow.

Current examples:
- `media_mapper` has embedded post-run interpretation
- the executor still interprets special outcomes instead of only consuming a universal stage result contract
- stage chaining does not yet appear to be driven by declared acceptance policy

The universal contract would shift responsibility:
- from Python-side special-case judgment
- to stage-emitted structured result + config-declared policy

## Current observed state

### Already true

- The orchestration shell exists and has been dry-run validated.
- The spec adaptor is correctly separated from the per-game operator pipeline.
- The operator pipeline already creates stage workspaces, prompts, artifacts, and stage result files.
- The executor already records structured per-stage metadata in JSON.

### Not yet true

- There is not yet a universal operator-produced JSON result contract used as the primary source of stage outcome.
- Stage success is not yet fully contract-driven.
- Next-stage acceptance policy is not yet defined as a first-class config contract.
- A simple “toy” input path has not yet been added to exercise the real pipeline on minimal content.

## Clarified scope for the next abstraction pass

The user clarified an important boundary:

- only the **input** should be simplified
- the **real pipeline must still run**

That means the next abstraction pass should not invent a fake mini-runner.
It should use:
- real run creation
- real input mirroring
- real operator stage execution path
- real run/game/stage artifacts
- real pipeline chaining

Only these should be simplified:
- the source fixture
- the operator task
- the operator result contract

## Proposed proving case

Use a tiny input fixture that is pipeline-compatible enough to run through the existing system.

### Candidate fixture

A minimal Hello World input:

- file: `index.html`
- initial visible text: `Hello World`

### Candidate operator task

Use one simple stage instruction:
- translate visible text to Spanish
- preserve the rest of the file structure
- emit result JSON with:
  - `status`
  - `detail`

### Why this proving case matters

This removes most current noise:
- no media cleanup complexity
- no catalog mapping complexity
- no multi-signal outcome heuristics
- no complex game source structure requirements beyond the minimum needed to run

It gives the team a minimal but real test of:
- operator-edited workspace
- operator self-evaluation
- executor-consumed result contract
- stage chaining policy

## Files likely to be touched

This section records currently expected touch points so the implementation can be revisited without rediscovery.

### 1. `scripts/run_operator_pipeline_game.py`

Why it matters:
- This is the per-game executor hotspot.
- It currently builds prompts, invokes worker execution, interprets outcomes, writes stage results, and handles stage progression.

Likely changes:
- add support for reading an operator-produced result JSON file
- normalize universal statuses (`ok`, `warning`, `error`) into executor behavior
- separate executor transport concerns from stage judgment concerns
- gate next-stage progression based on declared accepted upstream statuses
- reduce or replace stage-specific embedded success logic over time

Side-effect concerns:
- changing stage-result interpretation can alter retry semantics
- changing progression logic can break existing pipelines that assume current `completed/failed/timeout` handling
- existing artifacts and dashboards may expect current result fields

### 2. `scripts/operator_registry_v2.py`

Why it matters:
- This appears to define operator metadata and stage resolution behavior.

Likely changes:
- add stage-level acceptance policy fields
- possibly add result-contract metadata or expected artifact paths
- potentially expose new configuration values into resolved operator definitions

Side-effect concerns:
- changing operator definitions may require compatibility defaults for existing stages
- any strict schema change could break current config loading

### 3. `configs/operator_pipeline_v2.json`

Why it matters:
- This is the current stage-chain configuration entrypoint.

Likely changes:
- add declared accepted upstream statuses
- possibly define result artifact expectations per stage
- possibly allow stage-specific contract metadata without Python conditionals

Side-effect concerns:
- config changes must preserve default behavior for existing stages
- malformed or partially migrated config could block all runs

### 4. `scripts/creative_refactor_cli.py`

Why it matters:
- This is the user-facing entrypoint for starting runs.

Likely changes:
- possibly expose a controlled path for running the minimal proving fixture
- possibly add flags or convenience entrypoints only if needed

Side-effect concerns:
- avoid polluting the main CLI with one-off fixture behavior unless it becomes a reusable workflow
- fixture support should remain optional

### 5. `scripts/run_operator_pipeline_batch.py`

Why it matters:
- This orchestrates per-run batch execution and transitions between run setup and per-game execution.

Likely changes:
- likely minimal at first
- may need compatibility handling if universal stage statuses affect aggregate run reporting

Side-effect concerns:
- batch completion logic may currently assume binary success/failure at the per-game layer
- status aggregation may need extension if warning propagation becomes first-class

### 6. `prompts/operators_v2/...`

Why it matters:
- the selected proving stage will need an intentionally simplified operator instruction

Likely changes:
- create or adapt one minimal prompt for the proving case
- instruct operator to write a JSON result file with universal status values and detail text

Side-effect concerns:
- avoid accidentally degrading production prompts while building the proving case
- a dedicated prompt or dedicated stage variant may be safer than mutating a core production prompt first

### 7. `fixtures/...` and/or a new `samples/...` input area

Why it matters:
- the user wants the real pipeline to run, but against a tiny input fixture

Likely changes:
- add a minimal pipeline-compatible fixture
- add a manifest entry pointing to that fixture

Side-effect concerns:
- the input must satisfy whatever `prepare_inputs.py` and integrity checks require
- the proving fixture should be clearly separated from production-snapshot fixtures

### 8. `scripts/prepare_inputs.py`

Why it matters:
- the proving fixture must survive the normal mirroring/integrity path

Likely changes:
- ideally none
- may require observation if the minimal fixture fails current assumptions

Side-effect concerns:
- changing input preparation rules just to fit the toy fixture could accidentally weaken production assumptions
- if the toy fixture does not fit, better to shape the fixture to the pipeline than to relax the pipeline immediately

### 9. `docs/journals/repo-identity-and-operator-pipeline-reframe.md`

Why it matters:
- this is the active task history and must remain the canonical task log

Likely changes:
- append planning decisions
- append implementation outcomes once work begins

### 10. `docs/master_index.md`

Why it matters:
- this is the fastest-entry summary for future sessions

Likely changes:
- add this plan as the current next-step planning artifact once the direction is confirmed

## Open design questions

These are not blockers for planning, but they must be answered deliberately during implementation.

### 1. Should universal stage status replace or coexist with current executor status?

Current executor statuses include values like:
- `completed`
- `failed`
- `timeout`

Universal operator result statuses are proposed as:
- `ok`
- `warning`
- `error`

Most likely safe approach:
- keep executor transport/execution status separate
- add universal stage evaluation status alongside it

Example shape:

```json
{
  "execution_status": "completed",
  "stage_result": {
    "status": "warning",
    "detail": "Primary task completed but one issue remains."
  }
}
```

This preserves timeout/process semantics while still allowing universal evaluation.

### 2. Who decides retries?

Possible models:
- retries remain executor-driven based on allowed universal statuses
- retries become config-driven per stage
- retries depend on whether `error` is retryable versus terminal

This should be decided explicitly before generalizing beyond the proving case.

### 3. How should warning propagate?

Possible policies:
- warning still allows next stage if accepted
- warning upgrades run summary state without blocking progression
- warning only blocks if next stage explicitly requires `ok`

### 4. Where should result JSON live?

Likely safe option:
- a fixed file path inside each attempt workspace or attempt root

Example candidates:
- `operator_result_contract.json`
- `operator_stage_evaluation.json`

This should be stable and stage-agnostic.

## Side-effect and regression concerns

### 1. Dashboard/reporting assumptions

Existing dashboards or result readers may assume current fields only.
Adding new fields is safer than replacing old ones immediately.

### 2. Backward compatibility

Existing production stages should not all be forced to emit the new contract at once.
A bridge period is safer:
- if contract JSON exists, read it
- otherwise fall back to current behavior

### 3. False generality risk

It is easy to design an elegant contract on paper that only fits the toy case.
The proving case should therefore be intentionally tiny, but implemented through the real pipeline path.

### 4. Fixture-shaping risk

If the minimal fixture is too unlike production inputs, implementation may drift into fixture-only logic.
The fixture should be minimal, but still valid for the normal pipeline path.

### 5. Spec-adaptor coupling risk

This next pass should not entangle universal stage-result logic with spec-adaptor behavior.
The spec adaptor should remain a separate boundary.

## Recommended safe execution order

### Phase A — planning artifacts
1. record this design direction in docs
2. update the active journal
3. link the plan from the master index

### Phase B — proving fixture
1. create a tiny pipeline-compatible Hello World input fixture
2. add a manifest that targets that fixture
3. confirm the fixture can pass the normal run setup path

### Phase C — universal result contract bridge
1. define the minimal JSON contract: `status`, `detail`
2. add executor support for reading it if present
3. preserve fallback behavior if absent

### Phase D — policy-driven chaining
1. define accepted upstream statuses for the next stage
2. add config support for that policy
3. gate stage progression on the policy

### Phase E — generalization
1. validate the toy case end to end
2. only then migrate production stages incrementally
3. only then remove embedded special-case logic

## Current recommendation

The next implementation should not start by rewriting the whole pipeline.

It should start by building a bridge:

- real pipeline
- tiny fixture input
- one simple operator task
- one operator-emitted JSON result
- one executor reader path
- one policy-driven chaining rule

That will convert the current idea into an observable, testable abstraction without overcommitting the production pipeline too early.

## Resume checklist

When returning to this work, use this checklist:

- confirm `scripts/run_operator_pipeline_game.py` current state
- confirm `scripts/operator_registry_v2.py` current capabilities
- inspect `configs/operator_pipeline_v2.json` for best insertion point for policy fields
- design the minimal Hello World fixture so it survives current input preparation
- decide fixed filename/location for stage result JSON
- implement contract reader with backward-compatible fallback
- validate on the real pipeline, not a separate harness