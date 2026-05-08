# Generic Node-Chain Manifest Delta Plan

This document defines the next intended architecture shift away from the legacy fixed-stage pipeline and toward a generic manifest-driven node-chain executor.

It is written as an implementation design + delta map so the next execution pass can be done in controlled steps without re-discovering the target model.

---

## 1. Target Model

The future pipeline model is:

- one manifest defines:
  - the workspace source
  - the main prompt payload
  - the ordered node chain
- each node defines:
  - which prompt file implements it
  - whether it requires a previous valid contract
  - which previous statuses it accepts
- each node emits:
  - workspace edits
  - artifacts
  - `operator_result_contract.json`
- the executor:
  - runs node N
  - reads its contract
  - decides whether node N+1 is allowed
  - writes run/game/node artifacts generically

### Core simplification

The “spec” is no longer modeled as a separate first-class concern inside the pipeline.

Instead:
- the pipeline receives a prompt payload
- that prompt may be short or long
- each node decides how to interpret and implement that prompt

So the future core inputs are:

- workspace
- prompt
- ordered nodes

---

## 2. Sample Generic Manifest Shape

### Minimal example

```json
{
  "manifest_version": "2.0.0",
  "run_label": "hello-world-spanish-chain",
  "workspace": {
    "source_path": "fixtures/hello_world_game",
    "display_name": "Hello World Fixture"
  },
  "prompt": {
    "text": "Translate the game to Spanish."
  },
  "nodes": [
    {
      "id": "translate_to_spanish",
      "prompt_file": "prompts/operators_v2/01_hello_world_spanish_contract.md",
      "accepted_upstream_statuses": ["ok", "warning", "error"],
      "requires_contract": false
    },
    {
      "id": "finalize_copy",
      "prompt_file": "prompts/operators_v2/02_hello_world_finalize_contract.md",
      "accepted_upstream_statuses": ["ok"],
      "requires_contract": true
    }
  ]
}
```

### Real-game example

```json
{
  "manifest_version": "2.0.0",
  "run_label": "sample-game-spanish-pass",
  "workspace": {
    "source_path": "/path/to/game",
    "display_name": "Sample Game"
  },
  "prompt": {
    "text": "Translate this game to Spanish while preserving gameplay."
  },
  "nodes": [
    {
      "id": "translate_ui_and_copy",
      "prompt_file": "prompts/operators_v2/01_gameplay_narrative.md",
      "accepted_upstream_statuses": ["ok", "warning", "error"],
      "requires_contract": false
    },
    {
      "id": "validate_and_refine_copy",
      "prompt_file": "prompts/operators_v2/02_finalize_translation.md",
      "accepted_upstream_statuses": ["ok", "warning"],
      "requires_contract": true
    }
  ]
}
```

---

## 3. What This Replaces

### Legacy model

Current production assumptions still include:
- fixed ordered stage semantics
- `gameplay_narrative`
- `visual_emoji_identity`
- `media_mapper`
- `final_code_ui_mobile_repair`

Those are legacy pipeline concepts.

### New model

The new model removes the idea that the executor itself should know semantic stage names.

Instead, the executor should only know:
- ordered nodes
- prompt files
- contract requirements
- accepted upstream statuses

That means node semantics move into configuration + prompt files, not Python control flow.

---

## 4. File Delta Map

This is the concrete file-level impact expected for the next implementation phase.

### A. New docs

#### `docs/generic_node_chain_manifest_delta_plan.md`
Purpose:
- capture the intended generic manifest format
- record the file delta map
- define migration steps

#### `docs/universal_stage_result_contract_plan.md`
Needs update:
- align with prompt-as-core-input model
- reduce emphasis on separate spec handling inside the pipeline

#### `docs/master_index.md`
Needs update:
- point future sessions at the generic manifest / node-chain migration as the main active direction

#### `docs/journals/repo-identity-and-operator-pipeline-reframe.md`
Needs update:
- record this architecture pivot explicitly

---

### B. Config and manifest layer

#### Existing legacy configs
- `configs/operator_pipeline_v2.json`
- `configs/operator_pipeline_hello_world.json`
- `configs/operator_pipeline_hello_world_two_stage.json`

Status:
- useful as transitional artifacts
- not the long-term config model

#### New generic config or manifest shape
Likely new:
- either a new manifest schema alone
- or a small node-chain config schema referenced by the manifest

Decision:
- prefer putting `nodes` directly in the manifest unless strong reuse pressure appears

Why:
- simpler external interface
- easier per-run customization
- avoids two competing sources of truth too early

---

### C. Executor layer

#### `scripts/run_operator_pipeline_game.py`
This is the main executor hotspot.

