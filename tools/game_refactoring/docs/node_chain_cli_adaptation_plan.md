# Node-Chain CLI Adaptation Plan

## Goal

Finish the transition from the old spec-adaptor / operator-pipeline vocabulary to the newer prompt + workspace + ordered-nodes model, while preserving a safe compatibility path.

This document is the full adaptation plan for the remaining CLI, orchestration, naming, and runtime cleanup work.

---

## 1. Current State

The repository is in a mixed transitional state.

### Architecture that is already moving in the right direction
- per-game execution is already becoming generic
- manifests can now define:
  - `workspace`
  - `prompt`
  - `nodes`
- node chaining already uses:
  - accepted upstream statuses
  - contract presence / validity
  - per-node artifacts
- detached async launch already exists through:
  - `scripts/creative_refactor_cli.py start-batch`
  - `status`
  - `result`
  - `finish`

### Leftover old architecture still present
- batch orchestration still invokes `spec_adaptor.py`
- runtime naming still reflects older concepts:
  - `creative_refactor_cli`
  - `operator_pipeline`
  - `operator`
  - `remix_prompt`
  - run phases that still imply transform/spec-adaptation lineage

So the remaining work is mostly:
1. remove the leftover architecture mismatch
2. rename the surface area to match the actual system
3. revalidate the detached async node-chain flow end to end

---

## 2. Target Model

The intended system should be conceptualized as:

- one run launcher
- one run prompt payload
- one or more workspaces/games
- one ordered node chain per workspace
- one contract emitted per node
- async detached run launch
- pollable status and final result

### Core inputs
- `workspace`
- `prompt`
- `nodes`

### Core runtime behavior
- prepare inputs
- run node 1
- validate contract
- decide if node 2 may run
- continue until chain completion or failure
- expose background run status/result through the CLI

### Core outputs
- run artifacts
- per-node artifacts
- final transformed workspaces
- contract trail

---

## 3. Naming Adaptation Direction

The current filenames and field names still overstate older concepts.

## Recommended conceptual replacements

### Scripts
- `scripts/creative_refactor_cli.py`
  - future preferred identity:
    - `scripts/node_chain_cli.py`
    - or `scripts/game_pipeline_cli.py`

- `scripts/run_operator_pipeline_batch.py`
  - future preferred identity:
    - `scripts/run_node_chain_batch.py`
    - or `scripts/run_game_pipeline_batch.py`

- `scripts/run_operator_pipeline_game.py`
  - future preferred identity:
    - `scripts/run_node_chain_game.py`
    - or `scripts/run_game_pipeline_unit.py`

### Runtime vocabulary
- `operator` → `node`
- `remix_prompt` → `prompt` or `run_prompt`
- `operator_pipeline` → `node_chain`
- `operator_pipeline_completed_stages` → `completed_nodes`
- `operator_result_contract.json` can remain for compatibility initially, but later may become `node_result_contract.json`

### Legacy concept to remove from the active path
- `spec_adaptor`

---

## 4. Compatibility Strategy

Do not do a destructive rename-first migration.

### Safer rollout
1. keep current files working
2. remove spec-adaptor dependency from the active batch path
3. add preferred terminology in docs and runtime fields
4. optionally add better-named wrapper scripts
5. later deprecate older names once validation is complete

This avoids breaking existing entrypoints while the architecture is still being proven.

---

## 5. File Delta Map

## A. Must change now

### `scripts/run_operator_pipeline_batch.py`
Purpose of change:
- remove the leftover `spec_adaptor.py` invocation
- make prompt/manifest input the direct upstream source
- keep it as the long-running detached batch scheduler

Expected changes:
- remove spec-adaptor call path
- remove batch phases that assume spec adaptation is mandatory
- update run-state transitions to reflect node-chain flow directly

### `scripts/creative_refactor_cli.py`
Purpose of change:
- keep detached launcher behavior
- update naming/documentation surface
- ensure start/status/finish reflect the new system language over time

