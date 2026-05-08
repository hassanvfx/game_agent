# Game Refactoring

`game_refactoring` is a reusable operator-pipeline repository for transforming source games through a staged orchestration flow.

This repository is a documentation and architecture reset of the previously cloned `game_remix_editor` runtime. The current goal is to preserve the working pipeline, orchestrator, operators, and supporting contracts while making the project easier to understand, audit, and repurpose for different transformation steps.

## Current objective

This repo is being cleaned up in a documentation-first pass.

What that means:

- keep working code behavior unchanged
- treat the existing code as the source of truth
- remove stale `game_remix_editor` / `game_remixer` branding from current-facing documentation where safe
- classify core vs experimental vs generated vs historical material
- prepare the repository for a later repurposing pass where operator steps may change

This pass does **not** attempt to rename runtime identifiers, run IDs, or generated artifacts.

## Core architecture

At a high level, the repository centers on a staged transformation pipeline:

1. prepare a run and inputs
2. adapt shared style/spec context at the run level
3. execute per-game operator stages
4. collect outputs, status, and dashboards
5. inspect and debug runs through structured artifacts

The intended architectural center is the operator pipeline and its orchestration layer, not the legacy “Game Remixer” project identity.

## Core entrypoints

The most important repo-owned execution surfaces are:

### Main CLI and runtime
- `scripts/creative_refactor_cli.py`
- `scripts/game_workflow.py`
- `scripts/creative_refactor_runtime.py`

### Run and input preparation
- `scripts/create_run.py`
- `scripts/prepare_inputs.py`
- `scripts/generate_task_packet.py`

### Execution and orchestration
- `scripts/run_single_game.py`
- `scripts/run_parallel_batch.py`
- `scripts/run_operator_pipeline_batch.py`
- `scripts/run_operator_pipeline_game.py`
- `scripts/operator_registry_v2.py`

### Shared adaptation layer
- `scripts/spec_adaptor.py`

### Dashboard and operational helpers
- `scripts/build_dashboard.py`
- `scripts/serve_dashboard.py`
- `scripts/write_dashboard_launcher.py`
- `scripts/open_latest_dashboard.sh`
- `scripts/process_kill_utils.py`

## Configuration and contract inputs

The pipeline behavior is shaped by a combination of configs, prompts, specs, and style bundles.

### Configs
- `configs/operator_pipeline_v2.json`

### Shared prompts and policies
- `prompts/audio_policy.md`
- `prompts/creative_recovery_policy.md`
- `prompts/network_policy.md`
- `prompts/refactor_compliance_spec.md`
- `prompts/system_contract.md`
- `prompts/theme_policy.md`
- `prompts/visual_identity_contract.md`
- `prompts/operators_v2/`

### Specs
- `specs/creative_remix_contract.md`

### Styles
- `styles/neutral_prototype/`
- `styles/cyberpunk/`
- `styles/meme_arcade_game/`
- `styles/rigid_prototype/`

## Documentation authority

The repository currently contains historical and partially conflicting documentation. Until a later cleanup pass completes, read the docs in this order:

1. `README.md`  
   Canonical top-level project framing and current cleanup intent.

2. `docs/operator_pipeline_manual.md`  
   Detailed operator-pipeline behavior, responsibilities, and constraints.

3. `docs/game_workflow_cli.md`  
   Reference for the standalone workflow launcher and named workflow entrypoint.

4. `docs/media_mapper_prompt_packet_spec.md` and `docs/kill-all-operation.md`  
   Focused operational/reference documents.

5. `docs/journals/`  
   Historical implementation memory and decision logs. Useful for provenance, but not the canonical current architecture.

## Repository taxonomy

### Canonical core
These directories define the main reusable system:

- `scripts/`
- `configs/`
- `prompts/`
- `specs/`
- `styles/`

### Operational and reference docs
These describe how the system is intended to be used and understood:

- `README.md`
- `docs/operator_pipeline_manual.md`
- `docs/game_workflow_cli.md`
- `docs/media_mapper_prompt_packet_spec.md`
- `docs/kill-all-operation.md`

### Active support inputs
These may feed operator stages or runtime decisions and should not be removed blindly:

- `catalogs/`
- `assets/audio_library/`
- selected files in `fixtures/`

### Likely experimental or lab material
These areas appear to support exploration, dry runs, debugging, or one-off pipeline experiments:

- `fixtures/operator_pipeline_lab/`
- `fixtures/spec_adaptor_debug/`
- `fixtures/spec_adaptor_test_lab/`
- `fixtures/style_resolution_test_run/`
- `scripts/operator_pipeline_lab.py`
- portions of `catalogs/sprites/v2_prompt_optimize/`
- portions of `catalogs/sprites/runs/`

### Generated and historical artifacts
These are useful for inspection and provenance, but they are not the clean architectural center of the repo:

- `runs/`
- `docs/journals/`
- generated dashboards, logs, and state snapshots
- historical fixture outputs and optimization byproducts

## Naming policy for this cleanup phase

Not every legacy name should be changed in the same way.

### Safe to update in documentation
- human-facing project identity text
- stale top-level repo descriptions
- operator-facing docs where the meaning is unchanged

### Defer for now
- runtime identifiers such as `run_game_remixer_*`
- temp file names and helper-script internals
- generated artifact snapshots
- tests or fixtures that intentionally preserve old historical names
- code symbols whose rename could affect compatibility

## Working assumptions

The current codebase is assumed to be working and is the source of truth.

During this cleanup phase:

- do not change runtime behavior just to improve naming
- do not hand-edit generated run outputs
- do not delete lab or support directories until dependency boundaries are documented
- do not treat journals as the canonical architecture source

## Next cleanup targets

The next documentation passes should focus on:

- aligning `docs/operator_pipeline_manual.md` with the intended core architecture
- classifying quarantine candidates more explicitly
- separating current operational docs from historical journals
- re-auditing remaining repo-owned naming references after documentation cleanup
- planning a later compatibility-reviewed code symbol rename pass if still desired