Current legacy assumptions still present:
- loaded operator registry
- ordered legacy operator definitions
- stage-slug naming derived from stage number + operator id
- generic shell but still historically shaped around fixed stage identity

Expected future delta:
- consume node definitions from manifest/run data instead of legacy registry semantics
- iterate generic nodes
- continue writing artifacts per node attempt
- keep contract presence/validity/status/detail handling
- keep upstream acceptance checks
- reduce remaining hardcoded stage meaning

#### `scripts/operator_registry_v2.py`
Status:
- currently useful as a transition shim
- may become unnecessary once node definitions live directly in the manifest

Expected future options:
1. keep temporarily for backward compatibility
2. reduce to validation helpers only
3. remove from the main path after migration

#### `scripts/run_operator_pipeline_batch.py`
Expected future delta:
- continue handling run creation, mirroring, concurrency, dashboards
- stop assuming the old fixed stage model is the main execution identity
- mostly pass through generic manifest/run inputs to per-game execution

---

### D. Prompt layer

#### Current proving prompts
- `prompts/operators_v2/01_hello_world_spanish_contract.md`
- `prompts/operators_v2/02_hello_world_finalize_contract.md`

Status:
- canonical minimal proving prompts
- should remain useful for regression testing the generic executor

#### Production prompt
- `prompts/operators_v2/01_gameplay_narrative.md`

Status:
- already partially migrated to emit contract
- useful as the first production node prompt after Hello World

Expected future delta:
- prompts become reusable node implementations
- naming may later move away from “stage 01 / stage 02 / stage 03” language

---

### E. Fixtures

#### `fixtures/hello_world_manifest.json`
Status:
- old proving-manifest shape
- should eventually be replaced or duplicated by a v2 generic-manifest example

#### `fixtures/hello_world_game/index.html`
Status:
- keep as canonical simple workspace proving input

Expected future additions:
- generic Hello World manifest example using `workspace + prompt + nodes`
- later: one real game manifest using the same format

---

## 5. Responsibility Boundaries

### External interface owns:
- workspace selection
- prompt selection / prompt text
- node ordering
- per-node prompt file selection
- contract-policy declarations

### Pipeline owns:
- workspace copying
- node execution
- artifact writing
- contract reading
- continue/stop decisions based on declared policy
- run/game/node state

### Prompt files own:
- implementation logic for each node
- contract emission
- task-specific interpretation of the prompt

This is the cleanest separation found so far.

---

## 6. What Stays vs What Shrinks

### Stays
- run scaffold
- input mirroring
- per-game workspaces
- contract-based chaining
- run/game/node artifacts
- stdout contract as compatibility bridge for now

### Shrinks
- legacy 4-stage semantic importance
- Python-side stage-specific judgment
- internal spec-adaptor centrality
- registry-driven fixed operator identity

### Eventually removed from the “main idea”
- executor knowledge of legacy semantic stage names
- `media_mapper` special handling in the generic loop
- fixed production stage ordering as architecture, rather than as one config example

---

## 7. Safe Execution Order

### Step 1 — write down the target
- this document
- journal update
- master index update

### Step 2 — define the generic manifest format
- workspace
- prompt
- nodes

### Step 3 — create a generic Hello World manifest
- preserve current fixture workspace
- change only manifest shape

### Step 4 — refactor executor to consume generic nodes
- keep backward-compatible bridge behavior
- keep artifact-writing structure

### Step 5 — validate generic Hello World chain
- live run
- two-node chain
- contract gating
- contract presence/validity tracking

### Step 6 — run a real game translation-to-Spanish example
- use production prompt implementation as a node
- inspect output and remaining specialization

### Step 7 — add second prompt and validate contract I/O refinement
- second node validates and/or refines prior output
- confirm full chained node model works on a real game

---

## 8. Risks

### 1. Partial migration confusion
Risk:
- old fixed-stage configs and new generic manifests coexist awkwardly

Mitigation:
- name the new manifest format explicitly
- treat old configs as legacy compatibility artifacts

### 2. Registry overhang
Risk:
- `operator_registry_v2.py` continues to shape new design accidentally

Mitigation:
- new generic manifest should be primary source of node definitions

### 3. Prompt coupling
Risk:
- prompt files still assume legacy stage identity too strongly

Mitigation:
- keep proving prompts generic
- migrate production prompts incrementally

### 4. Hidden execution assumptions
Risk:
- batch/game runner still assumes legacy semantics in small ways

Mitigation:
- validate generic Hello World first, then real-game pass

---

## 9. Immediate Next Coding Task

The next coding task should be:

1. create the first generic manifest example
2. refactor the executor to read `nodes` from that manifest
3. keep bridge compatibility while that lands

That is the shortest path from the current partially generalized system to the actual intended architecture.