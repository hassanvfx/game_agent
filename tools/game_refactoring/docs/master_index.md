# Master Index

This file is the current master index for the `game_refactoring` repo cleanup, evidence, architecture, and next-step execution work.

It is intended to act as the fastest starting point for future sessions and should be updated as the repository understanding improves.

## Current repo status

The repository is in an evidence-first transition state.

Current priorities are:

1. preserve working behavior
2. keep the run-level spec adaptor boundary intact
3. validate the orchestration shell independently from `cline`
4. reduce specialization only after code-grounded evidence supports it

## Read this first

### Current orientation
- `README.md`
- `docs/operator_pipeline_manual.md`

### Working process
- `docs/evidence_first_refactor_process.md`

### Current execution target
- `docs/dry_run_mode_plan.md`

## Core architecture and classification docs

### Repository scope and structure
- `docs/repository_taxonomy.md`
- `docs/quarantine_manifest.md`
- `docs/runtime_naming_audit.md`

### Evidence and architecture truth
- `docs/code_facts_runtime_flow.md`
- `docs/code_facts_spec_adaptor.md`
- `docs/code_facts_media_policy.md`
- `docs/static_vs_dynamic_pipeline_map.md`
- `docs/intent_vs_code_deltas.md`

### Planned structural migrations
- `docs/invariant_contract_merge_plan.md`
- `docs/universal_stage_result_contract_plan.md`

## Active journal

Use this as the primary task-history record for the current cleanup/reframing effort:

- `docs/journals/repo-identity-and-operator-pipeline-reframe.md`

## Current major conclusions

### Confirmed
- spec adaptor is separate from the operator pipeline
- spec adaptor is run-scoped
- operator execution is per-game
- concurrency is across games
- operator order is already partially config-driven
- orchestrator shell is more reusable than the v2 per-game executor

### Confirmed problem areas
- `run_operator_pipeline_game.py` is still too specialized
- `build_operator_prompt_text(...)` is a major static/dynamic mixed zone
- `media_mapper` has Python-side post-run enforcement
- prompt simplification alone will not make the system generic
- optional spec adaptor currently behaves as skip-or-run, not pass-through bundle generation

## Current fastest path to completion

The current milestone is:

### Design the bridge from specialized executor logic to a universal stage-result contract
Target:
- `docs/universal_stage_result_contract_plan.md`

Intent:
- keep the real pipeline
- simplify only the proving input and operator task
- move toward stage-emitted JSON evaluation
- make downstream acceptance policy explicit and config-driven

This should happen before:
- broad production-stage migration
- removal of all embedded stage-specific executor logic
- invariant merge implementation
- runtime naming migration

## Suggested next execution order

1. update the active journal with the universal stage-result contract plan
2. create the tiny proving fixture input for the real pipeline
3. add a minimal operator-emitted JSON result contract bridge
4. validate the real pipeline on the proving fixture
5. only then generalize accepted-status chaining and remove more embedded specialization

## Current blind spot warnings

- over-planning without cashing out into executable validation
- simplifying prompts while leaving Python specialization intact
- merging invariant files without compatibility bridge
- assuming docs are truth instead of mutable observations

## When resuming later

If resuming this project later, the minimum recommended read order is:

1. `docs/master_index.md`
2. `docs/evidence_first_refactor_process.md`
3. `docs/dry_run_mode_plan.md`
4. `docs/intent_vs_code_deltas.md`
5. `docs/code_facts_runtime_flow.md`
6. `docs/code_facts_spec_adaptor.md`
7. `docs/code_facts_media_policy.md`
8. active journal entry

## Scope boundary reminder

Do not casually change:
- spec adaptor behavior
- runtime naming identifiers
- legacy fixture provenance
- invariant-file layout
- executor semantics

until the dry-run shell milestone is complete and validated.