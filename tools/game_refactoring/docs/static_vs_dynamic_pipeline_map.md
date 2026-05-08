# Static vs Dynamic Pipeline Map

This document classifies the current pipeline into static inputs, dynamic runtime products, and mixed/problematic zones based on inspected code.

It is an evidence-oriented architecture map, not a final redesign.

## Purpose

The current system is easier to understand if it is split into:

- **static** things that define stable structure and constraints
- **dynamic** things that are generated or resolved at runtime
- **mixed** zones where static and dynamic concerns are currently entangled

This distinction matters because simplification should preserve useful dynamic behavior while reducing unnecessary coupling.

## Sources used so far

- `scripts/creative_refactor_cli.py`
- `scripts/creative_refactor_runtime.py`
- `scripts/spec_adaptor.py`
- `scripts/run_operator_pipeline_batch.py`
- `scripts/run_operator_pipeline_game.py`
- `scripts/operator_registry_v2.py`
- `scripts/media_policy.py`
- `scripts/prepare_inputs.py`
- `scripts/run_parallel_batch.py`
- `scripts/run_single_game.py`
- `configs/operator_pipeline_v2.json`
- `prompts/operators_v2/03_media_mapper.md`

## Static layer

These are the parts that appear fixed, source-controlled, and structurally stable unless intentionally edited.

### 1. Pipeline structure config
- `configs/operator_pipeline_v2.json`
- stage ids
- stage numbers
- prompt file paths
- max retries per stage
- default timeout

### 2. Registry validation rules
- `scripts/operator_registry_v2.py`
- sequential stage-number enforcement
- prompt existence validation
- operator-id uniqueness

### 3. Base invariant/reference files
Currently still split across multiple files:
- `audio_policy.md`
- `network_policy.md`
- `system_contract.md`
- `refactor_compliance_spec.md`

These are treated as fixed context in `spec_adaptor.py`.

### 4. Style-local editable bundle sources
The editable style-local file set is statically defined:
- `creative_remix_contract.md`
- `visual_identity_contract.md`
- `theme_policy.md`
- `creative_refactor_agent_template.md`

### 5. Deterministic Python policy rules
In `scripts/media_policy.py`, the following are static:
- regex patterns
- suffix allowlists
- URL allowlists
- host blocklists
- icon vocabulary
- source-hint priorities
- placeholder naming patterns

### 6. Orchestration shell rules
The following behaviors are statically encoded in Python:
- create/reuse run
- prepare inputs before worker launch
- per-game bounded concurrency
- stale-heartbeat monitoring
- final dashboard rebuilds
- workspace promotion mechanics

## Dynamic layer

These are runtime-resolved or runtime-generated products.

### 1. Remix prompt input
- optional runtime user prompt
- resolved from CLI args or prompt file

### 2. Selected style at runtime
- style id chosen at invocation time

### 3. Spec-adaptor outputs
When invoked, spec adaptor dynamically produces:
- `run_dir/spec_adaptor/adapted/`
- `run_dir/spec_adaptor/invariants/`
- `recomposition_context.json`
- `recomposition_summary.json`
- `adaptation_report.json`
- `spec_adaptor_job_state.json`

### 4. Per-run state and notes
- `run_state.json`
- selected style
- remix prompt
- spec adaptor status
- notes and counters

### 5. Per-game state
- `game_state.json`
- integrity status
- current phase
- output paths
- pipeline artifacts
- completed stages

### 6. Attempt artifacts
Generated dynamically per attempt:
- prompts
- invocation files
- result files
- stdout/stderr
- stage state
- media policy reports

### 7. Media-policy findings
Generated at runtime from workspace inspection:
- URLs to remove
- media replacement candidates
- font candidates
- icon font candidates
- normalized replacement plans
- cleanup plans
- unresolved post-run candidate lists

### 8. Retry context
Both spec adaptor and operator stages incorporate dynamic retry context:
- previous failure data
- previous stdout-derived summaries
- remaining unresolved findings

## Mixed/problematic zones

These are the most important zones for future cleanup because they blend static structure with dynamic runtime behavior in a way that makes the architecture harder to reason about.

### 1. `build_operator_prompt_text(...)`
This is currently a major mixed zone.

It combines:
- static operator prompt file text
- static stage contract framing
- dynamic run context
- dynamic adapted spec path
- dynamic media policy findings
- dynamic retry context
- dynamic cleanup plans
- static icon vocabulary

Why this matters:
- the registry suggests modular stage abstraction
- but real runtime stage behavior is assembled through a large mixed Python prompt builder

### 2. `media_mapper` completion logic
In `run_operator_pipeline_game.py`:
- the operator id is statically checked
- completion/failure is dynamically overridden based on policy re-scan output

Why this matters:
- stage semantics are not fully owned by config + prompts
- Python still contains operator-specific enforcement

### 3. Optional spec-adaptor behavior
Current code does:
- with remix prompt → run adaptor
- without remix prompt → skip adaptor entirely

This is a mixed boundary because:
- the architecture suggests a shared run-level context layer
- but runtime behavior branches between generated adapted bundle and no adaptor subtree at all

### 4. Legacy prompt generation
`run_single_game.py` builds one combined prompt from:
- static template path
- static policy paths
- dynamic remix prompt
- dynamic packet content
- optional spec-adaptor reuse state

This is simpler than v2, but still mixed.

## Clean boundary that should likely be preserved

One boundary already looks correct and should probably survive refactoring:

### Run-level dynamic preparation
- run creation
- input preparation
- optional spec adaptation
- shared run-level context/state

### Per-game dynamic execution
- per-game workspace
- stage sequencing
- retries
- promotion
- output copy

This separation is a strength, not a weakness.

## Likely future target model

This is not yet an implementation plan; it is a boundary-cleanup direction.

### Static should own
- invariant contract
- stage registry/manifest
- base prompt templates
- style bundles
- artifact contract schemas
- general orchestrator rules

### Dynamic should own
- runtime chosen style/prompt
- adapted bundle
- per-game packet content
- retry context
- runtime findings
- state/artifact instances

### Mixed zones should shrink
Especially:
- Python prompt assembly that encodes stage semantics
- operator-id-specific completion overrides
- stage-specific dynamic enforcement that bypasses generic contracts

## Current blind spot warning

A likely blind spot is assuming that “prompt simplification” will automatically simplify the pipeline.

That may be false because:
- significant specialization currently lives in Python
- especially media-policy generation and post-run enforcement
- registry abstraction alone does not yet make the executor generic

## Implications for next work

### Good next target
- implement dry-run against the orchestrator shell without changing the static/dynamic boundary yet

### Later target
- reduce mixed zones by deciding what should move into:
  - static config
  - static prompt templates
  - dynamic reports only
  - generic executor contracts

### Invariant-contract merge relevance
If invariant files are merged later, they should move deeper into the **static layer** and become easier to reference consistently across:
- spec adaptor
- legacy prompt generation
- operator packet generation

## Working summary

The current pipeline is not purely static and not purely dynamic.

It is a hybrid with:

- a fairly reusable **static orchestration shell**
- a meaningful **dynamic runtime context layer**
- several **mixed zones** where specialization currently lives

The right refactor direction is not to remove dynamic behavior wholesale.

The right direction is:
- preserve useful dynamic behavior
- make static structure more explicit
- shrink the mixed/problematic Python coupling zones