Expected changes:
- no major architecture rewrite needed
- possibly update emitted payload field names gradually
- possibly add future wrapper/alias commands

### `scripts/run_operator_pipeline_game.py`
Purpose of change:
- continue migration from legacy operator terminology toward generic node terminology
- keep compatibility where needed

Expected changes:
- likely smaller naming/metadata updates after batch cleanup
- no deep async rewrite needed

## B. Docs that should change

### `docs/async_operator_pipeline_port_plan.md`
Needs update:
- clarify that the async launcher already exists
- note that the real remaining problem is spec-adaptor removal + naming cleanup

### `docs/generic_node_chain_manifest_delta_plan.md`
Needs update:
- reflect that the active remainder is now:
  - remove spec-adaptor
  - rename runtime surface
  - validate async node-chain flow

### New document
- this file:
  - `docs/node_chain_cli_adaptation_plan.md`

### Journal
- `docs/journals/repo-identity-and-operator-pipeline-reframe.md`
Needs update:
- record that:
  - async launcher was confirmed already present
  - spec-adaptor is still lingering in the batch path
  - naming adaptation is the remaining CLI cleanup layer

---

## 6. Execution Phases

## Phase 1 — remove architectural mismatch
1. remove `spec_adaptor.py` invocation from `scripts/run_operator_pipeline_batch.py`
2. make prompt/manifest input the only required upstream input
3. update run-state phases accordingly

### Success criteria
- `start-batch` no longer pauses in `spec_adaptor`
- run proceeds directly from input preparation into node-chain execution

## Phase 2 — validate async detached flow without spec adaptor
4. run:
   - `start-batch`
   - `status`
   - `finish`
5. confirm:
   - detached background launch still works
   - pollable status still works
   - final result still resolves cleanly

### Success criteria
- async UX remains intact after removing spec-adaptor
- no regression in launcher metadata or status polling

## Phase 3 — prove the real two-node chain
6. rerun the real game manifest:
   - node 1: translate to Spanish
   - node 2: invert color palette
7. inspect:
   - contract gating
   - second-node execution
   - final output artifacts
   - any residual legacy naming or assumptions

### Success criteria
- node 2 only runs after valid upstream contract
- palette inversion completes and emits a valid contract
- no spec-adaptor dependency remains in the path

## Phase 4 — naming adaptation
8. introduce more representative naming in:
   - docs
   - run-state fields where safe
   - compatibility wrappers if helpful
9. keep old script names functional during transition
10. define eventual deprecation targets

### Success criteria
- the system reads like what it actually is:
  - prompt + workspace + nodes
  - async detached launcher
  - contract-driven chain

---

## 7. Risk Notes

### Risk 1 — breaking existing run automation
If old script names are renamed too early, existing shell commands and workflows may break.

Mitigation:
- keep existing files
- introduce wrappers/aliases later
- adapt docs first, then entrypoints

### Risk 2 — hidden spec-adaptor assumptions
Some run-state or downstream scripts may still assume spec-adaptor artifacts exist.

Mitigation:
- remove spec-adaptor in the batch path first
- then validate `status` and `finish`
- inspect any remaining references before broad renaming

### Risk 3 — terminology drift during migration
Mixing `operator`, `node`, `stage`, and `pipeline` inconsistently can make the system harder to understand.

Mitigation:
- define preferred terminology explicitly
- apply it first in docs/plans
- then update runtime fields in controlled steps

---

## 8. Concrete Immediate Next Step

The next implementation pass should do this exact sequence:

1. remove `spec_adaptor.py` from `scripts/run_operator_pipeline_batch.py`
2. validate:
   - `scripts/creative_refactor_cli.py start-batch`
   - `status`
   - `finish`
   without spec adaptor
3. rerun the two-node real-game manifest
4. only after that, begin the naming cleanup / wrapper layer

That is the shortest path to making the current system match its intended architecture.